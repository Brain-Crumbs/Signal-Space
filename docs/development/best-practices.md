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

## BP-LM-02: Separate locked numerical decisions from later analytical results

Status: active. Added and last revised 13 October 2026.

When a locked comparison fails, preserve that failure and every dependent
unresolved criterion. A later exact proof or counterexample is a separately
dated analytical result, not a reason to relabel the frozen numerical check.
An implementation-comparison failure also does not refute an algebraically
derived representation identity. State which cases, prefixes and observables
failed; conservation alone cannot qualify the trajectory.

For finite-horizon records, report maxima over all saved prefixes and explicitly
identify gate endpoints, full-cycle endpoints and the tested perturbation
directions. Coordinate-basis tests cannot certify every combined perturbation
inside an initial-error ball or every within-gate readout.

Evidence: the [full linked-memory campaign](../research/gross-linked-memory-results.md)
has a failed global 64-cycle coherent comparison and an unresolved frozen
endpoint gate, alongside an independent post-run exact endpoint counterexample.
The active-minus largest signed record error and active-plus largest singular
amplification occur before the final prefix. Its fresh independent review
identified these reporting distinctions; the interpreted packet preserves them.

### Change history

| Date | ID | Change | Reason and evidence |
| --- | --- | --- | --- |
| 13 October 2026 | BP-LM-02 | added | Preserve frozen classifications and distinguish exact post-run claims from numerical and basis-test evidence; linked-memory campaign above |
