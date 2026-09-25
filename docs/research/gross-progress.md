# Signal Space / GROSS progress ledger

This ledger tracks Tests 1-11 of the operator program v0.2. These numbers are independent of the older E01-E11 charged/knot sequence.

| Test | Scope                                 | Prerequisites                                           | Status                                                                                                                                         |
| ---- | ------------------------------------- | ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | Operator and observer identities      | Source audit; registered algebra plugin; locked plan    | Pass: 1,000 samples, six checks; run-2ae9c65dbd171851, analysis-0001-d3c876ea, report-0002                                                     |
| 2    | Reciprocal event law and rescheduling | 1; complete registered event circuit                    | Pass: four preparations, both lambdas, ten checks; run-81319816afe7cf8e, analysis-0001-8c6b8920, report-0002                                   |
| 3    | Router propagation                    | 1-2; exact routing benchmark                            | Pass: 624 wave-block samples, nine checks; run-915ed88048939f8f, analysis-0001-53e821db, report-0001                                           |
| 4    | Complete microscopic spectrum         | 2-3; self-consistent background                         | Executed bounded audit: 8 controls pass; vacuum strong cone fails; counter stability unresolved                                                |
| 5    | Continuum action and characteristics  | 1; registered action audit                              | Bounded pass: 200 coframes, 48,000 roots, seven checks; run-d3333c7602af3e47, analysis-0001-4dbb966f                                           |
| 6    | Bound readable clock                  | 1,5; core profile and spectrum                          | Bounded pass for flat radial omega=0.900 branch; two thinner trials unresolved; 100-cycle local trace; clock-scale radiation energy unresolved |
| 7    | Predicted reception                   | Accepted 6 and frozen calibration                       | Not evaluated                                                                                                                                  |
| 8    | Two objects, exchange and recoil      | Accepted 6-7                                            | Not evaluated                                                                                                                                  |
| 9    | Observer/coordinate invariance        | Accepted local record, beginning with 6-7               | Not evaluated                                                                                                                                  |
| 10   | Spatial topology extension            | Explicit new action, domain, invariant and health audit | Not evaluated                                                                                                                                  |
| 11   | Drift and mode dependence             | Dispersion: 3-4; operational part: accepted clock and 9 | Paired spectral diagnostics in Tests 3-4; opposite port drift derived for six-gate circuit; operational part not evaluated                     |

A pass of Test 1 validates operator algebra and its implementation only. It does not pass Candidate A or B, establish a clock or derive spacetime. A successful Candidate B clock would not satisfy Candidate A's autonomous-clock requirement.

Runtime status: the repository's common runtime is available. Test 2 registers a bounded SS OPS 1 reciprocal event circuit; Tests 3 and 4 verify routing and full physical spectra on their stated backgrounds. Test 5 registers a local action audit of SS OCF 1. Test 6 now registers and executes its flat spherical matter evolution with reciprocal core/clock response. Generic noncollinear active-background spectra, Candidate A clocks, nonlinear Einstein evolution and neutral reception remain untested.

The user-authorized workflow is a focused branch, locked experiment, verified evidence and reader export, then a PR. Raw data and prior classifications stay immutable. PR review and merge are separate from scientific classification.

## Test 6 evidence

[Reviewed result](gross-test-06-results.md), [reader export](../../research/experiments/gross.bound-clock.v1/export-run-080a63d117abd84d/README.md) and [canonical run](../../research/experiments/gross.bound-clock.v1/run-080a63d117abd84d/manifest.json). Registered flat SS OCF 1 clock variant and locked recovery plan v2; the earlier plan and run with fixed-seed BVP failures remain in the archive. The selected $\omega_Q=0.900$ profile has $E_Q/Q=0.919412$ and bound $\Omega_\chi^2=0.17036249<0.25$. Its local trace yields 100.0001 inferred signed cycles over 100 eigenperiods. Projected clock-mode energy loss is $2.53\times10^{-5}$; maximum charge balance residual after the logged sponge sink is $1.44\times10^{-15}$. Ten preregistered selected-branch checks pass. The $0.868$ and $0.875$ BVP profiles remain numerically unresolved despite saved continuation attempts.

