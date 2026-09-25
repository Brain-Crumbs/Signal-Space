# Signal Space operator models and experimental program

**Version:** 0.2  
**Date:** 24 September 2026  
**Revision focus:** directional propagation, drift, and alternative geometric interpretations remain explicit hypotheses to discriminate, not exclusions imposed in advance.  
**Purpose:** extend the Operator Foundations Roadmap into explicit candidate theories, derivations, physical interpretations, and discriminating experiments.  
**Status:** analytical model construction and experiment design. No new nonlinear evolution or empirical measurement is reported.

## 1 What this construction accomplishes

The operator foundation can be developed into working mathematical models. It does not determine a unique physical theory. In particular, a Lorentzian determinant on an internal vector space does not, by itself, tell disturbances where to propagate.

The missing ingredient is a **relation between internal operators and changes between events**. This document develops that relation in two ways.

| Candidate | Defining law | What is already supplied | What follows from the stated law | Principal open question |
|---|---|---|---|---|
| **A Local projector scattering** | A reciprocal Hamiltonian interaction between incoming complex states and a carried projector memory | Event incidence, port routing, a symplectic structure, and coupling constants | Closed local evolution, norm and local matrix-charge conservation, and a calculable propagation operator | Can a self-consistent background make all relevant excitations and clocks share a geometry? |
| **B Dynamical operator coframe** | A local action for an operator-valued coframe, complex matter, a neutral signal, and a trapped clock field | A four-dimensional differentiable domain, universal metric coupling, and Einstein curvature dynamics | A dynamical metric, common principal characteristics, charge-supported object ansätze, and an explicit local clock/readout mechanism | Can these geometric assumptions eventually be derived from a more primitive event theory? |

**Candidate B is the complete classical continuum theory proposed here:** its fields, action, equations, constraints, and initial-value interpretation are specified. Its localized clock construction has an analytical existence criterion in a controlled limit. Particular stable finite-amplitude solutions still require calculation.

**Candidate A is a complete local event model once an incidence circuit is specified.** Its three-direction propagation benchmark is an additional circuit ansatz. It does not yet provide a universal spacetime, autonomous physical clocks, or a derivation of that circuit.

These are alternative research models, not proven microscopic and macroscopic descriptions of the same system. No coarse-graining map between them has been established.

**Revised research question:** can local operator dynamics generate a coherent causal geometry, including drift and directional anisotropy, and explain how signals, objects, and clocks relate to it?

Equal coordinate speeds in opposite directions are not required. Nor is a common characteristic cone for every material excitation a prerequisite for investigating emergent spacetime. The stronger claim of a universal cone remains one hypothesis. A geometric signal sector with additional material response, or several effective characteristic structures, must be classified and tested separately. Sections 6.5 and 11.1 develop the drift possibility; Test 11 discriminates these alternatives.

The most useful new conclusions are:

1. Four suitably chosen rank-one projectors can form a basis of the four-dimensional Hermitian operator space and generate a Lorentzian Gram matrix.
2. Turning that algebra into physical geometry requires a map from event displacements or derivatives into that space.
3. A reciprocal projector interaction can be written without a preassigned metric. Its actual propagation must then be calculated.
4. A common metric and readable clocks can coexist in a closed continuum model without the old quartic orientation term.
5. Spatial knot stabilization and technical relative locality remain separate additions with their own tests.

Throughout, **identity** means a mathematical consequence of definitions; **ansatz** means a proposed physical assumption or restricted solution form; **derived** means a consequence of a stated ansatz or action; and **open** means not established here.

## 2 The operator constitution

### 2.1 Complex states and projectors

Let $\mathcal H=\mathbb C^2$ be a complex two-dimensional vector space with its usual positive inner product. A dagger denotes Hermitian conjugation. A nonzero state $z\in\mathcal H$ defines

$$
\rho=z^\dagger z,\qquad
u=\frac{z}{\sqrt{\rho}},\qquad
P=uu^\dagger.
$$

Here $\rho>0$ is the state weight, $u$ is a unit vector, and $P$ is its rank-one Hermitian projector:

$$
P^\dagger=P,\qquad P^2=P,\qquad \operatorname{tr}P=1.
$$

The phase of $u$ disappears from $P$. Consequently, retaining $P$ alone discards information that can affect interference with a second state.

The three Pauli matrices are

$$
\sigma_1=\begin{pmatrix}0&1\\1&0\end{pmatrix},\quad
\sigma_2=\begin{pmatrix}0&-i\\i&0\end{pmatrix},\quad
\sigma_3=\begin{pmatrix}1&0\\0&-1\end{pmatrix}.
$$

The symbol $I$ denotes the $2\times2$ identity. They obey

$$
\sigma_i\sigma_j=\delta_{ij}I+i\epsilon_{ijk}\sigma_k,\qquad
\operatorname{tr}(\sigma_i\sigma_j)=2\delta_{ij}.
$$

Indices $i,j,k$ run from 1 to 3; $\delta_{ij}$ is the Kronecker delta and $\epsilon_{ijk}$ the antisymmetric symbol with $\epsilon_{123}=1$. Repeated indices are summed unless a sum is displayed.

Every rank-one projector is

$$
P=\frac12(I+\mathbf n\cdot\boldsymbol\sigma),\qquad
n_i=u^\dagger\sigma_i u,\qquad |\mathbf n|=1.
$$

The vector $\mathbf n$ is a direction in an internal real three-dimensional space. It is not yet a direction in physical space.

**Interpretation.** A complex state contains a weight, a ray orientation, and a phase. These need not become mass, spatial direction, and time respectively. Those identifications must survive the dynamics and measurement tests.

### 2.2 Two exact geometries on the same operator space

Let $\mathcal J=\operatorname{Herm}(2,\mathbb C)$, a four-dimensional real vector space. For $X,Y\in\mathcal J$, write

$$
X=x^0I+x^i\sigma_i,\qquad Y=y^0I+y^i\sigma_i.
$$

The real coefficients are $x^0=\operatorname{tr}X/2$ and $x^i=\operatorname{tr}(X\sigma_i)/2$, with analogous definitions for $Y$.

Define the trace form $h$ and determinant polarization $\mathfrak g$ by

$$
h(X,Y)=\frac12\operatorname{tr}(XY),
$$

$$
\mathfrak g(X,Y)=
\frac12\left[\operatorname{tr}X\,\operatorname{tr}Y-\operatorname{tr}(XY)\right].
$$

The Pauli identities immediately give

$$
h(X,Y)=x^0y^0+\mathbf x\cdot\mathbf y,
$$

$$
\mathfrak g(X,Y)=x^0y^0-\mathbf x\cdot\mathbf y,
\qquad \mathfrak g(X,X)=\det X.
$$

We use $\mathfrak g$ for this internal algebraic form and reserve $g_{\mu\nu}$ for a physical spacetime metric in Candidate B.

The symmetric product $X\circ Y=(XY+YX)/2$ remains Hermitian. The commutator $[X,Y]=XY-YX$ supplies additional noncommutative information. Symmetric observables do not require discarding the commutator from dynamics.

**Interpretation.** Euclidean and Lorentzian forms coexist because they measure different algebraic relations. The trace form compares operators using the chosen Hilbert inner product. The determinant distinguishes the two eigenvalue directions. Neither identity establishes a propagation law. The standard spinor/projective/Lorentz correspondence is discussed in [R1].

### 2.3 Rank and positivity

| Object in $\mathbb C^2$ | Space of possibilities | What its rank does and does not say |
|---|---|---|
| Rank-zero projector | Only $0$ | No state direction |
| Rank-one projector | $\mathbb{CP}^1\simeq S^2$ | A ray and an algebraic null direction |
| Rank-two projector | Only $I$ | Does not parameterize a timelike cone |
| Positive rank-two Hermitian operator | Two positive eigenvalues with variable eigenvectors | Lies inside the future determinant cone |
| General rank-two Hermitian operator | Eigenvalues may have either sign | Can be timelike or spacelike |

A weighted construction

$$
J=\sum_a \rho_a P_a
$$

uses projectors $P_a$ and nonnegative weights $\rho_a$. It produces a positive operator, usually not a projector. Signed weights are needed to span arbitrary Hermitian directions with a spectral decomposition.

A continuous family of exact finite-dimensional projectors cannot continuously change rank: its trace is an integer and is continuous. Neither candidate below includes unexplained rank jumps.

## 3 Observers from weighted local states

### 3.1 A local aggregate supplies a candidate observer

Suppose several states have actually been brought to the same event and expressed in the same local frame. Their positive aggregate is

$$
J=\sum_a z_a z_a^\dagger.
$$

For two states, direct determinant expansion gives

$$
\det J
=\rho_1\rho_2\left(1-|u_1^\dagger u_2|^2\right)
=\frac{\rho_1\rho_2}{2}(1-\mathbf n_1\cdot\mathbf n_2).
$$

More generally,

$$
\det J=\sum_{a<b}\rho_a\rho_b
\left(1-|u_a^\dagger u_b|^2\right).
$$

Thus nonparallel positive constituents can produce a timelike aggregate. Where $\det J>0$, define

$$
T=\frac{J}{\sqrt{\det J}},\qquad \det T=1.
$$

$T$ is a positive observer candidate. If all nonzero constituents are collinear, $J$ has rank one and this normalization fails. A single ray does not define a rest frame.

This is an algebraic construction from local data. Calling $\sqrt{\det J}$ a physical rest energy would require showing that $J$ has the appropriate conserved energy-momentum role. Candidate A does not establish that identification.

### 3.2 Observer-dependent Euclidean measurements

For such $T$, define

$$
h_T(X,Y)=2\mathfrak g(T,X)\mathfrak g(T,Y)-\mathfrak g(X,Y).
$$

To prove positivity, use $S=T^{-1/2}$, for which $\det S=1$ and $STS^\dagger=I$. Congruence by $S$ preserves $\mathfrak g$. In that frame,

$$
h_T(X,X)=h(SXS^\dagger,SXS^\dagger)>0
$$

for nonzero $X$. The three-dimensional plane $\mathfrak g(T,X)=0$ has spatial metric $-\mathfrak g$.

A positive spinor norm associated with this observer is

$$
\|z\|_T^2=z^\dagger T^{-1}z
=2\mathfrak g(T,zz^\dagger).
$$

The last equality follows because the adjugate of $T$ is $T^{-1}$ when $\det T=1$.

**Interpretation.** The observer is a timelike aggregate, while its spatial measurements are a slice orthogonal to that aggregate. This supplies a candidate local measurement geometry. It still does not supply a clock rate or a relation between different events.

### 3.3 Frame changes and actual transport

A unitary basis change $V$ acts as

$$
z\mapsto Vz,\quad P\mapsto VPV^\dagger.
$$

It preserves both ordinary normalization and projector idempotence.

A Lorentz spin-frame transformation $S\in SL(2,\mathbb C)$ acts on weighted Hermitian operators as

$$
J\mapsto SJS^\dagger,\qquad T\mapsto STS^\dagger.
$$

It preserves determinants. It generally does not preserve an ordinary normalized projector. If $J=\rho P$, the transformed normalized decomposition is

$$
c=\operatorname{tr}(SPS^\dagger),\qquad
P'=\frac{SPS^\dagger}{c},\qquad \rho'=c\rho.
$$

The weight transformation is essential. Unitary basis covariance alone is not Lorentz covariance.

For two different events, a comparison map must be supplied. If $U_{AB}$ transports a state from B to A, independent unitary changes of local bases give

$$
U_{AB}\mapsto V_AU_{AB}V_B^\dagger.
$$

For unit-normalized states, an invariant overlap is

$$
\mathcal O_{AB}=|u_A^\dagger U_{AB}u_B|^2.
$$

For a general spin-frame comparison, use the detector's positive form $T_A^{-1}$ after transporting both states to A. Comparisons then remain invariant when states, observer, and transport transform together.

**Interpretation.** A frame change modifies the description. A physical change of a transport map with endpoint states held fixed can modify the measured overlap. These are distinct operations.

## 4 The missing bridge between internal and physical geometry

### 4.1 Why internal symmetry cannot select propagation by itself

The same state space admits zero dynamics, onsite phase rotation, diffusion, reversible exchange, and wave propagation. Each can be written with basis-invariant scalar combinations.

Therefore the internal algebra alone does not determine:

- Which events can interact.
- Which derivative or event difference corresponds to an internal Hermitian direction.
- Which action governs those relations.

Any proposed derivation must expose these three choices. In Candidate A they are the incidence circuit, its routing, and a local Hamiltonian. In Candidate B they are a differentiable domain, an operator coframe, and a local action.

