# Signal Space: a 3+1D charged-recurrence model, winding sector, and explicit Hopf extension

Date: 17 September 2026.

Status: analytical model specification and derivation. No new 3D profile, stability spectrum, formation simulation, or knotted bound state is claimed in this document.

## 1. What is being extended

The supplied charged-clock model has a complex structural scalar and a real neutral scalar. Its 1+1D formation and radiation calculations establish behavior of that prescribed classical theory. This document extends its local action to 3+1D, derives the consequences, and then defines an additional orientation sector capable of carrying Hopf topology.

There are three distinct levels:

| Level                  | Fields and structure                                           | What is inherited or added                                                                     |
| ---------------------- | -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Minimal 3D recurrence  | Complex scalar Phi and real scalar a                           | Direct dimensional extension of the existing action                                            |
| Spatial winding        | The same fields, with azimuthally winding configurations       | New solution sector, not a new interaction                                                     |
| Hopf-linked recurrence | Phi, a, and a unit vector n with a stabilizing derivative term | A new, explicitly assumed effective theory containing the minimal model as a consistent sector |

The geometry is supplied Minkowski spacetime. Neither spatial dimension, Lorentz symmetry, charge quantization, quantum measurement, electric charge, nor a photon is derived from reception order. A numerical update order is not identified with fundamental physical time. Classical Q-balls and Hopf solitons are established constructions; the proposed Signal Space task is to test the specified coupling and interpret its local exchanges.

## 2. Conventions and dimensional consistency

Use natural units c = hbar = 1, coordinates x^mu = (t,x,y,z), and metric diag(+1,-1,-1,-1). Write Box = partial_t^2 - nabla^2. All repeated spatial indices run over three axes.

Choose the four-dimensional field normalization

$$
[\Phi]=[a]=M,\qquad [m]=M,\qquad [g]=[\lambda]=1,
\qquad [h]=[\epsilon]=M^{-2}.
$$

These dimensions differ from the 1+1D convention. Numerical statements such as m = g = h = 1 must not be transferred without specifying units. The sextic interaction and the derivative neutral coupling are effective interactions in four spacetime dimensions; quantization requires a regulator, a cutoff, and the symmetry-allowed counterterms. No ultraviolet completion is claimed.

## 3. Minimal action and its variation

Define s = |Phi|^2 and

$$
\boxed{
S_0=\frac1\lambda\int d^4x\left[
\partial_\mu\Phi^*\partial^\mu\Phi-U(s)
+\frac12 Z(s)\partial_\mu a\partial^\mu a\right],
}
$$

$$
U(s)=m^2s-gs^2+hs^3,\qquad Z(s)=1+\epsilon s.
$$

Take

$$
m>0,\quad g>0,\quad h>0,\quad\lambda>0,\quad
0<g^2<4hm^2,\quad\epsilon\ge0.
$$

Indeed,

$$
U(s)=s\left[h\left(s-\frac{g}{2h}\right)^2
+m^2-\frac{g^2}{4h}\right]\ge0,
\qquad Z\ge1.
$$

Variation with respect to Phi* gives

$$
\boxed{
\Box\Phi+(m^2-2gs+3hs^2)\Phi
-\frac\epsilon2\Phi\left(a_t^2-|\nabla a|^2\right)=0.
}
$$

Variation with respect to a gives

$$
\boxed{\partial_t(Za_t)-\nabla\cdot(Z\nabla a)=0.}
$$

The vacuum is Phi = 0 and constant a. Its linear spectrum is

$$
\sigma_\Phi^2=|\mathbf k|^2+m^2,
\qquad \sigma_a^2=|\mathbf k|^2.
$$

The neutral excitation remains a scalar in 3+1D; adding dimensions does not turn it into electromagnetism. The principal second-derivative terms of the minimal equations have the common Minkowski cone for Z > 0. This statement does not automatically extend to the derivative-interacting Hopf sector introduced later.

## 4. A local reception form with compatibility constraints

Set

$$
\Pi=\Phi_t,\quad D_i=\partial_i\Phi,\qquad
b=Za_t,\quad c_i=\partial_i a.
$$

The complete first-order-in-time system is

$$
\Phi_t=\Pi,
$$

$$
\Pi_t=\partial_iD_i-U_s\Phi
+\frac\epsilon2\Phi\left(\frac{b^2}{Z^2}-c_ic_i\right),
\qquad (D_i)_t=\partial_i\Pi,
$$

$$
a_t=\frac bZ,\qquad
b_t=\partial_i(Zc_i),\qquad
(c_i)_t=\partial_i\left(\frac bZ\right).
$$

If initially D_i = partial_i Phi and c_i = partial_i a, the evolution preserves these constraints in the continuum. Curl constraints are consequently preserved too. Do not treat D_i or c_i as independent physical polarizations.

For any unit spatial direction e, structural characteristic combinations are Pi +/- e dot D, with analogous neutral combinations a_t +/- e dot grad a. Their propagation involves transverse derivatives as well as the local source. Three dimensions are not three independent copies of the old left/right clock: all directional exchanges update the same retained local fields.

This gives a local, finite-speed interpretation of a supplied field theory. It does not derive that theory from a bare partially ordered set.

## 5. Charge, energy, momentum, angular momentum, and local ledgers

