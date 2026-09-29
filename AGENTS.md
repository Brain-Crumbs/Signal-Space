# Signal Space contributor instructions

## Authority and scope

GROSS is the sole active Signal Space implementation and research campaign.
Read `research/papers/gross-operator-program-v0.2.md`, the current protocol,
`docs/research/gross-progress.md`, `docs/research/architecture.md`, and
`docs/research/artifact-contract.md` before changing the model or runner.
Issue #1 and everything under `archive/` are historical evidence, not current
requirements. Do not import archived code or silently reuse historical equations.

Work on a feature branch and commit coherent tasks. Preserve others' work and
all canonical GROSS evidence. Do not merge or deploy without authorization.

## Active implementation

- Python 3.12+, source in `src/signal_space`, regression tests in `tests`.
- `signal-space` / `python -m signal_space` is the supported CLI.
- Closed schemas in `contracts/research`; locked configurations in
  `fixtures/research`; plans/protocols in `docs/research`.
- The runtime owns lifecycle, resource scheduling, subprocess isolation, events,
  provenance and immutable package verification. Plugins own scientific stages.
- Use the common schema API `signal_space.contracts.schema.check`.
- Register only `gross.*` experiments. No browser, npm, TypeScript, HTTP service,
  E00 demo, or E01 charged-branch compatibility work belongs in the active tree.
- Parallelize independent preparations, never coupled timesteps or a forecast
  and the receiver whose response it predicts. Keep native threads bounded.

## Scientific discipline

Use `.agents/skills/experiment-pipeline/SKILL.md` and `.agents/output-contract.md`
for experiments. Lock equations, exact config hashes, controls, resource ceilings,
criteria and planned figures before execution. Validate using the registered
runtime. A model/numerical change requires a new versioned plan and run identity.

Preserve every failed/interrupted attempt, seeds, full restart state and raw
bytes. Reanalysis and report regeneration create new identities. Technical
completion and scientific pass/fail/unresolved/not-evaluated are distinct.
Never change acceptance thresholds to make a run pass. Do not infer geometry,
gauge structure, protected topology or particle identity from visual resemblance.

Keep directional drift, anisotropy and geometry with material response open to
discrimination. Distinguish coordinate changes from invariant local detector
records. Keep Candidate A and Candidate B separately versioned. Update the
Tests 1–11 progress ledger only when new evidence justifies a status change.

Every research figure includes Question, Reading, Significance and Limitation,
with exact saved plot data. Full evidence, figures and reader exports belong in
run artifacts; avoid adding repeated binary exports to Git. Existing checksummed
GROSS evidence must remain byte-identical during code refactors.

## Validation

From the repository root:

```sh
python -m pip install -r requirements-lock.txt
python -m pip install --no-build-isolation --no-deps -e .
python -m unittest discover -s tests -v
python -m unittest discover -s .agents/tests -v
python scripts/verify-repository.py
python scripts/check-experiment-math.py
git diff --check
```

Compiled-backend tests require `requirements-performance-lock.txt`. Use bounded
engineering fixtures for a refactor; publication-scale physics campaigns need
their own locked plans and resource gates. Report missing platform/dependency
coverage honestly. Do not run archived test suites or install archived npm files.

Explain the problem, resulting behavior, numerical limits and validation in PRs.
Never represent engineering tests as new scientific acceptance or reviewer approval.
