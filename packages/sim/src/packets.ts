import { Ajv2020 } from 'ajv/dist/2020.js';
import schema from '@signal-space/model/schema' with { type: 'json' };
import { validateScenario } from '@signal-space/model';
import type { Scenario, Port, Packet } from '@signal-space/model';
import { emission, EnvelopeFailure } from './envelope.js';

export interface PacketOptions {
  /** Required physical seed. InitialHistory.rngState is legacy preparation metadata. */
  seed: string;
  detectorSeed?: string;
  interventionSeed?: string;
  maxSteps?: number;
  maxEvents?: number;
  maxPending?: number;
}
export interface PacketSample {
  time: number;
  nodes: Record<
    string,
    { phi: number; omega: number; left: number; right: number }
  >;
}
export interface PacketRecord {
  time: number;
  packetId: string;
  source: string;
  /** Outgoing port for emitted/escaped; receiving port for pending/received. */
  port: Port;
  target?: string;
  kind: 'emitted' | 'pending' | 'received' | 'escaped' | 'absorbed';
}
interface Stream {
  id: string;
  node: number;
  port: Port;
  bound: number;
  rng: number;
  next: number;
  count: number;
}
export interface PacketSnapshot {
  kind: 'packet-thinning-rk4-v1';
  scenario: Scenario;
  options: PacketOptions;
  time: number;
  state: number[];
  filters: number[];
  streams: Stream[];
  pending: Packet[];
  pendingResponses: Scenario['initialHistory']['pendingResponses'];
  history: PacketSample[];
  records: PacketRecord[];
  /** Each bounded advance call, including rejected trials, for trusted replay. */
  advances: number[];
  nextStep: number;
  steps: number;
  events: number;
  incomplete: string | null;
}
const validateStructure = new Ajv2020({ allErrors: true }).compile<Scenario>(
  schema,
);
const ports: Port[] = ['left', 'right'];
const order = (a: string, b: string) => (a < b ? -1 : a > b ? 1 : 0);
function canonical(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value !== null && typeof value === 'object')
    return `{${Object.entries(value)
      .sort(([a], [b]) => order(a, b))
      .map(([k, v]) => `${JSON.stringify(k)}:${canonical(v)}`)
      .join(',')}}`;
  return JSON.stringify(value);
}
function invalid(message: string): never {
  throw new EnvelopeFailure('INVALID_REQUEST', message);
}
function numerical(message: string): never {
  throw new EnvelopeFailure('NUMERICAL_FAILURE', message);
}
/** FNV-1a seed derivation; JSON tuple encoding prevents ambiguous stream names. */
function seedState(seed: string, id: string): number {
  let hash = 2166136261;
  for (const c of JSON.stringify(['physical-emission-v1', seed, id])) {
    hash = Math.imul(hash ^ c.charCodeAt(0), 16777619) >>> 0;
  }
  return hash;
}
/** Mulberry32, open-interval U: no log(0), and no shared generator across ports. */
function uniform(stream: Stream): number {
  let t = (stream.rng = (stream.rng + 0x6d2b79f5) >>> 0);
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return (((t ^ (t >>> 14)) >>> 0) + 0.5) / 4294967296;
}
function schedule(stream: Stream, time: number): void {
  stream.next = time - Math.log(uniform(stream)) / stream.bound;
  if (!Number.isFinite(stream.next) || stream.next <= time)
    numerical(
      'Candidate waiting time is not finite and representably positive.',
    );
}

/** Simulator-only stochastic truth. Ordinary arrivals consume a packet once.
 * No detector RNG, reporting rule, or observer label participates in evolution.
 */
export class PacketSolver {
  private scenario: Scenario;
  private options: PacketOptions;
  private state: number[];
  private filters: number[];
  private streams: Stream[] = [];
  private pending: Packet[];
  private history: PacketSample[] = [];
  private records: PacketRecord[] = [];
  private advances: number[] = [];
  private nextStep: number;
  private steps = 0;
  private events = 0;
  private currentTime = 0;
  private limit: string | null = null;
  private maxSteps: number;
  private maxEvents: number;
  private maxPending: number;