### 4.2 Four projectors can supply a Lorentzian basis

Choose four internal unit vectors

$$
\begin{aligned}
\mathbf n_1&=(1,1,1)/\sqrt3,&
\mathbf n_2&=(1,-1,-1)/\sqrt3,\\
\mathbf n_3&=(-1,1,-1)/\sqrt3,&
\mathbf n_4&=(-1,-1,1)/\sqrt3.
\end{aligned}
$$

They point toward the vertices of a regular tetrahedron and obey

$$
\mathbf n_A\cdot\mathbf n_B=-\frac13\quad(A\ne B),
\qquad \sum_A\mathbf n_A=0.
$$

Capital indices $A,B$ in this section run from 1 to 4. Define

$$
P_A=\frac12(I+\mathbf n_A\cdot\boldsymbol\sigma).
$$

Then

$$
\mathfrak g(P_A,P_B)=\frac{1-\mathbf n_A\cdot\mathbf n_B}{4}
=
\begin{cases}
0,&A=B,\\
1/3,&A\ne B.
\end{cases}
$$

The resulting Gram matrix has eigenvalues

$$
1,\quad-\frac13,\quad-\frac13,\quad-\frac13.
$$

The projectors are linearly independent over the reals and span $\mathcal J$. Every basis element is null, while their combinations support the entire Lorentzian space.

**Interpretation.** Three spatial algebraic directions do not require three independent primitive spatial axes. They can arise from relations among four null projector directions. This is a basis construction, not a derivation of four-dimensional physical spacetime or a distinguished physical tetrahedron.

### 4.3 The operator coframe ansatz

On a proposed four-dimensional event domain, introduce four independent real one-forms $\vartheta^A$. A one-form assigns a real number to an infinitesimal displacement. Define the Hermitian matrix-valued one-form

$$
E=\sum_{A=1}^4P_A\vartheta^A.
$$

For tangent displacements $v,w$, propose

$$
g(v,w)=\mathfrak g(E(v),E(w)).
$$

In coordinates $x^\mu$, with $\mu=0,1,2,3$,

$$
E=E_\mu dx^\mu=e^a{}_\mu\sigma_a dx^\mu,\qquad
\sigma_0=I,
$$

$$
g_{\mu\nu}=\mathfrak g(E_\mu,E_\nu)
=\eta_{ab}e^a{}_\mu e^b{}_\nu,\qquad
\eta_{ab}=\operatorname{diag}(1,-1,-1,-1).
$$

Lowercase Latin indices $a,b=0,1,2,3$ now label the four operator-basis components. The coefficients $e^a{}_\mu$ are a coframe, also called a tetrad. Its inverse is $e_a{}^\mu$, satisfying $e_a{}^\mu e^a{}_\nu=\delta^\mu{}_\nu$.

For the tetrahedral parameterization,

$$
e^0=\frac12\sum_A\vartheta^A,\qquad
e^i=\frac12\sum_A n_A^i\vartheta^A,
$$

$$
ds^2=\frac23\sum_{A<B}\vartheta^A\vartheta^B.
$$

In the last expression the one-forms are evaluated on the same displacement; the metric tensor uses their symmetric products. The coefficients $\vartheta^A(v)$ can have either sign. Requiring all such coefficients to be positive for every displacement would incorrectly exclude spacelike directions.

If the coframe is invertible, the metric has signature $(+---)$. No fixed spacetime metric was used to choose its local lengths, but a four-dimensional domain and the coframe map have been assumed.

An internal transformation $E\mapsto SES^\dagger$ leaves $g$ unchanged. Renormalizing the transformed $P_A$ requires compensating changes in $\vartheta^A$. The tetrahedral basis can be regarded as a frame choice; it does not add four physical preferred null directions.

**Interpretation.** This is the precise bridge missing from a bare determinant analogy: an actual displacement is mapped into an operator, and the determinant measures that displacement. Its physical credibility depends on the action and on whether actual disturbances and clocks obey the same metric.

## 5 Candidate A Local projector scattering

**Model identifier:** SS OPS 1.

### 5.1 Primitive data and locality

Assume an oriented incidence circuit. Each elementary event receives two complex states $z_1,z_2\in\mathbb C^2$ and a carried memory state $w\in\mathbb C^2$ with $w^\dagger w=1$. Outputs are passed to later events along specified ports. Repeated operations are represented by an unfolded causal history, not by circular instantaneous dependencies.

An edge carries a specified unitary transport map. For the simplest benchmark these maps are flat: in one global trivialization they are all the identity. Independent local basis changes are still allowed if all edge maps are transformed.

The incidence circuit supplies direct interaction opportunities. It supplies no physical lengths. It is an assumption and is not inferred by an all-pairs overlap search.

At an event all inputs are first expressed in its local frame. Define

$$
P=ww^\dagger,\qquad
d=z_1-z_2,\qquad
N=z_1^\dagger z_1+z_2^\dagger z_2.
$$

$P$ is the local memory projector, $d$ the difference of the incoming amplitudes, and $N$ their total weight.

### 5.2 Hamiltonian ansatz and equations

Use a dimensionless event parameter $s\in[0,1]$. It parameterizes a gate; it is not a derived proper time. Take the real event Hamiltonian

$$
\mathcal H_e=\kappa d^\dagger P d+\frac{\lambda}{2}N^2,
$$

where $\kappa$ and $\lambda$ are real dimensionless couplings, fixed as part of the model.

This is motivated by three explicit choices: only participants interact; the coupling measures a difference selected by a projector; and the memory responds reciprocally. It is not the unique invariant interaction. The second term supplies a simple nonlinear phase response and can be set to zero.

For any participant $q\in\{z_1,z_2,w\}$, choose canonical complex Hamiltonian evolution

$$
i\frac{dq}{ds}=\frac{\partial\mathcal H_e}{\partial q^\dagger}.
$$

It follows that

$$
\begin{aligned}
i\dot z_1&=\kappa P(z_1-z_2)+\lambda N z_1,\\
i\dot z_2&=-\kappa P(z_1-z_2)+\lambda N z_2,\\
i\dot w&=\kappa dd^\dagger w.
\end{aligned}
$$

A dot in Candidate A denotes differentiation with respect to $s$ only. These are finite-dimensional, smooth, closed equations. Their exact time-one flow defines the event. Norm conservation bounds the variables and prevents finite-gate blowup.

The symplectic structure and the Hamiltonian are additional physical assumptions. Merely specifying projectors would not have fixed either.

### 5.3 Conservation and reciprocal response

Because the generators are Hermitian,

$$
\frac{dN}{ds}=0,\qquad
\frac{d(w^\dagger w)}{ds}=0.
$$

The projector remains rank one. Its evolution is

$$
\dot P=-i\kappa[dd^\dagger,P].
$$

Define the event matrix charge

$$
J_e=z_1z_1^\dagger+z_2z_2^\dagger+P.
$$

Differentiation yields

$$
\frac{d}{ds}(z_1z_1^\dagger+z_2z_2^\dagger)
=-i\kappa[P,dd^\dagger],
$$

which cancels $\dot P$. Thus

$$
\dot J_e=0.
$$

The event Hamiltonian is also conserved during that event. A routed circuit does not automatically have a single conserved physical energy. With flat transport, the sum of matrix charges across a complete circuit cut is conserved; for general holonomy there is no frame-independent sum of distant matrices without further structure.

**Interpretation.** The wave can change the projector, and the projector can redirect the wave. The matrix ledger records the reciprocal exchange. This is stronger than prescribing a projector texture and letting a wave respond to it. It is not yet momentum conservation or mechanical recoil in an emergent space.

### 5.4 Event composition

Events acting on disjoint participants commute. Any two topological orderings of the same causal circuit therefore give the same exact records: they differ only by swaps of independent events.

Events sharing a state or a memory generally do not commute. Their order is physical incidence data and cannot be shuffled as a gauge freedom.

Every update uses participants present at the event. No update reads a distant simultaneous state. This supplies an explicit form of elementary locality before distance has been defined.

### 5.5 A projector router as a controlled limit

Freeze $P$ temporarily, set $\lambda=0$, and choose $\kappa=\pi/2$. Define symmetric and antisymmetric port states

$$
z_+=\frac{z_1+z_2}{\sqrt2},\qquad
z_-=\frac{z_1-z_2}{\sqrt2}.
$$

The equations give $\dot z_+=0$ and $i\dot z_-=2\kappa Pz_-$. At $s=1$,

$$
z_-\mapsto(I-2P)z_-.
$$

Returning to the original ports,

$$
\begin{pmatrix}z_1'\\z_2'\end{pmatrix}
=
\begin{pmatrix}I-P&P\\P&I-P\end{pmatrix}
\begin{pmatrix}z_1\\z_2\end{pmatrix}.
$$

The component selected by $P$ swaps ports; its complement stays. The block matrix is exactly unitary and involutive.

In the full reciprocal model, $P$ is not frozen at finite amplitude. However, about $z_1=z_2=0$, its change is quadratic in wave amplitude. The frozen router is therefore the exact linearization of the event interaction about that vacuum.

**Interpretation.** Here the projector has an explicit operational role: it decides which part of an amplitude changes port. Propagation follows only after these ports are connected into a specified circuit.

## 6 Deriving a propagation cone in a circuit benchmark

### 6.1 The additional routing ansatz

For a controlled comparison, prescribe a periodic circuit with three pairs of opposite translation ports. Denote the three integer labels by $\mathbf m\in\mathbb Z^3$. Introduce conversion scales $\ell$ and $\tau_c$ for one label increment and one full circuit cycle. These are declared calibration scales, not predicted constants.

Each direction $i$ uses complementary projectors

$$
P_i^\pm=\frac12(I\pm\mathbf n_i\cdot\boldsymbol\sigma).
$$

In a homogeneous frozen-memory sector, project the amplitude onto two opposite outgoing ports, transport those components by one label, and recombine the complementary components. Equivalently, the conditional-shift block is

$$
(\mathcal S_i\psi)(\mathbf m)
=P_i^+\psi(\mathbf m-\hat{\mathbf e}_i)
+P_i^-\psi(\mathbf m+\hat{\mathbf e}_i),
$$

where $\psi$ is the transported complex amplitude and $\hat{\mathbf e}_i$ is a unit label step. Projector swap gates with explicit auxiliary ports can implement this routing. The conditional-shift block and the order of the three blocks are part of the benchmark specification.

For spatially variable or dynamical memories, this stencil must not simply be used with $P_i(\mathbf m)$ inserted: doing so generally destroys unitarity. The actual implementation must use the local reciprocal gate circuit and retain its memory and port variables.

### 6.2 Fourier calculation

For a Fourier mode $e^{i\ell\mathbf k\cdot\mathbf m}$, where $k_i$ is the wave number conjugate to label direction $i$,

$$
\mathcal S_i(\mathbf k)
=P_i^+e^{-i\ell k_i}+P_i^-e^{i\ell k_i}
=e^{-i\ell k_i\mathbf n_i\cdot\boldsymbol\sigma}.
$$

One ordered cycle is

$$
\mathcal U(\mathbf k)=
\mathcal S_3(\mathbf k)\mathcal S_2(\mathbf k)\mathcal S_1(\mathbf k).
$$

At small $|\mathbf k|\ell$,

$$
\mathcal U=I-i\tau_c B^ik_i+O(\ell^2|\mathbf k|^2),
\qquad
B^i=v\,\mathbf n_i\cdot\boldsymbol\sigma,\qquad
v=\ell/\tau_c.
$$

The leading continuum equation is

$$
i\partial_t\psi=-iB^i\partial_i\psi.
$$

For a mode $e^{i(\mathbf k\cdot\mathbf x-\omega t)}$, its principal determinant is

$$
\det(\omega I-B^ik_i)
=\omega^2-v^2G^{ij}k_ik_j,
\qquad G^{ij}=\mathbf n_i\cdot\mathbf n_j.
$$

Thus the actual linearized dynamics generates a candidate inverse metric

$$
g_A^{00}=1,\qquad g_A^{0i}=0,\qquad
g_A^{ij}=-v^2G^{ij}.
$$

If the three $\mathbf n_i$ are linearly independent, $G$ is positive definite and this principal form is Lorentzian. Orthogonal internal directions give an isotropic Weyl cone. Collinear directions give a degenerate spatial principal form, despite the unchanged underlying algebra $\operatorname{Herm}(2,\mathbb C)$.

**Interpretation.** This is a genuine dynamics-to-geometry calculation for one sector. The determinant cone becomes relevant because the generator of translations is itself a Hermitian matrix linear in wave number. The selected incidence, three-direction routing, and scale conversion remain assumed.

### 6.3 An exact finite-bandwidth prediction

