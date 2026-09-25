# Signal Space / GROSS Test 1

Tracking: #52. Runtime dependency: #37. The historical Paper I epic #1 is a separate scope.

Source: [Operator program v0.2](../../research/papers/gross-operator-program-v0.2.md), 24 September 2026, sections 2-4 and 15.1. Supplied source SHA-256: `c733c958fde54c810c38889e5096de54358a77cc10e69d9f885870832595e123`.

This registers `gross.operator-identities.v1` with model `signal-space.operator-constitution.v1`. It checks the common algebraic prerequisites of SS OPS 1 and SS OCF 1. It does not register either candidate's physical evolution or reuse the charged-scalar equations.

## Definitions and independent check

A Hermitian operator is $X=x^0I+x^i\sigma_i$, where $I$ is the identity and $\sigma_i$ are the Pauli matrices. The worker computes the determinant polarization

$$
\mathfrak g(X,Y)=\frac{\operatorname{tr}X\operatorname{tr}Y-\operatorname{tr}(XY)}2.
$$

Analysis extracts the four real coefficients directly from matrix entries and independently computes $x^0y^0-\mathbf x\cdot\mathbf y$. A positive aggregate $J=AA^\dagger$ is made from the two columns of $A$. Its observer is $T=J/\sqrt{\det J}$. Test $\det T=1$, the norm $z^\dagger T^{-1}z=2\mathfrak g(T,zz^\dagger)$, covariance under $SL(2,\mathbb C)$ congruence, and positivity of $h_T(X,Y)=2\mathfrak g(T,X)\mathfrak g(T,Y)-\mathfrak g(X,Y)$.

For $P=zz^\dagger/(z^\dagger z)$ and $c=\operatorname{tr}(SPS^\dagger)$, check $P'=SPS^\dagger/c$ and $\rho'=c\rho$. Omitting the transformed weight is the deliberately incorrect control, not a new physical model.

## Frozen sampling and thresholds

- Full run: 1,000 samples, root seed 2026092501. NumPy PCG64 uses the runtime's independently derived sampling seed. Save start/end RNG state and all matrices.
- Random Hermitian Pauli coefficients and complex state constituents use independent standard normal components. Reject matrices/aggregates with condition number above 100; cap rejection at 10,000 trials per draw. Both signs of determinant are permitted for general Hermitian operators.
- Frame transformations are independent quaternion-generated SU(2) rotations surrounding a diagonal boost with uniform rapidity in [-1,1]. The condition domain is imposed on original matrices/aggregates, not silently on transformed records.
- Near-collinear columns are (1,0) and (cos(angle),sin(angle)); angles are 0, 0.5, 0.1, 0.01, ..., 1e-8 radians. Exact rank one is rejected. Condition number above 100 is explicitly outside the accepted observer domain, never regularized.
- Require each well-conditioned scale-normalized residual strictly below 1e-10 and positive observer norms/forms. Scalar differences use max(1, appropriate norm/product or reference magnitude). Idempotence and unit determinant/trace errors are dimensionless absolute residuals.
- Four tetrahedral projectors must have sorted Gram spectrum (-1/3,-1/3,-1/3,1) within 1e-10. The fixed boost negative control must show omitted-weight error above 1e-3; its independent exact prediction is 1-exp(-1).
- Wall/CPU ceilings: 60 seconds each; memory 512 MiB; attempt output 16 MiB. Resource estimates are conservative planning values, not benchmarks. BLAS thread counts are fixed to one and recorded in raw execution metadata.

## Controls, interpretation and exclusions

All checks are algebraic and dimensionless. There is no time integration, physical spatial boundary, conserved dynamical charge or detector record to evaluate. Mesh, timestep and domain convergence are not applicable. Conditioning is studied instead. A physical field visualization is omitted because this experiment contains no field on spacetime.

The three required figure IDs are `operator-residuals`, `tetrahedral-gram`, and `observer-domain`. Exact zeros remain in the data, with an explicit 1e-18 display floor for logarithmic residual charts. Ill-conditioned and singular data remain visible and outside the acceptance population.

Missing inputs or interrupted execution leave this experiment unresolved/pending analysis; failed identities or undetected controls fail the hypothesis. Technical completion is separate. The short atomic batch deliberately advertises no checkpoint/resume capability; a new bounded attempt/run is needed after interruption.

## Reproduce

Use the pinned Python environment, and set OPENBLAS_NUM_THREADS, OMP_NUM_THREADS and MKL_NUM_THREADS to 1. Run from the checkout:

```sh
python3 .agents/scripts/experiment_contract.py plan docs/research/plans/gross-test-01.json
python3 .agents/scripts/run_plan.py --plan docs/research/plans/gross-test-01.json --repo-root . --workspace .research-work --execute
```

Then use the returned run ID with the registered analyze, report, verify and archive operations. The reader export is a derivative of the canonical run, not a replacement for its evidence. Provenance pins the actual implementation commit. Later report improvements never alter original raw data.
