# Test 7 reconstruction: the late event remains unobservable under the present protocol

**Technical solver completion: yes. Scientific audit: fail, with five passing, one failing and three unresolved locked checks. Original Test 7 remains failed. Test 8 remains blocked.**

Run `run-ca19609e702134b1`; analysis `analysis-0001-a8cc0c93`; reviewed report `report-0002`. This is a bounded linear calculation, not another full reception evolution. Fifteen cases cover three packet shapes and five mesh/time/domain variants. No response coefficient, action, earlier threshold or frozen clock calibration was changed.

## What was tested

The unchanged frozen neutral equation is $M\ddot b=-Kb$, with $b=ra$, positive inertia $M$ and stiffness $K$ inherited from the SS OCF 1 radial action. Three independently solved profiles from the previous transfer run are reused at spacings 0.05, 0.025 and 0.0125. Independent time-step halving and a larger domain complete the controls. Surface and local output spacing is 0.0125, with 0.025 decimation controls and a saved 0.05 output comparison.

The single-site inverse receives the surface field and time derivative through time 16, known initial support [18,26], and the incoming derivative rule. A separate causal control adds the neighboring surface node. It reconstructs the interior state using the exact discrete commutator source, then stops that source at time 16 and evolves the captured state freely. The latter is a finite-capture approximation, **not an exact transparent boundary method**.

Each variant's forecasts and singular sensitivities were locked before its known-source interior audit. The broad and carrier packets have been inspected previously; a third linear packet has center 21.5, width 2.75 and carrier 0.8. It is new linear evidence, not a withheld nonlinear clock-response test.

## Separate first and last events

All times and errors below are in inverse-mass units. The finest mesh is 0.0125 and time step 0.0025. The new reconstruction target is 0.0001. These linear source events are not the previous nonlinear receiver events.

| Shape   | Inverse first-event error | Inverse last-event error | Causal first-event error | Causal last-event error |
| ------- | ------------------------: | -----------------------: | -----------------------: | ----------------------: |
| Broad   |                  2.69e-12 |                 0.003513 |                  6.21e-8 |                7.064919 |
| Carrier |                  5.90e-13 |                 0.003111 |                  1.20e-7 |                4.009644 |
| New     |                  1.78e-12 |                 0.001494 |                  1.76e-8 |                7.332622 |

All causal first events meet their individual budgets: 2.98e-6, 4.28e-6 and 3.75e-7 respectively. Last-event budgets are 3.197, 5.390 and 3.212, far above the 0.0001 target. The registered causal-timing gate is therefore **unresolved**, even though the large observed late errors clearly prevent using this control as an accepted replacement.

Absolute first-event mesh shifts are still 0.0616, 0.0812 and 0.0428 between the two finest grids. Excellent agreement on the same grid is not an absolute continuum arrival-time measurement. The source's late event also lacks the registered convergence trend for carrier and new packets. No continuum event accuracy is certified.

## Why the inverse fails its robustness gate

At the finest mesh, the inverse retains 451 of 641 initial-data directions. Surface replay residuals are 1.42e-13 to 2.26e-13, but many discarded directions still contribute substantially to the late local field. The plotted first-event sensitivity nearly vanishes in those directions; the late-event sensitivity does not.

The robustness test assumes a surface tolerance of $10^{-10}$ times the recorded surface norm and an initial-data perturbation norm at most twice the recovered input norm. These are declared conditional assumptions, not measured laboratory noise. Finite witnesses obey both constraints and the original support/incoming rule:

| Shape   | Witness input norm change | Complete surface relative residual | Last-event shift |
| ------- | ------------------------: | ---------------------------------: | ---------------: |
| Broad   |                     2.04% |                           9.98e-11 |          11.4767 |
| Carrier |                     3.01% |                           9.99e-11 |          13.3797 |
| New     |                     2.38% |                           9.98e-11 |          13.0057 |

These are constructive counterexamples to robustness in the stated input class. That class does not impose an independent bandwidth, smoothness or energy bound, so this is not a theorem that every restricted smooth pulse family is unobservable. Nor do these large shifts validate the enormous first-order root estimates: finite event recomputation is the relevant evidence. The last crossing is selected within a time window ending at 60; its sensitivity is partly sensitivity of this retrospective event definition.

The exact retained/discarded decomposition of the actual smooth-source reconstruction error also passes. Even without adversarial perturbations, all three inverse last-event errors exceed the new reconstruction target.

## Why finite causal capture is not the cure

The captured state agrees with the projected known-source interior at time 16 to a relative quadratic energy error of about 1e-19 to 1e-18 on the finest grid. Thus the two-site commutator reconstruction itself works well.