For an orthonormal right-handed triad and the order written above, let $\omega$ be the principal quasifrequency near $\mathbf k=0$, defined by eigenvalues $e^{\mp i\omega\tau_c}$. Then

$$
\cos(\omega\tau_c)=
\cos(\ell k_1)\cos(\ell k_2)\cos(\ell k_3)
+\sin(\ell k_1)\sin(\ell k_2)\sin(\ell k_3).
$$

Reversing the three-block order changes the sign of the last term. Both orders have the same leading Weyl cone, but differ at finite wavelength.

This predicts a useful distinction: the circuit has exact finite causal support determined by its incidence, while its long-wavelength cone is an approximate collective description. They need not agree at the shortest scales. Inspect the full Brillouin zone for additional modes; this calculation does not evade lattice fermion-doubling issues or identify a single physical fermion species.

### 6.4 The present obstruction

At the zero-wave vacuum, the memory projectors have no linear restoring or spatial propagation law of their own:

$$
\delta\dot P=0
$$

during a gate at leading order. With memories attached to fixed circuit labels, their physical orientation perturbations are stationary modes. They do not share the wave sector's Weyl characteristics.

Therefore **Candidate A does not pass the strong hypothesis that every physical sector shares the wave cone about this vacuum**. Freezing these degrees of freedom would hide that failure. This does not rule out a geometric wave sector interacting with material memories. Such an interpretation must identify the memories' physical role, any preferred frame, and their clock and detector consequences.

A nonzero, self-consistent periodic background could change the coupled spectrum, but this must be derived from the complete event flow. It is not a license to fit a metric to the wave sector and assume every other degree of freedom follows it.

Related quantum-walk work establishes that suitable local unitary circuits can represent curved-space Dirac equations [R2]. That does not establish that this reciprocal circuit produces an autonomous gravitational geometry.

### 6.5 Directional propagation and drift remain viable

The zero mixed components $g_A^{0i}=0$ in Section 6.2 follow from that particular traceless router generator. They are not a restriction imposed by Hermitian operator geometry.

Suppose the continuum limit of a specified local law instead gives Hermitian generators

$$
B^i=v_{\rm d}^iI+b^i_a\sigma_a,\qquad
v_{\rm d}^i=\frac12\operatorname{tr}B^i,\qquad
b^i_a=\frac12\operatorname{tr}(B^i\sigma_a).
$$

Here $v_{\rm d}^i$ are real drift-velocity components, $b^i_a$ are real propagation coefficients, $i$ labels derivative directions, and $a=1,2,3$ labels Pauli matrices. They have velocity units when the coordinates have length and time units. The drift $v_{\rm d}^i$ is distinct from the scalar conversion speed $v=\ell/\tau_c$ in the earlier benchmark.

For a local Fourier covector $(\omega,\mathbf k)$, direct use of the Pauli determinant gives

$$
\boxed{
\det(\omega I-B^ik_i)
=(\omega-v_{\rm d}^ik_i)^2-D^{ij}k_ik_j,\qquad
D^{ij}=\sum_a b^i_a b^j_a.
}
$$

Thus **the identity components provide drift and the traceless components provide the spatial cone shape**. If $D$ is positive definite, this is a Lorentzian principal form. For the phase convention $e^{i(\mathbf k\cdot\mathbf x-\omega t)}$, one representative inverse metric has

$$
g_{\rm drift}^{00}=1,\qquad
g_{\rm drift}^{0i}=v_{\rm d}^i,\qquad
g_{\rm drift}^{ij}=v_{\rm d}^iv_{\rm d}^j-D^{ij}.
$$

It is determined only up to a nonzero conformal multiplier by the cone. An equivalent line element, up to a positive scale, is

$$
ds^2\ \propto\
dt^2-(D^{-1})_{ij}
(dx^i-v_{\rm d}^i dt)(dx^j-v_{\rm d}^j dt).
$$

The matrix $D^{-1}$ is the inverse of $D$. A positive-definite anisotropic $D$ still gives one metric. Different speeds along different coordinate axes do not establish several metrics.

For a one-dimensional constant-coefficient illustration, let $D=c^2$ with $c>0$. Then

$$
(\partial_t+v_{\rm d}\partial_x)^2\psi-c^2\partial_x^2\psi=0
$$

has characteristic velocities

$$
\frac{dx}{dt}=v_{\rm d}+c,\qquad
\frac{dx}{dt}=v_{\rm d}-c,
$$

and a metric representative

$$
\boxed{ds^2=c^2dt^2-(dx-v_{\rm d}dt)^2.}
$$

For $|v_{\rm d}|<c$, the forward and backward speed magnitudes are $c+v_{\rm d}$ and $c-v_{\rm d}$. They differ even though there is only one cone. This motivates testing asymmetric propagation rather than rejecting it.

For constant $v_{\rm d}$ and $c$, the coordinate change $x'=x-v_{\rm d}t$, $t'=t$ removes the cross term. It is a drift-coordinate change, not a Lorentz boost. Standard Lorentz-related inertial observers using the metric's calibrated clocks and rulers still measure the same local vacuum light speed [R11]. A physical background flow relative to a detector can have observable consequences; merely rewriting the same entire experiment in drift coordinates cannot.

If coefficients vary, derivatives of coefficients and connection or measure terms must be retained in the evolution. For example, with a flat spatial inner-product measure, a formally Hermitian first-order Hamiltonian includes

$$
-iB^i\partial_i-\frac{i}{2}(\partial_iB^i)
$$

plus allowed Hermitian lower-order terms and suitable boundary conditions. The frozen principal determinant above does not by itself determine the full variable-coefficient equation, its conserved norm, or its clock couplings.

**Model boundary.** The original homogeneous three-shift circuit has $\det\mathcal U=1$ and a traceless small-wave-number generator, so it does not produce a leading identity drift by that calculation. Nonzero drift must be derived from a specified background, a modified local routing law, or a documented coordinate description. Writing a trace term into $B^i$ is a candidate construction, not evidence that SS OPS 1 already generated it.

**Interpretation.** Directional asymmetry may describe a tilted cone, spatial anisotropy may describe its shape, and polarization dependence may describe additional material propagation. Test which explanation fits the actual local law. A moving-fluid acoustic metric is an established example of a Lorentzian propagation geometry involving flow velocity [R10]; it is an analogy, not proof of universal matter coupling in this program.

## 7 Candidate B Dynamical operator coframe

**Model identifier:** SS OCF 1.

### 7.1 What is being assumed

This model assumes a smooth, oriented, time-oriented four-dimensional domain $M$ admitting the local coframes needed below. Restrict attention to globally hyperbolic regions for initial-value evolution. No fixed Minkowski metric is installed on $M$.

The primitive geometric variable is the invertible Hermitian coframe $E_\mu$. Its metric is the determinant polarization already derived:

$$
g_{\mu\nu}=\mathfrak g(E_\mu,E_\nu).
$$

Local Lorentz frame changes are gauge. The torsion-free metric connection is derived from $g$ rather than introduced as an independent propagating field. General relativity supplies the geometric dynamics in this candidate; it is an explicit completion assumption [R3].

The model includes three matter fields:

| Field | Definition and role | Real degrees of freedom before gravity constraints |
|---|---|---:|
| $\Phi=(\Phi_1,\Phi_2)^T$ | A complex scalar doublet supporting conserved charge and localized cores | 4 |
| $a$ | A real massless neutral signal field | 1 |
| $\chi$ | A real field that can have an oscillatory bound mode inside a core | 1 |

Here “scalar doublet” means that the two components of $\Phi$ are spacetime scalars with an internal complex index. They are **not** a Lorentz Weyl spinor.

This distinction matters. The Hermitian geometry bundle and the internal doublet bundle use related matrix mathematics, but are not identified by this action. Identifying them would require an additional transformation law and coupling, not a change of notation.

For the internal doublet, choose a flat reference connection $\mathcal A_\mu$, with

$$
D_\mu\Phi=\partial_\mu\Phi+\mathcal A_\mu\Phi,\qquad
\mathcal A_\mu^\dagger=-\mathcal A_\mu.
$$

In the simplest trivialization $\mathcal A_\mu=0$. Under a local change of internal basis $V(x)\in U(2)$,

$$
\Phi\mapsto V\Phi,\qquad
\mathcal A_\mu\mapsto
V\mathcal A_\mu V^\dagger-(\partial_\mu V)V^\dagger.
$$

This connection is supplied comparison structure, with zero curvature and no independent dynamics. It is not a derived electromagnetic or weak gauge field. A fixed trivialization still exhibits an ordinary global $U(2)$ symmetry.

### 7.2 Units and coupling definitions

Use $c=\hbar=1$, signature $(+---)$, and coordinates with dimensions of length. The matrix coefficients $E_\mu$ are dimensionless; the one-form $E_\mu dx^\mu$ has dimensions of length.

The scalar fields $\Phi,a,\chi$ have dimensions of mass. Define

$$
s=\Phi^\dagger\Phi,
$$

$$
U(s)=m^2s-\beta s^2+\gamma s^3,
$$

$$
Z(s)=1+\varepsilon\frac{s}{M_0^2},
$$

$$
V_\chi(s)=m_\chi^2-\nu s+\eta s^2.
$$

The parameters are:

- $m>0$: vacuum mass of each complex matter component.
- $\beta>0$: dimensionless attractive quartic coefficient.
- $\gamma>0$: sextic coefficient, with dimensions mass$^{-2}$.
- $\varepsilon\ge0$: dimensionless coupling of the neutral kinetic term to core density.
- $M_0>0$: mass scale appearing in that coupling.
- $m_\chi>0$: vacuum mass of the clock field.
- $\nu>0$: dimensionless coefficient lowering the clock mass inside a core.
- $\eta>0$: coefficient of dimension mass$^{-2}$ that bounds the clock mass function below.
- $\zeta\ge0$: dimensionless clock self-interaction coefficient.
- $M_g>0$: gravitational coupling scale, with $8\pi G_N=M_g^{-2}$.

Here $G_N$ is Newton's gravitational coupling in the continuum completion. It is a parameter, not a prediction.

Choose

$$
0<\beta^2<4\gamma m^2,\qquad
m_\chi^2>\frac{\nu^2}{4\eta}.
$$

Then $U(s)>0$ for $s>0$, $Z(s)>0$ for all $s\ge0$, and $V_\chi(s)>0$. These are useful sufficient conditions for a stable empty matter vacuum and positive matter kinetic terms. They do not establish stability of every nonlinear solution.

### 7.3 The complete action

Let $g=\det(g_{\mu\nu})$, and let $R$ be the scalar curvature of the metric connection. Define

$$
\boxed{
S=\int_M d^4x\,\sqrt{-g}
\left[-\frac{M_g^2}{2}R+\mathcal L_m\right],
}
$$

$$
\boxed{
\begin{aligned}
\mathcal L_m={}&
g^{\mu\nu}(D_\mu\Phi)^\dagger D_\nu\Phi-U(s)\\
&+\frac12 Z(s)g^{\mu\nu}\partial_\mu a\,\partial_\nu a\\
&+\frac12 g^{\mu\nu}\partial_\mu\chi\,\partial_\nu\chi
-\frac12 V_\chi(s)\chi^2-\frac{\zeta}{4}\chi^4.
\end{aligned}
}
$$

We use the curvature convention

$$
R^\rho{}_{\sigma\mu\nu}
=\partial_\mu\Gamma^\rho_{\nu\sigma}
-\partial_\nu\Gamma^\rho_{\mu\sigma}
+\Gamma^\rho_{\mu\lambda}\Gamma^\lambda_{\nu\sigma}
-\Gamma^\rho_{\nu\lambda}\Gamma^\lambda_{\mu\sigma},
$$

with $R_{\sigma\nu}=R^\rho{}_{\sigma\rho\nu}$. With our $(+---)$ signature and positive matter kinetic terms, the displayed gravitational sign gives $M_g^2G_{\mu\nu}=T_{\mu\nu}$ for the stress tensor defined below. Boundary terms appropriate to the chosen variational boundary conditions are understood; they do not alter the bulk equations.

The connection coefficients $\Gamma^\rho_{\mu\nu}$ are the Christoffel symbols of $g$. The symbol $G_{\mu\nu}$ denotes the Einstein tensor $R_{\mu\nu}-g_{\mu\nu}R/2$.

**Interpretation.** Every sector uses the same metric constructed from the operators. The metric evolves in response to the matter. This supplies a single coupled local law, rather than fitting a geometry after separately choosing each sector's propagation.

Universal coupling and the curvature term were chosen deliberately. Their success below is a consequence of those assumptions, not an emergence theorem from projectors alone.

