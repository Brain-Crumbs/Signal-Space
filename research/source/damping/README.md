# Signal Space charged-clock damping calculation

This is a new fixed-charge perturbation experiment about the equilibrium branch at Q=231.832883924705. It uses the same charged-sector equation as the supplied formation/radiation milestones. It is not a further restart of the original Cauchy data.

The results establish a weak outgoing linear resonance at Omega/m = 1.7285139600 - 1.43079689e-6 i. The dominant emitted power is quadratic in the small confined amplitude; the secondary negative-frequency harmonic is quartic. The full report distinguishes this mode-specific decay law from universal or arbitrarily late-time relaxation.

## Reproduce

Python 3 with NumPy (including numpy.trapezoid), SciPy, Matplotlib, and a C++17 compiler are required. No network access or external data is used.

```
OPENBLAS_NUM_THREADS=1 python run_all.py
```

This creates the initial binary data, compiles the C++ evolution, executes all 15 runs in at most three local processes, computes continuum/discrete poles and convergence tests, and regenerates the analyses, report, and figure. It took a few minutes on the original runtime; hardware changes runtime. Results and raw detector/ledger data are already included. To regenerate just the presentation from included results, run summarize.py, make_figure.py, and make_report.py in that order.

## Files and methods

- `resonance.py`: complex outgoing/evanescent shooting problem on the continuum stationary branch; even mode normalized to v(0)=1.
- `setup_scan.py`: exact discrete rotating backgrounds at equal charge, finite-energy resonance perturbation, one initial charge correction. The generated `.bin` inputs are reproducible and omitted from the distribution.
- `evolve_scan.cpp`: charged-sector drift–kick–drift update, equivalent even half-domain, no absorber or damping. Symmetry restricts this experiment to even perturbations.
- `discrete_resonance.py`: outgoing pole of the same spatial and temporal recurrence used by the evolutions.
- `analyze_scan.py`: harmonic fits, fluxes, envelope rates, energy/charge ledgers, and secular energy fits. `ground_correction.py` computes the small stationary energy-reference correction.
- `results/*_probes.bin`: raw detector history. Header: int32 count, then count float64 detector positions. Records: float64 time then 8 float64 values per detector: Re Phi, Im Phi, Re velocity, Im velocity, Re centered gradient, Im centered gradient, forward Re difference, forward Im difference. Native little-endian Linux layout. `analyze_scan.load` reads it.
- `results/*_ledger.csv`: raw full/core energy and charge, plus time-integrated lattice fluxes at the window-20 boundary. Units m=1, lambda=.01.
- `results/*_analysis.json`, `*_fit.npz`: measured fits at the stated temporal windows, raw and calibrated excitation energies, conservation errors, and harmonic currents.
- `results/amplitude_scan.csv`: compact numerical table.
- `results/summary.json`: final aggregated results, exponent fits, mode comparison, and stationary control diagnostics. `resonance_checks.json` and `discrete_resonance.json` retain convergence results.
- `inputs/parent_radiation_profiles.npz`: the actual spatial harmonics from the supplied Radiation Source archive, used only to compare the previous remnant with the new pole. Original relative path: `results/kick_fine_200_1000_profiles.npz`.
- `inputs/*.md`: supplied model and prior milestone reports. These are provenance inputs, not changed outputs of this calculation.
- `deliverables/`: new report and scientific figure.

The background frequency is selected from the previous remnant's mean core charge, not its excited carrier frequency. The matched pole is an independent calculation about the stationary solution. Seeding the pole profile isolates the mode for the amplitude test; the near-unit spatial overlap with the previous remnant supports the association but does not prove a global continuation or compute the finite-amplitude Floquet spectrum.

Do not interpret a fractional power-law slope fit as a statistical uncertainty estimate. Do not interpret finite-core quasinormal-mode energy as a globally normalizable resonance. The long e-fold time is inferred from the outgoing pole, not directly simulated. Generic other modes and continuum tails can change ultimate cooling.

`make_report.py` contains the benchmark interpretation alongside generated tables. A different charge or potential requires updating the derivation and narrative, not merely rerunning the template.
