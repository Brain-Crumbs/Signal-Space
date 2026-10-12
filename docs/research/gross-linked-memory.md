# GROSS v0.3 linked-memory persistence seed

Experiment `gross.linked-memory-persistence.v1`; unchanged model
`signal-space.ss-ops-1.v1`, $\lambda=0$. Preparation packet v0.1 was inspected
at main `9668e7394fc463075546971448a4d0b923d2a06e`. Its JSON SHA-256 is
`cd96483516183eab5716103828d24780a1a893b9c27e6712bd62aaee9bfd913d`.
The equation authority is [Operator Program v0.2 section 5](../../research/papers/gross-operator-program-v0.2.md),
SHA-256 `c733c958fde54c810c38889e5096de54358a77cc10e69d9f885870832595e123`;
it matches the supplied v0.2-1 attachment byte for byte.
[Program v0.3](gross-research-program-v0.3.md) supplies F0/F2/C1 priorities.

Status: implementation and engineering validation, campaign execution pending.
No Tests 1-11 classification changes. This seed does not finish the four-ray
F2 classification, establish an autonomous clock or infer physical geometry.
The current repository experiment-pipeline/planner/runner skills implement the
Signal Space experiment workflow named in the project instructions.

## Supplied incidence and unchanged law

Three coherent ports $z_i\in\mathbb C^2$, $i=1,2,3$, have total initial norm
$N=\sum_i z_i^\dagger z_i=1$. Unit memory spinors $w_A,w_B$ represent projectors
$P_a=w_aw_a^\dagger$. Their individual phases are unphysical. Event A uses
ports (1,2), event B uses (2,3), with identity wire transport. Each gate has
dimensionless parameter $s\in[0,1]$ and $\kappa=\pi/2$. All amplitudes and
couplings are dimensionless. A repeated A,B word is an unfolded ordered causal
history, not an instantaneous loop. No space, physical distance, mesh, external
input or proper-time clock is supplied.

For the active event and ports $i,j$, put $d=z_i-z_j$ and $D=dd^\dagger$.
The Hamiltonian and equations remain

$$
H_a=\kappa d^\dagger P_a d,\qquad
i\dot z_i=\kappa P_a d,\quad i\dot z_j=-\kappa P_a d,\quad
\dot P_a=-i\kappa[D,P_a].
$$

Inactive variables stay fixed. The existing `models/reciprocal.py:exact_gate`
is the baseline. It uses constant $S=D+2P_a$, $q=d^\dagger d$ and
$m=w_a^\dagger w_a$: $R(s)=\exp(-i\kappa Ss)$,
$d(s)=\exp(i\kappa qs)R(s)d(0)$ and
$w_a(s)=\exp(2i\kappa ms)R(s)w_a(0)$. The sum $z_i+z_j$ stays fixed.
No renormalization is applied during physical evolution.

The circuit conserves $N$ and
$J=\sum_i z_iz_i^\dagger+P_A+P_B$. Each event conserves its own $H_a$;
switching does not define a single conserved autonomous energy.

## Coherent representation and complement constraints

Stack all ports into $Z\in\mathbb C^6$ and retain the full $W=ZZ^\dagger$.
The active $6$ by $6$ Hermitian generator embeds diagonal blocks $\kappa P_a$
and off-diagonal blocks $-\kappa P_a$ at participating ports. Then

$$
\dot W=-i[K(P_a),W],\qquad
D=W_{ii}+W_{jj}-W_{ij}-W_{ji}.
$$

The memory equation closes using that $D$. This is a pure-data representation
equivalence modulo common wave phase; it is not a mixed-state ensemble closure
or a local distributed storage theorem. The independent operator solver
integrates all 36 complex W entries and all memory entries without projecting
them back to their constraints.

For $C=P_A+P_B-I$, let $c=\|C\|_F$ and $o=\mathrm{tr}(P_AP_B)$.
Rank-one unit memories satisfy the exact check $c^2=2o$. During the active
event $\dot C=-i\kappa[D,P_a]$. Since the other memory stays fixed,
continuous complement persistence requires the active commutator to vanish
throughout the word. Endpoint return is a different claim.

### Correction made before plan locking

Keep all seven original nominal preparations. Rename preparation 2
**initially-commuting**, and withdraw the packet's incorrect assertion that
its full A,B word is an exact persistence control. Initially it has
$z_1=e_1/\sqrt2,z_2=0,z_3=e_2/\sqrt2$, $P_A=e_1e_1^\dagger$,
$P_B=e_2e_2^\dagger$, where $e_1=(1,0)$, $e_2=(0,1)$.
During A, $d(s)=\exp(-i\pi s)e_1/\sqrt2$. At its endpoint $z_1=0$,
$z_2=e_1/\sqrt2$. Thus the next event starts with