## 8 Field equations and the common propagation calculation

### 8.1 Matter equations

Write $U_s=dU/ds$, $Z_s=dZ/ds$, and $V_{\chi,s}=dV_\chi/ds$. For a real scalar $f$, define

$$
\Box_g f=\frac1{\sqrt{-g}}
\partial_\mu\left(\sqrt{-g}\,g^{\mu\nu}\partial_\nu f\right).
$$

Use the analogous internal-covariant operator for $\Phi$. Variation gives

$$
\boxed{
D_\mu D^\mu\Phi+
\left[
U_s+\frac12V_{\chi,s}\chi^2
-\frac12Z_s\,(\partial a)^2_g
\right]\Phi=0,
}
$$

$$
\boxed{\nabla_\mu\left(Z(s)\nabla^\mu a\right)=0,}
$$

$$
\boxed{\Box_g\chi+V_\chi(s)\chi+\zeta\chi^3=0.}
$$

Here $(\partial a)^2_g=g^{\mu\nu}\partial_\mu a\partial_\nu a$, and $\nabla$ is the metric covariant derivative. The notation $D_\mu D^\mu$ includes the metric divergence as well as the internal connection.

The fields respond reciprocally. The core changes neutral propagation through $Z$, while neutral gradients act back on the core. The core traps $\chi$ through $V_\chi$, while $\chi^2$ perturbs the core.

### 8.2 Geometric equations and conservation

Define the matter stress tensor by

$$
\begin{aligned}
T_{\mu\nu}={}&
(D_\mu\Phi)^\dagger D_\nu\Phi+
(D_\nu\Phi)^\dagger D_\mu\Phi\\
&+Z\,\partial_\mu a\,\partial_\nu a
+\partial_\mu\chi\,\partial_\nu\chi
-g_{\mu\nu}\mathcal L_m.
\end{aligned}
$$

Variation of the invertible coframe is equivalent to metric variation plus Lorentz-frame redundancy:

$$
\boxed{M_g^2G_{\mu\nu}=T_{\mu\nu}.}
$$

The matter equations and geometric identities imply

$$
\nabla_\mu T^{\mu\nu}=0.
$$

This is local stress-energy conservation, not a global energy integral in every curved spacetime. Global charges require suitable symmetries or asymptotic conditions.

The phase symmetry of $\Phi$ gives the current

$$
j^\mu=i\left[
\Phi^\dagger D^\mu\Phi-(D^\mu\Phi)^\dagger\Phi
\right],\qquad \nabla_\mu j^\mu=0.
$$

On a spacelike hypersurface $\Sigma$ with future unit normal $n^\mu$ and induced positive spatial metric of determinant $h_\Sigma$, the conserved charge is

$$
Q=\int_\Sigma n_\mu j^\mu\sqrt{h_\Sigma}\,d^3x
$$

when boundary flux vanishes. This $U(1)$ symmetry is assumed through the chosen action. It has not been derived from ordered reception.

### 8.3 Derivation of a common principal cone

Write

$$
\Phi=\frac1{\sqrt2}
\begin{pmatrix}q_1+iq_2\\q_3+iq_4\end{pmatrix},
$$

where the four $q_I$ are real. Let the six-component perturbation be

$$
\delta\varphi=(\delta q_1,\delta q_2,\delta q_3,\delta q_4,\delta a,\delta\chi).
$$

Freeze an arbitrary smooth background at one event and retain only terms with two derivatives of the perturbations. For a covector $\xi_\mu$, the matter principal matrix is

$$
\boxed{
\mathcal P(\xi)=
H\,g^{\mu\nu}\xi_\mu\xi_\nu,\qquad
H=\operatorname{diag}(1,1,1,1,Z,1).
}
$$

Why does the $Z$ interaction not split the cone? Varying $Z(s)$ in the neutral equation produces $\delta s\,\nabla\bar a$ inside a divergence. This contains at most one derivative of a matter perturbation. Varying $(\partial a)^2_g$ in the core equation also gives only one perturbation derivative. The clock couplings are potentials and contribute none.

Thus

$$
\det\mathcal P(\xi)=
Z\left(g^{\mu\nu}\xi_\mu\xi_\nu\right)^6.
$$

Since $Z>0$, the field-space kinetic matrix is positive. All six physical matter components have the same principal characteristic cone.

In a suitable hyperbolic coordinate gauge, the Einstein equations have the same metric principal cone for their propagating gravitational degrees of freedom. Coordinate and constraint modes must be treated through the chosen gauge; an unconstrained metric-component count is not a physical polarization count.

As an additional algebraic check, a Weyl-type first-order operator using the inverse coframe has symbol

$$
\mathcal W(\xi)=\sigma^a e_a{}^\mu\xi_\mu,\qquad
\det\mathcal W(\xi)=g^{\mu\nu}\xi_\mu\xi_\nu.
$$

This is a compatibility identity. A Weyl matter field is not included in the present action and its quantization or spin-statistics would require separate work.

**Interpretation.** The earlier desired factorization is now derived from a fully stated action. It holds on general smooth backgrounds in the nondegenerate regime, rather than only on a fitted stationary texture. Massive packets may still have slower, frequency-dependent group velocities. Such dispersion is not a second wavefront cone.

### 8.4 Initial-value prescription

To evolve the full theory, supply on $\Sigma$:

1. A positive spatial metric and its extrinsic curvature satisfying the Einstein Hamiltonian and momentum constraints.
2. $\Phi,a,\chi$ and their normal derivatives.
3. An internal flat connection/trivialization and a coframe representative consistent with the spatial metric.
4. A hyperbolic coordinate gauge and boundary conditions compatible with the intended isolated or periodic problem.

Local well-posed evolution is sought for smooth data with invertible coframe and positive $Z$. This is not a claim of global regularity: gravitational collapse and field singularities remain possible.

For matter-only control calculations, take the explicit decoupling limit $M_g\to\infty$ and choose a flat solution. At finite $M_g$, setting the metric identically flat around a massive core is not an exact solution and must be labeled an approximation.

## 9 Localized objects and an actual clock

### 9.1 The charge-supported object ansatz

First take the flat decoupling limit, choose $\mathcal A_\mu=0$, and set $a=\chi=0$. Propose

$$
\Phi(t,\mathbf x)=F(r)e^{-i\omega_Qt}u_0,\qquad
r=|\mathbf x|,\qquad u_0^\dagger u_0=1.
$$

$F(r)$ is a real radial profile, $\omega_Q>0$ its internal phase frequency, and $u_0$ a constant internal orientation.

The field equation becomes

$$
F''+\frac2rF'
=(m^2-\omega_Q^2)F-2\beta F^3+3\gamma F^5,
$$

with $F'(0)=0$ and $F(r)\to0$ as $r\to\infty$.

For this ansatz,

$$
Q=2\omega_Q\int F^2\,d^3x,
$$

$$
E_Q=\int
\left[\omega_Q^2F^2+|\nabla F|^2+U(F^2)\right]d^3x.
$$

$E_Q$ is the flat-space energy of the core. The profile extremizes

$$
E_Q-\omega_QQ
=\int\left[|\nabla F|^2+U(F^2)-\omega_Q^2F^2\right]d^3x.
$$

An exponentially decaying tail requires $\omega_Q^2<m^2$. A negative region of the effective interior potential requires

$$
\omega_Q^2>\min_{s>0}\frac{U(s)}s
=m^2-\frac{\beta^2}{4\gamma}.
$$

Therefore the standard Q-ball existence window is

$$
\boxed{
m^2-\frac{\beta^2}{4\gamma}<\omega_Q^2<m^2.
}
$$

This is the familiar charge-supported soliton mechanism, not a new particle-identification theorem [R4]. Branch stability, fragmentation, nonradial modes, and gravitational corrections still need checking for the chosen solution. $E_Q<mQ$ excludes decay into free quanta at fixed charge but does not alone prove every form of stability.

**Interpretation.** Conserved phase charge can oppose collapse without a quartic derivative stabilizer. This allows localized recurrent complex fields while preserving the shared principal cone.

### 9.2 Why the rotating core is not yet a readable clock

For the ansatz above,

$$
s=F^2,\qquad
P_\Phi=\frac{\Phi\Phi^\dagger}{\Phi^\dagger\Phi}=u_0u_0^\dagger.
$$

Both density and projector are static. The internal phase rotates, but an isolated invariant density or projector record does not tick.

A relative phase can be measured when another coherent state arrives. That makes $\omega_Q$ a useful phase reference. It does not produce an autonomous local cycle counter.

This is why $\chi$ was added explicitly. Its purpose is operational and testable, not decorative.

### 9.3 Deriving a trapped clock mode

Linearize the $\chi$ equation around the quiet core. Seek

$$
\chi(t,\mathbf x)=A_\chi f_\chi(\mathbf x)
\cos(\Omega_\chi t+\theta_0)
$$

to leading order in the small amplitude $A_\chi$. The real spatial mode $f_\chi$ satisfies

$$
\boxed{
\left[-\nabla^2+V_\chi(F^2)\right]f_\chi
=\Omega_\chi^2 f_\chi,
}
$$

with $f_\chi$ square-integrable and normalized by $\int f_\chi^2d^3x=1$.

Because $V_\chi>0$, the eigenvalue is positive. A localized mode must also satisfy

$$
0<\Omega_\chi^2<m_\chi^2.
$$

The core can create precisely this mass well: $V_\chi(F^2)$ can be smaller than its asymptotic value $m_\chi^2$.

A useful sufficient existence criterion follows from the variational principle. If a ball of radius $R_c$ lies inside a region where

$$
V_\chi(F^2)\le V_{\rm in}<m_\chi^2,
$$

use the lowest Dirichlet radial mode supported on that ball as a trial function. Its Rayleigh quotient is at most

$$
\Omega_{\rm trial}^2=V_{\rm in}+\frac{\pi^2}{R_c^2}.
$$

Hence a bound eigenmode exists if

$$
\boxed{V_{\rm in}+\pi^2/R_c^2<m_\chi^2.}
$$

This criterion does not assume that the actual Q-ball profile is a square well. It requires verifying the stated upper bound on the actual potential throughout a ball.

### 9.4 A concrete parameter family

Measure masses in units of $m$ and set

$$
m=1,\quad\beta=1,\quad\gamma=1,\quad
m_\chi=0.5,\quad\nu=0.4,\quad\eta=0.2,\quad\zeta=0.1.
$$

Dimensionful values here mean the corresponding powers of $m$: $\gamma=m^{-2}$, $\eta=0.2m^{-2}$, and $m_\chi=0.5m$. The displayed numbers are dimensionless after this conversion.

For neutral coupling, a proposed initial choice is $\varepsilon=0.1$ and $M_0=m$. Gravity is initially decoupled for object calibration and restored in a separate constraint-satisfying calculation.

The core window is

$$
\sqrt{3/4}<\omega_Q<1.
$$

Near its large-radius, thin-wall limit, the interior density approaches

$$
s_0=\frac{\beta}{2\gamma}=0.5.
$$

At this density,

$$
V_\chi(s_0)=0.10,\qquad
\min_s V_\chi(s)=0.05,\qquad
V_\chi(0)=0.25.
$$

In an ideal constant-density interior, the sufficient trial condition becomes

$$
R_c>\frac{\pi}{\sqrt{0.15}}\simeq8.112.
$$

This is an analytical threshold for the declared interior approximation, not a measured radius or a computed bound frequency. The actual profile must be solved before using it as a detector.

At arbitrarily small nonzero clock amplitude, core backreaction is of order $A_\chi^2$. At finite amplitude, nonlinear frequency shifts and radiation can accumulate. The model therefore predicts a controllable weak-clock regime; it does not prove an eternal finite-amplitude periodic object.

### 9.5 A local phase and dimensionless record

For an isolated calibrated bound mode, write its amplitude coordinate and momentum as

$$
q_\chi=A_\chi\cos\theta_\chi,\qquad
p_\chi=-\Omega_\chi A_\chi\sin\theta_\chi.
$$

Then

$$
\theta_\chi=
\operatorname{unwrap}
\operatorname{atan2}\left(-p_\chi/\Omega_\chi,q_\chi\right).
$$

The calibration mode projection is a computational diagnostic. An operational receiver instead samples $\chi$ and its local canonical momentum in a small comoving part of the core, using the independently calibrated mode shape; zero crossings provide a direct local cycle count. A fit to an entire distant field history is not an admissible local readout.

There is also a readout that does not need to distinguish $\chi$ from $-\chi$. Define the local quadratic quadratures

$$
C_\chi=q_\chi^2-(p_\chi/\Omega_\chi)^2,\qquad
S_\chi=-2q_\chi p_\chi/\Omega_\chi.
$$

