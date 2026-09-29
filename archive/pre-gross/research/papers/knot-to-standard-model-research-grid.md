# Signal Space: knot topology to Standard Model — hypothesis, correspondence grid, and derivation gates

Date: 17 September 2026.

Revision: incorporates the whole-hadron interpretation of quarks and the proposed baryon winding description. These are research hypotheses and derivation targets, not new numerical results.

Status: research assessment, not a derivation of the Standard Model. Based on the supplied Signal Space 3+1D action and earlier 1+1D milestones. No new simulation or particle spectrum is reported.

## 1. The hypothesis worth testing

The proposal is that persistent knotted or twisted reception structures support internal states, and that the allowed local transformations and interactions of those states generate the symmetries and particles of the Standard Model.

The clarified working hypothesis is: **a baryon is a unit-winding recurrence; its effective quark content describes quantized internal states and localized responses of that complete recurrence.** Quarks need not be separately existing, individually knotted objects. The complete hadronic structure is the proposed physical object. Whether winding actually enforces its effective quark requirements and dynamics remains to be calculated.

This is a stronger, testable formulation of the proposed associations “unknot -> U(1), trefoil -> SU(3), weak interaction -> untying.” The associations themselves are not mathematical consequences of knot type. The required chain is:

1. Specify physical fiber variables and local dynamics.
2. Obtain finite-energy configurations and their quantum states.
3. Derive transformation operators on those states.
4. Establish the local gauge constraints and dynamical gauge fields.
5. Recover chiral matter representations, interactions, and measured phenomenology.

Topology may constrain the first three steps. It does not automatically complete steps four and five. A correspondence between diagrams and particle names is a classification proposal; it becomes a physical theory only with amplitudes, conserved currents, dynamics, and falsifiable observables.

## 2. What the current Signal Space model actually contains

The supplied 3D model contains a complex scalar Phi with an assumed global U(1), a real neutral scalar a, and an optional unit orientation field n. The Hopf extension has an independently supplied stiffness, four-derivative stabilization, and density-dependent coupling K(|Phi|^2).

Established in the supplied work: selected 1+1D classical charged formation, phase-sensitive two-object interactions, and weak outgoing structural radiation. Specified but not established by the supplied results: stable 3D charged configurations, charged-Hopf binding, quantum soliton spectra, emergent gauge fields, and Standard Model particles. Results from a separate ongoing calculation must be read before updating this status.

The current phase charge Q is not electric charge. The neutral a wave is spin zero under ordinary quantization, not a photon. Small orientation waves are also scalar modes. The n field has internal rotations, but an internal rotation symmetry is not yet a local electroweak gauge symmetry. A normalized doublet representation of n does not by itself supply a dynamical gauge boson or weak doublet of fermions.

## 3. Examine the proposed knot-to-group assignments

### 3.1 Unknot and U(1)

The complement of an unknot has fundamental group Z. A unitary one-dimensional representation assigns its generator a phase:

$$
\rho(1)=e^{i\theta},\qquad \rho(n)=e^{in\theta},\qquad
\operatorname{Hom}(\mathbb Z,U(1))\simeq U(1).
$$

That is a genuine mathematical bridge from winding to phase. It is not Maxwell theory. Moreover every ordinary single-knot complement has abelianization Z, so such Abelian phase representations are not unique to the unknot. U(1) has been selected as the representation target in this construction, rather than uniquely derived from the topology.

To obtain electromagnetism, derive a local connection, its propagating transverse modes, a Maxwell kinetic term, conserved electric current, and charge assignments. The current derivative-coupled scalar a does not satisfy these requirements; it is not even classically sourced from an exactly empty a sector by a charged core.

### 3.2 Trefoil and SU(3)

The usual trefoil notation is 3_1; it is also the (2,3) torus knot. Its complement group admits presentations

$$
\pi_1(S^3\setminus3_1)
=\langle a,b\mid aba=bab\rangle
\simeq\langle x,y\mid x^2=y^3\rangle.
$$

