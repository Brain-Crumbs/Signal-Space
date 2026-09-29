"""Evidence-derived narrative; scientific review remains separate."""

def assessment(manifest: dict, analysis: dict, checks: dict) -> str:
    """A conditional, evidence-derived assessment; not a human or AI review."""
    if manifest.get("experiment_id") == "gross.two-object-calibration.v1":
        lines = ["# Test 8 spatial calibration: automated assessment", "",
                 f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; classification {analysis['classification']}.",
                 "A short axisymmetric embedding pilot, not accepted two-object exchange.", "",
                 "| Locked check | Status |", "| --- | --- |"]
        lines += [f"| {c['id']} | {c['status']} |" for c in checks['checks']]
        lines += ["", "The pair is an unrelaxed superposition. Mesh and time steps change together; 100-period calibration, source-only controls, recoil, survival and Test 9 reconstruction remain open.",
                  "Inspect the PDFs and canonical arrays before using this as a prerequisite. Test 8 G0–G9 readiness is false."]
        return "\n".join(lines) + "\n"
    if manifest.get("experiment_id") == "gross.two-object-quiet-calibration.v1":
        lines = ["# Test 8 quiet calibration: automated assessment", "",
                 f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; classification {analysis['classification']}.",
                 "Six frozen periods with an accounted outgoing layer, not Test 8 exchange.", "",
                 "| Locked check | Status |", "| --- | --- |"]
        lines += [f"| {c['id']} | {c['status']} |" for c in checks['checks']]
        lines += ["", "Inspect independent mesh, timestep and domain differences, and the weak-mode-scale sink ledger.",
                  "Joint relaxation, 100-period longevity, both source channels, recoil and G0–G9 remain open."]
        return "\n".join(lines) + "\n"
    if manifest.get("experiment_id") == "gross.reception-acceptance.v1":
        lines = ["# Test 7 known-incident acceptance: automated assessment", "",
                 f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; classification {analysis['classification']}.",
                 "Scientific and visual review remain pending. All gates must pass to accept this new radial protocol.", "",
                 "| Locked check | Status |", "| --- | --- |"]
        lines += [f"| {c['id']} | {c['status']} |" for c in checks['checks']]
        lines += ["", "Known initial incident field, fixed local proper-time markers, and an unfitted fourth-order response are explicit protocol choices.",
                  "Previous surface-only failures remain unchanged. A pass supports Program 15.7 only within this calibrated radial sector.",
                  "Test 8 still requires its own two-object preparation, survival, exchange and recoil experiment."]
        return "\n".join(lines) + "\n"
    if manifest.get("experiment_id") == "gross.boundary-memory.v1":
        lines = ["# Test 7 causal boundary: automated assessment", "",
                 f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; classification {analysis['classification']}.",
                 "Scientific review and visual inspection remain pending.", "",
                 "| Locked check | Status |", "| --- | --- |"]
        lines += [f"| {c['id']} | {c['status']} |" for c in checks['checks']]
        lines += ["", "Complete two-site acquisition and causal exterior memory are tested with a new prospective event rule.",
                  "The old cutoff and retrospective markers remain diagnostic. No nonlinear clock forecast is performed.",
                  "A passing prerequisite permits a new nonlinear acceptance plan; failure or unresolved stops that stage.",
                  "Original Test 7 classification remains and Test 8 is blocked pending nonlinear acceptance."]
        return "\n".join(lines) + "\n"
    if manifest.get("experiment_id") == "gross.reconstruction.v1":
        lines = ["# Test 7 reconstruction: automated assessment", "",
                 f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; classification {analysis['classification']}.",
                 "Scientific review and visual inspection remain pending.", "",
                 "| Locked check | Status |", "| --- | --- |"]
        lines += [f"| {c['id']} | {c['status']} |" for c in checks['checks']]
        lines += ["", "Single-site observability and a separate two-site causal capture protocol are compared.",
                  "The conditional singular bounds use declared surface and input perturbation radii.",
                  "No nonlinear receiver was evolved. Original Test 7 remains failed and Test 8 remains blocked.",
                  "A controlled reconstruction method permits a fresh locked nonlinear forecast and acceptance review, not automatic promotion."]
        return "\n".join(lines) + "\n"
    if manifest.get("experiment_id") == "gross.reception-transfer.v1":
        lines = ["# Test 7 discrete-transfer assessment", "",
                 f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; classification {analysis['classification']}.",
                 "Scientific review and visual inspection remain pending.", "",
                 "| Locked check | Status |", "| --- | --- |"]
        lines += [f"| {c['id']} | {c['status']} |" for c in checks['checks']]
        lines += ["", "The full interval budget must resolve the second-to-fourth-order separation on both spectra.",
                  "The discrete inverse assumes known support and incoming preparation; no response coefficient is fitted.",
                  "Original Test 7 remains failed. Test 8 requires separate acceptance review.",
                  "Two-object recoil, invariance, gravity, angular stability and emergent spacetime remain untested."]
        return "\n".join(lines) + "\n"
    if manifest.get("experiment_id") == "gross.reception-order4.v1":
        lines = ["# Test 7 formal fourth-order follow-up", "",
                 f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; classification {analysis['classification']}.",
                 "Original Test 7 failed and retains its original result. The inspected-history amplitude comparison is diagnostic.",
                 "The new held-out radial waveform uses saved upstream records, locked predictions and local markers.",
                 "", "| Locked check | Status |", "| --- | --- |"]
        lines += [f"| {c['id']} | {c['status']} |" for c in checks['checks']]
        lines += ["", "A technical pass of this follow-up does not retroactively pass Test 7 or authorize Test 8.",
                  "Known-Z optical inversion is approximate; evaluate remaining spatial timing error before a two-object protocol.",
                  "No two-object recoil, coordinate invariance, gravity or emergent spacetime is tested."]
        return "\n".join(lines) + "\n"
    if manifest.get("experiment_id") == "gross.reception.v1":
        lines = ["# Test 7: surface-only reception assessment", "",
                 f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; classification {analysis['classification']}.",
                 "", "Scientific interpretation and visual review remain pending.", "",
                 "| Check | Status |", "| --- | --- |"]
        lines += [f"| {c['id']} | {c['status']} |" for c in checks['checks']]
        lines += ["", "Surface-only inversion and time-dependent Taylor predictions precede the held-out nonlinear receiver.",
                  "Local threshold markers define an interval; the quiet history at those times is a counterfactual reference.",
                  "Radial origin reflection supplies opposite propagation directions. No recoil or observer invariance is claimed.",
                  "Next: resolve any failed interval or numerical gate before Test 8. If accepted, register two surviving objects and conservation of exchanged momentum."]
        return "\n".join(lines) + "\n"
    if manifest.get("experiment_id") == "gross.router-propagation.v1":
        return router_assessment(manifest, analysis, checks)
    if manifest.get("experiment_id") == "gross.full-spectrum.v1":
        return floquet_assessment(manifest, analysis, checks)
    if manifest.get("experiment_id") == "gross.continuum-action.v1":
        lines = ["# Test 5 continuum action: automated assessment", "",
                 "Scientific interpretation and visual review remain pending.", "",
                 f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; bounded classification {analysis['classification']}.", "",
                 "| Check | Status | Value |", "| --- | --- | --- |"]
        lines += [f"| {c['id']} | {c['status']} | {c.get('value')} |" for c in checks['checks']]
        lines += ["", "The common matter cone is selected by the action. Frozen local jets do not establish emergence, a bound clock, nonlinear Einstein evolution or constraint-satisfying initial data.",
                  "", "Next: Test 6 core profile and independently resolved bound clock eigenmode; require branch and finite-domain convergence before reception work."]
        return "\n".join(lines) + "\n"
    if manifest.get("experiment_id") == "gross.bound-clock.v1":
        lines = ["# Test 6 bound clock: automated assessment", "",
                 "Human scientific interpretation and visual review remain separate.", "",
                 f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; bounded classification {analysis['classification']}.", "",
                 "| Check | Status | Value |", "| --- | --- | --- |"]
        lines += [f"| {c['id']} | {c['status']} | {c.get('value')} |" for c in checks['checks']]
        lines += ["", "This is a spherical flat decoupling calculation. An accepted radial lifetime does not establish nonspherical stability, gravity, reception or emergent geometry.",
                  "", "Next: if accepted, freeze the local clock calibration and preregister Test 7 incident neutral pulses and predicted local response before measuring reception; otherwise resolve the failing branch, mode or lifetime gate."]
        return "\n".join(lines) + "\n"
    if manifest.get("experiment_id") in ("gross.clock-longevity.v1", "gross.clock-response.v1"):
        lines = ["# Test 6 prerequisite: automated assessment", "",
                 "Scientific interpretation and visual review remain pending.", "",
                 f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; classification {analysis['classification']}.", "",
                 "| Check | Status |", "| --- | --- |"]
        lines += [f"| {c['id']} | {c['status']} |" for c in checks["checks"]]
        lines += ["", "Frozen radial profiles; no nonspherical beam, recoil, gravity or emergent spacetime claim.",
                  "The concentric-shell response uses an ideal local clock probe. Historical energy diagnostics do not resolve tiny clock radiation.",
                  "Next: inspect numerical and tick-shift errors, then specify upstream-characteristic-only prediction and physical marker events before a two-object link."]
        return "\n".join(lines) + "\n"
    classification = manifest["scientific_classification"]
    reciprocal = manifest.get("experiment_id") == "gross.reciprocal-events.v1"
    next_step = (
        "Proceed to Test 3 exact-router dispersion with orthogonal, oblique and collinear triads, reversed order and full-zone inspection; keep physical memory modes for Test 4 and directional controls for Test 11."
        if classification == "pass" and reciprocal else
        "Proceed to the Test 2 reciprocal-event conservation derivation; Test 5's action audit is an independent branch."
        if classification == "pass" else
        "Resolve the failed, unresolved or unevaluated checks before using this run to support the next experiment."
    )
    lines = ["# Experiment analysis and next calculation", "",
             "Automated assessment from saved checks. Scientific interpretation and visual review remain pending.", "",
             f"Run: `{manifest['run_id']}`. Analysis: `{analysis['analysis_id']}`.",
             f"Scientific classification: **{classification}**.", "",
             "| Check | Status | Measured value |", "| --- | --- | --- |"]
    lines += [f"| {c['id']} | {c['status']} | {c.get('value', 'not reported')} |" for c in checks["checks"]]
    lines += ["", "Evidence: `results/tables/checks.json`, `results/tables/analysis.json`, and the exact plotted data in `results/data/plot-data/`.",
              "", "## Meaning and limits", "",
              ("The checks audit a finite reciprocal circuit, its conserved matrix ledger, permissible scheduling and causal Jacobian. Exact-solution and half-tolerance comparisons control integration error. Flat transport and U(2) covariance do not establish Lorentz covariance, mechanical recoil, a clock or an emergent metric. Spatial boundary and continuum convergence are not evaluated because no spatial mesh is supplied."
               if reciprocal else "The checks test algebra and its numerical implementation in the locked conditioning domain. They do not establish physical propagation, clock behavior, or emergent spacetime. Finite sampling does not replace an exact proof."),
              "", "## Next calculation", "", next_step, "",
              ("Competing signatures for the next calculation: long-wavelength dispersion follows the projector Gram matrix; collinear triads become degenerate; reversed order changes finite-band terms. Do not hide stationary memory modes or identify the circuit labels with measured spacetime."
               if reciprocal else "The next discrimination is whether the specified reciprocal update conserves its declared aggregate under permissible event rescheduling. Derive the invariant and ordering assumptions before coding that dynamics."),
              "", "Review every figure and its limitations before promoting the result to a research conclusion."]
    return "\n".join(lines) + "\n"


