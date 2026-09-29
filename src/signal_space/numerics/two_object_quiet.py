"""Bounded outgoing-layer and local-clock diagnostics for Test 8 prerequisites.

The absorber acts only in a declared outer buffer. Its work and charge loss
are accumulated alongside the RK4 state, so a mirror-boundary reflection is
not silently interpreted as physical isolated-clock evolution.
"""

from __future__ import annotations

import hashlib
import time
from pathlib import Path

import numpy as np

from signal_space.models.two_object import charge_density, neutral_stiffness
from signal_space.numerics.two_object import AxisGrid, ROOT, initial_state
from signal_space.runtime.events import append_event
from signal_space.runtime.io import read_json, write_json


from signal_space.engine.axisymmetric import AbsorbingGrid, step, frozen_mode, local_observables

def execute(request_path):
    request = read_json(request_path)
    if request.get('execution_policy', {}).get('case_jobs', 1) > 1:
        from signal_space.runtime.quiet_cases import execute as execute_cases
        return execute_cases(request_path)
    config = request['config']['parameters']
    attempt = Path(request['attempt_path'])
    raw = attempt / 'raw'
    raw.mkdir(exist_ok=True)
    events = attempt / 'events.jsonl'
    append_event(events, 'worker-started', 'run', {'algorithm': 'axis-fv-rk4-sponge-v1'})
    source = ROOT / config['profile']['path']
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    if source_sha != config['profile']['sha256']:
        raise ValueError('frozen Test 6 profile differs from locked hash')
    with np.load(source) as data:
        profile = {key: data[key].copy() for key in ('r', 'u', 'mode')}
    write_json(raw / 'source.json', {'path': config['profile']['path'], 'sha256': source_sha,
                                     'omega_Q': .9, 'omega_chi': .41274991, 'mode_peak': .001})
    from signal_space.numerics.two_object_checkpoint import (
        atomic_npz, restore_checkpoint, restore_fields, save_checkpoint,
    )
    options = config.get('execution', {'backend': 'numpy', 'neutral_mode': 'full', 'checkpoint_stride': 1000})
    backend = options['backend']
    if backend not in ('numpy', 'numba') or options['neutral_mode'] not in ('full', 'exact-zero'):
        raise ValueError('unknown execution backend/neutral mode')
    if backend == 'numpy' and options['neutral_mode'] != 'full':
        raise ValueError('exact-zero specialization requires the compiled backend')
    saved = restore_checkpoint(request) if request.get('resume_checkpoint') else None
    cases = saved['accumulated_diagnostics']['cases'] if saved else []
    first_case = saved['solver_state']['case_index'] if saved else 0
    total_step = saved['solver_state']['step'] if saved else 0
    timings = []
    for case_index, entry in enumerate(config['scenarios']):
        if case_index < first_case:
            continue
        label = entry['label']
        case_started = time.perf_counter()
        case_cpu = time.process_time()
        measured = dict(setup=0., step=0., health=0., diagnostics=0., checkpoint=0., serialization=0.)
        grid = AbsorbingGrid(entry['h'], entry['radius'], entry['half_length'],
                            entry['absorber_width'], entry['absorber_strength'])
        initial = initial_state(grid, profile, config['separation'], pair=entry['pair'])
        state = (*initial, 0., 0.)
        centers = (-config['separation'] / 2, config['separation'] / 2) if entry['pair'] else (0.,)
        energy0, charge0 = grid.energy_charge(initial)
        steps = round(entry['periods'] * 2 * np.pi / (.41274991 * entry['dt']))
        samples = []
        max_neutral = 0.
        start_index = 0
        if saved and case_index == first_case and saved['solver_state']['state']:
            state = restore_fields(request, saved, grid)
            start_index = saved['solver_state']['index']
            samples = saved['accumulated_diagnostics']['samples']
            max_neutral = saved['solver_state']['max_neutral']
            energy0 = saved['solver_state']['initial_energy']
            charge0 = saved['solver_state']['initial_charge']
        integrator = None
        if backend == 'numba':
            from signal_space.numerics.two_object_compiled import CompiledStepper
            integrator = CompiledStepper(grid, state, exact_zero=options['neutral_mode'] == 'exact-zero')
            state = integrator.state
        measured['setup'] = time.perf_counter()-case_started
        for index in range(start_index, steps + 1):
            cancelled = (attempt / 'cancel.request').exists()
            if cancelled or (index < steps and index % options['checkpoint_stride'] == 0):
                checkpoint_started = time.perf_counter()
                checkpoint = save_checkpoint(request, step=total_step, case_index=case_index,
                    index=index, state=state, grid=grid, samples=samples, cases=cases,
                    max_neutral=max_neutral, initial_energy=energy0, initial_charge=charge0)
                measured['checkpoint'] += time.perf_counter()-checkpoint_started
                append_event(events, 'checkpoint-written', 'run', {'step': total_step, 'label': label, 'checkpoint': checkpoint.name})
            if cancelled:
                append_event(events, 'worker-cancelled', 'run', {'step': total_step})
                return 130
            if index % entry['sample_stride'] == 0 or index == steps:
                diagnostics_started = time.perf_counter()
                energy, charge = grid.energy_charge(state[:6])
                samples.append({'t': index * entry['dt'], 'energy': energy, 'charge': charge,
                                'energy_sink': state[6], 'charge_sink': state[7],
                                'clocks': local_observables(grid, state, profile, centers, config['separation'])})
                measured['diagnostics'] += time.perf_counter()-diagnostics_started
            if index == steps:
                break
            step_started = time.perf_counter()
            state = integrator.advance(entry['dt']) if integrator else step(grid, state, entry['dt'])
            measured['step'] += time.perf_counter()-step_started
            health_started = time.perf_counter()
            total_step += 1
            if not all(np.isfinite(x).all() for x in state):
                raise ValueError(f'{label} nonfinite state at step {index}')
            max_neutral = max(max_neutral, float(np.max(abs(state[4]))), float(np.max(abs(state[5]))))
            measured['health'] += time.perf_counter()-health_started
            if (index + 1) % 1000 == 0:
                append_event(events, 'scenario-progress', 'run',
                             {'label': label, 'step': index + 1, 'total_steps': steps,
                              'elapsed_seconds': time.perf_counter()-case_started,
                              'steps_per_second': (index+1-start_index)/max(time.perf_counter()-case_started, 1e-9)})
        serialization_started = time.perf_counter()
        atomic_npz(raw / f'{label}-final.npz', phi=state[0], pi=state[1],
                            chi=state[2], pchi=state[3], a=state[4], pia=state[5],
                            rho=grid.r, z=grid.z, absorber=grid.gamma,
                            energy_sink=state[6], charge_sink=state[7])
        write_json(raw / f'{label}-traces.json', {'samples': samples})
        cases.append({'label': label, 'pair': entry['pair'], 'h': entry['h'], 'dt': entry['dt'],
                      'radius': entry['radius'], 'half_length': entry['half_length'],
                      'absorber_width': entry['absorber_width'], 'steps': steps,
                      'duration': steps * entry['dt'], 'initial_energy': energy0,
                      'initial_charge': charge0, 'max_neutral': max_neutral})
        measured['serialization'] += time.perf_counter()-serialization_started
        checkpoint_started = time.perf_counter()
        save_checkpoint(request, step=total_step, case_index=case_index + 1,
            index=0, state=None, grid=None, samples=[], cases=cases,
            max_neutral=0., initial_energy=None, initial_charge=None)
        measured['checkpoint'] += time.perf_counter()-checkpoint_started
        timings.append({'label': label, 'case': entry, 'steps_measured': steps-start_index, 'complete_case': start_index==0,
                        'wall_seconds': time.perf_counter()-case_started, 'cpu_seconds': time.process_time()-case_cpu,
                        'phases_seconds': measured})
        write_json(attempt / 'performance.json', {'schema_version':'gross-case-performance-v1','cases':timings,'execution':options})
        append_event(events, 'scenario-completed', 'run', {'label': label, 'steps': steps})
    write_json(raw / 'scenarios.json', cases)
    write_json(raw / 'execution.json', {'scope': 'short outgoing-layer quiet calibration, no source or joint solve',
                                        'profile_sha256': source_sha, 'seed_ledger': request['seed_ledger'],
                                        'execution': options, 'resumed': saved is not None})
    append_event(events, 'worker-completed', 'run', {'scenarios': len(cases)})
    return 0
