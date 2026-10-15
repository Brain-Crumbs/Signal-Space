# C1-1 source and delivery contract

Scope: [#93](https://github.com/Brain-Crumbs/Signal-Space/issues/93), task 1 of
[#92](https://github.com/Brain-Crumbs/Signal-Space/issues/92), 15 October 2026.
The [theorem](gross-local-record-theorem.md) establishes conditional mathematical
bounds, not a computed robustness certificate. No pilot or confirmation runs,
new physics, thresholds, experiment registration or validated backend are added.

## Reconciled sources

GitHub main was read as `2a00525036008fb3fd7d8bc119cd1a0929957618`, matching
the clean local starting commit and the issue baseline. The only open PR was
#91; all eight remote branch names were inspected and none targets #93 or C1.
An all-state PR search for #93 returned none. One local worktree existed with
no changes. The new branch is `codex/issue-93-preparation-ball`.
Git transport returned proxy CONNECT HTTP 403; the connected GitHub API
provided the exact main ref. Publication uses that authorized connector.

The master explicitly uses textual dependencies. Separate native reads found
no parent for #93 (404, “No parent issue found”) and no sub-issues for #92.
Both issues had no comments. Issue #93 was last updated at
2026-10-15T16:27:42Z; #92 at 2026-10-15T16:30:33Z when audited.
There is no child prerequisite for #93. Tasks #94–#97 remain outside scope.

[Source fingerprints](gross-local-record-sources.json) record SHA-256 for the
actual audited baseline bytes, checked against the local baseline Git objects.
The operator authority SHA-256 is
`c733c958fde54c810c38889e5096de54358a77cc10e69d9f885870832595e123`, exactly
the hash in the master. It remains the equation authority.

PR #91 remains open and untouched at pinned evidence head
`444b4b6425b734b62dd2f4627509f577b8e99c4f`. Its
[result](https://github.com/Brain-Crumbs/Signal-Space/blob/444b4b6425b734b62dd2f4627509f577b8e99c4f/docs/research/gross-linked-memory-results.md)
and compact JSON were fetched at that revision; their local bytes reproduce
the API's Git blob hashes, and their SHA-256 hashes are in the source manifest.
No canonical raw packet bytes or arrays are reused. The retained packet locator
and digest in that JSON are provenance only, not fresh raw-data verification.
The 14 October preparation PDF is not available in this checkout and was not
used as proof authority. This derivation is self-contained. The cloud workflow
SKILL.md texts were read; linked reference resources could not be retrieved.
Repository pipeline/planner skills and artifact/output contracts were read.

## Source-to-obligation audit

| Source | Finding | Consequence for C1 |
| --- | --- | --- |
| Operator program §5 | Reciprocal Hamiltonian law with supplied incidence, unit memories and dimensionless parameter | Derive the gate at lambda=0; no physical time claim |
| `models/reciprocal.py:exact_gate` | Constant Hermitian S, phase factors q and memory norm m; floating eigendecomposition | Algebraically consistent on physical states; not validated arithmetic |
| `models/linked_memory.py` | Fixed active-plus/minus seeds, A/B incidence, additive wave and horizontal ray basis; no fixed-N or fixed-charge projection | Keep 12+2+2 directions and common wave phase |
| `gate_tangent`, `variational_rhs` | Differentiate q, m, S and memory feedback; floating Frechet/ODE paths | Independent diagnostics exist, but they do not enclose derivative errors |
| `physical_features` | 28 redundant real entries (waves plus complex projector entries divided by sqrt(2)) | Isometric to the theorem's 18-dimensional trace-one Hermitian coordinates; do not confuse output storage with physical input dimension 16 |
| `records`, `record_tangent` | Both wave and memory response enter all three records | New bound uses the same mathematical readouts, not a detector law |
| `numerics/linked_memory.py` | Serial gate and tangent composition without cycle resets; basis perturbations only | Retain word convention; basis samples do not cover a ball |
| `tests/test_linked_memory.py` | Independent variational comparisons, phase/charge witnesses, corruption checks, short runtime/export fixture | Preserve tests; new analytic controls supplement rather than replace them |
| Current protocol, ledger and claim register | Global conditional bound has zero useful full cycles; numerical/readout enclosure absent | No inherited certification or Tests 1–11 promotion |

## Preserved evidence and claim classes

The pinned result reports run `run-e350aab835156851`, analysis
`analysis-0001-3daf98c8`: **fail, 5 pass / 2 fail / 2 unresolved**. Its
all-case coherent comparison is `1.0750772e-6` against `1e-9`; the active
cases' better diagnostics do not repair this failure. Signed basis record
errors `2.888845e-5` and `2.242405e-5` and state amplifications `168.27847`
and `103.51826` are reported prior measurements, not recomputed here.
The exact complementarity obstruction and unresolved frozen endpoint criterion
remain distinct. None is changed by a conditional local-record theorem.

The exact identities and conditional inequalities in this change follow from
the declared Candidate A law. Bounded floating tests are engineering diagnostics.
Future validated numerical evidence must discharge every enclosure hypothesis.
No unconditional 32-cycle, within-gate, all-time, stable-object, autonomous-clock,
physical detector, metric-emergence or Candidate A/B bridge claim follows.
Novelty is unassessed. Existing canonical evidence, source equations, configs,
locks and all Tests 1–11 classifications remain unchanged.

## Acceptance matrix and delivery gates

| Criterion | Required evidence | Deliverable |
| --- | --- | --- |
| C1-AC-01 / M-AC-01 | Exact law/extension, isometric 16-direction chart, whole-ball coverage and norm/charge-changing inputs | Theorem §§1–3; bounded analytic controls |
| C1-AC-02 / M-AC-01 | Quantified tube, remainder, rounding and two-track hypotheses with no resets | Theorem computed-reference contract and dependency table |
| C1-AC-03 / M-AC-07 | Source integrity and preserved failures/scope | This audit, source manifest, scoped ledger/claim additions |
| C1-AC-04 / M-AC-01 | Independent analytic proof review, counterexample search, primary-source comparison and retained resolutions | Review record; no inference from diagnostic agreement to proof |

The finite-time theorem needs bounded gate/record Hessians over complete
declared tubes. Children #94–#95 must implement validated arithmetic and a
saved-proof checker; #96 owns measured feasibility and locked plans; #97 owns
authorized confirmation or a gated obstruction. No child is completed here.

Merge is blocked: the connected GitHub API returned HTTP 403 “Resource not
accessible by integration” for `branches/main/protection`. The ruleset list
was empty, which does not establish absence of branch protection. Required
checks and approval rules therefore cannot be certified. No bypass or broader
credentials are used. The PR remains draft and issues remain open until the
authorized merge and post-merge tracking gates can actually be satisfied.
