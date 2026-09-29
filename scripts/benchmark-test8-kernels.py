#!/usr/bin/env python3
"""Bounded synthetic kernel timing; no registered experiment or time history.

Evaluate each operation three times on the same manufactured arrays, discard
its result, and write an engineering observation. No physical profile is used.
"""
from __future__ import annotations

import argparse
import cProfile
import hashlib
import json
import os
from pathlib import Path
import platform
import pstats
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

import numpy as np
from signal_space.numerics.two_object_quiet import AbsorbingGrid, step


def measure(operation):
    operation()  # warm-up excluded
    walls, cpus = [], []
    for _ in range(3):
        cpu, wall = time.process_time(), time.perf_counter()
        operation()
        walls.append(time.perf_counter() - wall)
        cpus.append(time.process_time() - cpu)
    return {'wall_seconds': walls, 'median_wall_seconds': statistics.median(walls),
            'process_cpu_seconds': cpus}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('output exists; choose a new observation path')
    started = time.perf_counter()
    rows = []
    for h in (.2, .1, .05):
        grid = AbsorbingGrid(h, 32., 80., 4., .12)
        shape = np.exp(-(grid.r[:, None] / 10.)**2 - (grid.z[None, :] / 20.)**2)
        for active in (False, True):
            neutral = .001 * shape * np.sin(grid.z[None, :]) if active else np.zeros_like(shape)
            state = (shape.astype(complex), -.9j * shape, .001 * shape,
                     .0002 * shape, neutral, .0003 * neutral, 0., 0.)
            operations = {
                'rhs_with_sinks': lambda: grid.rhs_with_sinks(state),
                'rk4_step': lambda: step(grid, state, .005),
                'energy_charge': lambda: grid.energy_charge(state[:6]),
                'health_and_neutral_scan': lambda: (
                    all(np.isfinite(x).all() for x in state),
                    float(np.max(abs(state[4]))), float(np.max(abs(state[5])))),
            }
            row = {'h': h, 'radius': 32, 'half_length': 80,
                   'cells': grid.nr * grid.nz, 'neutral_active': active,
                   'state_bytes': sum(x.nbytes for x in state[:6]),
                   'operations': {name: measure(op) for name, op in operations.items()}}
            if h == .1 and active:
                profiler = cProfile.Profile()
                profiler.enable()
                for _ in range(3):
                    step(grid, state, .005)
                profiler.disable()
                stats = pstats.Stats(profiler)
                row['profile_total_seconds'] = stats.total_tt
                row['profile_by_self_time'] = [
                    {'file': Path(key[0]).name, 'line': key[1], 'function': key[2],
                     'calls': value[1], 'self_seconds': value[2], 'cumulative_seconds': value[3]}
                    for key, value in sorted(stats.stats.items(), key=lambda item: item[1][2], reverse=True)[:20]]
            rows.append(row)
            print(f'h={h}, active={active}: {row["operations"]["rk4_step"]["median_wall_seconds"]:.4f} s/step', flush=True)
    paths = ['scripts/benchmark-test8-kernels.py', 'src/signal_space/numerics/two_object.py',
             'src/signal_space/numerics/two_object_quiet.py', 'src/signal_space/models/two_object.py']
    result = {
        'schema_version': 'signal-space-kernel-timing-observation-v1',
        'recorded_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'scope': 'Synthetic engineering microbenchmark; repeated same-state calls; no physical evolution history, registered run, optimization or acceptance evidence.',
        'method': 'One untimed warm-up, three wall/process-CPU samples per operation; dt=.005; output discarded. Operations overlap and their times must not be added. Profiler is separate from timing samples.',
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'source_sha256_git_lf': {path: hashlib.sha256((ROOT / path).read_text(encoding='utf-8').encode()).hexdigest() for path in paths},
        'environment': {'python': sys.version, 'executable': sys.executable, 'numpy': np.__version__,
                        'platform': platform.platform(), 'logical_cpus': os.cpu_count(),
                        'thread_settings': {k: os.environ.get(k) for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS')}},
        'limitations': ['Not a complete-run ETA; no local tracking, events, checkpoint, serialization or future acceptance diagnostics.',
                       'Only three samples; no long thermal/concurrency test or peak-memory measurement.',
                       'Synthetic fields differ from the frozen clock; timings cannot replace saved physical-run timings.'],
        'rows': rows, 'total_wall_seconds': time.perf_counter() - started,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
