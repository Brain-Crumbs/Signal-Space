"""Spend an additional45s in the original campaign; never replenish its pilot."""
import os
from pathlib import Path

from signal_space.runtime.io import canonical_bytes, read_json, sha256_file, write_json

PILOT = 'gross.local-record-certificate.v1'
RUN = 'run-4fb4fc6333a29dbd'
ALLOCATION = dict(qualification_worker=30, qualification_analysis=15,
                  future_confirmation_worker=145, future_confirmation_analysis=50,
                  prior_pilot=60, total=300, remaining_confirmation=195,
                  prior_output_mb=16, qualification_output_mb=16,
                  remaining_output_mb=96, total_output_mb=128)


def campaign(run_path):
    return run_path.parent.parent/PILOT


def _exclusive(path, record):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(canonical_bytes(record))


def reserve_worker(run_path, config):
    from signal_space.runtime.verify import verify_package
    root = campaign(run_path)
    pilot = root/RUN
    if not verify_package(pilot)['valid']:
        raise ValueError('original canonical pilot unavailable or corrupt')
    if sha256_file(pilot/'checksums.sha256') != config['parameters']['pilot_checksums_sha256']:
        raise ValueError('pilot identity differs from locked continuation')
    manifest = read_json(pilot/'manifest.json')
    if manifest['scientific_classification'] != 'pass' or not manifest['analyses']:
        raise ValueError('pilot scientific prerequisite did not pass')
    markers = root/'.c1-budget-v1'
    for stage, seconds in (('pilot-worker', 45), ('pilot-analysis', 15)):
        expected = dict(stage=stage, run_id=RUN, reserved_cpu_seconds=seconds,
                        reserved_wall_seconds=seconds, reserved_output_mb=8)
        if read_json(markers/(stage+'.json')) != expected:
            raise ValueError('missing or changed original pilot reservation')
    if set(x.name for x in markers.glob('*.json')) != {'pilot-worker.json', 'pilot-analysis.json'}:
        raise ValueError('campaign already reserved confirmation or continuation work')
    record = dict(stage='qualification', run_id=run_path.name, pilot_run_id=RUN,
                  reserved_cpu_seconds=45, reserved_wall_seconds=45, reserved_output_mb=16,
                  allocation=ALLOCATION,
                  note='Reallocates only unspent confirmation allowance; no subsequent confirmation is registered.')
    _exclusive(markers/'qualification.json', record)
    return record


def analyze_saved(run_path, output, config):
    import shutil
    import subprocess
    import sys
    import time
    from signal_space.runtime.runner import _monitor_process, _terminate_process
    from signal_space.runtime.execution import ExecutionPolicy
    from signal_space.runtime.processes import ProcessTree
    marker = campaign(run_path)/'.c1-budget-v1'/'qualification.json'
    reservation = read_json(marker)
    if reservation['run_id'] != run_path.name or reservation['allocation'] != ALLOCATION:
        raise ValueError('qualification campaign reservation mismatch')
    _exclusive(marker.with_name('qualification-analysis.json'), dict(stage='qualification-analysis',
               run_id=run_path.name, reserved_cpu_seconds=15, reserved_wall_seconds=15,
               reserved_output_mb=8, charged_within='qualification.json'))
    stage = run_path.parent/'.c1-qualification-analysis'/run_path.name/output.name
    stage.mkdir(parents=True, exist_ok=False)
    request = stage/'checker-request.json'
    write_json(request, dict(run_path=str(run_path), output=str(stage), config=config))
    limits = dict(max_cpu_seconds=14, max_wall_seconds=14, max_memory_mb=1024, max_output_mb=4)
    start = time.monotonic()
    proc = tree = None
    try:
        with (stage/'checker.log').open('wb') as log:
            env = dict(os.environ)
            env.update(ExecutionPolicy(threads=1, case_jobs=1).environment())
            proc = subprocess.Popen([sys.executable, '-m', 'signal_space.analysis.certificate_qualification', str(request)],
                                    stdout=log, stderr=subprocess.STDOUT, env=env,
                                    start_new_session=os.name == 'posix',
                                    creationflags=getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0) if os.name == 'nt' else 0)
            tree = ProcessTree(proc)
            reason, code = _monitor_process(proc, stage, limits)
            if reason != 'completed' or code != 0:
                raise RuntimeError('qualification saved check: '+reason+' exit='+str(code))
        result = read_json(stage/'result.json')
        if sum(p.stat().st_size for p in stage.rglob('*') if p.is_file()) > 4*1024**2:
            raise RuntimeError('checker staging exceeds4MiB')
        shutil.copytree(stage, output)
        if time.monotonic()-start > 15:
            raise RuntimeError('saved analysis exceeds15s reservation')
        return result
    except BaseException as error:
        if proc is not None and proc.poll() is None:
            _terminate_process(proc, cooperative_seconds=0)
        write_json(stage/'failure.json', dict(error=type(error).__name__+': '+str(error),
                   reservation=reservation, files={p.relative_to(stage).as_posix(): sha256_file(p)
                                                  for p in stage.rglob('*') if p.is_file()}))
        raise
    finally:
        if proc is not None and proc.poll() is None:
            _terminate_process(proc, cooperative_seconds=0)
        if tree is not None:
            tree.close()
