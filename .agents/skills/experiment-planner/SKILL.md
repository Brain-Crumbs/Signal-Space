---
name: experiment-planner
description: Turn a Signal Space research question into a locked, falsifiable experiment plan with controls, acceptance criteria, and question-driven visual specifications. Use before executing an experiment.
---

Read `AGENTS.md`, `.agents/output-contract.md`, and the relevant model protocol. Create `.agents/schemas/experiment-plan.schema.json` data with a registered config path, model/action/equation references, units, baseline, independent mesh/domain/timestep controls, resource limit, competing predictions, explicit pass/fail/unresolved logic, and a visual plan. Plan at least one physical view and one quantitative discriminating view when the experiment permits both; explain omissions. Each planned visual must connect a question to observables, data, uncertainty, controls, and competing signatures. Lock and validate the plan with `.agents/scripts/experiment_contract.py`. Never make a prior result into a new model axiom.
