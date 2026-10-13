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
