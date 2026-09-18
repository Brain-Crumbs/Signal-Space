from __future__ import annotations

import csv
import html
import json
from pathlib import Path
from typing import Any

from signal_space.runtime.io import write_json


def render_report(
    run_path: Path,
    report_path: Path,
    manifest: dict[str, Any],
    analysis: dict[str, Any],
    render_provenance: dict[str, Any],
) -> dict[str, Any]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    analysis_path = run_path / analysis["path"]
    with (analysis_path / "derived/series.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    steps = [int(row["step"]) for row in rows]
    observed = [float(row["observed"]) for row in rows]
    expected = [float(row["expected"]) for row in rows]
    errors = [float(row["absolute_error"]) for row in rows]

    figures = report_path / "figures"
    plot_data = report_path / "plot-data"
    figures.mkdir(parents=True, exist_ok=True)
    plot_data.mkdir(parents=True, exist_ok=True)
    plot_csv = plot_data / "recurrence.csv"
    with plot_csv.open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["step", "observed", "expected", "absolute_error", "step_unit", "value_unit"])
        for values in zip(steps, observed, expected, errors, strict=True):
            writer.writerow([*values, "index", "dimensionless"])
    write_json(plot_data / "recurrence.json", {"step": steps, "observed": observed, "expected": expected, "absolute_error": errors})
    figure_spec = {
        "schema_version": "research-figure-spec-v1",
        "id": "fixture-recurrence",
        "source_datasets": [str(plot_csv.relative_to(report_path))],
        "transformations": [],
        "axes": {"x": {"label": "Step", "unit": "index"}, "y": {"label": "Value", "unit": "dimensionless"}},
        "ranges": "automatic",
        "normalization": "none",
        "downsampling": "none",
        "fit_window": None,
        "renderer": f"matplotlib-{matplotlib.__version__}",
    }
    write_json(figures / "recurrence.figure.json", figure_spec)
    figure, axis = plt.subplots(figsize=(8, 4.5), constrained_layout=True)
    axis.plot(steps, observed, label="saved output", linewidth=2)
    axis.plot(steps, expected, "--", label="independent recurrence", linewidth=1.5)
    axis.set(xlabel="Step (index)", ylabel="Value (dimensionless)", title="Synthetic recurrence fixture")
    axis.grid(True, alpha=0.25)
    axis.legend()
    for extension in ("png", "svg", "pdf"):
        figure.savefig(figures / f"recurrence.{extension}", dpi=160 if extension == "png" else None)
    plt.close(figure)

    checks = json.loads((analysis_path / "checks.json").read_text())
    failed = [entry["id"] for entry in checks["checks"] if entry["status"] != "pass"]
    solver_provenance = manifest["code_identity"]
    analysis_provenance = analysis["code_identity"]
    reporting_provenance = render_provenance["code_identity"]
    title = json.loads((run_path / "resolved-config.json").read_text())["report"]["title"]
    markdown = f"""# {title}

## Outcome

- Technical state: `{manifest['technical_state']}`
- Scientific classification: `{analysis['classification']}`
- Synthetic fixture only; this report makes no physics claim.

## Assumptions

The saved sequence is dimensionless and follows the declared fixture recurrence. The fixture is an infrastructure control, not a physical model.

## Methods and equation

The bounded worker evaluated $x_{{n+1}} = g x_n + f$. Analysis independently regenerated the recurrence from the resolved configuration and compared it to immutable raw CSV output.

## Controls and acceptance

Checks: `{', '.join(entry['id'] for entry in checks['checks'])}`. Failed checks: `{', '.join(failed) if failed else 'none'}`.

![Observed and independently regenerated recurrence](figures/recurrence.svg)

## Convergence and error budget

This exact deterministic fixture has no discretization study. Its declared error budget is the configured absolute comparison threshold; the maximum measured residual is `{analysis['summary']['max_abs_error']:.6g}`.

## Failures

Incomplete and failed attempts remain in the manifest and event logs. This selected analysis found: `{', '.join(failed) if failed else 'no failed fixture checks'}`.

## Limitations

Passing E00 verifies lifecycle and traceability behavior only. It does not establish numerical reproducibility across all hardware, validate a physical action, or support a scientific inference.

## Exact provenance

- Run: `{manifest['run_id']}`
- Analysis: `{analysis['analysis_id']}`
- Configuration hash: `{manifest['config_hash']}`
- Solver revision: `{solver_provenance['revision']}`
- Solver dirty patch hash: `{solver_provenance['dirty_patch_hash']}`
- Analysis revision: `{analysis_provenance['revision']}`
- Analysis dirty patch hash: `{analysis_provenance['dirty_patch_hash']}`
- Reporting revision: `{reporting_provenance['revision']}`
- Reporting dirty patch hash: `{reporting_provenance['dirty_patch_hash']}`
- Reporting environment: `{render_provenance['execution_identity']['environment']['python']}` on `{render_provenance['execution_identity']['environment']['os']}`
- Raw input: `{analysis['raw_source']}`
- Figure specification: `figures/recurrence.figure.json`
- Plot data: `plot-data/recurrence.csv` and `plot-data/recurrence.json`
"""
    report_path.mkdir(parents=True, exist_ok=True)
    (report_path / "report.md").write_text(markdown)
    escaped = html.escape(markdown)
    body = f"<pre>{escaped}</pre><figure><img src=\"figures/recurrence.svg\" alt=\"Synthetic recurrence\"></figure>"
    (report_path / "report.html").write_text(f"<!doctype html><html><head><meta charset=\"utf-8\"><title>{html.escape(title)}</title></head><body>{body}</body></html>\n")

    with PdfPages(report_path / "report.pdf") as pdf:
        page = plt.figure(figsize=(8.5, 11))
        page.text(0.08, 0.95, title, fontsize=18, weight="bold", va="top")
        page.text(0.08, 0.90, "Synthetic E00 infrastructure fixture — no physics claim", fontsize=11, va="top")
        page.text(0.08, 0.84, r"Method: $x_{n+1}=g x_n+f$", fontsize=13, va="top")
        page.text(0.08, 0.78, f"Classification: {analysis['classification']}\nMax absolute residual: {analysis['summary']['max_abs_error']:.6g}\nRun: {manifest['run_id']}\nAnalysis: {analysis['analysis_id']}", fontsize=10, va="top")
        page.text(0.08, 0.58, "Limitations", fontsize=13, weight="bold")
        page.text(0.08, 0.54, "This tests lifecycle, integrity, replay, and reporting only.\nIt is not a physical solver or a scientific result.", fontsize=10, va="top")
        pdf.savefig(page)
        plt.close(page)
        figure, axis = plt.subplots(figsize=(8.5, 6))
        axis.plot(steps, observed, label="saved output", linewidth=2)
        axis.plot(steps, expected, "--", label="independent recurrence")
        axis.set(xlabel="Step (index)", ylabel="Value (dimensionless)", title="Saved-data regeneration")
        axis.grid(True, alpha=0.25)
        axis.legend()
        pdf.savefig(figure)
        plt.close(figure)
    return {"figure_spec": "figures/recurrence.figure.json", "plot_data": ["plot-data/recurrence.csv", "plot-data/recurrence.json"]}
