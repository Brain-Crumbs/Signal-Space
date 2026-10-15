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
