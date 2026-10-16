# Issue 94 delivery record

Scope: [#94](https://github.com/Brain-Crumbs/Signal-Space/issues/94) only, under
[#92](https://github.com/Brain-Crumbs/Signal-Space/issues/92). Main baseline
`6b748dc373fc74dfd94f75d91369d394f7d056d6`; prerequisite #93 is closed/completed
and PR #98 is present in that actual main tree. Master updated
2026-10-15T22:05:49Z; child updated 2026-10-15T16:28:12Z; neither had comments
at preflight. The master explicitly uses textual child links. No native
hierarchy change is performed. No issue-94 branch/PR existed; open PR #91 was
the sole open PR and remains untouched. Isolated branch:
`codex/issue-94-validated-gates`, targeting main.

## Acceptance matrix

| Criterion | Evidence | Delivery status before submitted-head review |
| --- | --- | --- |
| C2-AC-01 / M-AC-02 | Pinned CPython arithmetic; integer dyadic proof; exact-source pi/chart; local state/DF/readout intervals and metadata | Implemented and locally qualified; independent review and exact-head CI pending |
| C2-AC-02 / M-AC-02 | Analytic full-box gate/readout Hessian majorants, ambient Hermitian extension, no eigenbasis division | Implemented; independent proof review pending |
| C2-AC-03 / M-AC-02,03 | Exact rational/commuting/dark/witness controls, invariants/covariance, corruption and missing-tail tests; retained fixed smoke cost/width table | Locally qualified; no long-horizon inference |
| C2-AC-04 / M-AC-07 | Existing physics/configs/canonical files untouched; targeted and AGENTS validation; best-practices addition | Local verification and CI evidence recorded in PR; optional compiled backend absent locally |

The [proof/API document](../research/gross-validated-local-backend.md) maps
all local quantities to code. The [cost record](../research/gross-local-backend-costs.json)
preserves the failed rational-size attempt and both successful fixed smokes.
The 24-call fixture is bounded to 30 CPU / 45 wall seconds, 1024 MiB and 8 MiB;
the final measured run used 5.47 CPU / 5.48 wall seconds and 2.41 MB output.
A repeated full development suite has a 120-second timeout; targeted tests,
agent-contract checks and repository verifiers are also engineering work.
No pilot, 32-cycle campaign, scientific budget expenditure, experiment
registration, #95 implementation or positive certified-horizon claim occurs.

## Verification and reproducibility

- New local qualification tests: exact polynomial arithmetic, an independently
  exercised missing exponential/derivative tail, both events/seeds against the
  independent variational ODE, dark/commuting/degenerate/off-manifold cases,
  all chart sectors, invalid modes/deadlines, local-output corruptions,
  exact first-word complement witness, N/J/r3 and covariance controls.
- Full suite: 106 tests; local compiled-backend coverage has six expected skips
  because numba/llvmlite are not installed. The initial full-suite attempt
  found a test setup calling the newly guarded chart under a deliberately
  unsupported runtime; the setup was corrected, without weakening the guard.
- Agent-contract suite: 13 tests pass, 10.544 seconds.
- Repository verifier, math formatting, reader-package scan, doctor and diff
  checks pass after moving engineering fixtures into `tests/fixtures`.
- No tracked files under `research/experiments`, `fixtures/research`, old plans,
  source model implementations or prior theorem/source-audit files change.
- Local build-only setuptools is 84.0.0 versus lock 80.9.0; scientific diagnostic
  versions match the base lock. CI installs pinned dependencies and runs both
  Ubuntu and Windows, including optional compiled tests.

The GitHub workflow skill was read in full; its two linked reference resources
were unavailable. Repository AGENTS, experiment pipeline/planner skills,
output/artifact contracts, current protocol, architecture, operator §5,
program v0.3, progress ledger, theorem/source audit and best practices were
read. This is numerical qualification, not an experiment-pipeline execution.

Git transport and the optional Arb package installation returned proxy CONNECT
403. Neither was bypassed. The existing authorized GitHub connector supplies
repository reads and publication; its remote main SHA matches the local base.
No credentials, access expansion or paid services are used.

## Merge and tracking boundary

The branch-protection endpoint returned 403, “Resource not accessible by
integration.” An empty ruleset list and the ordinary branch summary do not
establish the required review/check rules. Merge remains blocked until those
actual gates can be verified; no admin bypass or assumed absence of gates.
Retain a draft PR. Required GitHub approvals are distinct from the independent
agent review requested by the workflow. No issue closure, master-checkbox edit
or post-merge claim is made. Exact submitted head, review findings/fixes and CI
run evidence belong in the PR record, avoiding self-referential commit hashes
inside this file. Any new head requires fresh review and CI.
