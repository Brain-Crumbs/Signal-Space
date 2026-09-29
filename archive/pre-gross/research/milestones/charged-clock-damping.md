# Signal Space charged-clock damping milestone

Date: 17 September 2026.

## Result

**The tracked counterrotating oscillation has a weak but nonzero linear radiation channel.** A fixed-initial-charge amplitude scan gives dominant outgoing power proportional to amplitude squared, while the secondary negative-charge radiation channel is fourth order in amplitude. An independent outgoing-boundary calculation identifies the corresponding quasinormal-mode pole:

$$
\boxed{\Omega_{\rm pole}/m=1.72851396-i\,1.43080\times10^{-6}.}
$$

Thus this mode admits approximately exponential decay in the small-amplitude, resonance-dominated regime. It is not a bound linear normal mode whose radiation first appears at nonlinear order. There is no zero-radiation limit with a vanishing quadratic coefficient for this mode at this charge.

This result concerns one identified excitation of the supplied classical field theory. It does not prove exponential relaxation of every disturbance, prove eventual convergence of the original formation remnant, exclude other bound modes or late-time continuum tails, establish a finite-amplitude Floquet spectrum, or exclude exceptional nonradiating states elsewhere in parameter space.

The calculation consists of **15 conservative time evolutions** (14 excited preparations/resolutions and one stationary control), continuum resonance shooting with boundary/tolerance checks, and a separate resonance calculation for the exact discrete time update. All numerical results below were executed for this milestone. The earlier remnant is used for a profile comparison, not silently substituted for the new initial data.

## 1. Unchanged model and reference charge

Use the invariant classical sector $a=a_t=0$ of the previous model:

$$
\Phi_{tt}-\Phi_{xx}+\Phi-2|\Phi|^2\Phi+3|\Phi|^4\Phi=0,
\qquad \lambda=0.01,
$$

in units $m=g=h=1$. Here $h$ in the model parameters denotes the sextic coupling; numerical spatial spacing is written $\Delta x$ below. The energy and charge retain the normalization $1/\lambda$. No friction, absorber, neutral-wave seed, external source, or time-dependent retuning is introduced.

The equilibrium is $\Phi_0=e^{-i\omega t}f_\omega(x)$, with

$$
f_\omega^2(x)=\frac{2(1-\omega^2)}{1+\sqrt{4\omega^2-3}\cosh(2\sqrt{1-\omega^2}\,x)}.
$$

Choose the equilibrium frequency inferred from the previous radiation remnant's mean **core** charge:

$$
\omega_*/m=0.90347438791575,\qquad
Q_*=\frac{2\omega_*}{\lambda}\operatorname{artanh}(2\sqrt{1-\omega_*^2})
=231.832883924705.
$$

This is not the original formation run's larger full-domain charge, and it is not the excited remnant's carrier frequency $0.8999232m$. All new preparations start at the same full-domain charge $Q_*$. Charge is then allowed to move out of the core during conservative evolution.

## 2. Derivation of the coupled outgoing resonance

Write

$$
\Phi=e^{-i\omega_*t}[f+\eta],\qquad
\eta=b\left[u(x)e^{-i\Omega t}+v^*(x)e^{i\Omega^*t}\right].
$$

The conjugation is essential when $\Omega$ is complex: both physical components decay with the same sign of the imaginary part. Linearization gives

$$
\eta_{tt}-2i\omega_*\eta_t-\eta_{xx}
+(1-\omega_*^2-4f^2+9f^4)\eta
+(-2f^2+6f^4)\eta^*=0.
$$

Define

$$
A(x)=1-4f^2+9f^4,\qquad B(x)=-2f^2+6f^4.
$$

The two-channel equations are

$$
\begin{aligned}
u''&=[A-(\omega_*+\Omega)^2]u+Bv,\\
v''&=[A-(\omega_*-\Omega)^2]v+Bu.
\end{aligned}
$$

For this even excitation, impose $u'(0)=v'(0)=0$. Far outside the object impose **outgoing** behavior in the open component and **decay** in the closed component:

$$
u'(R)=ik_+u(R),\qquad v'(R)=-\kappa_-v(R),
$$

$$
k_+=\sqrt{(\omega_*+\Omega)^2-1},\qquad
\kappa_-=\sqrt{1-(\omega_*-\Omega)^2}.
$$

The branches continue the positive real outgoing wavenumber and positive real decay exponent near the real resonance. These are complex-frequency boundary conditions, not a reflecting-box eigenvalue calculation.