Choose the charge sign so Phi = exp(-i omega t) f has positive charge for omega > 0. The conserved current is

$$
j_Q^\mu=\frac i\lambda
\left(\Phi^*\partial^\mu\Phi-\Phi\partial^\mu\Phi^*\right),
\qquad\partial_\mu j_Q^\mu=0.
$$

Thus

$$
\rho_Q=-\frac2\lambda\operatorname{Im}(\Phi^*\Phi_t),
\qquad
\mathbf j_Q=\frac2\lambda\operatorname{Im}(\Phi^*\nabla\Phi),
\qquad Q=\int\rho_Q\,d^3x.
$$

Let L_0 denote the bracket in S_0, without 1/lambda. The symmetric stress tensor is

$$
T^{\mu\nu}=\frac1\lambda\left[
\partial^\mu\Phi^*\partial^\nu\Phi
+\partial^\nu\Phi^*\partial^\mu\Phi
+Z\partial^\mu a\partial^\nu a-g^{\mu\nu}L_0\right].
$$

In particular,

$$
\mathcal E=T^{00}=\frac1\lambda\left[
|\Phi_t|^2+|\nabla\Phi|^2+U
+\frac Z2(a_t^2+|\nabla a|^2)\right]\ge0,
$$

$$
\mathbf S_E=\mathbf T^{0}= -\frac1\lambda\left[
2\operatorname{Re}(\Phi_t^*\nabla\Phi)+Za_t\nabla a\right].
$$

The total quantities are

$$
E=\int\mathcal E\,d^3x,\qquad
\mathbf P=\int\mathbf S_E\,d^3x,\qquad
\mathbf J=\int\mathbf x\times\mathbf S_E\,d^3x.
$$

For an isolated finite-energy configuration they are conserved. For any fixed volume V,

$$
\frac{dQ_V}{dt}=-\oint_{\partial V}\mathbf j_Q\cdot d\mathbf A,
\qquad
\frac{dE_V}{dt}=-\oint_{\partial V}\mathbf S_E\cdot d\mathbf A.
$$

There is also a neutral shift current j_a^mu = Z partial^mu a/lambda. Its conserved integrated charge, when finite, is not Q and does not make a an electromagnetic gauge field.

### The real-component interpretation

Write Phi = (q_1 + i q_2)/sqrt(2), and p_A = qdot_A/lambda. Then

$$
\rho_Q=q_2p_1-q_1p_2.
$$

For a reciprocal local bond kick, Delta p_i = kappa(q_j-q_i), Delta p_j = -Delta p_i, the total internal circulation q_1 p_2 - q_2 p_1 of the pair is unchanged. Radial internal kicks and free drifts also preserve it. This algebra is independent of the spatial embedding of the graph.

Internal isotropy and reciprocal dynamics are substantive assumptions equivalent to the relevant symmetry, not consequences of ordering alone. Explicitly delayed exchanges would require a charge ledger for the propagating links as well as the sites. Neither Q nor its classical density is an integer count of events.

## 6. The unseeded neutral sector and the absence of a classical static scalar force

The exact sector a = constant, a_t = 0 remains invariant, even for moving, colliding, or oscillating structural objects. There is no spontaneous classical neutral radiation from those initial conditions.

For a regular static configuration with constant a at infinity and no neutral sources, multiply div(Z grad a) = 0 by a-a_infinity and integrate. With vanishing boundary term,

$$
\int Z|\nabla a|^2\,d^3x=0,
$$

so grad a = 0. Therefore the existing coupling does not generate a classical Coulomb field around an isolated object. Prepared neutral waves can scatter and recoil against it. Quantum emission and quantum-mediated interactions require separate calculations.

## 7. Charge-supported relative equilibria

Set a = 0 and seek

$$
\Phi(t,\mathbf x)=e^{-i\omega t+i\theta_0}f(\mathbf x),
\qquad f\ge0.
$$

The modulus, energy density, and stresses are time-independent; the internal field phase rotates. This is a relative equilibrium, not a pulsating density or a literal orbit of photons.

Define

$$
I[f]=\int f^2\,d^3x,\qquad Q=\frac{2\omega I}{\lambda}.
$$

For a prescribed amplitude profile, minimizing the time-derivative energy at fixed Q gives uniform phase rotation. This follows from Cauchy-Schwarz applied to Q and the kinetic norm. Eliminating omega gives

$$
\boxed{
E_Q[f]=\frac1\lambda\int\left[|\nabla f|^2+U(f^2)\right]d^3x
+\frac{\lambda Q^2}{4I[f]}.
}
$$

The local variational equation is

$$
\boxed{\nabla^2f=(m^2-\omega^2)f-2gf^3+3hf^5,\qquad
\omega=\frac{\lambda Q}{2I}.}
$$

This derives the recurrence from constrained energetics within the assumed action. It does not establish global minimality for every stationary solution.

Along a smooth branch,

$$
\frac{dE}{dQ}=\omega.
$$

An absolute phase is invisible to a detector coupled only through |Phi|^2. Phase-clock readout still requires a physical reference and causal overlap or exchange of the structural field. A classical continuously variable charge is not an already quantized particle spectrum.

## 8. Spherical branch and boundary conditions

For f = f(r),

