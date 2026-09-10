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

## T08 Setup A (#9)

Paper I §11.2 maps to `packages/experiments/src/setup-a.ts` and
`docs/setup-a.md`. The typed presets keep isolated, equal/unequal,
piecewise-periodic, finite-pulse, and equal-integral temporal-order protocols
separate. Deterministic envelope runs record R0/R1/R2 signed-gain responses,
phase displacement, frequency relaxation, next-tick status, physical bounds,
input integrals, and a declared diagnostic-only exponential filter response.
The response-curve dataset preserves pulse phase/amplitude inputs and defers
scientific interpretation. Event arrivals and physical filters remain T04–T05
scope; research-scale scans and manuscript conclusions remain deferred.

## T09 Setup B (#10)

Paper I section 11.3 and the facing-lobe caveat in section 3.5 map to
`packages/experiments/src/setup-b.ts`, `packages/sim/src/envelope.ts`, and
`docs/setup-b.md`. Reciprocal `A-B`/`B-A`, one-way `A-B`, and prescribed-drive
controls are distinct protocol IDs. The typed layer crosses E0/E1 with R0/R1/R2,
saves co-phase and pi-reflection preparations plus explicit link prehistory,
and supports signed gain sweeps through zero. It records mean-frequency
mismatch, unwrapped pair drift/slips, simulator-only retarded phase with an
explicit `chi`, collective modulation, and perturbation recovery evidence using
shared analysis metrics. The envelope solver's explicit state perturbation
option preserves pre-jump dense history and post-jump states in replayable
snapshots; ULP-equivalent propagated source queries retain the pre-jump left
limit, and Setup B runs save exact finite-window start samples. It is an
intervention, not an unstated phase reset or synchronization rule. Setup B smoke
runs are finite deterministic diagnostics, not locking or attraction findings.
Event statistics, physical filters, boundaries beyond open ports, and
research-scale scans remain deferred.

## T10 Setup C (#11)

Paper I section 11.4 maps to `packages/experiments/src/setup-c.ts` and
`docs/setup-c.md`. The scan layer uses the shared envelope solver and pair
classifier for dimensionless detuning, positive delay, signed gain, contrast,
and relaxation-time coordinates. It records physical conversions, the E0/E1
baseline matching rule, nested finite-window evidence, irregularity diagnostics,
replicate uncertainty, trajectory run IDs, and distinct unresolved, numerical
failure, and unrun masks. Forward and reverse orders adopt complete solver
snapshots as parameter-continuation state while independent restarts remain
separately identifiable. No cell is labeled as locking, coexistence, or chaos;
publication-scale scans and scientific interpretation remain deferred.

## T07 declarative runs (#8)

The current run layer also validates resolved scenarios against both JSON Schema and semantic constraints, rechecks root-seed-bound manifest identities, and binds checkpoint resumes to the exact planned manifest. See `docs/experiment-runs.md` for the validation and recovery contract.

Paper I §§11.1 and 11.11 map to `packages/experiments/src/runs.ts` and the `paper-i-experiment-v1` schema. Definitions resolve parameter axes, explicit E/R variants, named controls, interventions, windows, tolerances, observables, replicate seeds and bounded resource budgets into complete `signal-space-run-manifest` records. Canonical SHA-256 identities and hierarchical physical seeds are independent of sweep concurrency. Complete low-level execution events are retained in `RunResult`; `SweepCheckpoint` records partial, cancelled and completed work for hash-checked resume. `continueRun` is explicitly distinct from restarting a manifest and restores the full envelope/packet checkpoint. `createSmokeDefinition` covers inexpensive A–I wiring fixtures; no publication-scale or research manifest is included. See [experiment runs](experiment-runs.md) and `test/runs.test.ts`.

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
| finite-window regimes and uncertainty          | pure analysis records and replicate intervals             | #7                   |

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

Paper I §§2.7, 7.3, 10 and 11.9 map to `packages/sim/src/observation.ts` (pure local recording, explicit gates/reference channels, retention, latency, jitter, bins, optional readable marks, closed observer dataset), `interventions.ts` (validated parent-prefix branching and paired lineage), and `packets.ts` (physical absorption and positive-delay probe reception). Parent contract items 6 and 11 are controlled by analytic filter jumps/decay and nonzero-feedback trajectory comparisons. `test/observation.test.ts` proves passive detector invariance, independent observations, no deleted-event/remote-truth fields, half-open gates/bins, reporting reorder without physical reorder, causal probes, branch replay and direct/worker parity. `docs/observation.md` records coordinate/operation-order decisions, access assumptions and numerical limits. Intervention scheduling uses one ordered index and a pending cursor; controls cover 10,000 future actions across 10,000 steps, original plan IDs, simultaneous/time-zero batches, and replay across action times. The saved `observation-smoke.json` is reproducible technical QA, not Setup H inference or a paper finding.

## T06 finite-window diagnostics (#7)

Paper I §11.1 equation (66) and §11.11 equation (67) map to
`packages/analysis/src/index.ts`. Phase-advance frequency, unwrapped pair
phase/slips, retarded mismatch, reception inventories, spatial coherence,
response fronts, nested-window classifications, and independent-replicate
intervals retain their definitions and evidence. Retarded source state defaults
to simulator-only; phase attraction requires perturbation recovery; numerical
failure and unresolved evidence remain distinct. See `docs/diagnostics.md`.
