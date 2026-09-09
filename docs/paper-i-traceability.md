# Paper I implementation traceability

Source: *Directional Signal Clocks: Local Reception Feedback and Causal Networks in 1+1 Dimensions*, revised 8 September 2026, version 3, modified 2026-09-08 23:54 UTC. SHA-256 `457d68693ea4070789287a4de2d8950e2122e65d4cec9c91a40ce4f153aad004`. The manuscript is not in this repository; issue #1 is the authoritative implementation transcription. Paper III is background only.

| Setup | Issue | Fixture/runner target | Required metrics/controls | Explorer view |
|---|---:|---|---|---|
| A isolated/driven | #9 | `setup-a` | analytic R0, prescribed stream, pulse response | response plot/editor |
| B reciprocal pair | #10 | `setup-b` | mean frequency, retarded phase, perturbation, gain sign | pair playback |
| C pair scan | #11 | `setup-c` | detuning/delay/gain grid, coexistence, unresolved flag | sweep comparison |
| D A-B-C | #12 | `setup-d` | reflection, center/end rates, raw vs degree-normalized | network comparison |
| E chain | #13 | `setup-e` | onset/propagation times, causal bound | spacetime playback |
| F boundaries | #14 | `setup-f` | open/driven/mirror/ring and size control | boundary editor |
| G predictive state | #15 | `setup-g` | replay equality; packet/filter/history ablations | state inspector |
| H finite inference | #16 | `setup-h` | replicated uncertainty, event budget, passive vs probe | observer view |
| I transport/echo | #17 | `setup-i` | convention identities, overlap, return latency | transport comparison |

Common contracts are owned by #2–#8; UI surfaces by #18–#20; exports and independent validation by #21–#22. The initial `isolated.json` and `pair.json` files are schema smoke fixtures only, not completed protocol fixtures or scientific results.

## Equation and record coverage

| Paper contract | v1 representation | Later implementation |
|---|---|---|
| centers, `c0`, positive `tau` | `nodes`, `links`, semantic validation | #4 |
| emission E0/E1 | node `q`, scenario/model metadata | #4–#5 |
| response R0/R1/R2 | node response/gain/rate fields | #4 |
| event packets/filter | history packets/filters/RNG | #5 |
| prehistory/predictive state | `InitialHistory`, `Snapshot` | #4, #15 |
| observer vs truth | `ObservationProtocol`, `ObserverRecord`, `PhysicalOutput` | #6 |
| solver/provenance | `SolverSettings`, `RunManifest` | #8, #21 |
| ticks, wrapped/unwrapped phase, retarded phase | documented conventions; unwrapped storage | #7 |
| interventions and reporting latency | explicit intervention/protocol types | #6 |

Deferred: research-scale runs, classification of regimes, manuscript §§12–13 findings, generated motion/binding, conservation closure, emergent geometry, gravity/electromagnetism, SU(2), and formal chaos claims.
