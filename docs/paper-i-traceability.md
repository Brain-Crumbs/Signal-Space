# Paper I implementation traceability

Source: _Directional Signal Clocks: Local Reception Feedback and Causal Networks in 1+1 Dimensions_, revised 8 September 2026, version 3, modified 2026-09-08 23:54 UTC. SHA-256 `457d68693ea4070789287a4de2d8950e2122e65d4cec9c91a40ce4f153aad004`. The manuscript is not in this repository; issue #1 is the authoritative implementation transcription. Paper III is background only.

| Setup              | Issue | Fixture/runner target | Required metrics/controls                               | Explorer view        |
| ------------------ | ----: | --------------------- | ------------------------------------------------------- | -------------------- |
| A isolated/driven  |    #9 | `setup-a`             | analytic R0, prescribed stream, pulse response          | response plot/editor |
| B reciprocal pair  |   #10 | `setup-b`             | mean frequency, retarded phase, perturbation, gain sign | pair playback        |
| C pair scan        |   #11 | `setup-c`             | detuning/delay/gain grid, coexistence, unresolved flag  | sweep comparison     |
| D A-B-C            |   #12 | `setup-d`             | reflection, center/end rates, raw vs degree-normalized  | network comparison   |
| E chain            |   #13 | `setup-e`             | onset/propagation times, causal bound                   | spacetime playback   |
| F boundaries       |   #14 | `setup-f`             | open/driven/mirror/ring and size control                | boundary editor      |
| G predictive state |   #15 | `setup-g`             | replay equality; packet/filter/history ablations        | state inspector      |
| H finite inference |   #16 | `setup-h`             | replicated uncertainty, event budget, passive vs probe  | observer view        |
| I transport/echo   |   #17 | `setup-i`             | convention identities, overlap, return latency          | transport comparison |

Common contracts are owned by #2–#8; UI surfaces by #18–#20; exports and independent validation by #21–#22. The initial `isolated.json` and `pair.json` files are schema smoke fixtures only, not completed protocol fixtures or scientific results.

## Equation and record coverage

| Paper contract                                 | v1 representation                                         | Later implementation |
| ---------------------------------------------- | --------------------------------------------------------- | -------------------- |
| centers, `c0`, positive `tau`                  | `nodes`, `links`, semantic validation                     | #4                   |
| emission E0/E1                                 | node `emission` union: E0 `nu` / E1 `q`                   | #4–#5                |
| response R0/R1/R2                              | node response/gain/rate fields                            | #4                   |
| event packets/filter                           | history packets/filters/RNG                               | #5                   |
| prehistory/predictive state                    | `InitialHistory`, `Snapshot`                              | #4, #15              |
| observer vs truth                              | `ObservationProtocol`, `ObserverRecord`, `PhysicalOutput` | #6                   |
| solver/provenance                              | `SolverSettings`, `RunManifest`                           | #8, #21              |
| ticks, wrapped/unwrapped phase, retarded phase | documented conventions; unwrapped storage                 | #7                   |
| interventions and reporting latency            | explicit intervention/protocol types                      | #6                   |

Deferred: research-scale runs, classification of regimes, manuscript §§12–13 findings, generated motion/binding, conservation closure, emergent geometry, gravity/electromagnetism, SU(2), and formal chaos claims.

## T02 engineering foundation (#3)

The npm workspace, pinned Node/toolchain and lockfile, strict TypeScript boundary, CLI, React/Vite Web Worker shell, lint/format configuration and fresh-checkout CI implement engineering infrastructure for §11. Both entry points import `@signal-space/sim`; there is no UI physics implementation.

`inspect` checks the isolated/pair contract fixtures and returns the supplied complete initial snapshot at t=0. Contract, shared execution, cancellation, malformed-input, CLI parity and production-worker parity checks cover this infrastructure. See `docs/execution-api.md` and README validation commands. These checks add no physical law or numerical findings. The A–I protocols, actual solver, evolved-state replay, diagnostics and publication runs remain assigned to their later tasks.

PR #24 review validation enforces closed nested scenario shapes, complete per-clock history/filter maps and causal pending-packet times at the preparation boundary (§11.1; parent contract items 2, 6–7). Negative execution tests verify rejection before any snapshot is exposed; zero-time arrival and extensible-payload controls preserve supported preparations.

Follow-up review checks reject mismatched t=0 history endpoints and pending responses for undeclared clocks, preserving one consistent initial physical state.
