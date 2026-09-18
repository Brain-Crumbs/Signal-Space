# Signal Space: an ordered-reception model with a charged bound clock

Date: 17 September 2026.

Status: Proposed next test model, with an exact classical solution and verified initial binding benchmarks. Formation, full stability, quantum clock coherence, and coherent capture have not been demonstrated. This is a reference-geometry field model, not a derivation of spacetime from order.

## 1. The decision

Test a complex nonlinear field whose conserved charge supports a localized rotating configuration, coupled locally to a massless real signal field. Its phase is part of the field that binds the object, rather than an extra clock attached to an unrelated soliton. Use split-complex numbers to organize causal directions and ordinary complex numbers for field phase.

The candidate belongs to the established Q-ball family. The proposed Signal Space work is the joint test of reception, binding, phase readout, recoil, and outgoing records in the explicitly specified coupled model. Q-balls themselves are not a new Signal Space prediction.

This changes the immediate target from an equally spaced four-level oscillator to a charge-supported recurrence. It does not assume that this recurrence already implements the earlier protected-doublet capture map. The latter remains a separate, stricter gate.

## 2. What is assumed

Use a supplied flat 1+1-dimensional background with metric diag(+1,-1), c=hbar=1. Introduce a complex scalar Phi, a real massless scalar a, and the action below. Assume global U(1) symmetry of Phi, a shift symmetry of a, and a positive overall action normalization 1/lambda. These are model inputs. Charge Q is an internal Noether charge, not an identification with electric charge.

We do not derive the dimension, light cone, quantum postulates, action scale, potential, or symmetry from event ordering. Spatial grid points are sampling locations, not material receivers pinned in place. The localized field configuration can translate and recoil.

An event index labels progression along a causal history. It is not identified with proper time. A global numerical update index is a scheduling choice; it is not evidence for universal physical simultaneity.

## 3. Causal coordinates and split-complex representation

Let

$$
u=t+x,\qquad v=t-x,\qquad j^2=1,
\qquad e_\pm=(1\pm j)/2.
$$

Package coordinates as

$$
z=u e_++v e_-=t+jx,
\qquad z\bar z=uv=t^2-x^2.
$$

Future causal increments have du,dv >= 0. Rightward null propagation changes u at fixed v; leftward propagation changes v at fixed u. A timelike composite can advance in both.

Split-complex multiplication alone does not couple the two sectors: e_+ e_-=0. The coupling is supplied by the reception source in the equations below. Increasing relabelings of u and v preserve order but change the metric calibration, so these calibrated coordinates are additional structure.

## 4. Complete classical action

Define s=|Phi|^2 and

$$
S=\frac1\lambda\int dt\,dx\left[
\partial_\mu\Phi^*\partial^\mu\Phi-U(s)
+\frac12 Z(s)\partial_\mu a\partial^\mu a\right],
$$

$$
U(s)=m^2s-gs^2+hs^3,
\qquad Z(s)=1+\epsilon s.
$$

Choose

$$
m>0,\quad g>0,\quad h>0,\quad
0<g^2<4hm^2,\quad \epsilon\ge0,\quad\lambda>0.
$$

In 1+1 dimensions Phi and a can be taken dimensionless; g and h have units of mass squared, and epsilon and lambda are dimensionless. The overall lambda sets the semiclassical action scale without changing classical equations.

The inequality guarantees

$$
U(s)=s\left[h\left(s-\frac{g}{2h}\right)^2
+m^2-\frac{g^2}{4h}\right]\ge0.
$$

The attractive quartic term can favor concentration, the sextic term prevents runaway large amplitude, and charge constrains dispersal. These are independent physical roles; their coefficients remain inputs.

Vacuum: Phi=0 and constant a. Its linear excitations are a complex massive field of mass m and one real massless scalar. The latter is not a photon in 1+1 dimensions.

## 5. Local reception equations

Varying the action gives

$$
\Box\Phi+
\left(m^2-2gs+3hs^2\right)\Phi
-\frac\epsilon2\Phi(\partial a)^2=0,
$$

$$
\partial_\mu[Z(s)\partial^\mu a]=0.
$$

Both fields have the same principal characteristic cone. No instantaneous long-distance force or prescribed bath is used.

For an explicit two-direction reception form, define

