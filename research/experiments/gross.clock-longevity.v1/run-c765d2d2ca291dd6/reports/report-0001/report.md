# Signal Space: Test 6 longevity prerequisite

Technical state: completed. Scientific classification: pass.
Run: run-c765d2d2ca291dd6. Analysis: analysis-0001-22d5199b.
Source profile run: run-080a63d117abd84d; frozen omega_Q=0.900, Omega=0.41274991; local radius=0.1.
Solver revision: 867220030e89c2b8924f575c818be3393c911e38; renderer revision: 852a0ccec691d8a3bc6ac62bdf40730f848b5b4d.
The exact locked method, thresholds and controls are in the plan. Scope: flat spherical matter; no gravitational or nonspherical result.

Locked scientific checks:
- charge-ledger: pass
- convergence: pass
- frozen-inputs: pass
- lifetime: pass
- local-record: pass

## local-ticks
Question: Does the same local radius keep ticking over 100 periods on each grid?
Reading: All grids have 100 positive-going ticks. Fine frequency 0.412748290; largest relative grid/time difference 4.92e-06.
Significance: The full refined duration now supports using this radial core as a finite-duration local clock.
Limitation: The ideal probe samples r=0.1 in the fixed flat rest frame; no remote marker or nonspherical stability is established.

## long-baseline
Question: Do mode energy and charge remain controlled for the full refined baseline?
Reading: Final fine-grid mode change -6.23e-06; fine energy residual 0.806 initial mode energies.
Significance: Refined and time-step controls close the missing 100-period usability check. The energy diagnostic improves with time refinement.
Limitation: Near-constant projection does not measure a tiny radiation spectrum. A 100-period wide-box run and angular stability remain untested.
