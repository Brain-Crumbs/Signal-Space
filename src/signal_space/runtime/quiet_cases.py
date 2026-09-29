"""Parallel, restartable independent Test 8 quiet controls.

Only case order is scheduled. Every case retains the registered serial time
integrator, source hash, state, diagnostics and checkpoint implementation.
A coordinator checkpoint references immutable per-case checkpoint bytes.
"""
from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

from signal_space.runtime.events import append_event
from signal_space.runtime.execution import ExecutionPolicy, process_metrics_available
from signal_space.runtime.io import read_json, write_json, sha256_file, safe_child

KIND = 'gross-quiet-parallel-v1'


def _reference(path, root):
    return {'path': path.relative_to(root).as_posix(), 'sha256': sha256_file(path)}


def _checked(root, record):
    path = safe_child(root, record['path'])
    if not path.is_file() or sha256_file(path) != record['sha256']:
        raise ValueError('parallel checkpoint payload hash mismatch')
    return path


def _memory_mb(case):
    cells = round(case['radius']/case['h']) * round(2*case['half_length']/case['h'])
    return max(768, int(cells*.004) + 256)


def execute(request_path):
    request = read_json(request_path)
    attempt = Path(request['attempt_path'])
    root = attempt.parent.parent
    raw = attempt/'raw'; raw.mkdir(exist_ok=True)
    events = attempt/'events.jsonl'
    policy = ExecutionPolicy.from_record(request.get('execution_policy'))
    parameters = request['config']['parameters']
    scenarios = parameters['scenarios']
    resources = request['config']['resources']
    memory_budget = resources['max_memory_mb'] - 192  # coordinator and diagnostics
    reservations = [_memory_mb(case) for case in scenarios]
    if any(memory > memory_budget for memory in reservations):
        raise ValueError('quiet parallel case cannot fit locked memory ceiling including coordinator')
    from signal_space.numerics.two_object import ROOT
    source = ROOT / parameters['profile']['path']
    if sha256_file(source) != parameters['profile']['sha256']:
        raise ValueError('frozen Test 6 profile differs from locked hash')
    write_json(raw/'source.json', {'path': parameters['profile']['path'], 'sha256': parameters['profile']['sha256'],
                                 'omega_Q': .9, 'omega_chi': .41274991, 'mode_peak': .001})
    rows = [{'label': s['label'], 'state': 'queued', 'checkpoint': None, 'outputs': [], 'step': 0}
            for s in scenarios]
    saved = request.get('resume_checkpoint')
    if saved:
        if saved.get('kind') != KIND:
            raise ValueError('parallel execution requires its own checkpoint format')
        for key in ('config_hash', 'code_identity_hash', 'seed_ledger'):
            if saved[key] != request[key]:
                raise ValueError(f'parallel checkpoint {key} mismatch')
        if saved['producing_attempt_id'] != request['parent_attempt_id']:
            raise ValueError('parallel checkpoint parent mismatch')
        if saved['preparation'] != parameters['profile']:
            raise ValueError('parallel checkpoint preparation mismatch')
        rows = deepcopy(saved['cases'])
        if [x['label'] for x in rows] != [s['label'] for s in scenarios]:
            raise ValueError('parallel checkpoint scenario order mismatch')
        for row in rows:
            if row['checkpoint']:
                _checked(root, row['checkpoint'])
            for record in row['outputs']:
                _checked(root, record)
            if row['state'] == 'completed':
                for record in row['outputs']:
                    source_path = _checked(root, record)
                    if source_path.name.endswith(('-final.npz', '-traces.json')):
                        shutil.copyfile(source_path, raw/source_path.name)
            else:
                row['state'] = 'queued'
    append_event(events, 'worker-started', 'run', {'algorithm': KIND, 'execution_policy': policy.record(),
                                                 'memory_reservations_mb': reservations})
    pending = [i for i, row in enumerate(rows) if row['state'] != 'completed']
    active = {}
    sequence = 0
    last_checkpoint = None

    def save():
        nonlocal sequence, last_checkpoint
        fingerprint = repr(rows)
        if fingerprint == last_checkpoint:
            return
        sequence += 1
        value = {'schema_version': 'research-checkpoint-v1', 'checkpoint_format_version': 1,
                 'kind': KIND, 'producing_attempt_id': request['attempt_id'],
                 'parent_attempt_id': request.get('parent_attempt_id'),
                 'config_hash': request['config_hash'], 'code_identity_hash': request['code_identity_hash'],
                 'seed_ledger': request['seed_ledger'], 'preparation': parameters['profile'],
                 'solver_state': {'step': sum(row['step'] for row in rows)}, 'cases': rows}
        path = attempt/'checkpoints'/f'checkpoint-{sequence:010d}.json'
        write_json(path, value, canonical=True)
        last_checkpoint = fingerprint

    def collect(i, child):
        row = rows[i]
        paths = sorted((child/'checkpoints').glob('checkpoint-*.json'))
        if paths:
            reference = _reference(paths[-1], root)
            if reference != row['checkpoint']:
                value = read_json(paths[-1])
                row.update(checkpoint=reference, checkpoint_root=child.parent.parent.relative_to(root).as_posix(),
                           step=value['solver_state']['step'])

    save()
    exit_code = 0
    try:
        while pending or active:
            cancelled = (attempt/'cancel.request').exists()
            if cancelled:
                for i in pending:
                    rows[i]['state'] = 'cancelled-before-start'
                pending.clear()
                exit_code = 130
                for _, child, _ in active.values():
                    (child/'cancel.request').touch(exist_ok=True)
            used = sum(reservations[i] for i in active)
            for i in list(pending):
                if len(active) >= policy.case_jobs:
                    break
                if used + reservations[i] > memory_budget:
                    continue
                row = rows[i]
                child = attempt/'cases'/row['label']/'attempts'/request['attempt_id']
                child.mkdir(parents=True)
                child_request = deepcopy(request)
                child_request['config']['parameters']['scenarios'] = [scenarios[i]]
                child_request['execution_policy'] = {'threads': policy.threads, 'case_jobs': 1}
                child_request['attempt_path'] = str(child)
                child_request['resume_checkpoint'] = None
                child_request['parent_attempt_id'] = None
                if row['checkpoint']:
                    child_request['resume_checkpoint'] = read_json(_checked(root, row['checkpoint']))
                    child_request['parent_attempt_id'] = child_request['resume_checkpoint']['producing_attempt_id']
                    child_request['checkpoint_root'] = str(safe_child(root, row['checkpoint_root']))
                # With an opaque process namespace, conservatively divide the CPU
                # ceiling between every case and the coordinator. Each child has
                # its own memory cap; reservations bound simultaneous allocations.
                cpu = resources['max_cpu_seconds']
                if not process_metrics_available():
                    cpu = max(1, cpu // (len(scenarios) + 1))
                child_request['worker_limits'] = {**resources, 'max_memory_mb': reservations[i], 'max_cpu_seconds': cpu}
                write_json(child/'request.json', child_request)
                log = (child/'worker.log').open('wb')
                try:
                    process = subprocess.Popen([sys.executable, '-m', 'signal_space.runtime.case_worker',
                                                '--request', str(child/'request.json')],
                                               stdout=log, stderr=subprocess.STDOUT,
                                               env={**os.environ, **policy.environment()})
                except BaseException:
                    log.close()
                    raise
                active[i] = (process, child, log)
                pending.remove(i); used += reservations[i]
                row['state'] = 'running'
                append_event(events, 'scenario-started', 'run', {'label': row['label'], 'pid': process.pid})
            for i, (process, child, log) in list(active.items()):
                collect(i, child)
                code = process.poll()
                if code is None:
                    continue
                log.close(); del active[i]
                row = rows[i]
                row['exit_code'] = code
                row['state'] = 'completed' if code == 0 else 'cancelled' if code == 130 else 'failed'
                if code == 0:
                    child_raw = child/'raw'
                    row['outputs'] = [_reference(child_raw/f'{row["label"]}{suffix}', root)
                                      for suffix in ('-final.npz', '-traces.json')]
                    row['outputs'].append(_reference(child_raw/'scenarios.json', root))
                    for record in row['outputs'][:2]:
                        shutil.copyfile(_checked(root, record), raw/Path(record['path']).name)
                    row['case'] = read_json(child_raw/'scenarios.json')[0]
                else:
                    exit_code = code or 1
                append_event(events, 'scenario-'+row['state'], 'run', {'label': row['label'], 'exit_code': code, 'step': row['step']})
            save()
            if active:
                time.sleep(.1)
    finally:
        # Children inherit the supervisor's process group. On exceptions, also
        # terminate/reap them directly so a worker crash does not leak solvers.
        for i, (process, child, log) in active.items():
            (child/'cancel.request').touch(exist_ok=True)
        for i, (process, child, log) in active.items():
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait()
            log.close()
            collect(i, child)
            rows[i]['state'] = 'interrupted'
        save()
    if any(row['state'] != 'completed' for row in rows):
        return 1 if any(row['state'] == 'failed' for row in rows) else exit_code or 1
    write_json(raw/'scenarios.json', [row['case'] for row in rows])
    write_json(raw/'execution.json', {'scope': 'short outgoing-layer quiet calibration, no source or joint solve',
        'profile_sha256': parameters['profile']['sha256'], 'seed_ledger': request['seed_ledger'],
        'execution': parameters.get('execution', {'backend': 'numpy', 'neutral_mode': 'full', 'checkpoint_stride': 1000}),
        'parallel': policy.record(), 'resumed': saved is not None})
    append_event(events, 'worker-completed', 'run', {'scenarios': len(rows)})
    return 0
