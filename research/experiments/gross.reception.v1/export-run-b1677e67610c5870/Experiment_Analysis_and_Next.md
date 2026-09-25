# Test 7 results: reception is resolved, but the locked interval prediction fails

**Technical execution completed. Scientific classification: fail.** Ten of twelve locked checks pass. This is a bounded failure of the registered second-order reception approximation and marker protocol, not evidence that the accepted bound clock has disappeared. Do not promote this run to a Test 8 prerequisite pass.

Run `run-b1677e67610c5870`, analysis `analysis-0001-036cbbf0`, reviewed report `report-0002`. The complete pipeline took 600.407 seconds. The frozen SS OCF 1 action, core, clock eigenmode, coupling and calibration were retained. Fifty coupled receiver preparations were evolved across five mesh/time/box variants. All surface-only predictions were saved and hashed before the first nonlinear receiver-start event. No acceptance threshold was revised after execution.

## What the calculation established

The predictor used only upstream `a`, its time derivative and its radial derivative, together with the accepted receiver calibration. It reconstructed the incoming characteristic, then evolved the full time-dependent second-order core and clock response. It did not receive the prescribed interior neutral history or fit the withheld nonlinear receiver.

The two pulses started outside the recording sphere. The first reflected at the regular origin and overlapped the second inward pulse. Each pulse alone, both pulses, sign reversal, an amplitude ladder, a changed clock phase, matched quiet receivers and a deliberately incomplete frozen-core replay were included. Counterpropagation here means concentric radial shells; two independent planar beams and object recoil were not simulated.

| Finest-grid preparation       | Relative local chi waveform error | Measured interval, cycles | Absolute numerical budget, cycles | Interval prediction error |
| ----------------------------- | --------------------------------: | ------------------------: | --------------------------------: | ------------------------: |
| First pulse                   |                           0.1934% |               -4.56729e-9 |                       1.48608e-10 |                   5.9548% |
| Second pulse                  |                           0.4362% |                4.00888e-8 |                       2.49036e-10 |                   3.1715% |
| Both pulses                   |                           0.3751% |               -6.85035e-8 |                       6.64685e-10 |                   1.5938% |
| First pulse, clock phase pi/3 |                           0.1076% |               -1.39865e-7 |                       1.38628e-10 |                   0.1790% |

The intervals exceed their declared numerical budgets by factors of 30.7, 161.0, 103.1 and 1008.9 respectively. These are deterministic resolution ratios, not statistical confidence levels. The nonzero local clock record is therefore resolved under the registered controls.

The weak amplitude exponent is 1.99937. Amplitude-normalized chi traces differ by at most 0.7164% on the finest grid, and sign-odd response is zero in saved arithmetic. The both-minus-each-alone interaction trace is about 101.5 error budgets above zero and its prediction error is 0.1857%. This improves on the earlier counter-shell control, which lacked the separate outgoing-pulse subtraction. The frozen-core replay gives zero induced clock response, as the action requires when the neutral-to-core-to-clock path is suppressed.

## Why the overall classification is fail

The first failure is the **local interval prediction**. For the nominal first pulse, the actual interval is -4.56728926e-9 cycles and the standalone prediction is -4.83926352e-9. Their absolute discrepancy is 2.71974e-10 cycles. The locked allowance is the larger of 5% of the signal (2.28364e-10) and the numerical budget (1.48608e-10). The discrepancy exceeds that allowance. A 0.1934% full-waveform error cannot replace this failed local-record criterion.

The second failure is **marker timing across all required grids**. Every nonquiet preparation has both markers. The largest coarse-grid error is 0.104856 inverse-mass time units for the second pulse, above the locked 0.1 limit. The independent coarse-grid time and box controls show the same failure. Refinement reduces this maximum to 0.048883 at h=0.05 and 0.027312 at h=0.025. Thus the timing improves, but the preregistered all-grid gate still fails.

| Locked check                         | Outcome  |
| ------------------------------------ | -------- |
| Frozen input hashes                  | Pass     |
| Prediction before receiver execution | Pass     |
| Local record resolution              | Pass     |
| Surface-only waveform prediction     | Pass     |
| Local interval prediction            | **Fail** |
| Local marker timing                  | **Fail** |
| Sign parity                          | Pass     |
| Amplitude-squared response           | Pass     |
| Pulse-overlap response               | Pass     |
| Frozen-core control                  | Pass     |
| Numerical controls                   | Pass     |
| Conservation                         | Pass     |

## Numerical accuracy and interpretation

