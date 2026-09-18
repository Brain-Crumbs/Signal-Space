# T11 Setup D: three-clock asymmetry and degree controls

Setup D provides a small deterministic `A-B-C` envelope diagnostic over the
shared solver. `A` and `C` are open endpoints; `B` has two reciprocal incoming
and outgoing neighbor links. It runs separately with a declared increase of
the intrinsic frequency at `A`, `B`, or reflected endpoint `C`.

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
control, not a packet-level record or a physical source label.

Each run retains per-node phase-advance mean frequency, emitted and received
left/right rate means, `omega_target - omega` response lag, simulator-only
retarded phase mismatches, a matched unboosted reference, and causal-bound
disturbance-onset records. These are finite technical diagnostics only. They
make no claim about synchronization, attraction, binding, gravity,
electromagnetism, or a Paper I result.

`runSetupDPreparationEnsemble` executes the four named preparations (or a
validated requested subset) as independent runs with derived saved seeds. It
does not hand off a trajectory, reset a phase, or label any outcome.
