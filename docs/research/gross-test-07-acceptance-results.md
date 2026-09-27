# Test 7: full known-incident acceptance

**All eleven locked checks pass.** Run `run-f2e5dffd14f209f2`, analysis `analysis-0001-0b2d32e3`, reviewed report `report-0002`. This accepts Program v0.2 Section 15.7 for the calibrated flat radial model, a known incident preparation, and the fixed local marker protocol registered for this run. It clears the Test 7 prerequisite for bounded Test 8 planning. Test 8 itself has not been implemented or executed.

The [locked protocol](gross-test-07-acceptance.md), [plan](plans/gross-test-07-acceptance.json), and [compact checks and summary](../../research/experiments/gross.reception-acceptance.v1/README.md) specify the evidence. The paired downloadable reader and canonical package contain all arrays, exact figure data, source recovery information and hashes. No raw arrays or figures are added to Git for this run.

## What was tested

The unchanged SS OCF 1 flat neutral/clock action uses the accepted Test 6 radial clock at omega_Q=0.900, epsilon=0.2 and clock amplitude 0.001. Calibration files and modes retain their accepted hashes. Two compact incoming shells start at radii 19 and 27 with half-width 3.25. The first reflects through the origin and overlaps the second incoming shell. These are radial counterpropagating waves, not two material objects.

The probe is stationary at r=0.1. Its predeclared local proper-time markers are t=10 and t=60, measured from the shared preparation event in the flat frame. The observable is pulse-minus-quiet quadrature phase accumulated between those markers, in cycles. The timer is externally prescribed, and the quiet reference is a separately prepared matched control. An autonomous detector is not claimed.

The full time-dependent calibrated response is evolved, without an adiabatic approximation or fitting to receiver data. Its second-order core/clock response and unfitted fourth-order correction are retained separately. All known incident initial data, upstream recordings, calibration and prediction files were hash-locked before any full nonlinear receiver started. Twenty forecast preparations and fifty full receiver preparations cover five mesh/time/domain variants. An executed frozen-core control supplies the deliberately incomplete response null.

The primary fourth-order forecast was chosen before execution. The local record is taken directly as the argument of the receiver/quiet complex-quadrature ratio, avoiding subtraction of two large unwrapped phase histories. Its prediction includes the fourth-order phase logarithm term. No physical input, threshold, event definition or acceptance criterion changed after this run started.

## Acceptance results

| Locked check                 | Result | Evidence                                                                  |
| ---------------------------- | ------ | ------------------------------------------------------------------------- |
| Frozen calibration           | Pass   | All accepted profile and mode hashes match                                |
| Prediction before receiver   | Pass   | Input and forecast hashes locked before all coupled evolutions            |
| Resolved local record        | Pass   | Every nonquiet interval exceeds five combined budgets; minimum 24.13      |
| Withheld interval prediction | Pass   | Largest relative error 0.001424%, below the 5% allowance                  |
| Response histories           | Pass   | Phase, clock and density history forecasts pass for every nonquiet case   |
| Sign parity                  | Pass   | Single and paired sign-odd phase zero in saved arithmetic on all grids    |
| Weak amplitude law           | Pass   | Exponent 1.999485 on finest grid; normalized traces agree within 0.533%   |
| Pulse overlap                | Pass   | Pair-minus-individual record resolved at 43.62 budgets and predicted      |
| Quiet and frozen core        | Pass   | Both matched quiet intervals and frozen-core response coefficients zero   |
| Numerical convergence        | Pass   | Actual and forecast phase differences contract; time/domain controls pass |
| Conservation                 | Pass   | Charge, total energy and matched incident-energy checks pass              |

The finest-grid interval values below are in cycles. The budget adds receiver and forecast discretization differences separately, the output-sampling comparison and a 1e-11-cycle floor. It is a deterministic error estimate, not a statistical confidence interval.

| Preparation          | Actual interval | Forecast interval | Combined budget | Signal / budget |
| -------------------- | --------------: | ----------------: | --------------: | --------------: |
| Half amplitude       |    -4.565140e-8 |      -4.565075e-8 |    1.484887e-10 |          307.44 |
| First pulse          |    -1.822761e-7 |      -1.822760e-7 |    5.643179e-10 |          323.00 |
| Double amplitude     |    -7.238720e-7 |      -7.238712e-7 |     2.218899e-9 |          326.23 |
| Negative first pulse |    -1.822761e-7 |      -1.822760e-7 |    5.643179e-10 |          323.00 |
| Second pulse         |    -5.941133e-8 |      -5.941087e-8 |     2.462341e-9 |           24.13 |
| Both pulses          |    -2.303586e-7 |      -2.303603e-7 |     1.060012e-9 |          217.32 |
| Both negative        |    -2.303586e-7 |      -2.303603e-7 |     1.060012e-9 |          217.32 |
| Changed clock phase  |    -2.373479e-7 |      -2.373489e-7 |    5.166428e-10 |          459.40 |

