# C1-3: nonresetting local-record proof objects

[#95](https://github.com/Brain-Crumbs/Signal-Space/issues/95), task 3 under
[#92](https://github.com/Brain-Crumbs/Signal-Space/issues/92). This supplies a
producer and saved-proof checker for the [#93 theorem](gross-local-record-theorem.md),
using the [#94 arithmetic backend](gross-validated-local-backend.md).
The fixed engineering demonstration covers **one AB cycle**, both exact active
seeds, the full physical radius 1e-6, and all three records at both endpoints.
Registration, measured scientific admission and locked plans remain #96;
the 32-cycle confirmation remains #97. No scientific campaign was launched.
Tests 1–11, Candidate B, prior failed results and canonical bytes are unchanged.

## Source and campaign audit

Implementation starts at main `5344549a6e99cda62239e474931043bf7d4bacdc`,
which includes merged PR #98 (#93) and PR #99 (#94). Issue #94 remained open
when audited, despite its implementation being merged; the master checklist
also lagged that merge. Code prerequisites are available. This PR does not
close earlier issues or treat their tracking as a new scientific result.
#95 has no native GitHub parent (404); #92 is its explicit textual parent.
There was no existing #95 PR. PR #91 remains open and is not modified.
The supplied v0.2-1 attachment matches the unchanged equation authority:
SHA-256 `c733c958fde54c810c38889e5096de54358a77cc10e69d9f885870832595e123`.
No previous raw campaign bytes are consumed by this implementation.

## What is transported, and why

An initial error has sixteen independent physical directions: twelve real wave
components and two orientations per memory. Evolution and Taylor remainders
live in eighteen ambient coordinates. `record_tubes.produce` retains an 18x16
response, and every forcing and transition acts on all eighteen coordinates.
A large internal deformation need not destroy readable local records: the
record gradient is transported against the complete response before taking
its norm. Selecting sixteen separate error lines would miss combined inputs.

Let y_n be the exact stored numerical center, A_n a dyadic midpoint approximation
to DF_n(y_n), and E_n=DF_n(X_n) the derivative at the exact nominal trajectory.
Let T_n=A_(n-1)...A_0 J0 be the reference preparation response, enclosed by
interval matrix products. With alpha_n bounding ||X_n-y_n|| and beta_n bounding
||J_n-T_n||, the #93 theorem gives

    e_n = eta_n + H_n alpha_n >= ||E_n-A_n||,
    W_n = ||T_n|| + beta_n,
    R_n = ec W_n + Q_n.

Here eta_n bounds the point derivative discrepancy; H_n bounds the complete
ambient gate Hessian; ec is the chart radius; Q_n bounds the nonlinear
preparation remainder. The exact initial chart is centered on the mathematical
seed. Initial center rounding belongs only in alpha_0, and Q_0=ec² remains
preparation error. The exact J0 has zero representation error.

Instead of multiplying one-step norms, retain
Phi_A(n,k)=A_(n-1)...A_k, with Phi_A(n,n)=I. Every factor and every product is
outward enclosed; no inverse fundamental matrix is used. Define the local
forcing bounds

    f_alpha,n = d_n + eta_n alpha_n + H_n alpha_n²/2,
    f_beta,n  = e_n W_n,
    f_Q,n     = e_n Q_n + H_n R_n²/2.

Then the implemented sufficient bounds are

    alpha_n >= ||Phi_A(n,0)|| alpha_0
               + sum(k=0..n-1) ||Phi_A(n,k+1)|| f_alpha,k,
    beta_n  >= sum(k=0..n-1) ||Phi_A(n,k+1)|| f_beta,k,
    Q_n     >= ||Phi_A(n,0)|| ec²
               + sum(k=0..n-1) ||Phi_A(n,k+1)|| f_Q,k.

Derivation: write the nominal discrepancy as
 a_(n+1)=A_n a_n + [F_n(y_n)-y_(n+1)]
             + [DF_n(y_n)-A_n]a_n + Taylor remainder.
Similarly, J_(n+1)-T_(n+1)=A_n(J_n-T_n)+(E_n-A_n)J_n;
and q_(n+1)=A_n q_n+(E_n-A_n)q_n+nonlinear remainder.
Iterate each equality without resetting its initial value. The three forcing
sums follow by the triangle inequality. Scalar upward rounding can only enlarge
the stored inductive bounds. Interval T products include their own rounding,
so there is no uncharged matrix-storage defect rho. beta bounds discrepancy
from the exact product, not its interval midpoint.

The spectral norm upper bound is the smaller of the Frobenius bound and
sqrt(||A||1 ||A||inf), both outward enclosed. For example, an expanding diagonal
map followed by its inverse has intact-product norm one, even though multiplying
its one-step norms yields sixteen. The implementation does not assume
contraction or discard poorly observed directions.

## Deterministic bootstrap and record allocations

At input n, previously proved alpha_n, beta_n, Q_n determine R_n. The producer
constructs a coordinate box containing the **whole** Euclidean ball
B(y_n,alpha_n+R_n), and computes H_n on that box. It then computes the next
bounds and the complete endpoint readout box. The checker reconstructs these
boxes exactly. This is a forward deterministic bootstrap, not a fixed-point
iteration stopped at a tolerance. The domain must satisfy #94's magnitude
ceiling; a later obstruction preserves the earlier proved prefix.

Endpoint records use exactly theorem (B): preparation bounds exact-perturbed
versus exact-nominal records, numerical bounds exact-nominal versus the
mathematical readout at y_n, and readout bounds evaluation at y_n. The cross term
B alpha W is retained. Taylor remainders are preparation error; omitted-law
error is zero only for this unchanged exact declared law. Each allocation
remains <=1/4000 and total <=1/1000. Bounds and matrix norms use exact integer,
Fraction and outward dyadic arithmetic. Float conversions in the returned
obstruction table are presentation only.

## Saved evidence and checker trust boundary

A proof stores exact source/config hashes and chart constants; all reference
centers; local value/derivative/exponential-tail enclosures; eighteen-dimensional
derivative factors; full 18x16 response intervals; tube boxes; gate/record
curvatures; transition norm enclosures; every retained forcing and alpha/beta/Q;
gradient and readout enclosures; per-record budget terms; and exact rational
majorant, domain-inclusion, readout-inequality and budget margins. Majorant
margins compare against the intact-product sums, which can be sharper than
one-step norm products. Negative budget margins mean nonclosure; negative
proof/domain margins invalidate a proof. The derivative
factor sequence is a sufficient verified factorization of all transitions;
the checker reconstructs products, rather than saving O(n²) dense matrices.
JSON interval endpoints are integer strings on a declared grid, not rounded
decimal floats. Duplicate JSON keys and mixed precision are rejected.

`record_certificate_check.check_file` does not call the producer, choose a new
reference path, run a time integrator, or trust a `certified` flag. It checks
local exact-gate obligations at the **saved** centers with the qualified #94
backend, then independently reconstructs the ordered induction, products,
full-domain curvatures and allocations. It does not share the producer’s
high-level record-allocation formula or transition-transport loop. No newly integrated trajectory replaces
the saved proof. This local arithmetic re-verification has a cost; it is not
just a hash comparison or a second high-precision solver agreement.

The trusted computing base is the qualified CPython integer/Fraction/isqrt
runtime, the dyadic kernel, the #94 gate/derivative/tail and polynomial-readout
implementation, the shared elementary norm/matrix helpers, and the #93 analytic
chart/curvature proof. The checker is independent of the producer's induction,
not an independent implementation of the local gate mathematics or a formal
proof assistant. Independent analytic controls and fresh review are still
required to find bugs shared by that trusted base. Check saved proofs under
their recorded source revision; source changes deliberately invalidate replay
until explicitly requalified. Platform strings do not enter arithmetic equality;
CPython runtime admission still applies on both qualified OS/runtime pairs.

The checker reports a separate contiguous endpoint and full-cycle horizon for
each seed and each of its three records. A missing/over-budget endpoint cannot
be skipped. Arithmetic invalidity returns no certified horizon. A proved prefix
can remain valid when a later bootstrap/resource gate is unresolved.
An excessive **upper** bound is unresolved, never a counterexample.

`check_witness` accepts a separate saved physical perturbation and both local
trajectory enclosures. It proves its squared chordal radius from the exact chart
formula sum u_wave² + sum t_a²/(1+t_a²), verifies the saved local enclosures,
and obtains lower bounds from interval record differences. Only a lower bound
above the frozen preparation allocation can classify that criterion **fail**.
Producer-supplied claimed bounds are ignored. A harmless witness is unresolved,
not evidence that every perturbation is safe. No failing physical witness was
found or sought in this one-cycle implementation demonstration.

## Reproduction and bounded cost

```sh
python scripts/qualify-record-tubes.py NEW_OUTPUT_DIRECTORY
python scripts/qualify-record-tubes.py --check NEW_OUTPUT_DIRECTORY/active-plus.json
python -m unittest discover -s tests -p test_record_tubes.py -v
```

The fixed fixture has one worker, no numerical native threads, two seeds,
96-bit arithmetic and two gates. Ceilings: 30 CPU seconds, 45 wall seconds,
1024 MiB RSS and 8 MiB output. Unix uses the kernel self max-RSS; Windows
uses sampled psutil RSS, with the measurement method recorded. Engineering costs include both production
and saved-proof checking; they are separate from #92's scientific budget.
The script creates a new directory and preserves partial packets on failure.
A development smoke stopped after the first packet when psutil could not see
the managed host’s PID. That failed attempt is retained in the cost record;
Unix metering now uses self rusage and retains the failure without claiming a
scientific result or reusing the failed resource measurement.
The [compact demonstration record](gross-record-tube-costs.json) includes hashes,
exact-source versions, costs and the obstruction-term table. The full saved
proofs are regression fixtures, not canonical registered experiment packages.

The final fixture used **3.023 wall / 3.022 CPU seconds**, kernel max-RSS
19,382,272 bytes, and 879,708 proof bytes. Both retained JSON proofs replay
through the checker under their exact source hashes.

| Seed / endpoint | Largest linear term | Largest nonlinear/remainder term | Largest preparation bound | Largest numerical bound |
| --- | --- | --- | --- | --- |
| active-plus / A | 1.763835e-6 | 5.031684e-10 | 1.764338e-6 | 1.156193e-24 |
| active-plus / B | 1.815872e-6 | 7.847770e-9 | 1.823720e-6 | 5.684027e-24 |
| active-minus / A | 1.763835e-6 | 5.031684e-10 | 1.764338e-6 | 1.156193e-24 |
| active-minus / B | 1.925351e-6 | 1.048233e-8 | 1.935834e-6 | 8.806705e-24 |

These are upward-rounded display values, maximized over the three declared
records at each endpoint. Exact rational terms and margins are in the saved
proofs; the compact JSON records numerical display values. Readout is at most
6.310888e-29. Preparation dominates this short fixture; its largest bound is
less than 0.8% of its allocation. The increasing remainder motivates measuring
longer-prefix closure in #96, not extrapolating the one-cycle result. No
obstruction term currently exceeds budget. The loose-H regression deliberately
produces budget nonclosure, preserves per-record differences and remains
unresolved without inventing a physical failure.

## Acceptance traceability and limits

| #95 criterion | Implementation and evidence |
| --- | --- |
| C3-AC-01 | Full 18x16 T, 18x18 factors, all forcing retained; both A/B records at every endpoint; no fixed-charge projection or reset |
| C3-AC-02 | Complete bootstrap/readout boxes, outward integer arithmetic and theorem (B)'s separate allocations; transition products preserve cancellation |
| C3-AC-03 | Separate saved-proof induction; local obligation re-verification, source pins and exact interval JSON; mutations exercise tube, H, forcing, budget, column, order, rounding and reset obligations |
| C3-AC-04 | Separate contiguous horizons; unresolved upper-bound nonclosure; physical chart and validated lower bounds required by witness path |
| C3-AC-05 | Exact linear/nonlinear controls, chart remainder, combined-direction diagnostics, one-cycle fixtures, repository checks, fresh review and practices update |

The engineering fixture validates one cycle, not feasibility or success at
32 cycles. Matrix products and the conservative local curvature can still
inflate later tubes. No pilot/confirmation launch gate is claimed. No
within-gate uniform, all-time, stable-object, autonomous-clock, physical detector,
emergent metric or Candidate A/B bridge claim follows.