They equal $A_\chi^2\cos(2\theta_\chi)$ and $A_\chi^2\sin(2\theta_\chi)$. Use the invariant clock phase

$$
\Theta_\chi=\operatorname{unwrap}\operatorname{atan2}(S_\chi,C_\chi)
=2\theta_\chi
$$

up to the calibrated origin. In this readout one tick corresponds to half a signed field oscillation. Unlike the isolated rotating core projector, even the quadratic clock observables genuinely oscillate.

Let $e_1,e_2$ be two physically defined local marker events at the receiver, such as the reception of two weak tagging pulses. The proposed record is

$$
\boxed{
\mathcal N_R=
\frac{\Theta_\chi(e_2)-\Theta_\chi(e_1)}{2\pi}.
}
$$

For an intervention and matched control preparation, compare $\Delta\mathcal N_R$. The endpoints must be defined by the same local protocol, not by coordinate timestamps chosen after looking at the response.

Tagging pulses have their own physical backreaction. Calibrate it, and either keep it identical between preparations or verify the weak-tag extrapolation. Calling them markers does not make them noninteracting.

**Interpretation.** The clock now has something locally oscillating to count. The scale comes from a bound eigenmode of the same matter theory. Clock fidelity, finite-size effects, and signal-induced susceptibility remain measurable properties rather than presumed universality.

### 9.6 Deriving the proper-time law and observer operator

Consider a slowly moving localized core much smaller than the curvature scale. Let $X^\mu(\tau)$ be its center worldline, $v^\mu=dX^\mu/d\tau$ its future unit velocity, and $g_{\mu\nu}v^\mu v^\nu=1$.

In local rest coordinates around that worldline, insert $\chi=q_\chi(\tau)f_\chi(\mathbf y)$ into its quadratic action. Here $\mathbf y$ labels physical spatial offsets in the local rest frame. The normalization and eigenvalue equation give, at leading order in size and slow-background corrections,

$$
S_{\chi,\mathrm{bound}}
=\frac12\int d\tau
\left[
\left(\frac{dq_\chi}{d\tau}\right)^2
-\Omega_\chi^2q_\chi^2
\right].
$$

The leading core center action is $-E_Q\int d\tau$ in the weak-gravity, weak-excitation limit. Both results use the same proper-time element

$$
d\tau^2=g_{\mu\nu}dX^\mu dX^\nu.
$$

Thus the isolated calibrated quadratic clock has

$$
\frac{d\Theta_\chi}{d\tau}=2\Omega_\chi
$$

at this order. Tidal deformation, acceleration, changing core charge, and the incident interaction give calculable corrections. The approximation requires core radius squared times local curvature components to be small, and environmental changes slow enough for mode mixing to remain controlled.

The physical core can also supply an observer operator:

$$
T_{\rm core}=E_\mu v^\mu.
$$

It is positive for the chosen future orientation and

$$
\det T_{\rm core}=g_{\mu\nu}v^\mu v^\nu=1.
$$

Where the charge current is timelike, its normalized local flow can supply $v^\mu$. Where interference makes that current null or spacelike, that construction cannot be used; a well-defined object rest frame or another timelike material flow is required.

**Interpretation.** In the continuum completion, the observer matrix is tied to the actual motion of a localized object, and the clock scale is tied to its bound spectrum. Identifying this operator with Candidate A's normalized matrix aggregate would still require a microscopic-to-continuum map.

## 10 Interactions emission reception and recoil

### 10.1 What can propagate

In the empty flat vacuum, linearization gives

$$
\omega_a^2=|\mathbf k|^2,\qquad
\omega_\Phi^2=|\mathbf k|^2+m^2,\qquad
\omega_\chi^2=|\mathbf k|^2+m_\chi^2.
$$

The $\omega$ symbols here denote Fourier frequencies of the corresponding fields. Structural and clock radiation propagate only above their vacuum mass thresholds. Their high-frequency wavefronts share the neutral cone.

A core perturbation can scatter, transfer charge, excite bound modes, or emit above-threshold radiation. Which channels actually open is a spectral calculation, not a consequence of the object's appearance.

### 10.2 A necessary neutral-emission null

The neutral equation is homogeneous in $a$. If both $a$ and its initial normal derivative vanish, then

$$
a=0
$$

remains an exact solution throughout its domain of dependence.

Thus SS OCF 1 does **not** predict spontaneous classical neutral emission from a completely unseeded core. Neutral-signal experiments must supply initial neutral excitation, while structural emission can be tested by perturbing the core itself.

Adding a source term to obtain automatic neutral radiation would be a new model version. Its boundedness, conservation, and principal symbol would need to be derived again.

### 10.3 Reception through an independently calibrated clock

An incident neutral field affects the core through

$$
-\frac12Z_s(\partial a)^2_g\Phi.
$$

The changed core density alters the clock well. In the weak, slowly varying, fixed-flat-background limit, first-order eigenvalue perturbation theory gives

$$
\delta\Omega_\chi=
\frac{1}{2\Omega_\chi}
\int f_\chi^2(\mathbf x)
V_{\chi,s}(F^2)\,\delta s(\mathbf x)\,d^3x.
$$

The core translation must first be removed by using its comoving frame. Metric perturbations add the variation of the geometric eigenoperator and are excluded from this particular flat-space formula.

For the example interior density $s_0=0.5m^2$, $V_{\chi,s}=-0.2$. A positive density perturbation concentrated there therefore lowers the clock frequency in this approximation. The incident field need not produce a positive density perturbation, so the sign of the entire reception record still follows from the core response.

For an adiabatic disturbance between fixed physical marker events,

$$
\Delta\mathcal N_R\simeq
\frac1{\pi}\int_{e_1}^{e_2}\delta\Omega_\chi\,d\tau.
$$

Here $d\tau$ is receiver proper time. The factor $1/\pi$ reflects the quadratic readout $\Theta_\chi=2\theta_\chi$. Changes in the marker-event arrival times contribute separately when the full protocol changes them.

The overlap integral may vanish or change sign. A nonzero response cannot be promised from the coupling's presence alone.

If the incident neutral amplitude is scaled by a small real factor $b$, the leading core forcing is order $b^2$. Consequently, the leading clock phase response is generically

$$
\Delta\mathcal N_R=C_Rb^2+O(b^4),
$$

where $C_R$ is a response coefficient calculated from the calibrated core, propagation, and clock mode. The unseeded neutral equation and the symmetry $a\mapsto-a$ forbid an odd response in this protocol. If $C_R=0$, the leading nonzero order must be determined rather than fitted to the expected quadratic law.

### 10.4 A revealing plane-wave null

A single ideal right-moving plane wave $a=A f(t-x)$ in empty flat space has

$$
(\partial a)^2=0.
$$

It supplies no direct quadratic core forcing through the displayed invariant on that idealized background. Scattering from an inhomogeneous $Z$ can change this conclusion locally.

For two counterpropagating waves

$$
a=A f(t-x)+B h(t+x),
$$

where $A,B$ are real amplitudes and primes denote derivatives of the waveform arguments,

$$
(\partial a)^2=4AB f'h'.
$$

The overlapping pulses can drive a core even when either isolated ideal plane wave does not. This is a particularly clean hypothesis for a local reception test. The total two-pulse response should be compared with the two single-pulse controls.

### 10.5 Closed-system recoil

In the decoupled flat theory, the integrated matter momentum

$$
P^i_{\rm total}=\int T^{0i}d^3x
$$

is conserved when boundary flux is included. A receiver momentum change must be balanced by incoming/outgoing field momentum and changes elsewhere.

At finite gravitational coupling, use the constraint-consistent geometry and an appropriate local or asymptotic momentum ledger. Do not replace curved-spacetime conservation by a naive global Cartesian integral.

Preparation means choosing finite-energy initial data. After preparation, the closed evolution has no external prescribed pump. If a simulation uses an external source during evolution, record its work and momentum explicitly.

**Interpretation.** Reception is a physical disturbance of a surviving object with a readable state. A phase shift extracted from a remote waveform is a useful diagnostic but is insufficient on its own.

## 11 Static object labels and changing geometry

A coframe can change while selected object coordinates remain fixed. For illustration, take

$$
E=N(t)I\,dt+b(t)\sigma_i\,dx^i,
$$

where $N(t)>0$ is a lapse and $b(t)>0$ a spatial scale factor. Then

$$
ds^2=N(t)^2dt^2-b(t)^2d\mathbf x^2.
$$

Objects at fixed coordinate labels have local proper time $d\tau=Ndt$. Their equal-time proper separation is $b(t)|\Delta\mathbf x|$. Radial null signals satisfy $|d\mathbf x/dt|=N/b$.

An arbitrary pair of functions $N,b$ is not automatically a solution of SS OCF 1. The Einstein constraints and matter equations must support it. This example explains the variables and observable distinctions only.

A time-coordinate change can remove the lapse locally without removing physical expansion. More generally, changing $E$ by a local Lorentz frame transformation leaves the metric and all records unchanged; changing the metric while keeping the physical experiment fixed can alter travel times and clock comparisons.

A clock measures more than a null cone. A conformal rescaling

$$
g_{\mu\nu}\mapsto\Omega(x)^2g_{\mu\nu}
$$

preserves null directions but changes proper time and mass-dependent processes unless the full matter theory is transformed appropriately. The positive function $\Omega(x)$ is a conformal factor, not an independently assumed signal speed.

**Interpretation.** Fixed labels can coexist with physical relational motion. The test is a changed invariant record, not a changed matrix entry. In SS OCF 1, matter clocks and signal cones refer to the same metric by the chosen coupling law, while finite detector susceptibility remains a separate physical effect.

### 11.1 Including drift in the operator coframe

The diagonal example above does not exhaust Candidate B. A general local drift form is

$$
E=N I\,dt+\sigma_a L^a{}_i(dx^i-v_{\rm d}^i dt),
$$

where $N>0$ is the lapse and the invertible real matrix $L^a{}_i$ supplies a spatial coframe. Define the positive spatial metric

$$
h_{ij}=\sum_a L^a{}_iL^a{}_j.
$$

The determinant construction then gives

$$
ds^2=N^2dt^2-h_{ij}
(dx^i-v_{\rm d}^i dt)(dx^j-v_{\rm d}^j dt).
$$

Its null covectors satisfy

$$
(\omega-v_{\rm d}^ik_i)^2=N^2h^{ij}k_ik_j,
$$

where $h^{ij}$ is the inverse spatial metric. This matches Section 6.5 with $D^{ij}=N^2h^{ij}$. Candidate B therefore already permits tilted cones and direction-dependent coordinate speeds without changing its action.

Arbitrary prescribed $N,L,v_{\rm d}$ need not solve the field equations. A spatially or temporally varying drift may encode physical geometry, a noninertial chart, or both. Compute the full Riemann curvature tensor and invariant clock/transport records; nonconstant coefficients alone do not prove curvature. Conversely, the absence of a local scalar-curvature signal alone does not prove flatness.

One-way coordinate speed also depends on how distant clocks are synchronized. Use return signals, closed-path comparisons, and the local cycle record $\mathcal N_R$ to avoid interpreting a synchronization convention as a new physical effect. A pure change of description must preserve those records.

## 12 Hopf structure and the return of spatial knots

### 12.1 Internal Hopf geometry survives

For a normalized complex doublet $u$, the map

$$
u\in S^3\longmapsto uu^\dagger\in S^2
$$

is the Hopf fibration. Its phase fiber exists before any physical spacetime interpretation.

If an actual spatial domain $\Sigma$ is topologically compactified to $S^3$, and a smooth nonvanishing field defines $u$ there, introduce the real one-form

$$
\mathcal B=-iu^\dagger du,\qquad \mathcal F=d\mathcal B.
$$

For the usual normalization and a fixed orientation, the Hopf integer is

$$
Q_H=\frac1{4\pi^2}\int_\Sigma \mathcal B\wedge\mathcal F.
$$

Changing orientation changes the sign. Phase changes alter $\mathcal B$ by an exact form and leave the integral unchanged under the stated closed-domain conditions.

This formula requires the domain, regularity, and boundary hypotheses. It is not an integer attached to every finite graph or every internal orbit.

### 12.2 Why the present core is not a protected Hopf knot

The simple Q-ball has constant $P_\Phi$, so its Hopf texture is trivial. More generally, $\Phi\to0$ in the vacuum, making its normalized direction undefined there. Zeros can also allow a texture to unwind.

One may define a Hopf number for a specially prepared, smoothly extendible normalized field, but the unconstrained amplitude theory does not automatically protect that extension during evolution.

