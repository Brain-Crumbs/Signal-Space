"""Question-driven circuit figures derived solely from immutable saved evidence."""

import csv
import html
import shutil
import textwrap
import numpy as np

from signal_space.runtime.io import read_json, write_json

QUESTIONS = {
    "causal-incidence": "Do event outputs depend only on their causal ancestors?",
    "matrix-balance": "Does reciprocal memory exchange close the matrix-charge ledger?",
    "numerical-audit": "Do conservation and equivalent descriptions survive numerical refinement?",
    "order-controls": "Can the audit distinguish physical interventions from rescheduling?",
}


def render_report(run_path, report_path, manifest, analysis, render_provenance):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    derived = run_path / analysis["path"] / "derived"
    plots, figures = report_path / "plot-data", report_path / "figures"
    plots.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    for p in derived.iterdir():
        shutil.copy2(p, plots / p.name)

    def rows(name):
        with (plots / f"{name}.csv").open(newline="") as f:
            return list(csv.DictReader(f))

    summary = analysis["summary"]
    maximum, minimum = summary["maxima"], summary["minima"]
    incidence, jacobian = read_json(plots / "incidence.json"), rows("jacobian")
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
    made, specs = [], []

    def save(fig, key, sources, transformations):
        write_json(figures / f"{key}.figure.json", {
            "schema_version": "research-figure-spec-v1", "id": key,
            "source_datasets": [f"plot-data/{v}" for v in sources], "transformations": transformations,
            "axes": {"x": {"unit": "event index, gate parameter, input wire or category"}, "y": {"unit": "dimensionless"}},
            "ranges": "explicit log display floors where stated", "normalization": "see locked protocol; max(1, initial norm)",
            "downsampling": "none", "fit_window": None, "renderer": f"matplotlib-{matplotlib.__version__}"})
        for extension in ("png", "svg", "pdf"):
            fig.savefig(figures / f"{key}.{extension}", dpi=170 if extension == "png" else None)
        made.append(fig)
        specs.append(f"figures/{key}.figure.json")

    fig, axes = plt.subplots(1, 2, figsize=(11, 5.3), layout="constrained", gridspec_kw={"width_ratios": [1.1, 1]})
    events = incidence["events"]
    ancestors = np.array(incidence["ancestor_mask"])
    positions = {i: (i // 4, 3 - i % 4) for i in range(12)}
    previous = {}
    for event, wires in enumerate(events):
        x, y = positions[event]
        for wire in wires:
            if wire in previous:
                source = previous[wire]
                axes[0].annotate("", xy=(x - 0.12, y), xytext=(positions[source][0] + 0.12, positions[source][1]),
                                 arrowprops={"arrowstyle": "->", "color": "#969da6", "lw": 0.8, "alpha": 0.6})
            previous[wire] = event
        axes[0].scatter([x], [y], s=480, color="#1c9b86" if ancestors[event, 0] else "#d9dde3", zorder=3)
        axes[0].text(x, y, f"E{event}", ha="center", va="center", fontsize=8, zorder=4)
        axes[0].text(x, y - 0.23, f"w{wires[0]},w{wires[1]},m{wires[2]-8}", ha="center", fontsize=7)
    axes[0].set(xlim=(-0.4, 2.4), ylim=(-0.5, 3.6), title="Prescribed incidence (arrows are wires)")
    axes[0].text(1, 3.35, "Green: descendant of initial wave 0", ha="center", fontsize=8)
    axes[0].axis("off")
    data = np.zeros((12, 12))
    # Plot the maximum over both lambdas and both finite-difference step sizes.
    for row in jacobian:
        e, w = int(row["event"]), int(row["input_wire"])
        data[e, w] = max(data[e, w], float(row["response"]))
    masked = np.ma.masked_where(~ancestors, np.log10(np.maximum(data, 1e-18)))
    cmap = plt.get_cmap("viridis").copy()
    cmap.set_bad("#e2e5ea")
    im = axes[1].imshow(masked, cmap=cmap, vmin=-3, vmax=max(1, np.max(masked)))
    axes[1].set(xticks=range(12), yticks=range(12), xlabel="Initial wire (0-7 wave; 8-11 memory)", ylabel="Output event",
                title=f"Measured causal response\nGray: nonancestor; maximum response {maximum['jacobian_outside']:.2g}")
    fig.colorbar(im, ax=axes[1], shrink=0.72, label="log10 Jacobian response (dimensionless)")
    save(fig, "causal-incidence", ["incidence.json", "jacobian.csv"], ["max Jacobian norm over both lambdas and finite-difference steps", "nonancestors gray; causal entries log10, color range clipped below -3; exact data retained", "layout is incidence, not physical space or time"])

    balance = rows("balance")
    fig, axes = plt.subplots(2, 2, figsize=(10, 6), layout="constrained")
    for col, lam in enumerate((0, 0.1)):
        reciprocal = [r for r in balance if float(r["lambda"]) == lam and r["mode"] == "reciprocal"]
        frozen = [r for r in balance if float(r["lambda"]) == lam and r["mode"] == "frozen"]
        t = [float(r["s"]) for r in reciprocal]
        for field, label, color in (("wave_z_change", "Wave ledger", "#356eae"), ("memory_z_change", "Memory ledger", "#1c9b86")):
            axes[0, col].plot(t, [float(r[field]) for r in reciprocal], "o-", ms=3, label=label, color=color)
        axes[0, col].axhline(0, color="gray", lw=0.7)
        axes[0, col].set(title=f"Reciprocal exchange | lambda = {lam}", ylabel="Change in Pauli-z charge component")
        axes[0, col].legend(fontsize=8)
        for data, label, color in ((reciprocal, "Reciprocal", "#1c9b86"), (frozen, "Frozen memory", "#c6534f")):
            axes[1, col].semilogy(t, [max(1e-18, float(r["total_change"])) for r in data], "o-", ms=3, label=label, color=color)
        axes[1, col].set(xlabel="Gate parameter s (dimensionless)", ylabel="Absolute total matrix-charge change")
        axes[1, col].legend(fontsize=8)
    fig.suptitle("Test 2 | Backreaction closes the ledger; freezing memory opens it")
    save(fig, "matrix-balance", ["balance.csv"], ["preparation 0, first event; signed Pauli-z changes and Frobenius total changes", "log display max(value,1e-18); initial zeros retained"])

    residuals = rows("residuals")
    fig, axes = plt.subplots(1, 2, figsize=(10, 5), layout="constrained")
    names = ["N_error", "memory_norm_error", "J_error", "H_error"]
    for label, offset, color in (("base", -0.13, "#356eae"), ("fine", 0.13, "#1c9b86")):
        values = [max(float(r[k]) for r in residuals if r["resolution"] == label) for k in names]
        axes[0].bar(np.arange(4) + offset, np.maximum(values, 1e-18), width=0.26, label=label, color=color)
    axes[0].set(xticks=range(4), xticklabels=["Wave N", "Memory norm", "Matrix J", "Event H"], title="Maximum over every circuit and gate")
    names = ["exact", "refinement", "rescheduling", "frame", "cut_charge"]
    axes[1].bar(range(len(names)), [max(1e-18, maximum[k]) for k in names], color="#356eae")
    for i, key in enumerate(names):
        if maximum[key] == 0:
            axes[1].text(i, 3e-18, "exact 0", ha="center", fontsize=8)
    axes[1].set(xticks=range(len(names)), xticklabels=["Exact\nsolution", "Tolerance\nhalving", "Schedule", "U(2)\nframes", "Cut\ncharge"], title="Independent references and descriptions")
    for ax in axes:
        ax.set(yscale="log", ylabel="Normalized error (dimensionless)", ylim=(1e-18, 1e-7))
        ax.axhline(1e-9, color="#c6534f", ls="--", label="1e-9 acceptance limit")
        ax.legend(fontsize=8)
    save(fig, "numerical-audit", ["residuals.csv", "summary.json"], ["max across all samples, lambdas, gates and saved times; half tolerance compared with baseline", "log display max(value,1e-18); exact zeros retained"])

    controls = rows("controls")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8), layout="constrained")
    for col, key in enumerate(("order_signal", "frozen_charge")):
        for lam, marker, color in ((0, "o", "#356eae"), (0.1, "s", "#1c9b86")):
            subset = [r for r in controls if float(r["lambda"]) == lam]
            axes[col].scatter([int(r["sample"]) + (0.08 if lam else -0.08) for r in subset], [float(r[key]) for r in subset], marker=marker, color=color, label=f"lambda = {lam}")
        axes[col].axhline(1e-4, color="#c6534f", ls="--", label="control detection threshold")
        axes[col].set(yscale="log", xticks=range(4), xlabel="Seeded preparation", ylabel="Dimensionless response", title="Shared-memory order: projector change" if col == 0 else "Frozen-memory charge defect")
        axes[col].legend(fontsize=8)
    save(fig, "order-controls", ["controls.csv"], ["every preparation and both lambdas; no fit or smoothing", "physical interventions, not equivalent descriptions"])

    interpretations = {
        "causal-incidence": {"question": QUESTIONS["causal-incidence"],
            "reading": f"Green events descend from initial wave 0. Gray heatmap cells are nonancestors; their largest response is {maximum['jacobian_outside']:.3g}. Step-halving Jacobian difference is {maximum['jacobian_refinement']:.3g}.",
            "significance": "Tests participant-only causal dependence and includes a disconnected branch as a null. Memory-response and intervention checks separately verify nontrivial dynamics.",
            "limitation": "Incidence is supplied, not derived space. Jacobians cover one preparation, both couplings and physical memory tangents; no universal metric is inferred."},
        "matrix-balance": {"question": QUESTIONS["matrix-balance"],
            "reading": f"Wave and memory charge components exchange with opposite signs. The smallest frozen-memory relative charge defect across all cases is {minimum['frozen_charge']:.3g}.",
            "significance": "Tests whether reciprocal memory dynamics closes the conserved matrix ledger; a prescribed frozen projector is an externally driven control.",
            "limitation": "Displayed trajectory is the first gate of preparation 0. The Pauli component is basis dependent; the full Frobenius residual is the acceptance observable. This is not mechanical recoil."},
        "numerical-audit": {"question": QUESTIONS["numerical-audit"],
            "reading": f"Largest event conservation residual {maximum['conservation']:.3g}; exact-solution difference {maximum['exact']:.3g}; tolerance-halving difference {maximum['refinement']:.3g}. Compare with 1e-9.",
            "significance": "Checks integrated dynamics against a closed solution and tests description invariance under legal schedules and local frames.",
            "limitation": "Finite circuit and finite states. U(2) covariance is not Lorentz covariance; numerical tolerance refinement is not a continuum limit. Exact zeros use a display floor."},
        "order-controls": {"question": QUESTIONS["order-controls"],
            "reading": f"Smallest shared-memory projector change {minimum['order_signal']:.3g}; smallest frozen-memory defect {minimum['frozen_charge']:.3g}. Every preparation is compared with 1e-4.",
            "significance": "Distinguishes changes to physical event ordering and reciprocal feedback from permissible rescheduling of independent events.",
            "limitation": "Generic noncommutativity is expected, not guaranteed for all states. These fixed controls do not define new candidate models or test propagation."},
    }
    write_json(report_path / "interpretations.json", interpretations)
    lines = ["# Signal Space / GROSS Test 2", "", f"Scientific classification: {analysis['classification']}. Technical execution: completed.", "",
             "Question: does the reciprocal event law preserve its declared ledger and causal scheduling?",
             "Method: four seeded preparations, lambda=0 and 0.1, kappa=pi/2; twelve acyclic gates per circuit. DOP853 numerical evolution is compared with half integration tolerances and a separate closed matrix-exponential solution.",
             "Variables: z1,z2 are complex wave spinors; w is unit memory; P=ww-dagger, d=z1-z2, N=|z1|^2+|z2|^2. The gate Hamiltonian is H=kappa |w-dagger d|^2 + lambda N^2/2. All quantities and the gate parameter s are dimensionless.",
             "The exact reference uses the constant Hermitian matrix S=dd-dagger+2ww-dagger. The protocol derives this solution and defines all normalization and error gates.", "",
             f"Largest conservation residual: {maximum['conservation']:.6g}. Exact-reference difference: {maximum['exact']:.6g}. Outside-ancestor Jacobian: {maximum['jacobian_outside']:.6g}.",
             f"Run: {manifest['run_id']}. Analysis: {analysis['analysis_id']}.",
             f"Solver revision: {manifest['code_identity']['revision']}. Config: {manifest['config_hash']}.", "",
             "Error controls: within-gate norm, matrix-charge and Hamiltonian ledgers; complete-cut charge; half-tolerance integration; closed solution; central-difference step halving; local frames and valid topological rescheduling.",
             "Boundary sensitivity: no spatial box or mesh exists in this test. All circuit wires are retained, and the disconnected branch supplies a causal null. Changing incidence would change the apparatus, not refine it.",
             "Limits: causal support is not a metric. No clock, full mode spectrum, direction-dependent propagation or emergent spacetime has been evaluated. Event H is not asserted to be a globally conserved circuit energy.",
             "Next if accepted: Test 3 exact-router dispersion, with orthogonal, oblique and collinear triads, reversed order and full-zone inspection. Retain physical memory modes for Test 4 and directional comparisons for Test 11."]
    for key, value in interpretations.items():
        lines += ["", key] + [f"{k.title()}: {v}" for k, v in value.items()]
    markdown = "\n".join(lines) + "\n"
    (report_path / "report.md").write_text(markdown)
    (report_path / "report.html").write_text("<!doctype html><html><meta charset='utf-8'><title>Reciprocal events</title><body><pre style='white-space:pre-wrap'>" + html.escape(markdown) + "</pre>" + "".join(f"<img width='1000' src='figures/{k}.svg' alt='{html.escape(q)}'>" for k, q in QUESTIONS.items()) + "</body></html>")
    with PdfPages(report_path / "report.pdf") as pdf:
        wrapped = [piece for line in lines for piece in (textwrap.wrap(line, 100) or [""])]
        for start in range(0, len(wrapped), 48):
            page = plt.figure(figsize=(8.5, 11))
            page.text(0.07, 0.96, "Reciprocal event audit", fontsize=15, weight="bold", va="top")
            page.text(0.07, 0.91, "\n".join(wrapped[start:start + 48]), fontsize=9, va="top", linespacing=1.35)
            pdf.savefig(page)
            plt.close(page)
        for fig in made:
            pdf.savefig(fig)
            plt.close(fig)
    raw_dir = (run_path / analysis["raw_source"]).parent
    return {"required_inputs": [p.relative_to(run_path).as_posix() for p in sorted(raw_dir.iterdir()) if p.is_file()] + [f"{analysis['path']}/derived/{p.name}" for p in derived.iterdir()] + [f"{analysis['path']}/checks.json"],
            "figure_specs": specs, "interpretations": "interpretations.json"}