This discrete group is not SU(3), a continuous Lie group of dimension eight. Knot-group representations into different target groups can be studied; the knot does not uniquely choose SU(3). See the explicit study of trefoil representations into other groups by [Hilden, Lozano, and Montesinos-Amilibia](https://arxiv.org/abs/1003.3554).

Three crossings, three lobes, three-color knot diagrams, and three quantum color components are distinct notions. A knot diagram can gain extra crossings under allowed diagram moves without changing its knot type. Any proposed physical labels must be independent of such representation choices, or be additional physical framing/state data with a declared energy and transformation law.

In particular u and d mean flavor, not color. Both u and d each transform as a color triplet. Proton uud and neutron udd are color-singlet composites; their different flavor content does not define the three colors. The color contraction of a three-quark singlet involves epsilon_abc, with a,b,c color indices independent of flavor. QCD also needs antiquarks and mesons, not only three-constituent baryons. [PDG QCD review](https://pdg.lbl.gov/2025/reviews/rpp2025-rev-qcd.pdf).

### 3.3 A precise way the trefoil idea could be tested

Suppose the dynamics produces a three-component coherent internal response space within the complete hadronic structure, with amplitudes c = (c_1,c_2,c_3). This does not assume three isolated quark solitons. If the effective quadratic form is proportional to c^dagger c, it has U(3) symmetry. Its traceless transformations give an SU(3) candidate, while an overall phase is a separate direction. Degeneracy, complex amplitudes, and preservation by interactions must be established, not assigned after inspecting the knot.

For basis transition operators E_ab, one has

$$
[E_{ab},E_{cd}]=\delta_{bc}E_{ad}-\delta_{da}E_{cb}.
$$

The traceless anti-Hermitian combinations span su(3). Writing these matrices is trivial once a complex three-state space is assumed. The nontrivial test is whether physically allowed reception operations realize that algebra, act identically on both u-like and d-like states, and preserve it beyond a tuned quadratic approximation.

Even that gives at most an internal symmetry. Local gauge redundancy, Gauss constraints, and a propagating connection with Yang-Mills dynamics require an additional derivation. A finite permutation group of three modes is insufficient. A lattice link model can test consistency, but assigning SU(3) matrices to links would insert the gauge group rather than derive it.

## 4. Weak interactions: formulate the proposed move correctly

The user's udd -> uud example is neutron beta decay:

$$
n(udd)\longrightarrow p(uud)+e^-+\bar\nu_e.
$$

At the constituent level, the charged weak transition is

$$
d\longrightarrow u+W^{-*},\qquad
W^{-*}\longrightarrow e^-+\bar\nu_e.
$$

The W is virtual in neutron decay. Electric charge balances: -1/3 = 2/3 - 1. The emitted neutral particle is an electron antineutrino. Related capture channels have different incoming/outgoing assignments, for example p + e^- -> n + nu_e when energetically allowed.

Under the clarified whole-baryon hypothesis, this is an internal rearrangement preserving baryonic winding, not destruction of the complete object. Both initial and final nucleons remain baryons and color singlets. The effective d-to-u operation must be derived as an operator on the complete structure; it does not require an isolated d-knot turning into an isolated u-knot.

In the proposed winding/isospin description the transition is

$$
(B=1,I_3=-1/2)\longrightarrow(B=1,I_3=+1/2)+e^-+\bar\nu_e.
$$

This is a target assignment, not a derived weak amplitude. Physical isospin I here is distinct from weak gauge isospin T; the two must not be identified merely because both use SU(2) mathematics.

The sharp low-energy target is the charged-current operator

$$
\mathcal L_\beta=-\frac{G_FV_{ud}}{\sqrt2}
[\bar u\gamma^\mu(1-\gamma^5)d]
[\bar e\gamma_\mu(1-\gamma^5)\nu_e]+\mathrm{h.c.}
$$

Matching this requires spinors, left-chiral coupling, color preservation, and coherent amplitudes, not only charge-balanced diagram edits. Hadronic matrix elements are needed to turn this constituent operator into a neutron lifetime or angular correlations. The weak interaction also includes neutral-current scattering and purely leptonic processes such as muon decay, so a literal “all weak processes unknot baryons” rule is inadequate. [PDG electroweak review](https://pdg.lbl.gov/2025/reviews/rpp2025-rev-standard-model.pdf).

If a proposed move changes total Hopf charge, it is forbidden by smooth evolution with the present unit-vector constraint and fixed boundary conditions unless other excitations carry the missing charge. Alternatively one must explicitly introduce a reconnection core, a field zero, or changed boundary conditions and calculate its cost. A rearrangement of a preimage knot can occur without changing total Hopf charge; knot shape and Hopf integer are not interchangeable.

## 5. Exact matter-representation grid

The local Standard Model gauge algebra is su(3)_c + su(2)_L + u(1)_Y. Its conventional group notation is SU(3)_c x SU(2)_L x U(1)_Y; the possible global quotient is a separate question. Use the hypercharge convention q_em = T_3 + Y. In this table q_em is electric charge in units of e, not the structural Q.

These representations are targets to derive, not proposed knot identifications. The three generations have the same representations. Weak-basis partners need not coincide with mass eigenstates because of mixing. Standard electroweak assignments are reviewed by [PDG](https://pdg.lbl.gov/2025/reviews/rpp2025-rev-standard-model.pdf).

| Matter element                 | Members across generations                                   | Representation (SU(3), SU(2), Y)                           | Candidate Signal Space interpretation                                                                               | Present status and required definition                                                                                                |
| ------------------------------ | ------------------------------------------------------------ | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| Left quark doublets            | (u,d)_L; (c,s)_L; (t,b)_L                                    | (3,2,+1/6)                                                 | Effective internal quark responses within complete hadrons; three color components times two weak-flavor components | Missing: derive a six-component chiral multiplet and simultaneous commuting color/weak actions; no isolated quark soliton is required |
| Right up-type quarks           | u_R, c_R, t_R                                                | (3,1,+2/3)                                                 | Right-chiral states with color but no weak doublet action                                                           | Missing: distinguish right states dynamically, not by a mirror drawing alone                                                          |
| Right down-type quarks         | d_R, s_R, b_R                                                | (3,1,-1/3)                                                 | A second right-chiral color triplet                                                                                 | Missing: derive distinct hypercharge and masses                                                                                       |
| Left lepton doublets           | (nu_e,e)_L; (nu_mu,mu)_L; (nu_tau,tau)_L                     | (1,2,-1/2)                                                 | Color-singlet defect states paired by a chiral local move                                                           | Missing: spin-1/2, weak doublet algebra, correct charges and coupling                                                                 |
| Right charged leptons          | e_R, mu_R, tau_R                                             | (1,1,-1)                                                   | Color/weak-singlet chiral partners                                                                                  | Missing: obtain charged fermions without imposing labels                                                                              |
| Right neutrinos, if introduced | nu_R candidates                                              | (1,1,0)                                                    | Optional singlet sector                                                                                             | Not in the minimal renormalizable SM; their existence and Dirac/Majorana choice must not be assumed as a result                       |
| Antiparticles                  | Antiquarks, positron, antimuon, antitau, antineutrino states | Conjugate representations; reversed additive gauge charges | Candidate conjugation of a framed/quantized defect                                                                  | Missing: prove conjugate gauge action and CPT; reversing knot handedness or Hopf sign alone is not enough                             |

For observed neutrino masses and oscillations, additional structure beyond the minimal massless-neutrino SM is required. Distinct exactly conserved Hopf integers are not a natural basis for ordinary flavor oscillations; explore mixing among states in the same allowed topological sector. [PDG neutrino review](https://pdg.lbl.gov/2025/reviews/rpp2025-rev-neutrino-mixing.pdf).

## 6. Force, boson, and mechanism grid

| Standard Model element                  | Required physical structure                                                     | Possible topological route                                                                         | Signal Space status                                                               | Decisive next requirement                                                                                                        |
| --------------------------------------- | ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| Electromagnetism / photon gamma         | Unbroken local U(1)_em; massless spin-1 field with two transverse polarizations | Phase transport/holonomy of framed fibers                                                          | Global scalar phase exists; no electromagnetic gauge field                        | Derive connection, Maxwell action, Gauss law, and charged response                                                               |
| Strong force / eight gluons             | Local SU(3)_c, adjoint spin-1 connection, non-Abelian self-coupling             | Continuous transformations among three constituent modes                                           | No color triplet or gluon modes                                                   | Derive su(3) algebra and local Yang-Mills dynamics; demonstrate confinement/asymptotic freedom in the appropriate quantum theory |
| Charged weak bosons W+ and W-           | Massive spin-1 fields with chiral charged currents                              | Oriented local state conversion or reconnection amplitude                                          | No weak gauge sector                                                              | Recover charged-current operator, its mediators, universality, and energy dependence                                             |
| Neutral weak boson Z                    | Massive neutral spin-1 field and neutral currents                               | A neutral transport mode of an electroweak connection                                              | Missing                                                                           | Reproduce neutral-current scattering even with unchanged defect identity                                                         |
| Hypercharge field B and weak fields W^a | U(1)_Y and SU(2)_L before electroweak breaking                                  | Distinct commuting transport algebras                                                              | Missing; internal rotations of n are not these gauge fields                       | Derive charges and chiral representations before calling a phase electromagnetic                                                 |
| Electroweak mixing                      | Photon and Z arise from W^3/B mixing; Q_em = T3+Y                               | Vacuum selects an unbroken combination                                                             | Missing                                                                           | Derive a symmetry-breaking vacuum and mixing angle/couplings                                                                     |
| Higgs field / Higgs boson               | Complex doublet (1,2,+1/2), one physical scalar after breaking                  | A collective order parameter of the substrate                                                      | Phi is not this doublet; no identification established                            | Derive representation, potential, gauge masses, and measured-type couplings                                                      |
| Fermion masses                          | Yukawa structures and mass eigenstates                                          | Defect collective spectrum plus coupling to order parameter                                        | Classical lump energies only                                                      | Quantize and derive mass-generating operators; do not fit knot energies and call them predictions                                |
| CKM quark mixing / CP violation         | Misaligned up/down mass matrices and a physical complex phase                   | Mixing of internal defect states under weak moves                                                  | Missing                                                                           | Compute matrices from the same dynamics and reproduce flavor-changing amplitudes                                                 |
| PMNS neutrino mixing                    | Lepton flavor/mass misalignment and nonzero mass splittings                     | Several light states within compatible topological sectors                                         | Missing; ordinary orientation waves are scalar                                    | First obtain fermionic states, then masses and mixing                                                                            |
| Three generations                       | Three copies of chiral representations with unequal masses                      | Excitations or distinct protected families with identical gauge response                           | No selected family count                                                          | Explain why three light families, why their hierarchy, and why no unwanted states                                                |
| Spin and Fermi statistics               | Lorentz spin-1/2 and fermionic exchange                                         | Finkelstein-Rubinstein quantization of suitable defect configuration spaces                        | A mathematical possibility, not implemented                                       | Analyze our configuration space, choose/justify quantization, calculate spin states                                              |
| Color-singlet hadrons                   | Baryon and meson spectra, currents, and color-singlet amplitudes                | Complete recurrences with effective internal quark responses; candidate B=1 baryons and B=0 mesons | Whole-hadron hypothesis specified; no quark response or hadronic spectrum derived | Derive singlet composition, confinement, scattering response, and mesonic sectors; winding alone does not imply three quarks     |
| Baryon number                           | Additive baryon/antibaryon assignment in the hadronic regime                    | Integer degree B of an SU(2)-valued field, or a carefully matched Hopf sector                      | Proposed extension; B is not the existing phase charge Q                          | Specify field and boundaries, derive topological current, stabilize and quantize the B=1 sector                                  |
| Anomaly cancellation                    | Quantum consistency of chiral gauge currents                                    | A global constraint on allowed defect multiplets                                                   | Not addressed                                                                     | Recover anomaly-free representation content, including global SU(2) consistency                                                  |

The gauge-boson count is eight gluons plus W+, W-, Z, and photon after electroweak breaking. Before breaking it is eight plus three plus one. This count is a target for dynamical degrees of freedom, not a count of crossings. The Higgs is an additional physical scalar. Gravity and dark matter are not supplied by the Standard Model and are not counted as successes or omissions in this grid.

## 7. The strongest existing mathematical bridge—and its limit

Odd-Hopf-charge solitons can admit fermionic quantization via configuration-space topology. This is an established possibility, not an automatic consequence that every odd knot is a neutrino or quark. The full quantum theory and its allowed spin states still need to be constructed. [Krusch and Speight](https://arxiv.org/abs/hep-th/0503067).

There is also prior work explicitly assigning particle structure to braided ribbons: [Bilson-Thompson's preon proposal](https://arxiv.org/abs/hep-ph/0503213). A later representation-theoretic analysis maps aspects of that construction to SU(3)_c x U(1)_em and discusses chirality, while explicitly identifying its sector limitation. These are relevant precedents, not experimental confirmation or a completed derivation of Standard Model dynamics. [Chester, Arsiwalla, and Kauffman](https://arxiv.org/abs/2501.03260).

Study these approaches for their precise success/failure boundaries. Importing their labels without a local Signal Space Hamiltonian would not advance the dynamical derivation.

## 8. A sharp next derivation: one generation before all particle masses

The charged-Hopf binding calculation tests whether candidate objects exist. A separate algebraic milestone should test whether their proposed internal operations can carry one Standard Model generation.

1. Declare what one physical fiber retains: an amplitude, orientation, framing, phase, and/or other variable. Specify which are observable and which are redundancy.
2. Use the clarified whole-baryon ontology for the hadronic branch: effective quarks are internal responses, not separately postulated knots. Specify the meson and lepton sectors separately. Complete the winding calculation in section 10 before treating a three-quark interpretation as established.
3. Define diagram equivalences and physical moves. Equivalent pictures must yield the same observables; reconnection must have a local amplitude and conservation ledger.
4. Construct a state space and derive its transformation algebra. If quantum superposition is assumed, state it. Demonstrate three color states for each of two weak flavors, not three flavor crossings.
5. Establish commuting color and weak generators, a hypercharge assignment, and left/right asymmetry. First match the representation grid; only then investigate masses and generations.
6. Check quantum anomalies. In a left-handed Weyl convention one generation contains Q_L, u_R^c, d_R^c, L_L, e_R^c. For example the mixed SU(2)^2-U(1) condition reduces to 3(1/6)-1/2=0, and the cubic hypercharge condition is

$$
6(1/6)^3+3(-2/3)^3+3(1/3)^3+2(-1/2)^3+1^3=0.
$$

Also check SU(3)^2-U(1), the gravitational-hypercharge anomaly, cubic color consistency, and the even number of SU(2) doublets (four per generation including color multiplicity). Merely matching electric charges is insufficient.

7. Derive a local beta-transition amplitude with the displayed chiral operator and a color-singlet lepton pair. Also test a neutral-current process and purely leptonic decay so that the rule is not specialized to one baryon example.
8. Only after these gates derive propagating gauge dynamics, symmetry breaking, and independent predictions. A selected target algebra alone is not a force theory.

Success at this stage would be a defensible map from a microscopic move algebra to chiral multiplets. A failure to obtain continuous color transformations, chirality, or anomaly cancellation would identify a concrete missing mechanism rather than motivate assigning more knot names.

## 9. Assessment

The productive hypothesis is “topology constrains the state space, while local reception dynamics determines its symmetries and interactions.” Current equations support studying binding and topological sectors. They do not support the literal identifications unknot = electromagnetism, trefoil = SU(3), or untying = the weak interaction.

The closest actionable hadronic target is a stabilized unit-winding recurrence with a quantized nucleon-like internal doublet and calculated currents. Its relation to the existing Hopf sector must be made explicit. A three-state color algebra and a chiral beta-transition operator remain separate, harder targets; success on winding alone would not establish them.

## 10. Whole-baryon winding: proposed definition and calculation

### 10.1 Physical meaning and confinement

The user's proposal is that removing one essential internal part destroys the complete baryonic configuration: the quark labels describe interdependent aspects of one object. This is a useful constraint to test, but its energy cost and accessible decay or rearrangement channels must follow from the dynamics.

Gauge redundancy and confinement are distinct. Gauge redundancy identifies different descriptions of the same physical state; confinement concerns which excitations can exist as isolated asymptotic states. The absence of free quarks does not make quark response physically empty. A successful whole-object description must still recover gauge-invariant scattering observables, flavor currents, and the observed effective constituent/parton response. No isolated quark soliton is demanded by this program.

Mesons are an entire required sector, not a single pion exception. Effective q-antiquark channels, multiquark channels, and gluonic excitations must be accommodated wherever the hadron spectrum and scattering require them. Three internal labels alone cannot be the universal rule for every hadron. See the [PDG quark-model review](https://pdg.lbl.gov/2025/reviews/rpp2025-rev-quark-model.pdf).

### 10.2 A concrete candidate invariant

Introduce, provisionally, a smooth field with fixed asymptotic value:

$$
U(\mathbf x)\in SU(2)\simeq S^3,\qquad U(\mathbf x)\to\mathbf 1\quad(|\mathbf x|\to\infty).
$$

One-point compactification then gives a map from spatial S^3 to internal S^3. Define its degree by

$$
B=-\frac{1}{24\pi^2}\int d^3x\,\epsilon^{ijk}
\operatorname{Tr}\!\left[(U^\dagger\partial_iU)(U^\dagger\partial_jU)(U^\dagger\partial_kU)\right]\in\mathbb Z.
$$

The overall sign fixes an orientation convention. This is the candidate baryonic winding, not a count of crossings or loops. With compatible spacetime conventions its current is

$$
j_B^\mu=-\frac{1}{24\pi^2}\epsilon^{\mu\nu\rho\sigma}
\operatorname{Tr}(L_\nu L_\rho L_\sigma),\qquad L_\mu=U^\dagger\partial_\mu U,
\qquad B=\int d^3x\,j_B^0.
$$

For smooth constrained fields this current is identically conserved. Boundary flux, singularities, or leaving the target manifold require separate treatment. This conservation is topological, unlike the existing scalar phase Noether charge Q. Choosing the target manifold and calling its degree baryon number is an explicit modeling assumption; it has not been derived from ordered reception.

Skyrme-type effective theories provide an established precedent for baryons as winding solitons and collective quantization of nucleon states. They do not by themselves derive microscopic QCD or all Standard Model forces. See [Adam, Sanchez-Guillen, and Wereszczynski](https://arxiv.org/abs/1007.1567).

| Physical target              | Proposed winding assignment                      | What remains to derive                                                                          |
| ---------------------------- | ------------------------------------------------ | ----------------------------------------------------------------------------------------------- |
| Proton and neutron           | Both B=+1; different internal isospin states     | A spin-1/2, isospin-1/2 spectrum, currents, charges, and splitting                              |
| Antibaryons                  | B=-1 with appropriate conjugation                | Antiparticle transformation, spectrum, and current reversal                                     |
| Pions and other mesons       | B=0, with nontrivial excitations allowed         | Mesonic modes, quantum numbers, masses, and interactions; B=0 is not the vacuum alone           |
| Multiple baryons             | Additive integer B, including B greater than one | Binding or scattering, fission thresholds, and many-object dynamics                             |
| Effective uud / udd response | Internal states of a B=1 object                  | Why the response has three valence-quark quantum numbers and the correct color/flavor structure |

A proton is assigned B=1, not B=3. In QCD, B=(N_q-N_antiquark)/3; the factor 1/3 belongs to the quark assignment. An integer degree does not derive that factor or force a three-part decomposition. Imposing it by hand would not answer the user's central question.

### 10.3 Charges and internal states

For the two-flavor nonstrange hadronic sector, a target charge relation is

$$
\frac{Q_{\mathrm{em}}}{e}=I_3+\frac{B}{2}.
$$

At B=1, I_3=+1/2 gives a proton-like charge and I_3=-1/2 gives a neutron-like charge. At B=0 an isospin triplet has pion-like charges. This is a restricted hadronic relation, not a replacement for the full Standard Model hypercharge assignments. The field dynamics, collective quantization, and coupling to an electromagnetic current must establish the proposed I_3 and Q_em; winding alone supplies neither.

Keep three quantities distinct: the existing continuous classical phase charge Q, the candidate integer baryon degree B, and electric charge Q_em. No equality among them has been derived.

### 10.4 Relation to the existing Hopf extension

The candidate bridge is the Hopf projection

$$
\mathbf n\cdot\boldsymbol\sigma=U\sigma_3U^\dagger.
$$

For smooth maps with the stated compactification and compatible normalization, the Hopf invariant of this projection equals the degree of U, up to orientation convention:

$$
\mathscr H[\mathbf n]=\pm B[U].
$$

This connects the two topological descriptions; it does not equate their actions. The projection is invariant under local right multiplication U -> U exp(i theta sigma_3). One must decide whether this fiber phase is redundant or a new physical degree of freedom before adding a kinetic term. A dynamical SU(2)-valued field generally adds information beyond n alone. This SU(2) target is not automatically the weak gauge group. The configuration-space bridge and possible fermionic quantization are discussed by [Krusch and Speight](https://arxiv.org/abs/hep-th/0503067).

Neither unit degree nor unit Hopf charge forces a trefoil-shaped energy distribution. The integer class, geometry of preimage curves, framing/twist, and knot-complement group are different data. Their physical relations must be calculated rather than inferred from matching integers.

### 10.5 Next calculation and success criteria

1. **Declare the extension.** Specify whether U is a physical reception variable or only a lift of n. Write its energy and coupling to Phi; preserve the established charge definitions. Identify any new assumptions and parameters.
2. **Find a resolved B=1 minimum.** Include an explicit stabilization mechanism: in three spatial dimensions a quadratic gradient energy alone shrinks under scaling. Check energy, integer charge, resolution, boundary dependence, and nonsymmetric perturbations. A hedgehog ansatz may supply a seed, not proof of unrestricted stability.
3. **Quantize collective modes.** Calculate rotational/internal moments of inertia and configuration-space constraints. Test whether the lowest permitted states have spin 1/2 and isospin 1/2. These quantum numbers must not be read off from a classical knot picture.
4. **Calculate physical currents.** Obtain baryon and candidate electromagnetic/flavor matrix elements, then form factors and localized response. Test the proton/neutron target assignments without equating phase charge and electric charge by fiat.
5. **Test the effective quark claim.** Determine whether the response requires three valence-like components, their fractional charge assignments, color-singlet contractions, and the correct flavor transitions. Distinguish low-energy constituent descriptions from high-energy parton observables. Failure here means a baryonic soliton model, not a derivation of quarks.
6. **Include the B=0 and multi-object sectors.** Derive meson-like modes and their couplings; test baryon-baryon and baryon-antibaryon processes with conserved total charge and winding. Do not infer binding from integer additivity.
7. **Return to the Standard Model gates.** Derive local color dynamics, chiral weak amplitudes, and anomaly-free matter content using the earlier grids. An exactly conserved winding model describes a restricted regime unless it also explains how the full electroweak theory's anomalous baryon-number processes can be represented.

The immediate deliverable should be an explicit energy functional, a converged unit-winding solution, its collective spectrum, and current matrix elements. The decisive later question is whether the effective three-quark response follows from that same calculation without being inserted as a label.
