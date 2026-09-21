# Running E01: charged recurrence branch and stability

Issue [#39](https://github.com/Brain-Crumbs/Signal-Space/issues/39) implements the [preregistered protocol](first-experiment.md). The experiment is available; the author launches the research scan. Implementation validation uses small controls only and supplies no research finding.

## Launch from the local workspace

Follow the [README setup](../../README.md#quick-start), start Vite and the loopback runtime, and connect using its printed token.

1. Select **E01 · 3D charged recurrence branch and stability**.
2. Load **Author research run (opt-in)**. Loading the preset does not run anything.
3. Review the frequency interval, seed radii, resource budget, angular sectors and refinement settings. Acceptance thresholds are fixed in the schema.
4. Choose **Validate & estimate**, then **Validate & start run** when ready.
5. Follow point events and attempts in Run audit. Cancel/resume retains completed tasks and pending continuation work.
6. Analyze saved output, regenerate the report, and download the reports, figures and data from the artifact catalog.

The initial selection uses a **Small validation fixture** instead. It executes three nearby frequencies with a deliberately coarse spectrum and no refinement; its scientific outcome is always `unresolved`. The E00 interactive recurrence overlay is not used for E01; E01 has its own linked visual explorer in Run audit and a saved figure gallery in Reports. Analyze and regenerate a report to enable the explorer for older runs. See [Visual research workspace](visual-exploration.md).

## Headless launch and reproduction

From the repository root, with the pinned Python environment active:

```sh
npm run research -- validate --config fixtures/research/e01-research.json
npm run research -- estimate --config fixtures/research/e01-research.json

# Author launches the actual scan here:
npm run research -- --workspace .research-work run --config fixtures/research/e01-research.json
```

The research preset covers `0.875 <= omega/m <= 0.995`, seeded at `0.94` in both directions, with three trial widths. It keeps both sides of any resolved charge minimum. Endpoints of the mathematical existence interval are excluded. All three frequency fields enforce the schema's exclusive lower bound `0.8660254037844387` (the conservatively rounded boundary); equality is rejected. The preset is a starting numerical ladder, not a promise of a resolved candidate: insufficient mesh, domain, continuation or spectral accuracy yields an explicit unresolved result. Estimates are conservative scaling estimates, not timing guarantees; the default research estimate is several CPU hours and tens of GB of reserved output budget. Verify disk space and use the resource fields to bound execution. A changed configuration creates a new run.

Use the returned run ID for the remaining commands (replace `RUN_ID`):

```sh
npm run research -- --workspace .research-work status --run-id RUN_ID
npm run research -- --workspace .research-work cancel --run-id RUN_ID
npm run research -- --workspace .research-work resume --run-id RUN_ID
npm run research -- --workspace .research-work analyze --run-id RUN_ID
npm run research -- --workspace .research-work report --run-id RUN_ID
npm run research -- --workspace .research-work verify --run-id RUN_ID
npm run research -- --workspace .research-work archive --run-id RUN_ID
```

Archive verifies the package and writes `research/experiments/e01-charged-branch/RUN_ID/`, updating the catalog. Reanalysis and report regeneration create new linked artifacts; they never call the stationary solver. Reproduction uses the saved `resolved-config.json` and recorded code/dependency identities. Resume requires those identities to match. In-flight solves restart from their last completed task; a checkpoint is not a claim to preserve an internal LAPACK iteration.

## Source-to-code mapping

| Source section / equation                       | Implementation                                                          | Independent controls                                                                                     |
| ----------------------------------------------- | ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| §§2–3,14: action, dimensions, eta/lambda_4/zeta | `models/charged_scalar.py`, closed `contracts/research/e01.schema.json` | Fixed benchmark, strict interval, units and neutral-parameter rejection                                  |
| §§5,7–8: E, Q, radius, radial equation          | `numerics/charged_radial.py`                                            | Exact Gaussian integrals; physical `1/lambda` normalization; vacuum rejection                            |
| §8: regular origin, spherical vacuum tail       | Singular `solve_bvp` term, `models/charged_scalar.py:tail`              | Origin expansion, independent exterior integration, Robin normalization                                  |
| §§7,9: virial and dE/dQ                         | `analysis/charged.py`                                                   | Saved-field five-point derivatives; Simpson/trapezoid quadratures; independent frequency-step lane       |
| §10: coupled fixed-charge spectrum              | `numerics/charged_spectrum.py`                                          | Analytic free-field frequencies, original-equation residuals, charge constraint, phase/translation modes |
| §§10,23: breakup and selection                  | `analysis/charged.py`                                                   | Connected branch segments, signed-charge allocations, allocation refinement, explicit error margins      |
| §15: regulator responsibility                   | Separate consistent spectral stationary regulator                       | Mesh/volume background comparison, independent spectral basis refinement                                 |
| §23: reproducible branch study                  | `experiments/charged_worker.py`, `reporting/charged.py`                 | Point-level cancellation/resume, immutable raw inputs, solver-free reports                               |

Paths above are relative to `python/signal_space/` except the schema.

## Numerical decisions and limits

The branch solver uses SciPy 1.17.0 singular-origin collocation and a spherical Robin condition. Independent residuals use five-point derivatives of saved uniformly sampled field values, including the regular even origin stencil. Observables use Simpson quadrature with trapezoidal comparison and analytic exterior corrections. Exterior nonlinear terms have a saved bound. The virial and energy identities share integrals and must not be counted as independent confirmations.

Each accepted seed has its own branch identity. Numerically coincident seeds are recorded as duplicates within each continuation lane. Successful steps grow back toward the declared maximum; failed steps are halved. A large relative profile jump is an ill-conditioned point. A minimum step failure is an unresolved endpoint. There is no pseudo-arclength fallback: a frequency fold is explicitly unresolved rather than bridged by disconnected solutions. Charge turning points are separately marked in derivative tables.

The base and half-frequency-step lanes are separate connected traversals. Every base point schedules independent spacing, outer-volume, nonlinear-tolerance and spectral-basis tasks. Volume changes preserve approximately the baseline spacing. All failed controls remain in the raw branch record. The point budget includes both lanes and seed failures; exhausting it leaves the pending queue visible.

Spectra use `w=rU,z=rV`, so the Euclidean radial measure is the physical `r^2 dr` measure. The regular Dirichlet extension of the transformed operator includes `ell(ell+1)/r^2`. The stationary action is separately solved on this finite spectral mesh to preserve its exact discrete U(1) phase mode and first-order charge invariant. Its difference from the collocation profile is measured, not silently substituted into the independent E/Q ledger. A null-space basis enforces `integral(4 omega f U - 2 sigma f V) d^3x=0` in the radial sector. Higher angular sectors satisfy the integrated constraint by angular orthogonality.

A full dense eigensolve saves every eigenvalue/eigenvector and checks residuals against the **original** coupled generator, exposing any projection leakage. No truncation, shift or iterative eigensolver tolerance is hidden; the solver is double-precision LAPACK, and its residual target is fixed at `1e-7`. Phase and translation splittings, low-mode matching, background error and mesh/domain changes are reported. Each low, symmetry or positive-growth mode is matched one-to-one across mesh and volume refinements. Growth and symmetry splitting use that mode's own maximum mesh/domain shift, with a `1e-12` numerical floor; the largest shift across modes is only a general convergence check. An unmatched growing mode in a refinement leaves stability unresolved. Mode indices, partners and individual error budgets are saved in `spectral-budgets.json`. A positive pointwise lower bound on both stiffness operators at the next angular sector bounds all higher sectors: the centrifugal contribution increases with ell and the gyroscopic term does no work. The bound uses conservative Hermite interval amplitude bounds and the monotone exterior tail. If the bound or refinements do not resolve, angular coverage stays unresolved.

Breakup uses independently resolved samples and parent-connected branch segments. It includes positive and charge-conjugate fragments, free-charge remainder, exact sampled one- and two-fragment combinations, and a piecewise-linear lower envelope for up to the configured number of fragments. Charge allocation is repeated at doubled resolution. Its uncertainty includes measured branch interpolation error, both objects' numerical errors and a conservative charge-grid snapping allowance. It does not extrapolate across a missing branch interval. A finite seed search never proves every possible branch was discovered.

There is no positive energy gap against emission of arbitrarily soft free charge: the no-emission channel approaches the parent energy. Finite one-fragment emission is checked separately from this limit: on each connected piecewise-linear branch, the exact extrema of `E(q)+|Q-q|` occur at endpoints or the interior kink `q=Q`. All finite sampled jumps, conjugates and distinct branches at equal charge remain eligible; only the positive-sign parent record itself is excluded as the identity. On an edge incident to the parent, the affine margin is controlled by its other endpoint and the local soft-emission slope `dE/dQ=omega<m`; no positive uniform gap is asserted as the emitted charge tends to zero. Disconnected samples still supply discrete channels but cannot establish continuous coverage. The exact finite fragment count and sampled frequency/charge scope accompany every selection.

Classification is `candidate`, `no-candidate`, or `unresolved`, mapped to the common manifest's `pass`, `fail`, and `unresolved`. A numerical failure is never a scientific negative result. Stationarity, binding below tested thresholds and linear stability within tested sectors are separate per-point criteria. Top-level pointwise checks summarize all sampled base points: any resolved failure gives `fail`, all passes give `pass`, and missing evidence gives `unresolved`. Each check lists point IDs by status. The separately preregistered `selection` check expresses whether at least one candidate exists; thus a candidate can coexist with failed criteria at other points, and a fully resolved `no-candidate` retains its failing evidence even when different points fail for different reasons. No nonlinear stability, global minimum, longevity, particle identity, Hopf or gauge claim is made.

## Saved artifacts

Raw point JSON records contain profiles, derivatives, original collocation polynomials, tangents, solver diagnostics and spectra. Compressed NPZ files contain complex eigenvectors as separate real/imaginary arrays, indexed in eigenvalue order. The latest raw `branch.json` contains the exact completed record list and pending tasks; checkpoints duplicate the continuation state with provenance hashes.

Analysis produces branch, derivative, convergence, interpolation, charge-allocation convergence, spectrum and breakup CSV tables; spectral/background/error budgets; failed/pending records; and a machine-readable selection with criterion evidence paths. Reports include exact plot data, figure specifications, PNG/SVG/PDF figures and Markdown/HTML/paginated PDF reports. Failed and unfinished tasks remain visible even when the worker technically completes.
