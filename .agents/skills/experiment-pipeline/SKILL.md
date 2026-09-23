---
name: experiment-pipeline
description: Plan, run, analyze, visualize, interpret, and package an auditable Signal Space experiment with question-driven figures and a standard export. Use for a complete experiment request.
---

# Signal Space experiment pipeline

Read `AGENTS.md`, `docs/research/artifact-contract.md`, and [the output contract](../../output-contract.md). Use the repository runtime and schemas; never substitute a chat conclusion for a computed check.

1. **Plan:** Use `experiment-planner`. Save a plan conforming to `.agents/schemas/experiment-plan.schema.json`. Specify the exact action, units, controls, competing predictions, pass/fail/unresolved criteria, and visuals before running.
2. **Lock:** Run `python3 .agents/scripts/experiment_contract.py lock PLAN.json`. Review the plan, then validate it with `plan`. Any physical, numerical, or criterion change requires a new lock and run identity. Presentation changes create a new report identity.
3. **Execute:** Use `experiment-runner` and `.agents/scripts/run_plan.py` to verify the exact config bytes and bounded estimate before execution. Preserve every failed or incomplete attempt.
4. **Analyze:** Use `experiment-analyst` on saved outputs and preregistered criteria. Record uncertainty and controls; do not modify raw bytes.
5. **Visualize:** Use `experiment-visualizer`. Generate each planned evidentiary figure from saved plot data, with explicit transforms and interpretations. Mark missing visuals as gaps.
6. **Synthesize:** Use `research-mentor` to connect evidence across experiments and propose the next discriminating calculation. Label speculation and do not promote a numerical classification.
7. **Package:** Use `experiment-packager` to create the standard reader export and validate it. Return the run, analysis, report, and export identities and links.

Stop a dependent stage when its gate fails; record the failure and a useful recovery path. A scientifically failed or unresolved result may still be a valid completed experiment. For plan-only requests, finish at the locked plan and say execution has not occurred.
