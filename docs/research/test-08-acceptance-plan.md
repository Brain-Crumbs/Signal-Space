# Signal Space Test 8: path to full acceptance

This prospective design covers [issue #82](https://github.com/Brain-Crumbs/Signal-Space/issues/82), Program v0.2 §§7–10 and 15.6–15.9. It plans tests that can decide acceptance; it cannot promise that the physical hypothesis will pass. **No research evolution was started while preparing this plan.**

The [machine-readable design](plans/test-08-acceptance-design.json), [measured timing record](test-08-quiet-timing.json), and [preflight](../../scripts/preflight-test8-acceptance.py) form the planning handoff. This is a prospective design, not a `signal-space-plan-v1` runtime lock. Issue #82 prohibits inventing a locked configuration for an unavailable solver. The registered quiet experiment accepts exactly six periods and always leaves full exchange unevaluated. Its configuration cannot be relabeled as full acceptance.

The [performance and execution plan](test-08-performance-plan.md) adds code profiling, an equivalent compiled CPU backend proposal, complete restart, measured case scheduling and a bounded numerical-selection preflight. It targets a 2–7-day campaign conditionally, with 48 hours elapsed as a stretch target distinct from the existing CPU-hour ceiling. A saved synthetic kernel benchmark supports the optimization priorities; no optimized speedup or physical acceptance is claimed, and the matrix below is unchanged.

## Evidence and scope

Local run `run-2d17955e8ce845cb`, analysis `analysis-0001-641f2374`, report `report-0001` completed six periods in six configurations. Its six short checks pass; joint preparation and long clocks remain unresolved; full exchange is not evaluated. The canonical manifest hash is `049f8034ebf7f318bae32c2eb4ae80a2a06722ad80ad56b60b44d5915a0e34f9`. Packaging was recovered separately without rerunning physics. Evidence remains in the local `test8-quiet-005-recovery` package; this planning change does not claim new archival or scientific acceptance.

Retain the frozen omega_Q=0.900 source, omega_chi=0.41274991, local peak chi=0.001, and unchanged SS OCF 1 flat axisymmetric action. The old network epic #1 is a separate scope. Accepted radial Test 6/7 records support planning, but their full canonical bytes must be rehydrated and verified before dependent execution. A radial response or propagation operator cannot silently become a spatial one. New registrations will use Signal Space names; the design explicitly records this change from issue #82's historical, unregistered proposed ID.

## Staged test sequence

1. **S0 — Implement and validate the missing capabilities.** Derive physical stress/charge fluxes, absorber momentum sinks, moving-worldtube Reynolds terms, timelike tracking, proper-time markers and embedded-mode isolation. Implement complete restart state, independent numerical controls, classifiers and Test 9 reconstruction records. Validate manufactured axis-regular solutions, vacuum dispersion, translating-core diagnostics, Hamiltonian derivatives, flux signs, exact neutral zero and sign parity. Inject corrupted momentum, destroyed clocks, acausal markers and missing refinement to ensure classifiers reject them. Restart a small validation fixture and compare with uninterrupted evolution. Test packaging from saved fixtures before long runs: exact figure questions, immutable exports and mutable lock exclusion. Enforce actual Windows resource ceilings or use a supported environment with measured performance.
2. **S1 — Separate boundary effects and prepare the pair.** Compare six-period pairs in radius/axial-half-length 32/80, a larger 40/96 box at fixed width-4 sponge, and width 6 at the fixed base box. Repeat at h=0.2 and 0.1 with dt=0.005 fixed. This separates box size from sponge width. Solve the embedded clock eigenproblem and measure containment. Solve or freely settle joint initial data, prospectively capped at 20 preparation periods, saving all losses/residuals. Stop unresolved if usable preparation is not obtained; do not pin physical evolution or reset after adding the source.
3. **S2 — Demonstrate 100-period quiet usability.** Test isolated objects and the prepared pair at base/refined spatial grids, independent dt/2, larger domain with the same sponge width, and sponge-width-only controls. The illustrative isolated box is 32/48, enlarged to 40/64; pair boxes follow S1. Require less than 1% mode-energy loss and flux-corrected charge drift, less than 1% frequency deviation/jitter, and separate readable cores throughout 100 measurement periods. Pair costing includes up to 20 preparation periods. Add a third spatial grid if contraction is unresolved; its calibration cost is additional. Save complete prepared states and calibration uncertainties.
4. **S3 — Test at most six source-only physical candidates.** Allow at most three compact neutral packets and three compact structural perturbations, with numerical controls. Derive and freeze fields/canonical momenta, support, spectra, amplitude candidates and independent spatial receiver response before the pilot. Measure finite-beam invariant forcing and scattering; an ideal plane wave can have zero direct forcing. Structural radiation must be tested against its mass threshold, with a=pi_a=0 preserved. Select primary preparations using a frozen rule based on source-only evidence and independent receiver calibration, before inspecting held-out B histories. If no neutral candidate predicts resolved phase and impulse with survival headroom, stop with a mechanism/accuracy blocker.
5. **S4 — Run the complete held-out matrix.** Freeze source/calibration/configuration hashes, physical marker windows, nonzero normalization scales and numerical budgets after S3. Each run covers predicted last arrival and settling plus at least 20 independently calibrated signed-field periods. The 30-period cost example assumes arrival/settling fits into ten periods; massive group delay or greater separation can require more. No short cutoff can substitute for survival.
6. **S5 — Analyze independently and build the handoff.** Compare stress-flux impulse with direct worldtube momentum, form additive deterministic budgets, evaluate all G0–G9 gates and render the required figures. Save reconstruction data for a declared nonzero boost, provisionally v=0.1, including tilted-slice coverage, halos and time buffers. Verify withheld interpolation samples, canonical evidence, reader export and source recovery. Test 9 readiness becomes true only after every Test 8 gate passes; Test 9 invariance itself remains untested.

Stop on failed or unresolved prerequisites. Computational completion is never the scientific acceptance rule.

## Mandatory comparisons

The design includes 19 physical preparations with matched quiet references:

| Group            | Preparations                                                       | Purpose                                                        |
| ---------------- | ------------------------------------------------------------------ | -------------------------------------------------------------- |
| Baseline/neutral | Quiet; nominal, half, double and negative neutral amplitude        | Signal, amplitude behavior and whole-field neutral sign parity |
| B phase          | Changed-phase quiet and neutral                                    | Susceptibility and readout phase dependence                    |
| Structural       | Positive and opposite A perturbations, both neutral-free           | Separate structural emission/reception/recoil classification   |
| B removed        | Source quiet, neutral, positive structural and opposite structural | Source radiation, scattering and momentum attribution          |
| A removed        | Isolated B quiet and B with preserved initial neutral packet       | Reception without A-mediated scattering                        |
| Separation       | Larger-separation quiet and neutral                                | Causal window and attenuation                                  |
| Reflection       | Mirrored quiet and nominal neutral                                 | Reversed impulse and reflected scalar record                   |

For a conservative complete numerical envelope, run all 19 at five independently varied settings: base (h=.2, dt=.005), spatial (h=.1, same dt), temporal (same h, dt=.0025), larger domain at fixed h/dt/sponge width, and sponge width only at fixed domain. This gives 95 evolutions. Add h=.05 at dt=.005 for quiet, nominal neutral and both structural signs: 99 evolutions. Any other claimed effect or null bound with unresolved contraction needs a third grid too.

Refine event/output interpolation and extraction/worldtube placement independently using dense saved samples. If retained data cannot support this, add replay/evolution and its cost. A zero decimation difference on grid-aligned markers does not establish general interpolation accuracy.

## Acceptance map

The design JSON carries exact pass/fail/unresolved rules and fixed issue #82 thresholds.

| Gate | Required evidence                                                                                                                                                               |
| ---- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| G0   | Exact identities, verified Test 6/7 and prepared spatial prerequisites; pilot choices frozen before held-out receivers                                                          |
| G1   | Finite healthy initial data, positive Z, compact source support, accounted preparation energy/momentum and no later external work                                               |
| G2   | Primary neutral local cycle change >5 error budgets, contracting spatial error, no resolved pre-arrival change                                                                  |
| G3   | Receiver impulse >5 error budgets; independent flux/worldtube agreement; reflected impulse reverses                                                                             |
| G4   | Global and matched excitation-energy residuals <1%; momentum residual <1% on a nonzero scale; ledger uncertainty <20% of receiver impulse                                       |
| G5   | Both clocks survive >=20 post-settling periods; >=90% preinteraction mode energy at interaction end, >=99% post-settling retention, <1% charge drift/frequency deviation/jitter |
| G6   | Neutral null, sign/amplitude, phase, removed-object and quiet controls classified with forcing/response records                                                                 |
| G7   | Structural companion and source-only/numerical controls complete; a converged channel null is allowed                                                                           |
| G8   | Independent mesh/time/domain/sponge/output/extraction/preparation errors; tracking and causal precursors controlled                                                             |
| G9   | Verified canonical/reader files, eight visual groups, persistent physical events and reconstruction-ready history                                                               |

Use local chi and its proper-time derivative to form w=chi-i*p/Omega. The program's quadratic cycles are twice Test 7's signed-field cycles; save both and validate the conversion. Proper time comes from the measured timelike worldline, independently of the phase under test. Momentum includes radiation, neutral preparation and changing core energy; velocity times a fixed mass is insufficient.

Add absolute spatial, timestep, boundary, sampling, calibration/preparation and extraction/tracking errors. Do not assume deterministic contributions are independent random errors. Normalize small excitation/impulse errors to declared physical signal scales, not large core rest energy.

## Runtime projection and resource blocker

The [timing record](test-08-quiet-timing.json) comes from completed-run events, including setup/sampling/final serialization. It is wall time; the worker was observed occupying approximately one core, so it is only a CPU-equivalent proxy. Fine isolated evolution took 75.0 minutes and fine pair evolution 152.7 minutes for six periods. The full physics stage took 4.659 hours.

The preflight scales the closest measured case by cell count and integration-step count. It uses measured fine-grid timing rather than assuming coarse performance transfers across cache sizes. No parallel or accelerator speedup is credited. These are work projections, not measured completion times or confidence intervals:

| Stage                                                      | Costed evolutions |       Serial wall-time proxy | Two-times scheduling allowance |
| ---------------------------------------------------------- | ----------------: | ---------------------------: | -----------------------------: |
| S1 boundary discriminator                                  |                 6 |                       16.9 h |                         33.8 h |
| S2 longevity, including up to 20 pair preparation periods  |                10 |                      213.5 h |                        427.1 h |
| S3 six source candidates, base/refined, six-period example |                12 |                       29.0 h |                         57.9 h |
| S4 acceptance matrix, 30-period example                    |                99 |                    1,048.0 h |                      2,096.0 h |
| Costed total                                               |               127 | 1,307.4 h (54.5 serial days) |                      2,614.8 h |

Unpriced work includes S0, eigenmode/preparation solves, independent receiver calibration, new diagnostics/checkpoint overhead, extra grids, longer propagation/settling and S5/replay. Source-only costing conservatively retains the full proposed box; a smaller independently justified box could lower it. Third-grid scaling is particularly uncertain because it enters a new memory/cache regime. This is an explicit conservative matrix, not the minimum possible campaign.

Even simply extending the old six-case configuration from six to 100 periods projects about 77.7 serial hours, already above the issue's proposed 48 CPU-hour campaign budget. The full design needs at least 27.3 times the measured CPU-equivalent throughput to fit 48 hours, before unpriced work. Parallel cases reduce wall time but do not themselves reduce CPU-hours. A six-hour job limit requires checkpointed segments, not truncated observation.

Before launch, demonstrate equivalent optimized kernels and revised measured costs within the allowance, or explicitly approve a revised prospective budget. Benchmark the final diagnostics and restart path and re-estimate before locking. No speedup follows merely from available RAM or core count.

One fine-grid field state in the proposed 32/80 box is 31.25 MiB before diagnostics (two complex and four real float64 arrays). Saving full states every 0.4 time units for one 30-period case requires about 34.9 GiB uncompressed, above the entire 4 GiB output allowance. A declared checkpoint/replay and reconstruction-slab retention strategy is therefore a launch gate. Compression, peak memory and persisted size remain unmeasured; the old 150MB reading is not a campaign peak-memory estimate.

## Validation and manual use

The preflight checks G0–G9 coverage, all 19 preparations and quiet references, independent numerical changes, fixed thresholds, visual specifications, the six-candidate cap, source identity in Git LF representation, and timing arithmetic. Optional source verification checks the exact saved manifest/events. It never imports or calls a numerical solver. `--require-executable` returns exit code 2 while this is a design.

The current preflight also reports a machine-readable `readiness_checks` list. On this checkout it verifies the frozen Test 6 profile bytes, but identifies no registered full-exchange experiment, no locked S0–S5 stage plans, and no final-physics measured resource packet. The prospective design itself disables launch. These checks are a current-state audit, not a substitute for the S0 independent controls, verified Test 6/7 packages, complete numerical classifiers, or an actual measured campaign budget. A file's presence alone does not certify its scientific contents. After each missing capability is implemented, independently validate its plan, runtime configuration, evidence and resource measurements before changing the prospective design into a reviewed launch protocol.

At the original planning commit on 2026-09-28, six planning tests and 172 JavaScript/TypeScript tests passed. The measured timing source was verified against the saved manifest and events. The subsequent performance implementation repaired the then-existing `.venv` lint and Windows checkout-byte issues. For this readiness-audit update, seven planning tests and 17 focused numerical/restart tests pass; format, lint, type, contract, archive, JavaScript and 120 Python checks pass (one POSIX-only skip). Both production builds and CLI pair inspection pass when run with unsandboxed native Windows path resolution. All 15 browser cases reported pass, although the browser command did not exit cleanly in this sandbox and was interrupted after the results. These checks establish planning and implementation integrity, not physical acceptance or execution readiness.

From this checkout in PowerShell:

```powershell
$env:PYTHONUTF8 = '1'
python scripts/preflight-test8-acceptance.py
python scripts/preflight-test8-acceptance.py --require-executable
```

The first command validates and estimates. The second tests launch readiness and currently reports missing implementation/resource gates. **There is currently no correct full-acceptance launch command.** The six-period quiet launcher would repeat the completed prerequisite.

After S0 and stage registration, create each actual runtime configuration and its reviewed locked plan with prerequisite hashes. Validate with `.agents/scripts/experiment_contract.py plan PLAN`, then `.agents/scripts/run_plan.py --plan PLAN --repo-root . --workspace NEW_PATH` without `--execute`. Only after that preflight succeeds should the concrete stage command be manually launched with `--execute`. Pilot-dependent amplitudes and acceptance windows remain unset until S3 provides independent evidence.

## Visual and handoff plan

Eight required visual groups in the design JSON specify questions, observables, competing signatures, controls, transformations and uncertainty: prepared objects; field/energy flow; both local records; causal separation; recoil; survival; channel controls; decision margins. Spatial views illustrate propagation; physical flux and local event records support the quantitative claims. Every figure must reuse its exact locked question to prevent the quiet-005 packaging fault.

Do not infer binding, generic 3D stability, topology, emergent spacetime, autonomous emission or gravity from this flat axisymmetric campaign. Preserve all earlier failed/unresolved evidence.
