"""Conservative axisymmetric spatial calibration of the unchanged flat action.

Cell centers are rho=(i+1/2)h, z=zmin+(j+1/2)h.  Cell volumes are the
exact volumes of annular slabs, pi(r_outer²-r_inner²)h.  Face conductances
are area/distance; outer faces have zero normal derivative and the axis has
zero area.  This bounded mirror box is for calibration, not exchange acceptance.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

import numpy as np

from signal_space.models.two_object import (
    charge_density, clock_well, clock_well_prime, neutral_stiffness,
    potential, potential_prime,
)
from signal_space.runtime.events import append_event
from signal_space.runtime.io import read_json, write_json

ROOT = Path(__file__).resolve().parents[3]


from signal_space.engine.axisymmetric import AxisGrid, initial_state, step_rk4

def execute(request_path):
    request = read_json(request_path)
    if request.get('resume_checkpoint'):
        raise ValueError('calibration pilot is atomic; no resume support')
    p = request['config']['parameters']
    attempt = Path(request['attempt_path'])
    raw = attempt/'raw'
    raw.mkdir(exist_ok=True)
    events = attempt/'events.jsonl'
    append_event(events, 'worker-started', 'run', {'algorithm':'axis-fv-rk4-v1'})
    source = ROOT/p['profile']['path']
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    if source_sha != p['profile']['sha256']:
        raise ValueError('frozen Test 6 source mismatch')
    with np.load(source) as data:
        profile = {name:data[name].copy() for name in ('r','u','mode')}
    write_json(raw/'source.json', {'path':p['profile']['path'],'sha256':source_sha,
                                   'omega_Q':.9,'omega_chi':.41274991,
                                   'mode_peak':.001,'stochastic_use':'none'})
    scenarios = []
    for entry in p['scenarios']:
        grid = AxisGrid(entry['h'], entry['radius'], entry['half_length'])
        state = initial_state(grid, profile, p['separation'], pair=entry['pair'])
        start_energy, start_charge = grid.energy_charge(state)
        samples = []
        steps = round(entry['duration']/entry['dt'])
        for index in range(steps+1):
            if index % entry['sample_stride'] == 0 or index == steps:
                energy, charge = grid.energy_charge(state)
                local = tuple(float(np.interp(c, grid.z, state[2][0])) for c in
                              ((-p['separation']/2, p['separation']/2) if entry['pair'] else (0.,)))
                samples.append((index*entry['dt'], energy, charge, *local))
            if index == steps:
                break
            state = step_rk4(grid, state, entry['dt'])
            if not all(np.isfinite(f).all() for f in state):
                raise ValueError(f'nonfinite state at step {index}')
        label = entry['label']
        np.savez_compressed(raw/f'{label}.npz', samples=np.asarray(samples),
                            rho=grid.r, z=grid.z, initial_core=initial_state(grid,profile,p['separation'],pair=entry['pair'])[0].real,
                            final_core=state[0], final_pi=state[1], final_chi=state[2],
                            final_pchi=state[3], final_a=state[4], final_pia=state[5])
        record = {'label':label,'pair':entry['pair'],'h':entry['h'],'dt':entry['dt'],
                  'radius':entry['radius'],'half_length':entry['half_length'],
                  'steps':steps,'samples':len(samples),'initial_energy':start_energy,
                  'initial_charge':start_charge,'final_energy':energy,'final_charge':charge,
                  'max_neutral':float(max(abs(state[4]).max(),abs(state[5]).max())),
                  'max_energy_drift_fraction':float(max(abs(row[1]-start_energy) for row in samples)/start_energy),
                  'max_charge_drift_fraction':float(max(abs(row[2]-start_charge) for row in samples)/start_charge)}
        scenarios.append(record)
        append_event(events,'scenario-completed','run',{'label':label,'steps':steps})
    write_json(raw/'scenarios.json',scenarios)
    write_json(raw/'execution.json',{'stage':'spatial-calibration-pilot',
      'scope':'closed mirror box, exact fixed-internal-direction reduction; no exchange preparation',
      'source_sha256':source_sha,'scenarios':len(scenarios),'seed_ledger':request['seed_ledger']})
    append_event(events,'worker-completed','run',{'scenarios':len(scenarios)})
    return 0