Moreover, for a static fixed-length orientation texture of radius $R$ in three space dimensions, a quadratic gradient energy scales as

$$
E_2(R)\propto R.
$$

It can be lowered by shrinking. A quartic derivative energy scales as

$$
E_4(R)\propto R^{-1},
$$

and can balance the shrinking tendency. This scaling argument motivates familiar Faddeev-type knot models [R5], but it is not a derivation of their coefficients or of their physical interpretation.

### 12.3 The cone cost of the old stabilizer

For an independent unit vector $\mathbf n(x)$, define

$$
\mathcal H_{\mu\nu}
=\mathbf n\cdot(\partial_\mu\mathbf n\times\partial_\nu\mathbf n).
$$

Adding

$$
-\frac{\kappa_H}{4}\mathcal H_{\mu\nu}\mathcal H^{\mu\nu}
$$

changes the derivative Hessian on nonuniform backgrounds. Here $\kappa_H>0$ is a proposed quartic coupling. Covariantizing it with the same $g_{\mu\nu}$ does not generally make its physical perturbations share that metric cone.

The supplied characteristic checkpoint already demonstrated the corresponding split in the earlier coupled model. In a static one-gradient control, one orientation speed was

$$
v_{\rm extra}^2=\frac{K}{K+\kappa_Hp^2}
$$

while the ordinary mode and neutral sector had speed one. Here $K>0$ is the quadratic orientation stiffness and $p$ the background orientation gradient. The extra cone remains a physical difference after coordinate or invertible field redefinitions. The broader characteristic issue is also discussed in [R6,R7].

**Interpretation.** A shared fundamental or emergent spacetime is compatible with material excitations having different effective speeds. Direction-dependent coordinate propagation, including forward/backward asymmetry from drift, can belong to one Lorentzian metric and is explicitly retained as a research possibility. A persistent polarization-dependent split instead fails the narrower hypothesis that all tested modes share one characteristic cone. It does not by itself rule out a geometric signal sector with additional material dynamics, or a theory with several effective geometries.

The static orientation control above changes one mode's cone width without an odd directional drift term. Its two-cone result cannot be removed by a shared boost or coordinate change. That historical result remains valid; the broader decision to reject all emergent-spacetime interpretations does not follow from it. Test 11 distinguishes shared drift, spatial anisotropy, material response, and persistent mode splitting.

For now, retain charge stabilization in SS OCF 1 and treat protected spatial knots as an open extension. The next knot proposal must demonstrate both an appropriate invariant and its actual characteristic structure. It cannot inherit those achievements from the internal Hopf map.

## 13 Larger matrices and the selection of dimension

The special feature of $\operatorname{Herm}(2,\mathbb C)$ is that its determinant is quadratic on a real four-dimensional space. This makes it directly suitable for a Lorentzian quadratic form.

For comparison:

| Algebraic object | Real dimension | Natural structure | What does not follow automatically |
|---|---:|---|---|
| Traceless Hermitian $2\times2$ matrices | 3 | Positive trace inner product and $SU(2)$ adjoint rotations | Three physical spatial dimensions |
| Hermitian $2\times2$ matrices | 4 | Quadratic determinant of signature $(1,3)$ | A physical derivative map or propagation law |
| Traceless Hermitian $3\times3$ matrices | 8 | Positive trace form, $SU(3)$ adjoint action, and independent higher invariants | Eight physical directions or the strong interaction |
| Rank-one projectors in $\mathbb C^3$ | 4 | $\mathbb{CP}^2$ with its state-space geometry | A four-dimensional Lorentzian spacetime |
| Rank-$r$ projectors in $\mathbb C^N$ | $2r(N-r)$ | A complex Grassmannian of subspaces | A selected spacetime dimension or particle family |

Here $N$ is the complex dimension of the underlying Hilbert space and $r$ the fixed projector rank. The determinant for $3\times3$ Hermitian matrices is cubic, not a spacetime metric quadratic form.

Larger operator spaces could supply additional internal sectors, order parameters, or a phase selecting a $\operatorname{Herm}(2,\mathbb C)$ subalgebra. Such a selection would require an energy principle and a stability calculation.

**Interpretation.** The two-dimensional complex state is economical for the desired algebraic signature. That is a motivation for studying it, not a proof that nature selects it. Neither candidate predicts the Standard Model groups, three generations, the fine-structure constant, or lepton mass ratios.

## 14 Relative locality and changes of description

### 14.1 Three different meanings

1. **Elementary locality:** events use only their participants. Candidate A has this by construction.
2. **Observer-dependent reconstruction:** different observers infer descriptions from local clocks and exchanged signals. Both candidates can support this as an operational program.
3. **Technical relative locality:** momentum-space geometry changes composition and translation rules so distant coincidence can depend on the observer [R8].

The first two do not imply the third. A noncommuting matrix algebra is not yet a nonlinear momentum-composition law.

### 14.2 What these models currently predict

SS OCF 1 uses ordinary tangent-space energy-momentum conservation at a local interaction. It contains curved spacetime, but no separately deformed momentum space or new relative-locality effect.

SS OPS 1 has an internal conserved matrix charge. It has not established that this charge is spacetime energy-momentum. Calling its determinant a mass shell would be premature.

Consequently, neither candidate presently predicts a nonzero detector effect specifically attributable to technical relative locality.

### 14.3 The momentum-coordinate null

Let $p_\mu$ be ordinary momentum coordinates and $p'_\alpha=f_\alpha(p)$ a smooth invertible reparameterization with $f(0)=0$. The conjugate position variables transform as

$$
x'^\alpha=x^\mu\frac{\partial p_\mu}{\partial p'_\alpha}
$$

so that $x^\mu dp_\mu=x'^\alpha dp'_\alpha$.

Ordinary addition written in the new coordinates becomes

$$
p'\oplus' q'
=f\!\left(f^{-1}(p')+f^{-1}(q')\right).
$$

It can look nonlinear while remaining associative and commutative. This is a coordinate rewrite of the original theory, not evidence for new physics.

Transform the dispersion relation, symplectic variables, conservation functions, detector couplings, and endpoint conditions together. Then the same receiver cycle record must satisfy

$$
\mathcal N_R'=\mathcal N_R.
$$

A coordinate-only change of apparent interaction separation cannot pass as an effect.

### 14.4 What a future extension would have to add

A genuine relative-locality candidate would need an explicit phase-space action with a mass-shell function $C(p)$, a composition law $\oplus$, ordered vertex conservation functions $K_\mu$, and dynamical emitter and detector variables. Vertex endpoint conditions follow by varying that action and involve derivatives of $K_\mu$ with respect to every participating momentum.

It would also need all ordered spectator terms, recoil, a local clock model, and an undeformed limit. The same $\Delta\mathcal N_R$ must agree between emitter-centered and detector-centered descriptions, under the model's boost transformations, and under invertible momentum-coordinate changes.

Those structures are not supplied by this document. The sensible current prediction is a pure-relabeling null, with momentum-first language retained where useful.

## 15 Discriminating experiment program

The following are proposed numerical or analytical experiments, not completed runs. Their numerical thresholds are prospective engineering gates, not empirical confidence levels.

The supplied attachments are historical evidence. No current registered solver/configuration for SS OPS 1 or SS OCF 1 has been established here. Before execution, register the selected model equations, lock the exact input configuration and resource limits, and preserve failed attempts. Do not quietly run a historical solver under a new model name.

Use four result classes: **pass**, **fail**, **unresolved**, and **not evaluated**. A run that completes technically can still fail its hypothesis.

### 15.1 Test 1 Operator and observer identities

**Question.** Are the algebraic ingredients implemented consistently, including nonunitary frame changes?

**Hypothesis.** Determinants, $\mathfrak g$, observer norms, and normalized weighted-ray transformations agree with their exact formulas.

**Setup.** Generate 1,000 reproducible moderate-condition-number Hermitian matrices, positive full-rank aggregates, and $SL(2,\mathbb C)$ transformations. Include the four tetrahedral projectors, collinear states, and nearly collinear aggregates.

**Observables.** Determinant-polarization residuals, eigenvalues of the tetrahedral Gram matrix, observer norm changes, idempotence after correct ray renormalization, and conditioning of $T$.

**Controls.** Omitting the transformed weight must fail a boost comparison. A rank-one aggregate must be classified as having no normalized timelike observer, not regularized silently.

**Gate.** Scale-normalized residual below $10^{-10}$ for well-conditioned samples; ill-conditioned cases reported separately. Expected exact Gram spectrum: $(1,-1/3,-1/3,-1/3)$.

**Visual.** Observer-norm residual versus matrix condition number, with singular cases visibly excluded from the valid domain. This tests algebra and implementation, not physical spacetime.

### 15.2 Test 2 Reciprocal event law and rescheduling

**Question.** Does Candidate A obey its own locality and conservation rules?

**Hypothesis.** $N$, $w^\dagger w$, and $J_e$ are conserved, and disjoint events commute.

**Setup.** Use a small acyclic circuit of at most 32 events, with shared memories only along explicitly ordered memory wires. Set $\kappa=\pi/2$ and compare $\lambda=0$ with $\lambda=0.1$. Use noncollinear participant states of bounded norm. Integrate each Hamiltonian gate with a constraint-preserving or sufficiently converged method.

**Observables.** Relative norm and matrix-charge errors, overlap records, memory changes, and output differences between two permissible topological schedules.

**Controls.** Reverse two events that share a memory: a difference is allowed and generally expected. Freeze a driven memory: the missing matrix backreaction must appear in the ledger. Apply independent local unitary frame changes to the entire circuit.

**Gate.** Conservation and permissible-rescheduling residuals below $10^{-9}$, confirmed by halving the gate-integration tolerance. Check Jacobian dependence: outputs cannot depend on inputs outside their causal ancestors.

**Visual.** Event incidence with a highlighted causal response region and a matrix-charge balance plot. A finite causal region by itself is not a metric.

### 15.3 Test 3 Does propagation follow the projector generator

**Question.** Does the actual linear router circuit realize the derived cone?

**Hypothesis.** Its low-wave-number dispersion approaches

$$
\omega^2=v^2(\mathbf n_i\cdot\mathbf n_j)k_ik_j.
$$

**Setup.** Implement the explicit three conditional shifts and verify their Fourier matrix against the circuit. Compare an orthogonal triad, a nonorthogonal independent triad, and a collinear triad. Use label boxes $32^3$ and $64^3$ or evaluate the exact Fourier blocks directly before real-space evolution. Sample axial and oblique directions with $|\mathbf k|\ell=0.02,0.04,0.08,0.16$.

**Observables.** Quasifrequencies, group directions, amplitude conservation, full-zone extra modes, and the difference between the two block orders.

**Controls.** The collinear case must lose three-dimensional nondegeneracy. Reversing block order must preserve the leading cone while changing the finite-bandwidth triple-sine term. Simultaneously rotating all projectors must preserve predictions.

**Gate.** Agreement with the exact Fourier product to the solver's declared tolerance; convergence to the derived continuum expansion as $|\mathbf k|\ell\to0$. Do not infer failure of the leading cone merely from expected finite-wavelength corrections.

This is the specified zero-leading-drift benchmark. A nonzero-drift extension must be separately derived and tested under Test 11; zero trace in this circuit is not a selection rule for the whole program.

**Visual.** Constant-frequency surfaces and dispersion residuals versus wavelength for each triad. These show precisely how projector relations affect one propagation sector.

### 15.4 Test 4 The microscopic common-geometry test

**Question.** Does the complete Candidate A system, including memories, admit a common effective geometry?

**Hypotheses.** The strong hypothesis is that a selected self-consistent nonzero periodic background has a stable linearized spectrum whose physical propagation sectors share a nondegenerate cone, allowing shared drift and spatial anisotropy. The alternative is a geometric signal sector interacting with material modes that have additional constitutive response. Declare the proposed geometric sector and the material explanation before testing withheld sectors.

**Setup.** First reproduce the analytically known zero-wave obstruction. Then solve for an actual periodic background of one fully specified reciprocal routing circuit. Record its period and all state/memory variables. Linearize the complete one-period map, rather than treating the projector background as an external coefficient.

**Observables.** Floquet multipliers, all branches of the linear response, memory participation, kinetic stability, and causal response to localized perturbations.

**Controls.** Compare full backreaction with frozen memory. Distinguish genuine gauge variations from physical changes of projector overlaps. Test several oblique directions and a withheld sector.

