# T11 Setup D: three-clock asymmetry and degree controls

Setup D provides a small deterministic `A-B-C` envelope diagnostic over the
shared solver. `A` and `C` are open endpoints; `B` has two reciprocal incoming
and outgoing neighbor links. It runs separately with a prepared intrinsic-
frequency asymmetry at `A`, `B`, or reflected endpoint `C`. That asymmetry is
present throughout the declared prehistory; it is not described as a `t=0`
intervention.

Propagation is tested by a separate, explicit phase offset after `t=0`. Its
matched reference has the same asymmetric scenario and prehistory but no
offset. Frequency and phase onset thresholds and the causal-time tolerance are
distinct quantities with saved units.

The `C` case is not merely a renamed `A` case. Its saved preparation records
the `A <-> C` node map, `left <-> right` port map, and a `pi` lobe-phase shift.
The route table remains position-consistent, so the reflection convention is
inspectable instead of being baked into a conclusion.

Two response-scale conventions are distinct run metadata:

- `fixed-physical-r-star` is the default contract, using the scenario physical
  `r*` for every node;
- `degree-normalized-r-star` supplies an explicit per-node envelope option
  `r*_i = d_i r*`, giving endpoint scale `r*` and middle-node scale `2 r*`.

This option never overwrites `Scenario.rateScale`. An isolated node has zero
summed reception; the adapter keeps its stored scale at physical `r*` rather
than forming a zero degree denominator. It therefore does not introduce a
division-by-degree convention.

`runSetupD` also builds a separately typed `recorded-endpoint-replay` control.
It copies the reciprocal run's `A` right-port and `C` left-port envelope-rate
outputs into delayed driven schedules for an isolated `B` receiver. There are
no source nodes or links in that receiver scenario, and each source record is
marked `respondsToReceiver: false`; the replay schedule is therefore fixed and
cannot be changed by the receiver. This is a deterministic rate-envelope
control, not a packet-level record or a physical source label. Under the
`empty-links` preparation, replay inputs whose source time is negative are
exactly zero. The replay is exposed as its own executable experiment
definition; it is not a label attached to the reciprocal definition.

Each run retains per-node phase-advance mean frequency, emitted and received
left/right time-weighted rate means, `omega_target - omega` response lag,
simulator-only retarded phase mismatches, a matched undisturbed reference, and
causal-bound disturbance-onset records. E0 retains one fixed emission rate
under the intrinsic-frequency preparation. These are finite technical
diagnostics only. They
make no claim about synchronization, attraction, binding, gravity,
electromagnetism, or a Paper I result.

`runSetupDPreparationEnsemble` executes the four named preparations (or a
validated requested subset) as independent runs with derived saved seeds. It
does not hand off a trajectory, reset a phase, or label any outcome.
