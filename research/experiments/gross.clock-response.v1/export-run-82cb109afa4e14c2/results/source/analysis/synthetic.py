from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any

from signal_space.numerics.synthetic import recurrence
from signal_space.runtime.io import write_json


def analyze_series(raw_path: Path, output_path: Path, config: dict[str, Any]) -> dict[str, Any]:
    with raw_path.open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    observed = [(int(row["step"]), float(row["value"])) for row in rows]
    parameters = config["parameters"]
    if not observed or [step for step, _ in observed] != list(range(len(observed))) or observed[-1][0] > int(parameters["steps"]):
        raise ValueError("raw series must be a nonempty contiguous prefix starting at step zero")
    if any(not math.isfinite(value) for _, value in observed):
        raise ValueError("raw series contains non-finite observations")
    expected = recurrence(
        float(parameters["initial_value"]),
        float(parameters["gain"]),
        float(parameters["forcing"]),
        int(parameters["steps"]),
    )
    if any(not math.isfinite(value) for value in expected):
        raise ValueError("independent reference exceeds finite arithmetic")
    output_path.mkdir(parents=True, exist_ok=True)
    derived_path = output_path / "derived/series.csv"
    derived_path.parent.mkdir(parents=True, exist_ok=True)
    with derived_path.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["step", "observed", "expected", "absolute_error"])
        for step, value in observed:
            writer.writerow([step, format(value, ".17g"), format(expected[step], ".17g"), format(abs(value - expected[step]), ".17g")])
    complete = len(observed) == int(parameters["steps"]) + 1 and observed[-1][0] == int(parameters["steps"])
    max_error = max((abs(value - expected[step]) for step, value in observed), default=float("inf"))
    checks = {
        "schema_version": "research-checks-v1",
        "checks": [
            {
                "id": "fixture-complete",
                "status": "pass" if complete else "fail",
                "value": len(observed),
                "expected": int(parameters["steps"]) + 1,
                "evidence": "derived/series.csv",
            },
            {
                "id": "fixture-recurrence-error",
                "status": "pass" if max_error <= float(config["analysis"]["max_abs_error"]) else "fail",
                "value": max_error,
                "threshold": float(config["analysis"]["max_abs_error"]),
                "unit": config["units"]["value"],
                "evidence": "derived/series.csv",
            },
        ],
    }
    summary = {"row_count": len(observed), "complete": complete, "max_abs_error": max_error}
    write_json(output_path / "checks.json", checks)
    write_json(output_path / "derived/summary.json", summary)
    return {"checks": checks, "summary": summary}
