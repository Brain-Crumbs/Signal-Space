# Signal Space experiment handoff contract

The canonical evidence remains the immutable package specified by `docs/research/artifact-contract.md`. This contract adds a reader-facing export from one named run, analysis, and report; it does not move or rewrite raw evidence. New experiments can use the registered Python runtime and the current model IDs; historical ZIPs are imported sources, not conforming runs.

```text
<experiment-id>_<run-id>/
  README.md
  Experimental_Setup.pdf
  Experiment_Results.pdf
  Experiment_Analysis_and_Next.md
  plan.json
  export.json
  results/
    data/            raw/derived/plot-data (as available)
    tables/          CSV/JSON tables (as available)
    source/          all Python sources used in this export (as available)
  figures/
    static/          PNG/SVG/PDF renderings
    animations/      optional video/GIF
    interactive/     optional HTML
    figure_index.json
```

`README.md` states the question, model, run/analysis/report IDs, classification, navigation, and gaps. `Experimental_Setup.pdf` describes the locked method and all planned visuals. `Experiment_Results.pdf` includes the selected report's figures and interpretations; any missing interpretation is an explicit export failure. `Experiment_Analysis_and_Next.md` contains findings, limits, links to checks, and the next derivation/calculation. `export.json` records checksums and source-run provenance; `experiment_contract.py bundle` verifies the physical files and cross references.

Before execution, every planned figure must name its question, observables, competing signatures, controls, uncertainty, and source transformations. For each delivered figure, provide Question, Reading, Significance, and Limitation; label it illustrative, diagnostic, or evidentiary. Required evidentiary figures must be present. Figures show geometry and signal dynamics with relevant spatial/temporal views, as well as residuals, controls, and convergence that test the interpretation. Do not infer common geometry from a visually suggestive field plot alone.

Stages are sequential: locked plan → registered run → immutable analysis → visual report → mentor synthesis → export. The locked plan pins the runtime config SHA-256; `.agents/scripts/run_plan.py --plan PLAN.json --repo-root REPOSITORY --workspace WORKSPACE --execute` checks that hash, identity, resource ceiling, and registered runtime validation/estimate before executing. Changing analysis produces a new analysis; changing figures or narration produces a new report/export. Technical completion and scientific classification remain distinct.

Use `python3 .agents/scripts/experiment_contract.py lock PLAN.json`, `plan PLAN.json`, and `bundle EXPORT_DIRECTORY`. To build an export from a verified run, use `python3 .agents/scripts/package_experiment.py --run RUN_DIRECTORY --plan PLAN.json --interpretations INTERPRETATIONS.json --mentor MENTOR.md --output NEW_DIRECTORY [--source-dir PYTHON_SOURCE_DIRECTORY]`. The builder takes the latest analysis and its report, copies its raw/derived/plot data and figure specifications, and generates both PDFs with four-part interpretations for every saved figure. It refuses to overwrite an export. The bundle checker does not validate the physics; it verifies the handoff contract. CI scans any exports committed under `research/experiments/`. The canonical runtime `verify` remains mandatory on the source run.