$$
D_B=\frac12\begin{pmatrix}1&-1\\-1&1\end{pmatrix},\qquad
\|\dot C_B\|_F=\frac{\kappa}{\sqrt2}>0.
$$

Its isolated A and isolated B words do preserve the projectors and supply
exact commuting controls. The unchanged dark preparation is the exact full-word
stationary control. The active-plus preparation already has
$\|\dot C_A(0)\|_F=\sqrt2\kappa/3>0$. Consequently universal continuous
complement persistence is analytically contradicted before a campaign run.
This correction changes a false prediction, not the action, initial states or
numerical acceptance thresholds. Original packet bytes remain preserved.

The seven deterministic cases are dark, initially-commuting, active-plus,
active-minus, noncomplement, coherence-plus, and coherence-minus; their exact
arrays are declared in `models/linked_memory.py`. The two coherence witnesses
have $z_1=e_1/\sqrt2$, $z_2=\pm e_1/\sqrt2$, $z_3=0$ and
$P_A=(I+\sigma_x)/2$. Individual local ray operators agree, but $H_A=0$
and $H_A=\kappa$ respectively. No random case selection is performed.

## Full physical sensitivity

The chart retains twelve real wave directions and two horizontal memory-ray
directions per memory, for sixteen real inputs before imposing fixed N or
quotienting common wave phase. No fixed-J constraint deletes internal-orientation
or memory directions. For $w=(a,b)$, use the orthogonal complex vector
$v=(-\overline b,\overline a)$ and real tangent directions $v,iv$.
Finite chart changes normalize only the prepared memories; they do not
renormalize during the dynamics.

For perturbations $\delta d=\delta z_i-\delta z_j$ and $\eta=\delta w_a$,
$\delta P=\eta w_a^\dagger+w_a\eta^\dagger$ and
$\delta D=\delta d d^\dagger+d\delta d^\dagger$. The variational equations are

$$
i\delta\dot z_i=\kappa(\delta P d+P\delta d),\qquad
i\delta\dot z_j=-\kappa(\delta P d+P\delta d),\qquad
i\dot\eta=\kappa(\delta D w_a+D\eta).
$$

The numerical tangent differentiates the existing exact gate using the Frechet
derivative of the matrix exponential, including derivatives of S,q,m and all
phase factors. Independent ODE variational tests and centered differences at
$10^{-5}$ and $5\times10^{-6}$ check this derivative. The complete chain rule
carries variations through both events; it never resets at a cycle boundary.

Output features are the wave amplitudes and $P_A/\sqrt2,P_B/\sqrt2$.
On horizontal memory tangents $\|\delta P\|_F=\sqrt2\|\eta\|$,
so the feature derivative measures the declared physical tangent norm without
unobservable memory phases. Retaining a common wave phase here is explicit;
the norm bounds also use amplitude coordinates. No separate port phase fit is
allowed. The largest singular value is finite-time amplification, not Floquet
stability without a verified recurrent orbit and its phase treatment.
The two active phase preparations receive at most 32-cycle studies.

Local mathematical records are $r_i=|w_a^\dagger z_i|^2$, $r_j$ and
$q_a=|w_a^\dagger d|^2$. Their derivatives retain both wave and memory terms.
These are declared observation functions, not autonomous hardware.

## Closed-region comparison and its obstruction

Use the lifted norm $\|\delta x\|^2=\sum_i\|\delta z_i\|^2+
\sum_a\|\delta w_a\|^2$. For two exact preparations with initial error
$\varepsilon\le10^{-6}$, conservation closes the region: both have unit
memory norms and total wave norm at most $R=1+\varepsilon$. Every straight
segment between their states stays within these convex balls. Put $n=R^2$.
With $a=\|\delta z\|$ and $b=\|\delta w_a\|$, the vector-field derivative obeys

$$
\begin{pmatrix}\|\delta f_z\|\\\|\delta f_w\|\end{pmatrix}
\le |\kappa|
\begin{pmatrix}2&4\sqrt n\\4\sqrt n&2n\end{pmatrix}
\begin{pmatrix}a\\b\end{pmatrix}.
$$

Here $\|d\|\le\sqrt{2n}$, $\|\delta d\|\le\sqrt2 a$, and
$\|\delta P\|\le2b$ justify each entry. A valid common Lipschitz constant is

$$
L=|\kappa|\left(1+n+\sqrt{(1-n)^2+16n}\right).
$$