def router_assessment(manifest: dict, analysis: dict, checks: dict) -> str:
    status = manifest['scientific_classification']
    lines = ['# Router propagation: analysis and next calculation', '',
             'Automated assessment; scientific interpretation and visual review remain pending.', '',
             f"Run: {manifest['run_id']}. Analysis: {analysis['analysis_id']}. Classification: **{status}**.", '',
             '| Check | Status | Value |', '| --- | --- | --- |']
    lines += [f"| {r['id']} | {r['status']} | {r.get('value')} |" for r in checks['checks']]
    lines += ['', 'Evidence: results/tables/checks.json and results/data/plot-data/.', '',
              'This audits the homogeneous zero-wave linear router: supplied incidence, frozen background projectors, two wave bands. The Gram cone is predicted before execution; no metric fit is used. Collinear rank loss and order reversal are physical controls.', '',
              'Conservation means total wave amplitude norm. Periodic boxes check the explicit shifts; exact blocks have no PDE timestep or outgoing boundary. Group derivatives exclude band touchings, which remain in the saved spectrum. Extra full-zone nodes are detections, not a completeness or particle-species claim.', '',
              'No autonomous clock, invariant detector record, full-sector metric or emergent spacetime is established. Stationary physical memory modes are not removed from the full model. Finite-band directional asymmetry is not a leading identity drift.', '',
              ('Next: Test 4 complete zero-wave tangent spectrum, retaining stationary memory variations. A common-cone claim predicts all physical sectors; the known zero-wave obstruction instead predicts propagating waves plus physical stationary memory. A nonzero periodic background requires its own self-consistent full-circuit solution and a separately locked plan.'
               if status == 'pass' else 'Resolve the failed or incomplete checks before drawing a wave-cone conclusion; preserve this run and its thresholds.'), '',
              'Test 11 spectral diagnostics are preliminary here; operational drift tests still require an accepted clock and description-invariant local record.']
    return '\n'.join(lines) + '\n'


