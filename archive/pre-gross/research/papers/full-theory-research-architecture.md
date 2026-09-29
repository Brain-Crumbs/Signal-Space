# Signal Space: A fresh architecture for a full physical theory

Date: 11 September 2026.

Status: Proposed research program, mathematical alternatives, and completion criteria. This document supersedes the previous metric-first memo as a statement of the intended research scope. It does not assert a completed theory, a new derivation of quantum mechanics or gravity, or an established mass-gap result. No new numerical experiments are reported.

## 1. The objective

Construct one theory of composable signal interactions and histories whose accessible limits account for:

- Quantum probabilities, interference, entanglement, measurement records, and classical behavior.
- Operational time, rapidity, local Lorentz symmetry, and a dynamical 3+1-dimensional spacetime.
- Einstein gravity in its experimentally established regime, with a controlled description of corrections.
- Stable matter and appropriate sector-specific mass gaps, alongside massless radiation.
- Gauge interactions and ultimately the observed chiral matter content.
- Relationships among dimensionless physical constants and a common interpretation of physical scales.

The goal is not to make one suggestive identity carry these conclusions. It is to discover a small set of compositional and dynamical principles that constrains all of them. “Elegant” will mean few independent assumptions, reusable mathematical structure, explicit limits, and more independent consequences than adjustable inputs.

Do not constrain the research to three papers. Write manuscripts around completed bridges between these requirements.

## 2. Recommended foundation and alternatives

My recommended working architecture is **a quantum theory of causal signal histories, with an operational reconstruction of clocks and geometry, and a shared coarse-graining calculation for gravity and matter**. The word quantum describes an obligation to justify the composition law, not a result already established by reception statistics.

| Candidate foundation                                                   | Best use                                                                           | What it contributes                                                                                   | Main unresolved cost                                                                                                                                 | Recommendation                                                                        |
| ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Classical histories with maximum caliber or relative-entropy inference | Classical limit and falsification control                                          | Delays, noise, memory, transport and nonequilibrium response                                          | A positive local hidden-history model does not supply quantum composition or Bell correlations under the usual independence and locality assumptions | Keep as an essential control; do not treat more hidden memory as a quantum completion |
| Operational reconstruction plus quantum causal histories               | Primary constructive route                                                         | Derive or explicitly postulate a quantum composition rule, then implement causal exchange and records | Must justify the quantum-selecting assumptions; dynamical geometry and continuum physics remain to be derived                                        | Preferred working route                                                               |
| Euclidean statistical histories with reflection positivity             | Alternative if a statistical ensemble is the natural microscopic object            | A principled route from suitable correlations to a Hilbert space, Hamiltonian, and spectral analysis  | Reflection positivity alone is insufficient; additional reconstruction assumptions, continuation and a continuum limit are required                  | Strong alternative, especially for spectral gaps                                      |
| Observable algebras and modular flow                                   | Bridge joining quantum information, state-dependent time and local boost structure | A common operator language for state logarithms, relative entropy and symmetry                        | Generic modular flow is not local geometric time; obtaining a spacetime interpretation is difficult                                                  | Investigate after a concrete local model exists                                       |

