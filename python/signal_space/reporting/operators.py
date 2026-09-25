"""Question-driven Test 1 figures and reports from immutable analysis only."""

import csv
import html
import shutil
import textwrap

from signal_space.runtime.io import read_json, write_json

QUESTIONS = {
    "operator-residuals": "Do operator and observer identities remain accurate across the declared conditioning domain?",
    "tetrahedral-gram": "Do four null projector directions span the predicted Lorentzian operator space?",
    "observer-domain": "Do singular aggregates and omitted ray weights expose the intended failure controls?",
}


def render_report(run_path, report_path, manifest, analysis, render_provenance):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    import numpy as np

    derived = run_path / analysis["path"] / "derived"
    plots = report_path / "plot-data"
    figures = report_path / "figures"
    plots.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    for name in ("residuals.csv", "controls.json", "conditioning.json"):
        shutil.copy2(derived / name, plots / name)
    with (plots / "residuals.csv").open(newline="") as f:
        rows = [{k: float(v) for k, v in r.items()} for r in csv.DictReader(f)]
    controls = read_json(plots / "controls.json")
    near = read_json(plots / "conditioning.json")
    summary = analysis["summary"]
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    made = []
    specs = []

    def save(fig, key, sources, transforms, axes):
        spec = {"schema_version": "research-figure-spec-v1", "id": key,
                "source_datasets": [f"plot-data/{v}" for v in sources], "transformations": transforms,
                "axes": axes, "ranges": "automatic except declared log display floor",
                "normalization": "residuals divided by declared max(1, scale)",
                "downsampling": "none", "fit_window": None, "renderer": f"matplotlib-{matplotlib.__version__}"}
        write_json(figures / f"{key}.figure.json", spec)
        for ext in ("png", "svg", "pdf"):
            fig.savefig(figures / f"{key}.{ext}", dpi=160 if ext == "png" else None)
        made.append(fig)
        specs.append(f"figures/{key}.figure.json")

    fig, ax = plt.subplots(figsize=(9, 5.2), layout="constrained")
    ax.scatter([r["condition_j"] for r in rows], [max(1e-18, r["max_residual"]) for r in rows], s=12, alpha=0.5, label="maximum identity residual")
    ax.scatter([r["condition_j"] for r in rows], [max(1e-18, r["norm_transform_error"]) for r in rows], s=8, alpha=0.4, label="observer norm under frame change")
    ax.axhline(summary["threshold"], color="#b84040", linestyle="--", label="locked acceptance threshold")
    ax.set(xscale="log", yscale="log", xlabel="Aggregate condition number (dimensionless)", ylabel="Scale-normalized residual (dimensionless)", title=f"Test 1 | {summary['samples']} seeded observer comparisons")
    ax.set_ylim(5e-19, 1e-9)
    ax.grid(alpha=0.2)
    ax.legend(loc="upper left", fontsize=9)
    save(fig, "operator-residuals", ["residuals.csv"], ["display max(residual,1e-18) on log axis; raw zeros retained", "no fit or smoothing"], {"x": {"unit": "dimensionless"}, "y": {"unit": "dimensionless"}})

    fig, axes = plt.subplots(1, 2, figsize=(9, 4.8), layout="constrained")
    gram = np.array(controls["gram"])
    im = axes[0].imshow(gram, vmin=0, vmax=1 / 3, cmap="Blues")
    for i in range(4):
        for j in range(4):
            axes[0].text(j, i, "0" if i == j else "1/3", ha="center", va="center", color="black" if i == j else "white")
    axes[0].set(xticks=range(4), yticks=range(4), xlabel="Projector index", ylabel="Projector index", title="Null diagonals; nonzero overlaps")
    fig.colorbar(im, ax=axes[0], shrink=0.65, label="Determinant polarization")
    axes[1].bar(range(4), controls["gram_eigenvalues"], color=["#537eaa"] * 3 + ["#36a18b"], label="computed")
    axes[1].scatter(range(4), [-1 / 3] * 3 + [1], marker="_", s=250, color="black", label="exact prediction", zorder=4)
    axes[1].axhline(0, color="black", linewidth=0.7)
    axes[1].set(xticks=range(4), xlabel="Sorted eigenvalue index", ylabel="Eigenvalue (dimensionless)", title="One positive, three negative directions")
    axes[1].legend(fontsize=9)
    fig.suptitle("Test 1 | Algebraic signature, not a propagation measurement", fontsize=12)
    save(fig, "tetrahedral-gram", ["controls.json"], ["sorted eigenvalues compared with (-1/3,-1/3,-1/3,1)"], {"x": {"unit": "index"}, "y": {"unit": "dimensionless"}})

    fig, axes = plt.subplots(1, 2, figsize=(9, 4.8), layout="constrained")
    for status, marker, color in (("valid", "o", "#36a18b"), ("ill-conditioned", "x", "#b84040")):
        subset = [r for r in near if r["status"] == status]
        axes[0].scatter([r["angle"] for r in subset], [r["condition_j"] for r in subset], marker=marker, color=color, label=status)
    axes[0].axhline(100, linestyle="--", color="gray", label="acceptance-domain boundary")
    axes[0].set(xscale="log", yscale="log", xlabel="Constituent angle (radian)", ylabel="Aggregate condition number", title="Approaching a singular aggregate")
    axes[0].text(0.04, 0.96, "Angle = 0: no timelike observer\nExcluded explicitly; no regularization", transform=axes[0].transAxes, va="top", fontsize=8)
    axes[0].legend(loc="lower left", fontsize=8)
    axes[0].grid(alpha=0.2)
    errors = [controls["correct_weight_error"], controls["omitted_weight_error"]]
    axes[1].bar(["Correct weight", "Weight omitted"], [max(1e-18, e) for e in errors], color=["#36a18b", "#b84040"])
    axes[1].set(yscale="log", ylim=(1e-19, 10), ylabel="Relative weighted-ray reconstruction error", title="Same nonunitary frame change")
    axes[1].axhline(1e-10, linestyle="--", color="gray", label="identity threshold")
    axes[1].axhline(1e-3, linestyle=":", color="#b84040", label="negative-control detection threshold")
    axes[1].legend(fontsize=8, loc="upper left")
    fig.suptitle("Test 1 | Invalid domains and deliberately inconsistent transformations", fontsize=12)
    save(fig, "observer-domain", ["conditioning.json", "controls.json"], ["angle zero shown as annotation, not placed on log axis", "display max(error,1e-18); exact zero retained in data"], {"x": {"unit": "radian or category"}, "y": {"unit": "dimensionless"}})

    interpretations = {
        "operator-residuals": {"question": QUESTIONS["operator-residuals"],
            "reading": f"Maximum residual {summary['max_residual']:.3g}; compare all points with the locked 1e-10 line. Log plotting floors exact zeros at 1e-18.",
            "significance": "Tests consistent determinant, observer norm, positive form and weighted-ray transformations on saved inputs, with an independent component audit.",
            "limitation": "Finite moderate-conditioning samples; no propagation, clock or emergent metric is measured."},
        "tetrahedral-gram": {"question": QUESTIONS["tetrahedral-gram"],
            "reading": f"Each projector has a null diagonal. The sorted spectrum matches (-1/3,-1/3,-1/3,1) with maximum error {summary['gram_error']:.3g}.",
            "significance": "Four null projector directions can span the four-dimensional Hermitian operator space with Lorentzian signature.",
            "limitation": "This is internal algebra. The tetrahedron supplies neither physical spatial axes nor a dynamical spacetime."},
        "observer-domain": {"question": QUESTIONS["observer-domain"],
            "reading": f"Collinearity is rejected and ill-conditioned aggregates are marked separately. Omitting a boost-transformed weight gives error {summary['omitted_weight_error']:.6f}.",
            "significance": "The test distinguishes valid observer construction from a singular ray, and detects inconsistent transformation of physical weights.",
            "limitation": "A domain rejection is not a physical instability. The deliberately broken control is not an alternative dynamics."},
    }
    write_json(report_path / "interpretations.json", interpretations)
    lines = ["# Signal Space / GROSS Test 1", "", f"Classification: {analysis['classification']}. Technical execution: completed.",
             "", "Question: are the operator and observer identities implemented consistently, including nonunitary frame changes?",
             "", f"Measured: {summary['samples']} seeded samples; maximum scale-normalized residual {summary['max_residual']:.6g}; locked threshold 1e-10.",
             f"Tetrahedral spectrum error: {summary['gram_error']:.6g}. Omitted-weight negative-control error: {summary['omitted_weight_error']:.6g}.",
             "", "Method: saved complex 2x2 matrices and state vectors are audited using independent real Pauli components. Random Hermitian matrices and positive aggregates have condition number at most 100. SL(2,C) transformations combine SU(2) rotations with boosts of rapidity between -1 and 1.",
             "", "The exact rank-one aggregate has no normalized timelike observer. Near-collinear controls are reported separately, without clamping eigenvalues or inventing finite observer values.",
             "", "Error budget: floating-point algebra and conditioning; no fitted parameters, smoothing or stochastic confidence claim. Spatial boundary, conservation and timestep convergence are not applicable to this non-evolving matrix experiment.",
             "", "Limits: validates algebra/implementation only. No physical time, propagation, bound clock, Lorentz covariance of dynamics, or emergent spacetime is established.",
             "", "Next: Test 2 reciprocal event conservation and permissible rescheduling; Test 5 continuum action audit is an independent branch.",
             "", f"Run: {manifest['run_id']}", f"Analysis: {analysis['analysis_id']}", f"Solver commit: {manifest['code_identity']['revision']}",
             f"Config SHA-256: {manifest['config_hash']}", f"Renderer commit: {render_provenance['code_identity']['revision']}"]
    for key, value in interpretations.items():
        lines += ["", f"## {key}"] + [f"{k.title()}: {v}" for k, v in value.items()]
    markdown = "\n".join(lines) + "\n"
    (report_path / "report.md").write_text(markdown)
    (report_path / "report.html").write_text("<!doctype html><html><meta charset='utf-8'><title>Operator identities</title><body><pre style='white-space:pre-wrap'>" + html.escape(markdown) + "</pre>" + "".join(f"<img width='900' src='figures/{k}.svg' alt='{html.escape(q)}'>" for k, q in QUESTIONS.items()) + "</body></html>")
    with PdfPages(report_path / "report.pdf") as pdf:
        wrapped = [piece for line in lines for piece in (textwrap.wrap(line, 100) or [""])]
        for start in range(0, len(wrapped), 48):
            page = plt.figure(figsize=(8.5, 11))
            page.text(0.07, 0.96, "Operator and observer identity checks", fontsize=15, weight="bold", va="top")
            page.text(0.07, 0.91, "\n".join(wrapped[start:start + 48]), fontsize=9, va="top", linespacing=1.35)
            pdf.savefig(page)
            plt.close(page)
        for fig in made:
            pdf.savefig(fig)
            plt.close(fig)
    return {"required_inputs": [analysis["raw_source"], *[f"{analysis['path']}/derived/{n}" for n in ("residuals.csv", "controls.json", "conditioning.json", "summary.json")], f"{analysis['path']}/checks.json"], "figure_specs": specs, "interpretations": "interpretations.json"}
