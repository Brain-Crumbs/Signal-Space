"""Python-only GROSS CLI. JSON results on stdout; diagnostics on stderr."""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
import os
from pathlib import Path
import sys
import time
from typing import Any

from signal_space.contracts.validation import ContractError, load_json
from signal_space.runtime.errors import ResearchRuntimeError
from signal_space.runtime.execution import ExecutionPolicy, cpu_capacity, memory_capacity_mb, disk_capacity_mb
from signal_space.runtime.runner import ResearchRuntime
from signal_space.runtime.scheduler import Budget, run_batch

ROOT = Path(__file__).resolve().parents[2]


def _emit(value: Any) -> None:
    print(json.dumps(value, sort_keys=True, allow_nan=False), flush=True)


def _execution_options(command, batch=False):
    command.add_argument('--threads', type=int, default=1, help='native numerical threads per solver process')
    command.add_argument('--case-jobs', type=int, default=1, help='independent quiet Test 8 cases per run')
    if batch:
        command.add_argument('--jobs', type=int, default=1, help='concurrent independent runs')
        command.add_argument('--cpu-slots', type=int)
        command.add_argument('--memory-mb', type=int, help='aggregate reserved memory ceiling')
        command.add_argument('--output-mb', type=int, help='retained output ceiling across the entire batch')


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='signal-space', description='Registered GROSS experiments and immutable evidence')
    parser.add_argument('--workspace', default='.research-work', help='canonical run package root')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list')
    doctor = sub.add_parser('doctor')
    source = doctor.add_mutually_exclusive_group()
    source.add_argument('--recipe')
    source.add_argument('--plan')
    doctor.add_argument('--profile', choices=['desktop','overnight'], default='desktop')
    _execution_options(doctor)
    sub.add_parser('recipes', help='locked recipes, scope, prerequisites and estimated readiness')
    sub.add_parser('capabilities', help='implemented engine capabilities and explicit missing physics')
    ledger = sub.add_parser('ledger', help='evidence-linked Tests 1–11 current summary')
    ledger.add_argument('--markdown', action='store_true')
    derive = sub.add_parser('derive', help='create a new locked operational plan without changing physics')
    derive.add_argument('--plan', required=True)
    derive.add_argument('--output', required=True)
    for field in ('cpu-seconds','wall-seconds','memory-mb','output-mb'):
        derive.add_argument('--max-'+field, type=int)
    derive.add_argument('--backend', choices=['numpy','numba'])
    derive.add_argument('--neutral-mode', choices=['full','exact-zero'])
    derive.add_argument('--checkpoint-stride', type=int)
    schema = sub.add_parser('schema')
    schema.add_argument('--experiment', required=True)
    for name in ('validate', 'estimate', 'run'):
        command = sub.add_parser(name)
        source = command.add_mutually_exclusive_group(required=True)
        source.add_argument('--config')
        source.add_argument('--plan', help='validate locked design and config hash before execution')
        if name in ('estimate', 'run'):
            _execution_options(command)
    batch = sub.add_parser('batch', help='parallel independent registered configurations or locked plans')
    source = batch.add_mutually_exclusive_group(required=True)
    source.add_argument('--config', action='append')
    source.add_argument('--plan', action='append')
    _execution_options(batch, batch=True)
    sweep = sub.add_parser('sweep')
    sweep.add_argument('--config', required=True)
    sweep.add_argument('--axis', action='append', required=True, help='closed config path=v1,v2')
    _execution_options(sweep, batch=True)
    for name in ('status', 'cancel', 'resume', 'analyze', 'report', 'verify', 'events'):
        command = sub.add_parser(name)
        command.add_argument('--run-id', required=name != 'status')
        if name == 'report':
            command.add_argument('--analysis-id')
            command.add_argument('--plan')
        if name == 'status':
            command.add_argument('--watch', action='store_true')
            command.add_argument('--human', action='store_true')
        if name == 'events':
            command.add_argument('--cursor-file', help='durable per-attempt/per-case reconnect cursor outside the run')
            command.add_argument('--after', type=int, default=0)
            command.add_argument('--follow', action='store_true')
    archive = sub.add_parser('archive')
    archive.add_argument('--run-id', required=True)
    archive.add_argument('--archive-root', default='research/experiments')
    archive.add_argument('--catalog', default='research/catalog.json')
    pipeline = sub.add_parser('pipeline', help='locked run → analysis → report → verified reader package')
    source = pipeline.add_mutually_exclusive_group()
    source.add_argument('--experiment', help='recipe name, e.g. gross-test-01')
    source.add_argument('--plan')
    pipeline.add_argument('--resume', action='store_true')
    pipeline.add_argument('--output', required=True, help='external directory; existing only with --resume')
    _execution_options(pipeline)
    export = sub.add_parser('export', help='reader for a canonical run, or paired handoff for a pipeline')
    source = export.add_mutually_exclusive_group(required=True)
    source.add_argument('--pipeline')
    source.add_argument('--run-id')
    export.add_argument('--plan')
    export.add_argument('--output')
    export.add_argument('--locator', help='durable externally uploaded evidence location to record')
    importing = sub.add_parser('import', help='verify and unpack a paired handoff into a new folder')
    importing.add_argument('--index', required=True)
    importing.add_argument('--output', required=True)
    compare = sub.add_parser('compare', help='compare saved compatible results after showing configuration differences')
    compare.add_argument('left')
    compare.add_argument('right')
    compare.add_argument('--output')
    panel = sub.add_parser('panel', help='render a source-hashed saved-data diagnostic panel')
    panel.add_argument('--spec', required=True)
    panel.add_argument('--output', required=True)
    smoke = sub.add_parser('report-smoke', help='render and package copied saved evidence without evolution')
    smoke.add_argument('--plan', required=True)
    smoke.add_argument('--run', required=True)
    smoke.add_argument('--output', required=True)
    profile_cmd = sub.add_parser('profile', help='collect or match immutable observations of completed work')
    profiling = profile_cmd.add_subparsers(dest='profile_command', required=True)
    collect = profiling.add_parser('collect')
    source = collect.add_mutually_exclusive_group(required=True)
    source.add_argument('--run-id')
    source.add_argument('--pipeline')
    collect.add_argument('--output', required=True)
    matched = profiling.add_parser('match')
    matched.add_argument('--profile', required=True)
    matched.add_argument('--plan', required=True)
    _execution_options(matched)
    campaign = sub.add_parser('campaign', help='persistent bounded dependency graph with scientific gates')
    actions = campaign.add_subparsers(dest='campaign_command', required=True)
    for action in ('inspect','lock','preflight','start','status','stop','resume','export'):
        command = actions.add_parser(action)
        command.add_argument('target', help='locked design/recipe for inspect, preflight and start; output directory otherwise')
        if action in {'start','preflight'}:
            command.add_argument('--output', required=True)
            command.add_argument('--profile', choices=['desktop','overnight'], default='desktop')
            command.add_argument('--jobs', type=int)
            _execution_options(command)
        if action == 'status':
            command.add_argument('--watch', action='store_true')
            command.add_argument('--human', action='store_true')
    return parser


