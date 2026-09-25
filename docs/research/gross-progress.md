# Signal Space / GROSS progress ledger

This ledger tracks Tests 1-11 of the operator program v0.2. These numbers are independent of the older E01-E11 charged/knot sequence.

| Test | Scope                                 | Prerequisites                                           | Status                                                                                                       |
| ---- | ------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| 1    | Operator and observer identities      | Source audit; registered algebra plugin; locked plan    | Pass: 1,000 samples, six checks; run-2ae9c65dbd171851, analysis-0001-d3c876ea, report-0002                   |
| 2    | Reciprocal event law and rescheduling | 1; complete registered event circuit                    | Pass: four preparations, both lambdas, ten checks; run-81319816afe7cf8e, analysis-0001-8c6b8920, report-0002 |
| 3    | Router propagation                    | 1-2; exact routing benchmark                            | Pass: 624 wave-block samples, nine checks; run-915ed88048939f8f, analysis-0001-53e821db, report-0001         |
| 4    | Complete microscopic spectrum         | 2-3; self-consistent background                         | Zero-wave strong all-sector hypothesis analytically fails; nonzero background unresolved                     |
| 5    | Continuum action and characteristics  | 1; registered action audit                              | Analytical factorization available; numerical test not evaluated                                             |
| 6    | Bound readable clock                  | 1,5; core profile and spectrum                          | Not evaluated                                                                                                |
| 7    | Predicted reception                   | Accepted 6 and frozen calibration                       | Not evaluated                                                                                                |
| 8    | Two objects, exchange and recoil      | Accepted 6-7                                            | Not evaluated                                                                                                |
| 9    | Observer/coordinate invariance        | Accepted local record, beginning with 6-7               | Not evaluated                                                                                                |
| 10   | Spatial topology extension            | Explicit new action, domain, invariant and health audit | Not evaluated                                                                                                |
| 11   | Drift and mode dependence             | Dispersion: 3-4; operational part: accepted clock and 9 | Analytical protocol available; numerical test not evaluated                                                  |

A pass of Test 1 validates operator algebra and its implementation only. It does not pass Candidate A or B, establish a clock or derive spacetime. A successful Candidate B clock would not satisfy Candidate A's autonomous-clock requirement.

Runtime status: the repository's common runtime is available. The operator identity plugin is registered separately from the synthetic and charged-scalar plugins. Test 2 now registers the bounded SS OPS 1 reciprocal event circuit separately; SS OCF 1 evolution remains unregistered. Test 2 has now executed and verified the registered finite circuit. Test 3 now verifies the homogeneous wave-sector routing benchmark. The full coupled routing spectrum, Candidate A clocks and all SS OCF 1 evolution remain untested.

The user-authorized workflow is a focused branch, locked experiment, verified evidence and reader export, then a PR. Raw data and prior classifications stay immutable. PR review and merge are separate from scientific classification.

## Test 1 evidence

[Reader export](../../research/experiments/gross.operator-identities.v1/export-run-2ae9c65dbd171851/README.md) and [canonical run](../../research/experiments/gross.operator-identities.v1/run-2ae9c65dbd171851/manifest.json). Largest normalized residual: 3.963119603223247e-14. The omitted-weight control is detected; singular aggregates are rejected. Test 2 follows this prerequisite; its evidence is recorded below.

## Test 2 evidence

[Reader export](../../research/experiments/gross.reciprocal-events.v1/export-run-81319816afe7cf8e/README.md) and [canonical run](../../research/experiments/gross.reciprocal-events.v1/run-81319816afe7cf8e/manifest.json). Ten locked checks passed. Maximum conservation residual 3.50812e-10 (limit 1e-9); exact-solution difference 2.45401e-11; legal schedule difference and outside-ancestor Jacobian zero in saved arithmetic. Shared-memory reversal and frozen-memory controls both register nonzero changes. Technical pipeline completed locally in 31.671 seconds; GitHub-hosted dispatch/upload remains for the user's run after merge.

Prerequisites P0/P1: source and contracts read; prior Test 1 package reverified. P2A: SS OPS 1 Hamiltonian and explicit twelve-event circuit registered. P3: plan/config locked before execution. P4: canonical package and reader export verified; four figures and both PDFs visually inspected. P2B remains unregistered.

Next: bounded Test 3 exact-router dispersion with triad, reversed-order and full-zone controls. Retain Test 4 memory modes and Test 11 directional questions. Test 2 supplies no metric or accepted clock. All other numerical statuses above remain unchanged.

## Test 3 evidence

[Reader export](../../research/experiments/gross.router-propagation.v1/export-run-915ed88048939f8f/README.md) and [canonical run](../../research/experiments/gross.router-propagation.v1/run-915ed88048939f8f/manifest.json). All nine locked checks pass: 624 small-wavevector comparisons, three triads, both orders, global rotation, periodic boxes, group refinement and nested full-zone grids. Explicit circuit/reference error 6.78e-16; conservation residual 6.66e-16. Fine-radius normalized squared-cone error 0.00774245, adjacent ratio at most 0.497147. Orthogonal full-zone grids detect eight zero and eight pi nodes in each order at both resolutions. This is not a nodal-completeness or particle-species claim.

P0/P1: current source hash matched and both prior packages reverified. P2A: the homogeneous zero-wave wave sector is separately registered as `signal-space.ss-ops-1.router-linear.v1`; the full physical memory degrees of freedom remain part of SS OPS 1. P3: plan/config locked before execution. P4: canonical run and reader export validated; six figures and both PDFs inspected. Local recipe: 19.618 seconds. Hosted dispatch/upload remains untested.

Next: Test 4 complete zero-wave tangent spectrum with all physical memory variations, then only a separately bounded self-consistent nonzero background. Test 11 now has preliminary finite-band opposite-direction diagnostics; leading physical drift and invariant local records are not evaluated. Tests 4–10 retain their prior numerical status.
