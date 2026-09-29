---
title: 'Signal States, Lorentz Cones and Operational Clocks'
subtitle: 'Signal Space Foundations, Part II: From Reception Records to Conditional Geometry'
date: '11 September 2026 | Version 0.1.0'
lang: en-US
documentclass: article
fontsize: 11pt
geometry: margin=1in
colorlinks: true
linkcolor: NavyBlue
urlcolor: NavyBlue
toc: false
header-includes:
  - '\usepackage{amsmath,amssymb,mathtools}'
  - '\usepackage{microtype}'
  - '\usepackage{float}'
  - '\usepackage{needspace}'
  - '\usepackage{fancyhdr}'
  - '\pagestyle{fancy}'
  - '\fancyhf{}'
  - '\fancyhead[L]{\small Signal States and Operational Clocks}'
  - '\fancyhead[R]{\small Signal Space Foundations II}'
  - '\fancyfoot[C]{\thepage}'
  - '\setlength{\headheight}{14pt}'
  - '\setlength{\emergencystretch}{3em}'
  - '\allowdisplaybreaks[1]'
  - '\floatplacement{figure}{H}'
---

# Abstract {#sec-abstract}

Part I of the Signal Space foundations specified quantum reception histories, coherent alternatives, retained memory, and classical records. This paper develops their interface to signal-state comparison and clock calibration. For a declared two-component channel sector, calibrated analyzer records determine a positive Hermitian intensity operator. Its determinant supplies the standard Lorentz-cone quadratic form, and determinant-preserving congruences supply the proper orthochronous Lorentz action. We separate this representation from physical observer covariance: an intensity operator is neither a spacetime interval nor a response-hazard operator without an additional law, and normalized nonunitary filtering is not deterministic frame evolution. The diagonal hazard specialization recovers the earlier stationary rapidity identity while preserving its exact nonstationary failure. Independent echo measurements expose response latency and statistical lag. We prove that fixed local additive rewards in the two-state process cannot reproduce the proper-time rate of every ensemble-mean trajectory. As a different clock construction, a confined coherent mode on prescribed uniformly accelerated boundaries has an exactly calculable phase rate, approaching center proper time with a quadratic finite-size correction under fixed inertial calibration. A matched analytical and numerical benchmark distinguishes this correction from the count-clock excess. Finally, we state the additional tangent-space, cone, and universal-calibration assumptions needed for a Lorentzian metric, and show why the single-channel modular generator does not supply boosts by itself. The contribution is a set of conditional bridges, obstructions, and reproducible controls; autonomous spacetime, universal matter dynamics, and physical constants remain to be derived from a shared law.

**Keywords:** quantum reception histories; positive Hermitian cone; operational rapidity; radar time; phase clocks; calibration; emergent geometry.

**Status of the contribution.** This is a complete theoretical manuscript with explicit assumptions and reproducible finite calculations. Standard Lorentz, quantum-information, and accelerated-cavity identities are derived or attributed as appropriate. Their integration and diagnostic use within Signal Space are the proposed contribution; priority for the underlying mathematics is not claimed. Numerical values are synthetic model calculations, with no empirical validation asserted.

# 1. Introduction {#sec-introduction}

A theory organized around signal histories must explain how records become geometric comparisons. A reception rate can depend on source preparation, detector response, exposure, motion, and retained receiver state. A recurrence can depend on internal dynamics and environmental history. The presence of a hyperbolic function in either description is insufficient to identify a universal spacetime metric. The physical task is to establish agreement between independently defined procedures, with calibration fixed before the comparison.

Part I, *Composition of Signal Histories* [1], established the operational starting point for the revised Signal Space architecture [2]. A finite causal circuit carries quantum systems and retained memories. Instruments determine record probabilities, and a specified larger realization determines whether alternatives can interfere. The quantum representation is an explicit working postulate. Circuit order does not already supply duration, a spatial dimension, or a metric. These commitments remain unchanged here.

The architecture's next bounded deliverable combines two questions. First, can the earlier logarithmic ratio of directional response rates be embedded in a precisely interpreted three-directional comparison structure? Second, can recurrent readouts agree with time reconstructed from exchanges outside stationary conditions? The positive Hermitian cone is a mathematically economical candidate for the first question. A confined phase mode is a useful alternative to reversal counting for the second. Neither solves the other automatically.

The relation between two-component complex operators and Lorentz transformations is established mathematics. Its use in quantum filtering is particularly instructive because it distinguishes congruence, conditioning, and trace preservation [4]. Radar time similarly provides an established operational language on a supplied spacetime [5]. Extended quantum clocks illustrate why the point-clock approximation must be checked rather than imposed on every physical device [6,7]. We use these constructions as controlled benchmarks for Signal Space, exposing the assumptions needed to connect them.

The earlier reception-driven clock manuscript [3] supplies a decisive constraint. The stationary reversal rate, normalized by the geometric mean of outgoing hazards, agrees with the time-dilation factor of the stationary mean drift. During relaxation, the same normalized expected count generally exceeds the proper time of the mean trajectory. This distinction survives a change of notation and survives labeling each reversal by a phase increment. It motivates a different physical recurrence, rather than an observational correction chosen to enforce the desired answer.

This paper gives an operational intensity reconstruction, the full cone action and its limits, an independent echo comparison, an additive-readout obstruction, and a confined phase-clock control. The concluding reconstruction theorem is conditional: it states what a future autonomous model would have to supply for these local comparisons to define a common metric. In the publication sequence of [2], this is the second foundations paper, not a renumbering or replacement of the earlier manuscript called Paper III.

# 2. Interfaces inherited from Part I {#sec-interfaces}

## 2.1. Records and retained state

Retain Part I's finite-dimensional complex representation, tensor-product composition, local quantum instruments, and trace rule. For a protocol $\mathcal P$, the joint record law is

$$
p(r_1,\ldots,r_n\mid\mathcal P)
=\operatorname{Tr}\!\left[
\mathcal I_{r_n\mid a_n}\circ\cdots\circ
\mathcal I_{r_1\mid a_1}(\rho_0)\right].
\tag{P1}
$$

Adaptive settings depend only on permitted earlier records. Signal, receiver memory, and returning environments must remain in the predictive state whenever later protocols can access them. A reduced channel matrix used below is sufficient for its local analyzer statistics; it is not generally sufficient for arbitrary multitime predictions.

Unread instrument outcomes are summed as completely positive maps. Coherent alternatives are combined only in a specified larger realization. The two alternatives of Part I's channel register therefore provide a usable two-component sector, but no physical spatial direction has yet been assigned to that sector. Measurements along three Pauli axes are three analyzer choices on one qubit, not evidence for three extended spatial coordinates.

