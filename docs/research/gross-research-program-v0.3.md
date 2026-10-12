# GROSS research program v0.3

Date: 12 October 2026. Status: research-design and documentation revision;
no new model, registered experiment, simulation or scientific acceptance.
The [source comparison](gross-projector-control-audit.md) and
[claim register](gross-claim-register.md) give provenance and evidence classes.
The [v0.2 model document](../../research/papers/gross-operator-program-v0.2.md)
remains the equation authority for existing registered work.

## 1. Research objective and tracks

Develop local dynamics of coherent signals and projector memories, determine
which structures and records remain predictable, and investigate when an
operational geometric description follows. Begin with internal state spaces and
explicit event incidence. No physical spacetime manifold, spatial dimension,
metric or Einstein law is presumed in this foundation track.

| Track | Question | Existing starting point | Required new evidence |
| --- | --- | --- | --- |
| F: projector, signal and memory foundation | Which configurations persist, which memories are needed, and what can local/boundary records identify? | October 4 Projector Geometry and Memory program and atlas; Candidate A reciprocal event law | Classifications, obstruction witnesses, observable quotients and stable/finite-horizon regimes |
| C: certification and control | How does an approximate structure or measured residual bound actual state and record errors? | Exact gates, sensitivity maps, NLS structure/phase/remainder example and the specified hoop invariant-region certificate | Appropriate inverse/sensitivity, nonlinear remainder, phase and readout bounds for each new model |
| B: continuum benchmark | Can the specified continuum action support calibrated objects, reception and exchange? | Candidate B and registered work for Tests 5-8; observer-invariance Test 9 remains not evaluated | Those experiments' own locked acceptance evidence |

Track C is shared methodology, not a proved transfer theorem between models.
Track B supplies a working target and comparison cases. Its success does not
complete Track F. A derivation relating the two remains a separate conjecture
requiring a state map, scaling limit, error bounds and record correspondence.

## 2. Operator constitution before physical interpretation

The Pauli matrices obey $\sigma_i^2=I$ and have eigenvalues $+1,-1$.
They generate rank-one orthogonal projectors through

$$
P(\mathbf n)=\frac12(I+\mathbf n\cdot\boldsymbol\sigma),
\qquad |\mathbf n|=1,\qquad P^2=P=P^\dagger.
$$

The direction $\mathbf n$ is an internal Bloch coordinate. A polyhedron here
usually means a finite family of these projectors, not a larger matrix or a
polyhedron-shaped projection operator.

| Object | Mathematical size | What does not follow |
| --- | --- | --- |
| Unrestricted complex scalar / 1 by 1 matrix | Two real components | A Hermitian scalar is instead real; an orthogonal scalar projector is only 0 or 1 |
| Rank-one projector on $\mathbb C^2$ | $\mathbb{CP}^{1}$, two real parameters | A physical spatial sphere, ray or propagation direction |
| General Hermitian 2 by 2 operator | Four real coefficients, $X=x^0I+\mathbf x\cdot\boldsymbol\sigma$ | Four physical spacetime coordinates |
| Hermitian $n$ by $n$ operator | $n^2$ real coefficients | $n^2$ physical spacetime dimensions |
| Rank-one projector on $\mathbb C^n$ | $\mathbb{CP}^{n-1}$, $2(n-1)$ real parameters | A chosen graph dimension or a universal metric |
| Rank-$r$ projector on $\mathbb C^n$ | Complex Grassmannian, $2r(n-r)$ real parameters | A continuous rank-changing law while exact idempotence holds |

For the 2 by 2 Hermitian space,

$$
\det X=(x^0)^2-|\mathbf x|^2.
$$

This is an exact Lorentzian quadratic form on operator coefficients. Making it
govern physical propagation additionally requires a local law and a link to
accessible event records. Rank-one projectors have fixed trace; weighted
positive operators supply the interior of the associated positive cone.
An arbitrary larger complex Hermitian matrix has a degree-$n$ determinant,
so its entire determinant is not automatically a Lorentzian quadratic form.
For $n>2$, pure projectors obey constraints beyond a single Bloch-vector norm.

Choose matrix dimension, projector rank, coherent variables, allowed basis
changes, weights and transport explicitly before studying an extension.
Symmetry does not uniquely select dynamics or a physical dimension.

## 3. The retained state is not a collection of independent rays alone

The existing reciprocal model keeps port amplitudes $z_j\in\mathbb C^2$
and independent memory projectors $P_a$. Relative phases of different
ports matter. For the baseline with the onsite parameter $\lambda=0$,
one event uses

$$
d=z_1-z_2,\qquad H_e=\kappa d^\dagger P d,\qquad
i\dot z_1=\kappa P d,\quad i\dot z_2=-\kappa P d,\quad
\dot P=-i\kappa[dd^\dagger,P].
$$

