# Visual research workspace

Issue #49 extends the #38 UI with E01 exploration. Select a saved E01 run in **Run audit**. The primary view is the saved branch and its linked scientific diagnostics. The controls and existing audit trail remain on the same page.

## Getting started

1. Run the small validation fixture using the existing E01 instructions. It remains scientifically unresolved.
2. Choose **Analyze saved output**, then **Regenerate report**. Open **Run audit** to explore it. Reports made before this feature retain their figure gallery; regenerate them to add interactive data without rerunning the solver.
3. Select a solution through the dropdown, a branch point, or the keyboard-accessible exact-data table. Energy/charge, frequency/charge and frequency/radius views share this selection. Profiles, spectra, binding channels, criteria and numerical budgets update together.
4. Overlay another profile or filter the spectrum by angular sector. Chart X limits zoom the horizontal range; reset restores the full range. Hover points for exact saved values, or expand the paginated data table.
5. In **Compare**, select structurally compatible runs. Existing configuration differences remain visible. Branches and independently selected radial profiles overlay without implying an aggregate. Different physical or numerical parameters are not automatically equivalent just because the structural gate passes.
6. **Reports** automatically loads five saved PNG figures and can render the Markdown report, including equations and tables. Figure downloads retain their original SVG/PDF/PNG formats.

## Scientific mapping

| View                                    | Saved evidence                                  | E01 protocol                                                           |
| --------------------------------------- | ----------------------------------------------- | ---------------------------------------------------------------------- |
| Energy/charge, frequency/charge, radius | `branch.csv`, explicit raw parent edges         | §§4–5: branch construction and independent observables                 |
| Radial amplitude and derivative         | `profiles.csv` from saved accepted profiles     | §§2–5: stationary ansatz and radial boundary-value problem             |
| Complex spectrum by angular sector      | `spectra.csv`, per-mode `spectral-budgets.json` | §6: exp(σt), charge constraint, residuals and matched refinement error |
| Binding margins with 3× numerical error | `breakup.csv`                                   | §7: tested charge-conserving channels and finite coverage              |
| Refinement differences and threshold    | `convergence.csv`, configured tolerance         | §8: independent mesh, volume and tolerance changes                     |
| Point criteria and outcome              | `selection.json`                                | §9: candidate/no-candidate/unresolved criteria                         |

The equation source remains `research/papers/charged-recurrence-winding-hopf.md` §§2–10, 14–15 and 23. No model equations or acceptance criteria change. E and Q retain 1/λ. The energy view includes the free-charge reference for the implemented positive-Q, m=1 branch. A profile is a stationary radial solution: moving across frequency is not physical-time evolution.

Only explicit accepted parent edges are connected. Missing, failed and rejected records stay available in the coverage panel. No lines are invented by sorting independent seeds. Numerical error bars are not statistical confidence intervals. A missing mode error produces no bar and remains unavailable in the exact-data table; absence of a bar is not evidence of zero uncertainty. Point criteria come from saved independent analysis, never chart appearance. No nonlinear stability, particle identity or topology follows from these views.

## Live progress and replay

E01 `point-completed` events additionally contain `snapshot_version=e01-progress-v1`, point ID, lane, parent, and at most three finite observables (E, Q, radius) for accepted points. They are emitted after the completed point and checkpoint are saved. No field or eigenvector arrays are embedded. Failure events contain no reused prior-point observables. The existing event envelope supplies attempt identity and sequence; the existing cursor/deduplication logic handles replay and reconnect.

The progress view shows tasks across frequency, including rejected points and refinements, plus provisional E/Q scatter. It labels everything as provisional and displays the pending-task count, not a misleading fixed percentage for an adaptive queue. It does not read mutable artifacts or make scientific classifications. Interrupted attempts remain in the timeline; immutable results appear through normal analysis/report operations.

## Data contract, exports and performance

`contracts/research/exploration.schema.json` describes `plot-data/exploration.json`. The report packages exact scalar tables, selection/coverage evidence, source references and declarative view mappings: dataset, columns, units, filters, grouping, point identity, parent edges, uncertainty multiplier, and reference/threshold. The browser validates supported mappings and rejects malformed or non-finite rows. This is additional saved presentation data; existing E00 and static figure contracts remain compatible.

**Export reproducible view** downloads a JSON snapshot containing exact datasets and mappings, selected point/profile/sector, run/config/code identity, report/analysis IDs and cataloged artifact hashes. **Export comparison** records both runs and selections. Point/profile/sector preferences persist locally per run and report. These exports can be inspected or used for downstream reproduction; importing an exported view is not implemented.

Each chart's **Export SVG** produces a standalone figure with inline styling and embedded metadata for exact chart rows, range, display stride and provenance. Zoom is captured in SVG metadata; the whole-view JSON exports full data and selected point/profile/sector. There is no solver call during export.

Up to 4,000 display points are drawn before deterministic stride display sampling is applied (selected-point rows remain visible). Bounds use every in-range row, including numerical errors. At a display stride greater than one, connecting lines are omitted; sampling never invents a branch edge. Exact rows remain paginated and all data is exported. Profiles and report datasets are loaded on demand; research-scale arrays may require a future paged artifact service. No 3D reconstruction, time evolution or eigenfunction animation is claimed by this release.

## Validation

The inexpensive E01 integration test verifies profile counts, saved parent links, event-to-analysis E/Q agreement, bounded progress payloads and report/package verification with solver calls forbidden during reanalysis and reporting. Adapter tests cover disconnected/failed branches, lane filtering, linked point/sector filtering, numerical error multipliers and non-finite rejection.

`e2e/research-visuals.spec.ts` starts a real loopback runtime with two small E01 fixtures. It checks linked selection, spectra filtering, JSON/SVG downloads, five loaded saved figures, rendered reports, compatible overlays, switching runs, and narrow-screen layout. The existing browser suite covers interruption/resume, disconnected services, E00 and the historical workspace. Run `npm run check`, the built CLI sample, and `npm run test:browser` before merging.