Continuing from only that projected state discards the exterior field and creates a sharp truncation at the capture surface. The energy norm of the omitted state relative to the complete source state is 0.244%, 0.0240% and 0.109% for broad, carrier and new packets. These are norms of separately projected states, **not an additive physical energy partition or a radiation measurement**. The late plots show rapid ringing absent from the smooth source tail. In the linear equation, the subsequent difference is the propagated omitted state plus the much smaller capture error. This identifies the finite-capture approximation as the source of the new discrepancy; it does not reject all causal boundary-transfer methods.

The broad causal last marker moves by 0.209 under output decimation from 0.0125 to 0.025. Finer interpolation alone cannot supply the discarded exterior state. The larger-domain control produces zero saved event differences before the permitted outer return; the unforced acquisition energy drift is below 9.65e-12 across the suite. Total clock radiation, charged-core health and nonlinear conservation were not recalculated because no clock or core evolution occurs here.

## Locked decision table

| Check                                         | Status         |
| --------------------------------------------- | -------------- |
| Frozen hashes and forecast-before-audit order | Pass           |
| Retained/discarded error decomposition        | Pass           |
| Surface replay                                | Pass           |
| Frozen linear source energy                   | Pass           |
| Initial-data inverse observability            | **Fail**       |
| Causal state capture at time 16               | Pass           |
| Separate causal event budgets                 | **Unresolved** |
| Absolute event convergence                    | **Unresolved** |
| Output and acquisition sampling               | **Unresolved** |

## What to do next

**Do not add another clock-response order or run Test 8 on this evidence.** The smallest next derivation is an incoming-boundary protocol that retains the exterior's outgoing response instead of abruptly projecting it away. For the existing discrete linear operator, eliminate the exterior degrees of freedom to derive its causal boundary-memory kernel, or specify an equivalently exact transparent interface. Check it first against a known-source linear control. A first discriminator is whether the late ringing disappears without using interior receiver data.

The finite observation window needs its own identifiability criterion. Either establish a justified source energy/bandwidth restriction and propagate the unobserved remainder to the event, or acquire sufficient incoming data for the event being forecast. Do not infer a missing high-frequency bound from a tiny surface fit residual. A future acquisition change must be registered explicitly.

The current last-fall marker should also be reconsidered. Two independently recognizable incoming tagging pulses with separate first-rise triggers are a candidate local event protocol, provided the tags and trigger rules are specified before execution and carry no hidden source labels. This is a proposed measurement change requiring a new versioned protocol; it is not a retroactive repair of this run.

For a future clock interval $N=C(t_2)-C(t_1)$, where $C(t)$ is the matched local phase in cycles, endpoint uncertainty contributes approximately $C'(t_2)\delta t_2-C'(t_1)\delta t_1$. Reconstruction uncertainty also changes $C$ itself. Both contributions must enter a fresh forecast-inclusive budget. This audit does not compute a new phase uncertainty or promote the old quartic result: the earlier event prerequisite fails first.

After a controlled linear transfer and observable marker protocol pass, lock a new nonlinear waveform and its complete phase forecast. Test 7 then needs an explicit acceptance review; only that review could open Test 8. The radial clock and the earlier unfitted quartic response remain useful evidence. This calculation localizes a measurement and inference limitation, not a rejection of the underlying action or proof of emergent spacetime.

## Provenance and recovery

The solver ran from clean commit `fc758dab3f58802e036c04b2e31e0b2955048698`; the connected GitHub publication has the identical source tree `bc207bb5f330f4be28366382548550ffc1e55b68`. A Git bundle preserves the exact local source commit and names its required base. The original automated pipeline completed all physical cases, then stopped at analysis because a `Path` was indexed instead of joined. Its failed status and logs are retained. Commit `9ba17fc` fixes that adapter; analysis uses the original saved bytes. Report-0001 is retained, and report-0002 adds reviewed numerical interpretations. No physical run was repeated and no gate was changed.

The current attached program matches the repository program byte for byte. The prior canonical transfer package was reverified. Independent dense-commutator, causal-capture and finite-witness tests pass. Full repository checks, 90 Python tests, 13 pipeline tests, the CLI sample and math-format checks pass; no browser execution path changed. Canonical and reader verification plus visual PDF inspection are recorded with the final package.

[Locked protocol](gross-test-07-reconstruction.md) · [Canonical manifest](../../research/experiments/gross.reconstruction.v1/run-ca19609e702134b1/manifest.json) · [Reader package](../../research/experiments/gross.reconstruction.v1/export-run-ca19609e702134b1/README.md)
