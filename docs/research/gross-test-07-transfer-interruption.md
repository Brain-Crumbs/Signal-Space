# Test 7 transfer: local interruption and hosted recovery

The local execution environment became inaccessible while the bounded run was in progress. Its final process state and remaining files could not be retrieved. It is not reported as a completed experiment.

## Last observed local provenance

- Solver source commit: `5095f477105dc1d885cf6f79b524605b307339ce`.
- Published equivalent source tree: `7a9c8441873c90407f9c79e3cd0c5f387dd5ce96`, at GitHub commit `2324039aed0a2a1de53ca1a2dc96676cfdf1a208`.
- Local run: `run-8546b880d907e0ae`.
- All sixteen forecasts were recorded before any nonlinear receiver.
- Prediction-lock event: 2026-09-26T04:17:03.934227Z; lock SHA-256 `757b794583474ec122fda9d32f3dfd5bafb21d6bd14cbd63d9217c8a3807dbe3`.
- First receiver started at 2026-09-26T04:17:03.934634Z.
- Last observed event: carrier half-step receiver started at 2026-09-26T04:29:54.476429Z, after nine of sixteen receiver cases completed.
- Local full repository check passed, including 87 Python and 13 pipeline tests. An earlier preflight stopped before solver execution because the runtime configuration hash had not been populated; it was corrected before the source commit above.

These entries are transcribed from observed tool outputs. They are not a replacement for the unavailable complete local evidence package or its checksum verification.

## Partial observations, diagnostic only

At nominal amplitude 0.012 on the finest mesh:

| Spectrum | Observed interval | Locked second-order forecast | Locked fourth-order forecast |
| --- | ---: | ---: | ---: |
| Broad | -1.4640933917626983e-6 | -1.4942281252691185e-6 | -1.4641207992926101e-6 |
| Carrier | 5.602444109906745e-7 | 5.34148833451933e-7 | 5.601034452192704e-7 |

All values are cycles. The missing time/domain/control results prevent a completed classification. The carrier forecast showed poorer convergence than the measured interval, motivating a separately labeled downstream diagnostic of forecast convergence and linear inverse error. No original threshold was changed.

## Recovery rules

The branch-specific hosted workflow repeats the same locked configuration and physical solver with independent run provenance. It retains the original nine checks and adds the post-lock diagnostics. The already inspected local histories cannot be called a new held-out sample merely because they are repeated on another computer.

A completed hosted package is reproducibility evidence for this fixed protocol. Scientific review must retain the distinction between its machine classification and the stronger question of whether forecast convergence resolves the fourth-order correction. Original Test 7 remains failed, and Test 8 remains blocked pending a separate acceptance review.