Halving h from 0.1 to 0.05 changes the selected response traces by 2.15–3.47%. The additional h=0.025 refinement changes them by 0.53–0.86%. Independent time-step differences are below 6.84e-7 relative and box differences below 2.65e-8. Spatial error remains the dominant tested uncertainty. The new grid interpolates the frozen fine core and mode; it does not independently solve a new profile or recalibrate the clock.

The maximum relative charge error is 2.37e-9 across the suite and 2.31e-12 on the finest grid. The matched discrete energy residual is below 7.81e-8 of incident energy across the suite and 1.63e-10 on the finest grid. These support numerical reciprocity and conservation; they do not measure tiny clock-radiation losses or establish nonspherical stability.

The local phase is defined by `theta=unwrap atan2(-chi_dot/Omega,chi)`. The interval begins at the first rise and ends at the last fall through `|a|=1e-4`, within the registered local acquisition window. The quiet phase at those times is a counterfactual comparison, not a physical pulse detection in the quiet run. Last-crossing selection is retrospective. This is an ideal local field diagnostic, not an autonomous detector instrument or a transformed-frame invariance demonstration.

The amplitude-squared pass applies to full response traces. At a fixed absolute threshold, changing pulse amplitude also changes the interval endpoints. The resulting interval records need not obey a simple amplitude-squared law, and indeed the small first-pulse interval can change sign as those endpoints move. This does not contradict the action's leading quadratic forcing.

## Post-hoc diagnosis, separate from acceptance

A saved-data diagnostic decomposes each interval discrepancy into a response error evaluated at the actual marker events and the additional error from forecasting those events. This uses receiver information and therefore is **not** a new blind prediction or a substitute for the failed gate.

For the nominal first pulse, the response contribution is 2.75098e-10 cycles; the marker-time contribution is -3.12385e-12 cycles. Moving the forecast onto the measured markers therefore does not cure the discrepancy. The nominal interval is small because it subtracts two phase offsets; a small waveform discrepancy can become a larger percentage of that difference.

At those same nominal event times, the amplitude-ladder residuals are 1.47415e-11, 2.75098e-10 and 4.56191e-9 cycles for A=0.002, 0.004 and 0.008. Dividing by A to the fourth power gives approximately 0.921, 1.075 and 1.114. This trend suggests an omitted fourth-order contribution, with inversion/discretization contamination at weaker amplitude. It is a diagnostic inference, not a fitted correction or proof. The JSON values and reproducible source are preserved in the run's publication provenance.

## Next discriminating calculation

Before Test 8, derive the next response order while retaining this action and calibration: `a=A*a1+A^3*a3+...`, `Phi=Phi0+A^2*Phi2+A^4*Phi4+...`, and the analogous clock expansion. Include the corresponding quadrature-phase correction. The smallest useful calculation is whether this derived fourth-order term predicts the saved residual's sign and amplitude dependence without a fitted coefficient. Treat comparison with these already inspected histories as diagnostic; test a subsequently locked, held-out waveform for a fresh prediction claim.

Separately compare linear and derivative-informed local marker reconstruction, then halve the output sampling interval in a bounded follow-up if the interpolation budget matters. Refine the surface inversion with the known exterior Z profile, or an explicit discrete transfer calculation, to test the coarse marker timing error. A residual that persists under those controls would reject the response approximation more strongly; a derived fourth-order correction with the predicted scaling would support a controlled extension. Do not relax the present thresholds or call this run a pass retroactively.

Two-object survival and recoil, observer/coordinate invariance, gravity, angular stability and emergent spacetime remain untested here. The useful advance is a resolved local response predicted from an external surface record, together with a clearly located limit of the present approximation.

## Evidence and validation

Canonical evidence and reader export are under `research/experiments/gross.reception.v1/`. The reader includes `results/tables/checks.json`, exact plot data, frozen inputs, sources, six question-driven figures and both PDFs. The original report is retained; report-0002 improves the transport visualization and exposes numerical interval values without changing analysis or raw data.

The canonical package and reader bundle verify. The current program attachment matches the repository source byte for byte. Both Test 6 prerequisite packages were reverified. All 172 Node tests, 84 Python tests, 13 experiment-contract/recipe tests, formatting, lint, type checks, generated contracts and production builds passed after correcting registration order. The CLI sample and math-format check passed. Browser validation is blocked by the environment: Chromium download was truncated, and system dependency installation failed on user/group switching; those failure logs are preserved. No web or worker implementation was changed.
