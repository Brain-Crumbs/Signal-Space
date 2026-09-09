import { Ajv2020 } from 'ajv/dist/2020.js';
import type { Port } from '@signal-space/model';
import type { PacketSnapshot } from './packets.js';

export interface DetectorProtocol {
  observerId: string;
  nodeId: string;
  seed: string;
  retentionProbability: number;
  timestamp:
    { kind: 'local-phase' } | { kind: 'calibrated-time'; channel: string };
  /** Half-open [start,end), in the chosen reference, BEFORE detector distortions. */
  gate: { start: number; end: number };
  /** Same units as timestamp: radians for local-phase; seconds for calibrated-time. */
  latency: number;
  jitter: { kind: 'none' } | { kind: 'uniform'; halfWidth: number };
  quantization: { width: number; origin: number };
  readouts: Array<'local-phase' | 'local-frequency'>;
  marks: { kind: 'none' } | { kind: 'source-tag'; channel: string };
}
export interface LocalArrival {
  timestamp: number;
  side: Port;
  localPhase?: number;
  localFrequency?: number;
  sourceTag?: string;
}
/** Only this closed dataset crosses an observer-facing boundary. */
export interface ObserverDataset {
  kind: 'local-arrivals-v1';
  physicalRunId: string;
  protocol: DetectorProtocol;
  timestampUnit: 'rad' | 's';
  operationOrder: 'reference-gate-retain-latency-jitter-quantize-sort';
  missingness: {
    kind: 'independent-bernoulli';
    realizedMissingCount: 'unknown';
  };
  arrivals: LocalArrival[];
}
const number = { type: 'number' };
const nonnegative = { type: 'number', minimum: 0 };
const text = { type: 'string', minLength: 1, maxLength: 4096 };
const object = (
  properties: Record<string, unknown>,
  required = Object.keys(properties),
) => ({ type: 'object', additionalProperties: false, properties, required });
const variant = (kind: string, properties: Record<string, unknown> = {}) =>
  object({ kind: { const: kind }, ...properties });
const protocolSchema = object({
  observerId: text,
  nodeId: text,
  seed: text,
  retentionProbability: { type: 'number', minimum: 0, maximum: 1 },
  timestamp: {
    oneOf: [
      variant('local-phase'),
      variant('calibrated-time', { channel: text }),
    ],
  },
  gate: object({ start: number, end: number }),
  latency: nonnegative,
  jitter: {
    oneOf: [variant('none'), variant('uniform', { halfWidth: nonnegative })],
  },
  quantization: object({
    width: { type: 'number', exclusiveMinimum: 0 },
    origin: number,
  }),
  readouts: {
    type: 'array',
    uniqueItems: true,
    items: { enum: ['local-phase', 'local-frequency'] },
  },
  marks: { oneOf: [variant('none'), variant('source-tag', { channel: text })] },
});
export const observerDatasetSchema = object({
  kind: { const: 'local-arrivals-v1' },
  physicalRunId: text,
  protocol: protocolSchema,
  timestampUnit: { enum: ['rad', 's'] },
  operationOrder: {
    const: 'reference-gate-retain-latency-jitter-quantize-sort',
  },
  missingness: object({
    kind: { const: 'independent-bernoulli' },
    realizedMissingCount: { const: 'unknown' },
  }),
  arrivals: {
    type: 'array',
    items: object(
      {
        timestamp: number,
        side: { enum: ['left', 'right'] },
        localPhase: number,
        localFrequency: { type: 'number', exclusiveMinimum: 0 },
        sourceTag: text,
      },
      ['timestamp', 'side'],
    ),
  },
});
const ajv = new Ajv2020({ strictNumbers: true });
const validProtocol = ajv.compile<DetectorProtocol>(protocolSchema);
const validDataset = ajv.compile<ObserverDataset>(observerDatasetSchema);
function protocolValid(value: unknown): value is DetectorProtocol {
  return validProtocol(value) && value.gate.end > value.gate.start;
}
/** Reject excess fields at every layer and undeclared optional channels. */
export function isObserverDataset(value: unknown): value is ObserverDataset {
  if (!validDataset(value) || !protocolValid(value.protocol)) return false;
  const p = value.protocol;
  return (
    value.timestampUnit ===
      (p.timestamp.kind === 'local-phase' ? 'rad' : 's') &&
    value.arrivals.every(
      (r, i) =>
        (i === 0 || r.timestamp >= value.arrivals[i - 1]!.timestamp) &&
        (r.localPhase === undefined || p.readouts.includes('local-phase')) &&
        (r.localFrequency === undefined ||
          p.readouts.includes('local-frequency')) &&
        (r.sourceTag === undefined || p.marks.kind === 'source-tag'),
    )
  );
}
/** Independent named detector streams, never the physical emitter RNG. */
function random(seed: string, observer: string, channel: string): () => number {
  let state = 2166136261;
  const key = JSON.stringify(['detector-v1', seed, observer, channel]);
  for (let i = 0; i < key.length; i++)
    state = Math.imul(state ^ key.charCodeAt(i), 16777619) >>> 0;
  return () => {
    let t = (state = (state + 0x6d2b79f5) >>> 0);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return (((t ^ (t >>> 14)) >>> 0) + 0.5) / 4294967296;
  };
}
/** Pure recording adapter over a saved, complete simulator snapshot.
 * Uses local readouts only at actual arrivals; never exports adaptive mesh times.
 * No retained ordinal is inherited from physical records or deleted arrivals.
 */