Two independent outer solutions are integrated inward using DOP853. The determinant of their center-derivative matrix must vanish. Root finding in $\operatorname{Re}\Omega$ and $\operatorname{Im}\Omega$ yields the pole above. Normalize its profile by $v(0)=1$.

At the linear limit, the two physical signed frequencies are approximately

$$
\sigma_+/m=2.63198835,\qquad \sigma_-/m=-0.82503957.
$$

The first is propagating; the second remains evanescent. They differ slightly from the finite-amplitude remnant's $2.6284m$ and $-0.8286m$, because its carrier and excitation are shifted by nonlinear motion.

### Connection to the previously formed object

The new resonance frequency differs from the earlier measured modulation $1.72847466m$ by only $2.27\times10^{-5}$ relative. More significantly, the complex confined-component profile has normalized overlap **0.999840** with the previously measured $n=-1$ harmonic over $0\le mx\le12$, after fitting one complex normalization. The relative profile residual is **1.79%**.

This identifies a close small-amplitude counterpart of the observed motion. It does not turn the finite-amplitude remnant into an exact linear solution. The new experiments test a family prepared around the equilibrium branch, rather than a rescaling of the complete original formation history.

## 3. Fixed-charge preparation and evolution

For each mesh, solve for the even discrete equilibrium, including the time-splitting correction. If $F_j$ is the kick-position profile, its rotating solution obeys

$$
D_x^2F_j+(\widehat\omega^2-1)F_j+2F_j^3-3F_j^5=0,
\quad \widehat\omega=\frac{2}{\Delta t}\sin\frac{\omega\Delta t}{2},
$$

with integer-time Cauchy data

$$
\Phi_j=\cos(\omega\Delta t/2)F_j,
\qquad \dot\Phi_j=-i\widehat\omega F_j.
$$

The lattice frequency is chosen to give $Q_*$. Solving in the even sector removes the translational zero mode from this preparation solve. The maximum stationary-equation residual is below $10^{-12}$ for the executed meshes.

Add the continuum pole's Cauchy perturbation at amplitude $b_{\rm prep}$, smoothly retaining it for $|mx|\le16$ and tapering it to zero by $|mx|=22$. The background profile solve extends to $|mx|=40$. A quasinormal mode is not a globally square-integrable initial state, so this finite-energy cutoff is part of the preparation, not a later cooling operation. The cutoff generates transients; the analysis begins at $mt=200$ after the main outgoing transient has passed the detectors.

Correct the initial velocity once to impose **exact equal total charge**:

$$
\dot\Phi\longmapsto\dot\Phi-ic\Phi,
\qquad
c=\frac{\lambda(Q_*-Q_{\rm raw})}{2\Delta x\sum_j|\Phi_j|^2}.
$$

This is an initial-data operation only. No charge or energy rescaling occurs during evolution. The correction and finite-amplitude relaxation can excite other small components, which are retained in the analysis rather than assumed absent.

Use the original drift–kick–drift dynamics to $mT=700$. Reflection symmetry allows an equivalent half-domain implementation, with $\Phi_{xx}(0)\approx2(\Phi_1-\Phi_0)/\Delta x^2$. This restricts the experiments to even, zero-momentum excitations; it is not a general perturbation-stability test.

The full equivalent domain is $|mx|\le820$, outside the continuum domain of dependence of the core/detectors during the run. There is no absorbing layer. The spatial regulator has dispersive numerical precursors, so the causal exclusion statement is about the continuum/resolved limit, as in the parent milestones.

Primary amplitudes on $(m\Delta x,m\Delta t)=(0.025,0.005)$ are

$$
b_{\rm prep}=0.0025,0.005,0.01,0.02,0.04,0.09.
$$

A coarse scan includes $0.005,0.01,0.02,0.04,0.06,0.09$, plus the zero-amplitude control. The $0.01$ case is also repeated at $(0.025,0.0025)$ and $(0.0125,0.0025)$.

Record field, velocity and spatial derivative every $0.1/m$ at 11 locations from the center to $60/m$, and energy/charge ledgers every $1/m$. Integrate exact lattice boundary currents through the core boundary using trapezoidal time quadrature. Report outgoing power in both directions.

## 4. Amplitude-scaling result

