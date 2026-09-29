# Signal Space Test 8: performance and execution plan

Status at planning: prospective engineering plan for [issue #82](https://github.com/Brain-Crumbs/Signal-Space/issues/82), extending [PR #85](https://github.com/Brain-Crumbs/Signal-Space/pull/85). The subsequent [CPU backend and quiet restart implementation](test-08-performance-implementation.md) records implemented scope and qualification limits. No acceptance campaign or changed scientific threshold is implied by either engineering benchmark; original locked configurations remain unchanged.

## Recommendation and expected turnaround

Optimize the code first, then use a small numerical preflight to select affordable settings that meet the same error budgets. Do not launch the current full campaign. Target a useful engineering preflight in **15–30 minutes**, a qualified six-period fine pair in **15–35 minutes**, and a full campaign in **2–7 days** after implementation. These are development targets, not measured optimized runtimes or promises of scientific acceptance. Use **48 hours elapsed** as the provisional preferred campaign target; the existing **48 CPU-hour** allowance is a separate constraint and has not been increased.

The full acceptance design represents 127 evolutions, not one two-object demonstration. Its 1,307.4-hour serial projection is credible as a warning about the current implementation and conservative matrix. It is not an unavoidable physical cost, nor evidence that a simple smoke test should take weeks. A quick diagnostic can finish in minutes; the required 100-period longevity and post-interaction survival evidence cannot be inferred from it.

The first implementation milestone should deliver a measured profile, an equivalent compiled CPU kernel, complete restart, and a cost report. Only then decide whether the complete matrix fits this computer and the agreed resource allowance. If performance gains are insufficient, report the measured time and budget needed; do not silently shorten survival or delete controls.

## Evidence: where the time goes

The [saved physical-run timings](test-08-quiet-timing.json) are the campaign costing basis. They include setup, sampling and final serialization and are wall measurements, not instrumented CPU totals.

| Existing six-period case |   Cells |  Steps | Observed elapsed | Average step-equivalent time |
| ------------------------ | ------: | -----: | ---------------: | ---------------------------: |
| Isolated base            |  38,400 |  9,134 |         3.60 min |                      23.7 ms |
| Isolated fine            | 153,600 | 18,267 |         75.0 min |                       246 ms |
| Pair base                |  76,800 |  9,134 |         9.08 min |                      59.6 ms |
| Pair time control        |  76,800 | 18,267 |         21.1 min |                      69.2 ms |
| Pair fine                | 307,200 | 18,267 |        152.7 min |                       502 ms |

At fixed timestep, pair-fine costs 7.25 times pair-time for four times as many cells: about 1.81 times worse per cell-step. This is consistent with memory/cache/allocation costs, but does not prove their cause. The proposed 32/80 box has 128,000, 512,000 and 2,048,000 cells at h=.2, .1 and .05. Thirty signed-field periods at dt=.005 require 91,336 RK4 steps, each with four field-update evaluations. Simple geometry still entails substantial numerical work.

The current estimator projects **21.2 hours** for one fine 30-period pair, **84.8 hours** for one third-grid case, and **84.8 hours** for a fine pair's 100 measurement plus 20 preparation periods. Four third-grid cases alone account for **339.4 hours**, roughly 26% of the total. They need their own benchmark; coarse-grid throughput is an inadequate predictor.

### Short benchmark performed for this plan

[Reproducible harness](../../scripts/benchmark-test8-kernels.py) and [saved observation](test-08-kernel-timing.json). The 58.7-second benchmark repeatedly evaluated the existing routines on the same smooth synthetic arrays, discarded each result, and never advanced a physical history or read the accepted clock profile. Each operation has one untimed warm-up and three timing samples; profiling is separate. Inputs include both exactly zero and nonzero neutral fields.

Observed environment: Intel Core i9-10900KF (registry identification), 20 logical CPUs reported by Python, Windows, CPython 3.14.6 and NumPy 2.3.5. Numba is not installed. Usable RAM, GPU capability, sustained thermal behavior and physical-core scheduling were not verified; no speedup is credited to them.

| Proposed grid | Quiet RK4 step | Active-neutral RK4 step | Active energy/charge evaluation | Active health/neutral scan |
| ------------- | -------------: | ----------------------: | ------------------------------: | -------------------------: |
| h=.2          |         171 ms |                  175 ms |                         28.6 ms |                    0.56 ms |
| h=.1          |         927 ms |                  925 ms |                          156 ms |                    4.66 ms |
| h=.05         |       3,980 ms |                3,989 ms |                          657 ms |                    27.6 ms |

These synthetic timings are not replacements for complete-run measurements. The fine active profile attributes 82.4% of step time cumulatively to `rhs_with_sinks`, including the spatial update; RK stage construction and combination account for about 16.2% by self time. Face construction/divergence and array arithmetic are visible hotspots. Do not add cumulative percentages to their nested functions. Health scans are small; removing safety checks is not the useful first optimization. Zero neutral arrays currently cost almost the same as active arrays.

Code inspection identifies the following work:

- [AxisGrid](../../src/signal_space/numerics/two_object.py): repeated face arrays, zero-filled divergence accumulators, coefficient averages, polynomial temporaries and full-grid passes. Geometry is stored as repeated 2D arrays although much depends only on radius.
- [Quiet integrator](../../src/signal_space/numerics/two_object_quiet.py): four field-update evaluations plus allocated intermediate states per RK4 step; recomputed density/stiffness in the sink calculation; all neutral work executed even in the exactly invariant zero sector.
- The same module loops through scenarios sequentially, computes moving mode projections at sample times, and rejects resume. Final NPZ data is not yet a complete accepted restart protocol.
- [Runtime worker](../../src/signal_space/runtime/worker.py): OS resource limiting is applied on POSIX. Full Windows process-tree accounting/enforcement must be established before running multiple workers under a campaign budget.

## Work packages, in execution order

### P0 — Establish the benchmark and cost contract

Extend the synthetic harness into a registered, bounded engineering fixture with separate timings for preparation/eigenmode solves, field updates, local sampling/tracking, independent flux diagnostics, checkpoints, compression and reporting. Retain the current NumPy implementation as the reference. Record cold compilation separately from warm throughput; report median, range, process-tree CPU seconds, peak resident memory and bytes written. Save exact input, code, dependency and hardware identities.

Benchmark all three actual grid sizes, quiet and active-neutral data, an evolving short fixture, and a representative late-time state. Tail amplitudes and cache behavior may change cost. Run three 10–30-second steady windows, then one five-minute sustained window on the selected implementation. Impose an aggregate 30-minute wall and two CPU-hour preflight cap; stop with partial evidence when the cap is reached. This cap does not authorize a physical parameter scan.

Deliverable: a measured per-case estimator with upper scheduling allowance, not a constant derived from one coarse grid. The present solver-free acceptance preflight remains the scientific coverage checker. Add performance inputs separately; missing measurements must produce an unknown estimate or a launch blocker, never zero cost.

### P1 — Preserve the equations; reduce array traffic and compile the hot loop

1. Preallocate separate RK stage/work buffers; write into them with explicit aliasing rules. Cache fixed geometry as radial vectors and cache static masks. Compute density, Z and polynomial terms once per stage where their values agree. Preserve moving-center interpolation; do not freeze a tracked mode merely to save time. NumPy's `out` arguments allow reusable result storage [R1].
2. Implement a fused float64/complex128 CPU backend using Numba `njit` loops, retaining the reference backend. Compile the stencil, local forces, stage assembly and sink reduction; decorating the existing allocation-heavy wrapper alone is not the objective. Derive the same cell volumes, axis face, boundary conductances and coefficient averages. Begin serial with `fastmath=False`; benchmark parallel loops only after equivalence passes. Numba supports compiled loops and parallel execution, while fast-math permits changes to floating-point semantics [R2].
3. Pin a tested toolchain in an isolated environment and record it. The official compatibility table currently lists Numba 0.67.0 with Python 3.14 and NumPy 2.3 within its supported ranges [R3]. This makes it a candidate, not an installed or tested dependency. Confirm the Windows wheel/import/compiler smoke test. If unavailable, use an explicitly pinned supported Python environment or Cython typed memoryviews; do not mutate the evidence-producing environment. Cython provides typed buffer access and OpenMP loop parallelism [R4].
4. Add an explicit exact-zero neutral specialization for quiet and neutral-free structural cases. Enable it only when initial a and pi_a are identically zero and the registered equations/boundaries cannot source them. Retain zero arrays in saved state, test agreement with the full backend, and still run full-backend neutral-null controls. Never threshold a small physical neutral field to zero or use this specialization for active packets.

First performance target: **at least 4× complete-case acceleration** on the fine grid; next target **8×**, with **16×** a stretch goal to investigate. Targets apply to the total measured workload, including required diagnostics, not just a favorable stencil timer. Do not multiply claimed buffer, compilation and threading gains independently; they may address the same bottleneck. If the field-update portion alone became infinitely fast, the measured 82.4% fraction would cap this microbenchmark near 5.7×. Larger gains require improving stage arithmetic and the full execution path too.

### P2 — Equivalence, correctness and complete restart

Keep the action, physical preparation, RK4 method and precision unchanged for the first backend. Reuse and extend the independent manufactured-axis solution, vacuum dispersion, Hamiltonian derivative, neutral sign/null, boundary flux and translating-core checks. Cover sponge and boundary cells and nonzero neutral data. Compare reference/optimized derivatives and one-step fields on declared nonzero scales; a prospective starting tolerance is rtol=1e-12, atol=1e-14 in normalized field units. Investigate failures rather than relaxing tolerances after seeing acceptance results.

For accumulated local cycles, impulse and matched energy residuals, require backend discrepancy to fit within a separately allocated allowance of at most 10% of each corresponding numerical error budget. Sum this allowance with the other deterministic errors. The tiny signal scale, not core rest energy, governs that test. Repeat time/space convergence and the actual clock horizons before using optimized results for acceptance. Short equivalence does not establish long-time phase agreement. Keep classification rejection fixtures for destroyed clocks, incorrect momentum, acausal markers and missing refinement.

Implement atomic checkpoints containing fields/canonical momenta, grid, physical time/step, sinks, accumulated stress/flux integrals, tracker/worldtube state, proper times, unwrapped phases, event/interpolation history, preparation provenance and any RNG state. Resume appends a new attempt after identity/hash verification. Compare uninterrupted and split runs, including restart across a local event. Cancellation and packaging must work from saved state. Schedule segments below the six-hour job ceiling without cutting physical observation time.

### P3 — Benchmark case scheduling and bound storage

Compare one process with 1/2/4 kernel threads against 2/4 independent cases with one thread each. Test eight workers only if measured RAM and aggregate throughput justify it. Control nested BLAS/OpenMP threads, cap process-tree CPU/memory/output, and stop increasing concurrency when bandwidth contention worsens throughput. NumPy releasing the GIL does not mean this sequential case loop already uses all cores [R5].

Use independent registered case packages or isolated case outputs under one coordinator; multiple workers must not append to the same manifest/event file. Preserve deterministic case identities and aggregate checks only after their outputs verify. Reuse identical prepared checkpoints and matched quiet references by hash only when preparation, grid, phase, marker windows and diagnostics truly match. Different meshes require their own preparation/calibration. Reuse already-valid data windows only after verifying alignment and full record coverage.

Maintain dense local records and integrated ledgers, plus sparse restart states and declared reconstruction slabs. A fine state is 31.25 MiB before diagnostics and work buffers; a third-grid state is 125 MiB. Even one uncompressed final state per S4 case totals about **1.72 GiB**, before calibration, checkpoints and Test 9 history. Saving fine full states every .4 time units costs about 34.9 GiB for just one case. The existing 4 GiB campaign ceiling is therefore a genuine design gate.

Measure compression, replay time, interpolation error and a retained-size manifest. For the declared nonzero Test 9 boost, retain the required tilted-slice coverage, halos and time buffers; local traces alone are insufficient. Validate withheld interpolation samples. If replay is used, include its compute and exact restart dependencies in the estimate. Do not delete immutable checkpoint evidence or omit required reconstruction data to report compliance. A larger archival allowance needs an explicit prospective budget revision.

### P4 — Bounded numerical selection, then physical source pilots

This is the parameter component, after the code improvement. It minimizes measured cost subject to the unchanged error bounds; it does not optimize the appearance or size of B's held-out response.

| Parameter                  | Bounded preflight                                                                                                              | Selection and restrictions                                                                                                                                                                                                                         |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Timestep                   | At fixed h, compare .005 with .0025; test .01 only on h=.2/.1 where allowed                                                    | Choose by clock phase, energy/impulse and dispersion error. The existing safety bound is dt <= .25h/sqrt(2); at h=.05 it is .00884, so .01 is inadmissible. A spatial-convergence family keeps dt fixed. Do not credit a uniform 2× timestep gain. |
| Spatial grid               | h=.2/.1 with h=.05 for the already required primary cases                                                                      | Coarse runs screen invalid preparations; only converged evidence decides acceptance. Do not remove third-grid checks because they are costly.                                                                                                      |
| Domain and sponge          | Existing 32/80 versus 40/96 boxes at width 4; width 6 at the base box, independently                                           | Select using containment, reflected flux and boundary error over the required observation window. A short early run cannot qualify a smaller long-time box.                                                                                        |
| Output and extraction      | Compare dense records with prospectively decimated/interpolated copies and separate worldtube placement                        | Retain derivative/event information; require sampling/extraction contributions inside the allocated budgets. Sampling reductions do not reduce integration steps.                                                                                  |
| Preparation and separation | Measure containment and quiet-pair transients; retain the 20-period preparation cap                                            | Do not reduce separation below the containment/causal requirement or re-relax after source insertion. Stop unresolved if preparation fails.                                                                                                        |
| Physical source            | At most three neutral and three structural candidates, selected from source-only evidence and independent receiver calibration | Freeze support, spectrum, amplitude, propagation/settling window and prediction rule before inspecting held-out B histories. Preserve every pilot and the six-candidate cap.                                                                       |

Avoid a Cartesian product of every knob. Tune one numerical dimension at a time on the same prepared reference, retain its independent control, and recheck the combined selected settings. Allocate deterministic errors additively. Qualification of a short pilot does not replace S2's 100-period checks or S4's at least 20 post-settling periods.

The [current acceptance design](plans/test-08-acceptance-design.json) retains all 19 physical preparations and its 99-case numerical matrix. No matrix reduction is assumed in the runtime targets. A later risk-based numerical envelope could be proposed against issue #82, but it would need an explicit new design, per-observable coverage and prospective review. A weaker grid or missing control cannot silently become a performance optimization.

### P5 — Reprice and run the gated campaign

Complete the missing physical source, recoil, stress/flux, proper-time/local event and reconstruction capabilities from S0 alongside the performance work. Rerun the timing fixture with those capabilities enabled. Check canonical Test 6/7 evidence, spatial calibration and runtime registration. Neither this plan nor the existing six-period launcher is a full-acceptance launch command.

Execute S1 boundary/preparation first, S2 longevity next, S3 source feasibility only when prerequisites pass, then the locked S4 acceptance matrix and S5 analysis/export. Stop dependent work on failed/unresolved prerequisites. Preserve partial evidence and distinguish resource exhaustion from scientific failure. Within an independent stage, schedule the measured slow cases early while respecting dependencies and resource ceilings.

Before every stage, show expected and upper elapsed time, process-tree CPU-hours, peak memory, retained bytes, prerequisites, checkpoints and remaining campaign allowance. Stop before launch if any required estimate, prerequisite or allowance is missing. The full campaign is a go only after its **measured upper estimate** fits the selected elapsed target and separately approved CPU/storage ceilings.

## What would make 48 hours possible?

Let S be complete-workload acceleration at fixed thread allocation and fixed scientific work, and C the measured aggregate throughput factor from concurrent scheduling of that optimized workload. For the currently costed 1,307.4 serial hours:

`nominal elapsed = 1307.4 / (S × C)`

Use twice that value as scheduling headroom, then add newly priced preparation, calibration, replay and reporting work. This is sensitivity arithmetic, not a forecast or a statistical confidence interval. Actual scheduling must also account for stage barriers and the longest indivisible job; C is not automatically the worker count. Multithreaded S is not a CPU-hour reduction by the same factor.

| Measured code/work gain S | Measured concurrent throughput C | Costed-work nominal elapsed | With 2× scheduling headroom |
| ------------------------: | -------------------------------: | --------------------------: | --------------------------: |
|                        4× |                               4× |                      81.7 h |          163.4 h / 6.8 days |
|                        8× |                               4× |                      40.9 h |           81.7 h / 3.4 days |
|                       16× |                               4× |                      20.4 h |           40.9 h / 1.7 days |

The **8× CPU implementation plus measured concurrent throughput** is the initial practical objective. It makes a multi-day campaign a useful target. A 48-hour commitment needs roughly **54.5× combined throughput** for the costed work with this headroom; 16× code and 4× concurrency leaves only about seven hours for additional costs. There is no measured optimized gain yet.

On the old single-core CPU-equivalent proxy, a strict 48 CPU-hour allowance instead requires **27.3× work reduction/serial acceleration before overhead**, or 54.5× with the same headroom. Parallel cases cannot solve that constraint. Instrument actual CPU use and retain this as a separate launch blocker. At 8× serial speed, the costed work is still approximately 163 CPU-equivalent hours.

At 8×/16× serial gains, the projected fine six-period case becomes about 32/16 minutes, the fine 30-period case about 2.65/1.33 hours, and the fine 120-period pair about 10.6/5.3 hours before new overhead. Checkpoint segmentation makes the longer cases manageable. It does not reduce their total work.

## Escalation if the CPU plan misses the target

First use measured error budgets to assess whether a larger timestep or smaller qualified source-only box can reduce work. Do not increase neutral amplitude merely to swamp numerical error; use the capped source-only selection and survival headroom. Do not replace 3D-axisymmetric acceptance with radial evidence.

If CPU fusion and scheduling still miss the target, prototype one device-resident float64 GPU step and its full diagnostic/output path. Require actual device/VRAM identification and end-to-end measurements. CuPy documents asynchronous execution, cold initialization/compilation and synchronized timing [R6]; changing imports or timing only kernel submission is not evidence of acceleration. Revalidate precision, conservation and restart across that backend. No GPU purchase or remote compute is assumed or authorized by this plan.

Higher-order spatial methods, mesh refinement and a different integrator are later research/engineering options. They change numerical error and boundary/axis treatment and need new discretization validation. Standard explicit Verlet cannot simply be substituted for RK4: the canonical Hamiltonian contains pi_a²/(2Z(Phi)), and damping/sink quadrature also needs an action-consistent treatment. Start with the equivalent compiled RK4 path before taking on these risks.

## Deliverables and validation

1. **Performance baseline:** reproducible component and full-fixture timings, CPU/RAM/storage measurements, environment lock, three-grid estimator and explicit unknowns.
2. **Equivalent CPU backend:** preallocated/fused updates, reference comparison, independent controls, exact-zero specialization with full-backend null validation.
3. **Reliable execution:** complete checkpoint/restart/cancellation, bounded case scheduling, immutable outputs and tested reconstruction retention/replay.
4. **Qualified numerical settings:** independent timestep/grid/domain/output/error decisions and a capped source-only pilot design, with no held-out response tuning.
5. **Launch packet:** measured final cost and budget decision, registered stage configs and actual locked plans only when implemented, complete G0–G9 coverage, preserved 100/20-period gates, eight evidentiary visual groups and Test 9 data audit.

Implementation PRs must follow the current Python validation in AGENTS.md, numerical equivalence/restart tests, runtime integration checks and byte-preserving evidence verification. This planning change does not establish those future implementation gates.

Validation for this planning update: the six existing campaign-design tests, eight spatial/quiet numerical and packaging controls, and solver-free preflight pass; the saved benchmark's four source hashes match the Git-LF representations; the harness compiles and refuses to overwrite the saved observation. Local document links and `git diff --check` pass. Formatting passes with Node 24.19.0/npm 11.9.0. The full repository check stops at the existing 74 lint errors in third-party `.venv` JavaScript; later gates are not represented as having passed in this update. The prior PR records separate archive/fixture hash limitations. No web, shared execution path or numerical engine was changed.

To reproduce the short engineering observation without running an experiment (choose a new output path):

```powershell
python scripts/benchmark-test8-kernels.py --output .research-work/test8-kernels-new.json
python scripts/preflight-test8-acceptance.py
```

The benchmark refuses to overwrite its output and has fixed grids/repetitions. It has no campaign launch option. The acceptance preflight continues to report `execution_ready: false`.

## Primary technical references

Sources checked 2026-09-28. These document mechanisms and compatibility; none supplies a speedup measurement for Signal Space.

- **R1:** [NumPy 2.3 ufunc output buffers](https://numpy.org/doc/2.3/reference/generated/numpy.ufunc.html).
- **R2:** [Numba performance guidance: compiled loops, parallelism and fast-math semantics](https://numba.readthedocs.io/en/stable/user/performance-tips.html).
- **R3:** [Numba version support table and Windows installation](https://numba.readthedocs.io/en/stable/user/installing.html#version-support-information).
- **R4:** [Cython typed memoryviews](https://docs.cython.org/en/latest/src/userguide/memoryviews.html) and [parallel loops](https://docs.cython.org/en/latest/src/userguide/parallelism.html).
- **R5:** [NumPy 2.3 thread safety and GIL behavior](https://numpy.org/doc/2.3/reference/thread_safety.html).
- **R6:** [CuPy performance measurement, warm-up and asynchronous execution](https://docs.cupy.dev/en/stable/user_guide/performance.html).

Scientific mapping remains Program v0.2 §§7–10 and 15.6–15.9, the unchanged flat SS OCF 1 action and issue #82. Epic #1 is historical network scope. Tests 6/7 and their canonical artifacts retain their original statuses; synthetic kernel timing adds no physical acceptance claim.
