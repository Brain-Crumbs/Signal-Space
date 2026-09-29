# Running and recovering research campaigns

The workbench uses the existing registered physics, locked criteria and canonical
packages. A technically completed run can still fail or remain unresolved.
`test8-quiet` runs the six-period prerequisite. `test8` inspects the full exchange
proposal and deliberately refuses execution while required capabilities are absent.

## First local run

Use a dedicated clean checkout and Python 3.12 environment. Install
`requirements-performance-lock.txt` and then the editable package:

```sh
python -m pip install -r requirements-performance-lock.txt
python -m pip install --no-build-isolation --no-deps -e .
signal-space recipes
signal-space doctor --recipe gross-test-08-quiet-optimized --case-jobs 2
signal-space pipeline --experiment gross-test-08-quiet-optimized --case-jobs 2 --output ../quiet-001
```

Start with one numerical thread per independent case. More threads do not make
the current serial Numba kernel parallel. Doctor checks exact plan/config locks,
frozen input hashes, clean source, backend compilation, static figure questions,
host memory/CPU and retained output/export space. A compiler probe is a tiny
synthetic zero-state control. Static report validation is not a rendered report
or a physical acceptance gate. Both original and resumed quiet report/export
paths have saved-data engineering fixtures. For any registered recipe with
complete prior saved analysis, run `signal-space report-smoke --plan PLAN.json
--run /absolute/canonical-run --output ../report-check`. This copies evidence,
regenerates a report, packages and verifies it without evolving fields or editing
the original run. Compact indexes alone cannot substitute for missing raw/derived
files; import the full paired evidence first.

The original `gross-test-08-quiet` remains discoverable and unchanged. Its dense
checkpoint estimate exceeds its locked output ceiling. The local compatibility
wrapper now defaults to the separately locked optimized preset:

```sh
python scripts/run-test8-local.py --case-jobs 2 --output ../quiet-001
```

Outputs must be outside the source checkout. Keep that checkout and environment
unchanged while a campaign runs; use another worktree for development. CPU/wall
estimates are labeled legacy and unmeasured until compatible observations exist.

## Observe, stop and recover

The pipeline prints its run ID, attempt and workspace immediately. From another
terminal, substitute the printed ID below:

```sh
signal-space --workspace ../quiet-001/evidence/runs status --run-id RUN_ID --watch --human
signal-space --workspace ../quiet-001/evidence/runs events --run-id RUN_ID --follow --cursor-file ../quiet-events.json
signal-space --workspace ../quiet-001/evidence/runs cancel --run-id RUN_ID
signal-space pipeline --resume --output ../quiet-001
```

Events include run, attempt, case, stream and sequence. Cursors are acknowledged
after output and must be outside the run package. Human status includes queued
and active cases, steps, throughput, estimated remaining time, checkpoint age,
observed memory and output. Missing process metrics are explicitly marked.

`pipeline.json` records each stage's attempts, errors, identities and elapsed
time. Resume reuses a completed solver, existing analysis and a compatible
report; it retries failed later stages. A partial reader directory is retained
and a new numbered reader is created. Failed initial preflight can also resume.
Checkpointed numerical continuation creates a new immutable attempt. Solvers
without a compatible checkpoint need a new run/output; the CLI never silently
restarts them. Analysis/report recovery may use new code and records that code.
Numerical restart requires the original source/patch and environment and explains
which identities differ.

## Derive an operational plan

Resource changes create new config and plan hashes. All original scientific
parameters, controls and analysis criteria remain unchanged. The plan schema
also supports an optional explicit CPU ceiling; old plan locks are unchanged.

```sh
signal-space derive --plan docs/research/plans/gross-test-08-quiet-optimized.json --max-wall-seconds 43200 --output ../quiet-longer-budget
signal-space doctor --plan ../quiet-longer-budget/plan.json --case-jobs 2
signal-space pipeline --plan ../quiet-longer-budget/plan.json --case-jobs 2 --output ../quiet-002
```

Quiet plans additionally allow explicit `--backend`, `--neutral-mode` and
`--checkpoint-stride` changes within the existing closed execution schema.
`derivation.json` records predecessor hashes and before/after values. This does
not change the observation duration or make full exchange executable.

## Persistent campaigns

```sh
signal-space campaign inspect test8
signal-space campaign preflight test8-quiet --profile desktop --case-jobs 2 --output ../campaign-001
signal-space campaign start test8-quiet --profile overnight --case-jobs 2 --output ../campaign-001
signal-space campaign status ../campaign-001 --watch --human
signal-space campaign stop ../campaign-001
signal-space campaign resume ../campaign-001
signal-space campaign export ../campaign-001
```

Desktop reserves half the available CPU slots and 70% of the already discounted
available memory, with at most two jobs by default. Overnight uses available
slots and 90% of that memory, with at most four jobs. These are conservative
capacity profiles, not recommended speedup factors. Admission can reject a locked
run that does not fit; it never lowers or raises its scientific budgets. Explicit
`--jobs`, `--threads` and `--case-jobs` refine scheduling within those capacities.

