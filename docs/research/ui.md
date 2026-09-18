# Local research workspace

## Purpose and boundary

The React research workspace is an audit client for the local E00 runtime. It does not contain a solver, derive physics, or infer a scientific result. Configuration validation, resource estimates, execution, cancellation, resume, analysis, and report generation all cross the origin-bound loopback API and invoke the same `ResearchRuntime` used by the CLI.

The separately labeled delay-network panel still uses the historical TypeScript engine. Its preparation inspection is not a run in the charged-recurrence research framework.

## Start the workspace

Run the Vite application and the loopback runtime in separate terminals. The origin must exactly match the URL opened in the browser.

```sh
npm run dev -- --host 127.0.0.1 --port 5173
npm run research -- --workspace .research-work serve \
  --origin http://127.0.0.1:5173 \
  --port 8765
```

The service prints a JSON object containing its loopback port and ephemeral bearer token. In the browser, enter `http://127.0.0.1:8765` and that token, then choose **Connect runtime**. The token is retained only in the browser session so a reload can reconnect; it is never written into a run package.

## Views

### Prepare

The form is generated from the registered experiment's authoritative closed JSON Schema. It displays the active experiment/model IDs, declared units, numeric domains, seed, resource limits, analysis threshold, report title, source equation link, implemented capabilities, and explicitly unavailable capabilities. **Validate & estimate** returns the same normalized configuration and resource decision as the CLI. Any edit invalidates the previous resolution; starting after an edit creates a new immutable run identity.

### Run audit

The runtime lists saved run manifests, so a page reload does not lose access to earlier packages. The view exposes run and attempt IDs, exact resolved configuration, config hash, code revision, seed ledger, technical state, scientific classification, failures, checkpoints, acceptance evidence, and known gaps.

Events are resumed from the last acknowledged `attempt_id:sequence` cursor. Duplicate records are ignored. A non-contiguous sequence or rejected cursor is shown as a visible recovery warning; the client reloads the authoritative append-only log rather than concealing the gap. Cancel and resume remain separate attempt operations. Resume never edits its parent attempt.

### Compare

Comparison loads each run's cataloged resolved-configuration artifact. Model, units, geometry, boundary, parameters, and technical state are shown side by side. The client refuses to imply an aggregate when model, units, geometry, or boundary declarations differ. Failed and interrupted runs remain selectable evidence.

### Reports

Report preview reads only generated artifacts from the selected run. The linked plot uses the exact saved CSV and figure specification, and exposes axes, units, downsampling, normalization, fit window, and renderer. Raw, derived, check, plot-data, figure, and report artifacts remain individually downloadable by artifact ID. Regenerating a report invokes the runtime renderer and does not rerun the numerical worker.

## Research collection

The collection browser remains usable without the runtime. Markdown sources render as structured headings, paragraphs, lists, and equation blocks. Catalog relationship IDs connect milestones to their figures and reproducibility source bundles. Adding a conforming catalog entry or accepted archived run does not require a React component change.

## Validation and limitations

Browser tests cover the schema-driven preparation, resource estimate, run/audit journey, interrupted resume lineage, report regeneration, saved-data plot metadata, keyboard focus, and narrow viewport. API tests cover authoritative schemas, saved-run discovery, origin/token enforcement, resumable events, and artifact access.

The E00 fixture is intentionally non-physical. It has no field-slice, branch-continuation, or research-scale sweep output, so the UI truthfully labels those capabilities unavailable instead of presenting placeholder controls. Future experiment plugins can add those artifact types through the same schema, manifest, figure-specification, and artifact catalog contracts.