Operational reconstructions demonstrate that quantum structure can follow from substantive information-processing assumptions. They do not show that ordinary probability or reception finiteness suffices. Compare [Chiribella, D'Ariano and Perinotti](https://arxiv.org/abs/1011.6451) and [Hardy](https://arxiv.org/abs/quant-ph/0101012). [Markopoulou's quantum causal histories](https://arxiv.org/abs/hep-th/9904009) supplies a related framework with quantum structure already specified. [Sorkin's quantum measure approach](https://arxiv.org/abs/gr-qc/9401003) is a histories-based alternative; its generalized measure class should not be mistaken for a unique reconstruction of ordinary quantum theory. For the Euclidean branch, see [Jorgensen and Tian on reflection positivity](https://arxiv.org/abs/1705.05262).

These are alternative routes and benchmarks, not independent mechanisms to attach to different sectors without proving that they describe the same model.

## 3. Minimal primitives: avoid assuming what must emerge

Start with local operations, communication channels, retained internal state, and records of outcomes. Histories encode the composition of these operations and the causal relations between them. Use protocol-labelled probabilities to define what observers can compare.

An elementary signal is initially a carrier of a permitted state or influence, not an assumed photon. A clock is eventually a repeatable subsystem and readout, not an externally supplied proper-time parameter. A channel label is initially a relational distinction, not a point on an assumed celestial sphere. A delay is initially a relation between local sequences or recurrence readings, not a number of seconds in a background chart.

Candidate principles to examine, with every independent assumption listed:

1. **Composability:** compatible local operations compose sequentially and in parallel with consistent probabilities.
2. **Operational equivalence:** identify histories only when all allowed future protocols give the same record law.
3. **Causal consistency:** local choices cannot signal to causally inaccessible records. Reordering independent operations must not change predictions. This is operational causality, not Bell factorization of hidden variables.
4. **Closed-system accounting:** effective forgetting or dissipation has a specified larger realization, rather than erasing physical memory without consequences.
5. **Relabelling independence:** graph names and arbitrary calculation schedules are not physical observables.
6. **Controlled resolution:** bounded protocols have finite readable outputs; stronger claims about finite microscopic state dimension must be separately justified.
7. **Coarse-graining consistency:** refinement and marginalization agree on common accessible predictions within specified approximation errors.

These principles do not yet select a unique dynamics or quantum theory. Add and justify the necessary quantum-selecting and dynamical principles explicitly. Permit causal relations or connectivity to vary in the full model; a fixed graph is an initial regulator or benchmark, not automatically dynamical spacetime.

## 4. Step 1 — Establish the composition of histories and the quantum/classical boundary

**Question:** What makes two alternatives coherently recombinable, and what makes an event a persistent classical record?

Preferred approach: formulate preparations, transformations, measurements, and composition operationally. Assess whether purification and the accompanying reconstruction assumptions follow naturally from a closed signal system, or whether another axiom set is cleaner. Reversible dilation alone is not enough to select quantum theory.

After a quantum representation is justified, a finite regulated benchmark can use history operators $C_H$ and an initial state $\rho$:

$$
D(H,H')=\operatorname{Tr}(C_H\rho C_{H'}^\dagger).
$$

Off-diagonal terms describe interference between alternatives. For a set of histories $A$, the formal weight is

$$
\mu(A)=\sum_{H,H'\in A}D(H,H').
$$

Ordinary additive probabilities apply to appropriately decoherent record alternatives. The formula uses quantum operators and the trace rule; it is a test implementation, not a derivation of those ingredients. Actual detector instruments and their environments must define observable records. A normalized, positive histories functional alone does not establish locality, unique dynamics, or all of standard QM.

**Deliverable:** either an operational reconstruction with its assumptions proved for the proposed system, or an honest minimal quantum postulate plus a precise plan to explain it. In both cases derive the classical history limit.

**Tests:** coherent recombination; controlled loss and recovery of interference; a joint-state Bell/CHSH test with independently chosen settings and no signalling; sequential measurement probabilities; classical memory controls. Noncommuting classical updates and discarded records do not by themselves pass these tests. Decoherence explains suppression of interference in records; specify how probabilities and outcomes are interpreted rather than claiming it resolves every measurement question.

**Alternative:** build an ensemble of Euclidean histories with the required positivity, symmetry and regularity properties, then reconstruct quantum evolution. Explain why those extra structures are selected by the signal law. Do not simply substitute $\hbar$ for a classical noise parameter.

## 5. Step 2 — Extend the logarithmic rate structure through a Lorentz cone

The most economical algebraic extension of the earlier two-rate result uses positive Hermitian $2\times2$ matrices. For the diagonal model define

$$
X=\begin{pmatrix}r_-&0\\0&r_+\end{pmatrix}
=\gamma e^{h\sigma_3},
\qquad \gamma=\sqrt{r_+r_-}.
$$

For any positive-definite Hermitian matrix,

$$
X=x^0I+\mathbf x\cdot\boldsymbol\sigma,
\qquad
\det X=(x^0)^2-|\mathbf x|^2>0,
\qquad x^0>0.
$$

