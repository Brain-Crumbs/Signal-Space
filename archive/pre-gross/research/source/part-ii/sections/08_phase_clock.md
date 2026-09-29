# 8. A confined phase clock with fixed calibration {#sec-phase-clock}

## 8.1. Recurrence and quantum readout

A recurrent subsystem can carry a relative phase read through Part I's coherent recombination protocol. For a selected two-level sector, write

$$
U_C=|0\rangle\langle0|+e^{-i\phi}|1\rangle\langle1|,
\qquad
p_+(\vartheta)=\tfrac12[1+\mathcal V\cos(\phi-\vartheta)].
\tag{K1}
$$

The phase is relative to the analyzer setting $\vartheta$. This is an operational record law, not a self-reading absolute phase. Repeatedly prepared trials or a fully specified weak continuous readout are needed to estimate an evolving phase. A finite-dimensional phase is periodic: an unwrapped time also requires cycle records or a restricted observation interval. Those records consume physical memory and can disturb the clock.

If a phase accumulates at a stable angular frequency $\omega_0$ in an independently calibrated inertial preparation, define the inferred reading $\tau_\phi=(\phi-\phi_0)/\omega_0$ on an unwrapped branch. The dynamical origin of $\phi$ must then be supplied. Merely choosing $U_C=\exp[-i\omega_0\tau\,|1\rangle\langle1|]$ with proper time inserted by hand would not test a clock hypothesis.

We instead compute a propagation phase in a specified confined system. The field model supplies more physical structure than Part I, but the added structure is explicit and its finite-size consequences can be evaluated.

## 8.2. Prescribed uniformly accelerated cavity

Take a flat $1+1$ reference spacetime and a nonrotating cavity whose center has constant signed proper acceleration $a$. Let $\tau$ be center proper time and $\chi$ proper distance from the center in its instantaneous rest slices. For $a\ne0$, the coordinate transformation is

$$
\begin{aligned}
c_0t&=(c_0^2/a+\chi)\sinh(a\tau/c_0),\\
x-x_0&=(c_0^2/a+\chi)\cosh(a\tau/c_0)-c_0^2/a.
\end{aligned}
\tag{K2}
$$

Direct differentiation gives

$$
ds^2=-c_0^2(1+a\chi/c_0^2)^2d\tau^2+d\chi^2.
\tag{K3}
$$

Place reflecting boundaries at $\chi=\pm L/2$ and require $|a|L/(2c_0^2)<1$. The separation is fixed in these rest slices; different points have different proper accelerations. This is prescribed Born-rigid motion over the cavity domain, not a dynamical rigidity or binding theorem.

Define the optical coordinate

$$
y(\chi)=\frac{c_0^2}{a}\ln(1+a\chi/c_0^2),\qquad
\ell_{\rm opt}=y(L/2)-y(-L/2).
\tag{K4}
$$

Then (K3) is conformal to $-c_0^2d\tau^2+dy^2$. A massless scalar wave in two spacetime dimensions satisfies the flat wave equation in $(\tau,y)$ because the conformal factors cancel in its classical wave operator. With Dirichlet boundaries, its stationary mode frequencies measured relative to center $\tau$ are

$$
\omega_n(a)=\frac{n\pi c_0}{\ell_{\rm opt}},\qquad n=1,2,\ldots.
\tag{K5}
$$

Equivalently, the round-trip null propagation duration in center time is $2\ell_{\rm opt}/c_0$. This independently recovers the fundamental phase recurrence. No photon identification or $3+1$ electromagnetic boundary calculation is required for this scalar control. Extended field-clock models have been studied in relativistic quantum information [6,7]; the current symmetric, stationary acceleration setup isolates one exactly solvable finite-size effect.

## 8.3. Exact error under inertial calibration

**Proposition K1 (symmetric cavity phase rate).** Set $\epsilon=aL/(2c_0^2)$ and calibrate the mode at $a=0$ with $\omega_{n0}=n\pi c_0/L$. For a stationary mode during constant acceleration,

$$
\frac{d\tau_\phi}{d\tau}
=\frac{\omega_n(a)}{\omega_{n0}}
=f(\epsilon):=\frac{\epsilon}{\operatorname{artanh}\epsilon},
\qquad f(0)=1.
\tag{K6}
$$

For $|\epsilon|<1$,

$$
1-\epsilon^2\leq f(\epsilon)\leq1,
\qquad
f(\epsilon)=1-\frac{\epsilon^2}{3}
-\frac{4\epsilon^4}{45}+O(\epsilon^6).
\tag{K7}
$$

*Proof.* Equation (K4) gives $\ell_{\rm opt}=L\,\operatorname{artanh}\epsilon/\epsilon$. Substitution into (K5) proves (K6). For $0\leq\epsilon<1$, integrating $1\leq(1-u^2)^{-1}\leq(1-\epsilon^2)^{-1}$ from zero to $\epsilon$ bounds $\operatorname{artanh}\epsilon/\epsilon$ between $1$ and $(1-\epsilon^2)^{-1}$. Inversion gives the bounds. The ratio is even; expanding its reciprocal power series gives the stated coefficients. $\square$

Under fixed inertial calibration the extended cavity reads slightly less than center proper time. The leading error is $a^2L^2/(12c_0^4)$ in fractional rate. Its sign and magnitude follow from this symmetric geometry; they should not be extrapolated to every accelerated clock.

The result is exact for the prescribed stationary constant-acceleration field and its ideal boundaries. It does not include the preparation or transition from inertial motion to acceleration. Such switching can mix modes and create excitations, and arbitrary time-dependent acceleration cannot be handled by silently substituting $a(\tau)$ into (K6). Those cases require a separate field-evolution calculation. The small-$L$ limit here is a controlled ideal-boundary limit, not proof that arbitrarily small physical clocks can be constructed without energetic cost.

## 8.4. Incorporation into Part I's record model

Quantize the selected stationary mode as a benchmark and restrict preparation and ideal free evolution to its vacuum and one-excitation subspace. Their relative phase is $\omega_n(a)\Delta\tau$, yielding (K1). This uses Part I's quantum postulate plus the supplied field dynamics. It neither derives that postulate nor infers a universal action scale from the frequency. Identifying the energy difference as $\hbar\omega_n$ would invoke an independently normalized physical quantization.

Part I's controlled reception marker sends $|0\rangle|0\rangle_M$ to itself and $|1\rangle|0\rangle_M$ to $|1\rangle(\cos\theta|0\rangle_M+\sin\theta|1\rangle_M)$. In an interrogation performed after free evolution, matched temporal modes give

$$
\mathcal V=|\cos\theta|.
\tag{K8}
$$

For $0\leq\theta<\pi/2$, the real positive overlap leaves the fringe phase unchanged while reducing contrast. At $\theta=\pi/2$ the phase is unreadable in the signal marginal. Joint reversal restores the marker overlap if the relevant systems remain accessible; local reset alone does not. A complex overlap adds a phase offset that must be calibrated, and unequal temporal modes add the overlap factor already treated in Part I.

Thus phase evolution, phase readability, and physical record persistence are different parts of one protocol. For $N$ independent Bernoulli trials operated at quadrature with known visibility, the Fisher information for phase is $N\mathcal V^2$ and the local unbiased-estimator bound is $\operatorname{Var}\widehat\phi\geq1/(N\mathcal V^2)$. Contrast loss reduces precision without necessarily changing the recurrence frequency. A clock comparison must report both systematic calibration error and readout uncertainty.
