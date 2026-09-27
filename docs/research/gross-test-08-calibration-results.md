# Test 8 spatial calibration pilot: partial numerical result

The locked [pilot plan](plans/gross-test-08-calibration.json) was run with model `signal-space.ss-ocf-1.flat-axisymmetric-neutral-clock.v1`. The canonical identity is `run-500a2f07add9555b`, analysis `analysis-0001-e4df0387`, report `report-0002`. Its canonical verifier passed: one attempt, one analysis, two reports and 62 indexed artifacts. The **scientific classification is unresolved**; this is not Test 8 acceptance.

| Grid and preparation                | Max energy drift / initial total energy | Max charge drift / initial charge | Neutral field maximum |
| ----------------------------------- | --------------------------------------: | --------------------------------: | --------------------: |
| Isolated, h=0.8, dt=0.04            |                               1.1831e-8 |                         1.2053e-8 |                     0 |
| Isolated, h=0.4, dt=0.02            |                              3.7012e-10 |                        3.7731e-10 |                     0 |
| Quiet superposition, h=0.8, dt=0.04 |                               1.1831e-8 |                         1.2053e-8 |                     0 |
| Quiet superposition, h=0.4, dt=0.02 |                              3.7012e-10 |                        3.7731e-10 |                     0 |

These are closed-box **total** ledger fractions over 16 time units. They validate only the pilot's short conservation criteria. They do not bound a small clock signal or receiver impulse, nor disentangle spatial from timestep error because both changed together. Independent manufactured-axis, face-flux, Hamiltonian-derivative and zero-neutral/charge controls pass. The pair starts as unrelaxed superposed fields; the short trace cannot prove a 100-period independently usable clock.

The first pipeline analysis was recorded with inline JSON in check evidence and consequently failed canonical verification. Its source run `run-0e3c3c986a1a2d46` remains preserved locally as an invalid-package attempt, with the same physical raw array hashes. A new registered run from the unchanged locked plan corrected the adapter and verified. This analysis correction did not change the action, config, solver or thresholds.

## Next smallest discriminating calculation

Embed the frozen profile at h=0.2 and h=0.1, then independently halve dt and enlarge the mirror box. Solve or relax joint pair data and quantify preparation losses and the isolated/quiet 100-period local mode energy, charge, frequency, and spatial containment. Compare worldline-centered local samples with identical quiet-pair preparations. A resolved >1% mode loss, broken frequency gate or boundary/domain dependence blocks source-only feasibility. If calibration passes, design a source-only neutral and structural pilot with no more than six preparations, independently compute radiation/receiver feasibility, and only then lock the held-out issue #82 G0–G9 matrix.

No physical reception, recoil, postinteraction survival, transverse stability, gravity, emergent metric, or Test 9 readiness follows from these traces. `test9-readiness.json` must remain `ready: false` until all Test 8 gates and the canonical reader/evidence pair pass.