Fit the complex field over $200\le mt\le700$ to signed harmonics $n=-3,\ldots,3$, allowing quadratic phase drift. Frequencies are estimated with constant coefficients and Hann weighting. Constant-plus-linear complex envelopes are then fitted at those frequencies. The measured amplitude is

$$
b=|A_{-1}(x=0,t_c)|,\qquad mt_c=450.
$$

Using measured $b$ avoids mistaking initial transients and charge correction for the amplitude of the surviving oscillation. Harmonic power is extracted directly from the separately fitted velocity and gradient:

$$
P_n=-\frac4\lambda\operatorname{Re}(V_n^*G_n),\qquad
J_n=\frac4\lambda\operatorname{Im}(A_n^*G_n),
$$

at the right-hand detector $x=20/m$, with the factor accounting for both outward directions.

| Prepared amplitude | Measured confined amplitude | $P_{+1}/m^2$ | $P_{-2}/m^2$ | Harmonic excitation loss / calibrated excess energy, in $m$ |
| -----------------: | --------------------------: | -----------: | -----------: | ----------------------------------------------------------: |
|             0.0025 |                   0.0024919 | 3.825579e-08 | 3.682450e-12 |                                                2.855738e-06 |
|             0.0050 |                   0.0049706 | 1.521564e-07 | 5.826471e-11 |                                                2.855993e-06 |
|             0.0100 |                   0.0098888 | 6.012243e-07 | 9.104062e-10 |                                                2.856930e-06 |
|             0.0200 |                   0.0195682 | 2.338325e-06 | 1.381734e-08 |                                                2.859514e-06 |
|             0.0400 |                   0.0383009 | 8.694302e-06 | 1.943827e-07 |                                                2.853743e-06 |
|             0.0900 |                   0.0815260 | 3.090240e-05 | 2.988397e-06 |                                                2.500866e-06 |

Over the four smallest fine-grid amplitudes:

$$
\boxed{P_{+1}\propto b^{1.9959},\qquad P_{-2}\propto b^{3.9938}.}
$$

These are finite-range logarithmic slopes, not statistical confidence intervals. Slight departures from integers reflect finite-amplitude corrections and numerical resolution. The much smaller $n=+2$ channel also scales approximately as $b^{3.9968}$.

The dominant channel therefore survives in linear perturbation theory: its **field amplitude is first order in $b$**, and its energy flux is second order. The negative-frequency $n=-2$ channel is a nonlinear harmonic: its field amplitude begins at second order and its flux at fourth order. This explains why the earlier remnant could emit appreciable negative charge at finite amplitude without requiring that channel to control the small-amplitude decay.

At the smallest fine-grid amplitude, $P_{+1}/b^2=0.0061610m^2$, close to the independently calculated continuum linear value $0.0061749m^2$. The residual difference follows the measured spatial-regulator convergence.

The quadratic coefficient is nonzero. Although **all power tends to zero as $b\to0$**, the fraction of mode excitation lost per unit time tends to a nonzero constant. These are different statements.

## 5. Damping law and its normalization

For $\Omega=\Omega_R-i\gamma$ with $\gamma>0$, the pole predicts

$$
b(t)\simeq b(0)e^{-\gamma t},\qquad
\Delta E_{\rm mode}(t)\simeq\Delta E_{\rm mode}(0)e^{-2\gamma t}
$$

during the linear resonance-dominated regime. Here

$$
\gamma/m=1.43080\times10^{-6},\qquad
\Gamma_E/m=2\gamma/m=2.86159\times10^{-6}.
$$

The associated scales are

$$
\tau_{\rm amplitude}=6.989\times10^5/m,
\quad
\tau_{\rm energy}=3.495\times10^5/m,
\quad
 t_{1/2,\rm energy}=2.422\times10^5/m.
$$

The energy e-fold is about **50,250 equilibrium carrier cycles**. These are pole-derived local decay scales. The simulations last $700/m$, not one full e-fold, and do not measure an eventual lifetime.

### Energy and charge must be counted together

As in the parent milestone,

$$
\Delta E=E_{\rm core}-M(Q_{\rm core}),\qquad
-\dot{\Delta E}=P-\omega_QJ,
\qquad \frac{dM}{dQ}=\omega_Q.
$$

It would be incorrect to identify radiated energy power $P$ alone with the rate of excess-energy loss.

For completeness, the cycle-averaged quadratic form of $E-\omega_*Q$, on a finite core containing the mode, is

