# Signal Space

Signal Space is a computational research program testing whether local, finite-speed reception dynamics can support stable recurrence structures, topology-constrained matter states, and—only after explicit derivation gates—the gauge and gravitational limits of known physics.

The project is deliberately organized around questions and falsifiable experiments rather than particle-name correspondences. Knot or winding topology may constrain a state space; it does not, by itself, produce a gauge theory, fermions, or the Standard Model.

## Current research position

The working hypothesis is that a complete finite-energy recurrence can carry protected winding and coherent internal response modes. In the hadronic branch, effective quark labels are treated as responses of the complete object, not as three independently postulated classical knots.

What is established in the imported record is narrower:

- selected 1+1-dimensional charged formation and phase-sensitive interaction results;
- weak structural radiation and damping diagnostics for that model family;
- an operational positive-signal construction, Lorentz-cone representation, and clock-calibration analysis;
- explicit 3+1-dimensional charged and Hopf model proposals that still require independent numerical tests.

Stable three-dimensional charged branches, charged–Hopf binding, fermionic quantization, emergent gauge fields, chiral matter, and a common gravitational limit remain open. The repository must preserve that boundary between result, proposal, and conjecture.

## Program map

| Area                  | Purpose                                                                              | Start here                                                                 |
| --------------------- | ------------------------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| Research architecture | Shared runtime, model plugins, audit trail, analysis, reports, and UI boundaries     | [`docs/research/architecture.md`](docs/research/architecture.md)           |
| E00 runtime guide     | Install, lifecycle CLI/API, recovery, extension workflow, and reproducibility limits | [`docs/research/runtime.md`](docs/research/runtime.md)                     |
| Artifact contract     | Immutable run packages, provenance, checksums, figures, reports, and claims          | [`docs/research/artifact-contract.md`](docs/research/artifact-contract.md) |
| Experiment sequence   | Ordered gates from synthetic fixture through integrated theory tests                 | [`docs/research/experiment-plan.md`](docs/research/experiment-plan.md)     |
| First experiment      | Three-dimensional charged recurrence branch and constrained stability protocol       | [`docs/research/first-experiment.md`](docs/research/first-experiment.md)   |
| Theory and evidence   | Papers, milestones, figures, source code, configurations, and compact results        | [`research/README.md`](research/README.md)                                 |
| Local UI              | Search and inspect the research collection; retain the separate historical workspace | `npm run dev`                                                              |

The first implementation issues are [#37 common framework](https://github.com/Brain-Crumbs/Signal-Space/issues/37), [#38 research UI](https://github.com/Brain-Crumbs/Signal-Space/issues/38), and [#39 E01 charged branch](https://github.com/Brain-Crumbs/Signal-Space/issues/39).

## Repository layout

```text
apps/
  cli/                 Historical CLI plus thin `research` runtime adapter
  web/                 Local research browser and historical workspace
contracts/research/    Authoritative versioned runtime and artifact schemas
docs/research/         Architecture and experiment protocols
packages/              Historical delay-network model and shared UI engine
python/signal_space/   Scientific plugins, bounded runtime, analysis, reports, service
research/
  papers/              Theory manuscripts and research assessments
  milestones/          Executed-result reports
  figures/             Curated diagnostic figures
  source/              Reproducibility code, configs, manifests, compact outputs
  experiments/         Accepted immutable run packages
```

The existing TypeScript delay-network implementation is preserved as a separately labeled historical workspace. It is not the numerical foundation for the new charged-recurrence and knot program.

## Quick start

Install Node **24.19.0** (see `.nvmrc`), npm **11.9.0**, and Python **3.12**, then:

```sh
npm ci
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r python/requirements-lock.txt
python -m pip install -e python --no-deps
npm run verify:research
npm run check
npm run dev
```

Open the local Vite URL to search papers, milestones, figures, and source collections. The explorer remains read-only until issue #38 connects it to the loopback API. The runtime, lifecycle CLI, report generator, and origin-bound local service are implemented by issue #37; see the [E00 runtime guide](docs/research/runtime.md).

Run the synthetic framework fixture, which makes no physics claim:

```sh
npm run research -- validate --config fixtures/research/synthetic.json
npm run research -- estimate --config fixtures/research/synthetic.json
npm run research -- --workspace .research-work run --config fixtures/research/synthetic.json
```

The historical workspace remains available on the same page. Its direct CLI commands are unchanged:

```sh
npm run cli -- --sample isolated
npm run cli -- --sample pair --until 1
```

## Research discipline

Every experiment must:

1. begin with a declared model/action, units, boundary conditions, and input ledger;
2. define success, failure, and unresolved outcomes before the expensive run;
3. use independent analytic, convergence, conservation, and negative controls;
4. preserve seeds, solver state, failures, and incomplete sweep coverage;
5. separate raw outputs, derived analysis, figures, and scientific claims;
6. regenerate reports without rerunning the physical simulation;
7. compare against held-out observables only after calibrations are frozen.

Negative and unresolved results are valid completed experiments. A visual resemblance, fitted particle label, or post-hoc numerical coincidence is not a derivation.

## Validation

```sh
npm run verify:research
npm run check
npx playwright install --with-deps chromium
npm run test:browser
git diff --check
```

`verify:research` checks the catalog and byte-level archive manifest. `check` runs formatting, lint, strict type checking, generated contract checks, historical and E00 lifecycle tests, and production builds. Browser tests exercise the built worker and research explorer.

## Data policy

Git stores manuscripts, source, configurations, compact tabular/JSON results, report code, and curated figures. Large field arrays, probe streams, and transient binaries belong in immutable external run packages identified by hashes; accepted run summaries and manifests are archived under `research/experiments/`. This prevents Git history from becoming the raw-data backend while keeping every accepted claim traceable.
