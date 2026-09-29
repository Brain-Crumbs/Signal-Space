# Signal Space · GROSS

A Python CLI for the **Generalized Relative Operational Signal Space** research
campaign: registered models, bounded experiments, immutable evidence and
question-driven scientific reports.

**GROSS is the sole active implementation.** Start with the
[current program](research/papers/gross-operator-program-v0.2.md),
[Tests 1–11 progress ledger](docs/research/gross-progress.md), and
[CLI guide](docs/research/gross-runner.md). Prior campaigns are preserved in
[archive/](archive/README.md) for historical audit.

```sh
python -m pip install -r requirements-lock.txt
python -m pip install --no-build-isolation --no-deps -e .
signal-space list
signal-space doctor
signal-space estimate --plan docs/research/plans/gross-test-01.json
signal-space pipeline --experiment gross-test-01 --output /path/outside/checkout/test-01
```

Use a Python 3.12+ environment and an editable install from this source checkout;
frozen evidence and locked plans are repository resources. On Windows use a
normal absolute output path such as `C:\runs\gross-test-01`. The equivalent
module entry point is `python -m signal_space`.

Independent runs can use `batch --jobs N`; Test 8 quiet controls support
`run --case-jobs N`. The runner reserves resource budgets, caps native threads,
retains interruption/restart evidence and streams JSON events. See the
[execution guide](docs/research/gross-runner.md) for commands, limits and recovery.
The optional strict compiled Test 8 backend uses
`requirements-performance-lock.txt` and an explicitly registered backend config.

| Path | Purpose |
| --- | --- |
| `src/signal_space/` | CLI, runtime, models, numerics, analysis and reporting |
| `tests/` | GROSS and execution regression controls |
| `contracts/research/` | Closed experiment and evidence schemas |
| `fixtures/research/` | Registered GROSS configurations |
| `docs/research/` | Protocols, locked plans, ledger and engineering guides |
| `research/` | Current program and preserved GROSS evidence |
| `.agents/` | Experiment workflow and reader export contract |
| `scripts/` | Repository verification and bounded performance tools |
| `archive/` | Inactive historical sources and provenance manifest |

No UI, Node, npm or TypeScript installation is needed. The current scientific
status is unchanged: Test 7 has a bounded accepted radial protocol; full Test 8
exchange and Test 9 readiness remain unestablished. Runtime improvements do not
change those conclusions.

See [AGENTS.md](AGENTS.md) for contributor and validation instructions.
