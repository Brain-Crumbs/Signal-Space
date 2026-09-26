"""Declarative E01 views assembled from immutable analysis, never a solver."""
import csv
from signal_space.runtime.io import read_json, write_json


def write_exploration(plot, branch, selection, config):
    def rows(name):
        with (plot / name).open() as stream:
            values = list(csv.DictReader(stream))
        result = []
        for row in values:
            if row == {"status": "no-data"}:
                continue
            item = {}
            for key, value in row.items():
                if value == "":
                    item[key] = None
                else:
                    try:
                        item[key] = float(value)
                    except ValueError:
                        item[key] = value
            result.append(item)
        return result

    tables = {name: rows(f"{name}.csv") for name in (
        "branch", "profiles", "spectra", "convergence", "breakup", "derivatives"
    )}
    # Connect only explicit accepted parent edges, never frequency-sorted points.
    records = {row["file"]: row for row in branch["records"]}
    for row in tables["branch"]:
        raw = next(r for r in branch["records"] if r["id"] == row["id"])
        parent = records.get(raw.get("parent"))
        row["parent_id"] = parent["id"] if parent else None
    budgets = read_json(plot / "spectral-budgets.json")
    modes = {
        (budget["point"], mode["ell"], mode["mode"]): mode
        for budget in budgets
        for mode in (budget.get("spectral_assessment") or {}).get("modes", [])
    }
    for row in tables["spectra"]:
        mode = modes.get((row["point"], row["ell"], row["mode"]))
        row["numerical_error"] = mode["error"] if mode else None
        row["resolved_growth"] = mode["resolved_growth"] if mode else None
    views = []

    def view(id, title, dataset, x, y, xlabel, ylabel, unit_x, unit_y, **extra):
        views.append(dict(id=id, title=title, dataset=dataset, x=x, y=y,
                          x_label=xlabel, y_label=ylabel, x_unit=unit_x,
                          y_unit=unit_y, **extra))

    base = dict(filters={"status": "accepted", "lane": "base", "kind": ["seed", "continue"]},
                point_key="id", group="branch", parent_key="parent_id")
    view("energy", "Energy and charge", "branch", "Q", "E", "Q", "E", "dimensionless", "m", reference="identity", **base)
    view("charge", "Charge along the branch", "branch", "omega", "Q", "ω", "Q", "m", "dimensionless", **base)
    view("radius", "Object size", "branch", "omega", "radius", "ω", "Charge RMS radius", "m", "1/m", **base)
    for field, title, unit in [("f", "Radial amplitude", "m/√g"), ("fp", "Radial derivative", "m²/√g")]:
        view(field, title, "profiles", "r", field, "r", field, "1/m", unit, point_key="point", group="point", line=True)
    view("spectrum", "Charge-constrained spectrum", "spectra", "sigma_imag", "sigma_real", "Im σ", "Re σ", "m", "m", point_key="point", group="ell", error="numerical_error", error_multiplier=1)
    view("binding", "Tested binding margins", "breakup", "$index", "margin", "Channel index (inspect table for allocation)", "Threshold − E", "index", "m", point_key="point", group="channel", error="error", error_multiplier=3)
    view("convergence", "Independent refinements", "convergence", "$index", "max_relative", "Refinement index", "Maximum relative change", "index", "dimensionless", point_key="point", group="axis", threshold=config["analysis"]["refinement_relative"])
    write_json(plot / "exploration.json", {
        "schema_version": "research-exploration-v1", "tables": tables, "views": views,
        "selection": selection, "spectral_budgets": budgets,
        "failures": read_json(plot / "failures.json"),
        "sources": [f"plot-data/{name}.csv" for name in tables] + [
            "plot-data/selection.json", "plot-data/spectral-budgets.json", "plot-data/failures.json"],
        "normalization": "E and Q retain physical 1/lambda; lambda=0.01",
        "downsampling": "none", "renderer": "signal-space-svg-v1",
    })