  constructor(
    scenario: Scenario,
    options: PacketOptions,
    resume?: PacketSnapshot,
  ) {
    this.scenario = structuredClone(scenario);
    this.options = structuredClone(options);
    const s = this.scenario;
    if (!validateStructure(s) || !validateScenario(s).ok)
      invalid('Invalid packet scenario.');
    if (
      !options ||
      typeof options.seed !== 'string' ||
      !options.seed.length ||
      options.seed.length > 4096
    )
      invalid('Provide a nonempty physical seed (at most 4096 characters).');
    for (const key of Object.keys(options))
      if (
        ![
          'seed',
          'detectorSeed',
          'interventionSeed',
          'maxSteps',
          'maxEvents',
          'maxPending',
        ].includes(key)
      )
        invalid(`Unknown packet option: ${key}`);
    for (const key of ['detectorSeed', 'interventionSeed'] as const)
      if (
        options[key] !== undefined &&
        (typeof options[key] !== 'string' || options[key].length > 4096)
      )
        invalid(`Invalid ${key}.`);
    const budget = (value: number | undefined, fallback: number) => {
      const result = value ?? fallback;
      if (!Number.isSafeInteger(result) || result < 1 || result > 100000)
        invalid('Packet budgets must be integers in [1,100000].');
      return result;
    };
    this.maxSteps = budget(options.maxSteps, 10000);
    this.maxEvents = budget(options.maxEvents, 10000);
    this.maxPending = budget(options.maxPending, 10000);
    if (s.nodes.length > 128 || s.nodes.length * this.maxSteps > 1000000)
      invalid(
        'Packet history budget exceeds one million node steps or 128 nodes.',
      );
    if (!['event', 'rk4'].includes(s.solver.method))
      invalid(
        'Packets support event/rk4 with adaptive RK4 continuous evolution.',
      );
    this.nextStep = s.solver.step ?? 0.01;
    if (
      !(this.nextStep > 0) ||
      !Number.isFinite(this.nextStep) ||
      !(s.solver.absoluteTolerance > 0) ||
      !(s.solver.relativeTolerance > 0)
    )
      invalid('Positive finite step and tolerances are required.');
    if (s.interventions.length || s.initialHistory.pendingResponses.length)
      throw new EnvelopeFailure(
        'UNSUPPORTED_MODEL',
        'Event interventions and delayed response laws belong to T05; nonempty pending responses cannot be evolved yet.',
      );
    if (ports.some((p) => s.boundaries[p].kind !== 'open'))
      throw new EnvelopeFailure(
        'UNSUPPORTED_MODEL',
        'T04 supports open boundaries; driven event sources and mirror/ring adapters require declared later protocols.',
      );
    this.state = s.nodes.flatMap((n) => [n.phi, n.omega]);
    this.filters = s.nodes.flatMap((n) => [
      s.initialHistory.filters[n.id]!.left,
      s.initialHistory.filters[n.id]!.right,
    ]);
    if (
      !Number.isFinite(1 / s.filterWidth) ||
      !this.filters.every(Number.isFinite)
    )
      invalid('Filter width and memory must be representable.');
    this.pending = structuredClone(s.initialHistory.pendingPackets).sort(
      (a, b) => a.arrivalTime - b.arrivalTime || order(a.id, b.id),
    );
    if (
      this.pending.length > this.maxPending ||
      this.pending.length > this.maxEvents
    )
      invalid('Initial packet inventory exceeds resource limits.');
    const ids = new Set<string>();
    for (const packet of this.pending) {
      if (ids.has(packet.id) || packet.id.startsWith('event:'))
        invalid(
          'Initial packet IDs must be unique and cannot use reserved event: prefix.',
        );
      ids.add(packet.id);
      const route = s.links.find(
        (l) =>
          l.source === packet.source &&
          l.target === packet.target &&
          l.targetPort === packet.port,
      );
      if (!route || packet.emissionTime + route.delay !== packet.arrivalTime)
        invalid(
          'Initial packet must match a declared positive-delay route exactly.',
        );
      this.records.push({
        time: 0,
        packetId: packet.id,
        source: packet.source,
        target: packet.target,
        port: packet.port,
        kind: 'pending',
      });
    }
    s.nodes.forEach((node, nodeIndex) => {
      const nuMax =
        node.emission.law === 'E0'
          ? node.emission.nu
          : (node.emission.q * (node.omega0 + Math.abs(node.gain))) /
            (2 * Math.PI);
      const bound = nuMax * ((1 + node.amplitude) / 2);
      if (!(bound > 0) || !Number.isFinite(bound))
        invalid('Emission thinning bound must be finite and positive.');
      for (const port of ports) {
        const id = JSON.stringify([node.id, port]);
        const stream: Stream = {
          id,
          node: nodeIndex,
          port,
          bound,
          rng: seedState(options.seed, id),
          next: 0,
          count: 0,
        };
        schedule(stream, 0);
        this.streams.push(stream);
      }
    });
    this.streams.sort((a, b) => order(a.id, b.id));
    if (
      new Set(this.streams.map((stream) => stream.rng)).size !==
      this.streams.length
    )
      invalid('Physical stream seed collision; choose a different seed.');
    this.processEvents(); // Includes finite declared arrivals at t=0, jointly.
    this.history.push(this.sample());
    if (resume !== undefined) {
      if (
        resume.kind !== 'packet-thinning-rk4-v1' ||
        canonical(resume.scenario) !== canonical(s) ||
        canonical(resume.options) !== canonical(this.options) ||
        !Array.isArray(resume.advances) ||
        resume.advances.length > this.maxSteps + this.maxEvents + 1
      )
        throw new EnvelopeFailure(
          'INVALID_HISTORY',
          'Checkpoint version, scenario, options or replay budget mismatch.',
        );
      // Never trust edited filters, RNG, counters or queued packets: reconstruct them.
      for (const until of resume.advances) {
        if (
          this.limit ||
          typeof until !== 'number' ||
          !Number.isFinite(until) ||
          until <= this.time
        )
          throw new EnvelopeFailure(
            'INVALID_HISTORY',
            'Invalid checkpoint advance history.',
          );
        this.advance(until);
      }
      if (canonical(this.snapshot()) !== canonical(resume))
        throw new EnvelopeFailure(
          'INVALID_HISTORY',
          'Checkpoint differs from deterministic same-runtime replay.',
        );
    }
  }
  get time(): number {
    return this.currentTime;
  }
  get incomplete(): string | null {
    return this.limit;
  }
  sample(): PacketSample {
    return {
      time: this.time,
      nodes: Object.fromEntries(
        this.scenario.nodes.map((n, i) => [
          n.id,
          {
            phi: this.state[2 * i]!,
            omega: this.state[2 * i + 1]!,
            left: this.filters[2 * i]!,
            right: this.filters[2 * i + 1]!,
          },
        ]),
      ),
    };
  }
  snapshot(): PacketSnapshot {
    return structuredClone({
      kind: 'packet-thinning-rk4-v1',
      scenario: this.scenario,
      options: this.options,
      time: this.time,
      state: this.state,
      filters: this.filters,
      streams: this.streams,
      pending: this.pending,
      pendingResponses: [],
      history: this.history,
      records: this.records,
      advances: this.advances,
      nextStep: this.nextStep,
      steps: this.steps,
      events: this.events,
      incomplete: this.limit,
    });
  }
  private derivative(y: number[], offset: number): number[] {
    const decay = Math.exp(-offset / this.scenario.filterWidth);
    return this.scenario.nodes.flatMap((node, i) => {
      const phi = y[2 * i]!,
        omega = y[2 * i + 1]!;
      const input =
        (this.filters[2 * i]! * decay) / this.scenario.rateScale +
        (this.filters[2 * i + 1]! * decay) / this.scenario.rateScale;
      const z = node.response === 'R2' ? Math.cos(2 * phi) : 1;
      const target =
        node.omega0 +
        (node.response === 'R0' ? 0 : node.gain * z * Math.tanh(input));
      return [omega, (target - omega) / node.relaxationTime];
    });
  }
  private rk(y: number[], h: number, offset: number): number[] {
    const add = (k: number[], scale: number) =>
      y.map((v, i) => v + scale * k[i]!);
    const k1 = this.derivative(y, offset);
    const k2 = this.derivative(add(k1, h / 2), offset + h / 2);
    const k3 = this.derivative(add(k2, h / 2), offset + h / 2);
    const k4 = this.derivative(add(k3, h), offset + h);
    return y.map(
      (v, i) => v + (h / 6) * (k1[i]! + 2 * k2[i]! + 2 * k3[i]! + k4[i]!),
    );
  }
  private admissible(y: number[]): boolean {
    return (
      y.every(Number.isFinite) &&
      this.scenario.nodes.every((n, i) => {
        const w = y[2 * i + 1]!;
        const slack = 8 * Number.EPSILON * (n.omega0 + Math.abs(n.gain));
        return (
          w > 0 &&
          w >= n.omega0 - Math.abs(n.gain) - slack &&
          w <= n.omega0 + Math.abs(n.gain) + slack &&
          y[2 * i]! >= this.state[2 * i]!
        );
      })
    );
  }
  /** One adaptive trial. Rejected trials consume budget but never alter physics. */
  advance(until: number): void {
    if (!Number.isFinite(until) || until <= this.time)
      invalid('until must be finite and later than current packet time.');
    if (this.limit) return;
    this.advances.push(until);
    if (this.steps >= this.maxSteps) {
      this.limit = 'maxSteps';
      return;
    }
    const nextEvent = Math.min(
      this.pending[0]?.arrivalTime ?? Infinity,
      ...this.streams.map((s) => s.next),
    );
    const resolutionStep = Math.min(
      this.scenario.filterWidth / 4,
      ...this.scenario.nodes.map((n) =>
        Math.min(n.relaxationTime / 4, 0.1 / (n.omega0 + Math.abs(n.gain))),
      ),
    );
    const end = Math.min(
      until,
      nextEvent,
      this.time + resolutionStep,
      this.time + this.nextStep,
      this.time + (this.scenario.solver.step ?? 0.01),
    );
    const h = end - this.time;
    if (!(h > 0) || !Number.isFinite(h))
      numerical('Packet integration step underflow.');
    this.steps++;
    const full = this.rk(this.state, h, 0);
    const half = this.rk(this.state, h / 2, 0);
    const fine = this.rk(half, h / 2, h / 2);
    const error = Math.max(
      ...fine.map(
        (v, i) =>
          Math.abs(v - full[i]!) /
          (15 *
            (this.scenario.solver.absoluteTolerance +
              this.scenario.solver.relativeTolerance *
                Math.max(Math.abs(v), Math.abs(this.state[i]!)))),
      ),
    );
    const acceptable =
      Number.isFinite(error) &&
      error <= 1 &&
      this.admissible(half) &&
      this.admissible(fine);
    this.nextStep = acceptable
      ? Math.min(
          this.scenario.solver.step ?? 0.01,
          h *
            Math.min(
              2,
              Math.max(0.2, 0.9 * Math.pow(Math.max(error, 1e-12), -0.2)),
            ),
        )
      : h / 2;
    if (!acceptable) return;
    this.state = fine;
    this.filters = this.filters.map(
      (v) => v * Math.exp(-h / this.scenario.filterWidth),
    );
    this.currentTime = end;
    this.processEvents();
    this.history.push(this.sample());
  }
  private processEvents(): void {
    const arrivals = this.pending.filter((p) => p.arrivalTime === this.time);
    const candidates = this.streams.filter((s) => s.next === this.time);
    // Reserve worst-case output capacity before consuming any RNG or arrivals.
    if (this.events + arrivals.length + candidates.length > this.maxEvents) {
      this.limit = 'maxEvents';
      return;
    }
    if (
      this.pending.length - arrivals.length + candidates.length >
      this.maxPending
    ) {
      this.limit = 'maxPending';
      return;
    }
    const jumps = new Array<number>(this.filters.length).fill(0);
    for (const packet of arrivals) {
      const i = this.scenario.nodes.findIndex((n) => n.id === packet.target);
      jumps[2 * i + (packet.port === 'left' ? 0 : 1)]!++;
    }
    const nextFilters = this.filters.map(
      (v, i) => v + jumps[i]! / this.scenario.filterWidth,
    );
    if (!nextFilters.every(Number.isFinite))
      numerical('Receiver filter overflow.');
    // Intensities depend on continuous phi/omega, unchanged by simultaneous jumps.
    for (const stream of candidates) {
      const node = this.scenario.nodes[stream.node]!;
      const rate = emission(
        node,
        this.state[2 * stream.node]!,
        this.state[2 * stream.node + 1]!,
      )[stream.port === 'left' ? 0 : 1];
      if (
        !Number.isFinite(rate) ||
        rate < 0 ||
        rate > stream.bound * (1 + 8 * Number.EPSILON)
      )
        numerical('Conditional intensity exceeds its thinning bound.');
      const accepted = uniform(stream) * stream.bound < rate;
      const packetId = `event:${stream.id}:${stream.count++}`;
      schedule(stream, this.time);
      if (!accepted) continue;
      const route = this.scenario.links.find(
        (l) => l.source === node.id && l.sourcePort === stream.port,
      );
      const record = {
        time: this.time,
        packetId,
        source: node.id,
        port: stream.port,
      };
      this.records.push({ ...record, kind: 'emitted' });
      if (route) {
        const arrivalTime = this.time + route.delay;
        if (!Number.isFinite(arrivalTime) || arrivalTime <= this.time)
          numerical('Packet travel time is not representably positive.');
        this.pending.push({
          id: packetId,
          source: node.id,
          target: route.target,
          emissionTime: this.time,
          arrivalTime,
          port: route.targetPort,
        });
        this.records.push({
          ...record,
          target: route.target,
          port: route.targetPort,
          kind: 'pending',
        });
      } else this.records.push({ ...record, kind: 'escaped' });
    }
    this.filters = nextFilters;
    for (const packet of arrivals)
      this.records.push({
        time: this.time,
        packetId: packet.id,
        source: packet.source,
        target: packet.target,
        port: packet.port,
        kind: 'received',
      });
    this.pending = this.pending
      .filter((p) => p.arrivalTime !== this.time)
      .sort((a, b) => a.arrivalTime - b.arrivalTime || order(a.id, b.id));
    this.events += arrivals.length + candidates.length;
  }
}
