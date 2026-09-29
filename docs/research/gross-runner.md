# GROSS CLI and execution guide

GROSS is the only active experiment campaign. Install the Python package from
this checkout and use the CLI; no browser, Node or local HTTP service is needed.
The models, locked thresholds and frozen source bytes are unchanged by scheduling.

```sh
python -m pip install -r requirements-lock.txt
python -m pip install --no-build-isolation --no-deps -e .
signal-space list
signal-space doctor
signal-space estimate --plan docs/research/plans/gross-test-01.json
signal-space --workspace /path/outside/checkout/runs run --plan docs/research/plans/gross-test-01.json
signal-space pipeline --experiment gross-test-01 --output /path/outside/checkout/test-01
```

`python -m signal_space` exposes the same commands. `signal-space-research` is a
compatibility alias. `pipeline` runs the locked recipe and creates canonical
and reader evidence, figures and PDFs. Technical completion and scientific
classification remain separate. Scientific review is still required.

## Scheduling and resources

```sh
signal-space --workspace /path/runs batch --plan docs/research/plans/gross-test-01.json --plan docs/research/plans/gross-test-02.json --jobs 2 --cpu-slots 4 --memory-mb 4096
signal-space --workspace /path/runs sweep --config fixtures/research/gross-test-01.json --axis seeds.root=101,102,103 --jobs 3
python -m pip install -r requirements-performance-lock.txt
signal-space --workspace /path/quiet run --plan docs/research/plans/gross-test-08-quiet-optimized.json --case-jobs 2
```

Batch members must be scientifically independent. Dependency ordering remains
part of the locked design; never launch a forecast and its held-out receiver as
independent jobs. A sweep creates new configurations and run IDs and is not a
substitute for preregistering a research campaign.

The batch scheduler reserves each run's **locked memory ceiling**, not an
optimistic estimate. Total retained output ceilings must fit the output budget;
completed output remains on disk. `--jobs` bounds concurrent runs. `--threads`
(default 1) pins BLAS/OpenMP/Numba native threads. `--case-jobs` (default 1)
reserves additional CPU slots per run and is available only for the Test 8 quiet
plugin. Available CPU affinity/cgroup quota, memory and disk are checked before
launch. Other jobs can change host availability after admission; the monitor
therefore checks live use as well.

Quiet case scheduling reserves a conservative per-case working set plus a
192 MiB coordinator allowance inside the unchanged run memory ceiling. Case
order and within-case timesteps are unchanged; completion order does not affect
aggregation. No inner parallel reduction or fast-math change is introduced.
The serial path remains available. Each child keeps its log/checkpoints and the
coordinator stores a hash-checked restart map. A resumed attempt copies verified
completed case outputs and continues each unfinished case at its saved step.
Final outputs also appear at the canonical raw paths for existing analyses.
This intentionally retains child evidence and can increase archive storage;
output limits still apply to the full attempt.

The supervisor checks aggregate process-tree CPU/RSS and output every 0.5 s,
with wall/cancellation polling every 0.1 s. Limits are sampled, so small transient
overshoots are possible; POSIX workers also use kernel CPU/address-space/file
limits. On a platform whose process namespace is opaque, the resource record
explicitly marks unavailable process metrics. Quiet child CPU ceilings are then
conservatively divided among the cases and coordinator; memory reservations and
per-child POSIX limits remain. This is not equivalent to exact process-tree
accounting. `resource-usage.json` records measured peaks and the enforcement
scope. Wall and output checks work independently of process metrics.

Use `doctor` to size a run, and benchmark on the target machine. More workers
cannot guarantee faster execution for small jobs or memory-bound kernels.
Compilation/startup and checkpoint I/O are part of elapsed time. The existing
strict optional Numba backend requires `requirements-performance-lock.txt` and
an explicitly selected registered backend; the scheduler never switches it.

## Monitoring, cancellation and recovery

```sh
signal-space --workspace /path/runs status
signal-space --workspace /path/runs events --run-id RUN_ID --follow
signal-space --workspace /path/runs cancel --run-id RUN_ID
signal-space --workspace /path/runs resume --run-id RUN_ID
signal-space --workspace /path/runs analyze --run-id RUN_ID
signal-space --workspace /path/runs report --run-id RUN_ID
signal-space --workspace /path/runs verify --run-id RUN_ID
```

Events stream as JSON lines with run, attempt and sequence IDs. Resume requires
matching code, environment, policy, configuration and verified checkpoint
bytes. It adds an attempt and preserves the previous one. Ctrl+C in a batch
cancels active workers and records queued members as cancelled before launch.
A failed member stays failed; the scheduler does not silently retry it.
POSIX process groups and Windows kill-on-close Job Objects keep child solvers
owned through worker failure and supervisor shutdown.

Batch records live in `WORKSPACE/batches/` and are atomically updated at each
launch/completion. Per-run packages remain the authoritative scientific evidence.
The current Test 1–11 statuses are in [the progress ledger](gross-progress.md).
No scheduler benchmark passes a new scientific gate.

## Prepared Test 8 execution preset

`gross-test-08-quiet-optimized` is a separately locked operational preset for the
existing six-period quiet protocol. It selects the strict compiled backend with
the full neutral sector and checkpoint stride 5000 within the original
512 MiB output ceiling. Preflight estimates 324 MiB serial or 466 MiB with
parallel child evidence retained. Physical preparations, grid/time
steps, diagnostics, sample cadence and acceptance thresholds are unchanged.
The original plan/config bytes remain intact; its default checkpoint estimate
is 1011 MiB against a 512 MiB cap and is correctly rejected by preflight.
The two-case memory reservation is 2,546 MiB within the unchanged 4 GiB ceiling.
The new preset is validation/estimate-ready, **execution pending**.

```sh
signal-space estimate --plan docs/research/plans/gross-test-08-quiet-optimized.json --case-jobs 2
signal-space pipeline --experiment gross-test-08-quiet-optimized --case-jobs 2 --output /path/outside/checkout/quiet
python scripts/run-test8-local.py --recipe gross-test-08-quiet-optimized --case-jobs 2 --output /path/outside/checkout/quiet-zips
```

Use a new output path for each command; these are alternative complete launch
commands, not sequential stages of one run. Install the performance dependency
lock first. CPU/wall estimates remain the conservative existing projection;
compiled full-case throughput is not inferred from the small scheduler benchmark.
