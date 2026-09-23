---
name: experiment-analyst
description: Evaluate Signal Space run outputs against preregistered criteria, numerical convergence, controls, and uncertainty, preserving pass/fail/unresolved outcomes. Use after a saved run.
---

Read the locked plan, saved manifest, and `checks.json`. Run the registered runtime's `analyze` stage without rewriting raw artifacts. Link each conclusion to the saved check and comparison data. Include conservation, boundary, discretization, calibration, and held-out controls appropriate to the question. Mark criteria not measured as `not-evaluated`, borderline results as `unresolved`, and failure when the declared test fails. Distinguish technical completion from scientific outcome. Write tables and derived data under the immutable analysis, then verify the run again.
