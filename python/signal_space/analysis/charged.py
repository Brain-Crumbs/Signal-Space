"""Independent saved-profile analysis. No solver is invoked by reanalysis."""

import csv
import itertools
from pathlib import Path
import numpy as np
from scipy.optimize import linear_sum_assignment
from signal_space.numerics.charged_radial import observables
from signal_space.runtime.io import read_json, write_json
from signal_space.experiments.charged import CRITERIA


def table(path, rows):
    if not rows:
        path.write_text("status\nno-data\n")
        return
    keys = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def spectral_comparison(base, refined):
    values = []
    for a, b in zip(base["sectors"], refined["sectors"], strict=True):
        av = np.array(a["sigma_real"]) + 1j * np.array(a["sigma_imag"])
        bv = np.array(b["sigma_real"]) + 1j * np.array(b["sigma_imag"])
        # Pair low modes one-to-one; include every mode with positive growth.
        indices = set(np.argsort(abs(av))[: min(16, len(av))].tolist())
        indices.update(np.flatnonzero(av.real > 1e-8).tolist())
        av = av[sorted(indices)]
        i, j = linear_sum_assignment(abs(av[:, None] - bv[None, :]))
        values.append(float(np.max(abs(av[i] - bv[j]))))
    return max(values, default=0.0)


def branch_segments(points):
    """Only parent-connected edges; never interpolate across a failed gap/fold."""
    by_file = {p["file"]: p for p in points}
    edges = []
    for p in points:
        parent = by_file.get(p.get("parent"))
        if (
            parent is not None
            and p["branch"] == parent["branch"]
            and p["lane"] == parent["lane"]
        ):
            a, b = parent["observables"], p["observables"]
            if abs(a["Q"] - b["Q"]) > 1e-8 * max(a["Q"], b["Q"]):
                edges.append((parent, p))
    return edges


def breakup_thresholds(points, all_points, samples, max_fragments):
    """Min-plus allocation on signed charge grid, all resolved connected edges.

    The grid search includes conjugate charges and free-charge remainder. The
    reported discretization budget bounds snapping each fragment using measured
    piecewise-linear slopes. No interpolation is performed across missing edges.
    """
    edges = branch_segments(all_points)
    if not edges:
        return [
            {
                "point": p["id"],
                "channel": "free-charge",
                "threshold": abs(p["observables"]["Q"]),
                "margin": abs(p["observables"]["Q"]) - p["observables"]["E"],
                "error": p["errors"]["E"] + p["errors"]["Q"],
            }
            for p in points
        ], False
    qmax = max(p["observables"]["Q"] for p in all_points)
    grid = np.linspace(-qmax, qmax, 2 * samples + 1)
    dq = qmax / samples
    energy = np.full(len(grid), np.inf)
    errors = np.zeros(len(grid))
    slopes = []
    allocation_covered = True
    fragment_error = max(p["errors"]["E"] + p["errors"]["Q"] for p in all_points)
    for a, b in edges:
        qa, qb = a["observables"]["Q"], b["observables"]["Q"]
        ea, eb = a["observables"]["E"], b["observables"]["E"]
        lo, hi = sorted((qa, qb))
        mask = (abs(grid) >= lo) & (abs(grid) <= hi)
        allocation_covered = allocation_covered and hi - lo >= 2 * dq
        slope = (eb - ea) / (qb - qa)
        slopes.append(abs(slope))
        trial = ea + slope * (abs(grid) - qa)
        best = mask & (trial < energy)
        energy[best] = trial[best]
        errors[best] = max(
            a.get("errors", {}).get("E", 0.0), b.get("errors", {}).get("E", 0.0)
        )
    # Include exact sampled branch charges as discrete two-body controls below.
    dp = energy.copy()
    dp_error = errors.copy()
    dp_grid = grid.copy()
    rows = []
    for count in range(1, max_fragments + 1):
        for point in points:
            o = point["observables"]
            cost = dp + abs(o["Q"] - dp_grid)
            if count == 1:
                continue  # No positive gap exists against arbitrarily soft emission.
            idx = int(np.argmin(cost))
            if np.isfinite(cost[idx]):
                interpolation_error = count * dq * (1 + max(slopes, default=1.0))
                rows.append(
                    {
                        "point": point["id"],
                        "channel": f"{count}-resolved-fragments-plus-free",
                        "threshold": float(cost[idx]),
                        "margin": float(cost[idx] - o["E"]),
                        "error": float(
                            count * fragment_error
                            + point["errors"]["E"]
                            + point["errors"]["Q"]
                            + interpolation_error
                        ),
                        "fragment_total_charge": float(dp_grid[idx]),
                        "free_charge": float(o["Q"] - dp_grid[idx]),
                        "allocation_spacing": float(dq),
                        "finite_emission_cutoff": 0.0,
                        "interpolation_error": float(interpolation_error),
                    }
                )
        if count == max_fragments:
            break
        next_dp = np.full(len(dp) + len(energy) - 1, np.inf)
        next_error = np.zeros_like(next_dp)
        for j in np.flatnonzero(np.isfinite(energy)):
            candidate = dp + energy[j]
            section = next_dp[j : j + len(dp)]
            better = candidate < section
            section[better] = candidate[better]
            next_error[j : j + len(dp)][better] = dp_error[better] + errors[j]
        dp, dp_error = next_dp, next_error
        dp_grid = np.arange(len(dp)) * dq - (count + 1) * qmax
    for point in points:
        o = point["observables"]
        rows.append(
            {
                "point": point["id"],
                "channel": "free-charge",
                "threshold": abs(o["Q"]),
                "margin": abs(o["Q"]) - o["E"],
                "error": point["errors"]["E"] + point["errors"]["Q"],
            }
        )
        for a, b in itertools.combinations_with_replacement(all_points, 2):
            qa, qb = a["observables"]["Q"], b["observables"]["Q"]
            # Exact two-soliton charges + free remainder; signed variants.
            for sign in (-1, 1):
                remainder = o["Q"] - qa - sign * qb
                threshold = (
                    a["observables"]["E"] + b["observables"]["E"] + abs(remainder)
                )
                if np.isfinite(threshold):
                    rows.append(
                        {
                            "point": point["id"],
                            "channel": "discrete-two-plus-free",
                            "threshold": threshold,
                            "margin": threshold - o["E"],
                            "error": point["errors"]["E"]
                            + point["errors"]["Q"]
                            + sum(x["errors"]["E"] + x["errors"]["Q"] for x in (a, b)),
                            "fragment_a": a["id"],
                            "fragment_b": b["id"],
                            "sign_b": sign,
                            "free_charge": remainder,
                        }
                    )
    return rows, allocation_covered and bool(np.any(np.isfinite(energy)))


