# Finite-window diagnostics

Paper I §11.1 equation (66) and §11.11 equation (67) map to the pure
`@signal-space/analysis` package. It consumes saved physical samples; it does
not add observer access or infer manuscript conclusions.

- Mean frequency is phase advance over a declared window. Slip count uses
  unwrapped pair phase; bounded wrapped angle is not evidence of bounded phase.
- Nested windows begin after a declared transient and carry tolerances,
  duration, modulation, phase range, slips, and estimator evidence. Short or
  conflicting windows are `unresolved`; numerical failure remains separate.
- A phase-locking candidate requires declared perturbation recovery.
  Equal-frequency persistent offsets can only be frequency-locking candidates.
  Collective periodic frequency modulation is permitted.
- Retarded phase carries explicit `chi` and is `simulator-only` unless a
  separately declared observation protocol makes it measurable.
- Uncertainty uses independent replicate estimates and retains every run,
  preparation, seed, and saved-sample count. Within-run time samples may be
  correlated and are not counted as independent replicates.
- Spatial profiles, wrapped coherence, and causal response fronts preserve
  traveling-pattern evidence. Irregularity and low coherence are not chaos.

Normal-approximation replicate intervals are reporting controls, not tail
inference. Callers must declare scientifically justified tolerances and save
enough samples; diagnostics do not interpolate missing evidence.
