# T05 detector records and physical interventions

Implements task #6, parent #1, Paper I §§2.7, 7.3, 10 and 11.9. The recording operation changes knowledge of a run; physical pulse removal and added probes change its evolution. These are technical controls, not Setup H results or manuscript findings.

## Observer recording contract

`recordObserver({runId, snapshot}, protocol)` is a pure adapter over a **trusted, complete saved PacketSolver snapshot**. It reads local received events and their saved local phase/frequency at reception, never mutates input, and returns a detached `ObserverDataset`. Snapshot authenticity is checked by `new PacketSolver(scenario, options, snapshot)` when importing untrusted physical checkpoints. Keep those simulator snapshots in a QA interface; pass only the observer dataset to observer-facing analysis or UI. `isObserverDataset(unknown)` validates the closed schema plus channel permissions. It is a data-shape/access check, not cryptographic provenance verification.

The explicit `DetectorProtocol` selects one receiving node. Ordinary observations contain only arrival side and a reported timestamp. Own phase and frequency are opt-in readouts **at arrivals**, not samples of the simulator's adaptive integration mesh. That mesh also tracks remote events and is not an observer sampling clock. Independent scheduled readouts and inference are left to T06/T15. The older `scenario.observation` describes preparation metadata; this detector protocol is the complete T05 recording specification and is not implicitly derived from that metadata.

Use `timestamp: {kind: 'local-phase'}` for an uncalibrated observer: timestamps, gate, latency, jitter width and quantization are in **radians of its unwrapped own phase**. This does not assume access to global time or divide phase by a nominal frequency. `timestamp: {kind: 'calibrated-time', channel: 'declared-reference'}` explicitly grants a calibrated reference-time channel and uses **seconds** instead. The named channel is a declared experimental assumption; the implementation does not derive a calibration protocol. Local frequency readouts are in rad/s as defined by the supplied clock model and must also be explicitly permitted. Detector latency is an additive reporting offset in the selected coordinate; it never changes physical reception/filter times or supplies a delivery scheduler.

All fields are required so the recording assumptions are reviewable. A typical unmarked observer is:

```ts
import { recordObserver } from '@signal-space/sim';
const dataset = recordObserver(
  { runId: 'pair-physical-1', snapshot },
  {
    observerId: 'B-detector-1',
    nodeId: 'B',
    seed: 'B-detection-v1',
    retentionProbability: 0.8,
    timestamp: { kind: 'local-phase' },
    gate: {
      start: snapshot.history[0].nodes.B.phi,
      end: snapshot.history.at(-1).nodes.B.phi,
    },
    latency: 0,
    jitter: { kind: 'uniform', halfWidth: 0.02 },
    quantization: { width: 0.01, origin: 0 },
    readouts: [],
    marks: { kind: 'none' },
  },
);
```

Operation order, saved in every dataset:

1. Select local arrivals and express their reception timestamp in the chosen reference.
2. Apply the **half-open gate `[start,end)`** to that undistorted reference. The whole gate must be covered by the completed snapshot; incomplete runs cannot silently stand in for missing records.
3. Retain independently with the declared probability, including exact zero and one.
4. Add reporting latency, then independent zero-mean uniform jitter on `(-halfWidth,+halfWidth)` (or no jitter). Jitter is timestamp measurement error, so reports can reorder or precede their actual reception timestamp without changing physical causality.
5. Quantize to the lower edge `origin + floor((timestamp-origin)/width)*width`. Bins are `[origin+k*width,origin+(k+1)*width)`, including negative indices. Nonrepresentable/unsafe bin indices and overflow fail. Values at mathematical decimal edges follow ordinary IEEE-754 arithmetic; no undocumented epsilon is added.
6. Sort by reported timestamp, using permitted output fields alone to break ties. Distorted reports may lie outside the original gate; no second gate is silently applied.

Retention and jitter use separate detector streams: FNV-1a over the full UTF-16 encoding of `['detector-v1', seed, observerId, channel]`, then Mulberry32 open-interval uniforms. Neither touches physical emitter RNG. The full protocol/seed is exportable for reproducibility, but missingness reports **only the declared Bernoulli model**; realized deleted counts, timestamps, IDs and ordinal gaps are absent. Two independently seeded/identified observers share the same `physicalRunId` and can record different data. The dataset exposes neither raw physical records, remote phases/present state, packet IDs, filters, adaptive history, physical RNG, nor intervention lineage.

