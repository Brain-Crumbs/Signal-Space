# Signal Space

A local mathematics workspace and reproducible toolkit for the Paper I directional signal-clock model.

**Current capability:** validate scenarios, inspect their initial preparation, and evolve deterministic Paper I envelopes with causal delay history, error controls, ticks and complete restart snapshots. Seeded stochastic packets, pure observer recording and physical intervention branches are also available through the shared engine. The CLI and typed Web Worker share the numerical implementation. The React shell still displays preparation only; interactive evolution controls and A–I protocols follow in later tasks.

## Quick start

Install Node **24.19.0** (see `.nvmrc`; `nvm install && nvm use` if using nvm) and npm **11.9.0** (`npm install --global npm@11.9.0`). Then, from the repository root:

```sh
npm ci
npm run cli -- --sample isolated
npm run cli -- --sample pair
npm run dev
```

Open the local URL printed by Vite, select a sample, and choose **Inspect preparation**. Cancel requests are sent to the worker; these small samples can finish before a user clicks Cancel. The UI displays simulator truth and the raw initial snapshot with history; it is not an observer inference view.

To inspect a JSON scenario or build both applications:

```sh
npm run cli -- --file fixtures/scenarios/pair.json
npm run build
node apps/cli/dist/index.js --sample pair
node apps/cli/dist/index.js --sample pair --until 1
npm run preview -w @signal-space/web

# T07 declarative experiment commands
npm run cli -- validate --manifest definition.json
npm run cli -- sweep --manifest definition.json --checkpoint sweep.json
```

The CLI emits JSON Lines (progress, snapshot, then completed/cancelled/failed); SIGINT requests cancellation. Exit codes: 0 success, 1 invalid input/failure, 130 cancelled. Use `--help` for arguments. For machine-readable output, invoke the built CLI directly (npm itself prints script banners).

The web build is in `apps/web/dist`; the bundled CLI is in `apps/cli/dist/index.js`. Shared packages expose TypeScript workspace source, consumed by tsx, Vite and the CLI bundler; they are private packages, not separately published Node libraries. No server, database, authentication, secrets or cloud compute is needed. Hosting is outside this epic.

## Workspace

| Path                   | Responsibility                                                                 |
| ---------------------- | ------------------------------------------------------------------------------ |
| `packages/model`       | Versioned TypeScript contracts, JSON Schema, semantic validation               |
| `packages/sim`         | Shared execution API, causal envelope solver and cancellable worker adapter    |
| `packages/analysis`    | Initial-state inventory; numerical diagnostics follow in T06                   |
| `packages/experiments` | Independent copies of isolated/pair smoke fixtures; A–I protocols follow later |
| `apps/cli`             | File/sample input, JSONL output and SIGINT adapter                             |
| `apps/web`             | React shell; typed commands/results across a Web Worker                        |

See [detector records and physical branches](docs/observation.md), [envelope solver](docs/envelope-solver.md), [execution contract](docs/execution-api.md), [experiment runs](docs/experiment-runs.md), [model contract](docs/model-contract.md), [paper traceability](docs/paper-i-traceability.md), and [contributor instructions](AGENTS.md).

## Validation

```sh
npm run check
npx playwright install --with-deps chromium
npm run test:browser
```

The browser suite uses the **production build**, including its emitted worker, and compares its snapshot to the shared engine. Run `npm run build` after source changes before running it separately. CI installs from the lockfile and runs these checks on pull requests and main. Browser installation needs network access and Linux system dependencies; this is test tooling, not an application runtime requirement.

Use `npm run format` to format code and docs. The original dependency-free model tests can also be run with `node --test test/model-contract.test.js`.

Stochastic packets (T04): `node apps/cli/dist/index.js --sample pair --until 2 --seed pair-smoke-v1`. This runs the same seeded engine exposed to the production Web Worker and exports complete physical checkpoints in JSON Lines. See [packet engine](docs/packet-engine.md) for numerical controls, replay and resource limits; these smoke runs are not paper findings.
