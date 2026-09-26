# Test 7: bounded reconstruction and event timing

Issue #77 follows #75 / #76. This is a linear prerequisite calculation under the unchanged SS OCF 1 action (Operator Program v0.2 sections 7–10 and 15.7). No nonlinear receiver is evolved. A passing reconstruction control cannot by itself accept Test 7 or begin Test 8.

## Frozen equation and acquisition

Use $b=ra$, radial neutral amplitude $b$, neutral field $a$, radius $r$, and natural units $c=\hbar=m=1$. The frozen core determines the positive diagonal inertia $M$ and symmetric stiffness $K$ of the preceding discrete-transfer experiment:

$$
M\ddot b=-Kb,\qquad p=M\dot b.
$$

Both matrices contain $Z=1+0.2|\Phi_0|^2$, where $\Phi_0$ is the accepted stationary charged-core profile. These factors cancel in the continuum principal speed. This calculation introduces no optical speed correction.

Reuse the independently solved and hashed profiles at spacings $h=0.05,0.025,0.0125$ and outer radius 80; use radius 100 at $h=0.025$ for a domain control. Time step is 0.0025, with an independent 0.00125 finest control. Record local fields every 0.0125 through time 60, and surface data at radius 14 through time 16. Initial data have support [18,26] and the declared incoming rule $\dot b=D_hb$, where $D_h$ is the centered discrete derivative. Those restrictions are prior information, not inferred results.

The broad and carrier shapes are retained. A third compact envelope has center 21.5, width 2.75 and carrier 0.8. Its linear validation is new; it is not a new nonlinear reception forecast. Neutral amplitude is 0.012. Local events at radius 0.1 are the first rising and last falling crossings of $|a|=10^{-4}$ within the same time window. The last event remains retrospective.

## Initial-data inverse and event observability

Let $q$ denote supported initial $b$, $y=Hq$ the single-site surface record of $b,\dot b$, and $Lq$ the local history. Both observation matrices are computed with the exact adjoint of the RK4 discrete propagator. Write $H=U\Sigma V^T$, with singular values $\sigma_j$. The inverse retains values exceeding $10^{-10}\sigma_0$; $10^{-8}$ is a declared alternative cutoff.

For a local field row $\ell_e$ evaluated at a predicted event, define surface perturbation radius $\eta=10^{-10}\|y\|_2$ and input perturbation radius $\rho=2\|\widehat q\|_2$. These are explicit conditional tolerances, not an inferred physical noise level. With retained and discarded right singular vectors $V_r,V_d$:

$$
|\delta a_e|\le \eta\|\ell_e V_r\Sigma_r^{-1}\|_2+\rho\|\ell_e V_d\|_2.
$$

The row includes amplitude and radial conversion to $a$. The computed retained bound also includes the saved inverse fit residual. Finite witnesses reserve that residual from the surface tolerance and verify their complete residual against the actual measured record. Dividing this bound by the local absolute slope $|\dot a_e|$ gives a first-order root sensitivity, not a rigorous nonlinear event certificate. Each event is evaluated separately. Finite perturbations in retained and discarded directions are constrained by both radii, propagated through $L$, and their threshold events recomputed. An admissible witness moving an event by more than $10^{-4}$ rejects robustness within that conditional input class. A large sensitivity without a witness leaves observability unresolved.

Only after each variant's forecasts are locked is known initial $q$ used to split the actual interior error into retained and discarded contributions. This is a source audit, not predictor input. Operator matrices and singular data are saved; $L$ is a reproducible intermediate and exact displayed histories are saved.

## Causal control with an additional surface measurement

A separate protocol records $b,\dot b$ at the surface node and its immediate outer neighbor. This is additional information compared with the single-site inverse; it is equivalent to a discrete link derivative. Let $P$ keep nodes at or inside the recording radius. The projected solution satisfies

$$
M(Pb)_{tt}=-K(Pb)+(KP-PK)b.
$$

Because $K$ couples adjacent nodes, the commutator source has only two entries. Starting from zero interior fields, drive those entries with the measured pair of traces, using cubic Hermite interpolation at the RK4 stage times. At acquisition time 16 stop the source and evolve freely on the original full domain. Up to time 16 this reconstructs the projected interior state, subject to interpolation and time integration error. Afterward it omits the acquired solution's exterior state; its energy norm ratio and effect on local markers are audited, never assumed zero.

This control forecasts local events from surface data ending before the first local event. It does not inject a prescribed interior waveform. The captured state and projected known-source state are compared only downstream of the prediction lock. The causal control currently tests synthetic noiseless two-site data; a physical noise model remains absent.

## Locked checks and budgets

The exact criteria are in the locked plan and configuration. The reconstruction target $10^{-4}$ inverse-mass time units is a new, stricter prerequisite target; it does not change the old Test 7 gate of 0.1.

For the causal method define residual $e_j=t^{\rm capture}_j-t^{\rm source}_j$ separately for first/last event $j$. Its direct error estimate is the sum of changes in $e_j$ under mesh, time, and domain controls, both surface and output sampling changes, and a $10^{-7}$ floor. No Richardson division or fit reduces it. Require both residual and this budget below $10^{-4}$ and residual within budget. An excessive budget is unresolved. A resolved residual violation fails.

Also report absolute source/inverse/capture event mesh changes separately; the finest change must be no greater than 0.6 times the previous change plus the nonspatial terms. Agreement on one mesh does not establish absolute continuum event accuracy. Output decimation from 0.0125 to 0.025 and to 0.05 is saved; the 0.025 difference is gated. Independently decimate the two-site surface acquisition to 0.025.

The linear capture energy-error target is $10^{-6}$ relative to the projected source state. It measures reconstruction error, not energy conservation or clock radiation. The unforced linear acquisition must conserve its quadratic neutral energy to relative 1e-6 over time 0 through 16. No charged or clock state evolves here. Prior full-receiver conservation remains prior evidence only.

## Interpretation and next gate

Nine checks classify this bounded audit. Failure of conditional inverse robustness is evidence against that inverse/prior combination, not against the action. A successful causal control could justify changing the next acquisition protocol explicitly. A failed or unresolved causal control requires examination of finite acquisition, sampling or propagation before another nonlinear reception forecast.

A fresh nonlinear waveform and its complete forecast-inclusive phase budget remain necessary for Test 7 acceptance. This run neither computes the clock phase nor tests the next response order. Recoil, two-object survival, coordinate invariance, gravity, angular stability and emergent spacetime remain untested. All earlier scientific classifications are immutable.