## 2.2. Assumption ledger

The following additions are separated by purpose.

**S1. Signal-sector restriction.** Selected trials address a two-dimensional complex signal sector. Any vacuum, loss, leakage, temporal distinguishability, and inaccessible memory are separately accounted for. This sector is chosen as a minimal extension of Part I, not derived as a universal microscopic dimension.

**S2. Analyzer calibration.** The source ensemble is reproducible across settings, and a tomographically complete set of analyzer effects is calibrated. Exposure and efficiency are fixed independently when absolute intensity is reported. Settings that change the source require a larger protocol model.

**S3. Candidate comparison law.** A proposed local comparison between descriptions acts by a single complex linear amplitude map and hence by congruence on the intensity operator. Determinant preservation and orientation preservation are further restrictions when a Lorentz comparison is asserted. Section 5 distinguishes this ansatz from an instrument physically applied in the laboratory.

**K1. Reference-geometry controls.** Sections 6-9 use a supplied flat reference metric and speed $c_0$. These controls assess clock laws; they do not derive their reference geometry.

**K2. Confined-mode control.** The phase-clock example has prescribed reflecting boundaries, a fixed massless wave equation, and a declared mode preparation and readout. Boundary support and external driving are supplied. Binding, recoil, and their energy balance are not derived.

**G1. Conditional continuum interface.** Only Section 10 assumes a smooth four-dimensional tangent structure, a linear coframe, and a common interpretation of its cone by physical probes. Those assumptions are the missing geometric bridge, not conclusions of S1-S3.

Each result below identifies which additions it uses. In particular, satisfying S1-S2 does not establish S3, and satisfying S3 does not establish G1.

## 2.3. Notation and units

We write $X$ for an unnormalized positive signal operator and $\rho_S=X/\operatorname{Tr}X$ for its normalized state. The coordinates $x^a$ of $X$ initially have the units of intensity per declared exposure. The scalar $\gamma=\sqrt{\det X}$ has the same units; it is never a Lorentz factor in this manuscript. The signed diagonal coordinate is $h$, while $\eta$ denotes independently inferred kinematic rapidity.

Outgoing reversal hazards are $q_+$ and $q_-$. The directional mean is $b=\mathbb E\sigma$, with $\sigma=\pm1$. Counts are $N$, an expected count reading is $\mathbb E\widehat\tau$, and the proper time of a specified timelike reference curve is $\tau$. These are different objects. Physical thermodynamic entropy would be $k_B$ times dimensionless entropy; no such energy or temperature normalization is inferred here.

The matrix determinant uses $J=\operatorname{diag}(1,-1,-1,-1)$. For a spacetime metric we use the architecture's convention $\eta_{ab}=-J_{ab}$, so timelike vectors have negative squared length. This explicit sign conversion avoids changing conventions between the cone and the metric.

# 3. An operational positive signal operator {#sec-signal-operator}

## 3.1. Intensity from calibrated trials

Consider repeated trials of the selected channel sector with density operator $\rho_S$. Let $\mathcal J\geq0$ be the mean number of carriers in that sector per fixed exposure. Define

$$
X=\mathcal J\rho_S,\qquad
\mathbb E n_E=\operatorname{Tr}(EX)
\tag{S1}
$$

for a calibrated analyzer effect $0\leq E\leq I$, where $n_E$ is its count per exposure. For multiple carriers the second relation is an additive first-moment model: $X$ can equivalently be the sum of their one-carrier reduced operators. It does not require Poisson arrivals or independent carriers. Higher count correlations and temporal memory require additional data.

If a trial contains either vacuum or one carrier, $\mathcal J$ is its occupation probability and is bounded by one. Aggregated exposures allow unrestricted nonnegative intensity. Neither construction makes elapsed time fundamental: a fixed number of locally controlled trials can define exposure before seconds are assigned. To quote a rate per unit time, a separately calibrated time exposure is necessary.

**Proposition S1 (operational reconstruction).** Under S1-S2, the six calibrated projective analyzer means along the three Pauli axes determine a unique Hermitian operator $X$. They admit the quantum intensity model precisely when the reconstructed operator is positive semidefinite and the exposure normalizations agree.

*Proof.* Write $\sigma_0=I$ and let $\sigma_1,\sigma_2,\sigma_3$ be the Pauli matrices. Set

$$
X=x^0 I+\sum_{i=1}^3x^i\sigma_i,
\qquad
x^a=\tfrac12\operatorname{Tr}(\sigma_aX).
\tag{S2}
$$

For $E_{i,\pm}=(I\pm\sigma_i)/2$,

$$
\mu_{i,\pm}=\operatorname{Tr}(E_{i,\pm}X)=x^0\pm x^i.
\tag{S3}
$$

Thus $x^i=(\mu_{i,+}-\mu_{i,-})/2$, while every setting yields the same $x^0=(\mu_{i,+}+\mu_{i,-})/2$. These four real coordinates uniquely specify $X$. Its eigenvalues are $x^0\pm|\mathbf x|$, so positivity is equivalent to $x^0\geq|\mathbf x|$. Conversely, every such nonzero operator has the form (S1), with $\mathcal J=2x^0$ and a valid density operator. The zero operator represents no selected carriers. $\square$

This is finite qubit tomography with retained intensity, not a reconstruction of quantum theory. Pairwise nonnegative counts alone are insufficient: the combined contrasts must also obey $|\mathbf x|\leq x^0$. Finite noisy estimates can violate positivity. A constrained likelihood fit with a declared count law is then appropriate; a negative fitted eigenvalue should not be reinterpreted as a physical spacelike signal.

## 3.2. Coherence supplies the transverse coordinates

The diagonal basis gives

$$
X=\begin{pmatrix}
x^0+x^3&x^1-i x^2\\
x^1+i x^2&x^0-x^3
\end{pmatrix}.
\tag{S4}
$$

The real and imaginary coherences supply two additional coordinates beyond two diagonal intensities. They are read through incompatible analyzer settings on reproducibly prepared trials. They are not simultaneous preexisting classical outcome labels.

The reduced state from Part I's reception experiment has off-diagonal magnitude proportional to the memory overlap and temporal overlap. Complete unread recording removes that coherence. At fixed diagonal entries, dephasing $X_{01}\mapsto\zeta X_{01}$ with $|\zeta|\leq1$ gives

$$
\det X_{\rm after}-\det X_{\rm before}
=(1-|\zeta|^2)|X_{01}|^2\geq0.
\tag{S5}
$$

