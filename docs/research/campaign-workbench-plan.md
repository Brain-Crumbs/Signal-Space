# Campaign workbench implementation

Baseline: `6f04ade0f5c83fe0548bfb70159bcd7b0b4584d1`. Implements the 29 September
refactor-review backlog. This is bounded engineering work on the existing GROSS
models; full Test 8 exchange remains separately registered scientific work.

1. Repair quiet report questions/attempt lineage, common host admission, and
   recursive progress with durable cursors.
2. Centralize recipes, preflight and workstation profiles; derive new resource
   plans without touching source locks; journal/recover every pipeline stage;
   expose generic paired export/import verification.
3. Persist campaign DAGs and gate dependencies; reuse verified exact identities;
   measure per-stage/per-case costs; schedule long ready work first; compare
   compatible saved runs and account for retained evidence plus export space.
4. Extract the current axisymmetric physics core behind stable typed model,
   state, preparation, backend and detector interfaces. Keep a reference backend
   and explicit unsupported capabilities. Optimize repeated diagnostics without
   changing the registered equations or numerical cadence.
5. Add a machine-readable Tests 1–11 ledger, evidence-driven current summaries,
   reusable saved-data diagnostics and consistent external artifact handoff.
6. Validate failure/recovery paths, reference/compiled and serial/parallel
   equivalence, existing evidence immutability, CLI and pipeline workflows.

Engineering evidence uses bounded fixtures. No accepted physics status, locked
threshold, original plan/config, or archived evidence is rewritten. A model
extension needs its own action and plan; the engine must reject unsupported
gravity/topology/exchange/worldtube requests rather than fabricate support.

Commit each coherent implementation increment. Final delivery is a PR to main,
not an automatic merge. Source and environment identity remain strict for solver
resume; saved-data analysis/report recovery records its own current provenance.
