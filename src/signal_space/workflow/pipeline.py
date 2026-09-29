"""Durable run → analysis → report → reader workflow; recovery never reruns good physics."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback
import threading

from signal_space.runtime.events import _locked
from signal_space.runtime.execution import ExecutionPolicy
from signal_space.runtime.io import read_json, write_json, sha256_file, now, safe_child
from signal_space.runtime.runner import ResearchRuntime
from signal_space.workflow.assessment import assessment
from signal_space.workflow.plans import ROOT, load_plan, validate_plan, digest, canonical_plan
from signal_space.workflow.recipes import RECIPES, recipe_path
from signal_space.workflow.preflight import check

# These contract helpers remain available to external historical scripts.
from experiment_contract import validate_bundle
from package_experiment import package as package_reader

RENDER_LOCK = threading.RLock()  # Matplotlib and PdfPages use process-global state.


def rendered(function):
    with RENDER_LOCK:
        return function()


class Pipeline:
    def __init__(self, repo: Path, output: Path, experiment: str | None = None,
                 threads: int = 1, case_jobs: int = 1, *, resume=False,
                 plan_path=None, cancel_event=None):
        self.repo, self.output = Path(repo).resolve(), Path(output).resolve()
        if self.output.is_relative_to(self.repo):
            raise ValueError('output must be outside the checkout so generated files cannot dirty source provenance')
        self.cancel_event = cancel_event
        self.env = {**os.environ, 'PYTHONPATH': str(self.repo / 'src'), **ExecutionPolicy(threads, case_jobs).environment()}
        self.evidence = self.output / 'evidence'
        self.logs = self.evidence / 'logs'
        self.workspace = self.evidence / 'runs'
        self.journal_path = self.output / 'pipeline.json'
        self.resuming = resume
        if resume:
            self.journal = read_json(self.journal_path)
            if self.journal.get('schema_version') != 'gross-pipeline-v1':
                raise ValueError('unsupported pipeline journal')
            self.status = self.journal['status']
            self.experiment = self.status['experiment']
            self.threads = self.journal['execution_policy']['threads']
            self.case_jobs = self.journal['execution_policy']['case_jobs']
            if self.journal.get('initialized') and (sha256_file(self.evidence / 'plan.json') != self.journal['plan_sha256'] or sha256_file(self.evidence / 'config.json') != self.journal['config_sha256']):
                raise ValueError('pipeline locked inputs changed')
            self.plan_path = self.evidence / 'plan.json' if self.journal.get('initialized') else Path(self.journal['source_plan'])
        else:
            self.experiment = experiment or 'custom-plan'
            self.threads, self.case_jobs = threads, case_jobs
            self.plan_path = Path(plan_path).resolve() if plan_path else recipe_path(self.experiment)
            self.output.mkdir(parents=True, exist_ok=False)
            self.logs.mkdir(parents=True)
            self.status = {'experiment': self.experiment, 'technical_status': 'running',
                           'scientific_classification': 'not-evaluated', 'stage': 'preflight'}
            self.journal = {'schema_version': 'gross-pipeline-v1', 'created_at': now(),
                            'source_plan':str(self.plan_path), 'source_plan_sha256':sha256_file(self.plan_path),
                            'execution_policy': {'threads': threads, 'case_jobs': case_jobs},
                            'status': self.status, 'stages': []}
        self.runtime_api = ResearchRuntime()

    def _save(self):
        self.journal['status'] = self.status
        self.journal['updated_at'] = now()
        write_json(self.journal_path, self.journal)
        write_json(self.evidence / 'status.json', self.status)

    def command(self, stage, args, timeout=180):
        self.status['stage'] = stage
        self._save()
        print(f'[{stage}]', flush=True)
        suffix = ''
        index = 1
        while (self.logs / f'{stage}{suffix}.stdout.log').exists():
            index += 1
            suffix = f'-{index:04d}'
        stdout_path = self.logs / f'{stage}{suffix}.stdout.log'
        stderr_path = self.logs / f'{stage}{suffix}.stderr.log'
        with stdout_path.open('w', encoding='utf-8') as out, stderr_path.open('w', encoding='utf-8') as err:
            result = subprocess.run(args, cwd=self.repo, env=self.env, stdout=out, stderr=err, timeout=timeout)
        if result.returncode:
            raise RuntimeError(f'{stage} exited {result.returncode}; see logs/{stderr_path.name} and .stdout.log')
        return stdout_path.read_text(encoding='utf-8')

    def stage(self, name, function):
        self.status['stage'] = name
        row = {'stage': name, 'state': 'running', 'started_at': now()}
        self.journal['stages'].append(row)
        self._save()
        started = time.monotonic()
        print(f'[{name}]', flush=True)
        try:
            result = function()
            row.update(state='completed', result=result)
            return result
        except BaseException as error:
            row.update(state='failed', error=f'{type(error).__name__}: {error}')
            (self.logs / f'{name}-{len(self.journal["stages"]):04d}.error.log').write_text(traceback.format_exc(), encoding='utf-8')
            raise
        finally:
            row.update(elapsed_seconds=time.monotonic()-started, finished_at=now())
            self._save()

    def _initialize(self):
        if sha256_file(self.plan_path)!=self.journal['source_plan_sha256']:
            raise ValueError('original plan changed since the pipeline was created')
        if self.command('source-status', ['git', 'status', '--porcelain']).strip():
            raise ValueError('commit source changes before executing; a clean checkout is required')
        revision = self.command('source-revision', ['git','rev-parse','HEAD']).strip()
        tree = self.command('source-tree', ['git','rev-parse','HEAD^{tree}']).strip()
        plan, config, config_path = load_plan(self.plan_path)
        result = check(self.plan_path, self.output, ExecutionPolicy(self.threads,self.case_jobs), compile_backend=True)
        write_json(self.evidence / 'preflight.json', result)
        if not result['execution_ready']:
            raise ValueError('preflight rejected: ' + '; '.join(result['blockers']))
        # A portable lock is a new derived plan. Retain the exact original too.
        shutil.copy2(self.plan_path, self.evidence / 'registered-plan.json')
        shutil.copy2(config_path, self.evidence / 'config.json')
        portable = dict(plan, runtime_config='config.json')
        portable['locked_sha256'] = digest(canonical_plan(portable))
        validate_plan(portable)
        write_json(self.evidence / 'plan.json', portable)
        self.journal.update(plan_sha256=sha256_file(self.evidence / 'plan.json'),
                            config_sha256=sha256_file(self.evidence / 'config.json'),
                            registered_plan_lock=plan['locked_sha256'])
        self.status['source_commit'] = revision
        source_paths = {'AGENTS.md','.agents','src','tests','scripts','pyproject.toml','requirements-lock.txt',
                        'requirements-performance-lock.txt','contracts/research','fixtures/research','docs/research','research/papers'}
        def inputs(value):
            if isinstance(value, dict):
                for child in value.values(): inputs(child)
            elif isinstance(value, list):
                for child in value: inputs(child)
            elif isinstance(value,str) and value.startswith('research/'):
                candidate = (self.repo/value).resolve()
                if not candidate.is_relative_to(self.repo) or not candidate.exists():
                    raise ValueError(f'missing or unsafe frozen source: {value}')
                source_paths.add(value)
        inputs(config)
        self.command('source-snapshot',['git','archive','--format=tar.gz','--output',str(self.evidence/'source.tar.gz'),revision,*sorted(source_paths)])
        write_json(self.evidence/'execution.json', {'source_commit':revision,'source_tree':tree,
                   'source_archive_sha256':sha256_file(self.evidence/'source.tar.gz'),
                   'registered_plan_lock':plan['locked_sha256'],'portable_plan_lock':portable['locked_sha256'],
                   'github':{key:self.env.get(key) for key in ('GITHUB_REPOSITORY','GITHUB_SHA','GITHUB_RUN_ID','GITHUB_RUN_ATTEMPT')}})
        self.plan_path = self.evidence/'plan.json'
        self.journal['initialized'] = True
        self._save()

    def _solve(self, config):
        if not self.status.get('run_id'):
            created = self.runtime_api.create_run(config,self.workspace,policy=ExecutionPolicy(self.threads,self.case_jobs))
            self.status.update(run_id=created['run_id'],canonical_path=Path(created['path']).relative_to(self.evidence).as_posix())
            self._save()  # identity survives interruption even before worker launch
        run_id = self.status['run_id']
        state = self.runtime_api.status(self.workspace,run_id)
        started = lambda record: (print(f"run={record['run_id']} attempt={record['attempt_id']} workspace={self.workspace}",flush=True), self._save())
        if not state['attempts']:
            result = self.runtime_api.execute(self.workspace,run_id,on_started=started,cancel_event=self.cancel_event)
        elif state['attempts'][-1]['state'] == 'completed':
            return {'run_id':run_id,'state':'completed','reused':True}
        elif state['attempts'][-1]['state'] in {'running','prepared'}:
            raise ValueError('pipeline has an active attempt; inspect status or stop it before resuming')
        else:
            result = self.runtime_api.resume(self.workspace,run_id,on_started=started,cancel_event=self.cancel_event)
        if result['state'] != 'completed':
            raise RuntimeError(f"solver {result['state']}; resumable={result.get('resumable')}; run={run_id}")
        return result

    def execute(self):
        if self.resuming:
            # Re-entering a failed analysis/export is permitted with new code;
            # the runtime enforces exact source/environment for solver resume.
            for row in self.journal['stages']:
                if row['state']=='running': row.update(state='interrupted',finished_at=now())
            self.status.pop('error',None)
            self.status['technical_status']='running'
        if not self.journal.get('initialized'):
            self.stage('preflight',self._initialize)
        plan, config, _ = load_plan(self.plan_path)
        self.stage('run',lambda:self._solve(config))
        run_id = self.status['run_id']
        source = safe_child(self.evidence,self.status['canonical_path'])
        if not self.runtime_api.verify(self.workspace,run_id)['valid']:
            raise ValueError('canonical package verification failed before analysis')
        manifest = read_json(source/'manifest.json')
        if manifest['analyses']:
            analysis=manifest['analyses'][-1]
        else:
            analysis=self.stage('analyze',lambda:self.runtime_api.analyze(self.workspace,run_id))
        self.status.update(analysis_id=analysis['analysis_id'],scientific_classification=analysis['classification'])
        self._save()
        manifest=read_json(source/'manifest.json')
        reports=[r for r in manifest['reports'] if r['analysis_id']==analysis['analysis_id']]
        # A previously sealed report may predate the locked-question repair.
        # Keep it, but generate a fresh report identity for the current handoff.
        reports=[r for r in reports if report_matches_plan(source/r['path'],plan)]
        report=reports[-1] if reports else self.stage('report',lambda:rendered(lambda:self.runtime_api.report(self.workspace,run_id,analysis['analysis_id'],self.plan_path)))
        self.status['report_id']=report['report_id']; self._save()
        verified=self.stage('verify',lambda:self.runtime_api.verify(self.workspace,run_id))
        if not verified['valid']: raise ValueError('canonical package verification failed')
        manifest=read_json(source/'manifest.json')
        checks=read_json(source/analysis['path']/'checks.json')
        mentor = self.evidence/f'automated-assessment-{analysis["analysis_id"]}.md'
        if not mentor.exists(): mentor.write_text(assessment(manifest,analysis,checks),encoding='utf-8')
        reader = safe_child(self.output,self.status.get('reader_path','reader'))
        reusable=False
        if reader.exists() and (reader/'export.json').exists():
            try:
                validate_bundle(reader,source)
                identity=read_json(reader/'export.json')['source_run']
                reusable=identity['analysis_id']==analysis['analysis_id'] and identity['report_id']==report['report_id']
            except (ValueError,OSError): pass
        if not reusable:
            number=1
            while reader.exists():
                number+=1; reader=self.output/f'reader-{number:04d}'
            self.status['reader_path']=reader.relative_to(self.output).as_posix(); self._save()
            def export():
                package_reader(source,self.plan_path,source/report['path']/'interpretations.json',mentor,reader,
                               self.repo/'src/signal_space',self.status['canonical_path'])
                validate_bundle(reader,source)
                return {'reader_path':self.status['reader_path']}
            self.stage('package',lambda:rendered(export))
        self.status.update(technical_status='completed',stage='complete',checks=checks['checks'],
                           reader_path=reader.relative_to(self.output).as_posix(),
                           evidence_locator=self.status['canonical_path'])

    def summary(self):
        return (f"# Experiment: {self.experiment}\n\nTechnical pipeline: **{self.status['technical_status']}**. "
                f"Scientific classification: **{self.status['scientific_classification']}**.\n\n"
                f"Last stage: {self.status['stage']}. Run: {self.status.get('run_id','not created')}.\n\n"
                f"{self.status.get('error','')}\n\n"
                f"Recovery: `signal-space pipeline --resume --output {self.output}`.\n\n"
                "Canonical bytes, source, locks and stage history remain evidence. Review the paired reader before accepting scientific conclusions.\n")

    def run(self):
        started=time.monotonic(); code=0
        with _locked(self.output/'.pipeline-owner'):
            # Reload under ownership so simultaneous resume commands cannot act
            # on an outdated journal after waiting for the previous supervisor.
            if self.resuming:
                self.journal=read_json(self.journal_path); self.status=self.journal['status']
            try: self.execute()
            except (Exception,KeyboardInterrupt) as error:
                code=130 if isinstance(error,KeyboardInterrupt) else 1
                self.status.update(technical_status='interrupted' if code==130 else 'failed',error=f'{type(error).__name__}: {error}')
                print(self.status['error'],file=sys.stderr)
                print(f'Recover: signal-space pipeline --resume --output "{self.output}"',file=sys.stderr)
            finally:
                self.status['elapsed_seconds']=round(time.monotonic()-started,3)
                self._save()
                (self.evidence/'README.md').write_text(self.summary(),encoding='utf-8')
                shutil.copy2(self.journal_path,self.evidence/'pipeline-history.json')
                if self.env.get('GITHUB_STEP_SUMMARY'):
                    with Path(self.env['GITHUB_STEP_SUMMARY']).open('a',encoding='utf-8') as stream: stream.write(self.summary())
                files=[{'path':p.relative_to(self.evidence).as_posix(),'sha256':sha256_file(p)}
                       for p in sorted(self.evidence.rglob('*')) if p.is_file() and p.name!='evidence-index.json' and not p.name.startswith('.') and not p.name.endswith('.jsonl.lock')]
                write_json(self.evidence/'evidence-index.json',{'files':files})
        return code


def report_matches_plan(path, plan):
    try:
        interpretations=read_json(path/'interpretations.json')
        return all(interpretations.get(row['figure_id'],{}).get('question')==row['question']
                   for row in plan['visualization_plan'] if row['required'])
    except (OSError,ValueError):
        return False


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--experiment',choices=RECIPES)
    parser.add_argument('--plan',type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--threads',type=int,default=1)
    parser.add_argument('--case-jobs',type=int,default=1)
    args=parser.parse_args()
    try: return Pipeline(ROOT,args.output,args.experiment or ('gross-test-01' if not args.plan else None),args.threads,args.case_jobs,resume=args.resume,plan_path=args.plan).run()
    except (ValueError,OSError) as error:
        print(f'pipeline rejected: {error}',file=sys.stderr); return 1