The largest absolute forecast error is 1.626e-12 cycles. The independently saved second-order interval predictions also lie within 5%: errors range from 0.0583% to 0.9637% across these cases. Thus the leading calibrated susceptibility already predicts this observable within the program allowance. This is a diagnostic of the saved leading-order forecast, not a replacement of the locked fourth-order gate.

The largest finest-grid relative history errors are 0.000350% for phase, 0.000209% for chi and 0.000338% for core density. The half-amplitude second-order phase-history error is 0.0150%. The overlap forecast relative error is 0.000129%. Maximum relative charge and total-energy drifts are respectively 4.798e-11 and 4.706e-11; maximum matched energy residual divided by incident energy is 1.110e-9.

## Uncertainty and interpretation

Spatial refinement uses h=0.1, 0.05 and 0.025; separate controls halve the time step and double the domain. The finest grid interpolates the accepted fine profile instead of recalibrating it. Combined relative phase-history numerical budgets are 1.37–2.18%. The second-pulse interval has the least favorable relative budget, about 4.14% of its signal. Very small same-grid forecast residuals must not be read as continuum accuracy at that level: both evolutions share a discretized action, and spatial uncertainty is much larger.

Both fixed markers lie exactly on the 0.05 and 0.1 output grids, so the saved decimation difference is zero by design. This does not establish general arrival-time interpolation accuracy. Signed phase changes depend on the chosen clock phase and interval; the physically tested statement is a resolved local clock change with the predicted sign and magnitude for the registered preparations.

The figure set shows propagation, invariant forcing and core/clock response, phase histories with separate second- and fourth-order residual panels, interval uncertainty and acceptance margins, amplitude/sign/overlap controls, and convergence/conservation. The residual panels distinguish agreement hidden by overlapping curves. The interval error-to-allowance panel uses a logarithmic scale; its red line at one is the unchanged acceptance boundary.

## Why this differs from the earlier failures

The program asks about a **known incident field** and **fixed marker events**. Earlier surface-only protocols additionally required reconstruction of unknown incident data and threshold-based event timing. Those are useful stronger extensions, but neither is an explicit prerequisite of Section 15.7. The original run's interval and marker failures, the unresolved transfer timing audit, and the failed inverse-robustness check remain valid findings for their own protocols.

This new run changes both the available incident information and the marker observable, declares both changes before execution, and evaluates fresh receiver data. It does not claim that the original surface-only experiment has passed. Its improvement cannot be attributed solely to the fourth-order correction; the leading forecast also passes for the new observable. Transparent nonlinear boundary replay and unknown-input robustness remain separate research tasks.

## Execution and recovery provenance

The locked plan hash is `80e7b2dbb9fffcc757e049d11d300ba9690a89a4bfd64f5d4388dcd747ba2d7d`. The physical solver ran from clean commit `028337a9fb27e41cc11663df1988e3fb54a14cb8`. All physical evolutions completed once in about thirteen minutes. The initial pipeline stopped at analysis after 797.8 seconds because a quiet-control name was reversed in the analysis adapter. Its original failed status and logs are preserved.

Commit `7130570` resolves quiet names from the locked configuration. A subsequent analysis serialization exception was fixed in `0b0f07b` by converting NumPy booleans and floats to native JSON values. Analysis then completed from the original saved arrays, with no solver rerun. The successful classification belongs to that recovered analysis, not to the original failed pipeline status. A separate recovery status records completion.

Presentation-only commit `a4a00e7` adds visible residual panels and logarithmic acceptance margins, producing report-0002 while preserving report-0001. A report command initially pointed at the enclosing evidence directory instead of its runs directory; it failed before rendering and its log is retained. A post-render verification also found one empty standalone numerics PDF. Its original registered bytes were recovered from the identical prior figure with the original creation timestamp, and its SHA-256 matches the existing manifest exactly; no checksum was changed. The incomplete reader export is retained in the execution workspace, and the delivered reader was rebuilt after recovery. The delivered package keeps canonical raw data once and makes the reader refer to their hashes. The compact source archive and Git bundle preserve reproduction without duplicating unrelated historical data in the download.

## Next calculation

Proceed to a **bounded Test 8 implementation plan**, not a two-object result claim. The present radial solver cannot represent two separated moving cores. First derive and register a spatial model that supports two centers and measures both energy and momentum flux. State whether this remains the flat limit; finite gravitational coupling would additionally require solved constraints. Calibrate isolated objects in that discretization and measure quiet-pair relaxation before a signal run.

The discriminating prediction is a delayed local cycle change at B accompanied by a closed energy/momentum ledger and two surviving usable clocks. Alternatives are initial-data relaxation mistaken for a signal, a response without controlled recoil, or clock destruction. Predeclare usability thresholds, compare a quiet pair and a removed-object control, vary separation and domain, and include independent spatial refinement. The program requires ledger residuals below 1% and records restricted to the causal future of their source.

Retain the exact neutral-emission null for the companion preparation with a perturbed A core and a=0 initially; any structural emission must be identified through its own fields. This is a design requirement, not a result of this run. Coordinate invariance, nonspherical survival, gravity and emergent spacetime remain untested. The supported advance here is calibrated local reception in the stated radial sector.
