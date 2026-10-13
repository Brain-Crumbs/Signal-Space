# Linked-memory implementation readiness

12 October 2026. Scope: implement and qualify the separately registered v0.3
seed, then lock its executable plan. The **64-cycle campaign is unrun** and
its scientific classification is **not evaluated**. One-cycle engineering
fixtures do not meet that campaign's horizon or any Tests 1-11 acceptance.

## Implemented and locked

Experiment `gross.linked-memory-persistence.v1` reuses unchanged
`signal-space.ss-ops-1.v1` and the existing exact gate. It adds the supplied
three-port/two-memory A,B adapter; independent pure coherent W/P integration;
full 12+2+2 real physical tangent sectors; chart perturbations and raw endpoint
histories; independent saved-data analysis; five question-driven figures; and
the common canonical/reader pipeline.

Campaign configuration: `fixtures/research/gross-linked-memory.json`.
Exact file SHA-256:
`296a700bd6ad3cfc8d6fd21f3cea5d642facb1df8539b73ffef529b2ea6950c2`.
Plan: `docs/research/plans/gross-linked-memory.json`.
Locked SHA-256:
`25ee1feefd7190fe3a23bf386bd26c6d310550459decb6f1ec2a56d85a031266`.
Use the byte hashes emitted by the current repository validator as authority
if this document and a future version disagree; a changed plan needs a new lock.

All seven original preparations are preserved. The packet's false assertion
that preparation 2 is a commuting full-word persistence control is corrected
before locking: A transfers a wave into port 2, making B's complement derivative
have norm $\kappa/\sqrt2>0$. Its isolated A/B words remain exact controls.
See [the full analytical protocol](gross-linked-memory.md).

## Engineering evidence and review

Final validation: 89 core tests ran, with 83 passing and six optional compiled
backend cases skipped. All 13 agent contract tests pass; repository integrity,
all locked plans, math formatting and diff checks pass.

Twelve targeted tests cover closed schemas, exact nulls, the corrected
commuting obstruction, coherent signs and matrix-charge cancellation, physical
order, description covariance, Frechet phases, independent variational ODE,
chart/record derivatives, sampling, cancellation, raw metadata/continuity,
nonresetting bounds, and complete registered run/analysis/report/export
verification. The integration test asserts that unresolved certification and
disproved universal persistence are not promoted to acceptance.

Retained engineering run `run-cea81a267ad9dcac`, latest analysis
`analysis-0002-6143bf19`, report `report-0002`, and paired reader `reader-v3`
verify. These local QA artifacts are kept outside Git; source and compact
readiness records are versioned. The configured horizon is one cycle only.
Largest coherent/refinement mismatch: $2.34\times10^{-11}$; ledger residual:
$3.67\times10^{-11}$; relative tangent comparison: $1.47\times10^{-10}$.
All six engineering checks pass. The two universal complement claims fail in
the fixture; end-to-end prediction certification remains unresolved. These
are separate from software/package success and campaign acceptance.

The first engineering analysis hit a NumPy-boolean JSON serialization error;
it was fixed and the unchanged raw data reanalyzed. Reader packaging then
rejected differing exact question text; presentation wording was aligned and
the engineering plan relocked. Failure records and earlier identities remain
retained; no thresholds, initial states or model equations were changed.

A fresh independent review checked the source hashes, analytical obstruction,
coherent signs, horizontal projector norm and comparison region. Six random engineering states from one RNG stream seeded 73012 were checked against the variational ODE, with
maximum component discrepancy $2.71\times10^{-15}$. All substantive review
objections were resolved. The paired bundle and regenerated figures were
reviewed; both reader PDFs were rendered and visually inspected.

## Resource admission and unresolved limits

The registered campaign preflight accepts the locked config with one native
thread, 64 nominal cycles and 32-cycle perturbation studies. Estimates are
178 CPU seconds, 218.4 wall seconds, 384 MiB memory and 112 MiB output, within
ceilings of 300 CPU/wall seconds, 1024 MiB memory and 128 MiB output.
These are conservative serial engineering projections, **not measurements of
the full campaign**. The wall envelope is $20+2.5c+1.2p$ seconds and CPU
envelope $18+2c+p$, where c is nominal cycles and p is sensitivity cycles.
The output envelope is $16+1.5c$ MiB. Runtime ceilings stop overruns rather
than guaranteeing successful completion on every platform.

The retained one-cycle worker measured 0.8674 wall seconds and 428272 bytes
of attempt output. Canonical and reader footprints at this QA revision were
3124172 and 2182144 bytes. Fixed report/source overhead and variable trajectory
storage are included in the conservative projection. Sampling may miss a
brief resource peak. **CPU and RSS measurements are unavailable** because this
host has an opaque process namespace; their logged zeros are placeholders,
not measurements. The runtime reports POSIX per-worker kernel limits on this
platform. No full-campaign resource qualification is claimed.

The exact-region global Lipschitz comparison is valid for two exact admissible
trajectories, with initial error at most $10^{-6}$. It is too conservative to
support a positive full-cycle preparation horizon at the allocated record
budget. Validated numerical residual, roundoff and real readout enclosures
remain absent. Consequently no positive certified horizon, all-time stability,
Floquet result, autonomous clock or emerged physical geometry is claimed.

Optional compiled Test 8 backend coverage is separate from this NumPy/SciPy
plugin and was unavailable in the regression environment. Existing Test 2
fixtures and all canonical research bytes remain unchanged; repository archive
and research-index verification check that boundary.

## Launch boundary

The requested implementation/validation/locking stage is complete. The
following command checks the plan/config and estimate without execution:

```sh
python .agents/scripts/run_plan.py --plan docs/research/plans/gross-linked-memory.json --repo-root . --workspace ../linked-memory-campaign --threads 1
```

The complete `signal_space pipeline --experiment gross-linked-memory` recipe
is available for a separately authorized campaign. Its next substantive question
is measured finite-time record sensitivity versus a sharper same-family bound;
the full four-ray classification and Tests 1-11 retain their own requirements.