Thus ordinary record formation can change the determinant coordinate without moving the apparatus. This is an immediate control against identifying every change of $X$ with a geometric interval or velocity. Conversely, scalar attenuation $X\mapsto\lambda X$ changes its scale without changing its normalized state. Source power, decoherence, and motion must be separately identified by the observation law.

## 3.3. Intensity is not a response hazard

The quantity in (S1) describes incident carriers in selected trials. The hazard $q_+$ describes the probability per reference time of leaving the receiver's plus state. A physical response law can connect them, for example through a specified state-dependent interaction cross section and bath approximation. Positivity does not supply that law.

One may build an apparatus whose calibrated diagonal response data are represented by

$$
X_q=\operatorname{diag}(q_-,q_+).
\tag{S6}
$$

The reversed ordering follows the earlier Signal Space stationary occupations. Equation (S6) is a distinct specialization with units of inverse reference time, not an identification of arbitrary measured $X$ with hazards. A complete three-directional response model must specify how off-diagonal inputs alter receiver dynamics and what physical comparisons preserve that law.

\Needspace{9\baselineskip}

# 4. Lorentz-cone structure and its scope {#sec-cone}

## 4.1. Cone and logarithmic coordinates

For (S2), the Pauli product identity gives

$$
\det X=(x^0)^2-|\mathbf x|^2=x^T Jx.
\tag{L1}
$$

Strict positivity corresponds to the interior of the future Lorentz cone. Nonzero rank-one operators form its boundary; $X=0$ is the apex. For $X>0$, define

$$
\gamma=\sqrt{\det X},\qquad
h=\operatorname{artanh}\frac{|\mathbf x|}{x^0}.
\tag{L2}
$$

With $\mathbf n=\mathbf x/|\mathbf x|$ when $\mathbf x\ne0$,

$$
X=\gamma e^{h\mathbf n\cdot\boldsymbol\sigma}
=\gamma\bigl(\cosh h\,I+\sinh h\,\mathbf n\cdot\boldsymbol\sigma\bigr).
\tag{L3}
$$

Here $h\geq0$; the axis is immaterial at $h=0$. In a fixed diagonal axis one may instead use signed $h$, giving

$$
q_-=\gamma e^h,\qquad q_+=\gamma e^{-h},
\qquad h=\tfrac12\ln(q_-/q_+).
\tag{L4}
$$

The normalized operator is

$$
\rho_S=\frac12\bigl(I+\tanh h\,\mathbf n\cdot\boldsymbol\sigma\bigr).
\tag{L5}
$$

Normalization removes $\gamma$. At a fixed nonzero intensity the pure-state limit has $h\to\infty$ and $\gamma\to0$; the product in (L3) remains finite. A pure qubit in a stationary apparatus therefore lies on the algebraic null boundary. It is not thereby a photon or a null worldline. Operational spatial meaning requires more than cone membership.

## 4.2. Congruence and the Lorentz action

**Proposition L1 (standard cone representation).** For $A\in SL(2,\mathbb C)$, the real-linear map $X\mapsto AXA^\dagger$ preserves positivity and determinant and induces a proper orthochronous Lorentz transformation. Every such Lorentz transformation is induced, with kernel $\{I,-I\}$.

*Proof.* Positivity is preserved by invertible congruence, and $\det(AXA^\dagger)=|\det A|^2\det X=\det X$. Its real coordinate matrix is

$$
\Lambda(A)^a{}_b
=\tfrac12\operatorname{Tr}(\sigma_a A\sigma_b A^\dagger),
\qquad \Lambda(A)^T J\Lambda(A)=J.
\tag{L6}
$$

Continuity from identity and preservation of the positive cone select the proper orthochronous component. Unitary determinant-one matrices give all spatial rotations. Positive determinant-one matrices $\exp(\xi\mathbf n\cdot\boldsymbol\sigma/2)$ give all pure boosts. A proper orthochronous Lorentz map can first have its action on the time axis undone by a boost; the remaining map fixes that axis and is a spatial rotation. Hence these matrices cover the full group. If $AXA^\dagger=X$ for every Hermitian $X$, using $X=I$ makes $A$ unitary and using the Pauli matrices makes $A$ scalar. Determinant one leaves $A=\pm I$. $\square$

The factor of one half is essential: applying $A=\exp(\xi\sigma_3/2)$ to $X=\gamma I$ produces $X'=\gamma\exp(\xi\sigma_3)$, with cone coordinate $h=\xi$.

For a boost along $\mathbf n$, decompose $\mathbf x=x_\parallel\mathbf n+\mathbf x_\perp$. Direct multiplication gives

$$
\begin{aligned}
x'^0&=x^0\cosh\xi+x_\parallel\sinh\xi,\\
x'_\parallel&=x_\parallel\cosh\xi+x^0\sinh\xi,\\
\mathbf x'_\perp&=\mathbf x_\perp.
\end{aligned}
\tag{L7}
$$

These are active algebraic boosts. A passive reference-frame boost used below carries the opposite sign. Collinear signed rapidities add; non-collinear boosts do not reduce to addition of three scalar log-rate ratios.

## 4.3. What the representation does and does not select

The real vector space of Hermitian $2\times2$ matrices has dimension four. Choosing this sector supplies a local $1+3$ quadratic cone. It does not prove that an event network has four-dimensional tangent spaces, that three directions extend spatially, or that all excitations propagate on this cone. Larger channel spaces also have positive cones, whose determinants are generally higher-degree invariants. Selecting the two-component sector is an explanatory input.

The general congruence with $A\in GL(2,\mathbb C)$ scales the quadratic form by $|\det A|^2$. Restricting to $SL(2,\mathbb C)$ is therefore a scale condition. Arbitrary gain or exposure changes are not secretly excluded by quantum composition.

Noncommuting boosts can generate a Wigner rotation even in flat spacetime. A loop of mere frame changes has a stronger cancellation: if $G_{ji}=A_jA_i^{-1}$, then

$$
G_{ik}G_{kj}G_{ji}=I.
\tag{L8}
$$

A nontrivial sequence of physical boosts and a nontrivial spacetime curvature holonomy are different statements. Deriving curvature requires a physical transport connection over spacetime loops, not only noncommuting local matrices.

# 5. Frame covariance, filtering, and identifiability {#sec-covariance}

## 5.1. A conditional comparison ansatz

Suppose descriptions at two local frames are related by one invertible complex amplitude map $A$ for a specified family of signals. A bilinear intensity then transforms as $X'=AXA^\dagger$. If the same protocol scalar $\det X$ is invariant, $|\det A|=1$; removing an irrelevant overall phase permits a representative in $SL(2,\mathbb C)$.

