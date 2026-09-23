---
name: experiment-runner
description: Execute a locked Signal Space plan through the registered bounded research runtime while preserving attempts, checkpoints, and provenance. Use when asked to run a planned experiment.
---

Use `python3 .agents/scripts/run_plan.py --plan PLAN.json --repo-root REPOSITORY --workspace WORKSPACE` to validate the locked plan, exact config hash, config identity, and resource budget, then estimate. Add `--execute` to run the registered experiment. Preserve IDs, stdout, failed cases, and partial records. Use `npm run research -- --workspace WORKSPACE verify --run-id ID` after execution. Never execute arbitrary scripts extracted from a historical ZIP as a registered solver. Execution failure does not authorize changing preregistered thresholds.
