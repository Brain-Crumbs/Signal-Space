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

Pending-packet source/target membership is checked at the same preparation boundary; regression cases reject each undeclared endpoint before inspection exposes a snapshot.

Mirror round-trip history coverage (parent contract item 12) and classification of uncloneable input are covered by targeted execution regressions.

Shared-memory rejection and ordinary buffer ownership regressions protect detached preparation/snapshot semantics.

## T03 causal deterministic envelopes (#4)

Paper I §§3.1–3.5 / equations (8)–(13), using the source transcription in parent #1, now map to `packages/sim/src/envelope.ts` and the `envelope` execution mode:

| Contract                     | Implementation and evidence                                                                                                  |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| E0/E1 directional emissions  | Shared rate function and integrated directional intensities; positivity, rate-sum and per-cycle controls                     |
| R0/R1/R2 feedback            | Adaptive RK4 method of steps; analytic free phase and exponential R1, both gain signs, R2 reflection                         |
| Positive-delay reception     | Retained cubic history and off-grid retarded source evaluations; causal empty-link startup and refinement                    |
| Predictive preparation/state | Linear or sampled phase prehistory, separate empty links, versioned history-complete checkpoint, corruption/restart controls |
| Ticks/state bounds           | Unwrapped phases, cubic crossing times, frequency bounds, rejection without clipping                                         |
| Open/prescribed ports        | Piecewise external rates and recorded gain-change boundaries; transport seam for T13                                         |
| Shared execution             | CLI `--until`, production worker parity, cooperative cancellation with checkpoint                                            |

See `docs/envelope-solver.md` for units, algorithms, error controls, supported interventions and limitations. `test/envelope.test.ts` supplies inexpensive independent controls; the scenario fixtures remain smoke inputs rather than completed A–I protocols. Event dynamics, mirror/ring adapters, observer diagnostics, publication runs and manuscript conclusions remain deferred.

## T04 stochastic packets (#5)

PR #26 review regressions additionally cover supplementary-Unicode seed/node identity, malformed and non-JSON checkpoint classification through both direct and worker execution, and independently rounded decimal route timestamps with scale-sensitive mismatch rejection. These preserve stochastic stream identity and boundary validation without changing the paper's physical laws.

Paper I §3.3 equation (13a), §3.4 and §11.1 map to `packages/sim/src/packets.ts` and shared execution mode `packets`. E0/E1 bounded conditional-intensity thinning uses separate seeded emitter/port streams; R0/R1/R2 continuously evolve between causal events. Finite packet inventory, unique lifecycle records, joint left/right exponential-filter jumps, complete same-runtime replay, detector-independent physical RNG, resource-limited incomplete status and cancellation are covered by `test/packets.test.ts`. Analytical filter/response controls, 64-seed fixed-rate checks, packet accounting and CLI/browser worker controls provide inexpensive validation. See `docs/packet-engine.md` for algorithm versions, numerical limits and explicit preparation semantics. Boundary extensions and research results remain deferred; T05 adds the detector/intervention layer below.

## T05 detector records and physical branches (#6)

Paper I §§2.7, 7.3, 10 and 11.9 map to `packages/sim/src/observation.ts` (pure local recording, explicit gates/reference channels, retention, latency, jitter, bins, optional readable marks, closed observer dataset), `interventions.ts` (validated parent-prefix branching and paired lineage), and `packets.ts` (physical absorption and positive-delay probe reception). Parent contract items 6 and 11 are controlled by analytic filter jumps/decay and nonzero-feedback trajectory comparisons. `test/observation.test.ts` proves passive detector invariance, independent observations, no deleted-event/remote-truth fields, half-open gates/bins, reporting reorder without physical reorder, causal probes, branch replay and direct/worker parity. `docs/observation.md` records coordinate/operation-order decisions, access assumptions and numerical limits. The saved `observation-smoke.json` is reproducible technical QA, not Setup H inference or a paper finding.
