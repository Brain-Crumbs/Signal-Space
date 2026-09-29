# Signal Space charged-clock formation calculation

This archive contains the report, model and stability specifications, C++ evolution source, Python analysis/plotting scripts, all 99 executed time histories and their metadata, and selected raw field data. Results are classical numerical calculations, not empirical measurements or quantum predictions.

## Reproduce

Requirements: C++17 compiler (`g++`), Python 3 with NumPy, SciPy, Matplotlib. No additional data or network access is needed.

```bash
OPENBLAS_NUM_THREADS=1 python run_all.py
```

This rebuilds and reruns every simulation. It writes raw fields, histories and `analysis.json` under `results/`, then regenerates the Markdown report, scan CSV and figures under `deliverables/`. It uses up to four subprocesses and approximately a few GB of working storage. Long fine-grid evolutions dominate runtime. CPU-dependent last digits are not physically meaningful.

For one independent run:

```bash
g++ -O3 -std=c++17 evolve.cpp -o evolve
./evolve results/example .9 2 .9 .05 .01 800 gauss 0
python analyze.py example
```

The arguments are prefix, target omega, width ratio, initial nu, dx, dt, duration, mode, neutral-energy fraction; reception/readout modes also take a source final-state file, optional phase and separation. A negative neutral fraction means two symmetric incident packets with that total absolute energy fraction; it is not negative energy. The executable uses lambda=0.01 and epsilon=0.1.

## Files and conventions

- `evolve.cpp`: prescribed local Hamiltonian split evolution, finite domain, diagnostics and flux integration.
- `run_*.py`: exact experiment declarations; `run_all.py` runs them in dependency order.
- `analyze.py`: phase, charge, energy, profile, window and conservation diagnostics. A single-core phase/profile fit is explicitly inapplicable to two-object readout runs.
- `make_figures.py`, `make_report.py`: regenerate the presentation from the analysis/results. Narrative statements and selected rounded ledger entries in the report template refer to this executed benchmark; changing model parameters requires updating that narrative.
- `results/*.csv`: full time histories. Original non-benchmark scans may have instantaneous fluxes only; final benchmark and refinement histories also have per-step integrated fluxes.
- `results/*_meta.json`: mesh, domain, preparation, duration and packet metadata.
- `results/analysis.json`: full derived statistics; the final stdout summary is in `analysis_stdout.txt`.
- `results/*_snap.bin`: selected snapshot files. Native little-endian int32 node count, float64 dx, then records containing time and four float64 arrays: Re Phi, Im Phi, Re Phi_t, Im Phi_t. Snapshot x runs from -120 to 120. This archive preserves snapshots for the displayed long-run and readout figures.
- `results/*_final.bin`: selected full-domain Cauchy data. int32 node count, float64 dx, then the same four arrays; x=(index-N//2)*dx. Formed-core reception/readout source states are included for both meshes.
- Neutral a/b fields are evolved internally; their energies and total momentum are recorded in the histories. They are not included in the structural snapshot format.
- `inputs/`: exact model and stability specifications supplied with the task.
- `deliverables/`: report, 48-case scan CSV, and three scientific figures.

The source was executed with the versions listed in `environment.json`. Native compiled executables are excluded; compile locally. Snapshots not bundled regenerate with `run_all.py`.

The initial 48-case scan preceded adding per-time-step cumulative flux logging. Rerunning the final source therefore improves flux quadrature for those exploratory cases without changing their field evolution or total-conservation results. Two incomplete buffered diagnostic outputs encountered during generation were rerun; the delivered histories and selected/full raw outputs were checked for valid shape and the declared final time.

The main formation result is from nonstationary charged Gaussians, several of which are already below the free-wave threshold. Above-threshold preparations and unfinished relaxation are separately identified. No vacuum noise, friction, absorption, or analytic-profile reset is used to create the reported formed objects.
