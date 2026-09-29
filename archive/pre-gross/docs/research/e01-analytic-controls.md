# E01 analytic controls and normalization ledger

This is an implementation reference for issue #39, checked against the prescribed action in `research/papers/charged-recurrence-winding-hopf.md` §§2–10, 14–15. It supplies no computed branch or stability finding. `python/tests/test_e01_analytic_controls.py` checks the continuum algebra with analytic profiles and independent quadrature; the future solver must pass its own independent discretization and refinement tests.

## Action, units, and observables

Use the complete structural Lagrangian `(|∂Φ|² − U)/λ` with `U(s)=m²s−gs²+hs³`. In four dimensions `[Φ]=[m]=M`, `[g]=[λ]=1`, `[h]=[ε]=M⁻²`. The invariant `a=0` branch is independent of ε. The profile equation is independent of λ; its energy and charge are not.

For `Φ=exp(−iωt)f(r)`, positive ω gives positive Q:

\[
I=4\pi\int_0^\infty r^2 f^2dr,\quad
T=\frac{4\pi}{\lambda}\int_0^\infty r^2(f')^2dr,\quad
V=\frac{4\pi}{\lambda}\int_0^\infty r^2U(f^2)dr,
\]
\[
Q=\frac{2\omega I}{\lambda},\quad W=\frac{\omega^2 I}{\lambda},\quad
E=T+V+W,\quad R_Q^2=\frac{\int r^4f^2dr}{\int r^2f^2dr}.
\]

The source's dimensionless variables give `η=hm²/g²`, `ζ=εm²/g`, `λ₄=λg`; `Q=2ω̄∫|ψ|²d³x̄/λ₄`, `E=m Ē/λ₄`, and `R=R̄/m`. State explicitly whether reported quantities include λ₄; use the above physical normalization for E01. At the prescribed benchmark `η=1`, the strict frequency interval is `√3/2 < ω/m < 1`. Endpoints are excluded.

## Origin and tail

With `F(f)=(m²−ω²)f−2gf³+3hf⁵`, regularity gives `f=f₀+F(f₀)r²/6+O(r⁴)` and `∇²f(0)=3f″(0)`. Replacing the origin Laplacian by `f″(0)` introduces a factor of three error.

Write the exterior linear tail using its boundary amplitude rather than exponentially large C:

\[
f(r)=f_R\frac Rr e^{-k(r-R)},\quad k=\sqrt{m^2-\omega^2}.
\]

The Robin condition is `f′(R)+(k+1/R)f(R)=0`, not the one-dimensional condition `f′+kf=0`. Define `A=f_R²R²`. Linear exterior integrals are

\[
I_{\rm tail}=4\pi\frac A{2k},\quad
T_{\rm tail}=\frac{4\pi A}{\lambda}\left(\frac k2+\frac1R\right),\quad
E_{\rm tail}=\frac{4\pi A}{\lambda}\left(\frac{\omega^2+m^2}{2k}+\frac k2+\frac1R\right),
\]
\[
\int_R^\infty r^4 f^2dr=A\left(\frac{R^2}{2k}+\frac{R}{2k^2}+\frac1{4k^3}\right).
\]

These formulas omit nonlinear exterior potential terms. Check their size and tail-fit residual; do not treat the linear correction as exact for a finite-amplitude boundary. Near `k=0`, domain and correction errors can dominate.

## Independent variational and spectral checks

At fixed Q, dilation gives `E_Q(R)=RT+R³V+R⁻³W`; thus stationarity implies `T+3V−3W=0` and `E−ωQ=2T/3`. The second identity is algebraically related to the first and is not independent evidence if the same quadratures are reused. Evaluate the field residual and observables through independent numerical paths. The branch relation `dE/dQ=ω` requires a smooth, well-conditioned branch and continuation-step refinement.

Under the requested `exp(σt)` convention, source §10 becomes

\[
\begin{pmatrix}L_{+,\ell}+\sigma^2&2\omega\sigma\\-2\omega\sigma&L_{-,\ell}+\sigma^2\end{pmatrix}\binom UV=0,
\]

where `L₊=−∇²+m²−ω²−6gf²+15hf⁴` and `L₋=−∇²+m²−ω²−2gf²+3hf⁴`, with `ℓ(ℓ+1)/r²` in each radial operator. Here `σ=−iΩ`; growth means `Re σ>0`. The first-order charge constraint is `δQ=λ⁻¹∫(4ωfU−2σfV)d³x=0`. For `ℓ>0`, the angular integral vanishes; radial modes still require the correct `r²dr` measure and `r^ℓ` regularity. Phase and translation modes are `L₋f=0` at `ℓ=0` and `L₊f′=0` at `ℓ=1` respectively.

In the vacuum, with spatial wavenumber p, the coupled determinant has roots `σ=±i(√(p²+m²)±ω)`. This is a useful sign control, not a soliton stability test. A negative unconstrained L₊ eigenvalue, a virial pass, or the sign of `dQ/dω` is insufficient to claim stability.

## Implementation in #39

The registered `e01-charged-branch` plugin implements radial seeding/continuation, independent residuals and quadratures, constrained angular spectra, breakup allocation, refinements, and criterion-linked classification. SciPy 1.17.0 is pinned and recorded in execution identity. See [Running E01](e01-running.md) for equation mapping, controls, author launch instructions, and explicit numerical limits. This implementation does not include a research-scale finding.