Replacing each port by its own weighted ray $z_jz_j^\dagger$ loses required
cross-port coherence. For example, $z_1=e_1$, $z_2=\pm e_1$ and
$P=(I+\sigma_x)/2$, with $\kappa\ne0$, have identical individual port operators, but $H_e$ is
respectively $0$ and $2\kappa$. Their future dynamics differ.

A faithful finite operator representation is available: stack the retained
ports into $Z$, set $W=ZZ^\dagger$, and retain all coherent blocks
$W_{ij}=z_i z_j^\dagger$. With the Hermitian event block

$$
K(P)=\kappa\begin{pmatrix}P&-P\\-P&P\end{pmatrix},
\qquad D=W_{11}+W_{22}-W_{12}-W_{21},
$$

embedded at the participating ports,

$$
\dot W=-i[K(P),W],\qquad \dot P=-i\kappa[D,P].
$$

These equations are the outer-product specialization of the same baseline
event law. They introduce no metric or manifold. For admissible pure data they
preserve positivity, rank one and $N=\mathrm{tr}W$. If $N>0$, $W/N$ is a
projector, but $N$ must also be retained because it sets interaction strength.
Only the common wave phase is quotiented; relative port phases remain in the
off-diagonal blocks. An external coherent reference must be included or declared
as a boundary input.

This is an exact change of representation, not an originality claim or an
implemented local distributed algorithm. With $N_p$ ports, $W$ is
$2N_p$ by $2N_p$ and has $N_p^2$ coherent blocks. Remote idle diagonal blocks
do not change during a disjoint event. Changing cross-correlations is not
physical influence on their local records. Sparse storage, locally accessible
reconstruction and useful compression remain questions to prove. A mixed
positive $W$ is not automatically equivalent to an ensemble of the original
memory-coupled pure trajectories.

## 4. Keep the supplied structures visible

| Structure | Foundation-track treatment |
| --- | --- |
| Hilbert inner product and Hermitian adjoint | Supplied mathematical structure defining orthogonality |
| Which states meet | Explicit graph/event incidence, initially supplied |
| Order of shared events | Part of the local law; disjoint-event rescheduling must preserve records |
| Comparison of different internal frames | Declared transports and gauge conventions |
| Gate parameter and cycle count | Mathematical ordering parameters until physical calibration is obtained |
| Periodic graph labels, Euclidean embedding, wire delays | Optional benchmark assumptions, not emerged geometry |
| Boundary input, output loss, measurement noise, ensemble | Declared preparation and observation assumptions |
| Physical dimension, distance, proper time, metric dynamics | Research outputs to establish or explicit assumptions of a separate benchmark |

The tetrahedron-octahedron example supplies an FCC embedding and identifies
face normals with internal directions. Preserve it as a useful specified
architecture. Its embedding cannot count as dimensional emergence.

Graph incidence can remain a primitive for a limited metric-reconstruction
goal. Deriving incidence or selecting a spatial dimension is a stronger goal
requiring an explicit local edge law or a justified selection principle.
Neither follows from choosing Pauli matrices.

## 5. What residual/control methods add

Physical memory projectors $P_a$ are state variables in the interaction law.
Analysis projections $\Pi_{\rm tan},\Pi_{\rm normal}$ instead decompose
variations in a tangent space. They can share idempotence algebra while acting
on different spaces and having different meanings.

For exact dynamics $\dot x=f(x)$ and an approximate trajectory $y$, define
$r=\dot y-f(y)$ and $e=x-y$. Then

$$
\dot e=f(y+e)-f(y)-r.
$$

In an admissible region where $f$ is $L$-Lipschitz, while both trajectories
remain in that region,

$$
\|e(t)\|\le e^{Lt}\|e(0)\|
+\int_0^t e^{L(t-s)}\|r(s)\|\,ds.
$$

The formula identifies the missing sensitivity amplification. A certificate
must close the region/bootstrap and enclose discretization and omitted tails.
Small residual alone proves neither a nearby periodic solution nor stability.

The first-order correction $v$ satisfies
$\dot v-J(t)v=-r$, where $J(t)=Df(y(t))$. In a moving orthonormal frame $Q(t)$,
the linear variation operator is

$$
Q^\mathsf T J Q-Q^\mathsf T\dot Q.
$$

The frame-motion term must remain. Tangent and normal variations are not
automatically decoupled. Projector constraints and gauge directions require a
valid manifold chart or tangent construction.

Separate five questions:

1. **Existence:** does residual plus an inverse and nonlinear correction bound
   establish a nearby exact structure?
2. **Orbital confinement:** can shape stay in a certified region after allowed
   phase/translation alignment?
3. **Timing:** how much do the physical local marker events shift?
4. **Stability/lifetime:** how do perturbations and leakage evolve over the
   stated horizon?
