# Test 8 CPU backend and quiet restart

Engineering implementation for [issue #82](https://github.com/Brain-Crumbs/Signal-Space/issues/82), extending the [performance plan](test-08-performance-plan.md). This implements the serial CPU speedup and complete restart for the existing quiet prerequisite. It does not register the full exchange solver or qualify new physical settings. All Test 8 acceptance gates retain their existing status.

## Equations and precision

The optional `numba` backend implements the same annular finite-volume action and RK4 method as `AxisGrid`/`AbsorbingGrid`: Program v0.2 §§7–10 and 15.8, the [spatial Hamiltonian](gross-test-08.md#action-and-numerical-mapping), and the [quiet absorber sinks](gross-test-08-quiet.md#locked-question-and-preparation). It uses complex128 core fields, float64 real fields, serial reductions and `fastmath=False`. The reference Hamiltonian, local tracking and moving-center interpolation remain independent NumPy diagnostics.

Density is calculated once per stage; fixed geometry is cached as radial vectors. Compiled loops fuse face divergence, reciprocal forces and sink reduction. Four derivative buffers and a separate stage buffer are allocated once per integrator. `CompiledStepper` copies its initial state, owns its buffers, and updates its owned fields on `advance`. Its `state` property is a live view: callers retaining snapshots must copy or serialize them before advancing. Each case needs its own integrator.

`neutral_mode: exact-zero` skips neutral spatial calculations only for the registered homogeneous equations with exactly zero initial field and momentum. It rejects even a subnormal nonzero value. Full-backend neutral-null controls remain available. No amplitude threshold, altered stencil, source, center force or reduced precision is introduced.

The optional environment pins Numba 0.67.0 and llvmlite 0.49.0 alongside the existing dependency lock. The Windows CPython 3.14.6 / NumPy 2.3.5 wheel and compilation smoke test passed in a separate environment. The runtime records the installed compiler versions in execution identity, so resume rejects a different compiler environment. The [official support table](https://numba.readthedocs.io/en/stable/user/installing.html#version-support-information) describes the supported version combinations; local tests establish this implementation's evidence.

## Opt-in configuration

The historical quiet fixture and locked plans keep their exact bytes. Its schema still locks every physical, sampling, resource and acceptance parameter. A new configuration may additionally include this object under `parameters`:

```json
{
  "execution": {
    "backend": "numba",
    "neutral_mode": "exact-zero",
    "checkpoint_stride": 5000
  }
}
```

Use `neutral_mode: full` for independent null controls or any active neutral field. Omitting execution options retains the NumPy reference. Explicitly requesting Numba when it is absent fails; there is no silent backend substitution. New execution choices change the configuration/run identity and require a new prospective lock before physical execution.

The retained-state estimate is now explicit: the default 1,000-step checkpoint cadence projects 1,011 MiB and is rejected against the old 512 MiB output ceiling. The example 5,000-step cadence projects 324 MiB before extra resume attempts. This is a retention choice, not a change to sampling or physical observation duration. The old CPU/wall estimate remains a legacy value and must not be treated as measured optimized throughput; the separate campaign preflight remains blocked.

Create an isolated environment and install `python/requirements-performance-lock.txt`; do not upgrade the evidence-producing environment in place. The engineering benchmark can be run without a physical profile:

```powershell
.research-work/test8-perf-env/Scripts/python.exe scripts/benchmark-test8-backends.py --output .research-work/new-backend-observation.json
```

The output path must be new. The default harness compares all three proposed grids with quiet and active synthetic arrays, retains three wall/CPU samples, measures an evolving eight-step workload including reference diagnostics and compression, runs three ten-second steady windows for each compiled case, and runs a five-minute fine active-neutral window. Its aggregate caps are 30 wall minutes and two process CPU hours; it launches no children. Compilation/cache loading is separate. Set a new `NUMBA_CACHE_DIR` to measure cold compilation.

## Measured engineering result

The [saved backend observation](test-08-backend-timing.json), produced by [the bounded harness](../../scripts/benchmark-test8-backends.py), took 750.34 wall seconds and 749.58 process CPU seconds. It used a fresh compiler cache: first compilation plus one tiny step took 1.54 seconds. Process peak resident memory was 1.34 GiB. No child workers were launched.

| Grid                   | Quiet step speedup (exact-zero) | Active-neutral step speedup (full) | Quiet eight-step workload speedup | Active eight-step workload speedup |
| ---------------------- | ------------------------------: | ---------------------------------: | --------------------------------: | ---------------------------------: |
| h=.2, 128,000 cells    |                           4.13× |                              3.27× |                             2.63× |                              2.26× |
| h=.1, 512,000 cells    |                           5.55× |                              4.48× |                             3.61× |                              2.98× |
| h=.05, 2,048,000 cells |                           5.48× |                              5.21× |                             3.10× |                              3.29× |

These ratios compare measurements in the same preflight, not the older machine timing. The evolving workload includes initialization/buffers, eight steps, health checks, two independent energy/tracking samples and one compressed state. It is deliberately a short workload with frequent output; it is not a six-period physical run. The full compiled backend also speeds up quiet data without specialization (4.59× per fine-grid step), preserving a practical independent null control.

The five-minute fine active-neutral window completed 1,703 steps at 0.1762 seconds/step and ended with finite fields. Three ten-second windows per compiled case are retained in the observation. The fine compressed state was 16.59 MiB quiet or 22.76 MiB active; the third grid was 72.92/98.12 MiB. These measurements do not price Test 9 slabs, replay, future stress diagnostics or full campaign storage. The first 4× **complete physical case** target is not yet demonstrated.

## Restart scope and storage

The quiet worker writes an atomic compressed NPZ followed by a hash-bearing JSON checkpoint. JSON publication commits the checkpoint only after the state file is durable. Checkpoints are immutable, retained rather than overwritten, and indexed by cumulative step. They contain all six fields, both accumulated RK4 sinks, exact grid/absorber arrays, case and step position, initial ledgers, maximum neutral amplitude, complete clock sample history, completed case metadata/output hashes, preparation identity and the unused seed ledger. Physical time is exactly the case's step index times its locked timestep.

Resume uses the runtime's existing new-attempt lifecycle and config/code/environment verification, then verifies payload hashes and grid identity. Completed outputs are copied into the new attempt for self-contained analysis; the previous attempt is unchanged. A cancellation request is checked each step. If hard termination interrupts compression, the last published checkpoint remains usable; the interrupted write is not a valid checkpoint. Retention and copied completed outputs consume storage and must remain in the budget.

Quiet centroids and projections are stateless functions of each saved field. Crossings are derived from the full sample history, which split-run tests retain across a crossing event. This prerequisite has no dynamical worldtube, proper-time, phase-unwrapping, stress-flux or random evolution state. The checkpoint does not claim to implement those future full-exchange features or Test 9 tilted-slice retention/replay.

## Remaining qualification

Implementation validation on Windows with Node 24.19.0/npm 11.9.0 and the isolated pinned Python environment: all 17 focused numerical/restart tests, all 172 JavaScript tests, 119 Python tests (one existing POSIX-only skip), 15 browser tests, both production builds and the CLI pair inspection passed. Benchmark source hashes match the checked-in implementation. The browser tests use the configured `PYTHON` executable; run their preview launcher through the native Windows shell.

Validation also repaired three portability problems: lint/format no longer scan local dependency environments, report evidence paths use portable forward slashes, and byte-indexed research archives plus the synthetic locked fixture disable checkout newline conversion. Existing CRLF copies were restored to their exact committed/locked bytes; no archive hash or historical evidence content was changed. Clean-working-tree repository validation and its final outcome are recorded in the PR.

Backend equivalence uses prospective `rtol=1e-12`, `atol=1e-14` field/sink comparisons, including active neutral data, absorber/axis/boundary cells and accumulated evolution. Independent controls cover manufactured axis solutions, vacuum neutral dispersion, the discrete Hamiltonian derivative and neutral sign/null behavior. Restart tests compare uninterrupted and split fields/samples exactly and reject corruption.

Short synthetic agreement cannot certify the tiny physical receiver signal or long-time phase error. The full local-cycle/impulse allowance (at most 10% of each numerical error budget), time/space convergence, actual clock horizons, Windows process-tree limits, multi-case scheduling, Test 9 reconstruction retention, and numerical parameter/source selection remain qualification gates. No parallel workers or campaign are launched by this change. Missing components remain unknown costs, not zero, and full acceptance launch readiness stays false.