**Gate.** A stable candidate must have no unresolved exponentially growing physical modes. The strong common-cone hypothesis must predict withheld sectors within independently measured numerical error. Persistent distinct characteristic families fail that strong hypothesis for the background, not every emergent-spacetime interpretation. The alternative interpretation needs a derived causal geometric sector, an explicit physical role and response law for the other modes, and independent clock/transport predictions; relabeling unexplained discrepancies as “material” does not pass.

**Expected current result.** The zero-wave vacuum fails the strong all-sector cone hypothesis because it contains stationary physical memory modes. The status of a weaker geometric-sector interpretation and of nonzero backgrounds is unresolved.

**Visual.** Complete branch spectrum with wave and memory content indicated. Hiding flat branches would invalidate the test.

### 15.5 Test 5 Continuum action and characteristic audit

**Question.** Does an implementation of SS OCF 1 retain the derived common principal structure?

**Hypothesis.** The matter derivative Hessian is $H\otimes g^{\mu\nu}$ on arbitrary smooth local backgrounds, with $H=\operatorname{diag}(1,1,1,1,Z,1)$.

**Setup.** Independently differentiate the action with respect to field derivatives; compare with the written equations on 200 seeded nondegenerate coframes and matter backgrounds. Include nonzero $\nabla a$, nonzero $\chi$, and nonzero core gradients.

**Observables.** Hessian residual, field-space eigenvalues, and characteristic roots along at least 20 directions.

**Controls.** Set $Z$ artificially negative to verify that the health gate fails. In a separately versioned control only, add the old quartic orientation term and verify that its additional cone is detected.

**Gate.** Scale-normalized algebraic residual below $10^{-10}$ and strictly positive matter kinetic eigenvalues in the valid parameter region. Gravity is checked in a named hyperbolic gauge with its constraints monitored.

**Visual.** Overlaid characteristic surfaces for all sectors and the orientation-term control. Since the common-cone result is analytically built into this action, this test validates implementation; it is not empirical support for the completion.

### 15.6 Test 6 Build and calibrate a localized clock

**Question.** Does the proposed core support a readable, sufficiently persistent trapped mode?

**Hypothesis.** A Q-ball on the chosen stable branch has a bound eigenvalue $0<\Omega_\chi^2<m_\chi^2$, and a weak excitation produces a local oscillatory record for at least 100 periods.

**Setup.** In the flat decoupling limit, solve the radial core equation for $\omega_Q/m=0.868,0.875,0.90,0.94$. These are trial branch samples, not guaranteed accepted profiles. Use the parameter family in Section 9. Start with $r_{\max}m=80$ and radial spacing $\Delta r\,m=0.1$; refine to $0.05$ and enlarge the domain to 160 when the tail or clock mode is not negligible. Permit further refinement only to resolve a documented error.

Solve the clock eigenproblem independently of time evolution. Verify the actual potential-well criterion or establish the eigenvalue directly. Excite $\chi$ with a small peak field, initially $\max|\chi|/m=10^{-3}$, and repeat at half and twice that amplitude.

**Observables.** Profile residual, $Q$, $E_Q/mQ$, bound eigenfrequency, local zero-crossing frequency, amplitude-dependent shifts, radiated energy, and core drift. Check the core's perturbation spectrum before calling a branch stable.

**Controls.** Remove the trapping coefficient $\nu$ while retaining positive $V_\chi$; the proposed core-centered bound mode should disappear if no other well remains. Run an unexcited $\chi=0$ core to show that its rotating phase is not a ticking projector record.

**Gate.** The bound eigenvalue's separation from zero and continuum threshold must exceed five times the numerical error estimate. Over 100 calibrated periods, require less than 1% loss of clock-mode energy and less than 1% core charge drift after accounting for boundary flux. Those lifetime targets are proposed usability gates, not analytical guarantees.

**Visual.** Core profile, clock mass well, bound eigenfunction, local clock trace, and frequency/lifetime convergence. If no branch meets the lifetime requirement, classify the detector as unusable in that regime.

### 15.7 Test 7 Predict reception before looking at the receiver run

**Question.** Does an independently calibrated clock predict its local response to a known incident field?

**Hypothesis.** The weak neutral response is even in pulse amplitude and agrees with the calibrated core-plus-clock susceptibility.

**Setup.** Use an accepted clock from Test 6. Freeze its calibration. Prepare compact incoming neutral wave packets as initial data and record the incident field on a surface before the receiver. Use both a single pulse and a pair of counterpropagating pulses. Choose carrier and width from the measured core spectrum so that the proposed adiabatic approximation, if used, is justified.

Before the full coupled run, calculate the response using the calibrated linear core resolvent and the measured incident forcing. If the adiabatic approximation is invalid, use the full time-dependent linear response instead of the integral in Section 10.

**Observables.** The local $\chi$ cycle record between fixed marker events, the incident forcing invariant $(\partial a)^2$, core density response, and the predicted response coefficient.

**Controls.** Quiet receiver; each pulse alone; both pulses; amplitude sign reversal; amplitude factors $1/2,1,2$; changed receiver clock phase; and a deliberately incomplete replay that freezes core backreaction.

**Gate.** A nonzero record must exceed five times the combined numerical and finite-domain error estimate. The withheld-record prediction must agree to within the larger of 5% or that error estimate. The amplitude law is judged only where the leading coefficient is resolvable.

**Visual.** Incident forcing, predicted and actual local clock histories, phase residuals, and an amplitude-scaling plot including null controls. A coordinate arrival shift without a local clock change is not sufficient.

### 15.8 Test 8 Two surviving objects with exchange and recoil

**Question.** Can the model support a closed interaction between separately calibrated objects?

**Hypothesis.** A finite initial excitation near object A produces propagating fields, a local record at B, and momentum transfer consistent with the conservation ledger, while both objects remain usable.

**Setup.** Begin with two well-separated accepted cores and weak clock modes. Solve or relax the joint initial data; a naive superposition is only an approximation and its initial relaxation must be measured. At finite $M_g$, solve the gravitational constraints.

Use two versions: a prepared neutral packet initially localized near A, and an initially perturbed A core with $a=0$ everywhere. The latter must preserve the exact neutral-emission null and tests structural emission instead.

**Observables.** Local clock records at both objects, core charge and energy, radiated flux through enclosing surfaces, center motion, total momentum balance, and detector survival after the interaction.

**Controls.** A quiet pair, one object removed, signal phase/amplitude reversal where meaningful, larger separation, larger domain, and at least one independent spatial refinement.

**Gate.** Both clocks must satisfy their predeclared post-interaction usability criteria. Unexplained energy or momentum ledger residual above 1% fails the run. A signal-dependent record must survive refinement and occur only in the causal future of its source.

**Visual.** Field energy flow, source/receiver clock records, object trajectories, and the recoil ledger. This is the first full interaction experiment, and it should follow the cheaper tests.

### 15.9 Test 9 Observer and coordinate invariance

**Question.** Is the same physical detector record obtained under different descriptions?

**Hypothesis.** $\mathcal N_R$ is unchanged by coordinate changes, local Lorentz coframe changes, internal basis changes with transport, and pure momentum relabeling.

**Setup.** Re-express one accepted physical history and its marker events in two coordinate charts. In a flat control, also use a Lorentz-boosted description with correctly transformed initial hypersurface data. Apply nontrivial local spin-frame transformations to $E$ and internal basis changes to the matter/connection.

For the momentum null, one convenient invertible example is $p'_0=p_0$ and $p'_i=p_i\exp(\alpha p_0/M_*)$, where $\alpha$ is a dimensionless relabeling parameter and $M_*>0$ a chosen coordinate scale. Transform the entire phase-space description, not only the momentum labels.

**Observables.** Local event identity, cycle count, overlap records, and conserved quantities in their correct transformed forms.

**Controls.** Deliberately transform a state while leaving its transport or observer fixed; this should expose an inconsistent comparison.

**Gate.** The records agree within the combined numerical reconstruction error. Any claimed relative-locality effect that disappears under a pure relabeling fails.

**Visual.** Different coordinate diagrams paired with one invariant receiver record. The point is agreement of records, not visual agreement of coordinate trajectories.

### 15.10 Test 10 A future topology extension

**Question.** Can a justified spatial topological charge be stabilized without concealing new characteristic behavior?

**Hypothesis.** A separately specified extension supports a nontrivial invariant, resists collapse and unwinding, and has an explicitly healthy perturbation spectrum.

**Prerequisites.** A spatial domain with justified topology and boundary conditions; a field map well-defined everywhere needed; and a fully written extended action.

**Observables.** The invariant under refinement, minimum amplitude where normalization is used, core radius, energy scaling under dilation, perturbation growth, and all characteristic families.

**Controls.** Remove the proposed stabilizer; introduce a permitted amplitude zero; perturb transversely to the fibers; compare at least two independent mesh and domain refinements.

**Gate.** Integer-like output alone does not pass. It must converge, remain dynamically meaningful, and have its protection mechanism identified. A split cone may be acceptable as an effective material property, but fails a claim that all modes share one emergent propagation metric.

**Current classification.** Not evaluated. SS OCF 1 does not claim protected Hopf knots.

### 15.11 Test 11 Shared drift anisotropy and mode dependence

**Question.** Does asymmetric propagation come from a common tilted cone, spatial anisotropy within one cone, material response relative to a geometric sector, or genuinely distinct characteristic structures?

**Competing hypotheses.**

| Hypothesis | Predicted signature | Meaning of a successful test |
|---|---|---|
| Pure coordinate or synchronization change | Coordinate speeds change; the same physical local detector records do not | Representation effect, not new dynamics |
| Shared drift and one spatial cone | A common linear odd-in-wave-number part and common quadratic even part for the designated geometric modes | One effective metric remains viable despite directional asymmetry |
| Geometry with material response | A geometric signal sector and independently derived dispersion or constitutive laws for other modes predict the records | Different effective speeds coexist with a geometric description |
| Several characteristic structures | Mode-dependent principal forms remain after a shared change of description and convergence controls | Reject the all-mode common-cone claim; assess the broader theory separately |

These are competing explanatory targets. None is selected by a visually tilted pulse front alone.

**Setup.** Begin with homogeneous or locally homogeneous backgrounds from an explicitly stated law. For Candidate A, derive the generators from the complete circuit/background; do not insert a trace term and call it a result. For Candidate B, use a valid solution and its transformed descriptions, or label prescribed backgrounds as kinematic controls only.

First validate the inference using the exact constant-coefficient relations of Section 6.5. In a one-dimensional isotropic control, use $v_{\rm d}/c=0,0.25,0.5$. These are equation-generated controls, not new model solutions or observed drift values.

In three dimensions, sample equal-magnitude wave vectors in paired directions $\mathbf k$ and $-\mathbf k$, for several polarizations or fields. Include axial and oblique directions. Start in the regime

$$
v_{\rm d}^i(D^{-1})_{ij}v_{\rm d}^j<1
$$

so the positive-frequency branch can be paired without a sign ambiguity. Track branches by their eigenvectors or physical mode identity, not by switching to whichever root best fits the prediction.

For a massless geometric branch with

$$
\omega_+(\mathbf k)=v_{\rm d}^ik_i+\sqrt{D^{ij}k_ik_j},
$$

define

$$
\omega_{\rm odd}(\mathbf k)=
\frac{\omega_+(\mathbf k)-\omega_+(-\mathbf k)}2,
\qquad
\omega_{\rm even}(\mathbf k)=
\frac{\omega_+(\mathbf k)+\omega_+(-\mathbf k)}2.
$$

The single-metric prediction is

$$
\boxed{
\omega_{\rm odd}=v_{\rm d}^ik_i,\qquad
\omega_{\rm even}^2=D^{ij}k_ik_j.
}
$$

These relations separate drift from the spatial cone shape. Odd directional response alone does not prove drift: require the predicted linear dependence and check for frequency-dependent nonreciprocal corrections. For massive or dispersive material modes, use their independently derived dispersion relation; finite-frequency group-speed differences alone do not establish distinct principal cones.

Fit the three drift components and six symmetric $D$ components using the axis directions and three independent pairwise diagonal directions. Freeze that fit. Test additional oblique directions, wave numbers, and designated geometric sectors that were withheld from the fit.

For a continuum limit of a discrete model, use wavelengths much larger than the microscopic spacing but much smaller than the background variation scale where a local principal description is claimed. Check both the continuum trend and the background-scale separation. Do not confuse the shortest lattice waves with continuum characteristics.

**Operational records.** After the dispersion check, compare round-trip signals and the receiver cycle record $\mathcal N_R$ between physically specified marker events. Keep detector calibration and preparation fixed. If Candidate A has no accepted autonomous clock, report only the dispersion result and mark the clock test not evaluated.

