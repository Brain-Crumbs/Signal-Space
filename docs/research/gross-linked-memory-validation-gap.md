# Linked-memory validation revision 2

13 October 2026. This is a repair of implementation B, not a completed merge
of implementations A and B. PR90 was refreshed at
`d6707e4f17ddbe58d099c1b070cfcea6b30a3880`, based on
`9668e7394fc463075546971448a4d0b923d2a06e`. Its complete patch reconstructed
tree `3f9d6591aa784afa60e32c68c91972030be07920` exactly. The local snapshot
commit is only a transport reconstruction, not A's implementation.

A's reported commit `0d36461` remains unavailable: GitHub's commit endpoint
returns no matching commit, and the remote branch list supplies no separate A
branch. No A bytes have been incorporated. A source export and subsequent
source-level comparison remain mandatory before declaring integration complete.
The original preparation attachment is also absent from this checkout; the
repository protocol records its hash, but this repair cannot independently
reverify the attachment's bytes. Repository equations, all seven executable
preparations and both original locked plans were inspected and preserved.

## Reproduction and correction

A one-cycle registered engineering fixture reproduced the exact defect:
zeroing only active-plus `record_derivatives` preserved all original check
statuses and values, including tangent-refinement at 1.4722187027744694e-10.
The modified raw file was a disposable copy, not the sealed source run.

Analysis now reconstructs local records through the coherent W/P readout from
saved `finite_states`. Both centered steps and their direct difference are
compared with the saved 3 by 16 record derivative at every A/B prefix. Relative
errors use max(1, Frobenius norm of that derivative), retain the original 1e-4
threshold and enter the existing tangent-refinement gate. All three errors
are saved alongside the plotted sensitivities. No evolution is rerun by analysis.

On the retained one-cycle source data, the clean record comparison is
2.2660675566389265e-10; the zeroed derivative produces 2.322011662383833 and
fails tangent-refinement. Certification remains unresolved in both cases.
The conservative bound still supplies zero full cycles.

## Identity and acceptance

The plugin version is 1.0.1. New plans `gross-linked-memory-v2.json` and
`gross-linked-memory-smoke-v2.json` pin current scientific source hashes and
reference both original locks. Both original plan files and config files stay
byte-identical. The standard recipe selects v2; the original readiness record
is historical evidence for B's original head, not qualification of this repair.

| Requirement | Evidence/status |
| --- | --- |
| Reproduce saved-record gap | Same original check values after zero-only corruption |
| Both steps, every prefix, wave and both memories | Two-cycle regression, both active preparations, all four prefixes and three sectors |
| Actual analysis rejects corrupt plot input | One-cycle runtime/package test; tangent-refinement fails on disposable zeroed copy |
| Preserve equations, thresholds and original locks | Unchanged model/numerics/schema/config; new versioned plans |
| Core regression | 90 tests ran, 84 passed, six optional compiled Test 8 skips |
| Agent contract regression | 13 passed |
| Repository/math/diff | Passed; 22 locked plans, 2,825 research files unchanged |
| Linux and Windows CI, fresh exact-head review | Required on the published head; see PR evidence |
| Integrate A and B | Pending actual A source export |

No confirmatory campaign has run. Resource preflight still admits the estimates
178 CPU seconds, 218.4 wall seconds, 384 MiB memory and 112 MiB output under the
original ceilings; these are estimates, not campaign measurements. Existing
Tests 1-11 classifications are unchanged. Main merge and tracking gates remain
outside this repair's endpoint.
