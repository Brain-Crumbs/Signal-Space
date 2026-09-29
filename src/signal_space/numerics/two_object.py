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


class AxisGrid:
    def __init__(self, h: float, radius: float, half_length: float):
        self.h = h
        self.nr = round(radius / h)
        self.nz = round(2 * half_length / h)
        if self.nr < 3 or self.nz < 6:
            raise ValueError('insufficient axisymmetric cells')
        self.r = (np.arange(self.nr) + .5) * h
        self.z = (np.arange(self.nz) + .5) * h - self.nz * h / 2
        self.volume = (2 * np.pi * self.r * h * h)[:, None] * np.ones((1, self.nz))
        self.kr = (2 * np.pi * np.arange(1, self.nr) * h * h)[:, None] * np.ones((1, self.nz))
        self.kz = (2 * np.pi * self.r * h)[:, None] * np.ones((1, self.nz - 1))

    def faces(self, q, coefficient=None):
        dr = q[1:] - q[:-1]
        dz = q[:, 1:] - q[:, :-1]
        if coefficient is None:
            cr, cz = 1, 1
        else:
            cr = .5 * (coefficient[1:] + coefficient[:-1])
            cz = .5 * (coefficient[:, 1:] + coefficient[:, :-1])
        return self.kr * cr * dr / self.h, self.kz * cz * dz / self.h

    def divergence(self, flux_r, flux_z):
        accum = np.zeros((self.nr, self.nz), dtype=np.result_type(flux_r, flux_z))
        accum[:-1] += flux_r
        accum[1:] -= flux_r
        accum[:, :-1] += flux_z
        accum[:, 1:] -= flux_z
        return accum / self.volume

    def laplacian(self, q, coefficient=None):
        return self.divergence(*self.faces(q, coefficient))

    def squared_gradient(self, q):
        """Cell gradient from the exact face Hamiltonian derivative w.r.t. s."""
        fr = self.kr * (q[1:] - q[:-1])**2 / self.h
        fz = self.kz * (q[:, 1:] - q[:, :-1])**2 / self.h
        accum = np.zeros_like(q)
        accum[:-1] += fr
        accum[1:] += fr
        accum[:, :-1] += fz
        accum[:, 1:] += fz
        return .5 * accum / self.volume

    def energy_charge(self, state):
        phi, pi, chi, pchi, a, pia = state
        s = abs(phi)**2
        Z = neutral_stiffness(s)
        volume = self.volume
        local = (abs(pi)**2 + potential(s) + .5 * (pchi**2 + clock_well(s)*chi**2)
                 + .025 * chi**4 + .5 * pia**2 / Z)
        e = float(np.sum(volume * local))
        for q, coefficient, factor in ((phi, None, 1), (chi, None, .5), (a, Z, .5)):
            fr, fz = self.faces(q, coefficient)
            e += float(factor * (np.sum(np.real(np.conj(q[1:]-q[:-1])*fr))
                                 + np.sum(np.real(np.conj(q[:, 1:]-q[:, :-1])*fz))))
        charge = float(np.sum(volume * charge_density(phi, pi)))
        return e, charge

    def rhs(self, state):
        phi, pi, chi, pchi, a, pia = state
        s = abs(phi)**2
        Z = neutral_stiffness(s)
        neutral_v = pia / Z
        force = (potential_prime(s) + .5*clock_well_prime(s)*chi**2
                 - .1*(neutral_v**2 - self.squared_gradient(a)))
        return (pi, self.laplacian(phi) - force*phi,
                pchi, self.laplacian(chi) - clock_well(s)*chi - .1*chi**3,
                neutral_v, self.laplacian(a, Z))


def initial_state(grid, profile, separation, amplitude=.001, pair=False):
    r = profile['r']
    radial_core = np.r_[profile['u'][0]/r[1], profile['u']/r[1:-1], 0.]
    radial_mode = np.r_[profile['mode'][0]/r[1], profile['mode']/r[1:-1], 0.]
    radial_mode *= amplitude / np.max(radial_mode)
    centers = (-separation/2, separation/2) if pair else (0.,)
    core = np.zeros((grid.nr, grid.nz))
    chi = np.zeros_like(core)
    for center in centers:
        distance = np.hypot(grid.r[:, None], grid.z[None, :] - center)
        core += np.interp(distance, r, radial_core, left=radial_core[0], right=0)
        chi += np.interp(distance, r, radial_mode, left=radial_mode[0], right=0)
    zero = np.zeros_like(core)
    return (core.astype(complex), (-.9j*core).astype(complex), chi, zero.copy(),
            zero.copy(), zero.copy())


def step_rk4(grid, state, dt):
    def add(base, tangent, factor):
        return tuple(b + factor*k for b, k in zip(base, tangent))
    k1 = grid.rhs(state)
    k2 = grid.rhs(add(state, k1, dt/2))
    k3 = grid.rhs(add(state, k2, dt/2))
    k4 = grid.rhs(add(state, k3, dt))
    return tuple(q + dt/6*(x+2*y+2*z+w)
                 for q, x, y, z, w in zip(state, k1, k2, k3, k4))


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