def floquet_assessment(manifest, analysis, checks):
    lines = ['# Full reciprocal spectrum: analysis and next calculation', '',
             'Automated assessment; visual and scientific review remain pending.', '',
             f"Run {manifest['run_id']}; analysis {analysis['analysis_id']}; classification {analysis['classification']}.", '',
             '| Check | Status | Value |', '| --- | --- | --- |']
    lines += [f"| {c['id']} | {c['status']} | {c.get('value')} |" for c in checks['checks']]
    lines += ['', 'Evidence: results/tables/checks.json and results/data/plot-data/summary.json.', '',
              'Twenty physical real tangent dimensions include twelve memory orientations. Only unobservable memory spinor phases are removed. Vacuum and equal-port backgrounds have physical stationary memories; the opposing-port background tests genuine backreaction. Failures of the strong cone criterion are scientific outcomes, not pipeline failures.', '',
              'The six-gate routing is an explicit additional incidence assumption, not a nonlinear extension proven equivalent to the Test 3 reduced stencil. Floquet growth and tangent norms are not kinetic energy or a nonlinear stability theorem. Degenerate eigenspaces have basis-dependent mode participation.', '',
              'Test 11: paired spectral sectors exhibit routing-derived drift. They are not invariant clock records; a common coordinate drift cannot eliminate a difference between port-sector drift vectors.', '',
              'Next: derive a non-collinear, unequal-port periodic background with active memory response, then preregister its complete tangent and stability tests. A shared-cone candidate must predict withheld memory and port sectors; the alternative requires a derived material response and autonomous clock, not a new label for unexplained modes. Generic backgrounds, clocks and emergent spacetime remain unresolved.']
    return '\n'.join(lines) + '\n'

