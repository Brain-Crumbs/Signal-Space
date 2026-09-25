# Signal Space / GROSS Test 5: continuum action audit

Tracked by #62, based on operator program v0.2 §§7–8, 12.3 and 15.5. The bounded calculation completed with all seven preregistered action/characteristic/control checks passing. It tests the *chosen* SS OCF 1 local matter coupling. Nonlinear Einstein evolution, constraint-satisfying curved initial data and a bound clock have not been demonstrated.

Start with the [reviewed reader export](export-run-d3333c7602af3e47/README.md), [results PDF](export-run-d3333c7602af3e47/Experiment_Results.pdf), [reviewed interpretation](export-run-d3333c7602af3e47/Experiment_Analysis_and_Next.md), or [canonical run](run-d3333c7602af3e47/manifest.json).

- Model: `signal-space.ss-ocf-1.action-audit.v1`; 200 seeded local coframes, 20 directions, six matter sectors and 48,000 saved roots.
- Run: `run-d3333c7602af3e47`; analysis: `analysis-0001-4dbb966f`; report: `report-0001`. Complete local recipe: see `provenance` and the run manifest.
- Maximum Hessian/operator-metric discrepancy `8.88e-16`; matter equations `4.88e-16`; characteristic polynomial/root discrepancy `1.77e-15` against a locked `1e-10` gate.
- The negative-Z and separately versioned quartic orientation controls trigger; orientation speed `0.934947` against metric speed `1` in the control.

The selected run is independently verifiable using `PYTHONPATH=python python3 -m signal_space --workspace research/experiments verify --run-id run-d3333c7602af3e47`. Validate the reader with `python3 .agents/scripts/experiment_contract.py bundle research/experiments/gross.continuum-action.v1/export-run-d3333c7602af3e47`. After merge, rerun manually via Actions > Run experiment > `gross-test-05`. The workflow uploads new evidence and reader packages; it does not commit them.

`provenance/pipeline-attempts` retains two failed export attempts, including their raw attempts and logs, distinctly labeled and never counted as validated runs. `provenance/source-history.bundle` recovers the local source commits recorded in raw run provenance if this branch is published through the GitHub connector. No merge or deployment is included.