This is a sufficient construction of the desired action. It is not derived from analyzer counts alone. One must establish that the *same* $A$ compares a spanning collection of preparations, including coherent ones, while detector effects, exposures, and source descriptions transform consistently. Fitting a different $A$ to each source is not a covariance test.

Algebraically, a paired effect transforms dually as $E'=A^{-\dagger}EA^{-1}$, giving $\operatorname{Tr}(E'X')=\operatorname{Tr}(EX)$. However, the transformed effects sum to $A^{-\dagger}A^{-1}$ rather than $I$ when an original POVM sums to $I$. A nonunitary coordinate change therefore also requires a transformed normalization or exposure convention; it cannot be interpreted as an ordinary trace-normalized POVM change with every other laboratory definition held fixed. The operational model must specify which quantities are densities, which measure they use, and which outcomes are compared.

## 5.2. A physical filter has outcomes

A laboratory filter can implement the successful branch

$$
F=kA,\qquad F^\dagger F\leq I,
\qquad
p_{\rm s}=k^2\operatorname{Tr}(A\rho_S A^\dagger).
\tag{F1}
$$

Here $0<k\leq\|A\|_{\rm op}^{-1}$. A complementary operator $G=(I-F^\dagger F)^{1/2}$ completes a valid two-outcome instrument. Conditioned on success,

$$
\rho_{S\mid{\rm s}}
=\frac{A\rho_S A^\dagger}{\operatorname{Tr}(A\rho_S A^\dagger)}.
\tag{F2}
$$

The Lorentz/filtering relation is standard [4]. The successful branch has a selection probability, and discarded failures cannot be treated as absent trials in an unconditioned physical claim.

**Proposition F1 (deterministic-channel restriction).** A map $\rho\mapsto A\rho A^\dagger$ is trace preserving on all normalized states if and only if $A^\dagger A=I$. With $\det A=1$, such maps give the unitary rotation subgroup. A genuine boost followed by normalization is generally nonlinear in mixtures and hence is not a deterministic quantum channel on the qubit alone.

*Proof.* Trace preservation for every density operator means $\operatorname{Tr}[(A^\dagger A-I)\rho]=0$ for every $\rho$, forcing $A^\dagger A=I$. For the nonlinear assertion take $A=\exp(\xi\sigma_3/2)$, $\xi\ne0$. The two eigenstate projectors are individually unchanged by (F2), but their equal mixture $I/2$ maps to $(I+\tanh\xi\,\sigma_3)/2$. This differs from the equal mixture of their individual outputs. $\square$

A passive Lorentz comparison of suitably defined physical quantities remains possible. Proposition F1 only rules out identifying that comparison with a deterministic local qubit filter under unchanged normalization.

## 5.3. Three practical degeneracies

Source anisotropy can produce $h\ne0$ with no relative motion. Detector efficiency imbalance multiplies the two diagonal means differently and can imitate a shift of $h$. Temporal distinguishability or recording can reduce off-diagonal coherence and change $\gamma$ through (S5). These degeneracies can coexist.

Accordingly, a physical covariance test requires independently characterized sources and detectors, an intensity normalization, coherent probes spanning the selected operator space, and a separate motion protocol. The diagonal stationary test is necessary for the proposed hazard interpretation but is far from sufficient for full cone covariance. In particular, a successful reconstruction of $X$ does not make $X$ a complete causal state in the sense of Part I: two joint signal-memory states can have equal $X$ and different future echoes.

# 6. Statistical rapidity and the count-clock obstruction {#sec-count-clocks}

## 6.1. Exact diagonal specialization

For the classical control from [1,3], a constituent moves at reference velocity $c_0\sigma$, with outgoing hazards $q_+=\gamma e^{-h}$ and $q_-=\gamma e^h$. Writing $b(t)=\mathbb E\sigma(t)$, the master equation gives

$$
\dot b=2\gamma\cosh h\,(\tanh h-b).
\tag{C1}
$$

At fixed positive hazards, stationarity yields

$$
b_* =\tanh h,\qquad
\nu_* =\frac{2q_+q_-}{q_++q_-}
=\gamma\operatorname{sech}h.
\tag{C2}
$$

Here $\nu_*$ counts every reversal; a two-reversal directional recurrence has half this frequency. The stationary occupation matrix is $\operatorname{diag}(q_-,q_+)/(q_-+q_+)$, which explains the ordering in (S6). This relationship depends on the response law, rather than on positivity alone.

The long-run count reading $N/\gamma$ has mean rate $\operatorname{sech}h$. On the supplied reference geometry this equals the proper-time rate of the straight *mean-drift* history. Each locally finite piecewise-null constituent path has zero proper-time length. Its count reading and its mean trajectory therefore refer to different objects. A bound timelike material clock has not been constructed by averaging.

The passive frame transformation provides a useful consistency check. On a null segment, $dt'=e^{-\sigma\xi}dt$. Invariance of the infinitesimal reversal probability $q_\sigma dt$ gives

$$
q'_+=e^\xi q_+,\qquad q'_-=e^{-\xi}q_-,
\qquad \gamma'=\gamma,\quad h'=h-\xi.
\tag{C3}
$$

This is a transformation of the same path process with hazards per transformed coordinate time. It is not the transformation of an arbitrary incoming detector rate. In a nonstationary ensemble, equal-time slices and averaging must also be transformed; transforming an ensemble-mean curve and recomputing a mean on new simultaneity slices need not commute.

## 6.2. Nonstationary discrepancy

Let $\gamma(t)>0$ and $h(t)$ be deterministic bounded functions on a finite test interval. Define

$$
\widehat\tau(T)=\int_0^T\frac{dN(t)}{\gamma(t)},\qquad
\bar\tau(T)=\int_0^T\sqrt{1-b(t)^2}\,dt,
\tag{C4}
$$

where $|b|<1$. The first is a random normalized count; the second is proper time along the reference mean curve. The expected count intensity gives

$$
\frac{d}{dt}\mathbb E\widehat\tau
=\frac{q_+(1+b)+q_-(1-b)}{2\gamma}
=\cosh h-b\sinh h.
\tag{C5}
$$

\Needspace{7\baselineskip}

**Proposition C1 (inherited exact discrepancy).** With $\eta_b=\operatorname{artanh}b$,

$$
\frac{d}{dt}\mathbb E\widehat\tau-\dot{\bar\tau}
=\sqrt{1-b^2}\,[\cosh(h-\eta_b)-1]\geq0.
\tag{C6}
$$

