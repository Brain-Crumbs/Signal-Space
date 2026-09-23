---
name: experiment-packager
description: Assemble and verify a standard Signal Space experiment export with results, figures, setup and results PDFs, interpretations, and next calculations. Use for a completed experiment handoff.
---

Read `.agents/output-contract.md`. Use one selected run/analysis/report and their source manifest. Regenerate a report from saved analysis if needed; never rerun physics while packaging. Prepare a JSON interpretation map keyed by saved figure ID, with Question, Reading, Significance, and Limitation, and a mentor Markdown assessment. Verify the original run with the runtime `verify` command, then invoke `.agents/scripts/package_experiment.py` with the locked plan and source directory. It builds the PDFs, copies data/code/figures, and checks the bundle. Recheck with `python3 .agents/scripts/experiment_contract.py bundle DIR`; fix gaps before delivering. Keep optional figures labeled optional and document omissions.