def analyze(run_path, analysis_path, config):
    sources = sorted((run_path / "attempts").glob("*/raw/branch.json"))
    if not sources:
        raise ValueError("no E01 raw branch data")
    source = sources[-1]
    raw = source.parent
    state = read_json(source)
    p = config["parameters"]
    limits = config["analysis"]
    derived = analysis_path / "derived"
    derived.mkdir(parents=True, exist_ok=True)
    points = []
    failures = []
    all_rows = []
    datasets = {}
    for row in state["records"]:
        data = read_json(raw / row["file"])
        datasets[row["file"]] = data
        if row["status"] == "accepted":
            o = observables(data["profile"])
            item = {**row, "observables": o, "data": data}
            if row["kind"] in ("seed", "continue"):
                points.append(item)
            all_rows.append(
                {
                    "id": row["id"],
                    "branch": row["branch"],
                    "lane": row["lane"],
                    "kind": row["kind"],
                    "omega": row["omega"],
                    "status": row["status"],
                    **{k: v for k, v in o.items() if isinstance(v, (int, float))},
                }
            )
        else:
            failures.append(row)
            all_rows.append(
                {
                    k: row.get(k)
                    for k in ("id", "branch", "lane", "kind", "omega", "status")
                }
            )
    refinements = []
    for point in points:
        o = point["observables"]
        errors = {key: o["quadrature_error"][key] for key in ("E", "Q", "radius")}
        errors["E"] += o["tail_nonlinear_bound"] + abs(o["tail"]["E"])
        errors["Q"] += abs(o["tail"]["Q"])
        errors["radius"] += o["radius"] * o["tail_fraction"]
        comparisons = {}
        for row in state["records"]:
            if (
                row["parent"] == point["file"]
                and row["kind"] in ("spacing", "volume", "tolerance")
                and row["status"] == "accepted"
            ):
                ro = observables(datasets[row["file"]]["profile"])
                differences = {key: abs(o[key] - ro[key]) for key in errors}
                for key in errors:
                    errors[key] += differences[key]
                comparisons[row["kind"]] = max(
                    differences[key] / max(abs(o[key]), 1e-30) for key in errors
                )
                refinements.append(
                    {
                        "point": point["id"],
                        "axis": row["kind"],
                        **differences,
                        "max_relative": comparisons[row["kind"]],
                    }
                )
        point["errors"] = errors
        point["comparisons"] = comparisons
    # Parent-connected frequency interpolation errors, explicitly refined lane.
    fine = [x for x in points if x["lane"] == "half-step"]
    base = [x for x in points if x["lane"] == "base"]
    derivative_rows = []
    for point in base:
        same = [x for x in base if x["branch"] == point["branch"]]
        near = sorted(same, key=lambda x: abs(x["omega"] - point["omega"]))[:3]
        fine_near = sorted(
            [x for x in fine if x["branch"] == point["branch"]],
            key=lambda x: abs(x["omega"] - point["omega"]),
        )[:3]
        derivative = {
            "point": point["id"],
            "status": "unresolved",
            "relative_error": None,
            "step_error": None,
            "charge_condition": None,
            "charge_turning_point": False,
        }
        estimates = []
        for group in (near, fine_near):
            if len(group) < 3:
                continue
            group = sorted(group, key=lambda x: x["omega"])
            # Require both sides (endpoints deliberately remain unresolved).
            if not group[0]["omega"] < point["omega"] < group[-1]["omega"]:
                continue
            xs = np.array([x["omega"] - point["omega"] for x in group])
            es = np.array([x["observables"]["E"] for x in group])
            qs = np.array([x["observables"]["Q"] for x in group])
            de = np.polynomial.polynomial.polyfit(xs, es, 2)[1]
            dq = np.polynomial.polynomial.polyfit(xs, qs, 2)[1]
            condition = abs(dq) * (xs[-1] - xs[0]) / max(abs(qs))
            derivative["charge_turning_point"] = bool(
                (qs[1] - qs[0]) * (qs[2] - qs[1]) <= 0
            )
            if condition <= 1e-5 or derivative["charge_turning_point"]:
                continue
            estimates.append(float(de / dq))
            derivative["charge_condition"] = float(condition)
        if len(estimates) == 2:
            derivative["relative_error"] = (
                abs(estimates[-1] - point["omega"]) / point["omega"]
            )
            derivative["step_error"] = (
                abs(estimates[-1] - estimates[0]) / point["omega"]
            )
            derivative["status"] = (
                "pass"
                if max(derivative["relative_error"], derivative["step_error"])
                < limits["derivative_error"]
                else "unresolved"
            )
        point["derivative"] = derivative
        derivative_rows.append(derivative)
    # Interpolation uncertainty measured from actual half-step interior points.
    interpolation_rows = []
    for a, b in branch_segments(base):
        interior = [
            x
            for x in fine
            if x["branch"] == a["branch"]
            and min(a["omega"], b["omega"]) < x["omega"] < max(a["omega"], b["omega"])
        ]
        for middle in interior:
            frac = (middle["observables"]["Q"] - a["observables"]["Q"]) / (
                b["observables"]["Q"] - a["observables"]["Q"]
            )
            if not 0 <= frac <= 1:
                continue
            err = abs(
                middle["observables"]["E"]
                - ((1 - frac) * a["observables"]["E"] + frac * b["observables"]["E"])
            )
            a["errors"]["E"] += err
            b["errors"]["E"] += err
            interpolation_rows.append(
                {
                    "left": a["id"],
                    "right": b["id"],
                    "probe": middle["id"],
                    "energy_error": err,
                }
            )

    def stationary(point):
        o = point["observables"]
        return (
            o["field_residual"] < limits["field_residual"]
            and o["virial_defect"] < limits["virial_defect"]
            and o["energy_identity_defect"] < limits["virial_defect"]
            and o["tail_fit"] < limits["field_residual"]
        )

    def converged(point):
        return (
            set(point["comparisons"]) == {"spacing", "volume", "tolerance"}
            and max(point["comparisons"].values(), default=1)
            < limits["refinement_relative"]
        )

    resolved = [x for x in base if stationary(x) and converged(x)]
    # Unresolved points may still appear in raw tables but never define a
    # trusted breakup threshold or a negative scientific verdict.
    breakup, threshold_coverage = breakup_thresholds(
        base, resolved, p["breakup_samples"], p["max_fragments"]
    )
    refined_breakup, refined_coverage = breakup_thresholds(
        base, resolved, 2 * p["breakup_samples"], p["max_fragments"]
    )
    allocation_rows = []
    for row in refined_breakup:
        if "allocation_spacing" not in row:
            continue
        coarse = next(
            (
                x
                for x in breakup
                if x["point"] == row["point"] and x["channel"] == row["channel"]
            ),
            None,
        )
        if coarse:
            error = abs(row["threshold"] - coarse["threshold"])
            row["error"] += error
            allocation_rows.append(
                {
                    "point": row["point"],
                    "channel": row["channel"],
                    "threshold_step_error": error,
                    "coarse_spacing": coarse["allocation_spacing"],
                    "fine_spacing": row["allocation_spacing"],
                }
            )
    breakup = refined_breakup
    measured_edges = {(r["left"], r["right"]) for r in interpolation_rows}
    interpolation_covered = all(
        (a["id"], b["id"]) in measured_edges for a, b in branch_segments(resolved)
    )
    threshold_coverage = (
        threshold_coverage and refined_coverage and interpolation_covered
    )

    budgets = []
    selections = []
    spectral_rows = []
    for point in base:
        o = point["observables"]
        data = point["data"]
        spec = data.get("spectrum")
        spectral_ok = False
        numerical_spectrum = False
        angular = False
        growth = None
        spec_error = None
        partners = {
            row["kind"]: datasets[row["file"]].get("spectrum")
            for row in state["records"]
            if row["parent"] == point["file"]
            and row["status"] == "accepted"
            and row["kind"] in ("spectral", "volume")
        }
        if spec:
            growth = max(s["max_growth"] for s in spec["sectors"])
            if partners.get("spectral") and partners.get("volume"):
                spec_error = max(
                    spectral_comparison(spec, partners["spectral"]),
                    spectral_comparison(spec, partners["volume"]),
                )
                spectral_ok = all(
                    s["max_residual"] < limits["eigenpair_residual"]
                    and s["max_charge_defect"] < limits["eigenpair_residual"]
                    for v in (spec, *partners.values())
                    for s in v["sectors"]
                )
                numerical_spectrum = spectral_ok
                spectral_ok = (
                    spectral_ok
                    and spec_error < limits["refinement_relative"]
                    and growth <= 3 * max(spec_error, 1e-12)
                )
                spectral_ok = (
                    spectral_ok
                    and max(
                        v["background_relative_error"]
                        for v in (spec, *partners.values())
                    )
                    < limits["refinement_relative"]
                )
                spectral_ok = spectral_ok and all(
                    s["symmetry_splitting"] is None
                    or s["symmetry_splitting"] <= 3 * max(spec_error, 1e-12)
                    for s in spec["sectors"]
                )
            angular = spec["higher_sectors_bounded"] and all(
                v["higher_sectors_bounded"] for v in partners.values() if v
            )
            if partners.get("volume"):
                angular = angular and min(
                    spec["higher_sector_lower_bound"],
                    partners["volume"]["higher_sector_lower_bound"],
                ) > 3 * abs(
                    spec["higher_sector_lower_bound"]
                    - partners["volume"]["higher_sector_lower_bound"]
                )
            for s in spec["sectors"]:
                for index, (real, imag, residual, charge) in enumerate(
                    zip(
                        s["sigma_real"],
                        s["sigma_imag"],
                        s["residuals"],
                        s["charge_defects"],
                        strict=True,
                    )
                ):
                    spectral_rows.append(
                        {
                            "point": point["id"],
                            "ell": s["ell"],
                            "mode": index,
                            "sigma_real": real,
                            "sigma_imag": imag,
                            "residual": residual,
                            "charge_defect": charge,
                            "symmetry_mode": (
                                s["symmetry_name"]
                                if index == s["symmetry_mode_index"]
                                else ""
                            ),
                            "symmetry_overlap": (
                                s["symmetry_overlap"]
                                if index == s["symmetry_mode_index"]
                                else ""
                            ),
                            "eigenvectors": str(
                                (raw / s["eigenvectors_file"]).relative_to(run_path)
                            ),
                        }
                    )
        channels = [x for x in breakup if x["point"] == point["id"]]
        binding = (
            bool(channels)
            and threshold_coverage
            and bool(interpolation_rows)
            and point["derivative"]["status"] == "pass"
            and (1 - point["omega"])
            > 3
            * point["omega"]
            * max(
                point["derivative"]["relative_error"], point["derivative"]["step_error"]
            )
            and all(
                x["margin"] > limits["binding_error_multiplier"] * x["error"]
                for x in channels
            )
        )
        checks = {
            "stationary": stationary(point),
            "continuation": point["derivative"]["status"] == "pass",
            "convergence": converged(point),
            "spectrum": spectral_ok,
            "angular": angular,
            "binding": binding,
        }
        # Missing numerical evidence is unresolved, never proof of no candidate.
        definite_failure = (
            stationary(point)
            and converged(point)
            and (
                any(x["margin"] < -3 * x["error"] for x in channels)
                or (
                    spec_error is not None
                    and growth > 3 * max(spec_error, 1e-12)
                    and numerical_spectrum
                )
            )
        )
        selections.append(
            {
                "point": point["id"],
                "branch": point["branch"],
                "omega": point["omega"],
                "status": (
                    "candidate"
                    if all(checks.values())
                    else "no-candidate" if definite_failure else "unresolved"
                ),
                "criteria": {
                    key: {
                        "status": (
                            "pass"
                            if value
                            else (
                                "fail"
                                if definite_failure
                                and (
                                    (
                                        key == "binding"
                                        and any(
                                            x["margin"] < -3 * x["error"]
                                            for x in channels
                                        )
                                    )
                                    or (
                                        key == "spectrum"
                                        and numerical_spectrum
                                        and spec_error is not None
                                        and growth > 3 * max(spec_error, 1e-12)
                                    )
                                )
                                else "unresolved"
                            )
                        ),
                        "evidence": {
                            "stationary": "branch.csv",
                            "continuation": "derivatives.csv",
                            "convergence": "convergence.csv",
                            "spectrum": "spectra.csv",
                            "angular": "spectral-budgets.json",
                            "binding": "breakup.csv",
                        }[key],
                    }
                    for key, value in checks.items()
                },
            }
        )
        budgets.append(
            {
                "point": point["id"],
                "errors": point["errors"],
                "spectral_error": spec_error,
                "growth": growth,
                "background_error": (
                    spec.get("background_relative_error") if spec else None
                ),
                "higher_sector_lower_bound": (
                    spec["higher_sector_lower_bound"] if spec else None
                ),
                "angular_covered": angular,
            }
        )
    coverage = not state["queue"] and not any(
        r.get("endpoint_unresolved")
        or (r["kind"] == "seed" and r["status"] not in ("accepted", "duplicate-seed"))
        for r in state["records"]
    )
    for branch in {x["branch"] for x in base}:
        frequencies = [x["omega"] for x in base if x["branch"] == branch]
        coverage = (
            coverage
            and min(frequencies) <= p["omega_start"] + 1e-12
            and max(frequencies) >= p["omega_end"] - 1e-12
        )
    candidates = [x["point"] for x in selections if x["status"] == "candidate"]
    outcome = (
        "candidate"
        if candidates and coverage and p["research_run"]
        else (
            "no-candidate"
            if selections
            and coverage
            and all(x["status"] == "no-candidate" for x in selections)
            and p["research_run"]
            else "unresolved"
        )
    )
    files = {
        "branch.csv": all_rows,
        "convergence.csv": refinements,
        "derivatives.csv": derivative_rows,
        "interpolation.csv": interpolation_rows,
        "allocation-convergence.csv": allocation_rows,
        "breakup.csv": breakup,
        "spectra.csv": spectral_rows,
    }
    for name, rows in files.items():
        table(derived / name, rows)
    write_json(derived / "spectral-budgets.json", budgets)
    write_json(
        derived / "failures.json", {"failures": failures, "pending": state["queue"]}
    )
    selection = {
        "outcome": outcome,
        "candidates": candidates if outcome == "candidate" else [],
        "points": selections,
        "coverage": coverage,
        "scope": {
            "max_fragments": p["max_fragments"],
            "charge_conjugates": True,
            "radiation": "free-charge remainder on two-or-more soliton channels; soft emission via dE/dQ<m (no asserted positive soft gap)",
            "frequency": [p["omega_start"], p["omega_end"]],
            "seeds": p["seed_radii"],
        },
        "limitations": [
            "Finite seed search does not prove all stationary branches exist in the catalog.",
            "No global minimum, nonlinear stability, topology or particle identity inferred.",
            "Spectral uncertainty is measured mesh/domain sensitivity, not a rigorous continuum enclosure.",
        ],
    }
    write_json(derived / "selection.json", selection)
    checks = {
        "outcome": outcome,
        "checks": [
            {
                "id": key,
                "status": (
                    ("pass" if coverage else "unresolved")
                    if key == "coverage"
                    else "pass" if outcome == "candidate" else "unresolved"
                ),
                "evidence": f"derived/selection.json",
                "description": description,
            }
            for key, description in CRITERIA.items()
        ],
    }
    write_json(analysis_path / "checks.json", checks)
    return {
        "raw_source": source.relative_to(run_path).as_posix(),
        "checks": checks,
        "summary": {
            "outcome": outcome,
            "candidates": selection["candidates"],
            "points": len(base),
            "failures": len(failures),
            "pending": len(state["queue"]),
            "coverage": coverage,
        },
    }
