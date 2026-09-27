"""Bounded outgoing-layer and local-clock diagnostics for Test 8 prerequisites.

The absorber acts only in a declared outer buffer. Its work and charge loss
are accumulated alongside the RK4 state, so a mirror-boundary reflection is
not silently interpreted as physical isolated-clock evolution.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np

from signal_space.models.two_object import charge_density, neutral_stiffness
from signal_space.numerics.two_object import AxisGrid, ROOT, initial_state
from signal_space.runtime.events import append_event
from signal_space.runtime.io import read_json, write_json


class AbsorbingGrid(AxisGrid):
    def __init__(self, h: float, radius: float, half_length: float, width: float, strength: float):
        super().__init__(h, radius, half_length)
        r = np.clip((self.r[:, None] - (radius - width)) / width, 0, 1)
        z = np.clip((abs(self.z[None, :]) - (half_length - width)) / width, 0, 1)
        self.gamma = strength * np.maximum(np.sin(np.pi * r / 2) ** 2,
                                            np.sin(np.pi * z / 2) ** 2)

    def rhs_with_sinks(self, state):
        fields = state[:6]
        phi, pi, chi, pchi, a, pia = fields
        spatial = self.rhs(fields)
        gamma = self.gamma
        z = neutral_stiffness(abs(phi) ** 2)
        power = gamma * (2 * abs(pi) ** 2 + pchi ** 2 + pia ** 2 / z)
        removed_charge = gamma * charge_density(phi, pi)
        return (spatial[0], spatial[1] - gamma * pi,
                spatial[2], spatial[3] - gamma * pchi,
                spatial[4], spatial[5] - gamma * pia,
                float(np.sum(self.volume * power)),
                float(np.sum(self.volume * removed_charge)))


def step(grid, state, dt):
    def add(base, k, factor):
        return tuple(x + factor * dx for x, dx in zip(base, k))
    a = grid.rhs_with_sinks(state)
    b = grid.rhs_with_sinks(add(state, a, dt / 2))
    c = grid.rhs_with_sinks(add(state, b, dt / 2))
    d = grid.rhs_with_sinks(add(state, c, dt))
    return tuple(x + dt * (ka + 2 * kb + 2 * kc + kd) / 6
                 for x, ka, kb, kc, kd in zip(state, a, b, c, d))


def frozen_mode(grid, profile, center):
    r = profile['r']
    shape = np.r_[profile['mode'][0] / r[1], profile['mode'] / r[1:-1], 0.]
    distance = np.hypot(grid.r[:, None], grid.z[None, :] - center)
    return np.interp(distance, r, shape, left=shape[0], right=0.)


def local_observables(grid, state, profile, nominal_centers, separation):
    phi, pi, chi, pchi, _, _ = state[:6]
    rho_limit = min(grid.r[-1], 20.)
    observations = []
    for center in nominal_centers:
        mask_z = abs(grid.z - center) < separation / 4 if len(nominal_centers) == 2 else abs(grid.z) < 20
        mask_r = grid.r < rho_limit
        mask = mask_r[:, None] & mask_z[None, :]
        density = charge_density(phi, pi)
        positive_weight = grid.volume * np.maximum(density, 0) * mask
        total = float(np.sum(positive_weight))
        measured_center = float(np.sum(positive_weight * grid.z[None, :]) / total) if total > 0 else float('nan')
        mode = frozen_mode(grid, profile, measured_center)
        weights = grid.volume * mask
        norm = float(np.sum(weights * mode ** 2))
        q = float(np.sum(weights * mode * chi) / norm)
        p = float(np.sum(weights * mode * pchi) / norm)
        local = (9 * chi[0] - chi[1]) / 8  # regular-axis quadratic extrapolation
        observations.append({'center': measured_center, 'charge': float(np.sum(grid.volume * density * mask)),
                             'mode_q': q, 'mode_p': p,
                             'mode_energy': .5 * norm * (p * p + .41274991 ** 2 * q * q),
                             'axis_chi': float(np.interp(measured_center, grid.z, local))})
    return observations


def execute(request_path):
    request = read_json(request_path)
    if request.get('resume_checkpoint'):
        raise ValueError('quiet qualification is atomic; stopped cases require a new run')
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
    cases = []
    for entry in config['scenarios']:
        label = entry['label']
        grid = AbsorbingGrid(entry['h'], entry['radius'], entry['half_length'],
                            entry['absorber_width'], entry['absorber_strength'])
        initial = initial_state(grid, profile, config['separation'], pair=entry['pair'])
        state = (*initial, 0., 0.)
        centers = (-config['separation'] / 2, config['separation'] / 2) if entry['pair'] else (0.,)
        energy0, charge0 = grid.energy_charge(initial)
        steps = round(entry['periods'] * 2 * np.pi / (.41274991 * entry['dt']))
        samples = []
        max_neutral = 0.
        for index in range(steps + 1):
            if index % entry['sample_stride'] == 0 or index == steps:
                energy, charge = grid.energy_charge(state[:6])
                samples.append({'t': index * entry['dt'], 'energy': energy, 'charge': charge,
                                'energy_sink': state[6], 'charge_sink': state[7],
                                'clocks': local_observables(grid, state, profile, centers, config['separation'])})
            if index == steps:
                break
            state = step(grid, state, entry['dt'])
            if not all(np.isfinite(x).all() for x in state):
                raise ValueError(f'{label} nonfinite state at step {index}')
            max_neutral = max(max_neutral, float(np.max(abs(state[4]))), float(np.max(abs(state[5]))))
            if (index + 1) % 1000 == 0:
                append_event(events, 'scenario-progress', 'run',
                             {'label': label, 'step': index + 1, 'total_steps': steps})
        np.savez_compressed(raw / f'{label}-final.npz', phi=state[0], pi=state[1],
                            chi=state[2], pchi=state[3], a=state[4], pia=state[5],
                            rho=grid.r, z=grid.z, absorber=grid.gamma,
                            energy_sink=state[6], charge_sink=state[7])
        write_json(raw / f'{label}-traces.json', {'samples': samples})
        cases.append({'label': label, 'pair': entry['pair'], 'h': entry['h'], 'dt': entry['dt'],
                      'radius': entry['radius'], 'half_length': entry['half_length'],
                      'absorber_width': entry['absorber_width'], 'steps': steps,
                      'duration': steps * entry['dt'], 'initial_energy': energy0,
                      'initial_charge': charge0, 'max_neutral': max_neutral})
        append_event(events, 'scenario-completed', 'run', {'label': label, 'steps': steps})
    write_json(raw / 'scenarios.json', cases)
    write_json(raw / 'execution.json', {'scope': 'short outgoing-layer quiet calibration, no source or joint solve',
                                        'profile_sha256': source_sha, 'seed_ledger': request['seed_ledger']})
    append_event(events, 'worker-completed', 'run', {'scenarios': len(cases)})
    return 0