The nominal outer energy sink is measured, but total-energy ledger error is 13.4 times the initial clock energy, so a distinct clock radiation energy is unresolved. Grid/domain and amplitude time controls last 20 periods; nonspherical and gravitational dynamics remain untested. The radial clock is a conditional calibration for Test 7. The next run should freeze this selected branch and predict its local neutral-pulse response before inspecting the receiver evolution. The Test 11 operational and Candidate A clock requirements remain separate.

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

## Test 4 evidence

[Reader export](../../research/experiments/gross.full-spectrum.v1/export-run-5a55cb5041050589/README.md) and [canonical run](../../research/experiments/gross.full-spectrum.v1/run-5a55cb5041050589/manifest.json). Run `run-5a55cb5041050589`, analysis `analysis-0001-bceef551`, report `report-0001`. Technical recipe completed in 22.774 seconds. **Eight implementation/control checks pass; the strong vacuum all-sector common-cone criterion fails; counter-background stability remains unresolved.**

The separately registered model `signal-space.ss-ops-1.six-gate.v1` retains two complex wave ports and six physical memory projectors per cell. Its six reciprocal gates are explicit additional incidence data; no equivalence to Test 3's reduced stencil is claimed. Three exact physical period-one backgrounds are verified: vacuum/noncollinear, equal nonzero/noncollinear, opposing nonzero/collinear. All 20 real physical tangent dimensions are retained, yielding 17,940 mode rows. The phase quotient removes only unobservable memory spinor phases.

Vacuum and equal-wave backgrounds retain twelve stationary physical memory dimensions. Opposing waves activate reciprocal memory response: full/frozen map difference 0.4444444445. No exponential growth is detected on the samples; this does not establish stability or a common cone for that background. Strong geometry, a derived material response, autonomous clocks, and generic nonzero-background existence remain separate questions.

Largest map-refinement residual 4.712e-10; independent ODE Jacobian residual 6.106e-11; local conservation residual 1.984e-15; physical recurrence residual 3.674e-16. Local impulse causal-support and box differences are zero in saved arithmetic; Fourier discrepancy 1.390e-16. Five interpreted figures, exact data, and twelve PDF pages reviewed. Canonical and reader bundles verified. Prior pipeline failures and their raw runs are retained.

P0/P1: source matched and prior Tests 2-3 packages reverified. P2A: explicit six-gate reciprocal routing registered. P3: plan/config locked before numerical execution; formatting-only preflight failure retained. P4: complete local recipe and reviewed reader export verified. GitHub-hosted dispatch/upload remains untested; `gross-test-04` is available after merge. Local full checks pass; browser validation is blocked by unavailable Chromium/denied OS dependency installation.

Test 11 spectral result: for this circuit's vacuum/equal wave sectors, opposite routing-derived drift vectors coexist with D=I/4; one common coordinate shift cannot erase their difference. Signed frequencies are used, not the later subcritical positive-frequency clock protocol. Operational Test 11 is not evaluated.

Next: derive a noncollinear, unequal-port periodic background with active memory response, then preregister its complete spectrum and stability tests. The present counter background is a collinear control; no broad background search was executed. Tests 5-10 retain their earlier status, and Tests 5 then 6 remain the independent continuum route.

## Test 5 evidence

[Reviewed interpretation](gross-test-05-results.md), [reader export](../../research/experiments/gross.continuum-action.v1/export-run-d3333c7602af3e47/README.md), and [canonical run](../../research/experiments/gross.continuum-action.v1/run-d3333c7602af3e47/manifest.json). Run `run-d3333c7602af3e47`; analysis `analysis-0001-4dbb966f`; report `report-0001`. All seven locked bounded checks pass, with maximum action Hessian/operator-metric residual `8.88e-16`, equations `4.88e-16`, roots `1.77e-15`. A negative `Z` fails health; the separately versioned quartic orientation control has speed `0.934947` against metric speed `1`.

P0/P1: current source matches the program and Test 1 algebra prerequisite is complete. P2B: the SS OCF 1 local action audit is registered with a closed config and named quartic control. P3: plan/config locked before execution. P4: final canonical run and reviewed reader export verified, with setup/results PDFs visually inspected. Two failed pipeline exports are preserved with logs and raw attempts. The gravity result is a flat linearized harmonic-gauge symbol/constraint audit only; nonlinear Einstein constraints, on-shell curved backgrounds and coupled evolution remain untested. No clock has been established. Next: Test 6 profile, independent eigenmode, finite-domain lifetime and trapping-off controls.
