# Signal Space charged-clock milestone: constrained spectrum and breakup

Date: 17 September 2026.

## Result

The proposed object passes the classical, fixed-charge linear-stability test at omega=0.90. The apparent negative shape direction is removed by imposing charge conservation correctly. Translation and phase remain neutral symmetry directions. The neutral radiation field has a nonnegative, gapless spectrum. Breakup into separated members of the same Q-ball branch and free charged waves is energetically forbidden, including unequal and opposite-charge fragmentations.

The coupled structural spectrum has no resolved nonzero localized mode below its lowest radiation threshold, Omega=m-omega=0.10m. The lowest positive frequencies seen in a finite box move toward that continuum edge as the box grows; they are not a newly discovered internal clock oscillator. Independent continuum decaying-boundary calculations support this conclusion.

This is a positive result for a stable classical phase recurrence. It is not a calculation of quantum linewidths, a protected clock doublet, coherent capture, or formation. It does not establish stability against every large nonlinear perturbation or provide a complete variational existence theorem for arbitrary final configurations.

## 1. Model and calculation scope

Keep the previously specified model unchanged:

$$
\mathcal L=\frac1\lambda\left[
|\partial\Phi|^2-U(s)+\frac12Z(s)(\partial a)^2\right],
\qquad s=|\Phi|^2,
$$

$$
U(s)=m^2s-gs^2+hs^3,
\qquad Z(s)=1+\epsilon s.
$$

The benchmark parameters are m=g=h=1 in mass units, lambda=0.01, epsilon=0.1, omega=0.90. The background is

$$
\Phi=e^{-i\omega t}f(x),\quad a=0,\quad
f^2=\frac{2\kappa^2}{1+d\cosh(2\kappa x)},
$$

$$
\kappa=\sqrt{1-\omega^2},\qquad d=\sqrt{1-4\kappa^2}.
$$

The computation combines an analytic constrained-energy argument, finite-difference eigenvalue calculations about mesh-consistent stationary profiles, a continuum Evans-determinant scan, and analytic and numerical breakup thresholds. It is not a time-evolution experiment.

## 2. The actual coupled fluctuation problem

Set Phi=exp(-i omega t)(f+u+iv). The linear equations are

$$
u_{tt}+2\omega v_t+L_+u=0,
\qquad
v_{tt}-2\omega u_t+L_-v=0,
$$

$$
L_+=-\partial_x^2+1-\omega^2-6f^2+15f^4,
$$

$$
L_-=-\partial_x^2+1-\omega^2-2f^2+3f^4.
$$

For modes proportional to exp(i Omega t), choose u=U exp(i Omega t), v=iV exp(i Omega t). Then

$$
\begin{pmatrix}
L_+-\Omega^2&-2\omega\Omega\\
-2\omega\Omega&L_--\Omega^2
\end{pmatrix}
\begin{pmatrix}U\\V\end{pmatrix}=0.
$$

Taking square roots of the individual eigenvalues of L+ or L- would give the wrong physical frequencies. Their time-derivative coupling is essential.

The linear charge constraint is

$$
\delta Q=\frac1\lambda\left[
4\omega\int f u\,dx-2\int f v_t\,dx\right]=0.
$$

Thus an amplitude perturbation cannot be varied while silently holding its conjugate phase velocity fixed and allowing charge to change.

## 3. Analytic removal of the apparent unstable direction

The exact identities

$$
L_-f=0,\qquad L_+f'=0
$$

have strong consequences on the infinite line. Since f is nodeless, Sturm ordering makes zero the lowest L- eigenvalue. Since f' has one node, L+ has exactly one eigenvalue below zero; the next is its translation zero mode.

The negative L+ eigenvalue is therefore real, but it is not by itself evidence of a physical instability at fixed charge.

Let I=integral f^2 dx. Minimizing kinetic energy over velocities at fixed Q gives, for a real amplitude profile,

