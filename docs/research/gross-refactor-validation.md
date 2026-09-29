# GROSS refactor validation

This is an engineering validation of the runtime migration, not new Test 8
scientific evidence. Existing GROSS evidence and Test 1–11 classifications remain
unchanged. The [plan](gross-refactor-plan.md) and [CLI guide](gross-runner.md)
define the migration and supported surface.

## Completed checks

- 76 retained Python tests pass, including compiled-backend numerical controls.
- 13 reader-contract/pipeline tests pass, including locked-plan tampering,
  preserved failure logs, immutable input checks, reports and reader exports.
- All 16 registered experiments are GROSS plugins; all 17 current locked plans
  and registered configuration fixtures validate.
- All 386 archived files match their recorded SHA-256 and byte size.
- All 2,825 current research files match the reviewed index. No file under
  `research/experiments/` changed from main `89b3b307c621033cade9d34b518a6a4389558ecb`.
- No active Node, npm, TypeScript, browser, HTTP service, synthetic demo, or E01
  plugin remains. Historical snapshots are explicitly excluded from this claim.
- Serial and parallel GROSS algebra outputs match byte for byte, including RNG
  start/end records. Parallel Test 8 quiet arrays and sample traces are identical
  to serial execution in both NumPy and compiled modes. Interrupted/resumed
  parallel execution matches uninterrupted serial output and preserves prior
  attempt bytes. Corrupted checkpoint references are rejected.
- Process-tree cleanup, event concurrency/truncated tails, resource admission,
  queued cancellation, aggregate output enforcement and retained member failures
  pass their engineering controls.

## Measured overhead and throughput

Measured at clean commit `2e2398d9beb01e0f18002db3632ecd5ad59de343` with Python
3.12.14, NumPy 2.3.5, SciPy 1.17.0, and two worker slots. The exact environment,
measurements, run identities and raw-equivalence hashes are in
[gross-runner-benchmark.json](gross-runner-benchmark.json).

| Bounded workload | Reference | New path | Observed ratio |
| --- | ---: | ---: | ---: |
| 1,500 durable event appends | 2.911 s, full-log parse per append | 0.098 s, tail-only append | 29.68× |
| Four independent 1,000-sample GROSS algebra jobs | 3.740 s, one worker | 1.874 s, two workers | 2.00× |

The logging reference omits the obsolete lock overhead, favoring the reference.
Both paths flush and fsync each event. The batch timings include process startup,
source/environment identity, immutable hashing and output I/O. Twenty raw file
comparisons across four jobs match exactly, and every canonical run verifies.

These are single bounded observations on this host, not a statistical speed
model or a prediction for the full Test 8 campaign. A pipeline smoke ran
concurrently during part of this measurement; rerun on the intended machine for
capacity planning. Memory bandwidth, matrix sizes, JIT startup, sampling and
checkpoint I/O can change scaling. No universal "optimal runtime" is claimed.

Reproduce from a clean checkout with:

```sh
python scripts/benchmark-runtime.py --output /path/outside/checkout/benchmark --members 4 --jobs 2 --events 1500
```

This host exposes an opaque process namespace to psutil. Resource records
therefore explicitly report that live process-tree CPU/RSS metrics are
unavailable here. POSIX kernel limits, memory admission, cancellation, wall and
output limits remain exercised. Native Windows and Linux CI cover their own
process environments; the local result does not establish Windows execution.

## Installed CLI and packaging smoke

The installed `signal-space pipeline --experiment gross-test-01` completed in
6.062 s from the same clean commit. Canonical run `run-ebe0d60ff5d2c544`, analysis
`analysis-0001-dca8fedb`, report `report-0001`: six locked algebra checks pass;
canonical verification and paired reader export verification succeed. It is a
reproduction of the existing Test 1 protocol, not a new campaign milestone.

The reader contains both required PDFs, question-driven figures and exact plot
data. The source snapshot is 412,469 bytes (242 entries); it contains active
source and no legacy archive or unrelated historical experiment packages.
Full smoke/benchmark run bytes are generated outside Git and are reproducible
with the commands above. Compact measured evidence is retained in this document
and the adjacent JSON rather than duplicating all binary figures in the repo.

## Remaining scientific and platform limits

The full Test 8 exchange/long-clock campaign has not run. Joint quiet preparation,
G0–G9 exchange acceptance and Test 9 reconstruction readiness remain governed by
the existing ledger and acceptance design. This refactor does not alter those
models or thresholds. Independent quiet-case scheduling is the first case-level
adapter; other protocols use independent-run scheduling until their dependencies
are explicitly expressed by an appropriate adapter.

The first remote run passed both suites on Ubuntu and Windows. Windows then
exposed locale-dependent decoding in the repository-wide locked-plan verifier.
Active text readers/writers now specify UTF-8; archived and evidence bytes were
not rewritten. CI reruns the full matrix for this correction.

CI runs the retained suites on Ubuntu and Windows. PR checks are the authority
for the latest remote revision; local success is not a substitute for those
platform results.