It admits the representation

$$
X=\gamma\exp(h\,\mathbf n\cdot\boldsymbol\sigma)
=\gamma[\cosh h\,I+\sinh h\,\mathbf n\cdot\boldsymbol\sigma],
$$

with $h\ge0$ and $\mathbf n$ arbitrary at $h=0$. Signed one-dimensional rapidity is recovered by fixing the axis. Consequently,

$$
\gamma=\sqrt{\det X},\qquad
\frac{\mathbf x}{x^0}=\tanh h\,\mathbf n.
$$

The congruence action

$$
X\mapsto AXA^\dagger,\qquad A\in SL(2,\mathbb C),
$$

preserves the determinant and realizes the proper orthochronous Lorentz action, with the familiar double cover. This is standard algebra, used here as a candidate extension, not a novelty claim or proof of physical spacetime.

This is cleaner than assuming that arbitrary angular moments transform as a four-vector. It also contains the split-complex diagonal sector, while allowing noncommuting spatial orientations. Rank-one positive matrices lie on the null boundary.

**Required bridge:** derive what operational signal comparison produces $X$; why two complex components are selected; why the relevant observer comparisons act by the stated congruence; and how matrix components become intervals, currents, or another physical quantity. Those interpretations are distinct.

Normalizing $X$ gives a density matrix, but that normalization removes its independent scale. A nonunitary $SL(2,\mathbb C)$ congruence is not an arbitrary deterministic quantum channel on normalized density matrices. Do not identify a Lorentz boost with a physically performed filter without a separate argument. Nor is a pure qubit automatically a photon.

**Deliverable:** a representation theorem or a precisely stated ansatz, plus operational tests separating physical source anisotropy from relative motion. The algebra provides a local 3+1 cone; it does not yet prove three extended spatial dimensions or a manifold.

**Alternative:** derive a covariant angular reception measure including aberration, frequency, detector response and exposure, or pursue spacetime reconstruction from local observable algebras. Use those if the two-component interpretation cannot be physically justified.

## 6. Step 3 — Derive clocks, delay geometry and universal calibration

Recover rapidity from independent exchange protocols, then compare it with the statistical coordinate of Step 2. Use echo maps with explicit response latency and probe back-action. Construct recurrent composite readouts or coherent transition clocks within the same dynamics.

The earlier Paper III's stationary count identity and nonstationary discrepancy are benchmark constraints. They do not require all successors to use reversal count as their time readout. A potentially cleaner choice is a stable phase or transition frequency whose environmental corrections can be calculated. Once a physical Hamiltonian and action scale exist, energy differences govern transition phases; this relation must not be assumed to derive its own normalization.

Seek a shared coframe $e^a{}_{\mu}$ with

$$
g_{\mu\nu}=\eta_{ab}e^a{}_{\mu}e^b{}_{\nu},
\qquad \eta=\operatorname{diag}(-1,1,1,1).
$$

