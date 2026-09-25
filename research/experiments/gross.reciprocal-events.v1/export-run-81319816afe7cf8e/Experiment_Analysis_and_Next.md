# Test 2 analysis and next calculation

Test 2 passes its ten locked criteria for SS OPS 1 on this bounded circuit. The local recipe completed in 31.671 seconds, including analysis, reporting and packaging. This measures this execution environment, not expected GitHub queue or installation time.

Run: `run-81319816afe7cf8e`. Analysis: `analysis-0001-8c6b8920`. Reviewed report: `report-0002`. Solver revision: `183b95feeae1cc1d4bd79ad3b3cd506f4952fba0`. Report revision: `0ba0865`. Report 0002 only repairs a clipped annotation, marks a zero explicitly and narrows explanatory wording; it retains all original data and classifications. Report 0001 remains in the canonical package.

## Evidence and physical meaning

| Preregistered comparison | Observed | Gate |
| --- | --- | --- |
| Largest sampled conservation residual | 3.50812e-10 | below 1e-9 |
| Full-circuit exact-solution difference | 2.45401e-11 | below 1e-9 |
| Half-tolerance state/overlap difference | 2.14217e-11 | below 1e-9 |
| Legal schedule difference | exactly 0 in saved arithmetic | below 1e-9 |
| Independent local-frame difference | 2.07247e-11 | below 1e-9 |
| Outside-ancestor Jacobian | exactly 0 in saved arithmetic | below 1e-9 |
| Finite-difference step-halving difference | 4.23643e-8 | below 1e-6 |
| Smallest shared-memory order response | 0.0672786 | above 1e-4 |
| Smallest frozen-memory matrix-charge defect | 0.198404 | above 1e-4 |

Evidence: [checks](results/tables/checks.json), [summary](results/data/derived/summary.json), [gate residuals](results/data/derived/residuals.csv), [control values](results/data/derived/controls.csv), [Jacobian data](results/data/derived/jacobian.csv), [overlap records](results/data/derived/overlaps.csv), and [figure interpretations](figures/figure_index.json). The coverage criterion accounts for four preparations, both coupling values and 12 gates at two tolerances: 192 event-ledger rows. It does not mean 192 independent random preparations.

The substantive result is reciprocal exchange. Wave matrix charge changes while the carried memory supplies the compensating change. Freezing that memory leaves a large ledger defect. In these preparations, this supports implementing the reciprocal law rather than treating a driven projector as a passive fixed background. A frozen background is a valid separately specified external apparatus, but it is not the same closed event model.

Legal topological orders agree because they only swap disjoint events. Reversing events sharing a memory changes the memory's final ray, so that change is physical in this model rather than an arbitrary scheduler choice. The Jacobian's disconnected branch supplies a direct negative control for unimplemented distant influence. These checks numerically support the already-derived participant-local law; they do not discover the law from data.

The exact solution strengthens the numerical audit. With wave difference d and memory projector P, the Hermitian matrix S=dd-dagger+2P is constant. Its matrix exponential predicts the numerical trajectories without invoking the ODE solver. The Hamiltonian, symplectic structure and incidence remain assumptions; the constant-S solution is a consequence, not a new interaction selected after seeing results.

The first-gate charge curves and isolated order controls nearly coincide for lambda=0 and 0.1. This is expected: the lambda N term supplies a common wave phase within a gate and drops out of the projector equation. It does not prove that lambda never matters after differently phased wires meet later in a circuit.

## What this changes and what remains open

Test 1 previously established a verified finite algebra implementation screen. Test 2 adds a verified reciprocal event implementation and ordering/locality checks. This makes Test 3's routing calculation the next bounded prerequisite, without conflating the event circuit with an inferred metric.

All observed conservation errors are below the frozen threshold, including the finer integration, but the largest residual is only about 2.85 times below it. The conclusion is bounded numerical acceptance, not exact arithmetic preservation. The exact solution and half-tolerance differences provide additional error controls. The Jacobian covers one preparation at two couplings; structural locality follows from the participant-only circuit, while this numerical check would catch accidental implementation dependence outside it.

There is no spatial mesh or box, so continuum and spatial boundary convergence are not evaluated. The full wire cut is conserved for this flat-transport apparatus. Event Hamiltonian conservation is not a globally defined physical circuit energy. Neither the matrix charge nor its determinant has been established as spacetime energy-momentum or particle mass. U(2) frame covariance is not Lorentz covariance.

The local overlap records are algebraic apparatus diagnostics. There is no accepted autonomous clock, no frequency spectrum, and no measured travel time here. Drift, directional asymmetry, anisotropy, geometry with material response and multiple characteristics remain open. This experiment supplies no evidence for protected knots, quantum statistics, Standard Model identification or gravitational dynamics.

## Next discriminating calculation

Execute the smallest exact-Fourier part of Test 3 with a separately locked benchmark circuit. For three internal directions n_i, compare the small-wave-number dispersion with the Gram form G_ij=n_i dot n_j. Orthogonal triads predict an isotropic leading cone; oblique independent triads predict an anisotropic nondegenerate form; collinear triads predict degeneracy. Reversing the three-block order changes finite-wavelength terms while preserving the leading cone. Inspect the complete Brillouin zone instead of displaying only the desired low-wave-number branch.

Pair opposite wave vectors and retain the full microscopic spectrum for Test 4 and the spectral part of Test 11. The zero-wave stationary memory modes remain an analytically known obstruction to the strongest all-sector common-cone claim; this Test 2 pass does not remove that obstruction. A geometric wave sector interacting with material memory remains a separate interpretation to test. Elaborate reception experiments still require a demonstrated readable bound clock.
