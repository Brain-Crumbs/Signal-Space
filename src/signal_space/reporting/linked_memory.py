"""Question-driven linked-memory reports, regenerated only from saved data."""
import csv
import html
import shutil
import textwrap
import numpy as np

from signal_space.runtime.io import read_json, write_json

QUESTIONS = {
    "linked-incidence": "What is supplied by the event word, and what moves internally?",
    "complement-persistence": "Does complementarity persist within gates and at endpoints?",
    "coherent-equivalence": "Does the coherent lift retain the relative phase that local rays lose?",
    "finite-time-sensitivity": "How do all physical wave and memory perturbations amplify?",
    "record-error-budget": "Does the comparison bound support a full-cycle record forecast?",
}


def render_report(run_path, report_path, manifest, analysis, render_provenance):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    derived = run_path / analysis["path"] / "derived"
    plots, figures = report_path / "plot-data", report_path / "figures"
    plots.mkdir(parents=True,exist_ok=True); figures.mkdir(parents=True,exist_ok=True)
    for path in derived.iterdir(): shutil.copy2(path, plots / path.name)
    def rows(name):
        with (plots / f"{name}.csv").open(newline="") as handle: return list(csv.DictReader(handle))
    trajectory, audit, sensitivity, budget = (rows(x) for x in ("trajectories","audit","sensitivity","budget"))
    summary = analysis["summary"]
    made, specs = [], []
    interpretations = {}
    plt.rcParams.update({"font.size":9,"axes.spines.top":False,"axes.spines.right":False})

    def save(fig,key,sources,transformations,reading,significance,limitation):
        write_json(figures/f"{key}.figure.json", {"schema_version":"research-figure-spec-v1","id":key,
            "source_datasets":[f"plot-data/{x}" for x in sources],"transformations":transformations,
            "axes":{"x":{"unit":"dimensionless gate parameter or internal Bloch coordinate"},
                    "y":{"unit":"dimensionless"}},"ranges":"see labelled axes; explicit log display floors",
            "normalization":"N=1; horizontal memory tangent norm via P/sqrt(2)",
            "downsampling":"none except the explicitly stated first-four-cycle view",
            "fit_window":None,"renderer":f"matplotlib-{matplotlib.__version__}"})
        for ext in ("png","svg","pdf"): fig.savefig(figures/f"{key}.{ext}",dpi=160 if ext=="png" else None)
        specs.append(f"figures/{key}.figure.json"); made.append(fig)
        interpretations[key]={"question":QUESTIONS[key],"reading":reading,
            "significance":significance,"limitation":limitation}

    fig,axes=plt.subplots(1,2,figsize=(10,4.6),layout="constrained")
    incidence=read_json(plots/"incidence.json")
    positions=incidence["positions"]
    for left,right in incidence["edges"]:
        axes[0].plot(*zip(positions[left],positions[right]),color="#a9b2c0")
    for name,(x,y) in positions.items():
        axes[0].scatter(x,y,s=750,color="#328a83" if name in "AB" else "#416caa",zorder=3)
        axes[0].text(x,y,name,color="white",ha="center",va="center",zorder=4)
    axes[0].text(1,-.65,"Supplied order: A then B, repeated",ha="center")
    axes[0].set(xlim=(-.4,2.4),ylim=(-1,1.5),title="Incidence, not physical space"); axes[0].axis("off")
    selected=[r for r in trajectory if r["preparation"]=="active-plus" and float(r["total_s"])<=8]
    circle=np.linspace(0,2*np.pi,180)
    axes[1].plot(np.cos(circle),np.sin(circle),color="#dadfe5")
    for m,label in ((0,"Memory A"),(1,"Memory B")):
        axes[1].plot([float(r[f"memory_{m}_x"]) for r in selected],
                     [float(r[f"memory_{m}_z"]) for r in selected],label=label,lw=1)
    axes[1].set(xlabel="Internal Bloch x",ylabel="Internal Bloch z",title=f"Active-plus: first {min(4,summary['cycles'])} cycle(s)",aspect="equal")
    axes[1].legend()
    save(fig,"linked-incidence",["trajectories.csv","incidence.json"],["supplied incidence layout; not an embedding",
        "active-plus first min(4, cycles) cycles; Bloch x/z projection"],
        "The shared port links two separately carried memories. Their Bloch paths describe internal projector motion.",
        "Makes supplied wiring and evolved internal geometry visibly distinct.",
        "Projected paths can overlap; no physical trajectory, spatial dimension or spontaneous binding is inferred.")

    fig,axes=plt.subplots(2,1,figsize=(10,6),layout="constrained",sharex=True)
    for name in ("dark","initially-commuting","active-plus","active-minus"):
        chosen=[r for r in trajectory if r["preparation"]==name]
        t=[float(r["total_s"]) for r in chosen]
        axes[0].plot(t,[float(r["complement_defect"]) for r in chosen],label=name,lw=1)
        axes[1].plot(t,[float(r["overlap"]) for r in chosen],label=name,lw=1)
        endpoints=[r for r in chosen if float(r["s"])==1]
        axes[0].scatter([float(r["total_s"]) for r in endpoints],
                        [float(r["complement_defect"]) for r in endpoints],s=3)
    axes[0].set(ylabel="Complement defect ||PA+PB-I||F",title="Lines: within-gate samples; points: gate endpoints")
    control_rows=rows("controls")
    isolated_defect=max(float(r["max_complement_defect"]) for r in control_rows
        if r["preparation"]=="initially-commuting" and r["control"] in ("isolated-A","isolated-B"))
    axes[0].axhline(isolated_defect,color="#9098a6",ls="--",lw=1,label="Isolated commuting A/B (max)")
    axes[1].set(xlabel="Accumulated gate parameter (two gates per cycle)",ylabel="Memory overlap tr(PA PB)")
    axes[0].legend(ncol=2,fontsize=8)
    save(fig,"complement-persistence",["trajectories.csv","summary.json","controls.csv"],["four initially complementary preparations; exact trajectories",
        "all within-event samples; endpoints separately marked; c squared equals 2 overlap; isolated commuting control maximum is a horizontal baseline"],
        f"The active initial constraint derivative is {summary['analytical_constraint_derivatives']['active-plus']:.6g}. Preparation 2 is only initially commuting.",
        "Separates continuous constraints from endpoint return and retains the corrected counterexample.",
        "Finite samples cannot prove endpoint or continuous invariance for an arbitrary family. The nonzero derivative gives the analytical obstruction.")

    fig,axes=plt.subplots(1,2,figsize=(10,4.6),layout="constrained")
    for variant in ("operator","operator-fine"):
        grouped={}
        for r in audit:
            if r["variant"]==variant: grouped[int(r["gate"])]=max(grouped.get(int(r["gate"]),0),float(r["lift_mismatch"]))
        axes[0].semilogy(list(grouped),[max(v,1e-18) for v in grouped.values()],label=variant)
    axes[0].axhline(1e-9,color="#b85252",ls="--",label="Locked numerical gate")
    axes[0].set(xlabel="Gate index",ylabel="Maximum coherent state/record mismatch",title="Independent W, PA, PB evolution"); axes[0].legend(fontsize=8)
    witnesses=[next(r for r in trajectory if r["preparation"]==name) for name in ("coherence-plus","coherence-minus")]
    axes[1].bar(["Same phase","Opposite phase"],[float(r["H_event"]) for r in witnesses],color=["#328a83","#416caa"])
    axes[1].set(ylabel="Initial event Hamiltonian",title="Identical local ray operators, different H")
    save(fig,"coherent-equivalence",["audit.csv","trajectories.csv"],["max mismatch over all preparations/samples at each gate",
        "display floor 1e-18; exact zeros retained; witness uses first-gate initial H"],
        f"Largest lift/refinement difference is {summary['max_equivalence']:.3g}; witness energies are 0 and kappa.",
        "Checks a pure-state representation equivalence and exhibits the information lost by independent local rays.",
        "No ensemble closure for mixed W is established. Relative port phases remain; no separate phase fitting is used.")

    fig,axes=plt.subplots(1,2,figsize=(10,4.8),layout="constrained")
    for name in ("active-plus","active-minus"):
        chosen=[r for r in sensitivity if r["preparation"]==name]
        t=[float(r["cycle"]) for r in chosen]
        axes[0].semilogy(t,[float(r["singular_amplification"]) for r in chosen],label=name)
        for key,style in (("wave","-"),("memory_A","--"),("memory_B",":")):
            axes[1].semilogy(t,[max(float(r[f"{key}_record_sensitivity"]),1e-18) for r in chosen],
                            ls=style,label=f"{name}: {key}")
    axes[0].set(xlabel="Cycle count",ylabel="Largest finite-time singular amplification",title="All 16 physical input directions")
    axes[1].set(xlabel="Cycle count",ylabel="Maximum record derivative norm",title="Wave and both memory sectors")
    for ax in axes: ax.legend(fontsize=7)
    save(fig,"finite-time-sensitivity",["sensitivity.csv"],["SVD of physical feature derivative; unphysical memory phases removed",
        "max row norm by wave/memory input sector; 12+2+2 real directions"],
        f"Largest relative tangent comparison error is {summary['max_tangent_difference']:.3g}; check it against 1e-4 before trusting a linear forecast.",
        "Retains genuine orientation and memory response rather than studying only wave or charge-preserving directions.",
        "This is finite-time amplification, not Floquet stability. Finite differences may cease to resolve the derivative at a long horizon.")

    fig,ax=plt.subplots(figsize=(10,4.7),layout="constrained")
    ax.semilogy([float(r["cycle"]) for r in budget],[float(r["preparation_record_bound"]) for r in budget],
                "o",label="Conditional exact-law preparation bound (full-cycle points)",color="#b85252")
    for name in ("active-plus","active-minus"):
        chosen=[r for r in sensitivity if r["preparation"]==name and float(r["cycle"]).is_integer()]
        ax.semilogy([float(r["cycle"]) for r in chosen],[max(float(r["observed_record_error"]),1e-18) for r in chosen],"o-",ms=4,label=f"Observed: {name}")
    ax.axhline(1e-3,color="gray",ls="--",label="Total record target")
    ax.axhline(.00025,color="#328a83",ls=":",label="Preparation allocation")
    ax.set(xlabel="Full cycles (error carries across switches)",ylabel="Absolute local record error",title="A loose bound is a certification obstruction")
    ax.legend(fontsize=8)
    save(fig,"record-error-budget",["budget.csv","sensitivity.csv"],["full-cycle samples; observed maximum over 16 directions and both perturbation signs",
        "conditional exponential capped by exact q range 2N; no error reset"],
        f"The conservative preparation horizon is {summary['conditional_preparation_horizon_cycles']} full cycles. End-to-end certification remains unresolved.",
        "Separates empirical perturbation behavior from a justified comparison bound and its error allocations.",
        "Validated numerical residual, roundoff and readout enclosures are missing; no positive certified horizon or autonomous detector is claimed.")

    write_json(report_path/"interpretations.json",interpretations)
    lines=["# GROSS v0.3 linked-memory seed","",f"Scientific classification: {analysis['classification']}. Technical execution completed.",
        "A universal complement-persistence claim is contradicted analytically; certification remains a separate unresolved gate.",
        "Three coherent complex two-component ports, two unit projector memories, identity transports, serial A then B; lambda=0, kappa=pi/2.",
        "Every gate uses the existing exact_gate; an independent DOP853 operator lift retains all cross-port coherence.",
        f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; source {manifest['code_identity']['revision']}.",
        f"Cycles {summary['cycles']}; physical tangent dimensions 16; ledger residual {summary['max_conservation']:.5g}.",
        "The preparation's commuting full-word claim was corrected before lock: A transfers wave into the shared port, so B need not commute.",
        "N and J are global circuit invariants. Event H is conserved only within each active gate; gate parameter is not physical time.",
        summary["certification_obstruction"],
        "Next: derive a less conservative trajectory-specific bound on the same small family; retain every genuine memory/orientation direction.",
        "This seed does not complete the four-ray F2 problem, establish physical space or an autonomous clock, or alter Tests 1-11."]
    for key,parts in interpretations.items(): lines += ["",key]+[f"{k.title()}: {v}" for k,v in parts.items()]
    markdown="\n".join(lines)+"\n"
    (report_path/"report.md").write_text(markdown)
    (report_path/"report.html").write_text("<!doctype html><html><meta charset='utf-8'><body><pre style='white-space:pre-wrap'>"+
        html.escape(markdown)+"</pre>"+"".join(f"<img width='1000' src='figures/{k}.svg' alt='{html.escape(q)}'>" for k,q in QUESTIONS.items())+"</body></html>")
    with PdfPages(report_path/"report.pdf") as pdf:
        wrapped=[piece for line in lines for piece in (textwrap.wrap(line,100) or [""])]
        for start in range(0,len(wrapped),42):
            page=plt.figure(figsize=(8.5,11));page.text(.07,.96,"Linked-memory persistence",fontsize=15,weight="bold",va="top")
            page.text(.07,.91,"\n".join(wrapped[start:start+42]),fontsize=9,va="top",linespacing=1.3)
            pdf.savefig(page);plt.close(page)
        for fig in made: pdf.savefig(fig);plt.close(fig)
    return {"required_inputs":[path.relative_to(run_path).as_posix() for path in sorted(derived.iterdir())]+
        [analysis["raw_source"],f"{analysis['path']}/checks.json"],"figure_specs":specs,"interpretations":"interpretations.json"}
