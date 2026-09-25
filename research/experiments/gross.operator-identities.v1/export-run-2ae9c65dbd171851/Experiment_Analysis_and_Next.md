# Test 1 interpretation and next calculation

The registered 1,000-sample operator identity experiment completed and passes all six preregistered checks. This is a mathematical implementation result, not evidence of physical propagation or emergent spacetime.

## Findings and evidence

- Coverage: all 1,000 seeded matrix inputs and measurement rows are present. Independent analysis reconstructs the Pauli components directly from saved matrix entries.
- Largest scale-normalized valid-domain residual: 3.963119603223247e-14, below the frozen 1e-10 gate.
- Minimum tested positive observer-form eigenvalue or observer norm: 0.010339055007300693.
- Tetrahedral Gram spectrum discrepancy: 4.440892098500626e-16 from (-1/3,-1/3,-1/3,1).
- Deliberately omitting the transformed ray weight produces 0.6321205588285577 relative reconstruction error, matching 1-exp(-1) and exceeding the 1e-3 control-detection gate.
- Ten collinear/near-collinear preparations are accounted for. The rank-one aggregate has no normalized timelike observer; ill-conditioned aggregates are reported outside the valid domain without regularization.

See `results/tables/checks.json`, `results/data/derived/residuals.csv`, `results/data/derived/controls.json` and `results/data/derived/conditioning.json`. Raw matrices are preserved in `results/data/raw/attempt-0001/inputs.npz`; the seed stream and initial/final RNG states accompany them. The figure interpretation map is `figures/figure_index.json`.

## Physical interpretation

The determinant, positive observer norm and transformed weighted rays form a consistent implementation of the proposed operator constitution. The observer's positive form is not invariant if one inconsistently transforms a state but leaves its observer or weight fixed. The negative control makes this distinction measurable in the algebra.

The four-projector spectrum verifies an internal Lorentzian basis. It does not demonstrate four-dimensional physical spacetime, a causal cone, a preferred physical tetrahedron, or a law of motion. Those require a separate event/derivative map and dynamics.

## Limits and non-applicable checks

The acceptance population is finite and explicitly restricted to moderate conditioning. This computation does not replace the exact algebraic derivations, prove a universal numerical error bound, or authorize normalizing a singular aggregate.

There are no spatial fields, time integration, boundaries, conservation dynamics or detector records in Test 1. Mesh/domain/timestep convergence and physical clock invariance are not evaluated. The numerical controls here are conditioning, independent formulas, exact cases and deliberately inconsistent transformations. No confidence level is assigned to the 1e-10 deterministic threshold.

There was one full scientific execution attempt and no failed scientific run. Small infrastructure fixtures and an intentionally corrupted copy of fixture evidence were used in software tests, not counted as scientific samples. Report 2 only moves an annotation clear of the plotted controls; report 1, raw data, analysis and classification are retained unchanged.

## Next discriminator: Test 2

Register the SS OPS 1 reciprocal event equations and a concrete acyclic circuit with at most 32 events. Freeze the participants, memory wires and couplings before execution. Test conservation of incoming weight, memory norm and the event matrix charge. Compare two permitted topological schedules, independent local basis changes with transformed transport, a shared-memory order reversal and frozen-memory backreaction control.

Competing signatures: the stated reciprocal law conserves its matrix ledger and makes independent event rescheduling observationally irrelevant; a routing or backreaction error violates the ledger, causal dependence or scheduling equivalence. Use the source's 1e-9 gate and tighten integration tolerance independently. A successful result would justify the router/full-spectrum tests, not establish physical momentum or a metric.

Test 5's continuum action audit is a separate branch. Tests 6-9 remain dependent on an accepted readable clock. The current algebra pass does not rehabilitate earlier failed clock readouts, erase the historical split-cone finding, or complete a microscopic-to-continuum map.
