# E01: three-dimensional charged recurrence branch and stability

## 1. Research question

Does the prescribed three-dimensional charged scalar action possess a numerically resolved stationary candidate that is stable within tested charge-preserving linear sectors and lies below all computed charge-conserving breakup thresholds?

This is the reference-state experiment for later topology binding. It does not include the neutral field, orientation field, Hopf charge, gauge emergence, particle identification, or damping claims.

## 2. Authoritative source and model

Use sections 2–10, 14–15, and 23 of `research/papers/charged-recurrence-winding-hopf.md`. Model ID: `charged-scalar-3d-v1`.

In units `c = ħ = 1`, use

\[
\mathcal L = \partial_\mu\Phi^*\partial^\mu\Phi-U(|\Phi|^2),
\qquad
U(s)=m^2s-gs^2+hs^3,
\]

with `m = g = h = 1`, `λ = 0.01`, and `ε = 0.1` retained in the complete source-model ledger. On this invariant stationary branch set the neutral field to exactly zero and omit the orientation field; neutral parameters cannot influence the solution.

Use the ansatz

\[
\Phi(t,r)=e^{-i\omega t}f(r)
\]

and solve

\[
f''+\frac{2}{r}f'=(m^2-\omega^2)f-2gf^3+3hf^5,
\]

with `f'(0)=0`, positive nodeless `f`, and a converged vacuum tail. The admissible frequency window is

\[
\sqrt{m^2-\frac{g^2}{4h}}<\omega<m.
\]

## 3. Configuration and units

The resolved configuration must declare:

- dimensionless unit convention and conversion ledger;
- frequency interval and adaptive continuation policy;
- radial coordinate mapping, domain radius, spacing/order, and origin treatment;
- tail boundary condition and tail-correction method;
- nonlinear solver and tolerances;
- quadrature independent from the residual discretization;
- spectral sectors, basis/domain, and eigensolver tolerances;
- breakup-channel search scope;
- refinement ladder and resource limits.

Unknown fields and non-finite values are rejected. Vacuum and noded profiles are recorded as rejected branch candidates, not silently discarded.

## 4. Branch construction

1. Obtain a nontrivial radial seed without assuming the desired stability.
2. Continue adaptively in `ω` or pseudo-arclength while retaining branch identity.
3. Record accepted, rejected, failed, and ill-conditioned points.
4. Detect turning points using continuation conditioning rather than sorting disconnected solves by frequency.
5. Preserve profiles and continuation tangents needed to audit branch traversal.

A visually localized profile is not enough. The independently evaluated scaled field residual must be below `1e-7` for a resolved point.

## 5. Independent observables

Compute energy `E`, Noether charge `Q`, radius measures, central amplitude, tail amplitude/correction, and residual norms using independent quadrature and derivative paths. Record both signed `Q` and `|Q|` conventions.

Check:

\[
T+3V-3W=0,
\qquad
E-\omega Q=\frac{2T}{3},
\qquad
\frac{dE}{dQ}=\omega.
\]

The first two relative defects target `<1e-5` where their normalization is well conditioned. The derivative relation targets relative discrepancy `<1e-3` on well-conditioned branch segments and must be repeated with frequency/continuation-step refinement.

## 6. Constrained linear spectrum

Linearize with an explicitly documented `exp(σt)` convention and coupled `u/v` perturbations. Enforce the first-order charge constraint rather than reading stability from an unconstrained Hessian. Use the radial measure and correct origin regularity.

Resolve at least angular sectors `ℓ = 0, 1, 2`. Identify the global phase and translation symmetry modes and compare their splitting with measured mesh/domain error. Extend to higher `ℓ` or provide a justified bound.

For every reported eigenpair require scaled residual `<1e-7`. Report eigenfunctions, constraint defect, solver convergence, and sensitivity to mesh, domain, basis size, shift, and tolerance. A negative unconstrained `L+` eigenvalue or the sign of `dQ/dω` alone is not a stability verdict.

## 7. Binding and breakup tests

Compare `E` with `m|Q|` and every computed charge-conserving split across resolved branches. Search discrete and continuous breakup allocations at a resolution justified by the branch interpolation error. Include tail, quadrature, continuation, and interpolation uncertainty.

A claimed binding margin must exceed three times the combined numerical error. This multiplier is an engineering acceptance margin, not a statistical significance statement.

## 8. Refinement and controls

- exact vacuum rejection;
- small-amplitude/tail asymptotic control;
- independent radial spacing refinement;
- independent outer-volume refinement;
- continuation-step refinement;
- nonlinear tolerance/order refinement;
- spectral basis/domain/tolerance refinement;
- origin and tail-normalization unit tests;
- alternative observable quadrature;
- explicit endpoint and turning-point unresolved labels.

On the finest independent spacing and volume comparisons, `E`, `Q`, and declared radius measures should change by `<0.5%`, except explicitly unresolved endpoints.

## 9. Scientific classification

The machine-readable outcome is one of:

- `candidate`: stationary, converged, below tested thresholds by the required margin, and linearly stable within all declared tested sectors;
- `no-candidate`: the preregistered domain was resolved and every branch point failed at least one criterion;
- `unresolved`: numerical conditioning, angular coverage, refinement, or threshold coverage is insufficient.

Reports must distinguish stationary, below-tested-threshold, and linearly stable within tested sectors. They must not infer a global minimum, nonlinear stability, longevity, topology binding, or particle identity.

## 10. Required artifacts

- resolved configuration and source-equation mapping;
- branch table including failures and condition estimates;
- profiles and tail fits;
- independent observable and identity tables;
- spectra, constraints, residuals, and eigenvectors;
- breakup-channel table;
- convergence and error-budget tables;
- plot data plus PNG/SVG/PDF figures;
- machine-readable classification with criterion-to-evidence links;
- Markdown/HTML/PDF report regenerated from saved data;
- complete checksums and provenance.

Archive under `research/experiments/e01-charged-branch/<run-id>/` only after package verification.
