# E00 research runtime

## Purpose and boundary

The E00 runtime implements issue #37's lifecycle and evidence contracts with one deliberately non-physical deterministic recurrence. A passing fixture establishes that the framework can preserve configuration identity, bounded execution, checkpoint lineage, independent analysis, report regeneration, and package integrity. It makes no claim about a charged recurrence, knot, particle, force, or continuum limit.

The historical TypeScript delay-network engine remains separate. The Node CLI exposes the new runtime only under the explicit `research` namespace; both that adapter and the loopback service invoke the same Python `ResearchRuntime`.

## Fresh install

Install Node 24.19.0, npm 11.9.0, and Python 3.12, then run:

```sh
npm ci
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r python/requirements-lock.txt
python -m pip install -e python --no-deps
npm run check
```

The direct scientific dependencies are pinned in `python/requirements-lock.txt`. The package records the active Python, OS, architecture, NumPy, Matplotlib, dependency-lock digest, Git revision, tree state, and dirty-patch hash in every run. The canonical run ID includes both code and execution-environment identities, so the same configuration executed under materially different recorded environments cannot collide.

## CLI lifecycle

The direct entry point is `signal-space-research`. From a checkout, the equivalent npm command is:

```sh
npm run research -- list
npm run research -- validate --config fixtures/research/synthetic.json
npm run research -- estimate --config fixtures/research/synthetic.json
npm run research -- --workspace .research-work run --config fixtures/research/synthetic.json
```

The Node CLI's thin adapter is also available as `npm run cli -- research ...`. Runtime commands are:

```text
list  validate  estimate  run  sweep  status  cancel  resume
analyze  report  verify  archive  serve
```

Every command emits one JSON document. Errors have stable codes such as `INVALID_CONFIG`, `RESOURCE_REJECTED`, `INVALID_STATE`, `CHECKPOINT_MISMATCH`, and `CORRUPT_ARTIFACT`.

After `run`, use the returned run ID:

```sh
npm run research -- --workspace .research-work analyze --run-id RUN_ID
npm run research -- --workspace .research-work report --run-id RUN_ID
npm run research -- --workspace .research-work verify --run-id RUN_ID
```

Report generation reads the resolved configuration, immutable raw CSV, and selected analysis only. It does not invoke the worker. It writes exact plot data as CSV and JSON; a versioned figure specification; PNG, SVG, and PDF figures; and Markdown, HTML, and checked PDF reports.

### Cancellation and resume

`run` is foreground by default. A second process may request cooperative cancellation:

```sh
npm run research -- --workspace .research-work cancel --run-id RUN_ID
npm run research -- --workspace .research-work resume --run-id RUN_ID
```

The worker checks the attempt-local cancellation record, writes a full checkpoint, and exits in the distinct `cancelled` state. A wall-time kill or injected process loss is `interrupted`; a controlled worker error is `failed`. Resume creates a new linked attempt and never edits its parent. It rejects modified checkpoint bytes, configuration mismatches, and code-identity mismatches. Before selecting a checkpoint, resume also detects a recorded `running` attempt whose worker no longer exists, terminalizes it as an explicit orphaned interruption, and links the new attempt to it.

### Sweeps

The small local sweep adapter takes one or more closed configuration axes:

```sh
npm run research -- --workspace .research-work sweep \
  --config fixtures/research/synthetic.json \
  --axis parameters.gain=0.8,0.9,1.0
```

Every planned member remains visible in the sweep record, including invalid or failed members. Each executed member still receives an independent immutable run package.
The sweep's top-level state and process exit code propagate failed, interrupted, or cancelled member states; a terminal member is never reported merely as `executed`.

## Loopback API

Start the service with a trusted browser origin:

```sh
npm run research -- --workspace .research-work serve \
  --origin http://127.0.0.1:5173
```