`marks: {kind: 'source-tag', channel: 'readable-emitter-labels'}` explicitly assumes emissions carry readable emitter tags. Only then is each **retained** arrival's emitter name exported as `sourceTag`. Exported run IDs and source tags are nonempty strings of at most 4096 UTF-16 code units, and imported datasets enforce the same boundary independently of JSON Schema's Unicode-code-point length semantics. It is an information-channel variant; it adds no emissions or hidden phase oracle. Unmarked mode does not reveal a source table. Probe packet IDs and intervention metadata remain simulator-only even in tagged mode.

## Physical intervention and paired lineage

The packet engine now supports these explicit `scenario.interventions`:

| Kind           | `target`                              | `value`                        | Physical behavior                                                                                                                 |
| -------------- | ------------------------------------- | ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------- |
| `remove-pulse` | ID of a packet pending at action time | Must be absent                 | Consume the pending packet and record `absorbed`; no receiving filter jump                                                        |
| `add-probe`    | Emitting node ID                      | `{linkId: 'declared-link-id'}` | Add exactly one external probe emission on that node's declared positive-delay route; ordinary reception drives the target filter |

Probe IDs reserve `probe:<intervention-index>`. Their emitted/pending records, and absorption records, include simulator-only `interventionIndex`, pointing to the immutable scenario plan. The probe is an externally imposed additional emission, not a change to the autonomous Poisson law or a phase reset. Its arrival joins simultaneous ordinary arrivals and contributes the same `1/h` jump. Parameter changes and nonempty delayed-response inventories remain unsupported in packet mode.

At an action time, validate all removals against the already-pending inventory; apply removals before coincident arrivals, then sum surviving arrivals jointly. A probe emitted at that time arrives only after its strictly positive link delay. Duplicate/missing/already-consumed removal targets fail instead of becoming silent no-ops. Action batches reserve resource budgets before applying any mutation or advancing RNG. Actions count toward `maxEvents`; queued probes count toward `maxPending`. Time-zero actions are supported by a new scenario and run before the initial sample; a post-event checkpoint cannot be retroactively changed at its timestamp.

Use a separate run identity and paired lineage when comparing interventions:

```ts
import { branchPacketRun } from '@signal-space/sim';
const { solver, lineage } = branchPacketRun(
  { runId: 'baseline', snapshot: checkpoint },
  'probe-branch',
  [
    {
      time: checkpoint.time + 0.1,
      kind: 'add-probe',
      target: 'A',
      value: { linkId: 'A-to-B' },
    },
  ],
);
while (solver.time < until && !solver.incomplete) solver.advance(until);
const branch = { runId: lineage.runId, lineage, snapshot: solver.snapshot() };
```

The helper validates the complete parent checkpoint, requires distinct nonempty string run IDs of at most 4096 UTF-16 code units (matching the observer boundary), appends new actions **strictly after the checkpoint's already-processed time**, and replays the parent's identical advance prefix before returning a solver ready to re-evolve. Existing future actions remain in the plan; incompatible later removals fail. It compares the complete replayed prefix, including rejected trials and the proposed next step. A new event can shorten an old rejected trial that overshot the checkpoint; if that changes the prefix, branching fails explicitly with `INVALID_HISTORY`. Choose a later action time or an earlier checkpoint in that case. It never returns a silently advanced/mismatched fork or edits a saved outcome to counterfeit an intervention. Keep returned lineage alongside each saved branch snapshot: parent/run IDs, fork time, method and exact appended action plan. Complete packet checkpoint replay includes the plan, physical logs, queues, RNG and continuous state. Same-runtime numerical and resource limits from the packet engine still apply; prefix reconstruction is synchronous and bounded.

## Validation and limits

`test/observation.test.ts` covers zero/one retention on frozen physical data, half-open gates/bins and negative bin indices, declared timestamp channels, report reordering under a fixed jitter seed, deep schema/type rejection of hidden fields, independently recorded datasets, invalid/uncovered protocols, analytic filter differences after pulse removal, delayed probe reception and nonzero-feedback changes, unchanged parent prefixes, branch resume, invalid actions, joint arrivals, resource limits, and direct/worker parity.

`node --import tsx scripts/observation-smoke.mjs` regenerates `fixtures/validation/observation-smoke.json` with scenario, solver/recording settings, seeds, source hashes, paired lineage, separate observer datasets and compact physical QA summaries. No inference, scan, scientific conclusion, hosted UI, conservation law or physical delivery-time model is added.