Use `docs/research/campaigns/operator-chain.json` as a dependency example. Copy a
campaign design outside Git, edit it prospectively, then run `signal-space
campaign lock PATH`. Its closed graph rejects unknown nodes and cycles. Every
edge explicitly supplies allowed scientific `classifications` and required
passing `checks`. Empty classifications mean a deliberately technical-only edge.
Do not use that escape to substitute for a scientific prerequisite.

Nodes contain a locked `plan`, `dependencies`, and optional `reuse_from` pipeline
or `cost_profile` path. Use absolute paths for external reuse and profiles.
Verified completed nodes retain their exact manifest references. Reuse requires
identical configuration, locked plan, producer code and execution environment;
changed inputs never silently reuse a result. The graph enforces ordering and
acceptance. Input artifacts must already be explicitly frozen in each config;
no forecast or calibration is implicitly injected into a dependent experiment.

Ready independent nodes run under combined CPU and locked memory reservations.
Longer estimated/measured nodes run first. Independent quiet cases use a declared
cells-times-steps proxy and retain canonical input order when aggregated.
The campaign records all sessions, node checkpoints and numerical identities.
CPU charges accumulate across attempts; wall time includes pipeline stages.
When CPU metrics are unavailable, wall time times reserved CPU slots is charged
conservatively. Retained bytes include failed attempts; export reserves up to four
times each run ceiling plus metadata headroom. No sealed evidence is pruned.
Checkpoint cadence bounds lost work only while the worker can respond to stop;
a forced kill cannot promise a newly written checkpoint.

## Measure and compare saved work

```sh
signal-space profile collect --pipeline ../quiet-001 --output ../quiet-cost.json
signal-space profile match --profile ../quiet-cost.json --plan docs/research/plans/gross-test-08-quiet-optimized.json --case-jobs 2
signal-space compare /absolute/run-A /absolute/run-B --output ../comparison
```

Quiet timing separates setup/JIT, steps, health scans, diagnostics, complete
checkpoint serialization and final output. Pipeline stage timings include
analysis, plotting, verification/hashing and reader creation; handoff indexes
measure ZIP writing, CRC checks and hashing. Collection does not launch physics.
Profiles record their exact producer, work, backend/settings, hardware and
observed range. An incomplete resume segment cannot predict a whole workload.
A stale profile is reported and falls back to a labeled estimate. No full quiet
speedup or full Test 8 cost is asserted by the small engineering controls.

Compare verifies both packages, displays configuration differences first and
then compares common saved check quantities. Changed model, physical inputs,
calibration, seed or criteria block subtraction; explicit numerical/execution
controls stay visible. Values retain source units; there is no automatic rescaling,
acceptance promotion, convergence-order fit or field alignment. The original
clock/marker/conservation figures remain the source of detailed histories.

`signal-space panel --spec SPEC.json --output ../panel` provides reusable saved
CSV panels for field/energy-flow series, local markers, clock records,
conservation, convergence and decision margins. A `gross-panel-v1` spec names
`data`, its `sha256`, `kind`, explicit `x_unit`/`y_unit`, declared transformations
and Question/Reading/Significance/Limitation. CSV columns are `series,x,y`; an
optional `threshold` is in y units. All rows and their order are retained, with
PNG/SVG/PDF, exact plot data and source hashes. Spatial maps and worldtube
measurements still require the corresponding saved observables.

## Verified handoff

```sh
signal-space export --pipeline ../quiet-001 --locator https://YOUR-DURABLE-ARCHIVE/quiet-001
signal-space import --index ../quiet-001/handoff/pr-evidence-index.json --output ../quiet-import-check
signal-space --workspace /absolute/runs export --run-id RUN_ID --plan PLAN.json --output ../existing-run-handoff
```

Both ZIPs and their index form one immutable handoff. Import validates ZIP
identities, safe members, outer hashes, canonical verification and reader/run
pairing. Exporting an existing run copies its original canonical bytes and states
whether its complete producer source archive was supplied. It never substitutes
current source for that producer. Existing handoffs are verified before reuse;
changed source evidence requires a new handoff directory. Interrupted temporary
ZIPs are retained for diagnosis; select a new export directory to retry.

Upload the exact archives to durable external artifact storage, verify a fresh
download/import, and put the compact hash index and locator in a results PR.
GitHub Actions artifacts require a durable mirror before expiration. Repeated
binary reader exports and ZIPs do not belong in Git/LFS by default. Existing
archived evidence stays byte-identical. Uploading, review and scientific acceptance
are separate from local packaging; these commands do not upload files.

The current Tests 1–11 summary comes from `gross-progress.json`; run `signal-space
ledger --markdown` or `python scripts/update-research-ledger.py`. Evidence hashes
must still agree. Historical narratives remain preserved in `gross-progress.md`.