It approaches $6|\kappa|$ as $\varepsilon\to0$. The common record Lipschitz
constant $K_q=4\sqrt{n+n^2}$ follows from
$|\delta q_a|\le4\sqrt n a+4n b$; it also bounds $r_i,r_j$.
For exact trajectories, the initial-state contribution after c full cycles is
$K_q\varepsilon\exp(2Lc)$. A separate range bound caps any record difference
by $2n$; logs avoid overflow when evaluating the minimum of these bounds.

For an approximate trajectory y, a residual $r=\dot y-f(y)$ adds its
exponentially weighted integral, provided a valid region for y is actually
enclosed. No conservation assumption automatically closes an approximate
trajectory's region. The runtime does **not** claim that enclosure or validated
floating residual/roundoff. Empirical tolerance refinement is not a certificate.

The target absolute record error is $10^{-3}$, with $2.5\times10^{-4}$ each
for preparation, integration/roundoff, omitted approximation and readout.
The conservative exact-law preparation estimate already exceeds its allocation
after the first full cycle: its usable full-cycle horizon is zero. This is a
limitation of this bound, not proof that nearby trajectories cannot predict
records. The end-to-end numerical/readout certification stays unresolved,
even if empirical errors are small. Ideal exact records and zero physical
forcing do not establish real detector accuracy.

## Numerical controls, decisions and resources

Save 17 samples including both endpoints per gate. DOP853 uses rtol $10^{-11}$,
atol $10^{-13}$ and max step $1/16$; halve both tolerances and save 33 samples.
Audit N, J, each event H, Hermiticity, memory trace/idempotence, W purity and
positivity, local records, complement defect and overlap. Require normalized
state/record and ledger errors at most $10^{-9}$ on both refinements. Retain
all operator blocks, intensities, matrix-charge components and Bloch coordinates.

All seven cases receive isolated A/B, reversed B,A, frozen-memory, fixed global
unitary and common-wave-phase controls. Reverse order is a different apparatus
and is not required to agree. Frozen memory is deliberately nonreciprocal.
Compare sensitivity differences relatively to $\max(1,\|T\|_F)$ with limit
$10^{-4}$ at every measured prefix. A long-horizon failure remains a failure;
reporting an earlier resolved derivative does not erase it.

Continuous complementarity is falsified by the nonzero analytical derivative.
Numerical endpoint persistence is falsified only by a defect exceeding five
times the comparison budget with passing numerical gates; sampled agreement
alone remains unresolved. Missing/nonfinite coverage cannot pass. Scientific
failure or unresolved certification can coexist with successful software and
package verification.

The ceiling is 300 CPU/wall seconds, 1024 MiB memory, 128 MiB output and one
native thread. The campaign allows at most 64 cycles; the locked config fixes
the actual horizon. An engineering fixture tests one cycle; it is not the
campaign. The runtime enforces limits and preserves completed raw files plus
partial traces on cancellation/failure. No restart is advertised.

## Acceptance map and planned visual evidence

| Packet item | Implementation/evidence | Campaign status before launch |
| --- | --- | --- |
| A1 pinned action and incidence | This protocol; closed schema; exact_gate adapter | Not evaluated |
| A2 coherent lift and phase witness | Independent W/P integration; unit tests | Not evaluated |
| A3 continuous and endpoint audit | Constraint derivative; 17/33 within-event samples | Not evaluated |
| A4 complete tangent sectors | Frechet derivative, independent ODE, centered refinement | Not evaluated |
| A5 bound or explicit obstruction | Closed exact-region bound; zero-cycle conservative horizon; missing enclosure disclosed | Certification unresolved |
| A6 controls and immutable records | Registered runtime, cancellation and strict raw coverage | Not evaluated |
| A7 canonical/reader packaging | Saved-data report; five questions and four-part interpretations | Not evaluated |

Five required figures separate (1) supplied incidence from internal Bloch motion,
(2) within-gate complement defect from endpoints, (3) coherent numerical mismatch
from the phase witness, (4) full finite-time amplification and record sectors,
and (5) observed errors from the conditional bound and budget. Exact plot data,
transforms, Question/Reading/Significance/Limitation accompany every figure.

To validate and estimate the locked plan without running:

```sh
python .agents/scripts/run_plan.py --plan docs/research/plans/gross-linked-memory.json --repo-root . --workspace ../linked-memory-campaign --threads 1
```

After separate campaign authorization, a clean checkout supports the complete
canonical/reader pipeline:

```sh
python -m signal_space pipeline --experiment gross-linked-memory --output ../linked-memory-campaign --threads 1
```

This implementation request stops after engineering validation and lock.
Existing Test 2 fixtures, plans and checksummed evidence remain byte-identical.