Transform the whole experiment, including the receiver trajectory, clock state, markers, and transport maps, when testing a pure change of coordinates. A physical change of background flow relative to a fixed detector is a different experiment and may change its record. Closed-path timing can test additional effects when the geometry and detector configuration support them.

**Controls.** Zero drift; drift reversal; a pure-coordinate drift of one fixed physical history; a known anisotropic positive $D$ with zero drift; a deliberately two-cone control; internal basis changes with transport; and independent wave-number, spatial-resolution, and domain checks. For varying drift, compare a flat metric in noninertial coordinates with a separately justified curved case. Use curvature and local records to distinguish them.

**Decision criteria.** The pure-coordinate case must preserve $\mathcal N_R$ within combined numerical and readout error. A common-metric fit must predict withheld data within those errors; a systematic residual larger than five times the error estimate on two refinements rejects that fit in the tested regime. A material-response explanation must predict the discrepancy before seeing withheld records. If conditioning, branch identification, clock usability, or scale separation is inadequate, classify the outcome as unresolved.

Do not discard a candidate merely because $v_{\rm d}\ne0$, the two coordinate speeds differ, or $D$ is anisotropic. Do not accept emergent spacetime solely because a scalar dispersion relation can be fitted by a metric. Autonomous geometric dynamics, physical locality, and the relation to clocks remain separate tests.

**Visuals.** Paired directional propagation fronts; odd and even dispersion components; reconstructed cone shape with withheld points; residuals by mode; and invariant clock records shown alongside the different coordinate descriptions.

**Current classification.** Analytical predictions and protocol specified; no new drift simulation or detector experiment has been executed.

## 16 Order of work and stopping rules

With the directional-propagation focus, perform the inexpensive dispersion and coordinate-control part of **Test 11** alongside Tests 3 and 4 before ruling out a geometric interpretation on speed differences alone.

The next object calculation remains **Test 6**, after the action and algebra checks. It determines whether the continuum completion contains an independently readable clock and enables the operational part of Test 11. Without that, another elaborate emission/reception run would repeat the earlier ambiguity.

Candidate A also requires **Test 4**, beginning with its known failure of the strong all-sector cone hypothesis. Its purpose is to distinguish a shared metric, geometry with material memory, and irreducible mode dependence using the complete reciprocal dynamics.

The two lines should remain separately versioned:

~~~mermaid
flowchart TD
    A["Operator algebra and declared assumptions"] --> B["Local event model"]
    A --> C["Dynamical coframe model"]
    B --> D["Full spectrum including memories"]
    C --> E["Bound clock and common cone"]
    D --> F["Compare invariant interaction records"]
    E --> F
~~~

If the microscopic model retains distinct physical cones or stationary preferred memories, reject only the unsupported all-sector common-cone claim. Keep a geometric-sector or medium interpretation open if its causal structure, material response, preferred-frame consequences, and operational clocks can be derived and tested. If those links remain absent, report the emergent-spacetime claim as unresolved.

If the continuum clock cannot remain usable, adjust or reject the clock potential before attempting a two-object link. Do not identify unobservable global phase rotation as a successful clock.

If the continuum interaction works, the result supports a working operator-coframe completion. It does not show that the coframe, four-dimensional domain, or Einstein action were derived from microscopic projectors.

If a future topological extension splits propagation cones, report that result directly and apply the same discrimination. Stable knots, a viable geometric sector, and universal all-sector propagation are separate achievements.

### 16.1 What an executed experiment should deliver

For each future run, preserve the agreed project layout:

~~~text
experiment_name/
  README.md
  Experimental_Setup.pdf
  Experiment_Results.pdf
  Experiment_Analysis_and_Next.md
  plan.json
  results/
    data/
    tables/
    source/
    provenance/
  figures/
~~~

Record the model version, exact action, dimensionless parameters, initial data, solver/configuration hashes, seeds, all attempts, convergence evidence, and the frozen detector calibration. Every figure needs its question, reading, significance, and limitation.

This document is a theory and plan deliverable, not such an executed experiment package. No fabricated results PDF or placeholder simulation evidence is included.

## 17 Assumptions and conclusions at a glance

| Proposition | Status | Reason |
|---|---|---|
| Hermitian $2\times2$ operators support trace and Lorentzian determinant forms | Exact identity | Pauli decomposition |
| Noncollinear positive rays can define a timelike aggregate | Exact identity, physical interpretation conditional | Determinant of the local sum |
| Four tetrahedral projectors span a Lorentzian operator space | Exact identity | Explicit Gram matrix |
| A physical derivative/displacement map is required | Structural conclusion | Internal symmetry alone leaves dynamics undetermined |
| Candidate A is local and reciprocal | Derived from its event ansatz | Participant-only Hamiltonian and conserved matrix ledger |
| Candidate A's selected wave sector has a Weyl-type continuum limit | Derived for the stated routing benchmark | Fourier product and principal determinant |
| Candidate A's zero-wave vacuum gives every physical sector the same wave cone | Contradicted within this candidate | Physical memory perturbations remain stationary |
| Direction-dependent coordinate speeds exclude an emergent metric | False | Drift and spatial anisotropy can belong to one Lorentzian cone |
| The identity part of a Hermitian spatial generator supplies leading drift | Derived when that generator is supplied by a stated law | Determinant depends on $\omega-v_{\rm d}^ik_i$ |
| The original homogeneous three-shift benchmark already generates leading physical drift | Not established by that benchmark | Its small-wave-number generator is traceless |
| Distinct material characteristic cones exclude every emergent-spacetime interpretation | Not established | A geometric sector with derived material response remains an alternative |
| Candidate B has common matter characteristics | Derived from the stated action | Positive $H$ and factorized principal symbol |
| Candidate B derives Einstein gravity from projectors alone | Not established | Curvature action and universal coupling are completion assumptions |
| Candidate B permits a charge-supported core and a bound clock in a controlled limit | Analytically motivated with an explicit existence criterion | Q-ball window and variational clock-well bound |
| A particular finite-amplitude detector is stable and usable | Not evaluated | Requires profile, spectrum, and lifetime calculations |
| Candidate B spontaneously emits neutral radiation from $a=0$ | False in the classical model | Homogeneous neutral equation |
| Internal Hopf geometry guarantees a protected spatial knot | False | Domain, nonvanishing field, and stabilization are additional requirements |
| Either candidate predicts new technical relative locality | Not established | No derived deformed momentum-space dynamics |
| Either candidate predicts Standard Model constants or particle identities | Not established | No corresponding derivation or empirical test |

The conceptual direction is therefore precise: **operators provide a candidate causal algebra; a relational law must make that algebra govern propagation, including possible drift and anisotropy; independently readable clocks must fix its operational scale.** Candidate A tests the microscopic link. Candidate B supplies a complete continuum target whose extra assumptions are visible. Universal propagation is a hypothesis to discriminate, not a restriction that excludes directional dynamics before they are understood.

## 18 Sources provenance and verification

### 18.1 Supplied project evidence

The authoritative starting point was the attached **Signal Space Operator Foundations Roadmap v0.1**, dated 24 September 2026.

The earlier **Signal Space Characteristic Checkpoint**, read from the supplied calculation archive, established a shared-geometry failure for the old quartic orientation extension. Its reported characteristic split is retained as a constraint on this construction; its old numerical results have not been relabeled as new results.

The **Signal Space Two Core Finite Pulse Report**, read from its source archive, described externally scheduled probes and phase-sensitive outgoing records, but did not establish a core-owned calibrated clock or a universal metric. That motivates the explicit $\chi$ clock and local marker-event readout here.

The common-geometry candidate from the continuous-link archive was also inspected for the distinction between sector-specific geometry and universal coupling. Other attached archives were not needed to derive these new laws and are not represented as independently revalidated.

### 18.2 External references and their limited roles

- **[R1]** John C. Baez, *The Octonions*, section on projective lines and Lorentzian geometry. [Author's text](https://math.ucr.edu/home/baez/octonions/node11.html). Supports the established algebraic/spinor background. The explicit formulas here are derived from the displayed definitions.
- **[R2]** Pablo Arrighi and Stefano Facchini, *Quantum walking in curved spacetime in 3+1 dimensions and beyond*. [arXiv:1609.00305](https://arxiv.org/abs/1609.00305). Comparison for local-unitary continuum limits; not a proof of this model's autonomous geometry.
- **[R3]** Sean Carroll, *Lecture Notes on General Relativity*. [Author's notes](https://preposterousuniverse.com/grnotes/). Background for tetrads, the Hilbert action, constraints, and local causal evolution. Our sign convention is stated explicitly.
- **[R4]** Alexander Kusenko, *Small Q balls*. [arXiv:hep-th/9704073](https://arxiv.org/abs/hep-th/9704073). Context for charge-supported scalar solitons. The polynomial window and clock-well bound above are calculated from the proposed action.
- **[R5]** L. Faddeev and A. J. Niemi, *Knots and Particles*. [arXiv:hep-th/9610193](https://arxiv.org/abs/hep-th/9610193). Context for spatial knot solitons, not a particle identification for this theory.
- **[R6]** Érico Goulart, *Nontrivial Causal Structures Engendered by Knotted Solitons*. [arXiv:1410.7656](https://arxiv.org/abs/1410.7656). Characteristic-geometry comparison for Faddeev–Niemi-type textures.
- **[R7]** Willie Wai-Yeung Wong, *Regular hyperbolicity, dominant energy condition and causality for Lagrangian theory of maps*. [arXiv:1011.3029](https://arxiv.org/abs/1011.3029). Supports the need for a separate hyperbolicity audit of derivative nonlinearities.
- **[R8]** G. Amelino-Camelia, L. Freidel, J. Kowalski-Glikman, and L. Smolin, *The principle of relative locality*. [arXiv:1101.0931](https://arxiv.org/abs/1101.0931). Used for the technical meaning of relative locality.
- **[R9]** Felix Finster and Johannes Kleiner, *Causal Fermion Systems as a Candidate for a Unified Physical Theory*. [arXiv:1502.03587](https://arxiv.org/abs/1502.03587). A relevant operator-based variational comparison. Its action is not adopted here and does not supply this document's elementary incidence rule.
- **[R10]** Matt Visser, *Acoustic propagation in fluids: an unexpected example of Lorentzian geometry*. [arXiv:gr-qc/9311028](https://arxiv.org/abs/gr-qc/9311028). An established example of a propagation metric involving flow velocity; not evidence that this program has derived universal spacetime.
- **[R11]** Einstein Online, Max Planck Institute for Gravitational Physics, *The speed of light*. [Institute's explanation](https://www.einstein-online.info/en/speed_of_light/). Distinguishes relativistic measurements with calibrated clocks and rulers from naive velocity subtraction.

### 18.3 Checks performed for this document

The displayed equations were reviewed directly. Small independent floating-point matrix checks reproduced the tetrahedral Gram spectrum, the ordered-walk trace formula, and vanishing derivatives of the event norm and matrix charge. At one seeded noncollinear test point, the norm-derivative residual was $8.9\times10^{-16}$ and the matrix-charge derivative norm was $1.8\times10^{-15}$. The ordered trace residual was $1.1\times10^{-16}$.

These are arithmetic spot checks supporting the written derivations, not dynamical experiments or statistical evidence. No profile, bound eigenmode, scattering event, gravitational evolution, or topology calculation has been numerically executed for either new model.

The completed deliverable is a closed continuum model, a reciprocal event-model candidate, their analytical bridges and obstructions, and an ordered program for deciding which claims survive.

**Directional-propagation revision.** Added the Hermitian drift decomposition, an operator coframe with drift, and Test 11; revised the interpretation of mode splitting and the program's stopping rules. Existing actions and historical results are retained. A direct matrix-inverse check verifies the drift metric's displayed covariant and contravariant forms. The revision adds no executed evolution or empirical result.

### 18.4 Input fingerprints

SHA-256 fingerprints identify the exact supplied bytes used for the source audit. Archive contents were read directly; historical solvers were not executed.

| Supplied file | SHA-256 |
|---|---|
| Signal_Space_Operator_Foundations_Roadmap_v0.1.md | f443368234314093628cabeb881c916aafd7bc3191ac341be041aceda90da11a |
| 05-Signal_Space_Continuous_Link_and_Geometry_Source.zip | cd13aae23b033c8de2a5a7a856cdf73feb667c7a424e61847058fdc8d5c52b8c |
| 06-Signal_Space_Characteristic_Checkpoint_Calculations.zip | c33a27e73aa26bf8585a133863a559f043da13b58012c28d63e8460831382492 |
| 07-Signal_Space_Two_Core_Finite_Pulse_Source.zip | d34be218413bfb3fbb4eb1739f977730e258aa3e647db4f390b5444f31a5b9ed |
