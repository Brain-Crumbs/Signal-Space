# C1-1: full-direction local-record theorem

This is the conditional mathematical contract for [#93](https://github.com/Brain-Crumbs/Signal-Space/issues/93)
under [#92](https://github.com/Brain-Crumbs/Signal-Space/issues/92), not an executed
certificate. The [source audit](gross-local-record-source-audit.md) and
[SHA-256 manifest](gross-local-record-sources.json) pin the authority and
implementation bytes. No pilot, confirmation, numerical enclosure backend, or
positive certified horizon is supplied here. All inequalities below are exact
real mathematical inequalities; future software must enclose their evaluation.

## Model, coordinates and observations

Use Candidate A, `signal-space.ss-ops-1.v1`, lambda=0, kappa=pi/2,
identity transport, and ordered A=(1,2,A), B=(2,3,B). Each gate has s in [0,1].
The two exact seed definitions are

    z1=e1/sqrt(3), z2=e2/sqrt(3), z3=(e1 +/- i e2)/sqrt(6),
    PA=e1 e1†, PB=e2 e2†.

Square roots and pi here denote exact real constants. Floating preparations
are references to these seeds, not replacements for them. Set
X=(Re z, Im z, xA, xB) in R^18, P_a=I/2+x_a·sigma. The real and imaginary
wave components may be interleaved instead; use one fixed orthonormal ordering.
Physical memories have |x_a|=1/2. Since tr(sigma_i sigma_j)=2 delta_ij,

    ||delta X||² = sum_i ||delta z_i||² + (1/2)sum_a ||delta P_a||F².

This is an 18-dimensional ambient space with a 16-dimensional physical
preparation manifold. The retained wave directions include common wave phase,
total-norm-changing directions and matrix-charge-changing directions. No
constraint on conserved quantities is imposed on perturbations.
For each endpoint the active event defines records r=v†Pv, with v=z_i,z_j,
or z_i-z_j, respectively. The corresponding wave selectors have norms
a=1,1,sqrt(2). These are mathematical observations, not detector laws.

## Exact gate and its Hermitian ambient extension

For any complex waves and **any Hermitian trace-one P**, not necessarily
positive or idempotent, put d=z_i-z_j, b=z_i+z_j, D=dd†, q=d†d,
S=D+2P and U(s)=exp(-i kappa s S). Define

    d(s)=exp(i kappa s q) U(s)d,
    P(s)=U(s)P U(s)†, z_i,j(s)=[b +/- d(s)]/2.

Inactive waves and the other memory remain fixed. This defines F_s on all
R^18. In particular no projection or normalization of an off-manifold
reference is part of F_s.

Proof: the operator-program §5 equations at lambda=0 give
b'=0, d'=-2i kappa P d, P'=-i kappa[D,P]. Thus
D'=-2i kappa[P,D], S'=0 and q'=0, using Hermiticity. Conversely the displayed
formula gives D(s)=U D U† and S=D(s)+2P(s), because U commutes with S.
Differentiating d(s) and using D(s)d(s)=q d(s) yields
 d'=-i kappa(S-qI)d=-2i kappa P(s)d.
Differentiating P(s) gives its stated commutator equation. Thus the formulas
solve the law with the prescribed initial data for the whole real s axis.
For a physical memory represented by unit w, its spinor lift is
w(s)=exp(2i kappa s)U(s)w; the phase cancels in P. This agrees with
`reciprocal.exact_gate` at m=1 and lambda=0. For a general Hermitian P there
need not be a spinor w, and that spinor implementation must not be used as
an ambient map by silently projecting P.

The invariant quantities are q, b, the spectrum and trace of P,
N=sum_i ||z_i||², and the full charge J=sum_i z_i z_i†+PA+PB.
Indeed the active wave contribution is (bb†+D)/2, so its derivative cancels
P'. The event Hamiltonian H=kappa tr(DP) is invariant because D and P are
conjugated by the same U. Switching events does not give a single conserved
autonomous H. Physical projector positivity and rank persist by unitarity;
these invariants also hold for the ambient law wherever meaningful, without
making an indefinite Hermitian memory physical.

The matrix exponential power series converges locally uniformly with all
finite derivatives (on ||A||<=M, its differentiated series are dominated by
finite polynomials times exp(M)). Therefore F_s is real analytic everywhere,
including q=0 and repeated eigenvalues of S. An eigengap or a smoothly chosen
eigenbasis is not an assumption. One may obtain exponential derivatives by
differentiating the power series or the defining ODE; for example
D exp(A)[E]=integral_0^1 exp((1-t)A) E exp(tA) dt. The latter identity follows
by solving the differentiated linear ODE via variation of constants, so no
external regularity or spectral theorem beyond finite-dimensional Hermitian
unitarity is being imported as an unexamined numerical hypothesis.

## Chart, its remainder, and the entire physical ball

Fix each exact seed spinor w and its orthogonal unit v=(-conj(w2),conj(w1)).
For u in R^16 use twelve additive wave coordinates and, for each memory,
eta=(u_a1+i u_a2)v, t=||eta||. Define the preparation C(u) by these waves
and w(u)=(w+eta)/sqrt(1+t²), P(u)=w(u)w(u)†. This normalization applies
only to preparation. Let X*=C(0), J0=DC(0). Its memory part is
eta w†+w eta†, whose Frobenius norm divided by sqrt(2) is ||eta||.
The wave and two memory sectors are orthogonal; hence J0:R^16→R^18
is an isometry, retaining all sixteen directions simultaneously.

In the orthonormal basis (w,eta/t), the memory remainder after subtraction
of the constant and linear terms is

    (1/(1+t²)) [ -t²  -t³ ; -t³  t² ],

with harmless phase factors if eta/t is given a different convention.
Its physical norm is t²/sqrt(1+t²)<=t². The squared full remainder is the
sum of the two squared memory remainders, at most (sum_a t_a²)²<=||u||^4.
Consequently ||C(u)-X*-J0 u||<=||u||², and also
||C(u)-X*||<=||u|| (the memory chord is t/sqrt(1+t²)).

Conversely let a physical preparation be at chordal distance <=epsilon<1
from X*. For each memory its chord c_a satisfies
c_a²=(1/2)||P'_a-P_a||F²=1-|w†w'|². Since c_a<1, fix the representative
phase so w†w'>0 and set eta=w'/(w†w')-w. Then eta is horizontal and
 t_a²=c_a²/(1-c_a²).
If h is the wave displacement, ||h||²+sum c_a²<=epsilon², so

    ||u||²=||h||²+sum c_a²/(1-c_a²)
           <=epsilon²/(1-epsilon²)=ec².

Thus epsilon=1e-6 is covered by ec=epsilon/sqrt(1-epsilon²), including
arbitrary combinations across all sectors. Enclosing the larger chart ball
may be conservative; it is not legitimate to replace it by sixteen lines.
The bound does not cover orthogonal memories at epsilon=1; that excluded
chart singularity explains the strict condition. Exact seeds and J0 are the
centers here; their finite arithmetic errors enter the computed theorem below.

## Domains, curvature and exact-reference theorem

Let n=0,...,m-1 index ordered gates, F_n the appropriate A or B endpoint map,
X_0=X*, X_(n+1)=F_n(X_n), E_n=DF_n(X_n), and J_(n+1)=E_n J_n.
Fix ec as above. Choose finite closed convex domains D_n containing X_n
and its complete Euclidean ball of declared radius R_n (a larger convex
set is permitted). Require a nonnegative bound

    H_n >= sup_{X in D_n} ||D²F_n(X)||,

where the bilinear operator norm is sup over both unit real inputs, and
all derivatives and outputs use the 18-coordinate Euclidean norm. The
map is smooth on a neighborhood of D_n. These are **full ambient** bounds,
not merely bounds along the physical orbit, on the tangent columns, or on
the boundary of a tube. Compactness ensures finite bounds exist; it does
not compute a useful bound or validate one.

Take Q0=ec² and recursively choose outward upper bounds

    R_n=ec ||J_n||+Q_n,
    Q_(n+1)>=||E_n|| Q_n + (H_n/2) R_n².

For every ||u||<=ec, induction gives
X_n(u)-X_n=J_n u+q_n(u), ||q_n(u)||<=Q_n.
To prove the step, apply twice the fundamental theorem of calculus along
the segment from X_n to X_n+delta:
F(X_n+delta)=F(X_n)+E_n delta+
 integral_0^1 (1-t)D²F(X_n+t delta)[delta,delta]dt.
The segment is in D_n by the prior radius and convexity, and its integral
has norm <=H_n||delta||²/2. This proves the recurrence without assuming
what the next gate has yet to enclose. Choose or verify D_(n+1) only after
obtaining its radius. Failure of this inclusion stops coverage; no reset
at an event switch, cycle, or apparent recurrence is allowed.

At endpoint n, let g_n=Dr(X_n) and B_n enclose ||D²r|| on a convex domain
containing the whole radius-R_n ball. The same integral identity proves

    |r(X_n(u))-r(X_n)|
       <=ec ||g_n J_n||+||g_n|| Q_n+(B_n/2)R_n².             (P)

Here ||g_n J_n|| is the norm of the full 16-component row, not a maximum
of its entries. All chart and gate Taylor remainders belong to preparation
error. None is omitted physics.

There is also an independent invariant region: for the covered chart ball,
||z(0)||<=1+ec, so all physical trajectories satisfy N<=(1+ec)² and unit
projector norms. Straight segments between two such physical states satisfy
these same wave-norm and memory-operator-norm upper bounds by convexity.
A full ball containing a trajectory need not obey these sharper constraints.
For any tube ball B(y,rho), valid simple bounds are
N<=(||z_y||+rho)² and ||P_a||op<=||P_a(y)||op+rho. These follow from
||delta P||op=|delta x| and apply even to indefinite off-manifold references.
They must replace physical conservation whenever the domain includes such
references or a larger ambient ball. No numerical reference inherits exact
conservation by assumption.

## Record Hessian derived in the specified norm

Write v=Lz, ||L||=a, and consider variations (h,k) in waves and active
memory coordinate. Then delta v=Lh and delta P=k·sigma, with
||delta P||op=||k||. The first variation is

    Dr[h,k]=2 Re (Lh)†Pv + v†(k·sigma)v.

The second diagonal variation is

    D²r[(h,k),(h,k)]=2(Lh)†P(Lh)+4 Re (Lh)†(k·sigma)v.

If ||P||op<=p and ||z||²<=N everywhere on the segment/domain, its absolute
value is at most
 2a²p ||h||²+4a²sqrt(N)||h||||k||.
The maximum over ||h||²+||k||²<=1 is the largest eigenvalue of
 a² [[2p,2sqrt(N)],[2sqrt(N),0]], namely

    B=a²[p+sqrt(p²+4N)].

Inactive coordinates only increase the norm denominator. Since the Hessian
is a real symmetric matrix, its bilinear operator norm equals its maximum
absolute quadratic form on the unit sphere (diagonalize orthogonally);
the displayed bound therefore controls both mixed and diagonal inputs.
It is valid for Hermitian indefinite P when p bounds its operator norm.
A useful independently derived gradient bound is
 ||Dr||<=a² sqrt(4p²N+N²).
These are conservative bounds, not assumed optimal curvatures.

## Computed-reference theorem: two separately charged tracks

The following supplies a sufficient contract for a future enclosure backend.
All computed arrays below mean their exact stored real values. No floating
matrix is implicitly equated with an exact derivative or exact trajectory.
Let y_n in R^18, A_n in R^(18x18), T_n in R^(18x16), and row h_n in R^18
be stored reference states, gate derivatives, preparation tangents and record
gradients. Let hat r_n be the stored scalar readout. Enclose, in the declared
norms and at the exact stored y_n,

    ||F_n(y_n)-y_(n+1)||<=d_n,
    ||DF_n(y_n)-A_n||<=eta_n,
    ||T_(n+1)-A_n T_n||<=rho_n,
    ||Dr(y_n)-h_n||<=gamma_n,
    |r(y_n)-hat r_n|<=nu_n.

The rho residual includes matrix multiplication and storage arithmetic;
d includes exponential, constants (including pi), gate evaluation and state
storage errors relative to the exact declared F_n. Gradient error gamma and
scalar evaluation error nu must be enclosed independently. Constants encoded
in approximate parameters must be compared to the exact parameters in d,
eta and derivative enclosures, not treated as a new model.

Initialize alpha0>=||X*-y0|| and beta0>=||J0-T0|| using certified exact seed,
normalization and chart-basis evaluations. The full preparation chart remains
centered at the exact X*. If a rounded chart is used computationally its
error relative to J0 belongs in beta0, and any additional nonlinear chart
approximation requires an explicit remainder bound in Q0; Q0=ec² is justified
only for the exact chart proved above. Rounding the center is not an extra
physical preparation tolerance.

Let M_n>=||A_n||, V_n>=||T_n||. Define sequential outward bounds

    alpha_(n+1) >= d_n+(M_n+eta_n)alpha_n+(H_n/2)alpha_n²,
    e_n = eta_n+H_n alpha_n,
    L_n = M_n+e_n,
    beta_(n+1) >= L_n beta_n+e_n V_n+rho_n,
    W_n = V_n+beta_n,
    R_n = ec W_n+Q_n,
    Q0=ec²,
    Q_(n+1) >= L_n Q_n+(H_n/2)R_n².                       (C)

Here each D_n must contain the **entire** ball
B(y_n,alpha_n+R_n), and H_n must bound D²F_n throughout D_n.
These simultaneous hypotheses are checked sequentially: prior alpha,beta,Q
fix the required input tube before H is accepted and the next bounds are
formed. Existence of some finite H is not an executed enclosure. For endpoint
readouts, B_n must likewise cover B(y_n,alpha_n+R_n).

Proof: the nominal track alpha follows Taylor expansion from y_n to X_n.
Integrating D²F on that segment gives
||E_n-A_n||<=eta_n+H_n alpha_n=e_n and ||E_n||<=L_n.
Subtract T_(n+1) from E_n J_n and insert E_n T_n and A_n T_n;
this gives the beta recurrence, and hence ||J_n||<=W_n. The exact-reference
induction then yields Q,R. The ball condition encloses both the nominal
segment and every segment from X_n to X_n(u); the latter points are within
alpha_n+R_n of y_n. Thus no reference/preparation cross term has been discarded.

For each record let G_n>=||h_n|| and K_n>=||h_n T_n||, with the latter
product and its norm rigorously enclosed, not an unchecked product. Put

    c_n=gamma_n+B_n alpha_n,
    Preparation_n = ec [K_n+G_n beta_n+c_n W_n]
                    +(G_n+c_n)Q_n+(B_n/2)R_n²,
    Numerical_n = (G_n+gamma_n)alpha_n+(B_n/2)alpha_n²,
    Readout_n = nu_n.                                      (B)

Then ||g_n-h_n||<=c_n, so
||g_n J_n||<=K_n+G_n beta_n+c_n W_n. Formula (P) proves the Preparation
bound. Expanding r(X_n) about y_n proves the Numerical bound, and finally

    |r(X_n(u))-hat r_n|
       <=Preparation_n+Numerical_n+Readout_n.

This is the requested separation: Preparation bounds exact-perturbed versus
exact-nominal records; Numerical bounds exact-nominal versus exact mathematical
readout at the numerical reference; Readout bounds scalar evaluation there.
The term B_n alpha_n W_n explicitly retains the reference/preparation cross
effect in the preparation bound. Approximate derivatives may inflate that
bound but do not represent physical omitted-law error. This exact declared
model has omitted-law contribution zero, not zero Taylor remainder. Matrix
products and norm/square-root evaluations in (C),(B) require outward upper
bounds at every step; overflow, NaN, missing residuals or failed tube inclusion
cannot pass. No derivative-column or cycle resets are permitted.

To support the master target, every record at every one of 64 gate endpoints
for both seeds must separately satisfy Preparation<=2.5e-4,
Numerical<=2.5e-4, Readout<=2.5e-4, omitted law=0 within its allocation,
and total<=1e-3. These are unchanged thresholds, not claims that this
contract meets them. Report a contiguous covered endpoint prefix and its
floor(prefix/2) full cycles. An upper bound above threshold is unresolved,
not a physical counterexample.

## Dependency and error-term contract

| Quantity / obligation | Meaning and charging | Future owner |
| --- | --- | --- |
| Exact seed, pi, chart, ec; alpha0,beta0 | Exact-source vs arithmetic representation; numerical/tangent enclosures | #94 |
| d,eta,rho | Gate, derivative and tangent-product residuals; no unchecked products | #94, #95 |
| H and D | Gate Hessian on complete ambient input tube; finite and outward certified | #94 |
| p,N,B | Domain bounds including off-manifold points; record curvature | #94 |
| gamma,nu,G,K,M,V | Readout/gradient/product/norm enclosures, including rounding | #94, #95 |
| alpha,beta,Q,R and inclusions | Nonresetting induction and independently checkable proof data | #95 |
| Fixed thresholds and prefix coverage | Both seeds, all records, all endpoints; no selective pass | #95, #96 |
| Feasibility and execution | Qualified registered backend and locked bounded plan | #96, #97 |

## Analytic controls, source comparison and claim limits

The proof uses operator-program §5 as the primary equation source; its
Hermitian extension and chart/Taylor theorem are derived above rather than
imported from the unavailable preparation PDF. Existing floating
`gate_tangent` differentiates spinor lifts and is a useful physical-tangent
diagnostic, but does not supply the required full ambient DF or Hessian
bound on D_n. The full W/P operator ODE is another comparison representation,
not the 18-coordinate chart or a numerical certificate. Novelty is unassessed.

Independent limiting cases are exact: at s=0 or kappa=0, F is identity and
H=0; at d=0 waves and P stay fixed, though transverse derivatives need not
vanish; if [D,P]=0 the memory is constant and d evolves under constant P.
A zero nominal d therefore does not justify dropping transverse directions.
At t=0 the chart remainder vanishes and its derivative is the isometry;
as c approaches 1 the inverse chart diverges. At N=0 the record Hessian
bound becomes 2a²p, correctly retaining second wave variations even though
the first derivative vanishes. With alpha=beta=d=eta=rho=gamma=nu=0,
(C),(B) reduce to the exact-reference inequalities. These are analytic checks;
finite differences and ODE comparisons are bounded diagnostics only.

The prior linked-memory failure, zero-useful-cycle global bound, complementarity
counterexample, and unresolved numerical/readout certification remain intact.
Tests 1–11 are unchanged. No physical clock, stability, within-gate uniform
record certificate, all-time behavior, metric emergence, or transfer to
Candidate B is established. Independent review must challenge tube inclusion,
chart coverage, source identities and every arithmetic residual before this
conditional contract can be treated as complete; downstream numerical
hypotheses remain uncomputed even when the analytic proof is accepted.
