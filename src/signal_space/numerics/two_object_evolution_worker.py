"""Registered execution and full-state restart for doublet pair pilots."""
from pathlib import Path
import shutil

import numpy as np

from signal_space.numerics.two_object import ROOT
from signal_space.numerics.two_object_checkpoint import atomic_npz
from signal_space.numerics.two_object_evolution import (
    DoubletGrid, evolve_step, initial_state, local_records,
)
from signal_space.runtime.events import append_event
from signal_space.runtime.io import read_json, safe_child, sha256_file, write_json

FIELDS = ('phi', 'pi', 'chi', 'pchi', 'a', 'pia')
KIND = 'signal-space-doublet-pair-rk4-v1'


def save_checkpoint(request, *, count, case_index, index, state, grid, samples,
                    cases, preparation, max_neutral):
    attempt = Path(request['attempt_path'])
    root = attempt.parent.parent
    target = attempt / 'checkpoints' / f'checkpoint-{count:010d}-{case_index:03d}.json'
    target.parent.mkdir(exist_ok=True)
    if target.exists():
        return target
    state_record = None
    if state is not None:
        payload = target.with_suffix('.npz')
        atomic_npz(payload, **dict(zip(FIELDS, state[:6])),
                   sinks=np.asarray(state[6:]), rho=grid.r, z=grid.z, gamma=grid.gamma)
        state_record = {'path': payload.relative_to(root).as_posix(), 'sha256': sha256_file(payload)}
    outputs = [{'path': p.relative_to(root).as_posix(), 'sha256': sha256_file(p)}
               for p in sorted((attempt / 'raw').glob('*')) if p.is_file()]
    saved = {'schema_version': 'research-checkpoint-v1', 'checkpoint_format_version': 1,
             'kind': KIND, 'producing_attempt_id': request['attempt_id'],
             'parent_attempt_id': request.get('parent_attempt_id'),
             'config_hash': request['config_hash'], 'code_identity_hash': request['code_identity_hash'],
             'seed_ledger': request['seed_ledger'], 'rng_states': None,
             'preparation': request['config']['parameters']['profile'],
             'solver_state': {'step': count, 'case_index': case_index, 'index': index,
                              'state': state_record, 'preparation': preparation,
                              'max_neutral': max_neutral},
             'accumulated_diagnostics': {'samples': samples, 'cases': cases},
             'completed_outputs': outputs}
    write_json(target, saved, canonical=True)
    return target


def restore_checkpoint(request):
    saved = request['resume_checkpoint']
    if saved['kind'] != KIND or saved['checkpoint_format_version'] != 1:
        raise ValueError('unsupported doublet checkpoint')
    for key in ('config_hash', 'code_identity_hash', 'seed_ledger'):
        if saved[key] != request[key]:
            raise ValueError(f'doublet checkpoint {key} mismatch')
    if saved['preparation'] != request['config']['parameters']['profile']:
        raise ValueError('doublet checkpoint profile mismatch')
    if saved['producing_attempt_id'] != request['parent_attempt_id']:
        raise ValueError('doublet checkpoint parent mismatch')
    root = Path(request.get('checkpoint_root', Path(request['attempt_path']).parent.parent))
    references = saved['completed_outputs'] + ([saved['solver_state']['state']]
                                               if saved['solver_state']['state'] else [])
    for record in references:
        source = safe_child(root, record['path'])
        if sha256_file(source) != record['sha256']:
            raise ValueError('doublet checkpoint payload hash mismatch')
    for record in saved['completed_outputs']:
        source = safe_child(root, record['path'])
        destination = Path(request['attempt_path']) / 'raw' / source.name
        if destination.exists():
            raise ValueError('refusing to overwrite resume output')
        shutil.copyfile(source, destination)
    return saved


def restore_fields(request, saved, grid):
    root = Path(request.get('checkpoint_root', Path(request['attempt_path']).parent.parent))
    with np.load(safe_child(root, saved['solver_state']['state']['path']), allow_pickle=False) as data:
        for name, expected in (('rho', grid.r), ('z', grid.z), ('gamma', grid.gamma)):
            if not np.array_equal(data[name], expected):
                raise ValueError('doublet checkpoint geometry mismatch')
        fields = tuple(data[name].copy() for name in FIELDS)
        if fields[0].shape != (2, grid.nr, grid.nz) or fields[1].shape != fields[0].shape:
            raise ValueError('doublet checkpoint field shape mismatch')
        if data['sinks'].shape != (3,):
            raise ValueError('doublet checkpoint sink shape mismatch')
        return (*fields, *map(float, data['sinks']))


