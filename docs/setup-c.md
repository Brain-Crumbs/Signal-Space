# T10 Setup C: pair scans

Setup C is a small, deterministic scan layer over the shared envelope solver.
It provides pair cells for detuning, positive delay, signed gain, directional
contrast, and relaxation time, plus explicit no-feedback, zero-contrast, and
small-positive-delay controls.

The scan coordinates are dimensionless:

- `detuning = (omega0_B - omega0_A) / omegaReference`;
- `delay = omegaReference * tau`;
- `gain = g / omegaReference`;
- `contrast = a`;
- `relaxationTime = omegaReference * T_rel`.

Each cell stores both these coordinates and their physical conversion. The
baseline conversion is `nu_i = q * omega0_i / (2*pi)` for E0 and fixed `q` for
E1, so changing detuning does not silently change the comparison rule.

`runSetupCScan` returns a map-order cell list, trajectory run IDs, replicate
uncertainty, and separate masks for unresolved, numerical-failure, and unrun
cells. `maxCells` is an inexpensive way to produce a partial map without
turning omitted cells into failures. `direction: 'forward'` or `'reverse'`
records the continuation order and adopts the complete prior `EnvelopeSnapshot`
at each handoff. The prior dense causal segments, unwrapped phase, integrated
emission state, adaptive history, and perturbation history remain available to
the next parameter cell. `direction: 'independent'` records only separate
restarts. A handoff is not an observer-visible signal and does not reset phase
or infer a regime.

Nested finite windows are saved at exact boundaries and passed to the shared
pair classifier. A status is evidence from those windows only. Coexistence,
locking, and chaos are not asserted; irregularity values are descriptive
diagnostics, and a chaos classifier remains deferred.

The checked-in smoke definitions and tests use inexpensive fixtures. They are
engineering validation, not publication-scale scans or Paper I findings.
