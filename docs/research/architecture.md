# GROSS execution architecture

This document describes software organization. The scientific research layers
and their assumptions are defined in [program v0.3](gross-research-program-v0.3.md)
and the [source audit](gross-projector-control-audit.md). A common runtime does
not identify the projector/event candidate with the continuum candidate.

| Scientific track | Present role | Boundary |
| --- | --- | --- |
| Projector, signal and memory foundation | Exact local laws, configuration persistence, retained-state observation and supplied-incidence propagation | Internal operator geometry is not physical spacetime; graph, order and transports must be declared |
| Residual/control certification | Model-specific existence, finite-time error, invariant regions and observation conditioning | Analysis projections do not replace physical memories or provide a new interaction law |
| Candidate B continuum benchmark | Existing core/clock/reception and Test 8 experiments in the stated continuum action | Four-dimensional domain, metric coupling and Einstein action are assumptions; results do not transfer to Candidate A |

The current registered GROSS models and their locked protocols are the only
active implementation authority. The archived Paper I/E00/E01 systems are not
runtime dependencies.

The Python package has seven scientific/runtime layers:

| Module | Responsibility |
| --- | --- |
| `cli` | JSON command boundary and locked plan/pipeline entry points |
| `contracts` | Closed configuration and evidence validation |
| `runtime` | Lazy registration, resource admission, subprocesses, events, immutable artifacts and restart |
| `experiments` | Registered protocol stages and scientific classification |
| `models` | Versioned actions, equations and conserved quantities |
| `numerics` | Meshes, integrators, spectra and verified checkpoint state |
| `analysis`, `reporting` | Saved-data checks, exact plot data, figures and reports |

The runtime retains the established experiment interface: `describe`, `schema`,
`validate`, `estimate`, `prepare`, `run`, `analyze`, `classify`, and `report`.
The registry imports only the requested GROSS plugin. Physics does not depend on
CLI rendering or storage adapters.

`runtime.scheduler` supervises independent runs in a bounded thread pool;
scientific code executes in isolated subprocesses. Admission reserves each
run's resource ceilings and the total retained-output budget. Operational
thread/case policy participates in run identity, while the locked physics config
is unchanged. Completion order does not change aggregation order or seed ledgers.

The Test 8 quiet adapter additionally schedules independent cases in child
processes. Each case uses the unchanged serial integrator. The coordinator
reserves working memory, consolidates existing canonical raw paths, and saves
hash-linked checkpoint maps for completed and partial cases. This is not a
parallel time integrator and does not enable blocked acceptance-stage physics.

Events are append-only under kernel-released locks. Appending reads only the
last record; sequence continuity is independently checked by verification.
Package sealing retains immutable hash verification and reuses one verified
file digest when constructing its checksum index. No metadata-only integrity
shortcut is used.

Runs, attempts, analyses and reports keep distinct identities. Reanalysis never
changes raw data. Model action, acceptance criteria and detector calibration
remain owned by each registered experiment. The complete package contract is
[artifact-contract.md](artifact-contract.md); execution and platform limits are
[gross-runner.md](gross-runner.md).