$$
\boxed{f''+\frac2r f'=(m^2-\omega^2)f-2gf^3+3hf^5.}
$$

The regular, localized boundary conditions are

$$
f'(0)=0,\qquad f(0)>0,\qquad f(r)\to0\quad(r\to\infty).
$$

At the origin, with F(f) = (m^2-omega^2)f - 2gf^3 + 3hf^5,

$$
f(r)=f_0+\frac{F(f_0)}6r^2+O(r^4).
$$

At large r,

$$
f(r)\sim C\frac{e^{-kr}}r,
\qquad k=\sqrt{m^2-\omega^2}>0.
$$

The admissible positive-frequency interval is

$$
\boxed{\omega_{\min}<\omega<m,\qquad
\omega_{\min}^2=m^2-\frac{g^2}{4h}.}
$$

Its lower endpoint comes from min_{s>0} U(s)/s; the upper endpoint gives an evanescent vacuum tail. These are the standard Q-ball existence conditions for this potential, not a stability certificate for the whole interval. The 1D cosh profile and its analytic Q(omega) formula do not solve this radial problem.

The observables are

$$
Q=\frac{8\pi\omega}{\lambda}\int_0^\infty r^2f^2dr,
$$

$$
E=\frac{4\pi}{\lambda}\int_0^\infty
r^2\left[\omega^2f^2+(f')^2+U(f^2)\right]dr,
$$

$$
R_Q^2=\frac{\int_0^\infty r^4f^2dr}{\int_0^\infty r^2f^2dr}.
$$

There is no numerical value for a stable 3D benchmark Q or R_Q until this boundary-value problem and its stability conditions are solved.

## 9. Virial identity and two analytically distinct limits

Write

$$
T=\lambda^{-1}\int|\nabla f|^2d^3x,\quad
V=\lambda^{-1}\int U(f^2)d^3x,\quad
W=\frac{\lambda Q^2}{4I}=\frac{\omega Q}{2}.
$$

Under f(x) -> f(x/R), at fixed charge,

$$
E_Q(R)=RT+R^3V+R^{-3}W.
$$

Stationarity and the energy identity imply

$$
\boxed{T+3V=3W,\qquad E-\omega Q=\frac23T.}
$$

The second size derivative is 6V + 12W > 0, but this tests just one dilation direction. It does not exclude amplitude redistribution, nonspherical instability, or breakup. For d spatial dimensions the virial identity is (d-2)T + dV = dW.

### 9.1 Large-charge, thin-wall limit

Let

$$
s_0=\frac{g}{2h},\qquad
\omega_0=\omega_{\min}.
$$

As omega approaches omega_0 from above, the interior approaches f^2 = s_0 and a large radius R. To leading order,

$$
Q\simeq\frac{2\omega_0s_0}{\lambda}\frac{4\pi R^3}{3}.
$$

At omega_0,

$$
U(f^2)-\omega_0^2f^2=h f^2(f^2-s_0)^2.
$$

The planar wall tension in the constrained functional is

$$
\tau=\frac2\lambda\int_0^{\sqrt{s_0}}
\sqrt{U(f^2)-\omega_0^2f^2}\,df
=\frac{\sqrt h\,s_0^2}{2\lambda}.
$$

Consequently the leading fixed-charge energy expansion is

$$
E(Q)=\omega_0Q+4\pi\tau
\left(\frac{3\lambda Q}{8\pi\omega_0s_0}\right)^{2/3}
+o(Q^{2/3}).
$$

The surface correction and the linear bulk term have the correct mass dimension. The frequency is dE/dQ, so its finite-radius correction must be kept when comparing this expansion with E-omega Q = 2T/3. Setting omega exactly to omega_0 in that identity while retaining the surface correction would be inconsistent.

Because omega_0 < m, sufficiently large configurations on this branch lie below the free-wave threshold mQ. The positive Q^{2/3} surface term disfavors fission into two macroscopic thin-wall pieces at leading order. Small fragments, other branches, and perturbative stability still require explicit checks.

### 9.2 Diffuse, thick-wall limit: a critical difference from one dimension

Put k = sqrt(m^2-omega^2), and scale

$$
f(r)=\frac{k}{\sqrt g}F(kr).
$$

Then

$$
F''+\frac2yF'=F-2F^3+3\frac{hk^2}{g^2}F^5.
$$

For the nodeless diffuse branch as k -> 0, the limiting localized profile obeys the cubic equation. If C_3 = integral F^2 d^3y,

$$
I\sim\frac{C_3}{gk},\qquad
\boxed{Q\sim\frac{2\omega C_3}{\lambda gk}.}
$$

Thus Q diverges as omega -> m in three dimensions, rather than tending to zero as it does on the corresponding 1D branch. More generally Q scales as omega k^{2-d} at leading order.

In particular dQ/domega is positive near the 3D upper endpoint. This is a warning associated with the usual unstable diffuse Q-ball branch, not permission to assume the entire continuation is stable. A turning point of Q(omega) and a minimum-charge structure are expected when this branch is connected to the thin-wall branch. Their positions must be computed. The old omega/m = 0.90 benchmark is only a trial frequency in 3D.

## 10. The full angular stability problem

Around a spherical solution write

$$
\Phi=e^{-i\omega t}(f+u+iv),\qquad a=\alpha.
$$

At linear order,

$$
u_{tt}+2\omega v_t+L_+u=0,\qquad
v_{tt}-2\omega u_t+L_-v=0,
$$

$$
L_+=-\nabla^2+m^2-\omega^2-6gf^2+15hf^4,
$$

$$
L_-=-\nabla^2+m^2-\omega^2-2gf^2+3hf^4.
$$

For normalized spherical harmonics Y_{ell m}, replace these by

$$
L_{\pm,\ell}=-\frac{d^2}{dr^2}-\frac2r\frac d{dr}
+\frac{\ell(\ell+1)}{r^2}+V_\pm(r).
$$

For time dependence exp(-i Omega t), the spectral problem is

$$
\begin{pmatrix}
L_{+,\ell}-\Omega^2&-2i\omega\Omega\\
2i\omega\Omega&L_{-,\ell}-\Omega^2
\end{pmatrix}
\binom UV=0.
$$

Regular modes behave as r^ell at the origin. At infinity impose decay in closed channels and outgoing conditions in open channels when computing resonances. The lab-frame sidebands have frequencies omega +/- Omega and vacuum wavenumbers squared (omega +/- Omega)^2 - m^2. A pole with Im Omega < 0 is damped under this convention; an unstable eigenmode has Im Omega > 0.

The phase zero mode lies in ell = 0, with L_- f = 0. Translation zero modes lie in ell = 1, with L_+ partial_i f = 0. The first-order fixed-charge condition is

$$
\delta Q=\frac1\lambda\int
\left(4\omega fu-2fv_t\right)d^3x=0.
$$

The neutral linear equation is

$$
Z(f^2)\alpha_{tt}-\nabla\cdot[Z(f^2)\nabla\alpha]=0.
$$

For angular index ell its positive spatial operator is

$$
-\frac1{r^2}\frac d{dr}\left(r^2Z\frac{d\alpha_\ell}{dr}\right)
+\frac{Z\ell(\ell+1)}{r^2}\alpha_\ell
=\Omega^2Z\alpha_\ell.
$$

A radial evolution tests only ell = 0. Stability of a 3D object requires the angular sectors too, or a justified bound excluding higher sectors. In addition compare E(Q) with free-wave thresholds and every energetically relevant charge partition. The slope dQ/domega alone is not a universal stability certificate.

## 11. Radiation, angular cancellation, and cooling

For a = 0, rewrite the structural equation as

$$
(\Box+m^2)\Phi=S,\qquad S=2g|\Phi|^2\Phi-3h|\Phi|^4\Phi.
$$

For a temporal component exp(-i sigma t) with |sigma| > m, let k_sigma = sqrt(sigma^2-m^2). Its outgoing far field is

$$
\Phi_\sigma\sim\frac{\mathcal A_\sigma(\hat{\mathbf r})}{r}
e^{i\operatorname{sgn}(\sigma)k_\sigma r-i\sigma t},
$$

$$
\boxed{
\mathcal A_\sigma(\hat{\mathbf r})=
\frac1{4\pi}\int S_\sigma(\mathbf x)
e^{-i\operatorname{sgn}(\sigma)k_\sigma\hat{\mathbf r}\cdot\mathbf x}\,d^3x.
}
$$

This follows from the outgoing Helmholtz Green function. For an approximately periodic nonlinear state it is an on-solution source reconstruction; it is not an independent prediction from a freely prescribed source.

For a spherical source,

$$
\mathcal A_\sigma=\int_0^\infty r^2S_\sigma(r)
\frac{\sin(k_\sigma r)}{k_\sigma r}\,dr.
$$

Different radial shells can cancel. Nonspherical perturbations supply additional multipoles rather than only this spherical integral.

The outward energy and charge flux per solid angle are

$$
\frac{dP_\sigma}{d\Omega_{\rm solid}}
=\frac{2|\sigma|k_\sigma}{\lambda}|\mathcal A_\sigma|^2,
\qquad
\frac{dJ_{Q,\sigma}}{d\Omega_{\rm solid}}
=\frac{2\operatorname{sgn}(\sigma)k_\sigma}{\lambda}|\mathcal A_\sigma|^2.
$$

Hence P_sigma = sigma J_Q,sigma. Negative-frequency radiation carries positive energy and negative charge. Angular directions do not cancel their outgoing energies.

For a core measured relative to a smooth reference branch M(Q),

$$
\Delta E=E_{\rm core}-M(Q_{\rm core}),\qquad
-\dot{\Delta E}=P_{\rm out}-\omega_QJ_{Q,\rm out}.
$$

If angular momentum or another independent conserved quantity changes, use the corresponding reference energy M(Q,J,...) and include its additional conjugate-frequency flux terms. The 1D damping rate and its primary/secondary harmonic weights must be recomputed in 3D.

## 12. Integer winding without adding a new field

Use cylindrical coordinates (rho,phi,z) and the stationary winding ansatz

$$
\Phi=e^{-i\omega t+iN\varphi}F(\rho,z),\qquad N\in\mathbb Z,
\qquad a=0.
$$

Single-valuedness around phi -> phi + 2pi requires integer N. The equation is

$$
\boxed{
F_{\rho\rho}+\frac1\rho F_\rho+F_{zz}
-\frac{N^2}{\rho^2}F
=(m^2-\omega^2)F-2gF^3+3hF^5.
}
$$

For N != 0 regularity requires F = O(rho^{|N|}) on the axis. At spatial infinity F decays. For N = 0 impose F_rho = 0 on the axis. Reflection symmetry in z can be imposed for an even solution but is not a law of the theory.

The energy and charge are

$$
E=\frac{2\pi}{\lambda}\int_0^\infty\rho\,d\rho\int_{-\infty}^\infty dz
\left[\omega^2F^2+F_\rho^2+F_z^2+\frac{N^2F^2}{\rho^2}+U(F^2)\right],
$$

$$
Q=\frac{4\pi\omega}{\lambda}\int_0^\infty\rho\,d\rho\int dz\,F^2.
$$

Since partial_phi Phi = i N Phi,

$$
\boxed{J_z=-\frac2\lambda\int\operatorname{Re}
(\Phi_t^*\partial_\varphi\Phi)d^3x=NQ.}
$$

This exact relation holds for this ansatz. It is not a proof that all rotating states obey J_z = NQ, or that classical Q is quantized. The angular gradient term favors an off-axis density distribution, allowing toroidal profiles, but no particular rotating solution or stability result is supplied here.

Phase winding is not Hopf charge. Phi vanishes in the exterior and on the axis of these configurations, so the phase does not define an everywhere regular map from compactified 3-space into a nonzero vacuum circle. Phase slips, deformations, and fragmentation must be included in stability tests. A stationary winding state must be compared at its conserved Q and J with all accessible final states, including orbital angular momentum and radiation.

## 13. Many-object initial data and formation data

The same field equations evolve any number of objects. Approximate initial superposition is allowed for well-separated fields; it is not an exact nonlinear solution. For an exact stationary single-object profile, a Lorentz boost is defined by evaluating the scalar solution at Lorentz-transformed coordinates. Initial velocities are derivatives of that boosted solution, not an independent guessed phase gradient.

For multiple separated objects, prepare the sum of their Cauchy data, compute the actual total E, P, Q, J including any overlap, and evolve freely. Relative phases affect local interference and nonlinear interactions after causal contact. Individual core charges can exchange; total charge remains conserved. No additional pair force should be appended.

A spherical nonstationary Gaussian preparation is

$$
\Phi(0,r)=A e^{-r^2/(2w^2)},\qquad
\Phi_t(0,r)=-i\nu\Phi(0,r),\qquad a=a_t=0,
$$

$$
I=A^2\pi^{3/2}w^3,\qquad
A^2=\frac{\lambda Q_0}{2\nu\pi^{3/2}w^3}.
$$

Its exact continuum initial energy is

$$
E_G=\frac1\lambda\left[
(m^2+\nu^2)I+\frac{3I}{2w^2}
-\frac{gI^2}{2^{3/2}\pi^{3/2}w^3}
+\frac{hI^3}{3^{3/2}\pi^3w^6}\right].
$$

This distinguishes below-threshold preparation from genuinely above-threshold data. Add nonspherical perturbations after the radial baseline; a symmetry-constrained simulation cannot discover the excluded modes. Formation from Q = 0 cannot produce a nonzero net Q in a closed system; opposite-charge pairs require a separate dynamics and threshold test.

## 14. Dimensionless parameters and a reproducible starting point

Set

$$
\bar x^\mu=mx^\mu,\qquad
\Phi=\frac m{\sqrt g}\psi,\qquad
a=\frac m{\sqrt g}\alpha.
$$

Then

$$
S_0=\frac1{\lambda g}\int d^4\bar x\left[
|\bar\partial\psi|^2-|\psi|^2+|\psi|^4-\eta|\psi|^6
+\frac12(1+\zeta|\psi|^2)(\bar\partial\alpha)^2\right],
$$

$$
\boxed{\eta=\frac{hm^2}{g^2}>\frac14,\quad
\zeta=\frac{\epsilon m^2}{g}\ge0,\quad
\lambda_4=\lambda g.}
$$

The 4D overall coupling is lambda_4, unlike the 1+1D rescaling lambda g/m^2. The classical equations depend on eta and zeta, while the normalization affects Q, E, and the quantum expansion. Physical mass and length scales are restored through m.

A direct comparison benchmark is eta = 1, zeta = 0.1, lambda_4 = 0.01. Its frequency interval is sqrt(3)/2 < omega/m < 1. These are declared inputs, not fitted constants of nature. Begin a branch continuation over this interval, then select a stable reference charge from the computed results rather than asserting that the 1D omega/m = 0.90 state remains stable.

## 15. A regulator preserving the intended conservation law

On a cubic lattice of spacing d, use Phi = (q_1+i q_2)/sqrt(2), p_A = qdot_A/lambda, and p_a = Z adot/lambda, with brackets {q_A,n,p_B,m} = delta_AB delta_nm/d^3. Let Z on a bond be the arithmetic mean of its endpoint values.

The lattice Hamiltonian is

$$
H_d=d^3\sum_n\left\{
\frac\lambda2\sum_{A=1}^2p_{A,n}^2
+\frac{\lambda p_{a,n}^2}{2Z_n}
+\frac1\lambda\left[
U(s_n)+\frac12\sum_{i,A}(\delta_iq_{A,n})^2
+\frac12\sum_i Z_{n+i/2}(\delta_i a_n)^2\right]\right\},
$$

where delta_i is the forward difference divided by d, and each bond is counted once. Split into A = structural kinetic energy, B = neutral kinetic energy, and C = coordinate-only energy, then compose

$$
A(\Delta t/2)B(\Delta t/2)C(\Delta t)B(\Delta t/2)A(\Delta t/2).
$$

The B flow includes the structural momentum kick from derivatives of 1/Z. The C flow includes derivatives of the bond Z values. Each subflow preserves

$$
Q_d=d^3\sum_n(q_{2,n}p_{1,n}-q_{1,n}p_{2,n}).
$$

Energy is conserved by the continuous-time lattice system, only approximately by the time splitting. Spatial rotations, translations, and Lorentz invariance are broken by this regulator and require continuum checks. The finite lattice is not a derived microscopic reception substrate.

For the free structural lattice the linear stability condition of this second-order splitting includes Delta t sqrt(m^2 + 12/d^2) < 2. Nonlinear local stiffness can tighten it. Use refinement rather than treating that vacuum bound as a nonlinear guarantee. Boundaries must be causally excluded or accompanied by explicit flux and reflection checks. A radial solver needs an independently consistent origin stencil and volume weights.

## 16. Why Hopf linking is absent from the minimal model

The current vacuum is Phi = 0. Its phase is undefined there; a single complex scalar does not supply the everywhere defined S^2 orientation required for the standard Hopf invariant. Writing suggestive linked phase contours does not change this.

To obtain a genuine map S^3 -> S^2, introduce a physical unit vector

$$
\mathbf n(x)\in S^2,\qquad\mathbf n^2=1,
\qquad\mathbf n(\mathbf x)\to\mathbf n_0=(0,0,1)
\quad(|\mathbf x|\to\infty).
$$

The spatial boundary condition compactifies space to S^3. The n field is defined even where Phi vanishes. This is a new degree of freedom and a new vacuum structure, not a change of notation for Phi.

A normalized complex doublet z supplies an algebraic representation n = z^dagger sigma z, with z^dagger z = 1. Its common phase is redundant in n. It must not silently be identified with the physical U(1) phase of Phi. A vanishing unconstrained doublet would also permit n to become undefined and topology to change.

## 17. An explicit coupled Hopf extension

Define

$$
H_{\mu\nu}=\mathbf n\cdot
(\partial_\mu\mathbf n\times\partial_\nu\mathbf n).
$$

Choose the action

$$
\boxed{
S_H=S_0+\frac1\lambda\int d^4x\left[
\frac{K(s)}2\partial_\mu\mathbf n\cdot\partial^\mu\mathbf n
-\frac{\kappa_H}{4}H_{\mu\nu}H^{\mu\nu}
-V_n(\mathbf n)\right],\quad\mathbf n^2=1,
}
$$

with the fully specified positive stiffness

$$
K(s)=F_*^2\left(1-\alpha_*\frac{s}{M_*^2+s}\right),
\qquad
V_n=F_*^2\mu_n^2(1-n_3),
$$

$$
F_*>0,\quad M_*>0,\quad\kappa_H>0,\quad
0\le\alpha_*<1,\quad\mu_n\ge0.
$$

Here F__, M__, mu_n have mass dimension one; alpha_* and kappa_H are dimensionless. K is bounded below by F__^2(1-alpha__) > 0. The minus sign in the Lorentzian H^2 term gives positive static spatial-curvature energy. The potential fixes the preferred orientation when mu_n > 0; setting mu_n = 0 restores its full internal rotational symmetry.

This particular K(s) is a proposed coupling, not a derived Signal Space law. Its derivative is

$$
K_s=-\frac{F_*^2\alpha_*M_*^2}{(M_*^2+s)^2}\le0.
$$

Structural density lowers the cost of orientation gradients, providing a controlled candidate attraction between a charged lump and a Hopf texture. The nonzero lower bound preserves orientation stiffness even at high density. At alpha_* = 0 the sectors decouple apart from sharing spacetime and the overall normalization; no charged-Hopf binding follows then.

Setting n = n_0 exactly makes every added term and its source vanish. Thus every solution of the minimal model embeds as a solution of the extended equations. For a stationary Q-ball this embedding also has a positive linear orientation fluctuation operator, as derived below; nonlinear topology-bearing states require a separate analysis.

## 18. Extended field equations and positive energy

The neutral equation is unchanged. The structural equation becomes

$$
\boxed{
\Box\Phi+U_s\Phi-\frac\epsilon2\Phi(\partial a)^2
-\frac{K_s}{2}\Phi(\partial\mathbf n)^2=0.
}
$$

Introduce the orientation momentum, with the overall 1/lambda suppressed,

$$
\mathbf P_n^\mu=K\partial^\mu\mathbf n
+\kappa_H H^{\mu\nu}(\mathbf n\times\partial_\nu\mathbf n).
$$

The constrained orientation equation is

$$
\boxed{
(\mathbf 1-\mathbf n\mathbf n^T)
\left[\partial_\mu\mathbf P_n^\mu-F_*^2\mu_n^2\mathbf e_3\right]=0,
\qquad\mathbf n^2=1.
}
$$

One can equivalently take n cross the bracket. In the Euler-Lagrange variation the explicit n derivative of H^2 is normal to the target sphere and is removed by this projection. Derivatives of K(s) inside partial_mu P_n^mu must be retained. Initial orientation velocity is tangent: n dot n_t = 0.

The additional energy density is

$$
\boxed{
\mathcal E_n=\frac1\lambda\left[
\frac K2(|\mathbf n_t|^2+|\nabla\mathbf n|^2)
+\frac{\kappa_H}{2}\sum_iH_{0i}^2
+\frac{\kappa_H}{4}\sum_{i,j}H_{ij}^2+V_n\right]\ge0.
}
$$

Q remains exactly conserved because all additional couplings depend on Phi only through s. The total stress tensor gains

$$
\Delta T^{\mu\nu}=\frac1\lambda\left[
K\partial^\mu\mathbf n\cdot\partial^\nu\mathbf n
-\kappa_H H^{\mu\rho}H^\nu{}_{\rho}
-g^{\mu\nu}L_n\right],
$$

where L_n is the added Lagrangian bracket. Total energy, momentum, and spatial angular momentum include this term. The orientation action also preserves rotations around e_3, with current P_n^mu dot(e_3 cross n)/lambda. Static textures have zero corresponding charge; it is a separate symmetry from the structural Q. When mu_n = 0 there are three internal rotational generators.

Near the trivial vacuum the added sector contains two orientation modes of mass mu_n, or two extra massless modes if mu_n = 0. These are genuine new physical channels. They do not identify a photon or fermion.

For a stationary Q-ball with n = n_0, write the small tangent orientation perturbation as the two-vector pi_n. To quadratic order H^2 does not contribute, and

$$
K(f^2)(\boldsymbol\pi_n)_{tt}
-\nabla\cdot[K(f^2)\nabla\boldsymbol\pi_n]
+F_*^2\mu_n^2\boldsymbol\pi_n=0.
$$

Its quadratic energy is nonnegative. The structural and orientation perturbations decouple at linear order around this background, so this specified extension adds no exponentially growing orientation mode there. This does not settle finite-amplitude stability or stability around a nonuniform Hopf texture.

The energy is positive and the equations contain at most second derivatives, but their principal symbol depends on orientation gradients. A well-posed, hyperbolic evolution region must be checked for the chosen backgrounds and perturbations. Do not transfer the minimal model's common-cone statement to arbitrary Hopf-sector data simply because this action is Lorentz invariant.

## 19. Hopf charge, normalization, and what linking protects

On a smooth compactified spatial slice, let the two-form

$$
\mathcal H=\frac12H_{ij}\,dx^i\wedge dx^j
$$

be the pullback of the unit sphere's area form, whose integral over S^2 is 4pi. Since H^2(S^3) = 0, choose a one-form A_H satisfying dA_H = mathcal H. Then define

$$
\boxed{
\mathscr H=\frac1{16\pi^2}\int_{S^3}A_H\wedge dA_H
=\frac1{32\pi^2}\int d^3x\,\epsilon^{ijk}(A_H)_iH_{jk}
\in\mathbb Z.
}
$$

The overall sign depends on orientation conventions. Equivalently, for a normalized lift z, b_H = -i z^dagger dz has db_H = mathcal H/2 and

$$
\mathscr H=\frac1{4\pi^2}\int b_H\wedge db_H.
$$

These potentials are constructions used to compute the invariant, not an added electromagnetic field. The preimages of two generic regular target directions are collections of closed curves; their total linking number is mathscr H. A nonzero Hopf charge need not be represented by a single knotted curve, and configurations with the same charge may have different knot/link shapes.

Smooth evolution with fixed boundary orientation preserves mathscr H. A topology-changing singularity, a change of boundary conditions, or an extension that permits n to become undefined can defeat that protection. Charge conservation and Hopf conservation remain distinct: neither Q = mathscr H nor a particle-mass formula follows.

In particular, a nonzero total Hopf charge cannot be generated from a uniform n field by smooth evolution with those fixed boundary conditions. Nonzero-charge textures must be supplied in the initial topological sector, enter through a boundary, or arise through a separately specified topology-changing mechanism. Opposite-charge texture pairs with zero total Hopf charge are a different possible process; their formation is not demonstrated here.

## 20. Why an extra derivative term is necessary

For a static orientation texture with s = 0, write its energy as E_2 + E_4 + E_0, from the two-derivative, four-derivative, and potential terms. Under n(x) -> n(x/R),

$$
E_n(R)=R E_2+R^{-1}E_4+R^3E_0.
$$

Without E_4 a nontrivial texture can lower its energy by shrinking. A knot label alone does not create a preferred size. With E_4 > 0,

$$
E_2-E_4+3E_0=0
$$

is the stationary scaling balance. For mu_n = 0 the natural length scale is of order sqrt(kappa_H)/F_* and the energy scale is F_* sqrt(kappa_H)/lambda, multiplied by dimensionless shape-dependent factors. These scales are inserted by the new coefficients, not derived constants.

This is the role of the Skyrme-Faddeev term: sharp concentration of orientation gradients becomes expensive. It is additional physics beyond the charged-clock potential.

## 21. Joint charged-Hopf relative equilibria and the binding test

Take

$$
\Phi=e^{-i\omega t}f(\mathbf x),\qquad
a=0,\qquad\mathbf n=\mathbf n(\mathbf x).
$$

At fixed Q and Hopf class mathscr H, the energy functional is

$$
\boxed{
E_{Q,\mathscr H}[f,\mathbf n]=\frac{\lambda Q^2}{4\int f^2d^3x}
+\frac1\lambda\int d^3x\left[
|\nabla f|^2+U(f^2)+\frac{K(f^2)}2|\nabla\mathbf n|^2
+\frac{\kappa_H}{4}H_{ij}H_{ij}+V_n\right].
}
$$

Stationarity with respect to f yields

$$
\boxed{
\nabla^2 f=\left[U_s(f^2)-\omega^2
+\frac{K_s(f^2)}2|\nabla\mathbf n|^2\right]f,
\qquad\omega=\frac{\lambda Q}{2\int f^2d^3x}.
}
$$

The static orientation equation follows from section 18 or by constrained variation of this energy. Since K_s < 0 for alpha_* > 0, orientation gradients can lower the effective structural restoring coefficient and favor density in the texture. This is a possible binding mechanism, not proof of a joint soliton.

The sharp necessary energetic comparison is

$$
E_{\rm joint}(Q,\mathscr H)
<E_{\rm Qball}(Q)+E_{\rm Hopf}(\mathscr H),
$$

where the right side represents infinite separation. Further compare with all relevant partitions of Q and mathscr H and with emitted radiation, and compute the constrained fluctuation spectrum. A solution can be stable against changing its Hopf class yet unstable to splitting into several textures in the same total class.

At alpha_* = 0, separation costs no cross-coupling energy and the construction supplies no joint binding mechanism. For nonzero alpha_* the two-way back-reaction is included in the displayed equations. Uniform n gives the old Q-ball sector with the positive linear orientation operator above; finite-amplitude reorganization and stability of nonuniform joint solutions are new questions.

This is a complete proposed coupled classical action and stationary variational problem. Its nontrivial charged-Hopf solutions, their formation, and their causal evolution have not been computed here.

## 22. Integer structures and their limits

| Label                                      | Origin                                                           | What it does not establish                                 |
| ------------------------------------------ | ---------------------------------------------------------------- | ---------------------------------------------------------- |
| Harmonic index n                           | Fourier mixing, e.g. n_out = n_1 - n_2 + n_3 in the cubic source | A rational value for the physical frequencies              |
| Angular index ell and magnetic index m_ang | Spherical-harmonic decomposition                                 | Quantized classical particle spin                          |
| Winding N                                  | Single-valued azimuthal phase in a specified ansatz              | Hopf topology or universal J = NQ for every state          |
| Hopf integer mathscr H                     | Smooth maps S^3 -> S^2 with fixed boundary                       | Equality with structural charge, mass, or a fermion number |
| Structural Q                               | Continuous classical Noether charge                              | Integer quantization before a quantum theory is specified  |

In special toroidal constructions a Hopf number can be expressed as a product of two winding integers. That is a property of those maps, not an independently derived mass spectrum. No prime-number law, fine-structure constant, Koide relation, or exact recurrence frequency follows from the present extension.

## 23. What should be calculated next

The model is specified sufficiently to proceed without inventing a new cooling bath or force law.

1. Continue the spherical 3D boundary-value problem across omega, including both sides of any Q minimum. Check field residuals, tails, the virial identity, and dE/dQ = omega.
2. Compute the fixed-charge spectrum including angular sectors; compare breakup thresholds. Select an actual stable 3D benchmark from these results.
3. Test formation from Gaussian data with an explicit E/mQ ledger, then perturb nonspherically and test collisions. Recompute angular radiation and damping instead of importing the 1D resonance.
4. Solve the N = 1 winding boundary-value problem; test nonaxisymmetric fragmentation at fixed total Q and J.
5. Independently validate the orientation model, its Hopf normalization, and its hyperbolic evolution regime. Minimize the joint functional at fixed (Q,mathscr H), then compare against separated constituents before claiming a charged knot.

These are proposed calculations, not results performed in this derivation. A successful result at one level is not assumed to pass later levels.

## 24. Provenance and external mathematical context

The direct extension uses the supplied Signal Space_Charged_Clock_Formation_Milestone.md and Signal Space_Charged_Clock_Radiation_Milestone.md, and the Signal Space_Ordered_Reception_Charged_Clock_Model.md embedded in Signal Space_Formation_Source.zip. Their original setting is 1+1D. The action, boundary conditions, normalization changes, and conditional Hopf coupling above are stated explicitly so the extension can be checked independently.

- [Battye and Sutcliffe, Q-ball Dynamics](https://arxiv.org/abs/hep-th/0003252): established Q-ball dynamics in one, two, and three spatial dimensions, including interactions and charge transfer.
- [Almumin, Heeck, Rajaraman, and Verhaaren, Slowly rotating Q-balls](https://arxiv.org/abs/2302.11589): Q-ball existence and rotation; explains the ansatz-dependent nature of J = NQ and more general slowly rotating configurations.
- [Faddeev, Knotted solitons](https://arxiv.org/abs/math-ph/0212079): the three-dimensional orientation-field and Hopf-invariant framework.
- [Sutcliffe, Knots in the Skyrme-Faddeev model](https://arxiv.org/abs/0705.1468): numerical linked and knotted solitons in that established model; not evidence for the new coupling proposed here.

The algebraic derivations in this document are for the explicitly displayed actions. Literature establishes the surrounding constructions, not the existence or stability of the particular new coupled charged-Hopf candidate.
