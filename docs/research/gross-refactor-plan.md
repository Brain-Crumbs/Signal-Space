# GROSS-only runtime migration

Authoritative baseline: main `89b3b307c621033cade9d34b518a6a4389558ecb`.
Requested 29 September 2026. GROSS is the sole active campaign. Issue #1 is
historical context, not an implementation specification for new work.

## Audit and boundaries

The Python GROSS plugins are independent of the Paper I TypeScript engines.
They do depend on the generic schema checker misleadingly named `contracts.e01`,
the immutable package lifecycle, shared model/numerical modules within GROSS,
and frozen input files in previous GROSS evidence packages. Preserve those
dependencies and every GROSS evidence byte. Archive E01 charged-branch physics,
the E00 synthetic demonstration, the loopback service, older source collections,
and their dedicated tests/docs. Remove the browser/Node toolchain from active
development; preserve historical sources in a quarantined archive.

Measured code findings before changes:

- Registry imports all 18 plugins at startup, including obsolete campaigns and
  eager numerical/report imports.
- CLI sweep executes members serially and has no aggregate resource admission.
- Worker native-library thread counts are inherited from the host; parallel
  jobs can oversubscribe CPUs and memory.
- Supervisor walks the complete attempt directory every 0.05 seconds.
- Event append reads and parses all previous lines, making cumulative logging
  quadratic in event count. Its lock-file creation has an empty-owner race.
- Package sealing hashes immutable files repeatedly, including a second pass
  solely to construct checksums. Integrity verification must remain explicit.
- The existing strict compiled Test 8 kernel and restart format are useful and
  must remain. Six quiet controls still execute serially within one attempt.
- CI, generated boundary types, contributor instructions and the README still
  describe the old UI or E01 program.

## Task commits

1. **Plan and authority:** record this audit, scope, decisions and validation.
2. **Runner:** lazy GROSS registry, common schema API, resource-aware bounded
   parallel scheduling, native thread limits, CLI progress/events and robust
   cancellation. Retain the immutable lifecycle and artifact schema.
3. **GROSS execution:** integrate independent Test 8 quiet scenarios with bounded
   scheduling and restart, while preserving serial reference execution, exact
   equations, frozen sources, chronological state evolution and control order.
4. **Repository migration:** `src/signal_space`, root packaging/CLI, `tests`,
   GROSS-only workflows/docs, archived legacy code with a content manifest.
5. **Verification:** CLI and packaging smoke; serial/parallel equivalence;
   cancellation, limits and restart; all retained regression tests; measured
   engineering timings; final audit and pushed commits.

## Execution design

Independent runs/cases are the units of parallelism. Sequential timesteps and
forecast-before-receiver dependencies remain sequential. A central scheduler
reserves declared memory, output and CPU slots before starting a subprocess;
native BLAS/OpenMP/Numba threads default to one per process. Unfit requests fail
before launch. No automatic scientific parameter or resource-cap changes.
Scheduling settings and actual outcomes are saved in provenance. Failed and
interrupted members remain individually inspectable. Deterministic input order
governs aggregation, regardless of completion order. Restart checks source,
configuration and code identity; it never silently retries with new physics.

The CLI is the only supported execution surface. Existing locked plans and
registered GROSS configurations remain usable. New package paths require
updating active callers, not rewriting historical evidence or source snapshots.
The synthetic demo is replaced by real, inexpensive GROSS runtime controls.

## Validation and completion criteria

- All active experiment IDs begin with `gross.`; no active UI, npm, TypeScript,
  service, E01 or synthetic dependency remains.
- Editable install exposes `signal-space` and the existing Python module CLI.
- Every current locked plan/config validates, and frozen GROSS evidence remains
  byte-identical. Existing Test 1–11 scientific statuses remain unchanged.
- Parallel independent jobs preserve input ordering, seeds and numerical
  outputs; admission prevents declared CPU/memory oversubscription.
- Interrupted jobs terminate their subprocess trees, retain evidence and expose
  supported restart. Partial scheduler records survive interruption.
- New performance claims include measured scope, environment and limitations;
  no claim that the full Test 8 acceptance campaign has run.
- Retained numerical, contract and export tests pass; archive manifest checks,
  package installation, CLI help and `git diff --check` pass.

Long physics campaigns are outside this engineering refactor. The smallest
bounded engineering fixtures will test the new execution paths, without
promoting their results to new physical acceptance.
