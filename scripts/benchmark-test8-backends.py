#!/usr/bin/env python3
"""Bounded synthetic backend preflight, never a physical acceptance campaign.

Three warm timing samples, an evolving eight-step workload with reference
diagnostics and compressed state output, three steady windows, and an optional
five-minute sustained window. Aggregate cap: 30 wall minutes / 2 CPU hours.
No children are launched. Missing campaign diagnostics remain unpriced.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMBA_NUM_THREADS'):
    os.environ[name] = '1'

import numpy as np
from signal_space.numerics.two_object_compiled import CompiledStepper
from signal_space.numerics.two_object_quiet import AbsorbingGrid, local_observables, step
from signal_space.numerics.two_object_checkpoint import atomic_npz


def peak_memory():
    if os.name != 'nt':
        import resource
        value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return int(value if sys.platform == 'darwin' else value * 1024)
    import ctypes
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
            (key, ctypes.c_size_t) for key in ('PeakWorkingSetSize', 'WorkingSetSize',
                'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage',
                'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi = ctypes.WinDLL('psapi', use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    if not psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    return counters.PeakWorkingSetSize


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--window-seconds', type=float, default=10)
    parser.add_argument('--sustained-seconds', type=float, default=300)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('output exists; choose a new observation path')
    if not 0 <= args.window_seconds <= 30 or not 0 <= args.sustained_seconds <= 300:
        parser.error('window must be 0–30 seconds and sustained 0–300 seconds')
    started, cpu_started = time.perf_counter(), time.process_time()
    def budget():
        if time.perf_counter()-started > 1800 or time.process_time()-cpu_started > 7200:
            raise TimeoutError('aggregate preflight cap reached')
    def timed(call):
        budget()
        wall, cpu = time.perf_counter(), time.process_time()
        call()
        return {'wall_seconds': time.perf_counter()-wall, 'cpu_seconds': time.process_time()-cpu}
    def measure(call):
        samples = [timed(call) for _ in range(3)]
        walls = [x['wall_seconds'] for x in samples]
        return {'samples': samples, 'median_wall_seconds': statistics.median(walls),
                'range_wall_seconds': [min(walls), max(walls)]}
    def window(call, seconds):
        wall, cpu, count = time.perf_counter(), time.process_time(), 0
        while time.perf_counter()-wall < seconds:
            budget()
            call()
            count += 1
        elapsed = time.perf_counter()-wall
        return {'steps': count, 'wall_seconds': elapsed, 'cpu_seconds': time.process_time()-cpu,
                'seconds_per_step': elapsed/count if count else None}
    def fixture(grid, active):
        shape = np.exp(-(grid.r[:, None]/10)**2 - (grid.z[None, :]/20)**2)
        neutral = .001*shape*np.sin(grid.z[None, :]) if active else np.zeros_like(shape)
        return (shape.astype(complex), -.9j*shape, .001*shape, .0002*shape,
                neutral, .0003*neutral, 0., 0.)
    rows = []
    partial = None
    paths = ['scripts/benchmark-test8-backends.py', 'requirements-performance-lock.txt',
             'requirements-lock.txt', 'src/signal_space/numerics/two_object_compiled.py',
             'src/signal_space/numerics/two_object_quiet.py',
             'src/signal_space/numerics/two_object_checkpoint.py',
             'src/signal_space/numerics/two_object.py', 'src/signal_space/models/two_object.py']
    # A fresh cache is selected by the caller for a true cold measurement.
    tiny = AbsorbingGrid(.5, 3, 4, 1, .12)
    cold = timed(lambda: CompiledStepper(tiny, fixture(tiny, True)).advance(.005))
    radial = np.linspace(0, 100, 1001)
    profile = {'r': radial, 'mode': radial[1:-1]*np.exp(-(radial[1:-1]/10)**2)}
    sustained = None
    try:
        for h in (.2, .1, .05):
            for active in (False, True):
                grid = AbsorbingGrid(h, 32, 80, 4, .12)
                initial = fixture(grid, active)
                for backend in ('numpy', 'numba-full') + (() if active else ('numba-zero',)):
                    setup_start = time.perf_counter()
                    engine = None if backend == 'numpy' else CompiledStepper(grid, initial, exact_zero=backend == 'numba-zero')
                    setup = time.perf_counter()-setup_start
                    def advance():
                        return step(grid, initial, .005) if engine is None else engine.advance(.005)
                    advance()  # warm-up
                    step_timing = measure(advance)
                    component = {'energy_charge': measure(lambda: grid.energy_charge(initial[:6])),
                                 'local_observables': measure(lambda: local_observables(grid, initial, profile, (-36.,36.), 72))}
                    with tempfile.TemporaryDirectory(dir=ROOT/'.research-work') as folder:
                        output = Path(folder)/'state.npz'
                        def workload():
                            nonlocal engine
                            state = tuple(x.copy() for x in initial[:6]) + initial[6:]
                            engine = None if backend == 'numpy' else CompiledStepper(grid, state, exact_zero=backend == 'numba-zero')
                            for index in range(8):
                                state = step(grid, state, .005) if engine is None else engine.advance(.005)
                                if not all(np.isfinite(x).all() for x in state):
                                    raise ValueError('nonfinite fixture')
                                if index % 4 == 0:
                                    grid.energy_charge(state[:6])
                                    local_observables(grid, state, profile, (-36.,36.), 72)
                            atomic_npz(output, **{f'field_{k}': x for k, x in enumerate(state)})
                        total = timed(workload)
                        persisted = output.stat().st_size
                    # Same-state reference versus evolving optimized windows is
                    # disclosed; the complete workload above evolves both.
                    windows = [window(advance, args.window_seconds) for _ in range(3)] if engine is not None else []
                    row = {'h': h, 'cells': grid.nr*grid.nz, 'neutral_active': active, 'backend': backend,
                           'setup_wall_seconds': setup, 'rk4_step': step_timing, 'components': component,
                           'eight_step_workload': total, 'compressed_state_bytes': persisted,
                           'state_bytes': sum(x.nbytes for x in initial[:6]),
                           'process_peak_rss_bytes_so_far': peak_memory(), 'steady_windows': windows}
                    rows.append(row)
                    print(f'{h} active={active} {backend}: step={step_timing["median_wall_seconds"]:.4f}s workload={total["wall_seconds"]:.3f}s', flush=True)
                    del engine
                    engine = None
                    gc.collect()
        # Fine active-neutral, intentionally the unspecialized backend.
        grid = AbsorbingGrid(.1, 32, 80, 4, .12)
        engine = CompiledStepper(grid, fixture(grid, True))
        sustained = window(lambda: engine.advance(.005), args.sustained_seconds)
        sustained['finite_final_state'] = all(np.isfinite(x).all() for x in engine.state)
    except TimeoutError as error:
        partial = str(error)
    result = {'schema_version': 'signal-space-backend-preflight-v1',
        'recorded_at_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'scope': 'Synthetic engineering fixture only; no accepted profile or scientific acceptance execution.',
        'source_commit': subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        'source_sha256_git_lf': {p: hashlib.sha256((ROOT/p).read_text(encoding='utf-8').encode()).hexdigest() for p in paths},
        'environment': {'python': sys.version, 'platform': platform.platform(), 'processor': platform.processor(),
            'logical_cpus': os.cpu_count(), 'dependencies': {name: importlib.metadata.version(name) for name in ('numpy','scipy','numba','llvmlite')},
            'numba_cache_dir': os.environ.get('NUMBA_CACHE_DIR'),
            'threads': {name: os.environ[name] for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMBA_NUM_THREADS')}},
        'first_compile_or_cache_load': cold, 'rows': rows, 'sustained_fine_active': sustained,
        'total_wall_seconds': time.perf_counter()-started, 'total_process_cpu_seconds': time.process_time()-cpu_started,
        'peak_rss_bytes': peak_memory(), 'partial_reason': partial,
        'campaign_estimate': None, 'campaign_launch_ready': False,
        'limitations': ['Single process/serial kernel; process CPU covers all benchmark work but no process-tree concurrency test.',
            'Eight-step workload includes allocation, evolution, health checks, reference diagnostics and compression; excludes future stress/worldline/reconstruction/reporting work.',
            'RK4 samples use fixed NumPy input and evolving compiled input; full workloads start from identical arrays.',
            'Peak RSS is a process high-water mark, not per-case incremental memory.',
            'No physical late-time reference, 100-period error qualification, parameter selection or full-case speedup claim.',
            'Steady and sustained windows evolve synthetic fields and are timing evidence only.']}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
