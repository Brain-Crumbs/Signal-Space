# Test 8: local outgoing-layer and quiet-pair qualification

This separately registered prerequisite is `gross.two-object-quiet-calibration.v1` under the unchanged flat axisymmetric SS OCF 1 action. It follows the [16-unit spatial pilot](gross-test-08-calibration-results.md) and [issue #82](https://github.com/Brain-Crumbs/Signal-Space/issues/82). It is **not** the two-object exchange experiment or a declaration of Test 9 readiness.

## Locked question and preparation

Can the frozen Test 6 radial profile and clock be embedded as isolated and two-center spatial data for six signed-field periods, with a measured outgoing-layer sink and separately varied spatial grid, timestep and domain? The competing explanations are usable quiet clocks or drift from superposed preparation, numerical error and outer-boundary reflections.

Freeze $\omega_Q=0.900$, $\Omega_\chi=0.41274991$, local peak $\chi=0.001$, the source byte hash and separation $d=72$. The pair starts from a naive superposition at $z=\pm36$, with $a=\pi_a=0$. The free evolution may settle, move and radiate. No pins, externally imposed worldline or subsequent reset are applied. A genuinely prepared joint pair and 100-period isolated/quiet survival remain separate issue gates. The fixed-direction doublet reduction, annular measure and Hamiltonian are specified in [the first spatial protocol](gross-test-08.md).

In a declared outer layer, add $-\gamma\Pi$, $-\gamma p_\chi$, and $-\gamma\pi_a$ to the canonical momentum derivatives only. Here $\gamma$ is the maximum of cosine-squared radial and axial ramps, from zero at the inner edge to 0.12 at the reflecting outer face. The base box is $\rho<24$ with axial half-length $32$ (isolated) or $64$ (pair), width $4$; the larger-domain pair has $\rho<32$, axial half-length $80$, width $6$. The absorber is a declared numerical intervention, not a term in the SS OCF 1 action. It may backscatter; its adequacy is judged by the larger-domain control. Its continuum instantaneous energy and charge sinks are

```math
\dot E_{\rm sink}=\int\gamma\left(2|\Pi|^2+p_\chi^2+\pi_a^2/Z\right)d^3x,
\qquad \dot Q_{\rm sink}=\int\gamma j^0\,d^3x.
```

Both sinks are integrated with the same RK4 stages. Direct total Hamiltonian and charge are recomputed separately at saved times. The energy residual is normalized to the **initial projected clock-mode energy**, avoiding a small clock error hidden by core rest energy. A physical exchange experiment additionally needs measured local stress flux and axial momentum sinks; this short quiet study does not implement recoil.

The frozen mode is projected in a nonoverlapping region around each measured charge centroid. Positive-going projected-field crossings measure the short clock frequency and jitter; the local axis field is extrapolated from the first two annular cells. The projection is a diagnostic: a new embedded eigenproblem, mode isolation, axial interpolation and tracked timelike local events are still required before Test 8 reception acceptance.

Six locked cases are isolated and pair at $h=.2,.1$ with $\Delta t=.01,.005$, pair at $h=.2,\Delta t=.005$ for independent time error, and pair in a larger box at $h=.2,\Delta t=.01$. The fine grid changes both $h$ and $\Delta t$, so spatial error is not isolated by that comparison alone. The locked checks require source identity, exact neutral null, sink-corrected energy residual <1% of initial projected mode energy and charge residual <1%, distinct pair centroids, six-period readable clock diagnostics, and <5% relative base-amplitude trace changes in the three controls. A failed or unresolved short check blocks promotion. The 100-period and full-exchange checks remain unresolved/not evaluated by construction.

## Run on your machine

Use Python 3.12 in Linux or WSL2. On an implementation branch after its PR is merged, from a clean checkout:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r python/requirements-lock.txt
python .agents/scripts/experiment_contract.py plan docs/research/plans/gross-test-08-quiet.json
python .agents/scripts/run_plan.py --plan docs/research/plans/gross-test-08-quiet.json --repo-root . --workspace ../test8-preflight
git status --short
python scripts/run-test8-local.py --output ../test8-quiet-001
```

The preflight performs validation and an estimate **without evolution**. The final command runs the unchanged locked configuration, independently analyzes saved data, renders figures/PDFs, verifies canonical and reader packages together, checks the outer file index, and produces two ZIPs and `pr-evidence-index.json` outside the Git checkout. It never commits or pushes. The case estimate is roughly 4,816 CPU seconds, 1,378 MiB memory and 142 MiB uncompressed output under 7,200 CPU seconds, 8,000 wall seconds, 4 GiB memory and 512 MiB output ceilings. These are preflight estimates rather than timing measured on your machine. Reserve additional room for packages and dependency installation. A technical interruption preserves the partial directory and logs. The new [CPU backend and quiet restart implementation](test-08-performance-implementation.md) supports checkpointed continuation in a new attempt; its retained-state estimate supersedes the original disk estimate above. The old default checkpoint cadence now exceeds the locked output ceiling, so select and prospectively lock an explicit execution configuration before a new physical run. `--package-only` verifies and packages a completed output without running physics again.

During the long `run-plan` stage, inspect `../test8-quiet-001/evidence/status.json` and the `scenario-progress` events in `../test8-quiet-001/evidence/runs/gross.two-object-quiet-calibration.v1/<run-id>/attempts/attempt-0001/events.jsonl`. The command returns only after all six cases and packaging complete; an `unresolved` or `fail` **scientific** classification still yields the paired ZIPs.

## Results PR handoff

After inspecting `evidence/status.json`, checks, figures and both PDFs, create a **new results branch**. Copy both generated ZIPs and `pr-evidence-index.json` into `research/experiments/gross.two-object-quiet-calibration.v1/packages/`. Keep the archives as a paired immutable unit; do not independently repack one or edit inside it. For a ZIP over 50 MiB, install and configure Git LFS for this specific package path **before** `git add`; confirm the remote repository permits the transfer. Verify a fresh checkout downloads real ZIP data rather than LFS pointer text. Update reviewed results and `gross-progress.md` with measured values, status and remaining G0–G9 gates. Then run `npm run research:manifest`, repository checks and `git diff --check`, commit and open your PR into `main` referencing issue #82 without closing it unless all its gates have passed.

```sh
git switch -c research/test8-quiet-results
mkdir -p research/experiments/gross.two-object-quiet-calibration.v1/packages
cp ../test8-quiet-001/*.zip ../test8-quiet-001/pr-evidence-index.json \
  research/experiments/gross.two-object-quiet-calibration.v1/packages/
# If either ZIP exceeds 50 MiB, do this before git add:
# git lfs install
# git lfs track 'research/experiments/gross.two-object-quiet-calibration.v1/packages/*.zip'
npm run research:manifest
npm run check
git diff --check
git add .gitattributes research/experiments/gross.two-object-quiet-calibration.v1 \
  research/archive-manifest.json docs/research/gross-progress.md
git commit -m "Archive local Test 8 quiet calibration evidence"
git push -u origin research/test8-quiet-results
# Open a PR from this branch into main in GitHub or with gh pr create.
```

If `.gitattributes` has not changed, omit it from `git add`. Add any reviewed results Markdown you create to the commit. The two archives and index alone establish provenance and packaging, not scientific acceptance; put the exact check outcomes and your interpretation in the PR description.

The calibration can end in `fail` or `unresolved` while producing valid evidence. Passing short numerical checks only allows design of 100-period calibration and later source-only feasibility; it cannot preselect neutral/structural amplitudes or freeze held-out exchange choices from a nonexistent receiver result.
