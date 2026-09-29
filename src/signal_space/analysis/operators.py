"""Independent Pauli-component audit of saved matrix inputs and measurements."""

import csv
import numpy as np

from signal_space.runtime.io import read_json, write_json


def components(x):
    # Deliberately independent of the model's trace/Pauli implementation.
    return np.array([(x[0, 0].real + x[1, 1].real) / 2, x[0, 1].real,
                     -x[0, 1].imag, (x[0, 0].real - x[1, 1].real) / 2])


def minkowski(x, y):
    return float(x[0] * y[0] - x[1:] @ y[1:])


def analyze(run_path, output, config):
    paths = sorted((run_path / "attempts").glob("*/raw/measurements.csv"))
    if not paths:
        raise ValueError("no saved matrix measurements")
    raw = paths[-1].parent
    with paths[-1].open(newline="") as f:
        rows = [{k: float(v) for k, v in row.items()} for row in csv.DictReader(f)]
    required_errors = {"det_transform_error", "g_transform_error", "sl_error", "observer_det_error",
                       "norm_transform_error", "norm_identity_error", "projector_error", "projector_trace_error",
                       "weighted_ray_error", "euclidean_error"}
    if not rows or any(not required_errors <= row.keys() or not all(np.isfinite(v) for v in row.values()) for row in rows):
        raise ValueError("missing or nonfinite raw measurements")
    with np.load(raw / "inputs.npz", allow_pickle=False) as saved:
        arrays = {key: saved[key] for key in ("x", "y", "j", "z", "s", "constituents")}
    n = config["parameters"]["samples"]
    complete = len(rows) == n and [row["sample"] for row in rows] == list(range(n)) and all(len(a) == n for a in arrays.values())
    if not complete:
        raise ValueError("saved sample coverage does not match the resolved configuration")
    derived = []
    for i, row in enumerate(rows):
        x, y, j, z, s, a = [arrays[k][i] for k in arrays]
        cx, cy, cj = [components(v) for v in (x, y, j)]
        if not all(np.all(np.isfinite(v)) for v in (x, y, j, z, s, a)):
            raise ValueError("nonfinite saved matrix input")
        detj = minkowski(cj, cj)
        if detj <= 0 or np.linalg.cond(j) > 100.000001:
            raise ValueError("random sample outside preregistered observer domain")
        t = j / np.sqrt(detj)
        ct = components(t)
        zz = np.outer(z, z.conj())
        reference_norm = 2 * minkowski(ct, components(zz))
        sp = s @ z
        tp = s @ t @ s.conj().T
        transformed_norm = 2 * minkowski(components(tp), components(np.outer(sp, sp.conj())))
        independent = {
            "det_reference_error": abs(row["det_x"] - minkowski(cx, cx)) / max(1, np.linalg.norm(x) ** 2),
            "polarization_reference_error": abs(row["g_xy"] - minkowski(cx, cy)) / max(1, np.linalg.norm(x) * np.linalg.norm(y)),
            "norm_reference_error": abs(row["observer_norm"] - reference_norm) / max(1, abs(reference_norm)),
            "transformed_norm_reference_error": abs(row["observer_norm_transformed"] - transformed_norm) / max(1, abs(transformed_norm)),
            "constituent_error": float(np.linalg.norm(j - a @ a.conj().T) / max(1, np.linalg.norm(j))),
            "independent_covariance_error": abs(reference_norm - transformed_norm) / max(1, abs(reference_norm)),
        }
        derived.append({**row, **independent, "max_residual": max([row[k] for k in required_errors] + list(independent.values()))})
    controls = read_json(raw / "controls.json")
    near = read_json(raw / "conditioning.json")
    limit = config["analysis"]["max_residual"]
    expected_spectrum = np.array([-1 / 3, -1 / 3, -1 / 3, 1])
    gram_error = max(float(np.max(np.abs(np.linalg.eigvalsh(controls["gram"]) - expected_spectrum))),
                     float(np.max(np.abs(np.array(controls["gram_eigenvalues"]) - expected_spectrum))))
    expected_angles = [0.0, *config["parameters"]["near_angles"]]
    near_ok = len(near) == len(expected_angles) and [r["angle"] for r in near] == expected_angles
    for row in near:
        angle = row["angle"]
        expected_status = "singular" if angle == 0 else "valid" if 1 / np.tan(angle / 2) ** 2 <= 100 else "ill-conditioned"
        near_ok &= row["status"] == expected_status
        near_ok &= abs(row["det_j"] - np.sin(angle) ** 2) < limit
        if expected_status != "valid":
            near_ok &= row["observer_det_error"] is None
        else:
            near_ok &= row["observer_det_error"] is not None and row["observer_det_error"] < limit
    max_error = max(r["max_residual"] for r in derived)
    min_positive = min(min(r["euclidean_min_eigenvalue"], r["observer_norm"]) for r in rows)
    values = {
        "coverage": (complete, len(rows)),
        "identities": (max_error < limit, max_error),
        "positive-observer": (min_positive > 0, min_positive),
        "tetrahedral": (gram_error < limit, gram_error),
        "weight-control": (controls["correct_weight_error"] < limit and controls["omitted_weight_error"] > config["analysis"]["min_negative_error"] and abs(controls["omitted_weight_error"] - (1 - np.exp(-1))) < limit, controls["omitted_weight_error"]),
        "singular-domain": (bool(near_ok), len(near)),
    }
    target = output / "derived"
    target.mkdir(parents=True, exist_ok=True)
    with (target / "residuals.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(derived[0]))
        writer.writeheader()
        writer.writerows(derived)
    write_json(target / "controls.json", controls)
    write_json(target / "conditioning.json", near)
    checks = {"schema_version": "research-checks-v1", "checks": [
        {"id": key, "status": "pass" if passed else "fail", "value": value,
         "evidence": "derived/conditioning.json" if key == "singular-domain" else "derived/controls.json" if key in {"tetrahedral", "weight-control"} else "derived/residuals.csv"}
        for key, (passed, value) in values.items()]}
    summary = {"samples": len(rows), "max_residual": max_error, "minimum_positive_value": min_positive,
               "gram_error": gram_error, "omitted_weight_error": controls["omitted_weight_error"],
               "near_control_count": len(near), "threshold": limit, "physical_evolution": False}
    write_json(output / "checks.json", checks)
    write_json(target / "summary.json", summary)
    return {"raw_source": paths[-1].relative_to(run_path).as_posix(), "checks": checks, "summary": summary}