$$
K_2=\lambda^{-1}\int\left[
(|\Omega|^2+A-\omega_*^2)(|u|^2+|v|^2)
+|u'|^2+|v'|^2+2B\operatorname{Re}(uv^*)\right]dx.
$$

For the normalization $v(0)=1$, evaluating over $|mx|\le24$ gives approximately

$$
\Delta E_{\rm mode}\simeq1417.12\,m\,b^2,
\qquad P\simeq0.00617486\,m^2b^2,
$$

$$
P-\omega_*J\simeq0.00405523\,m^2b^2.
$$

Their ratio is $2.86159\times10^{-6}m$, agreeing with $2\gamma$. This is a consistency identity of the linear mode and its boundary flux, rather than an independent time-evolution measurement. A complex outgoing resonance grows at sufficiently large spatial distance; these expressions use the stated finite core and must not be interpreted as a norm over the entire infinite line.

### Direct evolution check

| Prepared amplitude, fine mesh | Harmonic prediction $(P-\omega_QJ)/m^2$ | Measured core excess-energy loss / $m^2$ | Relative difference |
| ----------------------------: | --------------------------------------: | ---------------------------------------: | ------------------: |
|                        0.0025 |                           2.5129007e-08 |                            2.5129560e-08 |             0.0022% |
|                        0.0050 |                           1.0000549e-07 |                            1.0000874e-07 |             0.0033% |
|                        0.0100 |                           3.9607510e-07 |                            3.9610488e-07 |             0.0075% |
|                        0.0200 |                           1.5543069e-06 |                            1.5547114e-06 |             0.0260% |
|                        0.0400 |                           5.9721233e-06 |                            5.9789359e-06 |             0.1139% |
|                        0.0900 |                           2.4327520e-05 |                            2.4553414e-05 |             0.9200% |

Secular energy slopes are fitted with oscillatory nuisance terms at the measured modulation harmonics, preventing small time-splitting oscillations from masquerading as a long-term trend. At the larger amplitudes, direct total flux includes small additional transient or unresolved components. For $b_{\rm prep}=0.09$, the direct total flux predicts $2.45699\times10^{-5}m^2$, versus the measured $2.45534\times10^{-5}m^2$; the narrow harmonic bands alone are short by about 0.92%.

For very small amplitudes, the stationary lattice energy differs from the continuum branch energy by an amount that is small absolutely but relevant relative to $b^2$. The last column of the scan table subtracts the stationary mesh/window offset at the same charge. At the fine mesh and window 20 this correction is approximately $-6.77\times10^{-5}m$. Its charge derivative is also recorded; the charge variation is small enough that the linear correction suffices. The continuum excess and calibrated excess are both supplied in the machine-readable results. This correction changes the energy reference, not the trajectory or the measured power.

## 6. Numerical checks

The continuum pole is unchanged to the quoted precision when the outgoing matching radius is changed from $R=16/m$ to $20/m$ and $24/m$, or the integration tolerance is reduced from $2\times10^{-10}$ to $2\times10^{-12}$. The largest change of the imaginary part across these checks is about $1.1\times10^{-12}m$. This is internal ODE convergence, not uncertainty in the physical applicability of the model.

A separate calculation uses the actual lattice background and exact kick-position recurrence. For each channel replace the temporal frequency by $2\sin(\sigma\Delta t/2)/\Delta t$ and impose the matching discrete outgoing/evanescent root. This directly predicts the pole of each discretized simulation.

| $(m\Delta x,m\Delta t)$ | Discrete pole $\gamma/m$ | Measured envelope decay $\gamma/m$, prepared $b=0.01$ | Dominant power / $m^2$ |
| ----------------------- | -----------------------: | ----------------------------------------------------: | ---------------------: |
| 0.05, 0.01              |          1.419041776e-06 |                                       1.418894854e-06 |          5.9745974e-07 |
| 0.025, 0.005            |          1.427855033e-06 |                                       1.427728021e-06 |          6.0122433e-07 |
| 0.025, 0.0025           |          1.427695520e-06 |                                       1.427568475e-06 |          6.0116920e-07 |
| 0.0125, 0.0025          |          1.430061235e-06 |                                       1.429939226e-06 |          6.0216679e-07 |

The direct envelope decay agrees with the corresponding discrete pole within about 0.011% in this small-amplitude test. The finest pole differs from the continuum width by about 0.052%; the remaining small finite-amplitude frequency/decay shift is separately visible. Halving the time step at fixed $\Delta x=0.025/m$ changes the measured width by about 0.011%.