$$
D_\pm=\partial_t\pm\partial_x,
\quad R_\pm=D_\pm\Phi,
\quad A_\pm=D_\pm a.
$$

Then

$$
D_-R_+=D_+R_-=F,
\quad F=-U_s\Phi+\frac\epsilon2\Phi A_+A_-.
$$

$$
D_-A_+=D_+A_-=
-\frac{(D_+Z)A_-+(D_-Z)A_+}{2Z}.
$$

Reconstruct the retained local fields through

$$
\partial_t\Phi=(R_++R_-)/2,
\qquad\partial_t a=(A_++A_-)/2,
$$

and preserve the compatibility constraints

$$
\partial_x\Phi=(R_+-R_-)/2,
\qquad\partial_x a=(A_+-A_-)/2.
$$

The field values retain the phase and amplitude needed for subsequent receptions. The sources use only the local state and the incoming characteristic data. Because of the derivative definition, R_- transports rightward when F=0 and R_+ transports leftward; their subscripts label D_±, not propagation direction.

The factor A_+A_- shows why counterpropagating waves can affect the local structural field. A single strictly one-directional free wave has (partial a)^2=0. Scattering in a nonuniform Z can create the other direction; this is not a universal statement that an incident one-sided packet cannot interact.

## 6. Conserved quantities and recoil

The exact continuum energy, momentum, and charge are

$$
E=\frac1\lambda\int dx\left[
|\dot\Phi|^2+|\Phi_x|^2+U(s)
+\frac Z2(\dot a^2+a_x^2)\right],
$$

$$
P=-\frac1\lambda\int dx\left[
2\operatorname{Re}(\dot\Phi^*\Phi_x)+Z\dot a a_x\right],
$$

$$
Q=\frac i\lambda\int dx\left(\Phi^*\dot\Phi-\dot\Phi^*\Phi\right).
$$

All are conserved on the full line for appropriate localized finite-energy data. Energy is nonnegative. Outgoing radiation carries the missing energy and momentum when the localized object relaxes or recoils. Subdomain conservation must include boundary fluxes.

No external center coordinate, confining wall, friction, or recoil correction is appended. The center is extracted from the evolving localized field. For an isolated boosted exact solution its total energy-momentum is (gamma E0, gamma beta E0).

## 7. Exact self-bound rotating solution

Set a=0 and seek

$$
\Phi(t,x)=e^{-i\omega t+i\theta_0}f_\omega(x-X),
\qquad f_\omega>0.
$$

For positive charge choose

$$
\omega_{\min}<\omega<m,
\qquad\omega_{\min}^2=m^2-\frac{g^2}{4h}.
$$

Writing kappa^2=m^2-omega^2, the profile equations are

$$
f''=(m^2-\omega^2)f-2gf^3+3hf^5,
$$

