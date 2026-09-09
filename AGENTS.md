# Signal Space contributor instructions

Read parent issue #1, your assigned child, its dependencies and this file before editing. Work on an issue-focused branch and PR; preserve others' changes. Do not merge or deploy unless separately authorized.

## Scientific scope

- Use the `paper-i-v1` contract and the source provenance in `docs/paper-i-traceability.md`. The current Paper I manuscript is not committed. Paper III and the original galaxy-rotation paper are different scopes.
- Record material ambiguities as explicit decisions. Never silently add forces, phase resets, readable source labels, synchronization or a hidden-state oracle. Name model variants separately.
- Keep physical state, observer records, deterministic envelopes and stochastic realizations distinct. Detector deletion changes records; physical pulse removal is an intervention.
- Preserve unwrapped phase, delay history, pending packets/responses, filters and RNG state. Current phases alone are not a restartable network.
- Validate units and admissible domains at boundaries; document tolerances and solver settings. Keep browser UI and Node imports out of shared numerical packages.
- Use independent analytic, causal, state-bound and statistical controls where appropriate. Preserve independent seeds and uncertainty in stochastic work. A test must not assert a desired scientific conclusion.
- Small reproducible fixtures are authorized. Publication-scale scans, regime findings, manuscript conclusions, binding, generated motion and conservation closure remain deferred.

## Architecture and task boundaries

Use `packages/model`, `sim`, `analysis`, `experiments`, `apps/cli`, `apps/web`; all consumers use the same engine. Browser work runs in a Web Worker with typed messages. `inspect` is only a T02 preparation check at t=0, not a numerical solver or replay implementation. Keep future features in their assigned tasks.

UI controls must be keyboard accessible and show units, assumptions, loading, cancellation and failure states. Use saved engine data for charts and clearly label simulator-only information. No server, database, login or hosted deployment is required.

## Required validation

Use Node from `.nvmrc` and npm 11.9.0. From a fresh checkout:

```sh
npm ci
npm run check
node apps/cli/dist/index.js --sample pair
npx playwright install --with-deps chromium
npm run test:browser
git diff --check
```

`check` includes formatting, lint, strict type checking, contract/execution/CLI tests and both production builds. Run browser integration tests when changing web, worker, build or shared execution paths. Use `npm run format` after edits. Commit package-lock.json for dependency changes. Never bypass failing gates; report environmental limitations accurately.

Each PR must link its child issue, explain the problem and resulting behavior, map paper sections/equations, list validation evidence and limits, and update traceability/docs. Resolve relevant review findings with tested commits; explain irrelevant findings with evidence. Close a child only after acceptance criteria are met. Do not report tests as reviewer approval.
