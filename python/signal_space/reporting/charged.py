"""E01 figures and paginated reports regenerated exclusively from saved data."""

import csv
import html
import json
import shutil
import textwrap
from signal_space.runtime.io import read_json, write_json


def render_report(run_path, report_path, manifest, analysis, render_provenance):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    derived = run_path / analysis["path"] / "derived"
    selection = read_json(derived / "selection.json")
    config = read_json(run_path / "resolved-config.json")
    raw_source = run_path / analysis["raw_source"]
    raw = raw_source.parent
    branch = read_json(raw_source)
    figures = report_path / "figures"
    figures.mkdir()
    plot = report_path / "plot-data"
    plot.mkdir()
    for path in derived.iterdir():
        shutil.copyfile(path, plot / path.name)
    profiles = []
    for row in branch["records"]:
        if (
            row["status"] == "accepted"
            and row["kind"] in ("seed", "continue")
            and row["lane"] == "base"
        ):
            profile = read_json(raw / row["file"])["profile"]
            profiles.extend(
                {"point": row["id"], "r": r, "f": f, "fp": fp}
                for r, f, fp in zip(
                    profile["r"], profile["f"], profile["fp"], strict=True
                )
            )
    from signal_space.analysis.charged import table

    table(plot / "profiles.csv", profiles)
    write_json(plot / "profiles.json", profiles)

    from signal_space.reporting.exploration import write_exploration

    write_exploration(plot, branch, selection, config)

    def rows(name):
        with (plot / name).open() as stream:
            return list(csv.DictReader(stream))

    accepted = [
        r
        for r in rows("branch.csv")
        if r.get("status") == "accepted"
        and r.get("kind") in ("seed", "continue")
        and r.get("lane") == "base"
    ]
    spectra = rows("spectra.csv")
    convergence = rows("convergence.csv")
    thresholds = rows("breakup.csv")
    plots = []

    def make(name, title, xlabel, ylabel, source):
        fig, ax = plt.subplots(figsize=(8, 4.8), layout="constrained")
        ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
        ax.grid(alpha=0.2)
        plots.append((name, fig, ax, source))
        return ax

    ax = make(
        "branch",
        "Computed branch (failures retained in branch table)",
        "Q (dimensionless; includes 1/lambda)",
        "E (m; includes 1/lambda)",
        "branch.csv",
    )
    for branch_id in sorted({r["branch"] for r in accepted}):
        group = sorted(
            [r for r in accepted if r["branch"] == branch_id],
            key=lambda r: float(r["omega"]),
        )
        ax.plot(
            [float(r["Q"]) for r in group],
            [float(r["E"]) for r in group],
            ".-",
            label=branch_id,
        )
    if accepted:
        q = [float(r["Q"]) for r in accepted]
        ax.plot(sorted(q), sorted(q), "--", label="free charge m|Q|")
        ax.legend()
    ax = make(
        "profiles",
        "Saved positive radial profiles",
        "r (1/m)",
        "f (m/sqrt(g))",
        "profiles.csv",
    )
    for point in sorted({r["point"] for r in profiles}):
        group = [r for r in profiles if r["point"] == point]
        ax.plot([r["r"] for r in group], [r["f"] for r in group], alpha=0.65)
    ax = make(
        "spectra",
        "Coupled charge-constrained spectrum",
        "Im sigma (m)",
        "Re sigma (m)",
        "spectra.csv",
    )
    for ell in sorted({r.get("ell") for r in spectra if r.get("ell") is not None}):
        group = [r for r in spectra if r.get("ell") == ell]
        ax.scatter(
            [float(r["sigma_imag"]) for r in group],
            [float(r["sigma_real"]) for r in group],
            s=8,
            label=f"ell={ell}",
            alpha=0.6,
        )
    if spectra and "ell" in spectra[0]:
        ax.legend()
    ax = make(
        "convergence",
        "Independent refinement differences",
        "Comparison index",
        "max relative change (E,Q,radius)",
        "convergence.csv",
    )
    values = [float(r["max_relative"]) for r in convergence if r.get("max_relative")]
    if values:
        ax.semilogy(range(len(values)), values, ".")
    ax.axhline(config["analysis"]["refinement_relative"], linestyle="--", color="black")
    ax = make(
        "thresholds",
        "Binding margins and combined numerical error",
        "Computed channel index",
        "Threshold - E (m)",
        "breakup.csv",
    )
    valid = [r for r in thresholds if r.get("margin")]
    if valid:
        ax.errorbar(
            range(len(valid)),
            [float(r["margin"]) for r in valid],
            yerr=[3 * float(r["error"]) for r in valid],
            fmt=".",
            capsize=1,
        )
    ax.axhline(0, color="black", linewidth=0.8)
    title = config["report"]["title"]
    paragraphs = [
        (
            "Outcome",
            f"{selection['outcome']}. Technical state: {manifest['technical_state']}. Candidate IDs: {', '.join(selection['candidates']) or 'none'}.",
        ),
        (
            "Assumptions and action",
            "c=hbar=m=g=h=1; lambda=0.01; epsilon=0.1. Neutral a=0 exactly. eta=1, lambda_4=0.01, zeta=0.1. E and Q include 1/lambda. Source: charged-recurrence-winding-hopf.md sections 2–10, 14–15 and 23.",
        ),
        (
            "Methods",
            "Singular-origin collocation with f prime(0)=0 and spherical Robin tail. Adaptive frequency continuation retains rejected seeds and failed endpoints. Saved-field finite differences and Simpson/trapezoid quadrature independently test the residual and observables. Virial and energy identities share quadrature and are not independent evidence. The spectral grid separately solves the stationary action with Dirichlet exterior; its background error is saved. Full coupled exp(sigma*t) spectra use w=rU,z=rV and the first-order charge null space. Original-equation eigenpair residuals expose projection leakage. No conclusion follows from L+ or dQ/domega alone.",
        ),
        (
            "Controls and convergence",
            "Origin, tail, vacuum and free-spectrum controls are tested in CI. Research configurations request independent mesh, volume, tolerance, frequency-step and spectral-basis refinements. Their differences, quadrature, tail and interpolation errors form numerical budgets; these are not statistical error bars. See convergence.csv, derivatives.csv and spectral-budgets.json. Missing comparisons remain unresolved.",
        ),
        ("Threshold scope", json.dumps(selection["scope"], sort_keys=True)),
        (
            "Failures and coverage",
            f"{analysis['summary']['failures']} rejected/failed records; {analysis['summary']['pending']} pending tasks. Coverage: {selection['coverage']}. Full details and pending continuation state are retained in failures.json. A finite seed search cannot prove exhaustive branch discovery. Endpoints and ill-conditioned derivatives are unresolved.",
        ),
        (
            "Classification and limitations",
            "Stationary, below tested thresholds, and linearly stable within tested sectors are distinct checks in selection.json. A candidate requires all checks and completed declared coverage. No global minimum, nonlinear stability, damping, Hopf binding, fermion or particle identity is inferred. Small fixtures always remain scientifically unresolved.",
        ),
        (
            "Provenance",
            f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; config hash {manifest['config_hash']}. Solver {json.dumps(manifest['code_identity'],sort_keys=True)}. Analysis {json.dumps(analysis['code_identity'],sort_keys=True)}. Renderer {json.dumps(render_provenance,sort_keys=True)}. Raw source {analysis['raw_source']}. Figures are regenerated from saved data without invoking a solver.",
        ),
    ]
    markdown = f"# {title}\n\n" + "\n\n".join(
        f"## {head}\n\n{body}" for head, body in paragraphs
    )
    markdown += "\n\n## Criterion evidence\n\n| Point | Status | Criteria |\n| --- | --- | --- |\n"
    for point in selection["points"]:
        criteria = ", ".join(
            f'{key}: {value["status"]}' for key, value in point["criteria"].items()
        )
        markdown += f'| {point["point"]} | {point["status"]} | {criteria} |\n'
    for name, fig, ax, source in plots:
        write_json(
            figures / f"{name}.figure.json",
            {
                "schema_version": "research-figure-spec-v1",
                "id": f"e01-{name}",
                "source_datasets": [f"plot-data/{source}"],
                "transformations": [
                    "select declared columns and accepted base branch points; see renderer"
                ],
                "axes": {
                    "x": {"label": ax.get_xlabel(), "unit": "declared in label"},
                    "y": {"label": ax.get_ylabel(), "unit": "declared in label"},
                },
                "ranges": "automatic",
                "normalization": "physical 1/lambda in E,Q",
                "downsampling": "none",
                "fit_window": None,
                "renderer": f"matplotlib-{matplotlib.__version__}",
            },
        )
        for ext in ("png", "svg", "pdf"):
            fig.savefig(figures / f"{name}.{ext}", dpi=160)
        markdown += f"\n![{ax.get_title()}](figures/{name}.svg)\n"
    (report_path / "report.md").write_text(markdown)
    (report_path / "report.html").write_text(
        '<!doctype html><html><head><meta charset="utf-8"><title>'
        + html.escape(title)
        + "</title><style>body{max-width:1000px;margin:3rem auto;font-family:system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere}img{max-width:100%}</style></head><body><pre>"
        + html.escape(markdown)
        + "</pre>"
        + "".join(
            f'<img src="figures/{name}.svg" alt="{html.escape(ax.get_title())}">'
            for name, _, ax, _ in plots
        )
        + "</body></html>"
    )
    with PdfPages(report_path / "report.pdf") as pdf:
        # Fixed line budget prevents long provenance or failures clipping pages.
        lines = []
        for head, body in [(title, "")] + paragraphs:
            lines.extend(textwrap.wrap(head, 85))
            lines.append("")
            lines.extend(textwrap.wrap(body, 95))
            lines.extend(["", ""])
        for start in range(0, len(lines), 49):
            page = plt.figure(figsize=(8.5, 11))
            page.text(
                0.07,
                0.95,
                "\n".join(lines[start : start + 49]),
                fontsize=9.5,
                linespacing=1.4,
                va="top",
                family="monospace",
            )
            pdf.savefig(page)
            plt.close(page)
        for _, fig, _, _ in plots:
            pdf.savefig(fig)
    for _, fig, _, _ in plots:
        plt.close(fig)
    return {
        "required_inputs": [
            analysis["raw_source"],
            *[
                str((raw / row["file"]).relative_to(run_path))
                for row in branch["records"]
                if row["status"] == "accepted"
                and row["kind"] in ("seed", "continue")
                and row["lane"] == "base"
            ],
            f"{analysis['path']}/checks.json",
            *[f"{analysis['path']}/derived/{p.name}" for p in derived.iterdir()],
        ],
        "figure_specs": [f"figures/{name}.figure.json" for name, _, _, _ in plots],
        "plot_data": [f"plot-data/{p.name}" for p in plot.iterdir()],
    }