export function recordObserver(
  truth: { runId: string; snapshot: PacketSnapshot },
  protocol: DetectorProtocol,
): ObserverDataset {
  if (
    !protocolValid(protocol) ||
    typeof truth.runId !== 'string' ||
    !truth.runId ||
    truth.runId.length > 4096
  )
    throw new Error('Invalid detector protocol or physical run ID.');
  const p = structuredClone(protocol),
    snapshot = truth.snapshot;
  if (
    snapshot.incomplete ||
    !snapshot.scenario.nodes.some((n) => n.id === p.nodeId)
  )
    throw new Error(
      'Recording requires a complete snapshot and a declared local node.',
    );
  const first = snapshot.history[0]?.nodes[p.nodeId],
    last = snapshot.history.at(-1)?.nodes[p.nodeId];
  const coverage =
    p.timestamp.kind === 'local-phase'
      ? [first?.phi, last?.phi]
      : [0, snapshot.time];
  if (
    coverage[0] === undefined ||
    coverage[1] === undefined ||
    p.gate.start < coverage[0] ||
    p.gate.end > coverage[1]
  )
    throw new Error(
      'The complete recording gate must be covered by saved physical history.',
    );
  const retain = random(p.seed, p.observerId, 'retention'),
    jitter = random(p.seed, p.observerId, 'jitter');
  const samples = new Map(
    snapshot.history.map((sample) => [sample.time, sample.nodes[p.nodeId]!]),
  );
  const arrivals: LocalArrival[] = [];
  for (const event of snapshot.records) {
    if (event.kind !== 'received' || event.target !== p.nodeId) continue;
    const local = samples.get(event.time);
    if (!local)
      throw new Error('Physical arrival lacks its saved local readout.');
    const reference =
      p.timestamp.kind === 'local-phase' ? local.phi : event.time;
    if (reference < p.gate.start || reference >= p.gate.end) continue;
    if (retain() >= p.retentionProbability) continue;
    const distorted =
      reference +
      p.latency +
      (p.jitter.kind === 'uniform'
        ? (2 * jitter() - 1) * p.jitter.halfWidth
        : 0);
    const bin = Math.floor(
      (distorted - p.quantization.origin) / p.quantization.width,
    );
    const timestamp = p.quantization.origin + bin * p.quantization.width;
    if (
      !Number.isFinite(distorted) ||
      !Number.isSafeInteger(bin) ||
      !Number.isFinite(timestamp) ||
      timestamp + p.quantization.width === timestamp
    )
      throw new Error('Detector timestamp/bin is not representable.');
    const record: LocalArrival = { timestamp, side: event.port };
    if (p.readouts.includes('local-phase')) record.localPhase = local.phi;
    if (p.readouts.includes('local-frequency'))
      record.localFrequency = local.omega;
    if (p.marks.kind === 'source-tag') record.sourceTag = event.source;
    arrivals.push(record);
  }
  // Canonical tie ordering uses only permitted fields, never hidden physical order.
  arrivals.sort(
    (a, b) =>
      a.timestamp - b.timestamp ||
      (JSON.stringify(a) < JSON.stringify(b)
        ? -1
        : JSON.stringify(a) > JSON.stringify(b)
          ? 1
          : 0),
  );
  return {
    kind: 'local-arrivals-v1',
    physicalRunId: truth.runId,
    protocol: p,
    timestampUnit: p.timestamp.kind === 'local-phase' ? 'rad' : 's',
    operationOrder: 'reference-gate-retain-latency-jitter-quantize-sort',
    missingness: {
      kind: 'independent-bernoulli',
      realizedMissingCount: 'unknown',
    },
    arrivals,
  };
}
