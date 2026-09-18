# Signal Space charged-clock radiation calculation

This package continues the previously formed excited object, resolves its field harmonics, reconstructs outgoing radiation from the measured nonlinear source, and compares energy and charge fluxes with the core's measured relaxation.

The report distinguishes a measured weak leakage rate from a lifetime extrapolation. This is a classical calculation in a supplied spacetime and field theory. No quantum emission, coherence, electric charge identification, or emergent geometry is claimed.

## Reproduction

Requirements: C++17 compiler (`g++`), Python with NumPy, SciPy, Matplotlib. The input state is included; network access is unnecessary.

```bash
OPENBLAS_NUM_THREADS=1 python run_all.py
```

The script compiles the evolution program, runs three continuations in up to three local processes, extracts spectra and source overlaps, checks FFT cross-spectra and energy/charge ledgers, and regenerates the Markdown report and PNG figure. Expect several minutes and roughly 1 GB of temporary space for dense field histories; speed depends on the machine. Diagnostic results are already included.

## Provenance and scope

`inputs/excited_state.bin` is the actual final Phi/Phi_t Cauchy data from the earlier fine-grid `unbound_settled_fine` formation run at t=2400, not a fitted profile. `formation_metadata.json` gives its original preparation and grid. The parent model specification is also included. The state came from Signal_Space_Formation_Source.zip, previously saved with the formation milestone.

The continuation preserves the fields for |x|<1150 and tapers only the distant outer 50 units of the |x|<=1200 domain. The measurement region cannot be reached by that preparation change during the 1000-unit run in the continuum domain of dependence. All three resolutions use this same saved state, so the refinement concerns the continuation and analysis rather than a rerun of the original formation.

The a=0 field stays zero exactly, so this executable evolves only its invariant charged sector. There is no damping, random seed, absorber, neutral bath or center constraint.

## Included outputs

- `results/*_probes.bin`: complete 0.1-spaced detector histories for the final three runs.
- `results/*_ledger.csv`: full-domain energy/charge and core windows 20/40/60. Full energy includes both boundary bonds.
- `results/*_spectrum.json`: fitted carrier/modulation and chirps, component norms, outgoing/incoming amplitudes, fluxes, cancellation ratios, and source-to-detector comparisons.
- `results/*_profiles.npz`: complex spatial field and nonlinear-source harmonic coefficients, detector coefficients and fit parameters. These preserve the scientific spatial results without requiring the large dense intermediate histories.
- `results/*_diagnostics.npz` and `diagnostics.json`: FFT cross-spectra, excess-energy histories, source integration and validation statistics.
- `deliverables/`: report and verified scientific figure.

The original pilot sampling of integer-time fields was replaced by kick-position sampling for source reconstruction. Only the final kick-position data and outputs are bundled. Repeated evolutions used to check the boundary-energy ledger are not independent physical preparations; the final source computes the complete ledger in the main runs.

## Binary formats

All stored arrays are little-endian/native on the recorded Linux runtime.

- Initial state: int32 N, float64 dx, followed by four N-element float64 arrays: Re Phi, Im Phi, Re Phi_t, Im Phi_t. Coordinates are `(index-N//2)*dx`.
- Probe history: int32 detector count, float64 detector positions, then repeated records: float64 integer time and eight float64 values per detector: Re Phi, Im Phi, Re Phi_t, Im Phi_t, Re centered Phi_x, Im centered Phi_x, forward Re Phi difference, forward Im Phi difference.
- Dense intermediate field history (regenerated, not bundled): int32 spatial count, float64 sample spacing, then time t+dt/2 and the Re/Im arrays of the kick-position Phi+dt*Phi_t/2 over x=-30..30. This variable obeys the centered recurrence used in the discrete source reconstruction.

Energy and charge fluxes are extracted from the measured velocity and derivative; frequency fits allow slow drift. Source reconstruction uses the discrete dispersion, Green factor and the position-to-kick cosine conversion. The coherent source integral is not an adjustable forcing: it is evaluated from the same nonlinear solution.

Norm percentages are field-amplitude-squared diagnostics, not energy fractions. The cancellation normalization is a sum of absolute source contributions, not a physically executed alternative. The rate scale ΔE/(-dΔE/dt) is not a demonstrated eventual lifetime.

The report template contains narrative interpretations and rounded numbers for this benchmark. Changing initial data or model parameters requires reconsidering that narrative, even when the scripts regenerate tables and figures.