*Proof.* Substitute $b=\tanh\eta_b$ into (C5) and use the hyperbolic subtraction identity. Equality holds precisely when $h=\eta_b$. $\square$

This is the result of earlier Paper III [3], carried through Part I without weakening its qualification. The excess is a relaxation effect relative to a specified ensemble-mean curve. It is neither a laboratory disagreement with relativity nor evidence for a universal correction to proper time.

For a small statistical lag $\delta=h-\eta_b$,

$$
\frac{d}{dt}\mathbb E\widehat\tau-\dot{\bar\tau}
=\tfrac12\sqrt{1-b^2}\,\delta^2+O(\delta^4).
\tag{C7}
$$

The earlier relaxation bound [3] controls $\delta$ under bounded driving and a relaxation rate bounded away from zero. Approximate stationary agreement is therefore a restricted adiabatic result. It does not remove count noise, response memory, or the distinction between mean curves and individual trajectories.

## 6.3. Why a local phase relabeling does not repair the clock

Consider the most general additive readout with fixed state residence rewards and fixed reversal rewards at a given bath setting:

$$
Y(T)=\int_0^T u_{\sigma(t)}\,dt
+\sum_{t_j\leq T}w_{\sigma(t_j^-)}.
\tag{C8}
$$

The coefficients may depend on the prescribed bath and on time, but not on the current ensemble distribution. The jump weight uses the pre-reversal state. This includes counting with unequal tick weights and accumulating a phase at fixed state-dependent rates.

**Proposition C2 (local additive-readout obstruction).** No such readout has expected instantaneous rate $\sqrt{1-b^2}$ for every $b$ in a nonempty open interval of $(-1,1)$ at a fixed bath setting.

*Proof.* Its expected rate is

$$
\frac{d}{dt}\mathbb EY
=\frac{1+b}{2}(u_++q_+w_+)
+\frac{1-b}{2}(u_-+q_-w_-)=A+Bb.
\tag{C9}
$$

This is affine in $b$. The target has strictly negative second derivative, $-(1-b^2)^{-3/2}$. The two functions cannot agree on an open interval. $\square$

The proposition does not exclude coherent composite clocks, additional dynamically relevant memory, nonlinear estimators, or a readout fitted to one preparation. It rules out a universal repair by assigning fixed local phase increments to the original two-state process. A controller that estimates $b$ and programs a phase speed proportional to $\sqrt{1-b^2}$ can enforce the target, but has supplied the desired geometry through feedback.

More generally, the expectation of a fixed observable is affine in the state. Proper time computed from an ensemble-mean velocity is a nonlinear ensemble functional. One should not require that functional to equal a universal one-copy expectation without explaining the physical meaning of the averaging. This helps identify why a bound recurrent subsystem is a cleaner successor than further renormalization of an unbound null transport ensemble.

# 7. Independent rapidity from exchanges {#sec-echoes}

## 7.1. Instantaneous reflection control

In the reference flat $1+1$ geometry, place the observer at $x=0$ with calibrated proper time equal to $t$. A smooth timelike reflector remains at $x>0$ on the interval of interest. For an instantaneous reflection at $(t,x)$, let $s$ and $r=\mathcal R(s)$ be emission and return readings. Then

$$
s=t-x/c_0,\qquad r=t+x/c_0,
\qquad t=\frac{s+r}{2},\quad x=\frac{c_0(r-s)}2.
\tag{E1}
$$

Differentiating along the reflector gives