5. **Observation:** can accessible records distinguish the relevant changes
   with a controlled inverse/conditioning bound?

Phase alignment can define orbital distance; it must not erase the timing
signal being tested. A constant bound on shape need not bound phase error.
The NLS scattering example motivates adapted coordinates, but does not make
Candidate A or the full Candidate B action integrable NLS.

The latest verified hoop guide reports a specific all-time invariant-region
and whole-cycle sweep certificate for its exact periodic motor. It does not
reset a finite-time comparison each cycle. Its existence, inverse/twist,
rounding, Fourier-tail and barrier obligations illustrate the required
discipline; their values and hypotheses do not transfer to projector networks.
That certificate was read, not rerun in this documentation audit.

A prescribed control input is a separate model assumption. Newton correction
or residual minimization used to prepare a candidate is an analysis operation.
An actuator or feedback controller applied during physical evolution must have
its own declared dynamics and work/transfer account. A driven-system certificate
does not by itself establish an autonomous clock.

## 6. Prioritized analytical work

Retain the October 4 program's six packages. Add explicit constitution and
certification deliverables rather than replacing the program with a large
continuum simulation.

| Priority | Work | Decisive output |
| --- | --- | --- |
| F0 | Fix primitive variables and coherent information; compare local rays with the exact operator lift | A state/record equivalence statement, lost-information witness and declared locality/storage costs |
| F1 | Labelled square/tetrahedron complements; two copies and one parity cycle | Admissible-map and gluing classification, including obstructions |
| F2 | Two linked memories and a four-ray frame under a complete reciprocal word | Constraint derivatives; continuous versus endpoint frame persistence; deformation witnesses |
| C1 | Derive correction and record-error bounds for the same small family | A model-specific inverse or finite-time sensitivity bound, phase budget and horizon; an explicit obstruction if these fail |
| F3-F4 | Boundary inverse and predictive quotient on the same retained chain | Gauge-aware rank/conditioning, blind families, hidden-memory lower bounds and withheld-input predictions |
| F5 | Preparation-band prediction with geometrically restricted partitions | Event uncertainty and resolution/memory cost bounds; separate first-exit survival from endpoint retention and mixing |
| F6 | A selected small periodic architecture, retaining all tangent sectors | Complete ordered symbol, active stability, first anisotropy and localization qualifications |

The later active-resonance source reports exact connected recurrence and strong
instability for three selected preparations. This rejects those preparations
as stable hosts; it does not rule out all active families. Conserved-charge
constraints cannot silently delete their genuine growing modes. A scheduled
event Hamiltonian also does not automatically define autonomous global energy;
switching work or an explicit clockwork completion must be accounted for.

A graph cage is a confinement control. A recurrence in that cage is not a
self-binding theorem. Evaluate finite-horizon usefulness when all-time
stability is unavailable, with actual readout disturbance included.

## 7. Operational geometry and the continuum benchmark

Only after a usable response/clock regime is established should an operational geometric
description be inferred from independent records. Keep graph volume growth,
connectivity diagnostics, internal rank, propagation dimension and calibrated
observer geometry distinct. A conditional cone fit in a declared four-coordinate
chart is not a derivation of that chart.

Derive the complete signal/memory response before eliminating hidden variables.
Memory elimination generally leaves a retarded kernel; a local approximation
requires a controlled resolvent away from memory poles. Fit candidate geometry
on one calibrated probe family, freeze it, and predict withheld families.
Compare a material-response model, pure frame relabeling, and a shared
geometric explanation. A common principal cone alone does not prove gravity
or universal clock coupling.

Candidate B remains useful for this operational benchmark. It explicitly
assumes the four-dimensional domain, the coframe/metric correspondence,
universal metric coupling and the Einstein curvature action. Flat core/clock
experiments further choose the gravity-decoupling limit. Test 8 can validate
exchange within that action; it cannot establish those assumptions as emerged.

Before expanding its expensive pair campaign, qualify mesh-consistent
preparation and a physically useful receiver response. A separately specified
finite reference-wave receiver can be explored: neutral forcing about a
nonzero reference contains a cross term linear in a small signal. Its timing,
reference energy, phase blindness, spatial averaging, recoil and clock survival
must be tested with reference-only and signal-reversal controls.
This is a proposed protocol, not an executed result, spontaneous emission or
a reinterpretation of the original Test 8.

## 8. Versioning and completion

This revision changes research priorities and documentation, not model laws,
runtime interfaces, canonical evidence or locked Tests 1-11 criteria.
Higher matrix dimensions, graph selection, stabilizing terms, detector laws
and new receiver preparations each need an explicit model/protocol definition
before execution. A failed test remains failed under its original definition.

The next foundation deliverable is a small-network constitution/persistence
and certification problem, ending in a theorem, counterexample or explicit
conditioning/stability obstruction. No new calculation is authorized merely
by appearing in this roadmap.
