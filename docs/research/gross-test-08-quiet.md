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

Use Python 3.12+ in a clean checkout. The separately locked optimized preset below retains the same physical protocol and thresholds, selects the strict compiled/full-neutral backend, and changes checkpoint cadence while retaining all original resource ceilings. Its execution is pending:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-performance-lock.txt
python .agents/scripts/experiment_contract.py plan docs/research/plans/gross-test-08-quiet-optimized.json
python .agents/scripts/run_plan.py --plan docs/research/plans/gross-test-08-quiet-optimized.json --repo-root . --workspace ../test8-preflight --case-jobs 2
git status --short
python scripts/run-test8-local.py --recipe gross-test-08-quiet-optimized --case-jobs 2 --output ../test8-quiet-001
```

The preflight performs validation and an estimate **without evolution**. The final command runs the explicitly selected locked operational preset, independently analyzes saved data, renders figures/PDFs, verifies canonical and reader packages together, checks the outer file index, and produces two ZIPs and `pr-evidence-index.json` outside the Git checkout. It never commits or pushes. The existing CPU/wall projection is 4,816 CPU seconds and 5,473 wall seconds; it is not a measured compiled-backend timing. The new preset estimates 324 MiB retained output in serial or 466 MiB with parallel child evidence, within the unchanged 512 MiB ceiling. The 4 GiB memory ceiling is shared by the coordinator and admitted cases. Reserve additional room for packages and dependency installation. A technical interruption preserves the partial directory and logs. The [CPU backend and quiet restart implementation](test-08-performance-implementation.md) supports checkpointed continuation in a new attempt. The original plan remains available but its default retained-checkpoint estimate is 1,011 MiB and is rejected by preflight. `--package-only` verifies and packages a completed output without running physics again.

For live per-case progress, checkpoint-and-stop, failed-stage recovery, measured
profiles and verified handoff, follow the [campaign workbench guide](campaign-workbench.md).
The wrapper accepts `--resume` and defaults to the optimized recipe. JSON events
now include nested parallel workers; use `status --watch --human` for the terminal
view. `pipeline --resume` recovers failed analysis/report/export without repeating
completed evolution.

## Results PR handoff

Inspect the canonical checks, figure interpretations and both PDFs. Upload the
unchanged paired ZIPs from `OUTPUT/handoff/` to durable external artifact storage;
record that locator and the compact `pr-evidence-index.json` in the results PR.
Verify a fresh download with `signal-space import`. Follow the
[artifact contract](artifact-contract.md); repeated binary exports do not go into
Git/LFS by default, and existing archived bytes remain untouched.

Update reviewed results and the evidence-linked `gross-progress.json` only when
new evidence supports a status change, then regenerate `gross-current.md`.
Report exact check outcomes and remaining G0–G9 gates. Packaging and PR review do
not establish acceptance. Keep issue #82 open while any required gate remains
unresolved or not evaluated.

The calibration can end in `fail` or `unresolved` while producing valid evidence. Passing short numerical checks only allows design of 100-period calibration and later source-only feasibility; it cannot preselect neutral/structural amplitudes or freeze held-out exchange choices from a nonexistent receiver result.
