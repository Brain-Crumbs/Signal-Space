# Test 7 follow-up: fourth-order local reception

**Technical completion: yes. Scientific classification for this separately locked follow-up: bounded pass (7/7 checks). Original Test 7 remains a scientific fail (10/12); its thresholds and analyses were not changed. Test 8 remains blocked.**

Source commit `2854331b9151859ac465cc97de98089950025188`; canonical run `run-29c4c4228ffddbb4`; analysis `analysis-0001-ac36b679`; report `report-0001`. The clean source was committed before execution. The registered recipe locked every surface, reconstructed input and order-four forecast before any held-out receiver evolution. All source profile and prior evidence hashes verify. The canonical run and reader export both verify independently.

## What was derived

The frozen SS OCF 1 action, radial Hamiltonian, $\omega_Q=0.900$ core, $\Omega_\chi=0.41274991$ clock and local $r=0.1$ calibration are unchanged. Formal neutral orders $b=Ab_1+A^3b_3+\cdots$, core orders $u=u_0+A^2u_2+A^4u_4+\cdots$, and clock orders $w=w_0+A^2w_2+A^4w_4+\cdots$ were evolved together. The fourth-order local quadrature phase contains both $\operatorname{Im}(z_4/z_0)$ and the indispensable $-\frac12\operatorname{Im}[(z_2/z_0)^2]$, with $z=\chi-i\dot\chi/\Omega_\chi$. The [protocol](gross-test-07-order4.md) derives every source term from the registered discrete action. An independent full-equation finite-amplitude check finds the expected $A^5$ neutral and $A^6$ charged/clock remainder orders. No response coefficient was fitted.

## Inspected-history diagnostic, not a fresh prediction

At **the same fixed nominal $A=0.004$ marker times** used by the prior post-hoc Test 7 diagnostic, the computed correction has the observed positive sign and nearly the observed fourth-power scaling:

|   $A$ | Saved actual minus order two, cycles | Derived order four, cycles | Remaining actual minus order four, cycles |
| ----: | -----------------------------------: | -------------------------: | ----------------------------------------: |
| 0.002 |                          1.47415e-11 |                1.80167e-11 |                              -3.27517e-12 |
| 0.004 |                          2.75098e-10 |                2.88267e-10 |                              -1.31684e-11 |
| 0.008 |                           4.56191e-9 |                 4.61226e-9 |                              -5.03584e-11 |

Those histories and fixed markers had already been inspected. This table diagnoses the missing response order; it is not evidence of an independent prediction. The displayed remainder also contains surface inversion, finite-mesh and higher-order contributions.

## New locked waveform

A compact neutral shell centered at $r=22$ with width $3.25$ was recorded outside the receiver at $R_s=14$. The predictor consumed the upstream $a,a_t,a_r$ record and the independently frozen receiver calibration. It used the known exterior $Z(r)=1+0.2|\Phi_0|^2$ for leading optical travel-time and amplitude transport. The full nonlinear receiver was then evolved separately with $A=+0.004,-0.004,+0.006$ and a matched quiet preparation.

| Grid      | Actual interval at $A=0.004$, cycles | Order-two forecast | Order-four forecast | Relative phase-history error, order two → four | Max standalone marker timing error |
| --------- | -----------------------------------: | -----------------: | ------------------: | ---------------------------------------------: | ---------------------------------: |
| $h=0.1$   |                        -2.2083813e-7 |      -2.1644394e-7 |       -2.1599815e-7 |                            2.12480% → 2.11267% |                           0.059807 |
| $h=0.05$  |                        -2.1005469e-7 |      -2.1130055e-7 |       -2.1086111e-7 |                            0.57637% → 0.56254% |                           0.031458 |
| $h=0.025$ |                        -2.0877767e-7 |      -2.0939039e-7 |       -2.0895272e-7 |                            0.18820% → 0.17124% |                           0.010608 |

The finest fourth-order interval differs by **1.75045e-10 cycles** from the receiver, versus **6.12712e-10 cycles** for order two. The declared absolute numerical budget is **1.29462e-9 cycles**, and the locked allowance is the larger of that budget and 5% of the observed record (**1.04389e-8 cycles**). The measured record is about 161 times its numerical budget. Both interval forecasts already fall below that numerical budget, so the reduction in scalar interval error is suggestive rather than independently resolved by these controls. The more informative evidence is the unfitted $A^4$ diagnostic together with the fresh phase-history improvement across meshes. The full waveform error still includes the approximate surface inverse.

All new positive/negative marker and interval controls agree in saved arithmetic. Maximum relative charge drift is **4.80e-11** and matched total-energy residual relative to incident energy is **1.33e-6**. These conservation checks do not resolve tiny clock radiation. The fine-to-finest marker and trace changes remain larger than the order-four interval improvement; the finer grid interpolates the frozen fine profile and does not constitute an independently recalibrated clock.

## Timing and surface inversion controls

At $h=0.1$, using 0.1 output spacing with linear threshold interpolation moves a marker by up to **0.007083** relative to the 0.05-output derivative-informed reconstruction. Hermite interpolation with the saved local $a_t$ reduces that sampling difference to **0.0000316**. On the finest grid the corresponding differences are **0.004050** and **0.0000184**. Derivative-informed interpolation helps locate an event within sampled history but cannot fix propagation mismatch.

For the coarse held-out shell, a vacuum-characteristic inverse gives maximum marker error **0.059978**, while the separately saved, known-$Z$ optical inverse gives **0.059807**. The $Z$ correction moves the error by only about **0.000171**; the remaining error is dominated by spatial transfer/discretization on this control. The comparison of vacuum and known-$Z$ timing against the receiver is explicitly post-hoc. The known-$Z$ fourth-order forecast itself was hashed before the receiver started. Neither inversion is claimed to be an exact discrete transfer.

## Decision and next calculation

The new follow-up passes its seven locked criteria on this radial preparation. It supports a controlled fourth-order extension of the fixed action and a resolved local record predicted from an external surface history. It does **not** retroactively change Test 7's failed 5% nominal interval and 0.1 all-grid timing checks. In particular, the new waveform's passing timing does not repair the old second-pulse coarse error of 0.104856.

Before Test 8, the smallest useful discriminator is an **explicit discrete surface-to-interior transfer** on the same frozen $Z(r)$ background, checked against an independently refined radial profile and a second waveform with a different spectrum. Predict its first and last marker times before full receiver evolution; require the residual to decrease with the declared mesh and time errors, and predeclare an interval error budget that can actually distinguish second from fourth order. A persistent timing or phase discrepancy beyond those budgets would reject the extended radial approximation. A spatially converged and resolved correction would permit a separate acceptance review for Test 7, not automatic promotion of this run.

All results remain flat and spherically symmetric. Counterpropagation, two-object survival and recoil, observer/coordinate invariance, gravity, angular stability, autonomous detector hardware and emergent spacetime are not tested. The last-fall marker is selected retrospectively; quiet phase at event times is a counterfactual reference.

## Evidence

[Canonical run](../../research/experiments/gross.reception-order4.v1/run-29c4c4228ffddbb4/manifest.json), [reader package](../../research/experiments/gross.reception-order4.v1/export-run-29c4c4228ffddbb4/README.md), exact CSV/JSON plot data, three figures with Question/Reading/Significance/Limitation, both PDFs, source snapshot and a verified solver-source Git bundle are included. The runner finished in 275.55 seconds. Full `npm run check`, 85 Python research tests, 13 pipeline tests, and the independent formal-order test pass; no browser-facing execution path was changed. All eight reader PDF pages were rendered and visually inspected. GitHub-hosted workflow dispatch/upload was not exercised.