$$
\mathcal R'=\frac{1+b}{1-b},\qquad
\eta_{\rm echo}=\tfrac12\ln\mathcal R',\qquad
\frac{d\tau}{ds}=\sqrt{\mathcal R'}.
\tag{E2}
$$

Here $b=\dot x/c_0$ is the reflector's actual reference velocity. The logarithmic echo coordinate is operationally distinct from the hazard coordinate $h$. Radar-time constructions and their observer dependence are discussed in [5]. Equations (E1)-(E2) require their stated reference geometry and response law.

For a small error $\delta\mathcal R'$ in a positive derivative, the first-order rapidity error is $\delta\eta_{\rm echo}=\delta\mathcal R'/(2\mathcal R')$. Differentiation amplifies timestamp noise, so a practical estimate must specify the fit window, smoothness assumptions, and uncertainty propagation. Exact derivatives in a synthetic control are not finite-sample measurements.

## 7.2. Response latency is a distinct unknown

If reception and re-emission occur at separate events $a$ and $b$ on the responding object,

$$
s=t_a-x_a/c_0,\qquad r=t_b+x_b/c_0.
\tag{E3}
$$

The ordinary midpoint is then a combination of two events rather than a unique reflection event. A stationary relay at distance $L$ with coordinate response delay $d(s)$ produces

$$
\mathcal R(s)=s+2L/c_0+d(s),\qquad
\eta_{\rm app}=\tfrac12\ln[1+d'(s)].
\tag{E4}
$$

Whenever $1+d'>0$, the same uncorrected echo map can be interpreted as an instantaneous moving reflector over a suitable finite interval. Thus echoes alone cannot generally separate motion from an unrestricted latency law. A constant delay biases distance but not the slope in this stationary example; a variable delay can bias both.

Latency must be independently measured, constrained by a previously fitted response model, or resolved by additional local records. For a moving responder, subtracting a laboratory delay from the return reading is not generically sufficient: (E3) must be propagated through the responder's trajectory. Probe recoil and state changes similarly belong in the local instrument and response dynamics.

## 7.3. A comparison with predictive content

The proposed diagonal test fixes detector gains, exposure, source preparation, and response calibration using separate records. It then estimates $q_\pm$, predicts $b$ using the residence law, and compares $h=\tfrac12\ln(q_-/q_+)$ against $\eta_{\rm echo}$ on new histories. Equilibrium predicts equality only for the stated hazard process; a transient predicts the explicit lag and excess of (C1) and (C6).

For a full cone test, a common transformation must also predict transverse coherent preparations and their analyzer records. A diagonal fit cannot validate the non-collinear action. Protocols with deliberately changed source anisotropy, detector imbalance, temporal overlap, and response latency provide negative controls. Geometry should explain the remaining common relation, not absorb each apparatus change into a separately fitted boost.

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

# 9. A reproducible nonstationary comparison {#sec-benchmark}

## 9.1. Matched reference curve, distinct constructions

Choose a center curve starting at rest with positive proper acceleration $a$ and initial position $x_0>0$:

$$
\begin{aligned}
b(t)&=\frac{at/c_0}{\sqrt{1+(at/c_0)^2}},\\
\eta(t)&=\operatorname{arsinh}(at/c_0),\\
\tau(t)&=\frac{c_0}{a}\operatorname{arsinh}(at/c_0).
\end{aligned}
\tag{B1}
$$

An instantaneous echo reflector on this curve yields $\eta_{\rm echo}=\eta$. The cavity of Section 8 has this center curve. To construct a statistical control whose *mean* curve matches it, fix $\gamma>0$, choose $b(0)=0$, and drive the bath by

$$
h(t)=\eta(t)+\operatorname{arsinh}
\!\left[\frac{\dot b(t)}{2\gamma\sqrt{1-b(t)^2}}\right].
\tag{B2}
$$

Indeed $\sinh h-b\cosh h=\sqrt{1-b^2}\sinh(h-\eta)$, so (B2) makes the master equation (C1) hold exactly. The bath parameters have been designed to realize a chosen trajectory; this is a matched control, not autonomous acceleration generated by Signal Space.

This construction compares two model families on one supplied curve. The statistical mean is not identified with an individual bound cavity, and the cavity does not derive the bath hazards. Their common role is to separate two clock errors under specified, fixed calibrations.

## 9.2. Executed values

Use dimensionless reference units with $c_0=1$, $\gamma=1$, $a=0.4$, cavity length $L=0.2$, and reference duration $T=5$. For the count model, divide every reversal by the fixed $\gamma$. For the cavity, use its independently specified inertial frequency $\omega_{10}=\pi c_0/L$; no acceleration-dependent rescaling is applied. The exact formulas and deterministic quadrature give:

| Reading or diagnostic | Value |
| --- | ---: |
| Center proper duration $\tau(T)$ | 3.609088687947 |
| Expected count reading $\mathbb E\widehat\tau(T)$ | 3.641659505751 |
| Cavity phase reading $\tau_\phi(T)$ | 3.607163018690 |
| Count excess $\mathbb E\widehat\tau-\tau$ | 0.032570817804 |
| Phase deficit $\tau-\tau_\phi$ | 0.001925669257 |
| Phase rate ratio $f(0.04)$ | 0.999466438920 |

**Table 1.** Deterministic synthetic control. The digits describe evaluation of the stated mathematical model, not experimental accuracy. The phase origin is set at the beginning of the constant-acceleration comparison; switching transients and detector sampling are excluded.

At the initial event, $\eta_{\rm echo}=0$ while $h=0.198690110349$. At $T=5$, the echo rapidity is $1.443635475179$ and the hazard coordinate is $1.483624816185$. Thus a nonzero statistical lag persists even though the driven Markov mean follows the selected curve exactly.

![Statistical rapidity and fixed-calibration clock errors in the accelerated reference control. Panel A compares the hazard coordinate with independently defined echo rapidity. Panel B compares expected count and cavity phase readings with center proper time. No measurement noise or acceleration-switching effects are included.](figures/clock_comparison.pdf){width=100%}

The curve labeled expected count is evaluated from (C5), not from sampled jump histories. The phase curve is evaluated from the exact stationary cavity spectrum. The comparison therefore tests algebraic and integration consistency, not the ability to infer an unknown model from finite noisy records.

## 9.3. Size refinement and verification

Keeping $a$, $\gamma$, $T$, and the center curve fixed, recalibrate each cavity size once in its own inertial preparation. The acceleration-dependent phase deficit decreases as follows:

| Cavity length $L$ | $\epsilon$ | Phase deficit at $T=5$ |
| ---: | ---: | ---: |
| 0.40 | 0.08 | 0.007712573727 |
| 0.20 | 0.04 | 0.001925669257 |
| 0.10 | 0.02 | 0.000481263165 |
| 0.05 | 0.01 | 0.000120306165 |

**Table 2.** Refinement in the prescribed ideal-boundary family. Halving $L$ reduces the leading deficit by a factor of four. This confirms the analytical $L^2$ behavior of (K7), with no claim about microscopic binding or a finite energetic construction cost.

The accompanying program also reconstructs 200 seeded positive matrices from analyzer means, compares congruence with its explicit Lorentz coordinate action, checks determinant and metric preservation, completes each filter with its failure outcome, verifies the marker fringe, and compares the cavity frequency with an independently integrated null round trip. Algebraic residuals are below $7\times10^{-15}$ in the stated sweep. A numerical solution of the driven master equation differs from (B1) by less than $2.3\times10^{-12}$ on 501 test points. Assertions use tolerances $10^{-10}$ for the finite algebraic checks and $10^{-9}$ for that ODE comparison.

The program includes a nonaffinity witness for normalized filtering, noncommuting boosts, and a pure-frame loop that closes to identity. Passing these checks confirms implementation of the stated identities. It does not test a universal observer transformation, a shared autonomous clock law, a manifold limit, gravitational response, or a physical spectrum. No Monte Carlo error bars are appropriate for these deterministic outputs.

# 10. Conditions for a common operational metric {#sec-geometry}

## 10.1. An intensity cone is not an interval field

The coordinate $x^a$ of $X$ has an operational intensity meaning from Section 3. A tangent displacement has different units and a different transformation obligation. Even a reliable four-current would not determine the metric: one timelike vector field supplies neither a complete coframe nor all null directions.

Suppose a future model produces a smooth four-dimensional region $M$ and a real-linear isomorphism at each point,

$$
\Theta_p:T_pM\longrightarrow\operatorname{Herm}(2),\qquad
\Theta(v)=e^0(v)I+\sum_{i=1}^3e^i(v)\sigma_i,
\tag{G1}
$$

with four linearly independent one-forms $e^a=e^a{}_{\mu}dx^\mu$. Their values have units of length after calibration. Equation (G1) is a coframe, not the intensity operator $X$. An operational model must derive how signal and clock comparisons identify this map, rather than copy intensity coordinates into it by notation.

**Proposition G1 (conditional metric construction).** Assume (G1), a specified time orientation, and the identification of future causal tangent directions with the positive semidefinite cone of $\Theta$. Then

$$
g(v,v)=-\det\Theta(v),\qquad
 g_{\mu\nu}=\eta_{ab}e^a{}_{\mu}e^b{}_{\nu},
\quad \eta=\operatorname{diag}(-1,1,1,1)
\tag{G2}
$$

defines a Lorentzian metric. Local changes $\Theta\mapsto A\Theta A^\dagger$ with $A\in SL(2,\mathbb C)$ preserve it. A positive rescaling $\Theta\mapsto\Omega\Theta$ gives $g\mapsto\Omega^2g$ and preserves its null cone.

*Proof.* Equation (L1) and the invertible coframe give a nondegenerate quadratic form of signature $(-,+,+,+)$. Its polarization defines the bilinear metric. Determinant preservation proves the frame statement, and the determinant's degree two gives conformal scaling. $\square$

The proposition is a construction conditional on a coframe and its physical interpretation. It does not infer a tangent bundle from a causal circuit. Manifold approximation is a separate nontrivial issue in causal approaches to geometry [8].

## 10.2. What calibration must fix

In a tangent space of dimension at least three, two Lorentzian quadratic forms with the same null cone are proportional. An elementary argument in four dimensions makes the limitation explicit. Choose coordinates in which one form is $-(v^0)^2+|\mathbf v|^2$. The other must vanish on every $(1,\mathbf n)$ with $|\mathbf n|=1$. Comparing $\mathbf n$ and $-\mathbf n$ eliminates all mixed time-space terms. Constancy of the remaining spatial quadratic form on the unit sphere makes it a scalar multiple of the identity, with the time coefficient fixed by the null condition. Matching signature and time convention makes the proportionality positive.

Consequently, ideal null directions determine a conformal class, not its scale. At each point, one independently calibrated nonzero timelike reading fixes the remaining positive factor *if* all clock species couple to the same quadratic form. In a supplied coordinate parameter $\lambda$,

$$
\frac{d\tau}{d\lambda}
=\frac{1}{c_0}\sqrt{-g_{\mu\nu}
\frac{dx^\mu}{d\lambda}\frac{dx^\nu}{d\lambda}}.
\tag{G3}
$$

For an actual finite clock $A$, a more appropriate hypothesis is

$$
\frac{d\tau_A}{d\lambda}
=\frac{d\tau}{d\lambda}\,[1+\delta_A],
\tag{G4}
$$

where $\delta_A$ is independently predicted from size, state, acceleration, and environmental response. The cavity control gives $\delta_A=f(\epsilon)-1$ in its stated regime. The count control fails the corresponding mean-curve comparison by (C6), without representing an individual bound clock.

A geometry cannot be validated by defining a separate conformal factor from each device on each trajectory. Calibrate device parameters on separate histories, then test whether the corrected comparisons share one $g$. A residual species-dependent leading rate that cannot be removed by established device physics would obstruct the universal metric hypothesis. A demonstrated finite-size correction that vanishes in a controlled regime has a different status.

A physical volume measure could also constrain scale, but raw reception counts are source- and detector-dependent. Identifying counts with spacetime volume would require an additional universal sampling law. Neither finite records nor intensity tomography supplies one.

## 10.3. The operational reconstruction target

A successful next model must produce a manifold-like regime, enough independent probes to resolve the local cone, controlled finite delays and response latencies, and recurrent subsystems that supply compatible scale calibration. It must also explain why different physical modes have a common characteristic cone. One optical mode on a prescribed background does not establish that universality.

Reconstruction should be assessed on held-out records. A fit uses one shared coframe and declared nuisance parameters for source and apparatus. It then predicts new clock comparisons and exchange histories, including non-collinear preparations and changing motion. Residual coordinate and local Lorentz freedoms are representation choices; unsupported freedom to retune a clock law is not.

Nothing in (G1)-(G4) selects a Levi-Civita connection, gravitational field equations, or the number of physical gravitational polarizations. Torsion, nonmetricity, and physical transport require their own derivation. The pure-frame identity (L8) remains a control against mistaking local basis changes for curvature.

# 11. Logarithmic states, entropy, and the modular boundary {#sec-entropy}

The positive-matrix construction gives a precise connection to the logarithms used in Part I's information analysis. For the faithful normalized state (L5),

$$
\ln\rho_S=h\,\mathbf n\cdot\boldsymbol\sigma
-\ln(2\cosh h)I,
\qquad
K_S=-\ln\rho_S.
\tag{M1}
$$

Its dimensionless entropy is

$$
s(\rho_S)=\ln(2\cosh h)-h\tanh h.
\tag{M2}
$$

These identities connect the statistical polarization coordinate to eigenvalue contrast and distinguishability. They do not imply that rapidity is entropy production. An anisotropic state can be stationary, and the two-state hazard process can satisfy detailed balance despite a nonzero log ratio [1,3].

For a faithful reference $\rho_0$, Part I's relation remains

$$
D(\rho\Vert\rho_0)
=\Delta\langle-\ln\rho_0\rangle-\Delta s\geq0.
\tag{M3}
$$

This is an information constraint before a physical energy normalization is supplied. If the reference is independently known to be a Gibbs state, its logarithm can be related to a Hamiltonian and temperature. That identification is additional physics.

There is also a simple obstruction to identifying the finite signal-state logarithm directly with a Lorentz boost. With the explicitly chosen modular convention

$$
\sigma_s(O)=\rho_S^{is}O\rho_S^{-is},
\tag{M4}
$$

(M1) gives

$$
\sigma_s(O)=e^{ish\mathbf n\cdot\boldsymbol\sigma}
Oe^{-ish\mathbf n\cdot\boldsymbol\sigma}.
\tag{M5}
$$

For real $s$, this is unitary conjugation: it rotates qubit observables around $\mathbf n$ and leaves $\rho_S$ fixed. It is not the positive nonunitary boost congruence $X\mapsto e^{\xi\mathbf n\cdot\boldsymbol\sigma/2}Xe^{\xi\mathbf n\cdot\boldsymbol\sigma/2}$. At $h=0$ it is trivial, and for a nonfaithful pure state (M1) is not a finite logarithm on the full two-dimensional space.

The architecture's proposed modular-geometric connection must therefore concern a richer observable algebra and state, with spacetime localization and an appropriate continuum limit. It does not follow from the common appearance of logarithms in (L4) and (M1). The thermal-time proposal [9] provides a broader hypothesis about algebraic states and flow; applying it to Signal Space requires the missing geometric and dynamical structure. The finite result here identifies a boundary condition for that work.

Likewise, Fisher information describes precision in a statistical parameter space. Its positive quadratic form is not the Lorentzian interval metric of (G2). Relative entropy and inference geometry remain useful without being assigned the role of spacetime by definition.

# 12. Architectural consequences and the next physical step {#sec-discussion}

The revised architecture gains a concrete interface from the two-component construction. Part I's channel coherences can be measured together with intensity, their positive operator has a complete cone representation, and the diagonal response specialization preserves the known rapidity identity. The explanatory benefit is a common operator language. The cost is the selected two-component sector, a calibrated measurement model, and an observer-comparison law that remains to be physically justified.

Three gaps should remain visible when extending the paper sequence. First, a Lorentz action on signal data is not yet a universal spacetime action on all modes. Second, a recurrence is not an ideal clock merely because it can be assigned a phase. Third, separately correct geometric and clock controls do not select a shared autonomous dynamics. These are substantive completion criteria, not editorial qualifications that can be removed from later drafts.

The count obstruction makes the phase-clock branch more precise. A simple phase label on the old reversal process cannot universally reproduce the nonlinear proper time of its mean curve. A confined mode instead has a recurrence set by its propagation and boundary conditions, with a calculable finite-size response. This is a useful existence control on supplied geometry. The boundary support that confines it remains external. Recovering binding, recoil, excitation energy, and recurrence from one reception law is the next physical task.

Accordingly, *Autonomous Geometric Phases*, the provisional Part III of [2], should select one regulated local evolution and retain its parameter ledger. It must identify a stationary state or vacuum, propagating modes, recurrent composites, and the regime in which operational comparisons support a common cone. Dimension and Lorentz symmetry require independent continuum diagnostics; a four-dimensional cone already inserted into each local channel is not dimension selection. Causal scheduling consistency from Part I should survive, but it does not replace a demonstration of physical locality or covariance.

There are useful failure branches. If the two-component intensity comparison is not observer-covariant, it can remain an internal signal-state description while geometry is inferred from exchanges or a covariant transport measure. If phase clocks retain uncontrollable state-dependent errors, the candidate must explain their correction or adopt another recurrent subsystem. If different modes retain different leading cones, the model has not recovered universal Lorentzian spacetime. A controlled analogue remains publishable when accurately classified, but it should not be presented as completion of the universal theory.

The constants program is not advanced by fixing units in the present benchmark. The supplied $c_0$, rate scale $\gamma$, cavity size $L$, and acceleration $a$ are independent inputs. Their dimensionless combination $aL/c_0^2$ controls a response within a known reference geometry. The cavity's discrete mode spectrum is boundary-induced; it is not an infinite-volume mass gap. No Planck scale, gravitational coupling, gauge coupling, or particle-mass ratio has been calculated. Those targets require the common physical normalization and autonomous sectors specified in the architecture.

The immediate empirical obligation is also clear. The calculations here reproduce consequences of their inputs. New physical content would arise from a selected Signal Space dynamics that constrains previously independent quantities, such as response hazards, coherent phase evolution, binding size, and probe transport. Such a relation could be calibrated on a subset of observations and then tested elsewhere. The present manuscript supplies definitions and controls needed to make that future comparison meaningful.

# 13. Conclusion {#sec-conclusion}

A two-component reception sector admits an operationally reconstructed positive intensity operator whose standard determinant geometry is a Lorentz cone. Its logarithmic coordinate extends the diagonal hazard ratio, while its full congruence action supplies non-collinear Lorentz algebra. Intensity reconstruction, response dynamics, and observer covariance nevertheless remain distinct requirements.

Independent echoes make this distinction testable. The earlier stationary count-clock identity persists only under its response and equilibrium assumptions; its nonstationary excess cannot be removed for every ensemble state by fixed local additive rewards. A confined coherent mode supplies a different clock mechanism with an exact, size-dependent calibration error on prescribed constant-acceleration boundaries. The executed control separates that error from statistical relaxation and retains Part I's accounting of coherence and records.

The conditional coframe construction specifies the remaining bridge to geometry: a common physical cone, a manifold-like regime, and independently calibrated recurrent subsystems. These results prepare a definite autonomous-model problem while preserving the architecture's central requirement that clocks, geometry, and matter ultimately follow from the same dynamics.

# Data and code availability {#sec-availability}

The accompanying source package contains separate section files with stable equation identifiers, an assembled Markdown manuscript, a PDF build script, the deterministic verification program, its machine-readable results, the generated figure, a claim ledger, an architecture review, and revision instructions. No external dataset is used. The verification program records software versions and the random seed used for matrix generation. All benchmark values are synthetic. Authorship, affiliations, disclosures, and venue-specific declarations must be supplied by the submitting author; this manuscript asserts no institutional endorsement or external peer review.

# References {#sec-references}

1. Signal Space project manuscript. *Composition of Signal Histories: Signal Space Foundations, Part I: Causal Operations, Coherence, and Records*. 11 September 2026, version 0.1.0. Unpublished. Source: `Signal_Space_Part_I_Composition_of_Signal_Histories.md`.

2. Signal Space project memorandum. *Signal Space: A fresh architecture for a full physical theory*. 11 September 2026. Unpublished. Supplied source: `Signal_Space_Full_Theory_Research_Architecture-1.md`. The memorandum supersedes the earlier metric-first memo as the statement of full-theory scope.

3. Signal Space project manuscript. *Reception-Driven Clocks: Calibration, Memory, and Observable Dynamics in One Dimension*. Earlier Signal Space Paper III, complete first draft, 8 September 2026. Unpublished. Source: `Signal_Space_Paper_III_Full_Draft.md`. Inherited results are attributed to this manuscript; its earlier simulations are not reported as new runs here.

4. F. Verstraete, J. Dehaene, and B. De Moor. “Local filtering operations on two qubits.” *Physical Review A* **64**, 010101(R) (2001). [Author preprint](https://arxiv.org/abs/quant-ph/0011111). See also the same authors, “The Lorentz singular value decomposition and its applications to pure states of 3 qubits,” *Physical Review A* **65**, 032308 (2002). [Author preprint](https://arxiv.org/abs/quant-ph/0108043).

5. C. E. Dolby and S. F. Gull. “Radar Time and a State-Space Based Approach To Quantum Field Theory In Gravitational and Electromagnetic Backgrounds.” Preprint (2002). [Author preprint](https://arxiv.org/abs/gr-qc/0207046).

6. J. Lindkvist, C. Sabín, I. Fuentes, A. Dragan, I.-M. Svensson, P. Delsing, and G. Johansson. “Twin paradox with macroscopic clocks in superconducting circuits.” Preprint submitted 2013. [Author preprint](https://arxiv.org/abs/1401.0129).

7. J. Lindkvist, C. Sabín, G. Johansson, and I. Fuentes. “Motion and gravity effects in the precision of quantum clocks.” Preprint (2014). [Author preprint](https://arxiv.org/abs/1409.4235).

8. S. Surya. “The causal set approach to quantum gravity.” *Living Reviews in Relativity* **22**, 5 (2019). [Author preprint](https://arxiv.org/abs/1903.11544).

9. A. Connes and C. Rovelli. “Von Neumann algebra automorphisms and time-thermodynamics relation in general covariant quantum theories.” *Classical and Quantum Gravity* **11**, 2899-2918 (1994). [Author preprint](https://arxiv.org/abs/gr-qc/9406019).
