# C1-2 local reciprocal-gate enclosures

Issue [#94](https://github.com/Brain-Crumbs/Signal-Space/issues/94), under
[#92](https://github.com/Brain-Crumbs/Signal-Space/issues/92). This implements
local numerical obligations of the [conditional theorem](gross-local-record-theorem.md).
It does not implement #95's trajectory induction or saved-tube checker, register
an experiment, run a scientific pilot, or establish a positive certified horizon.
The physical model, floating implementations, thresholds, prior failures and
canonical evidence are unchanged. PR #91 is not modified or merged.

## Arithmetic choice and trust boundary

The certified path uses a small outward dyadic kernel, `numerics/dyadic.py`,
with CPython **3.12.14** pinned in `requirements-validated-lock.txt` and CI.
Its arithmetic dependencies are the standard-library exact integers,
`fractions.Fraction`, and `math.isqrt`, not NumPy, SciPy, libm or a floating
rounding mode. Unsupported runtimes fail closed. There is no new third-party
arithmetic dependency. The runtime implementation and the source hashes in
the retained smoke record are part of the qualification boundary; this is
reviewable executable mathematics, not a machine-checked formal proof or a
hardware fault certificate.

We compared two approaches before implementation:

| Approach | Rigorous obligations / degeneracies | Decision |
| --- | --- | --- |
| Explicit Pauli 2x2 exponential with entire cos/sinc | Outward transcendental evaluation and their differentiated remainders; sinc must be entire at repeated eigenvalues | Plausible future optimization; not implemented or benchmarked here |
| Validated exponential/Frechet via matrix power series | Submultiplicative norm tails and product differentiation, no eigenbasis or gap division | Selected: direct 1x1/2x2 dyadic series with scaling and squaring |
| Arb/python-flint | Existing rigorous ball library, version/platform qualification still needed | Attempted python-flint 0.8.0 installation was blocked by proxy CONNECT 403; not installed, trusted or bypassed |

Arb's primary description is [Johansson's paper](https://arxiv.org/abs/1611.02831).
The selected kernel instead has the elementary proof below and no imported
transcendental-library guarantee. Python's primary specifications describe
[unlimited-precision integers](https://docs.python.org/3.12/library/stdtypes.html#numeric-types-int-float-complex),
[rational arithmetic](https://docs.python.org/3.12/library/fractions.html), and
[integer square roots](https://docs.python.org/3.12/library/math.html#math.isqrt).
They are the only numerical-library assumptions used. Agreement with a
high-precision or floating solver is never the enclosure argument.

An interval stores integer endpoints l,h and means [l/2^b,h/2^b], b=64,96,128.
Addition/negation are exact. Multiplication takes extrema of four exact integer
products, divides by 2^b with floor/ceiling, and therefore contains every product.
Reciprocal reverses endpoints away from zero and divides 2^(2b) outward; a
zero-containing denominator fails. Squaring treats zero crossings separately.
Square-root endpoints use floor integer sqrt(l*2^b), and ceil sqrt(h*2^b).
No floating conversion occurs in these operations. Euclidean and Frobenius
norms sum squared rational magnitude bounds exactly before an integer-square-root
upper bound; this avoids a sqrt(grid-spacing) floor on tiny residuals.
Complex operations are the four real operations. Each resulting complex
rectangle contains the mathematical result. Floating values in cost tables
are presentation only; every consumable bound remains an exact rational string.

Pi is enclosed by pi=16 atan(1/5)-4 atan(1/239). Each arctangent uses b terms
of the alternating series, with the magnitude of the next term added on both
sides using exact rationals. The identity follows from the tangent addition
formula and the angles' quadrant (4 atan(1/5)-atan(1/239) is in (0,pi/2) and
has tangent one). Seed square roots and the source chart use the same outward
kernel. The coupling is **mathematical pi/2**, never the stored binary64 value.
The new smoke configuration explicitly declares `exact-pi/2`; the local API
rejects any other coupling mode. Existing configs retain their original bytes
and interpretation.

## Exponential and derivative proof

Let A be a 1x1 or 2x2 complex matrix, and B=A/256. The backend checks an
outward bound a<=1/4 for the maximum row sum of entrywise complex one-norms.
This norm is submultiplicative and dominates every entry's complex modulus.
For m=32, calculate T=sum(k=0..m) B^k/k! by interval matrix multiplication.
With a=0 use the same formulas (no 0/0):

    ||exp(B)-T|| <= a^(m+1)/(m+1)! / (1-a/(m+2)) = t0.

The geometric majorant follows because every subsequent scalar Taylor term
ratio is <=a/(m+2). For a coordinate derivative E=dB/dx, differentiating
B^k gives k placements of E. Hence

    ||D exp(B)[E]-D T(B)[E]||
      <= ||E|| a^m/m! / (1-a/(m+1)) = t1(E).

Each polynomial operation propagates all 18 real partial derivatives by the
product rule. The separately enclosed t0 and each t1 are added to both real
and imaginary parts of every matrix entry, then eight interval squarings
propagate both value and derivative enclosures. This proves inclusion of
exp(A) and its full first derivative; it is not differentiation of a truncated
series with the omitted derivative set to zero. All tail quantities, term
counts, scaling counts and norm bounds are included in each local result.
No eigengap, eigenvector differentiation or projector assumption occurs.

Two exponentials are evaluated: U=exp(-i t (dd†+2P)) and exp(i t q), with
t=(pi/2)s, q=d†d. The phase and S derivatives are included by the jet product
rule, not omitted because q is constant along an exact gate. Inactive
coordinates have their identity derivatives. Interval dependency can enlarge
widths without invalidating containment.

## Full-domain gate and record curvature

Every input real box represents trace-one Hermitian memories P=I/2+x·sigma;
it need not be positive or rank one. Let N bound sum |z|² throughout that box,
p=1/2+sup |x| for the active memory, D=sqrt(2N), c=sqrt(2), and t=(pi/2)s>=0.
For any two ambient unit inputs h,k:

    ||delta d|| <= c,
    ||DS[h]|| <= L=2Dc+2,       ||D²S[h,k]|| <= 4,
    |Dq[h]| <= 2Dc,             |D²q[h,k]| <= 4.

Here ||delta P||op=|delta x|<=1. Hermitian unitarity and the Frechet integral
imply ||DU||<=u1=tL and ||D²U||<=u2=4t+t²L², including the second derivative
of S. The second Frechet bound follows by differentiating the integral into
two ordered simplices whose total area is one. For f=exp(i t q),
|Df|<=f1=2tDc and |D²f|<=f2=4t+f1². Differentiating f U d twice yields

    hd=(f2+2 f1 u1+u2)D+2(f1+u1)c.

This bounds the second derivative of the evolved difference, including both
phase/S cross terms and both derivatives hitting d. The two port outputs
contribute hd/sqrt(2) in the wave norm. For U P U†, using the Frobenius norm
divided by sqrt(2), ||P||F/sqrt(2)<=p and ||delta P||F/sqrt(2)<=1 gives

    hp=2p(u2+u1²)+4u1,
    H=sqrt(hd²/2+hp²).

The hp terms respectively cover both second derivatives of U, the two
first-derivative products, and four mixed U/P terms. There is no D²P term
because P is affine in x. Inactive coordinates have zero second derivative.
Thus H bounds the bilinear Hessian on the **entire requested box**, including
all off-manifold points and mixed directions. It is not a sampled curvature.
Every evaluation of this positive expression is outward enclosed. At s=0,
H=0 exactly. The bound is conservative (about 499 at the active seeds).

Records are evaluated as v†Pv, for v=z_i,z_j,d. Their values and gradients use
exact polynomial interval differentiation. Their full-box Hessian bound is
B=a²[p+sqrt(p²+4N)] with a²=1,1,2, as independently derived in #93. The bound
retains the nonzero wave Hessian at zero waves. No unit-projector conservation
is assigned to an off-manifold reference or its box. The memory trace stays
one by the coordinate definition, while p explicitly bounds its spectrum.
No output center is silently projected or normalized; any later center's
spectral bound must be evaluated on that later domain.

## API and equation-to-code mapping

`evaluate(box,event,bits=96,duration="1",coupling="exact-pi/2")` accepts 18
real intervals or exact rationals. Ordering is interleaved Re/Im of the six
wave components, then (x,y,z) of memory A and B. Event 0 is A, event 1 is B.
`ball_box(center,radius)` encloses the complete Euclidean ball by a coordinate
box; loss of correlation is explicit. Finite coordinates must have magnitude
<=4 and the scaled exponential norm must pass admission. Duration is an exact
rational in [0,1]. Inputs reject floats, nonfinite values, mixed precision,
invalid dimensions, scientific-notation strings and oversized rationals.
A stored float can be supplied explicitly as `Fraction.from_float(value)`;
that represents the stored number, not the exact mathematical seed.

Success returns `status=enclosed`, the actual domain, arithmetic/proof metadata,
state centers/radii, all 18x18 derivative intervals and midpoint matrix,
a Frobenius upper bound on its operator error, and full-domain H. The same
payload includes the three **input-domain** record values, 3x18 gradients,
scalar radii and Hessian bounds. Records are not implicitly evaluated at the
output; pass the desired endpoint box in a separate call. Each matrix entry's
interval is authoritative; derivative error is relative to the returned exact
rational midpoint matrix. For a non-point box that error includes variation
throughout the box, not only rounding. Per-row gradient error bounds can be
computed with `norm_upper` on row radii. The combined bound is also valid
for every row. All matrix products are enclosed by `mm`; no NumPy product
is part of a proof quantity.

`source_chart` encloses the two active seeds plus arbitrary simultaneous chart
coordinates. It evaluates P=(w+eta)(w+eta)†/(1+|eta|²), algebraically the same
normalized spinor chart, without a redundant normalization sqrt. The wave
coordinates are additive. `source_contract` returns exact J0 (including all
12 wave columns), its zero representation error, source state radii and their
norm bounds, enclosed pi/ec, and the chart remainder ec² from #93. J0 is
isometric; it retains common wave phase, norm- and charge-changing directions.
This is not a general nonzero-u chart Jacobian API.

| Theorem quantity / equation | Implementation | Local evidence |
| --- | --- | --- |
| Exact source constants, C(u), J0, ec² | `pi_interval`, `source_chart`, `source_contract` | Rational constants, integer sqrt, chart and all-sector tests |
| F and DF including q/S/phase | `gate_jets`, `exponential`, `Jet` | Tail proof above, commuting/dark/degenerate controls and ODE diagnostic |
| Full D, p, N, H | `ball_box`, `curvature` | Full-box analytical majorants above, indefinite-memory tests |
| r, Dr, B | `record_jets`, `curvature` | Exact polynomial values/derivatives and theorem Hessian |
| Representation error, products/norms | `pack`, `mm`, `norm_upper` | Outward integer arithmetic and independent rational controls |
| Local tail/proof integrity | `check_local_output` | Corrupted radius, derivative, record, missing tail and precision rejected |
| Nonresetting alpha/beta/Q/R, tube inclusion, horizons | Not implemented | Owned by #95; no scientific budget or horizon evidence here |

`check_local_output` is a deterministic recomputation guard for local results,
not an independent implementation or #95's saved-proof checker. It requires
an identical request and execution metadata. It rejects altered local outputs,
but shared implementation bugs require the independent analytic controls and
review. In particular, the tail test deliberately reduces polynomial degree
and disables widening; an independent exact rational lower bound on exp(1)
then rejects both the value and derivative. A missing tail is actually
exercised, rather than merely rejected by an unrelated hash comparison.

Failures return `status=unresolved` and a reason, with no usable gate payload.
Lower-level arithmetic/chart helpers raise explicit exceptions. Supported
precision, runtime, coordinate and exponent ceilings bound work; the gate
checks a maximum 30-second local deadline during its fixed loops and before
returning success. Memory allocation failure also fails closed where Python
can catch it. An externally killed process produces no certificate. No
unbounded precision escalation or scientific resource admission is performed.

## Qualification and measured limits

The fixed [engineering fixture](../../tests/fixtures/local-record-backend-smoke.json)
makes 24 independent local calls: two seeds, two events, three precisions,
point boxes and complete radius-1e-6 ball boxes. It does not propagate an AB
trajectory. One separate two-gate analytic test checks PR #91's exact first-word
complement witness c²=(2/5)sin²(pi sqrt(5)/4), with independent scalar Taylor
bounds. Other tests cover N/J balance, within-event r3 constancy, common phase
and internal U(2) covariance, repeated eigenvalues, off-manifold memory,
source chart sectors, invalid/resource modes, and the independent physical
variational ODE. Floating comparisons remain diagnostics.

[Retained cost/width evidence](gross-local-backend-costs.json) records every
call, source hashes and exact-output SHA-256 digests. The first smoke attempt
stopped unresolved at a rational-size ceiling; its summary is retained. The
bounded limit was raised from 4096 to 16384 bits to accommodate the 128-bit
Taylor-tail rational, and the fixed fixture was repeated without changing
physical inputs or thresholds. Detailed output files are reproducible with:

```sh
python scripts/qualify-local-backend.py NEW_OUTPUT_DIRECTORY
```

A [complete local proof fixture](../../tests/fixtures/local-record-proof-active-plus.json)
retains the active-plus/event-A/96-bit point result. The other raw local smoke
outputs are engineering scratch, not canonical scientific artifacts.

After moving engineering fixtures out of the registered-config directory, the
final 24-call attempt used about 5.48 wall / 5.47 CPU seconds,
16.3 MB sampled RSS, and 2.41 MB of local output. RSS is sampled after each
call, not a kernel peak measurement. The fixed ceilings are 30 CPU / 45 wall
seconds, 1024 MiB and 8 MiB, with one process and no native numerical threads.
All costs are separate from the later #92 scientific ceiling. No launch gate
for #96 is supplied by these timings.

| Precision | Point state-error norm (range over seeds/events) | Point derivative-error bound | Radius-1e-6 box state-error norm |
| --- | --- | --- | --- |
| 64 | 2.72e-15 to 8.10e-15 | 4.33e-14 to 1.17e-13 | 1.11e-4 to 1.35e-4 |
| 96 | 6.55e-25 to 1.87e-24 | 1.04e-23 to 2.70e-23 | 1.11e-4 to 1.35e-4 |
| 128 | 1.47e-34 to 4.25e-34 | 2.34e-33 to 6.13e-33 | 1.11e-4 to 1.35e-4 |

These values are engineering observations, not acceptance thresholds. Width
need not decrease monotonically with precision. The box width plateaus from
wrapping; increasing precision cannot remove this loss of correlation. Local
qualification gives no evidence that a 32-cycle tube closes or that the later
scientific resource envelope is feasible. Those remain explicit #95/#96
obligations. No record-budget, physical detector, all-time, stability, clock,
metric or Candidate B claim follows.
