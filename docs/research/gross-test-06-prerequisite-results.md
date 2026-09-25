# Test 6 prerequisite results: the radial receiver approximation survives

Both requested prerequisite calculations completed and passed their locked bounded scientific checks. This narrows two gaps in Test 6. It does not change Test 6's unresolved thin-wall profiles, establish tiny clock-radiation losses, or complete the operational two-object protocol of Test 7.

| Calculation                    | Saved evidence                                   | Scientific outcome                                                                          |
| ------------------------------ | ------------------------------------------------ | ------------------------------------------------------------------------------------------- |
| 6a: frozen 100-period baseline | `run-c765d2d2ca291dd6`, `analysis-0001-22d5199b` | Five checks pass; full refined and time-step baselines retain local ticks                   |
| 6b: predicted neutral response | `run-82cb109afa4e14c2`, `analysis-0001-6a931d18` | Nine checks pass; precomputed second-order local response matches within numerical controls |

## What Test 6 did and did not establish

The selected omega_Q=0.900 profile supports an independently bound clock eigenmode and a local chi oscillation. The nominal trace and mode projection supplied a bounded radial success. The 0.868 and 0.875 BVP failures are numerical unknowns, not physical exclusions. Refinement and box evolution lasted only 20 periods, and the historical energy ledger residual was 13.4 initial clock-mode energies. Those limits prevented treating it as an unqualified receiver or radiation result.

The follow-ups copied the nominal, refined and wide profiles and eigenmodes byte for byte, checked their hashes, and used frozen Omega=0.41274991. No branch was re-solved and no response coefficient was fitted. The local probe is now at fixed r=0.1 on all grids. The active-neutral run explicitly adds the previously inactive parameter epsilon=0.2 to the registered SS OCF 1 action; this is a chosen coupling, not a prediction.

## 6a: full refined lifetime

| Quantity                                         | Base h=0.1, dt=0.04 | Fine h=0.05, dt=0.02 | Time control h=0.1, dt=0.02 |
| ------------------------------------------------ | ------------------- | -------------------- | --------------------------- |
| Positive-going local ticks                       | 100                 | 100                  | 100                         |
| Measured local frequency / m                     | 0.4127472803        | 0.4127482895         | 0.4127493105                |
| Final relative mode-energy change                | -2.5264e-5          | -6.2296e-6           | -6.2294e-6                  |
| Maximum charge-plus-sink relative residual       | 1.60e-15            | 3.20e-15             | 1.60e-15                    |
| Historical energy residual / initial mode energy | 13.404              | 0.8064               | 0.6838                      |

All cover t=1522.28, approximately 100 nominal periods. Maximum frequency difference is 4.92 ppm. The fine result therefore closes the missing full-duration mesh check. Comparing base with the time control also shows that much of the observed mode-energy change is time-step dependent.

The refined energy residual is smaller than one initial clock-mode energy but still much larger than the tiny mode change. It cannot isolate a radiation spectrum. A full-duration wide-box check, angular perturbations and gravity remain untested.

## 6b: prediction before nonlinear receiver evolution

The neutral gradient contraction drives the core quadratically; the core density change perturbs the clock potential. The worker first evolved the neutral first-order field and the second-order core/clock Taylor equations around the matched no-pulse history. All four prediction files were saved and hashed before the first nonlinear receiver run. The local prediction is the saved second-order coefficient multiplied by A squared, with no fit to receiver data.

