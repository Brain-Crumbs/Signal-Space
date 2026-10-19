"""Verify a saved locked C1 pilot and emit a bounded launch/obstruction handoff."""
import argparse
import hashlib
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from signal_space.runtime.io import read_json,write_json,sha256_file
from signal_space.runtime.verify import verify_package
from signal_space.numerics.record_tubes import SOURCES

SCIENCE=tuple(SOURCES)+('src/signal_space/experiments/local_certificate.py',
    'src/signal_space/numerics/local_certificate.py','src/signal_space/numerics/certificate_controls.py',
    'src/signal_space/analysis/local_certificate.py','src/signal_space/runtime/certificate_budget.py')


def readiness(run):
    verification=verify_package(run)
    if not verification['valid']:raise ValueError('canonical pilot package verification failed')
    m=read_json(run/'manifest.json');c=read_json(run/'resolved-config.json')
    if m['experiment_id']!='gross.local-record-certificate.v1' or not m['analyses']:
        raise ValueError('wrong experiment or missing analysis')
    analysis=m['analyses'][-1];s=analysis['summary']
    if m['code_identity']['tree_state']!='clean':raise ValueError('pilot source was not committed cleanly')
    revision=m['code_identity']['revision'];sources={}
    for p in SCIENCE:
        source=subprocess.check_output(['git','show',revision+':'+p],cwd=ROOT)
        sources[p]=hashlib.sha256(source).hexdigest()
        if sources[p]!=sha256_file(ROOT/p):raise ValueError('scientific source changed since pilot: '+p)
    plan=read_json(ROOT/'docs/research/plans/gross-certificate-pilot.json')
    config_path=ROOT/plan['runtime_config']
    if read_json(config_path)!=c or sha256_file(config_path)!=plan['runtime_config_sha256']:
        raise ValueError('locked pilot configuration changed')
    sys.path.insert(0,str(ROOT/'.agents/scripts'))
    from experiment_contract import validate_plan
    validate_plan(plan)
    checks=read_json(run/analysis['path']/'checks.json')
    pilot_ok=analysis['classification']=='pass' and all(x['status']=='pass' for x in checks['checks'])
    blockers=list(s['blockers'])
    if not pilot_ok:blockers.append('pilot criteria not all qualified')
    # This implementation intentionally emits no fake confirmation lock when
    # measured admission is blocked. An admissible estimate still needs a
    # separately reviewed registered confirmation config/lock before Task5.
    allowed=pilot_ok and not blockers
    return dict(schema='gross.c1-readiness.v1',pilot_run_id=m['run_id'],analysis_id=analysis['analysis_id'],
        scientific_classification=analysis['classification'],source_revision=revision,source_sha256=sources,
        plan_sha256=plan['locked_sha256'],config_file_sha256=sha256_file(config_path),
        canonical_checksums_sha256=sha256_file(run/'checksums.sha256'),canonical_run=str(run.resolve()),
        verification=verification,one_cycle_checked=pilot_ok,estimate_admitted=allowed,
        launch_allowed=False,blockers=blockers+(['separate confirmatory registration and lock required'] if allowed else []),
        confirmatory_estimate=s['confirmatory_estimate'],budget=s['reservation'],
        task5_command=None,confirmation_status='blocked/not-evaluated',
        next_action='Sharpen the qualified cost estimate under a new bounded lock or obtain a revised explicit budget; do not substitute a32-cycle run.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--run',required=True,type=Path);p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();result=readiness(a.run);a.output.mkdir(parents=True,exist_ok=False)
    write_json(a.output/'readiness.json',result)
    text=['# C1 pilot readiness',f"Pilot {result['pilot_run_id']}; analysis {result['analysis_id']}; classification {result['scientific_classification']}.",
          'Confirmation: BLOCKED / NOT EVALUATED. No32-cycle command is authorized by this handoff.',
          'Blockers: '+('; '.join(result['blockers']) or 'none'),
          'The intact-product work-count extrapolation is deliberately conservative; an admission obstruction does not prove physical record failure.',
          'The worker/analysis reservations are60s pilot and240s confirmation, with128MiB aggregate output. Failed stages retain their reservations.',
          result['next_action']]
    (a.output/'readiness.md').write_text('\n\n'.join(text)+'\n')
    print(__import__('json').dumps({k:result[k] for k in ('pilot_run_id','one_cycle_checked','launch_allowed','blockers')}))


if __name__=='__main__':main()
