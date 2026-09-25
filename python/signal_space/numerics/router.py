"""Bounded exact-block worker; preserves all inputs and measured matrices."""
import itertools
import os
from pathlib import Path
import numpy as np
from scipy.linalg import expm
from signal_space.models.router import SIGMA, stencil, fourier, phase, apply_shifts
from signal_space.runtime.events import append_event
from signal_space.runtime.io import read_json, write_json


def execute(request_path):
    request = read_json(request_path)
    attempt = Path(request['attempt_path'])
    raw = attempt / 'raw'
    raw.mkdir(parents=True, exist_ok=True)
    cfg = request['config']['parameters']
    events = attempt / 'events.jsonl'
    rng = np.random.Generator(np.random.PCG64(request['seed_ledger']['sampling']))
    write_json(raw / 'rng-start.json', rng.bit_generator.state)
    append_event(events, 'worker-started', 'run', {'pid': os.getpid(), 'algorithm': 'port-stencil-fourier-v1'})
    directions = np.array(cfg['directions'], float)
    directions /= np.linalg.norm(directions, axis=1)[:, None]
    q = (np.array(cfg['radii'])[:, None, None] * directions[None, :, :]).reshape(-1, 3)
    # Include exact additional zero- and pi-quasienergy probes on the periodic torus.
    nodes = np.array(list(itertools.product([-np.pi, 0.0], repeat=3)) +
                     list(itertools.product([-np.pi / 2, np.pi / 2], repeat=3)))
    theta = np.linspace(0, 2*np.pi, 181)
    circle = cfg['surface_frequency'] * np.column_stack([np.cos(theta), np.sin(theta), np.zeros_like(theta)])
    axis = np.array([1., 2., 3.]) / np.sqrt(14)
    rotation = expm(-0.5j * cfg['rotation_angle'] * np.einsum('a,aij->ij', axis, SIGMA))
    saved = {'q': q, 'directions': directions, 'nodes': nodes, 'circle': circle, 'rotation': rotation}
    grids = {}
    for size in cfg['zone_sizes']:
        grid_axis = np.linspace(-np.pi, np.pi, size, endpoint=False)
        grid = np.array(np.meshgrid(grid_axis, grid_axis, grid_axis, indexing='ij')).reshape(3, -1).T
        grids[size] = grid
        saved[f'zone_q_{size}'] = grid
    for label, triad in cfg['triads'].items():
        triad = np.array(triad)
        rotated = np.array([[np.trace(rotation @ np.einsum('a,aij->ij', n, SIGMA) @ rotation.conj().T @ s).real / 2 for s in SIGMA] for n in triad])
        for order_label, order in cfg['orders'].items():
            if (attempt / 'cancel.request').exists():
                append_event(events, 'cancellation-observed', 'run', {'sector': label})
                return 130
            key = f'{label}_{order_label}'
            shifts, coefficients = stencil(triad, order)
            saved[f'{key}_u'] = fourier(q, shifts, coefficients)
            saved[f'{key}_nodes'] = fourier(nodes, shifts, coefficients)
            rs, rc = stencil(rotated, order)
            saved[f'{key}_rotated'] = fourier(q, rs, rc)
            for h in cfg['derivative_steps']:
                grads = []
                for axis in range(3):
                    delta = np.eye(3)[axis] * h
                    grads.append((phase(fourier(q+delta, shifts, coefficients)) - phase(fourier(q-delta, shifts, coefficients))) / (2*h))
                saved[f'{key}_gradient_{h}'] = np.array(grads).T
            # Exact sections at omega*tau=surface_frequency, confined to the low-q region.
            # Analyzer independently computes continuum sections; these are measured phase samples.
            surface_axis = np.linspace(-0.35, 0.35, 101)
            xx, yy = np.meshgrid(surface_axis, surface_axis)
            surface_q = np.column_stack([xx.ravel(), yy.ravel(), np.zeros(xx.size)])
            saved['surface_q'] = surface_q
            saved[f'{key}_surface_phase'] = phase(fourier(surface_q, shifts, coefficients))
            for size, grid in grids.items():
                saved[f'{key}_zone_{size}'] = phase(fourier(grid, shifts, coefficients))
            for size in cfg['box_sizes']:
                initial = rng.normal(size=(size,size,size,2)) + 1j*rng.normal(size=(size,size,size,2))
                initial /= np.linalg.norm(initial)
                saved[f'{key}_field_{size}_initial'] = initial
                saved[f'{key}_field_{size}_final'] = apply_shifts(initial, triad, order)
            append_event(events, 'measurement', 'run', {'triad': label, 'order': order_label, 'samples': len(q)})
    np.savez_compressed(raw / 'router.npz', **saved)
    write_json(raw / 'rng-end.json', rng.bit_generator.state)
    write_json(raw / 'execution.json', {'sampling_seed': request['seed_ledger']['sampling'], 'algorithm': 'numpy.PCG64',
               'physical_scope': 'homogeneous zero-wave linear wave sector only',
               'blas_threads': {k: os.environ.get(k) for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS')}})
    append_event(events, 'worker-completed', 'run', {'sectors': 6, 'wavevectors_per_sector': len(q)})
    return 0
