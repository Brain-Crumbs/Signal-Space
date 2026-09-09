# T09 Setup B: reciprocal pair / Experiment Zero

Setup B is the first pair-level explorer layer over the shared deterministic
envelope solver. It keeps reciprocal, one-way, and prescribed-drive controls as
separate protocol IDs and exposes all six E/R combinations (`E0`/`E1` crossed
with `R0`/`R1`/`R2`).

`packages/experiments/src/setup-b.ts` provides:

- co-phase, pi-reflection, small-offset, and deterministic seeded-random
  preparations;
- explicit linear link prehistory and established versus empty-link startup;
- reciprocal `A-B` and `B-A` routes, one-way `A-B`, and an uncoupled
  prescribed right-port drive;
- signed gain sweeps through zero;
- matched no-perturbation continuations and finite-window pair diagnostics.

## Perturbation decision

The Setup B phase/frequency perturbation is an explicit deterministic state
intervention. It is stored in `EnvelopeOptions.perturbations`, lands at an exact
solver boundary after the declared preparation duration, and records a post-jump
state in `EnvelopeSnapshot.jumps`. The solver retains the pre-jump dense history
and uses the post-jump state for exact retarded queries at the intervention time.
This is a comparison intervention, not an implied phase reset, synchronization
rule, or physical force.

## Metrics and limits

Runs save phase-advance mean frequencies, mean-frequency mismatch, unwrapped
pair-phase drift and slips, simulator-only retarded phases with `chi = 0`,
collective frequency modulation, and recovery evidence from the shared finite-
window classifier. A reference continuation is saved beside the perturbed run;
its state is not an observer-readable signal. Classifier status is deliberately
unresolved/candidate/slipping evidence, never a required locking outcome.

The checked-in smoke definitions are inexpensive wiring checks, not scientific
response or regime findings. Event packet statistics and physical receiver
filters remain in the event-engine scope; mirror/ring boundaries and
publication-scale scans remain deferred.
