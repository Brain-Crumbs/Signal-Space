#!/usr/bin/env python3
"""Build a reader export from one verified saved run/analysis/report, without rerunning physics."""

from __future__ import annotations

import argparse
import json
import shutil
import textwrap
from pathlib import Path

from experiment_contract import digest, validate_bundle, validate_plan


def copy(source: Path, target: Path) -> None:
    if not source.is_file() or source.is_symlink():
        raise ValueError(f"missing or unsafe source {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def text_pages(pdf, title: str, content: str) -> None:
    import matplotlib.pyplot as plt

    lines = []
    for line in content.splitlines():
        lines.extend(textwrap.wrap(line, width=105, replace_whitespace=False) or [""])
    # Keep the last line well above the letter-page bottom at 8.2 pt and 1.35 spacing.
    for start in range(0, max(1, len(lines)), 40):
        page = plt.figure(figsize=(8.5, 11))
        page.text(0.07, 0.96, title, fontsize=14, weight="bold", va="top")
        page.text(0.07, 0.91, "\n".join(lines[start : start + 40]), fontsize=8.2, va="top", family="monospace", linespacing=1.35)
        pdf.savefig(page)
        plt.close(page)


def figure_page(pdf, png: Path, interpretation: dict[str, str]) -> None:
    import matplotlib.image as mpimg
    import matplotlib.pyplot as plt

    page = plt.figure(figsize=(8.5, 11))
    axis = page.add_axes((0.07, 0.38, 0.86, 0.56))
    axis.imshow(mpimg.imread(png))
    axis.axis("off")
    lines = []
    for heading in ("question", "reading", "significance", "limitation"):
        lines.extend(textwrap.wrap(f"{heading.title()}: {interpretation[heading]}", width=105))
        lines.append("")
    if len(lines) > 23:
        raise ValueError(f"interpretation too long for one figure page: {png.name}")
    page.text(0.07, 0.35, "\n".join(lines), fontsize=8.5, va="top", linespacing=1.28)
    pdf.savefig(page)
    plt.close(page)


def setup_summary(plan: dict) -> str:
    lines = [
        plan["question"], "",
        f"Experiment: {plan['experiment_id']}    Model: {plan['model_id']}",
        f"Runtime configuration: {plan['runtime_config']}",
        f"Plan lock: {plan['locked_sha256']}", "",
        "MODEL AND NUMERICAL SETUP",
        *[f"{key.replace('_', ' ').title()}: {value}" for key, value in plan["method"].items()],
        "", "COMPETING PREDICTIONS",
        *[f"{row['id']}: {row['prediction']}" for row in plan["hypotheses"]],
        "", "CONTROLS",
        *[f"{row['id']}: {row['purpose']}; method: {row['method']}" for row in plan["controls"]],
        "", "PREREGISTERED DECISIONS",
    ]
    for row in plan["criteria"]:
        lines.extend([f"{row['id']} ({row['observable']})", f"Pass: {row['pass_if']}",
                      f"Fail: {row['fail_if']}", f"Unresolved: {row['unresolved_if']}",
                      f"Uncertainty: {row['uncertainty']}", ""])
    lines.append("VISUAL QUESTIONS")
    for row in plan["visualization_plan"]:
        lines.extend([f"{row['figure_id']} [{row['role']}]: {row['question']}",
                      f"View: {row['representation']}; observables: {', '.join(row['observables'])}",
                      *[f"{key}: {value}" for key, value in row["competing_signatures"].items()],
                      f"Controls: {', '.join(row['controls']) or 'none'}; uncertainty: {row['uncertainty']}",
                      f"Data: {', '.join(row['source_data'])}; transforms: {', '.join(row['transformations']) or 'none'}", ""])
    lines.extend(["RESOURCE LIMITS", json.dumps(plan["resources"], sort_keys=True)])
    if plan.get("prohibited_inferences"):
        lines.extend(["", "PROHIBITED INFERENCES", *plan["prohibited_inferences"]])
    return "\n".join(lines)


def package(run: Path, plan_file: Path, interpretations_file: Path, mentor_file: Path, destination: Path, source_dir: Path | None, source_locator: str | None = None) -> None:
    if destination.exists():
        raise ValueError("destination exists; exports are immutable, choose a new path")
    plan = json.loads(plan_file.read_text(encoding="utf-8"))
    validate_plan(plan)
    manifest_path = run / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (manifest["experiment_id"], manifest["model_id"]) != (plan["experiment_id"], plan["model_id"]):
        raise ValueError("run does not match plan")
    if not manifest.get("completeness", {}).get("report"):
        raise ValueError("source report incomplete; verify the run first")
    if not (run / "checksums.sha256").is_file():
        raise ValueError("source run lacks checksum ledger")
    analysis = manifest["analyses"][-1]
    report = next((item for item in reversed(manifest["reports"]) if item["analysis_id"] == analysis["analysis_id"]), None)
    if report is None:
        raise ValueError("no report for latest analysis")
    figures = {v["figure_id"]: v for v in plan["visualization_plan"]}
    interpretations = json.loads(interpretations_file.read_text(encoding="utf-8"))
    report_dir = run / report["path"]
    specs = {json.loads(p.read_text())["id"]: p for p in (report_dir / "figures").glob("*.figure.json")}
    if set(specs) - set(figures):
        raise ValueError(f"unplanned report figures: {sorted(set(specs) - set(figures))}")
    if any(item["required"] and key not in specs for key, item in figures.items()):
        raise ValueError("a required planned figure has no saved report spec")
    if not specs:
        raise ValueError("no saved figure specifications")
    for key in specs:
        if key not in interpretations or any(not interpretations[key].get(field) for field in ("question", "reading", "significance", "limitation")):
            raise ValueError(f"missing four-part interpretation for {key}")
        if interpretations[key]["question"] != figures[key]["question"]:
            raise ValueError(f"interpretation question differs from locked plan: {key}")
    destination.mkdir(parents=True)
    try:
        copy(plan_file, destination / "plan.json")
        copy(mentor_file, destination / "Experiment_Analysis_and_Next.md")
        for attempt in manifest["attempts"]:
            raw = run / attempt["path"] / "raw"
            if raw.exists():
                for p in raw.rglob("*"):
                    if p.is_file():
                        copy(p, destination / "results/data/raw" / attempt["attempt_id"] / p.relative_to(raw))
        derived = run / analysis["path"] / "derived"
        if derived.exists():
            for p in derived.rglob("*"):
                if p.is_file():
                    copy(p, destination / "results/data/derived" / p.relative_to(derived))
        copy(run / analysis["path"] / "analysis.json", destination / "results/tables/analysis.json")
        copy(run / analysis["path"] / "checks.json", destination / "results/tables/checks.json")
        copy(run / "resolved-config.json", destination / "results/tables/resolved-config.json")
        if source_dir:
            for p in source_dir.rglob("*.py"):
                if p.is_file():
                    copy(p, destination / "results/source" / p.relative_to(source_dir))
        plot_dir = report_dir / "plot-data"
        for p in plot_dir.rglob("*"):
            if p.is_file():
                copy(p, destination / "results/data/plot-data" / p.relative_to(plot_dir))
        index = []
        for key, spec_path in specs.items():
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
            spec_out = f"results/figure-specs/{spec_path.name}"
            copy(spec_path, destination / spec_out)
            stem = spec_path.name.removesuffix(".figure.json")
            files = []
            for extension in ("png", "svg", "pdf"):
                src = report_dir / "figures" / f"{stem}.{extension}"
                if src.is_file():
                    dst = f"figures/static/{src.name}"
                    copy(src, destination / dst)
                    files.append(dst)
            if not any(p.endswith(".png") for p in files):
                raise ValueError(f"no PNG to embed in results PDF for {key}")
            data = [f"results/data/{path}" for path in spec["source_datasets"]]
            if any(not (destination / path).is_file() for path in data):
                raise ValueError(f"figure {key} has missing exact plot data")
            index.append({"figure_id": key, "role": figures[key]["role"], "question": figures[key]["question"],
                          "reading": interpretations[key]["reading"], "significance": interpretations[key]["significance"],
                          "limitation": interpretations[key]["limitation"], "source_data": data,
                          "spec_file": spec_out, "transformations": spec["transformations"], "files": files})
        (destination / "figures/figure_index.json").write_text(json.dumps({"schema_version": "signal-space-figure-index-v1", "figures": index}, indent=2) + "\n")
        from matplotlib.backends.backend_pdf import PdfPages

        with PdfPages(destination / "Experimental_Setup.pdf") as pdf:
            text_pages(pdf, "Experimental Setup", setup_summary(plan))
        with PdfPages(destination / "Experiment_Results.pdf") as pdf:
            text_pages(pdf, "Experiment Results", (report_dir / "report.md").read_text(encoding="utf-8"))
            for item in index:
                png = next(path for path in item["files"] if path.endswith(".png"))
                figure_page(pdf, destination / png, {**item, "question": item["question"]})
        locator = source_locator or str(run.resolve())
        readme = f"# {plan['question']}\n\nModel: `{plan['model_id']}`. Run: `{manifest['run_id']}`. Analysis: `{analysis['analysis_id']}`. Report: `{report['report_id']}`. Scientific classification: `{manifest['scientific_classification']}`.\n\nCanonical source locator: `{locator}`. For an Actions download, the canonical package is also in the companion evidence artifact under `runs/<experiment-id>/<run-id>/`; a repository locator is the intended check-in destination. See `plan.json` for the locked protocol, `Experimental_Setup.pdf` for the setup, `Experiment_Results.pdf` for all saved figures and interpretations, `Experiment_Analysis_and_Next.md` for assessment, `results/` for data and code, and `figures/figure_index.json` for figure provenance.\n\nKnown gaps: {', '.join(manifest['known_gaps']) or 'none recorded'}.\n"
        (destination / "README.md").write_text(readme, encoding="utf-8")
        listing = [{"path": p.relative_to(destination).as_posix(), "sha256": digest(p.read_bytes())}
                   for p in sorted(destination.rglob("*")) if p.is_file()]
        export = {"schema_version": "signal-space-export-v1", "source_run": {
            "experiment_id": plan["experiment_id"], "model_id": plan["model_id"], "run_id": manifest["run_id"],
            "analysis_id": analysis["analysis_id"], "report_id": report["report_id"],
            "manifest_sha256": digest(manifest_path.read_bytes()), "locator": locator},
            "classification": manifest["scientific_classification"], "files": listing,
            "known_gaps": manifest["known_gaps"]}
        (destination / "export.json").write_text(json.dumps(export, indent=2) + "\n")
        validate_bundle(destination)
    except BaseException:
        shutil.rmtree(destination)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("run", "plan", "interpretations", "mentor", "output"):
        parser.add_argument(f"--{name}", required=True, type=Path)
    parser.add_argument("--source-dir", type=Path)
    parser.add_argument("--source-locator", help="portable canonical locator; defaults to the local absolute path")
    args = parser.parse_args()
    package(args.run, args.plan, args.interpretations, args.mentor, args.output, args.source_dir, args.source_locator)
    print(f"validated export: {args.output}")
