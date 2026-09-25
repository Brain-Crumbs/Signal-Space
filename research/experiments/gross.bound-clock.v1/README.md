# GROSS Test 6: localized flat radial clock

**Selected bounded result:** `run-080a63d117abd84d`, analysis `analysis-0002-04d7ed8c`, report `report-0002`. Technical run complete; ten preregistered selected-branch checks pass at $\omega_Q=0.900$. This establishes a local radial clock in the chosen flat continuum action for the tested 100 periods. Trial profiles at $0.868$ and $0.875$ remain numerically unresolved. Neither nonlinear gravity nor full nonspherical core stability was evaluated.

- [Reviewed reader export](export-run-080a63d117abd84d/README.md): setup and interpreted results PDFs, exact plotted data, all figures, source files and reviewed next calculation.
- [Canonical run](run-080a63d117abd84d/manifest.json): immutable raw attempt, solver failures, analyses, reports, checksums and provenance.
- [Reviewed analysis](../../../docs/research/gross-test-06-results.md) and [protocol](../../../docs/research/gross-test-06.md).
- [Initial solver run](run-6d546dddc252a783/manifest.json): preserved precursor using the first locked plan. Fixed-seed BVP guesses failed for the two thinner-wall trials; its saved raw data and one analysis remain auditable. It did not supply the selected report.
- [Source recovery bundle](provenance/source-history.bundle): original solver, analysis and report commits needed to interpret the canonical code identities.

The mode retained 99.9975% projected energy, and a local field trace completed about 100 signed cycles. The energy balance residual exceeds the initial clock energy, so clock radiation energy cannot be isolated from the outer sink. The next bounded calculation is Test 7: freeze this branch and predict neutral-packet reception before running the receiver.