Half-window tests ($200$–$450$ and $450$–$700$) preserve the small-amplitude harmonic powers and inferred damping. For the smallest fine run the fitted envelope rate changes by less than 0.03% between the full-window result and either half. At the largest amplitude the envelope estimate is more window-sensitive (about 2%), so the report does not promote its fitted rate to a precise nonlinear lifetime.

Full-domain relative charge drift stays below $3\times10^{-14}$. The largest relative energy variation is approximately $5.0\times10^{-6}$ in the most excited coarse run; at fixed fine spacing, halving the time step reduces the small-amplitude energy variation by a factor of four. The finite-step local energy and integrated-flux residuals are retained in the JSON results. These oscillatory residuals are not silently removed from the recorded trajectories.

The zero-amplitude discrete equilibrium has total-energy range $5.9\times10^{-12}m$ and total-charge range $2.6\times10^{-12}$. Its finite-window mean flux at $x=20/m$ is about $3.9\times10^{-12}m^2$, while projection onto the tested dominant radiation harmonic gives below $4\times10^{-25}m^2$. This establishes a negligible narrow-band background for the reported amplitude scan; it is not a claim of exact floating-point zero everywhere.

## 7. Interpretation and remaining boundary

The original qualitative explanation now has a more specific mathematical classification. The long-lived counterrotating motion is closely associated with an **outgoing linear resonance**: one component is confined, but the coupled component can propagate. The conversion is weak enough that thousands of clock cycles can pass with little visible change.

The confinement and cancellation suppress the leakage coefficient strongly, but do not eliminate it at this charge. The secondary nonlinear harmonic becomes relatively less important as the excitation becomes smaller. This selects weak linear resonance damping over a purely higher-order damping law for the tracked oscillation.

At finite amplitude the rate changes. In the largest new fine run the harmonic excitation-loss ratio is about $2.50\times10^{-6}m$, compared with $2.862\times10^{-6}m$ in the linear limit. The earlier formation remnant's ratio, about $2.29\times10^{-6}m$, is of the same scale but belongs to a different, more excited state. One should not replace either finite-amplitude rate by the linear coefficient without a controlled continuation.

Several questions remain open:

1. Other bound modes may decay through nonlinear radiation and eventually dominate a generic perturbation after this resonance has weakened.
2. Continuum threshold tails can invalidate a single-exponential description at arbitrarily late times.
3. A Floquet calculation about the actual finite-amplitude recurrence has not been performed. The present pole is about the stationary branch.
4. The scan fixes the initial charge but does not survey other charges or potentials for exceptional zero-radiation states.
5. The neutral field remains exactly zero in this classical sector. Quantum spontaneous neutral emission, electric-charge identification, and reception-derived field equations remain outside this calculation.

For the Signal Space program, the result strengthens the internally consistent classical-clock benchmark. It still does not derive the chosen potential, coupling law, or spacetime cone from ordered reception. The next targeted extension is to resolve the other bound/continuum components of the actual formation remnant and their amplitude laws, or to calculate its finite-amplitude Floquet continuation if the question is its complete long-time cooling.

## 8. Reproducibility and prior work

The accompanying archive contains Python/C++ source, generated initial-data specifications, all detector histories and conservation ledgers, resonance profiles, extracted harmonic fits, the numerical table, and the prior remnant profile used for comparison. Initial binary states regenerate deterministically from the supplied scripts. Run `OPENBLAS_NUM_THREADS=1 python run_all.py` with NumPy, SciPy, Matplotlib and a C++17 compiler. The report and figure regenerate from numerical outputs.

The coupled two-frequency structure and coexistence of nonlinear normal-mode damping with long-lived quasinormal modes are established Q-ball phenomena; see Ciurla, Dorey, Romańczukiewicz and Shnir, [Perturbations of Q-balls: from spectral structure to radiation pressure](https://arxiv.org/abs/2405.06591). That paper treats the same polynomial-potential family, with different highlighted parameter choices. The earlier breather connection is discussed by Bowcock, Foster and Sutcliffe, [Q-balls, Integrability and Duality](https://arxiv.org/abs/0809.3895). This milestone supplies a calculation at the supplied Signal Space candidate's charge and parameters, not a novelty claim for the resonance mechanism.

![Amplitude scaling, decay rate, convergence and mode comparison](Signal Space_Charged_Clock_Damping_Diagnostics.png)
