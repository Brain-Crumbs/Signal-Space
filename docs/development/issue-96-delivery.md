# Issue96 delivery evidence

Source: issue96 updated2026-10-15T16:29:23Z; parent92. Base main
43e5c91b9edf0c4cdff116fdb1425bc0b40f3b13 includes prerequisites93–95.
Branch: codex/issue-96-certificate-pilot. Endpoint: draft PR; no merge.

| Criterion | Implementation and evidence | Status |
| --- | --- | --- |
| C4-AC-01 | Closed schema/config, plugin and source-pinned prepare/estimate; negative parameter tests; unchanged old files | Pass |
| C4-AC-02 | Locked plan; registered run_plan pilot; attempt0001 and canonical verification; presentation failures retained | Pass |
| C4-AC-03 | Four independent seed/precision proof replays, controls and five saved checks | Pass |
| C4-AC-04 | Measured admission, one-shot aggregate guard and explicit blocked readiness; no32-cycle run/command | Pass, obstruction path |
| C4-AC-05 |126 tests,13 agent tests, repository/math/plan/canonical/reader checks; hosted CI tracked on PR | Original local pass; Ubuntu/Windows CI pass at e66ccdb; archival follow-up blocked below |

Scientific execution revision770729bc416d866d0948fff34f01295dafb953fc; final
local test revision59cf6f8e70748ba81980a04fbd362d3a10c8226a (presentation
fixes only since science). Full test elapsed59.048s; agent-contract tests7.209s.
Tests execute engineering fixtures; saved pilot supplies scientific evidence.

Independent review found source-cleanliness, native-thread, failed-checker-log
retention and zero-prefix handling gaps before launch; all repaired and
regression checked. The original PR description reports post-pilot review of
all four proof packets and exact lock/source hashes, and final submitted-tree
review. The fresh PR lookup returned no review submissions or discussion
comments; the handoff report is not a GitHub approval. Best-practices guidance now explains consumed
aggregate reservations and blocked-admission semantics with issue96 evidence.

The evidence archive locator/hash and readiness details are in
../research/gross-certificate-pilot-results.json. No prior canonical evidence,
physical model, thresholds or Tests1–11 ledger entries were changed.

## Archival follow-up (18 October 2026)

[GROSS Python CI run 39142377812](https://github.com/Brain-Crumbs/Signal-Space/actions/runs/39142377812)
completed successfully for submitted head
`e66ccdb089c1e7994d39ddea940b76dcaedabbd6`. Both Ubuntu and Windows executed
the Python and agent suites, repository/math checks, export scan, doctor and
diff check. This is historical exact-head evidence; subsequent commits require
their own CI result.

[Artifact contract section 2](../research/artifact-contract.md#2-package-layout)
requires the same manifest and checksums in Git even when the package is
external. The current compact index retains a checksum-file digest and Library
locator, but not those original files. No approved superseding rule was found
in the repository instructions, issue #96, master #92 or PR #101 discussion.
Archival compliance therefore remains blocked, independently of the original
pilot's reported scientific result and CI success.

Library resolved `libfile_a03f1e592bdc8191b72d09d3e7b1dad9` to version 1 of
`gross-c1-issue-96-evidence.zip` (2,636,185 bytes), matching the index filename
and size. The current supported consumer-local transfer helper failed with
`library file transfer failed: download failed`, both in the sandbox and on an
approved outside-sandbox retry. No readable local archive was obtained.
Consequently its SHA-256, original manifest/checksums, canonical verification
and paired-reader verification were **not freshly verified** in this follow-up.
The earlier verification record is retained as historical evidence, not a new
verification result. No replacement manifest was reconstructed from the index.

To complete the correction, restore supported access to that same Library
version, verify the archive against its indexed SHA-256, check canonical and
paired-reader integrity, and commit the identical manifest and checksums from
the retained run. No scientific rerun or contract relaxation is needed.
Main-branch protection and repository-ruleset reads also returned `Forbidden`;
merge requirements remain unverified. Keep PR #101 and issue/master tracking
open. Confirmation remains blocked by CPU/wall/memory admission; PR #91 is
outside this follow-up.