$$
E_Q[f]=\frac1\lambda\int[(f')^2+U(f^2)]\,dx
+\frac{\lambda Q^2}{4\int f^2dx}.
$$

For f -> f+delta u, the coefficient of delta squared in E_Q is lambda^-1 <u,K_Q u>, with

$$
\boxed{
K_Q=L_++\frac{4\omega^2}{I}|f\rangle\langle f|.
}
$$

The operator |f><f| acts by f(x) integral f(y)u(y)dy. It is not an additional nonlocal force: it results from eliminating velocities subject to one global conserved-charge constraint. The underlying field evolution remains local.

Differentiation of the profile equation gives L+ partial_omega f=2 omega f. On the even subspace, where the odd translation kernel is absent,

$$
1+\frac{4\omega^2}{I}\langle f,L_+^{-1}f\rangle
=1+\frac{\omega I'}I
=\frac{\lambda Q'}{2I}.
$$

At the benchmark,

$$
I=1.3404479147,
\qquad Q'=-2829.0228243,
$$

$$
\frac{\lambda Q'}{2I}=-10.55252798<0.
$$

Starting from one negative eigenvalue, this positive rank-one correction crosses and removes that eigenvalue. The even constrained operator is positive; the odd sector is nonnegative with translation as its only zero direction. The imaginary-field variation has nonnegative L- quadratic form with the phase zero mode. Velocity components beyond the constrained minimum add positive squares.

Consequently the fixed-charge quadratic energy is nonnegative, with only the expected symmetry degeneracies in the localized structural sector. This excludes finite-energy exponentially growing linear modes. A drift of the center or phase from a symmetry/generalized symmetry mode is not an exponential instability. Phase comparisons must account for these collective coordinates.

This argument covers the high-frequency structural sector too; stability is not inferred solely from a finite list of low eigenvalues.

## 4. Neutral signal spectrum

At linear order, alpha=delta a obeys

$$
Z(f^2)\alpha_{tt}-\partial_x[Z(f^2)\alpha_x]=0.
$$

Its quadratic energy is

$$
E_a^{(2)}=\frac1{2\lambda}\int Z(f^2)
(\alpha_t^2+\alpha_x^2)dx\ge0.
$$

Let rho=sqrt(Z), psi=rho alpha, and W_a=rho'/rho. The frequency operator is

$$
H_a=-\partial_x^2+\frac{\rho''}{\rho}
=(-\partial_x-W_a)(\partial_x-W_a)\ge0.
$$

Since rho tends to 1 at both infinities, the continuum begins at zero. The formal zero solution psi=rho is not square-integrable; a constant a is the shift symmetry, not a localized oscillator. The short-range one-dimensional potential has oscillatory asymptotic solutions at positive energy, so there is no ordinary positive-energy square-integrable bound mode.

The epsilon interaction first couples neutral fluctuations to structural perturbations beyond quadratic order about this a=0 background. This establishes linear neutral stability, not absence of nonlinear scattering, quantum emission, or phase noise. The complete theory remains gapless.

## 5. Structural continuum and the absence of a resolved extra oscillator

Far from the object, both L operators approach -partial_x^2+1-omega^2. The dispersion relation is

$$
(k^2+1-\omega^2-\Omega^2)^2-4\omega^2\Omega^2=0.
$$

Positive co-rotating frequencies are

$$
\Omega_-(k)=\sqrt{k^2+1}-\omega,
\qquad
\Omega_+(k)=\sqrt{k^2+1}+\omega.
$$

Thus their thresholds are 0.10m and 1.90m. The laboratory mass of a free structural quantum is still m; Omega is a frequency relative to the rotating background. These thresholds are distinct from the neutral continuum at zero.

Finite-box convergence results are inserted below from the executed source.

| Half-domain mL | Grid m dx | Lowest positive Omega/m | Fraction in core |
|---:|---:|---:|---:|
| 40 | 0.100 | 0.1024202149 | 0.158645 |
| 40 | 0.050 | 0.1024201942 | 0.159511 |
| 60 | 0.050 | 0.1011362550 | 0.063724 |
| 80 | 0.050 | 0.1006635616 | 0.031249 |
| 80 | 0.025 | 0.1006635594 | 0.031339 |


The shrinking core fraction of the lowest positive box mode is additional evidence that it is becoming an extended continuum state. Core fraction here means integral of |u|^2+|v|^2 over |x|<10/m divided by the same integral over the full box. It is a localization diagnostic, not a quantum probability or symplectic norm.

The phase and translation zero modes split into small numerical eigenvalue clusters of order 1e-8 to 1e-6 in the first-order dynamical matrix, depending on arithmetic and grid. Their exact continuum identities and constrained-energy result identify them as symmetry modes, not growing physical excitations. No nonzero computed eigenmode has a resolved real growth rate.

### Independent continuum boundary calculation

For 0<Omega<0.1, asymptotic decay constants are

$$
k_s=\sqrt{1-(\omega+\Omega)^2},\qquad
k_f=\sqrt{1-(\omega-\Omega)^2}.
$$

Integrate the two-dimensional decaying solution space inward from x=L using its exterior square. This avoids loss of a solution through dominance by the faster exponential. Even bound states require det(U',V')=0 at the origin; odd bound states require det(U,V)=0. These determinants are evaluated from the two basis solutions, not from one arbitrarily selected component.

Divide out the known Omega squared behavior at zero. A scan of 210 frequencies, with extra points approaching 0.1 from below, finds no sign-changing root in either parity. The closest point to threshold is Omega=0.1-1e-9. Changing the starting boundary and integration tolerances checks the determinants independently of the finite-difference mesh.

The minimum scaled even determinant over the scan was 0.79549965, and the minimum scaled odd determinant was 6.83211530; both remained positive. These magnitudes depend on basis normalization; their zeros are the physical test. Tightening the relative integration tolerance from 2e-11 to 2e-12 changed the checked determinants by at most 1.39e-13. Starting at L=40 and L=60 also agrees at the displayed accuracy; L=20 shows the expected larger tail error near threshold.

This is numerical evidence for no nonzero subthreshold localized mode, not a certified interval proof that no arbitrarily narrow or tangential root exists. No claim is made here about resonances inside the continuum or exceptional embedded modes. The analytic quadratic-energy argument, rather than this scan, establishes absence of exponential linear instability.

## 6. Analytic breakup result for the entire selected branch

For m=g=h=1, define

$$
b=2\sqrt{1-\omega^2}=\tanh r,\qquad r>0,
\qquad\omega(r)=\sqrt{1-\tfrac14\tanh^2r}.
$$

The exact charge and energy simplify to

$$
Q(r)=\frac{2\omega(r)r}{\lambda},
$$

$$
E(r)=\frac1\lambda\left[
(\omega(r)^2+\tfrac34)r+\frac14\tanh r\right].
$$

These formulas agree with direct profile quadrature. The branch runs from Q=0 to arbitrarily large Q, with omega decreasing from 1 to sqrt(3)/2.

To establish monotonicity, use

$$
\operatorname{artanh}b<\frac{b}{1-b^2},\qquad 0<b<1.
$$

It follows that dQ/dr>0: in

$$
\frac{dQ}{dr}=\frac2\lambda\left[
\omega-\frac{r\tanh r\operatorname{sech}^2r}{4\omega}\right],
$$

the subtracted numerator is less than b squared, while 4 omega squared=4-b squared>b squared. Since domega/dr<0,

$$
\frac{dQ}{d\omega}<0,
\qquad
\frac{dE}{dQ}=\omega,
\qquad
\frac{d^2E}{dQ^2}=\frac1{Q'}<0.
$$

At the benchmark E''=-0.0003534789438 in the declared units.

Strict concavity and E(0)=0 imply

$$
\boxed{E(q)+E(Q-q)>E(Q),\qquad0<q<Q.}
$$

This excludes all nontrivial same-sign two-fragment splits into this branch, and induction excludes arbitrarily many such fragments. For mixed signs, the total absolute charge is at least |Q|. Applying the same inequality to the absolute charges and using monotonic E(Q) excludes opposite-charge fragmentation as well. Kinetic energies and neutral radiation only increase final energy.

Free charged radiation of net charge q has energy at least m|q|. Because E(q)<mq for positive q, replacing any bound fragment by free waves does not open a lower threshold. In particular,

$$
E(Q-q)+mq-E(Q)
=\int_{Q-q}^{Q}[m-\omega(q')]\,dq'>0
$$

for 0<q<=Q. This is stronger than testing complete free dissociation alone.

The proof compares the exact fundamental Q-ball branch, its charge-conjugate branch, and free charged waves. It is not a proof classifying every possible nonlinear configuration of the full theory.

## 7. Numerical threshold ledger

The benchmark rest energy and charge are

$$
Q=241.2806246494,\qquad E=230.9043694139\,m.
$$

All costs below are final rest energy minus initial rest energy, so positive values mean the isolated object cannot undergo that process spontaneously.

| Final configuration | Energy cost / m |
|---|---:|
| Entire charge dispersed into free charged waves | 10.37625524 |
| Two equal fundamental Q-balls | 7.00577923 |
| 25% / 75% charge split | 5.05467727 |
| 10% / 90% charge split | 2.28823108 |
| 1% / 99% charge split | 0.24023005 |
| Q-1 remnant plus one free unit of positive charge | 0.09982276 |
| Q-1 remnant plus a classical unit-charge Q-ball | 0.09982172 |
| Q+1 remnant plus a classical negative-unit-charge Q-ball | 1.89982272 |

The last three are tree-level evaluations of a continuously parameterized classical energy curve. They are not renormalized integer-charge quantum thresholds. In particular, a unit-charge classical fragment is outside the well-controlled large-charge semiclassical regime.

There is no uniform positive cost for every classical split: as q tends to zero, the cost tends to (m-omega)q and therefore to zero. This does not invalidate the strict inequality for any nonzero fragment. It prevents interpreting the fission result as a finite mass gap.

## 8. Numerical method and reproducibility

The supplied Python program requires NumPy, SciPy and Matplotlib. Run

```bash
OPENBLAS_NUM_THREADS=1 python calculate_milestone.py
```

It writes results.json and stability_diagnostics.png next to the source. The archive includes the source, this report, the model specification, dependencies, executed results, and figure.

For each grid, the code first solves the discrete stationary profile equation by Newton iteration, starting from the exact continuum profile. This avoids manufacturing a phase instability by linearizing a discrete evolution around a background that is not stationary on that mesh. It then constructs L+, L-, the constrained rank-one Hessian, and the coupled first-order evolution matrix.

The source checks the lowest Sturm-operator eigenvalues and the constrained Hessian, solves for low dynamical eigenpairs near the gap, and records eigenvector residuals. Both mesh and domain are varied. A deterministic seed is supplied to the iterative eigensolvers. Last digits of near-zero eigenvalues depend on numerical libraries and do not carry physical significance.

At the finest grid (L=80, dx=0.025), the lowest L+ eigenvalues are approximately -0.272637973, zero, and 0.189154925. The lowest L- eigenvalues are zero and 0.179936477. The constrained Hessian has the translation zero followed by a positive eigenvalue 0.186060100. These are static curvature eigenvalues, not the coupled normal-mode frequencies.

The largest recorded dynamical eigenvector residual is 1.96e-12. The largest stationary-background equation residual is 1.11e-11. The largest near-zero dynamical cluster magnitude is 9.18e-07; its sensitivity to background and arithmetic residuals is expected for symmetry modes. The maximum real part in the resolved nonzero modes is 5.95e-16. These residuals characterize the numerical approximation, not physical decay rates.

At L=80, refining dx from 0.05 to 0.025 changes the lowest positive box frequency by 2.26e-09, whereas changing L from 40 to 80 produces a much larger shift toward the continuum. This distinguishes a domain effect from a mesh artifact.

The continuum Evans calculation uses the exact profile and a high-order adaptive ODE solver; it is an independent method rather than a second evaluation of the same discrete matrix. The analytic branch formulas are checked against direct quadrature of the field energy and charge.

## 9. What this changes for Signal Space

The earlier kink shape clock could radiate its defining excitation away. This candidate now has a demonstrated classical stability mechanism: charge conservation changes the admissible perturbations, eliminating the negative amplitude direction, while the energy curve disfavors fragmentation.

The recurrence is still the rotating field phase, not a newly found trapped shape oscillator. Its frequency changes with charge. A finite phase reference, charging event, or charge-dependent outgoing record may therefore alter or dephase the clock. The negative curvature E'' quantifies a source of charge-dependent phase evolution; it is not a phase-diffusion calculation.

The next milestone is now justified: evolve unbound charged initial data and determine whether a localized recurrence forms while excess energy and momentum leave through the same equations. Keep a=0 as an explicit classical control; that channel remains zero exactly, so classical cooling in that control must use Phi radiation. Separately test prepared neutral packets and eventual quantum spontaneous emission. Do not add noise or friction to guarantee formation.

The first formation scan should use the previously specified fixed-charge Gaussian preparations with w/R_Q in {0.5,1,2,4} and nu/m in {0.8,0.9,1.0}, retaining successful and unsuccessful outcomes, with mesh refinement, outgoing-flux accounting, and a causal two-object phase-readout protocol after formation.

## Sources

- Signal_Space_Ordered_Reception_Charged_Clock_Model.md, 17 September 2026: exact model, conventions, parameter choices, and milestone scope.
- Supplied Signal_Space_Full_Theory_Research_Architecture-1.md and Signal_Space_Part_II.md: distinction between reference-geometry controls, physical clocks, quantum coherence, and autonomous formation.
- [Gulamov, Nugaev, Smolyakov, Analytic Q-ball solutions and their stability in a piecewise parabolic potential](https://arxiv.org/abs/1303.1173): primary literature context for explicitly solving 1+1-dimensional Q-ball perturbation spectra. Its potential differs from the one calculated here.
- [Panin and Smolyakov, Problem with classical stability of U(1) gauged Q-balls](https://arxiv.org/abs/1612.00737): why the ordinary ungauged Q-ball criterion must not be transferred automatically to a gauged theory. This candidate has a global charge and a neutral scalar; it is not the gauged model of that paper.

All model-specific numbers and stability arguments in this report are computed or derived from the stated Signal Space candidate. Literature citations provide context, not substitute numerical results.
