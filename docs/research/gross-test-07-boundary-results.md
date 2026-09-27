# Test 7: causal boundary prerequisite passes

**The next registered linear test passed all six checks. Full Test 7 acceptance has not been demonstrated; Test 8 remains blocked.**

Run `run-cbe4ee3c4897af06`, analysis `analysis-0001-7f0eb43d`, reviewed report `report-0002`. Fifteen cases cover three incident waveforms and five spatial, temporal and domain variants. The solver completed in about eleven minutes. The locked action, profiles, thresholds and numerical settings were not changed after execution.

## Result

| Locked check                                  | Result | Evidence                                                                                           |
| --------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------- |
| Frozen inputs and forecast-before-audit order | Pass   | All source and forecast hashes and event ordering verify                                           |
| Local waveform reconstruction                 | Pass   | Maximum relative L2 error 2.43e-9; limit 1e-5                                                      |
| Frozen linear energy                          | Pass   | Maximum initial-to-final relative drift 3.62e-11; limit 1e-6                                       |
| Separate prospective event budgets            | Pass   | Largest finest event error 1.20e-7; largest budget 4.28e-6; limit 1e-4                             |
| Absolute event convergence                    | Pass   | Mesh changes contract under the locked criterion; largest finest change 0.0812, below the 0.1 gate |
| Surface and local sampling                    | Pass   | Largest event change 2.27e-6; limit 1e-4                                                           |

The event errors and budgets below are in inverse-mass time units. The primary method uses the complete two-site surface history through time 60 and retains exterior memory. Each waveform uses the first rise and first subsequent fall of the local absolute field through 1e-4.

| Waveform | Rise error | Rise budget | Fall error | Fall budget |
| -------- | ---------: | ----------: | ---------: | ----------: |
| Broad    |    6.21e-8 |     2.98e-6 |   9.59e-13 |     1.00e-7 |
| Carrier  |    1.20e-7 |     4.28e-6 |    1.83e-9 |     1.47e-7 |
| New      |    1.76e-8 |     3.75e-7 |   4.90e-10 |     1.09e-7 |

## What resolved the previous failure

The previous capture method discarded the exterior state at time 16. Here the predictor retains the exterior's causal response through an auxiliary evolution. Two observed surface sites determine the incoming free drive after subtracting the exterior response to the measured inner surface. Only these records and the frozen operator enter the predictor. Known-source local histories are computed after each forecast is saved and hashed.

Suppressing exterior memory gives relative waveform errors of 1.0005, 1.0017 and 1.0010 on the finest grid. Complete memory gives 2.45e-10, 2.36e-9 and 8.73e-10. This strongly supports the diagnosis that the earlier abrupt truncation caused the large late ringing.

Cutting only the incoming drive at time 16 while retaining memory gives much smaller waveform errors: 1.94e-6, 5.54e-7 and 8.39e-7. Its first-excursion events agree with the full-input events at saved precision. Nevertheless, its broad-wave historical last-fall residual is 1.39e-4, above the new 1e-4 target. Complete acquisition reduces that diagnostic residual to 2.92e-9. The old capture protocol and inverse robustness failure remain unchanged.

This is an offline forecast from an acquired frozen-linear surface record. Acquiring through time 60 is an explicit change from the old finite window. The first-complete-excursion rule is also a new prospective event definition. Neither change retroactively passes the original Test 7.

## Limits that matter for acceptance

The small reconstruction residual compares source and predictor on the same discretization. Absolute first-event shifts between the two finest grids remain 0.0616, 0.0812 and 0.0428. The registered contraction test passes, but this does not certify absolute continuum timing to 1e-4. Clock-interval uncertainty must propagate these endpoint changes together with changes in the phase trajectory.

No nonlinear receiver, local phase forecast, amplitude/sign/clock-phase controls, two-pulse interaction record or nonlinear conservation ledger was executed in this run. The first excursion of a single pulse does not by itself provide an interval spanning the two-pulse interaction. There is no physical noise model. The independently tested discrete Hamiltonian, dense-exponential fixture and causal suffix tests support implementation accuracy within these limits.

## Concrete next calculation

The nonlinear bridge must be derived before launching another acceptance suite. The auxiliary exterior field here is a state-space realization of memory; it is not the physical total incident exterior field. Inserting it unchanged into the nonlinear Taylor solver would produce incorrect quadratic neutral forcing near and outside the interface. The nonzero frozen core tail at radius 14 also prevents assuming that all exterior core forcing vanishes.

For the existing linear partition, write the physical exterior as the free incoming part plus its boundary-driven response. In the nonlinear extension, derive the corresponding exterior response at each retained perturbative order, including the neutral kinetic coefficient on the evolving quiet core and the quadratic core source. Alternatively, register a farther acquisition surface and explicitly bound every omitted exterior contribution. Moving the surface alone is not an error bound.

The first discriminator should compare this surface-driven Taylor forecast with a separately labeled known-source Taylor control. Source initial data may enter that control only. Agreement must be judged on the local phase trace and interval, with independent interface-radius, spatial, temporal and sampling changes; the primary predictor must never receive source initial data or receiver interior samples. A resolved discrepancy rejects that boundary closure before expensive receivers are run.

Once that closure is controlled, lock a fresh waveform and operational event interval, then save the complete phase forecast before any nonlinear receiver evolution. Execute quiet, each pulse alone, both pulses, sign reversal, half/nominal/double amplitude, changed clock phase and frozen-core controls. Include endpoint and reconstruction errors in the complete cycle budget. Preserve the Test 7 requirements that the nonzero interval exceed five budgets and forecast error stay below the larger of 5% of the record or the budget. Assess the overlap record and energy/charge controls separately. An explicit acceptance review is required before Test 8.

The passing linear prerequisite therefore advances Test 7, but no scientifically valid full acceptance result can be issued from this run. The remaining obstacle is the nonlinear boundary closure and its fresh controlled receiver test, not a threshold that can be relaxed.

## Provenance and delivery

The physical solver used clean commit `cec11d8c0b12b3f4edf48e379cab53e354cd21cd`. The automated pipeline then stopped at analysis on a path-joining bug. Its failed status, traceback and initial index are preserved. Commit `4d8fc62d2f084231ecd87e8f917e2a1a2fb0bd56` fixes only that adapter; analysis uses the original raw bytes. Report-0001 is retained and report-0002 improves event zooms and the free-drive display without changing calculations.

The paired artifact stores raw and derived arrays once in canonical evidence; the reader references their hashes. Compact source recovery includes a Git bundle requiring main commit `ebebee9587059be16595c8e930945598ae5b6836` and the pinned profile inputs. The original full source snapshot is preserved separately; it contains historical repository evidence and is not needed in every reader download. The pre-recovery outer index is historical; use the new package index and canonical verifier for the completed package.

Full repository checks and independent boundary tests passed. Canonical hashes, reader pairing and rendered PDFs were verified. The initial publication attempt was blocked by automatic approval review. The user subsequently authorized publishing the issue branch and opening a PR into main; issue #80 tracks the work. The saved experiment package preserves its original delivery-time publication status. Publishing this source does not promote Test 7 acceptance, and no merge is authorized.

[Locked protocol](gross-test-07-boundary.md) · [Compact evidence](../../research/experiments/gross.boundary-memory.v1/README.md)