$$
(f')^2=\kappa^2 f^2-gf^4+hf^6.
$$

The exact localized solution is

$$
\boxed{
f_\omega(x)^2=
\frac{2\kappa^2}
{g+\sqrt{g^2-4h\kappa^2}\cosh(2\kappa x)}.
}
$$

No boundary wall holds it together. Its local modulus and stress tensor are stationary, while the complex field rotates. This is a relative equilibrium, not a periodically pulsating energy density.

Let d=sqrt(g^2-4h kappa^2). Direct integration gives

$$
Q(\omega)=\frac{4\omega}{\lambda\sqrt h}
\operatorname{artanh}\sqrt{\frac{g-d}{g+d}},
$$

$$
E(\omega)=\omega Q(\omega)
+\frac2\lambda\int dx\,(f')^2.
$$

For a smooth solution branch, dE/dQ=omega. The rotating field is an exact solution for every epsilon because a=0 makes the classical radiation interaction vanish. This is a classical result, not a proof of a fully dressed quantum spectrum.

## 8. Initial verified benchmarks

Use m=g=h=1 in mass units, lambda=0.01, and epsilon=0.1. Thus omega_min=sqrt(3)/2. The small lambda gives relatively large classical charge, making a semiclassical investigation more appropriate than treating a charge of order unity as a classical soliton.

Define R_Q^2=integral x^2 f^2 dx / integral f^2 dx in the rest frame.

| omega/m | Q | E/m | E/(mQ) | m R_Q |
|---|---:|---:|---:|---:|
| 0.88 | 322.298464 | 302.903104 | 0.939822 | 2.210068 |
| 0.90 | 241.280625 | 230.904369 | 0.956995 | 2.262044 |
| 0.95 | 139.146142 | 136.633021 | 0.981939 | 2.982275 |
| 0.98 | 82.567796 | 82.002915 | 0.993159 | 4.598132 |

These numbers were computed by deterministic quadrature of the displayed exact profile. At omega=0.90, the analytic charge formula agrees with quadrature to floating-point precision and dQ/domega is approximately -2829.0229. The first-integral residual was below 6e-18 on the test grid. Independent second-difference checks of the profile equation gave maximum residuals 8.14e-9 and 2.19e-9 at spacings 0.002 and 0.001.

E<mQ rules out complete dissociation into free charged quanta at tree level. It does not by itself rule out fission, mixed charged/neutral emission, a negative fluctuation mode, or quantum corrections. A negative dQ/domega is a useful branch diagnostic; use the full constrained stability analysis rather than treating this sign alone as a universal proof.

## 9. What makes it a clock, and what does not

Classically its internal phase advances at omega. For a boosted solution

$$
\Phi_\beta(t,x)=
f_\omega\big(\gamma(x-X_0-\beta t)\big)
\exp[-i\omega\gamma(t-\beta(x-X_0))+i\theta_0].
$$

At its center x=X0+beta t,

$$
\frac{d\theta_{\rm center}}{dt}=-\frac\omega\gamma.
$$

This is an exact inertial phase-clock calibration within the supplied Lorentz-invariant theory. It is not an emergent derivation of Lorentz invariance. Accelerated motion requires the full field response; substituting a time-dependent beta into this solution is not an exact accelerated solution.

Absolute U(1) phase is invisible to observables made only from s, the stress tensor, and a. A neutral radiation detector coupled only through Z(s) cannot read this clock phase. A phase reference is therefore required.

Use a second packet or object of the same Phi field. When they meet, the density contains a cross term proportional to cos(theta_A-theta_B). The exact nonlinear collision and its back-action must be evolved. A separated diagnostic such as Phi_A^* Phi_B represents a relational quantity, not an instantaneous local measurement across space. A physical comparison must exchange charged Phi excitations or bring the fields into causal contact.

In the quantum theory, an exact charge-energy eigenstate has no directly observable rotating one-point phase. A clock can use coherence between charge partitions of a larger system with fixed total charge. For example,

$$
\frac{1}{\sqrt2}\left(
|Q\rangle_A|Q_R\rangle_B+
|Q+1\rangle_A|Q_R-1\rangle_B\right)
$$

has relational frequency

$$
\Omega_{\rm rel}=
[E_A(Q+1)-E_A(Q)]
-[E_B(Q_R)-E_B(Q_R-1)].
$$

Here E denotes dressed energies when making quantum claims. Classical continuously variable Q is not silently rounded into an exact quantum spectrum. Integer-charge states and their energies require semiclassical quantization and corrections.

Charge conservation protects a sector. Only an actual lowest-energy state in that sector, below all relevant breakup thresholds, cannot lower its energy by emitting neutral radiation. This does not make superpositions of different charge partitions automatically immune to dephasing or environment records.

## 10. First full calculation: the fluctuation spectrum

Write

$$
\Phi=e^{-i\omega t}(f+u+iv),\qquad a=\alpha.
$$

At linear order around a=0,

$$
u_{tt}+2\omega v_t+L_+u=0,
\qquad v_{tt}-2\omega u_t+L_-v=0,
$$

$$
L_+=-\partial_x^2+m^2-\omega^2-6gf^2+15hf^4,
$$

$$
L_-=-\partial_x^2+m^2-\omega^2-2gf^2+3hf^4.
$$

The neutral channel obeys

$$
Z(f^2)\alpha_{tt}-\partial_x[Z(f^2)\alpha_x]=0.
$$

Solve the coupled quadratic eigenvalue problem for u,v, including the phase and translation zero modes L_- f=0 and L_+ f'=0. Enforce the fixed-Q constraint when diagnosing energetic stability. The neutral sector is linearly decoupled, but interacts at nonlinear order. Its positive weighted wave operator supplies a useful independent stability control.

Required output: localized eigenmodes, continuous-spectrum thresholds, unstable growth rates if present, and convergence under box enlargement and mesh refinement. Compare E(Q) with all accessible partitions E(Q1)+E(Q-Q1) and charged-emission thresholds. Do not call an object stable solely because a short evolution looks quiet.

## 11. Formation and finite-speed reception tests

Use three distinct preparations.

1. Exact-profile control: the stationary or boosted solution, then small generic compact perturbations of Phi and its velocity. Check conserved quantities, zero modes, radiation, and recovery of recurrence.
2. Unbound-data formation: Phi(0,x)=A exp[-x^2/(2w^2)] and dotPhi(0,x)=-i nu Phi(0,x). Its charge is 2 nu A^2 w sqrt(pi)/lambda. Choose A from a target charge, vary w and nu independently of the exact-profile width/frequency, and let the dynamics decide whether a localized state forms. Initial charged density and coherent rotation are declared preparation inputs. This does not establish formation from neutral radiation alone.
3. Reception/recoil: collide the established object with one-sided and two-sided signal packets, and with charged Phi packets of controlled relative phase. Evolve the complete fields without pinning the center.

For a reproducible neutral packet centered at x0, use a(0,x)=B exp[-(x-x0)^2/(2sigma^2)] cos(k(x-x0)); set adot=-a_x for rightward motion and adot=+a_x for leftward motion. Its amplitude B is calibrated by the packet energy, not chosen to imply negligible back-action.

Start with omega=0.90, then repeat at 0.88,0.95,0.98. For the Gaussian preparation use target charges from the table, w/R_Q in {0.5,1,2,4}, and nu/m in {0.8,0.9,1.0}; do not preselect only successful evolutions. For reception use packet energies 0.001,0.01,0.05 times the object rest energy, both symmetric and asymmetric incidence, and record k and sigma in mass units.

No classical a radiation is generated from exactly a=adot=0: its equation is homogeneous. Classical relaxation can emit massive Phi waves. Neutral spontaneous pair emission requires a quantum calculation; a deliberately seeded classical a bath is a different preparation and must be labeled as such. No unspecified vacuum noise is added to manufacture cooling.

A nonzero net Q cannot form from neutral a radiation in a closed system starting at Q=0. Formation of opposite-charge objects with total Q=0 is a separate possible channel requiring its own threshold and dynamics test.

## 12. Neutral emission and records: the next quantum gate

The coupling depends only on s, so a global classical phase shift leaves neutral scattering unchanged. This removes direct classical sensitivity to that absolute phase; it does not prove that different charge or excitation branches have identical outgoing states. Their profiles and energies generally differ.

For a canonically normalized asymptotic neutral field a_c=a/sqrt(lambda), the interaction is

$$
S_{\rm int}=\frac\epsilon2\int d^2x\,
s(x):\partial_\mu a_c\partial^\mu a_c:.
$$

Use its Dyson expansion, not a hand-selected jump operator. At leading Born order a transition |i> to |f> involves the structural form factor

$$
F_{fi}(K)=\int dx\,e^{-iKx}
\langle f|s(0,x)|i\rangle,
\qquad K=k_1+k_2,
$$

multiplied by the derivative contraction k1 dot k2 and external-state normalization factors fixed by the Dyson expression. In a collective-coordinate treatment the center produces exp(-i K X). Include the full shape/charge spectrum and all competing massive-Phi channels.

For asymptotic massless plane waves in 1+1 dimensions,

$$
k_1\cdot k_2=0\quad\hbox{for equal directions},
\qquad k_1\cdot k_2=2|k_1||k_2|
\quad\hbox{for opposite directions}.
$$

As in the previous kink test, this selects opposite directions at leading Born order, not equal energies or K=0. Background distortion is included by using the actual neutral scattering modes when going beyond that order. The static diagonal form factor alone cannot emit an on-shell pair from a stable state with no energy release.

At initial rest and using asymptotic rest energies Mi,Mf, exact kinematic support obeys

$$
M_i=\sqrt{M_f^2+K^2}+|k_1|+|k_2|.
$$

Resolve every final structural state and the emission time, momentum, charge-transfer, and recoil records. The overlap required for coherent transfer is that of the entire discarded state, not merely an overlap of momentum marginals.

For two logical input branches with normalized discarded states R0,R1, calculate mu=<R1|R0>. If there are multiple output channels use the full induced channel or its complementary channel rather than assuming a single pure record. An ideal capture isometry would have

$$
V|B_j\rangle=|D_j\rangle\otimes|R\rangle,
\qquad j=0,1,
$$

with the same R and probability for both j. This model does not assume that such doublets exist. An answer showing stable classical recurrence but failure of this quantum condition is a valid partial result, not a completed capture mechanism.

The quantum action is used as a regulated effective theory. Specify a cutoff, measure m and the interaction coefficients in independent vacuum observables, and include symmetry-allowed counterterms. Quote cutoff-dependent intermediate shifts as such. Do not claim a physical clock splitting from one projected oscillator or a bare tree-level Q-ball mass.

## 13. A concrete regulator and update prescription

For implementation write Phi=(q1+i q2)/sqrt(2), s=(q1^2+q2^2)/2. On a spatial mesh of spacing dx use canonical momenta p_i=qdot_i/lambda and pi_a=Z adot/lambda, with Poisson brackets {q_i,n,p_j,m}=delta_ij delta_nm/dx.

Use the semidiscrete Hamiltonian

$$
H_{dx}=dx\sum_n\left[
\frac\lambda2(p_{1,n}^2+p_{2,n}^2)
+\frac{\lambda\pi_{a,n}^2}{2Z_n}
+\frac1\lambda\left(U(s_n)
+\frac12\sum_{i=1}^2\left(\frac{q_{i,n+1}-q_{i,n}}{dx}\right)^2
+\frac{Z_{n+1/2}}2\left(\frac{a_{n+1}-a_n}{dx}\right)^2\right)\right],
$$

where Z_{n+1/2}=(Z_n+Z_{n+1})/2. All terms are local and energy is bounded below. Split H=A+B+C into the q momentum term, the a momentum term, and the coordinate-only remainder.

- A flow: q_i advances by dt lambda p_i; all momenta and a are fixed.
- B flow: q_i and pi_a are fixed, a advances by dt lambda pi_a/Z, and p_i advances by dt lambda pi_a^2 (partial Z/partial q_i)/(2Z^2).
- C flow: coordinates are fixed and every momentum advances by minus dt/dx times the corresponding coordinate derivative of C. Include derivatives of the edge Z coefficients.

Compose A(dt/2), B(dt/2), C(dt), B(dt/2), A(dt/2). This is an explicit symmetric symplectic second-order integrator. Each subflow preserves global U(1) charge

$$
Q_{dx}=dx\sum_n(q_{2,n}p_{1,n}-q_{1,n}p_{2,n}),
$$

up to arithmetic error. H_dx is conserved by the exact semidiscrete Hamiltonian flow; the split integrator has an energy error that must converge with dt. Continuous translation symmetry and exact continuum momentum are broken by the spatial regulator. Check recoil balance by refinement, not by asserting exact lattice momentum conservation.

Start with dx=0.05/m and dt=0.2 dx, then halve dx and dt. Repeat dt refinement at fixed dx to separate temporal and spatial errors. The local stencil gives a finite numerical dependence per step, but its cone is not an exact Lorentz light cone. The target speed and dispersion must converge to the continuum equations; at finite mesh do not interpret the regulator as fundamental Signal Space microphysics.

Use a domain whose edges cannot contaminate the measurement interval; choose its half-length larger than the initial support scale plus T in c=1 units, with a measured buffer for exponentially small profile tails. For long runs, outgoing boundaries are permissible only with a flux ledger and boundary-reflection controls. Periodic boundaries require stopping before returns. Do not use absorbing layers as an unreported energy sink.

## 14. Required observables and acceptance gates

Track the localized core with a moving window; report sensitivity to the window. Measure charge, energy, and momentum both in the core and outside it. Define the core center from its positive-charge density when appropriate; use energy density when positive/negative charge mixtures make that definition ill-conditioned. Fit phase by projecting onto the translated, boosted profile, and report loss of fit rather than forcing an answer when the core fragments.

| Gate | Calculation | Passing evidence | Failure interpretation |
|---|---|---|---|
| Local dynamics | Principal symbol and regulator refinement | Common continuum cone, positive energy, conserved charge | Candidate or implementation is inconsistent |
| Self-binding | Exact profile, thresholds, constrained spectrum | No growing mode and no energetically favored accessible breakup | Localized ansatz is not a stable object |
| Formation | Gaussian and scattering data | A finite region of initial-data space settles into a localized recurrence with outgoing-energy balance | Exact solution has no demonstrated formation basin |
| Classical clock | Phase fit and causal interference readout | Persistent phase and predicted inertial dilation | Bound lump is not a usable clock under the tested protocol |
| Reception and recoil | Full packet-object scattering | Local transfer with total E,P,Q accounting | Prescribed-center or bath approximations hid a failure |
| Quantum persistence | Dressed spectrum and thresholds | Appropriate stable states and a usable relational coherence time | Charge protection was confused with clock coherence |
| Coherent capture | Full outgoing/complementary channel | Common record and preserved relative phase to stated accuracy | Classical recurrence does not solve quantum capture |
| Emergent geometry | Not addressed by this candidate | No success claim at this stage | Requires a later model beyond the supplied spacetime |

Numerical targets for the initial controlled runs: relative charge drift below 1e-8, total energy-accounting error below 1e-4, and fitted frequency/energy/width agreement within 0.5% between the two finest meshes. Run perturbed objects for at least 100 internal periods initially; extend only after spectral and boundary checks. These are engineering tolerances and finite observation windows, not proofs of eternal stability.

For the quantum test report linewidth/frequency, phase-diffusion time, and full record distinguishability. A convenient target such as visibility loss below 1% over 100 periods must be stated as an application threshold, not an exact theorem. Compare to the same preparation without capture to isolate additional loss caused by capture.

Correlations must be tested with a specified density operator and a specified trace-preserving dephasing/discard operation. Preserve the advertised local marginals, report any changed interaction energy and operation cost, and evolve under the same Hamiltonian. This classical mean-field model alone cannot decide whether states with identical one-site reduced density matrices differ in quantum binding. That is a separate quantum many-body extension, not an effect established by randomizing a classical phase profile.

## 15. Why this is the next model

The kink calculation used adjacent shape-oscillator levels as the clock, so the same interactions could radiate the clock excitation away. Here the recurrence belongs to the phase of the binding field and is associated with an exact conserved charge. It offers a testable mechanism for a persistent classical recurrence without imposing equal oscillator spacings.

The central remaining risk is equally explicit: the neutral channel cannot read absolute phase, and a relational quantum clock may lose coherence through charge-dependent profiles and radiation. Symmetry does not erase these records by itself.

The first major calculation should therefore be the coupled fixed-charge fluctuation and breakup analysis at omega=0.90, followed by the formation and causal readout tests. Only if those succeed should the full emitted-plus-recoil quantum channel be calculated. Do not search for constants or claim a protected capture doublet before those gates pass.

## Sources and continuity

- Supplied Signal_Space_Full_Theory_Research_Architecture-1.md: distinctions among causal order, cone reconstruction, clock calibration, autonomous matter, and emergent geometry.
- Supplied Signal_Space_Part_II.md: the nonstationary count-clock obstruction and the requirement for independently calibrated coherent clocks.
- Signal_Space_Local_Reception_Recoil_Milestone.md and Signal_Space_Kink_Pair_Emission_Milestone.md, inspected in the preceding turn: recoil records, imperfect pair cancellation, and failure of adjacent oscillator levels as a protected clock.
- [Bazeia, Marques, Menezes, Exact solutions, energy and charge of stable Q-balls](https://arxiv.org/abs/1512.04279): established analytic Q-ball constructions in two spacetime dimensions.
- [Bowcock, Foster, Sutcliffe, Q-balls, Integrability and Duality](https://arxiv.org/abs/0809.3895): 1+1-dimensional Q-ball interactions and relative-phase dependence.
- [Surya, The causal set approach to quantum gravity](https://arxiv.org/abs/1903.11544): causal partial order as a distinct structural starting point.

The action, conventions, exact-profile derivation, neutral coupling, numerical benchmarks, and test sequence above define this candidate explicitly. Literature context does not substitute for verifying the coupled candidate.