Startup prints an ephemeral bearer token and the selected loopback port. Every API request must present that token and the exact `Origin`. Exact-origin CORS headers and strict `OPTIONS` handling permit only `GET`/`POST` with `Authorization` and `Content-Type`. The server refuses non-loopback binding. Operations accept registered experiment/run IDs and configuration documents; there is no shell-command endpoint and no browser-supplied filesystem path. Artifacts are fetched only through IDs from the manifest catalog.

`POST /v1/runs` validates and creates the package, starts execution in a background job, and immediately returns HTTP 202 with the run ID. Clients can then poll status/events or request cancellation while the attempt is active. The foreground CLI remains blocking.

`GET /v1/runs/{run_id}/events?cursor={attempt_id}:{sequence}` supports resumable polling over append-only attempt logs. A missing cursor is an explicit conflict rather than a silent gap.

`GET /v1/experiments/{experiment_id}/schema` returns the authoritative closed configuration schema and its preparation template. `GET /v1/runs` lists saved manifests from the configured workspace in last-updated order. These endpoints let the local UI generate forms and reconnect to durable packages after reload without accepting arbitrary filesystem paths.

For the browser workflow, including token handling, event-gap recovery, compatibility checks, and saved-data report preview, see [the local research workspace](ui.md).

## Resource controls

Validation rejects unknown fields, missing units, non-finite values, and out-of-domain values. `estimate` runs before package creation and compares estimated CPU, memory, disk, and wall time with the declared limits. The worker runs in its own process group. On POSIX, the parent also applies CPU, address-space, and per-file limits. On every platform the parent monitors aggregate attempt bytes and wall time while the worker is running. Cooperative cancellation and soft termination are followed by a guaranteed hard-kill fallback; terminal manifest recording runs even when shutdown handling fails.

These controls bound accidental local workloads; they are not a hostile multi-tenant sandbox. Do not run untrusted experiment plugins.

## Numerical reproducibility limits

The fixture uses a fixed recurrence and a versioned SHA-256 seed-stream ledger. Checkpoints preserve the current field value, index/domain, solver identity, all independent RNG states, pending work, accumulated diagnostics, and producer identities. Its results are deterministic for one Python floating-point implementation.

Future scientific plugins must not overstate that guarantee. Bitwise identity can change across numerical-library, BLAS, compiler, accelerator, thread-count, or hardware revisions. A plugin must record those identities, fix or record reduction order and thread settings, report tolerances and uncertainty, and distinguish bitwise reproducibility from agreement within a declared numerical error budget.

## Adding an experiment

1. Assign versioned experiment and model IDs and add a closed JSON Schema before accepting inputs.
2. Implement `ExperimentPlugin` stages in `python/signal_space/experiments/`; keep equations in `models`, algorithms in `numerics`, diagnostics in `analysis`, and rendering in `reporting`.
3. Register the plugin server-side. Do not expose module names, shell commands, or filesystem paths to the browser.
4. Declare units, domains, resource estimates, independent seed streams, checkpoint state, controls, and pass/fail/unresolved criteria.
5. Add an inexpensive deterministic fixture and fault-injection tests for cancellation, interruption, corruption, and resume mismatch.
6. Generate reports from saved outputs, export exact plot data, and link every classification to checks and artifact IDs.
7. Verify CLI/service parity and schema/type generation with `npm run check`.
8. Archive any verified, explicitly classified (`pass`, `fail`, or `unresolved`) run with a report. Preserve its classification, failures, and limitations in the catalog.

## Known limitations

- E00 is local and single-host; it does not provide distributed scheduling or hostile-code isolation.
- The service uses resumable polling rather than a long-lived push transport.
- Resource enforcement is strongest on POSIX; Windows retains wall-time, aggregate-output monitoring, and process-tree termination but lacks the POSIX pre-exec limits.
- The archive command requires a verified package, explicit scientific classification, and generated report. It does not upload large artifacts to external storage.
- The synthetic fixture is not the E01 charged-recurrence solver.