Null exchange constrains the cone. Independent clock calibration or a justified physical volume measure fixes additional scale. Raw reception counts depend on sources and detectors and cannot automatically be used as spacetime volume. The causal-order/conformal-geometry connection has assumptions on the continuum structure; arbitrary causal graphs need not be manifold-like. See [Surya](https://arxiv.org/abs/1903.11544).

**Deliverable:** common geometry inferred by independent clock types and probes, unique up to declared gauge freedom in a stated regime, with calibrated uncertainty. Fix calibration on separate records, then predict unseen histories. Compute finite-size and acceleration-dependent clock errors rather than requiring every device to be ideal.

**Failure branch:** if raw count clocks fail, test coherent phase or composite transition clocks before adding an observer-dependent correction. If different physical modes retain different cones at leading order, the candidate has not recovered universal spacetime.

## 7. Step 4 — Select an autonomous vacuum and a 3+1 continuum phase

Remove supplied propagation distances and let one local law determine histories and, where necessary, connectivity. Choose a tractable regulated model with an explicit family of update parameters or a dimensionless action. Maintain the same choice through the subsequent calculations.

Derive or determine:

- A stable stationary vacuum or appropriate covariant state, and how boundary conditions select it.
- Effective dimension from more than one diagnostic: causal/volume scaling and the propagation spectrum, for example. A spectral-dimension plot alone does not establish Einstein spacetime.
- Long-wavelength locality and Lorentz symmetry, including suppression of measurable regulator anisotropy.
- Common characteristic cones for the relevant modes.
- How refinement or blocking changes couplings, and whether there is a controlled continuum limit or a finite-cutoff effective regime.
- Consistent observables under different admissible update schedules and choices of relational clock.

A physical matter state may define a rest frame; the requirement is covariant laws and appropriate vacuum behavior, not isotropy of every environment. A regular microscopic lattice generally requires a demonstrated emergent symmetry limit. A causal partial order does not by itself solve locality or Lorentz invariance.

**Deliverable:** one reproducible model with an identified geometric regime. Reconstruction of geometry planted into a simulator is a necessary control, not evidence that this step succeeded.

**Alternative:** fixed causal complexes or Lorentzian triangulations can be useful regulators if derived comparably. They are not evidence for dimension selection when that dimension is built into the regulator. A fixed-network quantum information model may remain a valuable analogue if geometry never becomes autonomous, but should then be classified accordingly.

## 8. Step 5 — Derive physical dynamics, energy and gravitational response

First establish the closed evolution law, stable energy spectrum in a suitable stationary regime, and physical conserved currents. In a generally covariant theory there need not be a global energy for every spacetime; use local balance and appropriate asymptotic charges where applicable. Signal recoil, internal excitation and all retained memory must enter the same accounting.

Distinguish local frame choice from transport. A pure frame change $G_{ij}=L_jL_i^{-1}$ telescopes around comparison loops. Thomas–Wigner rotation can occur in flat spacetime. Gravitational curvature requires the physical connection, its relation to the coframe, and a small spacetime-loop limit. Test torsion and nonmetricity; derive their absence, suppression or physical role rather than silently selecting Levi-Civita transport. Compare final clock rates after different paths with controlled final internal preparation to distinguish dynamical excitation from intrinsic history-dependent calibration.

For Einstein gravity, pursue two calculations in the same model:

**Dynamical route:** integrate out short-scale variables and derive the long-distance action. In units $c=\hbar=1$ after normalization is justified, a target is

$$
S_{\rm eff}=\int d^4x\sqrt{-g}\left[
\frac{M_P^2}{2}R-\rho_\Lambda
-\sum_a\frac{Z_a}{4}F^a_{\mu\nu}F_a^{\mu\nu}
+\mathcal L_{\rm matter}+\sum_i c_i\mathcal O_i\right].
$$

Listing this symmetry-allowed action is not deriving its coefficients, spectrum or dominant terms. Obtain the constraint structure and healthy two-polarization gravitational sector, universal coupling, nonlinear field equations and controlled corrections. Test the weak field, redshift, light bending, gravitational radiation and representative nonlinear solutions. Track unwanted scalar/vector modes and the vacuum term.

**Information route:** test whether the same state's local entanglement variations reproduce the same geometric response. Entanglement-equilibrium derivations provide a model for this connection but assume substantial local quantum-field and geometric structure; [Jacobson's result](https://arxiv.org/abs/1505.04753) is restricted to first-order vacuum variations with further conditions, especially for nonconformal matter. It is not a full microscopic derivation of gravity.

**Deliverable:** dynamical and information calculations agree on a common gravitational coupling wherever both apply. An entropy argument cannot substitute for nonlinear dynamics. Audit the actual assumptions of emergent-gravity constraints such as those discussed by [Jenkins](https://arxiv.org/abs/0904.0453); discreteness alone does not evade them.

## 9. The most promising thermodynamic bridge: quantum relative entropy and modular structure

For a faithful finite-region reference state $\rho_0$, define

$$
K_0=-\ln\rho_0,
\qquad s(\rho)=-\operatorname{Tr}(\rho\ln\rho),
$$

$$
D(\rho\Vert\rho_0)
=\Delta\langle K_0\rangle-\Delta s\ge0.
$$

For a small normalized perturbation about the reference state, the first variation obeys $\delta s=\delta\langle K_0\rangle$. Here $K_0$ and $s$ are dimensionless. Physical entropy is $k_Bs$. Continuum local algebras require the appropriate algebraic definitions rather than an assumed finite density matrix.

This gives a more substantial use of logarithmic statistical structure than identifying rapidity with dissipated entropy. Modular flow connects an algebra and a state; in special relativistic quantum-field settings it has a geometric interpretation. The [thermal-time proposal of Connes and Rovelli](https://arxiv.org/abs/gr-qc/9406019) is a related hypothesis. [Casini](https://arxiv.org/abs/0804.2182) supplies a precise relative-entropy connection to entropy bounds.

For a faithful Gibbs state only,

$$
\rho=Z^{-1}e^{-H/(k_BT)}
\quad\Rightarrow\quad
-\ln\rho=\frac{H}{k_BT}+\ln Z.
$$

This relation does not identify every modular generator with energy, every modular parameter with proper time, or vacuum entanglement with ordinary thermal noise. The zero-temperature vacuum is not a classical frozen state.

**High-value Signal Space conjecture:** the logarithmic comparison structure of signal states admits a continuum limit in which suitable local modular flows agree with the boost/clock geometry inferred from exchanges. Test it first on known quantum-field benchmarks, then on the actual event model. If it fails, retain relative entropy for distinguishability and thermodynamics; the broader theory need not depend on thermal time being fundamental.

## 10. Step 6 — Derive matter and gauge sectors from the same dynamics

Study excitations of the selected vacuum before assigning particle names to topology. Find invariant sectors, conserved charges, and physical correlation functions. Local basis freedom can organize a gauge description but does not automatically create a propagating force.

Derive independent gauge variables, their kinetic terms, source currents, constraints, and forces. Distinguish internal gauge connections from the spacetime spin connection. Recover the two transverse photon modes in a massless electromagnetic regime. To pursue a universal theory, explain the observed gauge structure and chiral fermions, anomaly cancellation, symmetry breaking, flavor structure and mixing. A gravity-plus-U(1) construction alone leaves those requirements open.

For matter, test ordinary collective excitations, bound states, solitons and topological sectors as alternatives. Use the least additional structure that yields the needed spin, statistics, stability and interactions. An $SU(2)$ sign or $4\pi$ recurrence is not by itself fermionic exchange statistics. Handedness and charge conjugation must be distinguished; antimatter is not generically intrinsically short-lived, and neither Majorana character nor neutrino flavor mixing follows just from an inverted-clock picture.

**Deliverable:** operationally distinguishable excitations with calculated quantum numbers, dispersion and interactions. A proposed topology earns a physical interpretation only through these predictions.

## 11. Step 7 — Establish sector-specific mass gaps and generated scales

A theory with massless radiation should not be required to have a strictly positive gap above the vacuum in its entire infinite-volume spectrum. State the sector and background for every gap claim. A positive rest mass, a stable classical lump, a metastable barrier, and a quantum mass gap are different achievements. Soft massless quanta also complicate charged-particle spectral statements.

For a chosen isolated gapped theory or well-defined sector, target

$$
\operatorname{spec}(H)\subseteq\{E_0\}\cup[E_0+\Delta,\infty),
\qquad\Delta>0.
$$

Ground-state degeneracy and superselection sectors require the corresponding formulation. In a suitable Euclidean reconstruction with a positive transfer operator $T$, a finite regulator can yield

$$
\Delta(a,L)=-\frac{\hbar}{\delta\tau_E}
\ln\frac{t_1}{t_0},
$$

where $t_0,t_1$ are the relevant leading eigenvalues and $\delta\tau_E$ is independently calibrated. This finite-regulator result is only a first step. Establish the physical Hilbert space, infinite-volume behavior, cutoff/refinement control and a nonzero physical gap. Connected correlation decay must be checked in enough physical channels; an operator can miss lower states by symmetry or overlap. A small Markov mixing eigenvalue is not automatically a Hamiltonian mass gap.

**Preferred mechanism to investigate:** a non-Abelian quantum sector with a dynamically generated scale. With the explicitly chosen leading beta-function convention

$$
\mu\frac{dg}{d\mu}=-b_0g^3+\cdots,\quad b_0>0,
$$

the leading running suggests an energy scale

$$
\Lambda_{\rm dyn}\simeq\mu
\exp\left[-\frac{1}{2b_0g^2(\mu)}\right].
$$

This explains how dimensionless dynamics can generate a hierarchy, but it neither proves a gap nor fixes the scale without a boundary condition or selection rule. The gap calculation is nonperturbative.

**Alternatives:** a protected spectral gap in a microscopic model as a controlled toy construction; symmetry breaking for appropriate matter/vector masses; soliton quantization when genuine topology is derived. None alone solves the four-dimensional pure Yang–Mills existence and mass-gap problem. That problem remains listed as unsolved by the [Clay Mathematics Institute](https://www.claymath.org/millennium/yang-mills-the-maths-gap/).

## 12. Step 8 — Predict constants by matching sectors and reducing free parameters

Start the input ledger at Step 1. It includes the local state dimension, update law, continuous couplings, regularization, boundary/state choices and every calibration convention. Discrete choices also count as explanatory inputs.

Prioritize

$$
\alpha(\mu),\quad\frac{m_i}{m_j},\quad
\frac{Gm_*^2}{\hbar c},\quad
\Lambda_{\rm cosm}\ell_*^2,
$$

plus mixing angles, phases and ratios of limiting speeds. Separate the cosmological constant $\Lambda_{\rm cosm}$ from the generated energy scale $\Lambda_{\rm dyn}$.

Physical scales still need explanation, even though their numerical SI values depend on units. Predict the same action normalization across sectors, shared propagation speed, and dimensionless ratios. Do not determine $\hbar$ by defining a tick to have a chosen energy.

Two particularly useful consistency targets are the equilibrium acceleration-temperature relation and the leading gravitational entropy coefficient:

$$
\frac{k_BT}{\hbar a/c}=\frac{1}{2\pi},
\qquad
\frac{S_{\rm grav}}{k_BA}=\frac{c^3}{4G\hbar}.
$$

These apply under the relevant relativistic vacuum/detector and semiclassical Einstein-gravity assumptions; they are not general formulas for every noisy clock or quantum geometry. Recovering them from one microscopic law would test common normalization. It would not alone predict the absolute values of the constants.

For example, if the microscopic calculation gives a universal leading entropy density $s_A=S_{\rm grav}/(k_BA)$ and the Einstein regime is established, then

$$
G=\frac{c^3}{4\hbar s_A}.
$$

This becomes a prediction only if $s_A$ is independently calculated rather than supplied, with species, regulator and renormalization effects treated consistently. Compare it with $G$ inferred from the action and force law.

The main parameter-reduction candidates are continuum fixed points, symmetry, anomaly consistency and discrete sector selection. Universality does not automatically fix all relevant couplings; demonstrate which freedoms remain. Fit a declared subset of observables, then predict held-out quantities with uncertainty and scale conventions. Simple identities and post-hoc numerical matches do not count.

## 13. Step 9 — Demonstrate that all limits coexist

The full theory needs one region of microscopic parameter/state space supporting the claimed phenomena simultaneously. Separate toy models are not sufficient.

Check quantum probability and positive-energy consistency, approximate local causality and Lorentz symmetry, universal gravity, physical gauge sectors, massive and massless excitations, and the same calibration of action and time. Include cosmological vacuum response, representative black-hole/horizon regimes and the quantum treatment of geometry where the classical approximation fails. Einstein gravity is the required classical limit, not necessarily an exact description at every scale.

Compare the actual predicted corrections with measurements only after specifying the regime and fitted inputs. Relevant classes include composition-dependent acceleration, clock comparisons, polarization-dependent propagation, force laws, scattering, mass ratios and cosmological observables. A theory must also explain or model known dark-sector phenomena; reproducing the Einstein equations alone does not settle cosmology.

**Deliverable:** a reproducible shared parameter fit and independent predictions, with a clear separation of established theorems, controlled approximations, numerical evidence and conjectures. A rigorous mathematical existence claim needs stronger evidence than numerical convergence.

## 14. Review points and cleaner alternatives

| Earlier pressure point                                | Cleaner primary direction                                                    | Alternative if it fails                                                                                           |
| ----------------------------------------------------- | ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Hidden histories or anti-aliasing as QM               | Operational quantum reconstruction and coherent history composition          | Reflection-positive Euclidean histories; explicitly declared quantum input for a narrower emergent-gravity theory |
| Incoming rate imbalance identified with velocity      | Derive a residence-response law and covariant operational state              | Infer relative motion through independent echo and spectral protocols                                             |
| Stationary reversal count identified with proper time | Stable composite phase/transition clocks with calculated response            | A controlled adiabatic statistical clock with explicit error bounds                                               |
| Arbitrary angular moments treated as a Lorentz vector | Positive Hermitian cone with a justified operational interpretation          | Full covariant angular transport law or observable-algebra reconstruction                                         |
| Fisher information used as spacetime metric           | Causal cone plus universal calibration; Fisher for inference precision       | Quantum relative entropy as a dynamical consistency tool                                                          |
| Bare log rate ratio treated as entropy production     | Complete forward/reverse process with physical heat and state changes        | Equilibrium quantum relative entropy and modular comparisons                                                      |
| Local recurrence slowing identified with gravity      | Shared coframe and universal matter/signal response                          | Treat the effect as a scalar environmental field and test whether it decouples                                    |
| Loop memory identified with curvature                 | Derive a physical connection and its spacetime-loop limit                    | Retain memory as internal dynamics or a gauge sector                                                              |
| Toroidal collapse resistance used to infer a mass gap | Quantum spectrum and nonperturbative scale generation                        | Stable soliton plus quantization as a specific matter model                                                       |
| Classical causal pressure used as vacuum binding      | Ground-state energy, entanglement and quantum effective dynamics             | Explicit finite-temperature free energy as a correction                                                           |
| Spinorial sign identified with fermions               | Representation, observable relative phase and exchange-statistics derivation | Treat it as a classical frame lift until the quantum tests succeed                                                |
| Constants inferred from topology or unit choices      | Calculated response coefficients, running and held-out ratios                | Publish a precise relation after a stated calibration                                                             |

## 15. Immediate work: four bounded deliverables

**A. A short foundations specification.** Define local operations, observable histories, composition, retained memory, gauge equivalence and the input ledger. Compare the operational and Euclidean routes on explicit criteria. Select one working dynamics rather than writing a universal action by inspection.

**B. A two-channel coherent reception model and classical control.** Use a declared quantum benchmark to test interference, reversible recording and entanglement. Include finite delays and memory in both versions. Quantum behavior built into the benchmark is a consistency check, not a derived result. In parallel in the research schedule, justify the chosen composition axioms.

**C. The positive-matrix and clock-calibration calculation.** Derive the diagonal reduction, full cone action and observable interpretation. Compare statistical and echo-inferred rapidities. Test a phase clock against the known nonstationary count-clock discrepancy using independently fixed calibration.

**D. A shared-model feasibility study.** Identify a candidate vacuum, spectrum, propagation cone and parameter flow in a small regulated model. Determine whether the same law can plausibly support geometric and massive sectors. Stop extending that candidate if it requires unrelated laws or independent tuning for every desired effect.

These establish whether the proposed mathematical economy is real before committing to a long particle taxonomy or a claimed Einstein derivation.

## 16. Publication plan

Use provisional work titles: _Composition of Signal Histories_; _Signal States, Lorentz Cones and Operational Clocks_; _Autonomous Geometric Phases_; _Quantum Information and Einstein Dynamics_; _Gauge Sectors and Massive Excitations_; _Coupling Relations and Empirical Tests_. Split or combine them according to actual completed results.

The earlier Paper III remains a source of conditional transport results, calibration obstructions and predictive-memory controls. Preserve those results without making its two-state bath or fixed relays mandatory microscopic constituents. The organizing commitment is now to one compositional theory and its common physical limits.
