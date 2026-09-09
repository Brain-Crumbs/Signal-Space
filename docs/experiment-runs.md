# T07 experiment runs

T07 implements the declarative run layer for Paper I §§11.1 and 11.11. The source is `packages/experiments/src/runs.ts`; it is shared by the CLI and the browser bundle. These are reproducibility and wiring controls, not completed A–I experiments or scientific findings.

## Definition format

An `ExperimentDefinition` contains one validated `paper-i-v1` scenario, an execution mode (`inspect`, `envelope`, or `packets`), an absolute end time, parameter axes, explicit E/R variants, named analytic/causal/state-bound/statistical controls, interventions, transient and measurement windows, tolerances, requested observables, replicate count, a root seed, and resource/checkpoint budgets. The scenario remains the authority for units, histories, filters, pending packets/responses, observation protocol, solver settings and physical interventions.

Parameter paths are top-level scenario fields or `nodes.<node id>.<numeric field>`. Axes are expanded in sorted axis-id order; axis IDs and target paths must be unique, axis values must be unique, and the resolved Cartesian plan is bounded by `budgets.maxRuns` (default 100,000). Variants and controls are applied to detached scenarios and validated against both the exported JSON Schema and semantic model contract, so every resolved manifest contains the complete reproducible scenario rather than an undocumented notebook patch. Nested diagnostic windows are positive, post-transient, and shortest-to-longest containment chains.

## Identity and provenance

`resolveDefinition` canonicalizes finite JSON with lexicographically sorted object keys and hashes the definition and each resolved scenario with SHA-256. A run identity includes experiment, variant, control, parameter values and replicate index. Every manifest retains its root seed; packet runs derive a separate physical seed from that root seed and run identity, and validation recomputes both the run ID and derived seed. Therefore editing a saved identity or seed cannot silently change a replicate, and concurrency or scheduling order cannot change it. Detector/intervention seed namespaces remain part of the lower-level packet options and are not silently reused as physical seeds.

Each manifest stores model/schema versions, code revision, dirty state, source, creation time, solver settings through the scenario, complete initial history, observation/detector protocol, interventions, windows, tolerances, observables, budgets, the root seed, and the derived physical seed where applicable. Run results retain all low-level events, including complete envelope/packet checkpoints and explicit completion, cancellation, incomplete or failure status.

## Sweeps and recovery

`runSweep` bounds concurrent jobs by `budgets.maxJobs` and the requested concurrency. It emits detached run results/checkpoints through callbacks and returns a `SweepCheckpoint` with both successful `completed` results and append-only `attempts`, including cancelled, failed and resource-incomplete runs. `resumeSweep` verifies the definition hash, exact plan manifest identity (including scenario, options, windows, budgets and seed), terminal statuses and event ownership before skipping only successfully completed work; unsuccessful attempts remain auditable but are retried. A restarted sweep is a new execution from its manifest; `continueRun` is a separate operation that extends the end time from the saved full solver checkpoint and transfers delay history, filters, queues and RNG state. It never reconstructs state from current phases alone. Resource-incomplete runs cannot be continued without revised immutable budgets.

The CLI exposes:

```text
npm run cli -- validate --manifest definition.json
npm run cli -- run --manifest definition.json
npm run cli -- sweep --manifest definition.json --checkpoint sweep.json --concurrency 2
npm run cli -- resume --manifest definition.json --checkpoint sweep.json
```

The CLI writes checkpoint files in sequence, reports compact checkpoint summaries on stdout, returns nonzero status for failed, incomplete or partial runs, and maps SIGINT to a cancelled run. Packet and envelope solver options are validated before a definition is accepted.

The exported `smokeSetupIds` and `createSmokeDefinition` provide inexpensive, protocol-shaped fixtures for setups A–I. They deliberately use the existing isolated/pair contract fixtures and do not launch research-scale scans. No research manifests are bundled.