def execute(request_path):
    request = read_json(request_path)
    config = request['config']['parameters']
    attempt = Path(request['attempt_path'])
    raw = attempt / 'raw'
    raw.mkdir(exist_ok=True)
    events = attempt / 'events.jsonl'
    source = ROOT / config['profile']['path']
    if sha256_file(source) != config['profile']['sha256']:
        raise ValueError('frozen radial profile hash mismatch')
    with np.load(source, allow_pickle=False) as data:
        profile = {name: data[name].copy() for name in ('r', 'u', 'mode')}
    saved = restore_checkpoint(request) if request.get('resume_checkpoint') else None
    if not saved:
        write_json(raw / 'source.json', config['profile'])
    cases = saved['accumulated_diagnostics']['cases'] if saved else []
    first_case = saved['solver_state']['case_index'] if saved else 0
    count = saved['solver_state']['step'] if saved else 0
    append_event(events, 'worker-started', 'run', {'algorithm': KIND, 'resumed': bool(saved)})
    for case_index, case in enumerate(config['scenarios']):
        if case_index < first_case:
            continue
        label = case['label']
        grid = DoubletGrid(case['h'], case['radius'], case['half_length'],
                           case['absorber_width'], case['absorber_strength'])
        if saved and case_index == first_case and saved['solver_state']['state']:
            state = restore_fields(request, saved, grid)
            preparation = saved['solver_state']['preparation']
            samples = saved['accumulated_diagnostics']['samples']
            start_index = saved['solver_state']['index']
            max_neutral = saved['solver_state']['max_neutral']
        else:
            state, preparation = initial_state(grid, profile, case, config['correction'])
            samples, start_index, max_neutral = [], 0, 0.
            atomic_npz(raw / f'{label}-initial.npz', **dict(zip(FIELDS, state[:6])), rho=grid.r, z=grid.z)
            write_json(raw / f'{label}-preparation.json', preparation)
        steps = round(case['duration'] / case['dt'])
        for index in range(start_index, steps + 1):
            cancelled = (attempt / 'cancel.request').exists()
            if cancelled or (index < steps and index % config['checkpoint_stride'] == 0):
                path = save_checkpoint(request, count=count, case_index=case_index,
                    index=index, state=state, grid=grid, samples=samples, cases=cases,
                    preparation=preparation, max_neutral=max_neutral)
                append_event(events, 'checkpoint-written', 'run', {'step': count, 'checkpoint': path.name})
            if cancelled:
                append_event(events, 'worker-cancelled', 'run', {'step': count})
                return 130
            if index % case['sample_stride'] == 0 or index == steps:
                energy, charge = grid.energy_charge(state)
                samples.append({'t': index * case['dt'], 'energy': energy, 'charge': charge,
                                'momentum': float(np.sum(grid.volume * grid.momentum_density(state))),
                                'energy_sink': state[6], 'charge_sink': state[7], 'momentum_sink': state[8],
                                'clocks': local_records(grid, state, case, profile)})
            if index == steps:
                break
            state = evolve_step(grid, state, case['dt'])
            count += 1
            if not all(np.isfinite(value).all() for value in state):
                raise ValueError(f'{label}: nonfinite state at step {index+1}')
            max_neutral = max(max_neutral, float(np.max(abs(state[4]))), float(np.max(abs(state[5]))))
            if (index + 1) % 500 == 0:
                append_event(events, 'scenario-progress', 'run', {'label': label, 'step': index+1, 'total': steps})
        atomic_npz(raw / f'{label}-final.npz', **dict(zip(FIELDS, state[:6])),
                   sinks=np.asarray(state[6:]), rho=grid.r, z=grid.z)
        write_json(raw / f'{label}-traces.json', {'samples': samples})
        cases.append({'label': label, 'case': case, 'preparation': preparation,
                      'steps': steps, 'duration': steps * case['dt'], 'max_neutral': max_neutral})
        append_event(events, 'scenario-completed', 'run', {'label': label, 'steps': steps})
        save_checkpoint(request, count=count, case_index=case_index+1, index=0,
                        state=None, grid=None, samples=[], cases=cases, preparation=None, max_neutral=0.)
    write_json(raw / 'scenarios.json', cases)
    write_json(raw / 'execution.json', {'scope': 'doublet pair implementation pilot; full acceptance not evaluated',
                                      'algorithm': KIND, 'seed_ledger': request['seed_ledger'],
                                      'stochastic_use': 'none', 'resumed': bool(saved)})
    append_event(events, 'worker-completed', 'run', {'scenarios': len(cases)})
    return 0