def _locked_config(path: str) -> dict[str, Any]:
    from signal_space.workflow.plans import load_plan
    return load_plan(path)[1]


def _coerce(text: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _set_closed(config: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split('.')
    target: Any = config
    for part in parts[:-1]:
        if not isinstance(target, dict) or part not in target:
            raise ContractError(f'sweep axis uses unknown path: {path}')
        target = target[part]
    if not isinstance(target, dict) or parts[-1] not in target:
        raise ContractError(f'sweep axis uses unknown path: {path}')
    target[parts[-1]] = value


def _sweep(runtime, config, axes, workspace, budget=None, policy=None):
    members = [config]
    declarations = []
    for axis in axes:
        if '=' not in axis:
            raise ContractError('sweep axis must be path=v1,v2')
        path, raw = axis.split('=', 1)
        values = [_coerce(item) for item in raw.split(',')]
        declarations.append({'path': path, 'values': values})
        expanded = []
        for member in members:
            for value in values:
                copy = deepcopy(member)
                _set_closed(copy, path, value)
                expanded.append(copy)
        members = expanded
    record = run_batch(runtime, members, workspace, budget, policy)
    # Persist declarations with the execution record for reproducible sweeps.
    from signal_space.runtime.io import write_json
    record['axes'] = declarations
    write_json(Path(record['path']), record)
    return record


def _events(runtime, workspace, run_id, after, follow, cursor_file=None):
    from signal_space.runtime.progress import EventStream
    package = runtime._package(workspace, run_id)
    reader = EventStream(package.path, cursor_file)
    while True:
        for event in reader.poll(after):
            _emit(event)
        reader.acknowledge()
        manifest = package.manifest
        if not follow or not any(row['state'] in {'prepared', 'running'} for row in manifest['attempts']):
            return
        time.sleep(.25)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    # Apply native thread policy before lazy analysis/report imports as well.
    os.environ.update(ExecutionPolicy().environment())
    runtime = ResearchRuntime()
    workspace = Path(args.workspace).resolve()
    try:
        if args.command == 'list':
            result = {'experiments': runtime.list()}
        elif args.command == 'doctor':
            result = {'cpu_slots': cpu_capacity(), 'available_memory_mb': memory_capacity_mb(),
                      'available_output_mb': disk_capacity_mb(workspace), 'python': sys.version,
                      'source_root': str(ROOT), 'default_execution': ExecutionPolicy().record()}
            from signal_space.workflow.preflight import check, profile
            from signal_space.workflow.recipes import recipe_path
            result['profile'] = profile(args.profile)
            if args.plan or args.recipe:
                result.update(check(args.plan or recipe_path(args.recipe), workspace,
                                    ExecutionPolicy(args.threads,args.case_jobs),compile_backend=True))
        elif args.command == 'recipes':
            from signal_space.workflow.recipes import catalog
            result = {'recipes':catalog()}
        elif args.command == 'capabilities':
            from signal_space.engine import capabilities
            result = capabilities()
        elif args.command == 'ledger':
            from signal_space.workflow.ledger import current, markdown
            result = current()
            if args.markdown:
                print(markdown(result)); return 0
        elif args.command == 'derive':
            from signal_space.workflow.plans import derive
            changes = {key:getattr(args,key) for key in ('max_cpu_seconds','max_wall_seconds','max_memory_mb','max_output_mb') if getattr(args,key) is not None}
            execution = {key:getattr(args,key) for key in ('backend','neutral_mode','checkpoint_stride') if getattr(args,key) is not None}
            result = derive(args.plan,args.output,changes,execution=execution)
        elif args.command == 'schema':
            result = runtime.schema(args.experiment)
        elif args.command in ('validate', 'estimate', 'run'):
            config = _locked_config(args.plan) if args.plan else load_json(args.config)
            if args.command == 'validate':
                result = {'config': runtime.validate(config)}
            elif args.command == 'estimate':
                result = runtime.estimate(config, policy=ExecutionPolicy(args.threads, args.case_jobs))
            else:
                result = runtime.run(config, workspace, policy=ExecutionPolicy(args.threads, args.case_jobs),
                                     on_started=lambda record: print(json.dumps(record), file=sys.stderr, flush=True))
        elif args.command in ('batch', 'sweep'):
            budget = Budget(args.jobs, args.cpu_slots, args.memory_mb, args.output_mb)
            policy = ExecutionPolicy(args.threads, args.case_jobs)
            if args.command == 'batch':
                configs = [_locked_config(p) for p in args.plan] if args.plan else [load_json(p) for p in args.config]
                result = run_batch(runtime, configs, workspace, budget, policy)
            else:
                result = _sweep(runtime, load_json(args.config), args.axis, workspace, budget, policy)
        elif args.command == 'status':
            if args.watch or args.human:
                if not args.run_id:
                    raise ValueError('--watch/--human requires --run-id')
                from signal_space.runtime.progress import snapshot, human_status
                while True:
                    runtime.status(workspace, args.run_id)
                    result = snapshot(runtime._package(workspace, args.run_id).path)
                    print(human_status(result), flush=True) if args.human else _emit(result)
                    if not args.watch or result['technical_state'] not in {'prepared', 'running'}:
                        return 0
                    time.sleep(1)
            result = runtime.status(workspace, args.run_id) if args.run_id else {'runs': runtime.list_runs(workspace)}
        elif args.command in ('cancel', 'resume', 'analyze', 'verify'):
            result = getattr(runtime, args.command)(workspace, args.run_id)
        elif args.command == 'report':
            result = runtime.report(workspace, args.run_id, args.analysis_id, args.plan)
        elif args.command == 'events':
            _events(runtime, workspace, args.run_id, args.after, args.follow, args.cursor_file)
            return 0
        elif args.command == 'archive':
            from signal_space.runtime.archive import archive_run
            result = archive_run(runtime._package(workspace, args.run_id).path, Path(args.archive_root).resolve(),
                                 Path(args.catalog).resolve() if args.catalog else None)
        elif args.command == 'pipeline':
            from signal_space.workflow.pipeline import Pipeline
            if not args.resume and not (args.experiment or args.plan):
                raise ValueError('pipeline requires --experiment or --plan, or --resume')
            return Pipeline(ROOT,Path(args.output),args.experiment,args.threads,args.case_jobs,
                            resume=args.resume,plan_path=args.plan).run()
        elif args.command == 'export':
            from signal_space.workflow.artifacts import handoff, export_run
            if args.pipeline:
                result = handoff(args.pipeline,args.output,args.locator)
            else:
                if not args.plan or not args.output: raise ValueError('run export requires --plan and --output')
                result = export_run(workspace,args.run_id,args.plan,args.output)
        elif args.command == 'import':
            from signal_space.workflow.artifacts import import_handoff
            result = import_handoff(args.index,args.output)
        elif args.command == 'compare':
            from signal_space.workflow.compare import compare
            result = compare(args.left,args.right,args.output)
        elif args.command == 'panel':
            from signal_space.reporting.panels import render_panel
            result = render_panel(args.spec,args.output)
        elif args.command == 'report-smoke':
            from signal_space.workflow.artifacts import smoke_report
            result = smoke_report(args.run,args.plan,args.output)
        elif args.command == 'profile':
            from signal_space.runtime.costs import collect, collect_pipeline, match
            if args.profile_command=='collect':
                result = collect_pipeline(args.pipeline,args.output) if args.pipeline else collect(runtime._package(workspace,args.run_id).path,args.output)
            else: result = match(args.profile,_locked_config(args.plan),ExecutionPolicy(args.threads,args.case_jobs).record())
        elif args.command == 'campaign':
            from signal_space.workflow import campaign
            action = args.campaign_command
            if action == 'inspect': result = campaign.inspect(args.target)
            elif action == 'lock': result = campaign.lock_design(args.target)
            elif action == 'preflight': result = campaign.preflight(args.target,args.output,args.profile,args.jobs,args.case_jobs,args.threads)
            elif action == 'start': result = campaign.Campaign(args.target,args.output,profile_name=args.profile,jobs=args.jobs,case_jobs=args.case_jobs,threads=args.threads).run()
            elif action == 'resume': result = campaign.Campaign(None,args.target,resume=True).run()
            elif action == 'stop': result = campaign.stop(args.target)
            elif action == 'export': result = campaign.export_campaign(args.target)
            else:
                from signal_space.runtime.io import read_json
                while True:
                    result = read_json(Path(args.target)/'campaign.json')
                    if args.human:
                        print(campaign.human_status(result),flush=True)
                    elif args.watch: _emit(result)
                    if not args.watch or result['state']!='running': break
                    time.sleep(1)
                if args.human or args.watch: return 0
        else:
            raise AssertionError(args.command)
        _emit(result)
        if isinstance(result, dict) and (result.get('state') in {'failed', 'interrupted','blocked'} or result.get('execution_ready') is False or result.get('accepted') is False or result.get('valid') is False):
            return 1
        if isinstance(result, dict) and result.get('state') == 'cancelled':
            return 130
        return 0
    except KeyboardInterrupt:
        return 130
    except (ContractError, ResearchRuntimeError, ValueError, OSError) as error:
        code = getattr(error, 'code', 'INPUT_ERROR')
        print(json.dumps({'error': {'code': code, 'message': str(error)}}, sort_keys=True), file=sys.stderr)
        return 2 if code in {'CHECKPOINT_MISMATCH', 'CORRUPT_ARTIFACT', 'INVALID_STATE'} else 1


if __name__ == '__main__':
    raise SystemExit(main())