| Observable                                            | Result                                   | Interpretation                                                                |
| ----------------------------------------------------- | ---------------------------------------- | ----------------------------------------------------------------------------- |
| Nominal single-packet local-response prediction error | 0.1943% base; 0.1917% fine               | Second-order coefficient predicts the full local trace                        |
| Nominal counter-shell prediction error                | 0.1929% base; 0.1904% fine               | Agreement survives the specified inward/outward preparation                   |
| Weak amplitude exponent                               | 1.999354 base                            | Consistent with a leading A-squared response                                  |
| Normalized amplitude-ladder variation                 | 0.7284% base                             | Small higher-order corrections across A=0.002, 0.004, 0.008                   |
| Sign-odd / sign-even norm ratio                       | 0 in saved arithmetic, both preparations | Exact action symmetry respected; not independent evidence for the coefficient |
| Local nominal response RMS                            | 1.3051e-9 m                              | A small resolved local field difference                                       |
| Mesh response difference                              | 2.1493% single; 2.1353% counter          | Dominant numerical uncertainty                                                |
| Time-step response difference                         | 4.85e-7 relative                         | Much smaller than the mesh effect                                             |
| Box response difference                               | 2.35e-8 single, relative                 | No resolved box contamination at this scale/window                            |
| Maximum relative charge error                         | 2.36e-9 base; 7.38e-11 fine              | Controlled charge conservation                                                |
| Matched energy residual / initial incident energy     | 1.38e-7 base; 4.42e-9 fine               | Discrete reciprocal energy transfer is numerically controlled                 |

The approximately 0.19% prediction discrepancy must not be advertised as 0.19% continuum accuracy: the mesh changes the response by about 2.15%. The discrepancy grows approximately fourfold when A doubles, as expected for the relative correction to a second-order expansion. That is supportive numerical evidence, not a proof of the continuum equations or an independently derived geometry.

Six local positive-going ticks are identifiable and paired in every preparation. For nominal A=0.004, the largest clock advance magnitude is 1.33968e-7 cycles. The largest predicted tick-shift error is 5.26323e-10 cycles, and the largest fine-grid change is 5.29645e-10 cycles. These additional values are computed directly from saved marker CSVs, not new acceptance thresholds. The preregistered 1e-5-cycle absolute marker-prediction floor was permissive relative to this very small signal; the trace prediction and the reported resolved tick-error values carry more information than that pass alone.

The counter control is concentric inward and outward shells. The outgoing shell is initially inside the core, so this is not an independent distant opposing beam. Both signs are reversed together. An outward-only subtraction was not run, so this control does not separately isolate the interference cross term. The upstream sphere records the actual waveform, including returning radiation, but the prediction uses the full prescribed initial data, not an inverse reconstruction from that sphere alone.

## What should happen next

The evidence supports proceeding to a bounded, properly registered Test 7 receiver protocol. Keep this core, eigenmode, coupling and calibration frozen. The smallest next discrimination is to reconstruct the incoming characteristic from an upstream record of both a and its normal/time derivatives, then predict held-out local clock records without access to the interior neutral history. Separate incoming from reflected radiation and anchor start/end markers to a stated local interaction.

Use at least one further spatial refinement for that next prediction: mesh error dominates here. Tighten the absolute marker-error criterion using a preregistered noise and numerical budget appropriate to the observed approximately 1e-7-cycle signal. Test an outward-only control if the counterpropagating cross term is the target. A persistent prediction mismatch beyond those errors or ambiguous physical marker pairing would reject that next approximation. Two-object recoil and frame/coordinate invariance remain Tests 8 and 9, not claims of these prerequisite runs.

## Reader and source navigation

- [Longevity reader export](../../research/experiments/gross.clock-longevity.v1/export-run-c765d2d2ca291dd6/README.md)
- [Longevity canonical evidence](../../research/experiments/gross.clock-longevity.v1/run-c765d2d2ca291dd6/manifest.json)
- [Response reader export](../../research/experiments/gross.clock-response.v1/export-run-82cb109afa4e14c2/README.md)
- [Response canonical evidence](../../research/experiments/gross.clock-response.v1/run-82cb109afa4e14c2/manifest.json)
- [Registered derivation and protocol](gross-test-06-prerequisites.md)

Each export contains setup/results PDFs, interpreted figures, exact plotted CSVs, raw prediction and receiver data, source code and provenance. Structural verification is separate from the scientific classifications above. Manual Actions choices are `gross-test-06-longevity` and `gross-test-06-response`; hosted execution has not been dispatched during this work.
