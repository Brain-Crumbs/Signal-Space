# Research implementation practices

## Saved derivative audits

Every saved derivative used in a figure or forecast must participate in an
independent saved-data comparison. Checking only shape, finiteness, a related
state derivative, or the formula's unit test leaves the actual artifact unchecked.
Reconstruct centered observation differences from saved perturbed states for
each declared step, prefix and physical input sector; retain comparison errors
in plot data and include them in the locked numerical gate.

Evidence: PR90's original linked-memory record derivatives could be replaced
with zeros without changing any scientific check. The regression in
`tests/test_linked_memory.py` now detects that corruption through the actual
analysis path, while isolated tests cover both steps and every prefix/sector.

Keep corrupted regression copies separate from sealed canonical evidence.
Preserve original locks and create versioned replacement plans when extending
validation coverage; retain the original failed behavior as provenance.

## Full preparation balls and computed references

For a uniform perturbation claim, prove chart coverage in the declared physical
norm before propagating tangent columns. Orthogonal basis tests do not cover
combined perturbations. Keep norm- and charge-changing inputs unless the
scientific preparation contract explicitly excludes them.

Specify a smooth ambient extension for every off-manifold Taylor segment.
Unit-projector invariants of exact trajectories do not qualify arbitrary
numerical references or the whole tube. Separate physical preparation error,
nominal-to-reference propagation error and scalar readout evaluation error;
charge derivative, matrix-product and norm-enclosure errors explicitly. Carry
both budgets continuously across every ordered gate.

Evidence: issue #93's [conditional theorem](../research/gross-local-record-theorem.md)
and [source audit](../research/gross-local-record-source-audit.md) distinguish
18 ambient coordinates from 16 physical inputs and retain seed rounding.
The independent Hermitian ODE and polynomial Hessian diagnostics in
`tests/test_local_record_contract.py` test algebra without representing
floating agreement as a validated numerical certificate.

## Local enclosure qualification

Preserve the mathematical constants as enclosed exact sources; a stored float
is a reference value with an error, not a replacement law. Include derivative
remainders when differentiating a truncated exponential, and exercise a missing
tail with an independent analytic inequality whose gap exceeds rounding noise.
A recomputation/hash guard alone cannot qualify its own arithmetic algorithm.

Bound curvature on the entire requested ambient domain, including indefinite
Hermitian memories when the domain contains them. Record point-rounding width
separately from interval wrapping across a tube; more precision need not shrink
wrapping. Keep local engineering costs and failed qualification attempts
separate from scientific pilot/confirmation budgets and horizon claims.

Evidence: #94's [local backend proof and qualification](../research/gross-validated-local-backend.md),
`test_exponential_tail_obligation_is_exercised`, exact rational polynomial
controls, and the fixed point/ball smoke fixture. The 128-bit smoke initially
hit an explicit rational-size ceiling; the bounded adjustment and repeated
fixture are retained without substituting numerical agreement for enclosure.

## Continuous proof transport and saved-proof checks

Carry all initial uncertainty and every forcing term through the entire ordered
word. Retain intact transition products when sharpening a norm bound; preserve
all ambient directions and include interval matrix-product rounding. A later
endpoint must not overwrite an earlier error allowance or skip a failed budget.
Keep preparation, numerical-reference and mathematical readout allocations
separate, including reference/preparation cross terms.

A saved-proof checker must reconstruct the induction from source enclosures,
local obligations and factorization, rather than trusting stored success flags
or scalar majorants. State its shared arithmetic/analytic trusted base. Validate
corruption at the obligation it breaks, and distinguish excessive upper bounds
from an admissible physical witness with a validated lower bound.

Evidence: [#95](https://github.com/Brain-Crumbs/Signal-Space/issues/95),
[proof contract](../research/gross-record-tube-certificates.md),
`tests/test_record_tubes.py`: exact cancellation/nonlinear controls, all sixteen
combined preparation directions, missing-force/column/order/reset/rounding
mutations, and physical-source witness validation. Added 17 October 2026.

## Change history

| Date | Practice | Change | Evidence |
| --- | --- | --- | --- |
| 2026-10-17 | Continuous proof transport and saved-proof checks | Added explicit retained-forcing, shared-trust and counterexample requirements | #95 and its proof/corruption controls |
