# E01 readiness bug bash

Scope: the charged-recurrence experiment in issue #39, using `main` at `4f7e7f617c0ef5f63b0a45324677644b298337ba`. Reviewed the source action/protocol, current E00 numerical control, plugin lifecycle, evidence verification, CLI/service wiring, and research UI. The historical delay-network implementation is separate; its regression suite was retained, but this review does not certify its physics for E01.

## Significant findings and repairs

| Area                  | Finding and resulting behavior                                                                                                                                                                                                                                                 |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Action normalization  | E01's displayed action omitted `1/λ`. Restored it and supplied the explicit E, Q, radius, dimensionless conversion, origin, tail, and spectral-sign ledger.                                                                                                                    |
| Plugin boundary       | Shared manifests, resume requests, analyses, reports, and archive labels assumed the synthetic recurrence. Plugins now declare acceptance/gap metadata and evidence paths; a non-series profile fixture tests the boundary.                                                    |
| Resume                | An old interrupted attempt could be resumed after a later success. Only the latest unsuccessful attempt is eligible; changed execution environments are rejected. Old analyses remain preserved but are not presented as the current result after resume.                      |
| Failure audit         | Preparation and process-launch errors could leave no terminal failure record. Both now preserve failed attempts, partial evidence, and error events.                                                                                                                           |
| Cancellation          | A worker that ignored cancellation could continue until the wall limit. Cancellation now has a bounded grace period and process-group termination.                                                                                                                             |
| Process startup       | Threaded API execution used POSIX `preexec_fn`. Limits now apply in the child before plugin imports.                                                                                                                                                                           |
| Concurrency           | Process-local locks did not serialize CLI/service manifest mutations. OS locks now serialize updates across processes.                                                                                                                                                         |
| Integrity             | Byte hashes alone did not check resolved run identity or analysis input identities. Verification now checks those relations, ordered parents, checkpoint producer/progress, criterion evidence, and saved records. The API rejects changed immutable artifact bytes.           |
| Independent reference | The synthetic closed form lost precision near unit gain; raw analysis accepted malformed step sequences. Stable `expm1` evaluation and strict finite contiguous-prefix validation prevent false controls.                                                                      |
| Import boundaries     | Importing the analysis module directly caused a circular registry import. Package exports now load lazily.                                                                                                                                                                     |
| UI preparation        | Nested solver objects and array-valued settings could become strings. Recursive fields, JSON array/object editors, and enumerated selections retain typed values. Empty required numbers no longer become zero.                                                                |
| UI evidence           | Reports required E00 recurrence filenames; malformed plot rows were silently dropped; delayed polling could contaminate another selected run. Common Markdown previews work without recurrence files, plot corruption is explicit, and stale run/client responses are ignored. |
| Comparison            | JSON key ordering could make identical configurations appear different. Comparisons now ignore object key order while preserving array order.                                                                                                                                  |

## Mathematical review

The source radial equation, origin coefficient `F(f₀)/6`, three-dimensional tail `exp(−kr)/r`, current sign, E/Q normalization, fixed-charge dilation, and coupled L± spectral signs agree with the supplied action. The protocol correction concerns the overall action normalization. See [the analytic ledger](e01-analytic-controls.md) for calculations and source-section mapping.

Continuum tests compare analytic Gaussian observables with independent quadrature, check exterior integrals and the radial origin coefficient, differentiate the effective potential independently to recover L± coefficients, check the vacuum coupled spectral determinant, and differentiate fixed-charge dilation energy. These tests validate specification controls. They are not tests of a production radial discretization, a branch solution, or soliton stability.

## Readiness boundary

The repaired infrastructure supports implementing E01. It does **not** yet run E01: the only registered production experiment remains E00. Issue #39 must supply its closed schema, pinned solver dependencies and recorded numerical-library/thread identities, full checkpoint validation, continuation, independent diagnostics, constrained spectra, breakup/refinement checks, and saved reports. Its candidate/no-candidate/unresolved record must distinguish a resolved negative finding from insufficient numerical coverage.

The generic UI supports configuration, lifecycle, audit, Markdown report preview and artifact downloads. E01-specific interactive branch/spectrum views and rendering richer schema constructs such as references or conditional alternatives must be added with the E01 schema if needed. Windows paths exist for locking/termination but were not exercised in this Linux review. Publication-scale scans and scientific conclusions remain outside this bug bash.

## Validation

`npm ci`, `npm run check`, the built CLI pair sample and `git diff --check` are the local gates. The check suite includes 169 TypeScript/JavaScript tests and 36 Python tests at this revision, including four continuum analytic controls. Browser regression tests cover nested solver/sector settings and non-recurrence reports in addition to the existing workspace journeys.

Local `playwright install --with-deps chromium` is blocked by container package-manager privileges; the browser-only download also timed out. Browser results must be taken from the PR CI run, not inferred from passing type checks or builds. The PR records the final CI result.
