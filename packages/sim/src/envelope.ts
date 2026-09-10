import { Ajv2020 } from 'ajv/dist/2020.js';
import type { ClockNode, Port, Scenario } from '@signal-space/model';

const TAU = 2 * Math.PI;
type Vector = number[];
export interface HistoryPoint {
  time: number;
  nodes: Record<string, { phi: number; omega: number }>;
}
export interface EnvelopePerturbation {
  time: number;
  nodeId: string;
  phaseOffset: number;
  frequencyOffset: number;
}
export interface EnvelopeOptions {
  /** Suppress pre-zero emissions on links, without deleting source history. */
  preparation?: 'established' | 'empty-links';
  /** Cubic Hermite phase data, with omega = d(phi)/dt. */
  prehistory?: HistoryPoint[];
  /** Right-continuous, piecewise constant external rates, starting at t=0. */
  boundaryInputs?: Partial<Record<Port, Array<{ time: number; rate: number }>>>;
  /** Explicit state intervention applied at an exact solver boundary. */
  perturbations?: EnvelopePerturbation[];
  tickSection?: number;
  maxSteps?: number;
}
export interface DenseSegment {
  start: number;
  end: number;
  y0: Vector;
  y1: Vector;
  d0: Vector;
  d1: Vector;
}
export interface AdaptiveAttempt {
  end: number;
  accepted: boolean;
}
export interface EnvelopeSnapshot {
  kind: 'envelope-rk4-v1';
  scenario: Scenario;
  options: EnvelopeOptions;
  time: number;
  state: Vector;
  nextStep: number;
  segments: DenseSegment[];
  attempts: AdaptiveAttempt[];
  acceptedSteps: number;
  rejectedSteps: number;
  /** Post-intervention states needed for exact retarded-history replay. */
  jumps: Array<{ time: number; state: Vector }>;
}
export interface EnvelopeSample {
  time: number;
  nodes: Record<
    string,
    {
      phi: number;
      omega: number;
      rhoLeft: number;
      rhoRight: number;
      integratedLeft: number;
      integratedRight: number;
      ticks: number;
      boundMargin: number;
      receptionLeft: number;
      receptionRight: number;
    }
  >;
  /** Simulator-only source state; not an observer record. */
  retarded: Array<{
    linkId: string;
    sourceTime: number;
    phi: number;
    omega: number;
    rate: number;
  }>;
}
export interface TickCrossing {
  nodeId: string;
  time: number;
  sectionIndex: number;
  direction?: 1 | -1;
}
export class EnvelopeFailure extends Error {
  constructor(
    public code:
      | 'INVALID_REQUEST'
      | 'INVALID_HISTORY'
      | 'UNSUPPORTED_MODEL'
      | 'NUMERICAL_FAILURE',
    message: string,
  ) {
    super(message);
  }
}
function fail(message: string): never {
  throw new EnvelopeFailure('INVALID_HISTORY', message);
}
const ajv = new Ajv2020({ allErrors: true, strict: false });
const validateOptions = ajv.compile({
  type: 'object',
  additionalProperties: false,
  properties: {
    preparation: { enum: ['established', 'empty-links'] },
    tickSection: { type: 'number' },
    maxSteps: { type: 'integer', minimum: 1, maximum: 1000000 },
    prehistory: {
      type: 'array',
      minItems: 2,
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['time', 'nodes'],
        properties: {
          time: { type: 'number', maximum: 0 },
          nodes: {
            type: 'object',
            additionalProperties: {
              type: 'object',
              additionalProperties: false,
              required: ['phi', 'omega'],
              properties: {
                phi: { type: 'number' },
                omega: { type: 'number', exclusiveMinimum: 0 },
              },
            },
          },
        },
      },
    },
    boundaryInputs: {
      type: 'object',
      additionalProperties: false,
      properties: Object.fromEntries(
        ['left', 'right'].map((side) => [
          side,
          {
            type: 'array',
            minItems: 1,
            items: {
              type: 'object',
              additionalProperties: false,
              required: ['time', 'rate'],
              properties: {
                time: { type: 'number', minimum: 0 },
                rate: { type: 'number', minimum: 0 },
              },
            },
          },
        ]),
      ),
    },
    perturbations: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        required: ['time', 'nodeId', 'phaseOffset', 'frequencyOffset'],
        properties: {
          time: { type: 'number', exclusiveMinimum: 0 },
          nodeId: { type: 'string', minLength: 1 },
          phaseOffset: { type: 'number' },
          frequencyOffset: { type: 'number' },
        },
      },
    },
  },
});
function allNumbersFinite(value: unknown): boolean {
  if (typeof value === 'number') return Number.isFinite(value);
  if (Array.isArray(value)) return value.every(allNumbersFinite);
  if (value && typeof value === 'object')
    return Object.values(value).every(allNumbersFinite);
  return true;
}
function stable(value: unknown): string {
  return JSON.stringify(value, (_key, v: unknown) =>
    v && typeof v === 'object' && !Array.isArray(v)
      ? Object.fromEntries(
          Object.entries(v).sort(([a], [b]) => a.localeCompare(b)),
        )
      : v,
  );
}
const PORTABLE_REPLAY_ABSOLUTE_TOLERANCE = 1e-12;
const PORTABLE_REPLAY_MAX_ULPS = 32n;
const PHYSICAL_BOUND_MAX_ULPS = 8n;
const UNRESOLVABLE_INTERVAL_MAX_ULPS = 1n;
const MAX_TICK_CROSSINGS_PER_STEP = 10000;
const FLOAT64_SIGN_BIT = 1n << 63n;
const FLOAT64_MASK = (1n << 64n) - 1n;
const replayBits = new DataView(new ArrayBuffer(8));
function orderedReplayBits(value: number): bigint {
  replayBits.setFloat64(0, value);
  const bits = replayBits.getBigUint64(0);
  return bits & FLOAT64_SIGN_BIT
    ? FLOAT64_MASK - bits
    : FLOAT64_SIGN_BIT + bits;
}
function withinUlps(
  actual: number,
  expected: number,
  maximumDistance: bigint,
): boolean {
  const actualBits = orderedReplayBits(actual),
    expectedBits = orderedReplayBits(expected),
    distance =
      actualBits > expectedBits
        ? actualBits - expectedBits
        : expectedBits - actualBits;
  return distance <= maximumDistance;
}
function float64NextSpacing(value: number): number {
  if (value === 0) return Number.MIN_VALUE;
  replayBits.setFloat64(0, value);
  const bits = replayBits.getBigUint64(0);
  replayBits.setBigUint64(0, value > 0 ? bits + 1n : bits - 1n);
  return replayBits.getFloat64(0) - value;
}
function portableReplayEqual(actual: unknown, expected: unknown): boolean {
  if (typeof actual === 'number' && typeof expected === 'number')
    return (
      Number.isFinite(actual) &&
      Number.isFinite(expected) &&
      (Math.abs(actual - expected) <= PORTABLE_REPLAY_ABSOLUTE_TOLERANCE ||
        withinUlps(actual, expected, PORTABLE_REPLAY_MAX_ULPS))
    );
  if (Array.isArray(actual) || Array.isArray(expected))
    return (
      Array.isArray(actual) &&
      Array.isArray(expected) &&
      actual.length === expected.length &&
      actual.every((value, index) =>
        portableReplayEqual(value, expected[index]),
      )
    );
  if (
    actual &&
    expected &&
    typeof actual === 'object' &&
    typeof expected === 'object'
  ) {
    const actualEntries = Object.entries(actual).sort(([a], [b]) =>
        a.localeCompare(b),
      ),
      expectedEntries = Object.entries(expected).sort(([a], [b]) =>
        a.localeCompare(b),
      );
    return (
      actualEntries.length === expectedEntries.length &&
      actualEntries.every(
        ([key, value], index) =>
          key === expectedEntries[index]![0] &&
          portableReplayEqual(value, expectedEntries[index]![1]),
      )
    );
  }
  return actual === expected;
}
export function emission(
  node: ClockNode,
  phi: number,
  omega: number,
): [number, number] {
  const nu =
    node.emission.law === 'E0'
      ? node.emission.nu
      : (node.emission.q * omega) / TAU;
  const asymmetry = node.amplitude * Math.cos(phi);
  return [(nu * (1 - asymmetry)) / 2, (nu * (1 + asymmetry)) / 2];
}
function cubic(
  a: number,
  b: number,
  da: number,
  db: number,
  h: number,
  u: number,
): number {
  return (
    (2 * u ** 3 - 3 * u ** 2 + 1) * a +
    (u ** 3 - 2 * u ** 2 + u) * h * da +
    (-2 * u ** 3 + 3 * u ** 2) * b +
    (u ** 3 - u ** 2) * h * db
  );
}
function derivative(
  a: number,
  b: number,
  da: number,
  db: number,
  h: number,
  u: number,
): number {
  return (
    ((6 * u * u - 6 * u) * (a - b)) / h +
    (3 * u * u - 4 * u + 1) * da +
    (3 * u * u - 2 * u) * db
  );
}
function dense(s: DenseSegment, time: number): Vector {
  if (time === s.start) return [...s.y0];
  if (time === s.end) return [...s.y1];
  const h = s.end - s.start,
    u = (time - s.start) / h;
  return s.y0.map((a, i) => cubic(a, s.y1[i]!, s.d0[i]!, s.d1[i]!, h, u));
}
/** Extrema of the derivative of a Hermite cubic (a quadratic). */
function derivativeRange(
  a: number,
  b: number,
  da: number,
  db: number,
  h: number,
): [number, number] {
  const A = (6 * (a - b)) / h + 3 * (da + db),
    B = (-6 * (a - b)) / h - 4 * da - 2 * db;
  if (!Number.isFinite(A) || !Number.isFinite(B)) return [NaN, NaN];
  const values = [da, db];
  const u = -B / (2 * A);
  if (u > 0 && u < 1) {
    const value = derivative(a, b, da, db, h, u);
    if (!Number.isFinite(value)) return [NaN, NaN];
    values.push(value);
  }
  return [Math.min(...values), Math.max(...values)];
}
function cubicRange(
  a: number,
  b: number,
  da: number,
  db: number,
  h: number,
): [number, number] {
  const A = (6 * (a - b)) / h + 3 * (da + db),
    B = (-6 * (a - b)) / h - 4 * da - 2 * db;
  const values = [a, b];
  const disc = B * B - 4 * A * da;
  const roots =
    A === 0
      ? B === 0
        ? []
        : [-da / B]
      : disc < 0
        ? []
        : [(-B + Math.sqrt(disc)) / (2 * A), (-B - Math.sqrt(disc)) / (2 * A)];
  for (const u of roots)
    if (u > 0 && u < 1) values.push(cubic(a, b, da, db, h, u));
  return [Math.min(...values), Math.max(...values)];
}
/** Shared transport seam: future mirror/ring adapters must supply positive-delay routes. */
export function envelopeRoutes(scenario: Scenario) {
  return scenario.links.map((link) => ({ ...link }));
}

export class EnvelopeSolver {
  time = 0;
  state: Vector;
  segments: DenseSegment[] = [];
  attempts: AdaptiveAttempt[] = [];
  acceptedSteps = 0;
  rejectedSteps = 0;
  nextStep: number;
  readonly options: EnvelopeOptions;
  private readonly minDelay: number;
  private readonly boundaries: number[];
  private readonly canonicalBoundaryTimes = new Map<number, number>();
  private readonly changes: Array<{
    time: number;
    target: string;
    gain: number;
  }>;
  private readonly perturbations: EnvelopePerturbation[];
  private jumps: Array<{ time: number; state: Vector }> = [];
  constructor(
    readonly scenario: Scenario,
    options: unknown = {},
    snapshot?: unknown,
  ) {
    if (!validateOptions(options))
      throw new EnvelopeFailure(
        'INVALID_REQUEST',
        `Invalid envelope options: ${ajv.errorsText(validateOptions.errors)}`,
      );
    if (!allNumbersFinite(options))
      throw new EnvelopeFailure(
        'INVALID_REQUEST',
        'All numeric envelope option values must be finite.',
      );
    this.options = options as EnvelopeOptions;
    if (scenario.solver.method !== 'rk4')
      throw new EnvelopeFailure(
        'UNSUPPORTED_MODEL',
        'Envelope evolution implements adaptive RK4 step doubling only.',
      );
    if (
      ![
        scenario.solver.step ?? 0.01,
        scenario.solver.absoluteTolerance,
        scenario.solver.relativeTolerance,
      ].every((x) => Number.isFinite(x) && x > 0)
    )
      throw new EnvelopeFailure(
        'INVALID_REQUEST',
        'RK4 step and tolerances must be finite and positive.',
      );
    for (const side of ['left', 'right'] as const) {
      const b = scenario.boundaries[side];
      if (b.kind !== 'open' && b.kind !== 'driven')
        throw new EnvelopeFailure(
          'UNSUPPORTED_MODEL',
          'Mirror/ring transport is reserved for T13.',
        );
      const schedule = this.options.boundaryInputs?.[side];
      if (schedule) {
        if (
          b.kind !== 'driven' ||
          schedule[0]!.time !== 0 ||
          schedule.some((p, i) => i > 0 && p.time <= schedule[i - 1]!.time)
        )
          throw new EnvelopeFailure(
            'INVALID_REQUEST',
            'Boundary schedules require a driven port and strictly increasing times beginning at zero.',
          );
      }
    }
    const h = scenario.initialHistory;
    if (
      h.pendingPackets.length ||
      h.pendingResponses.length ||
      Object.values(h.filters).some((f) => f.left !== 0 || f.right !== 0)
    )
      throw new EnvelopeFailure(
        'UNSUPPORTED_MODEL',
        'Event packets, responses and physical filter memory require the event engine.',
      );
    this.changes = scenario.interventions
      .map((event) => {
        const n = scenario.nodes.find((n) => n.id === event.target);
        const value = event.value as { gain?: unknown } | undefined;
        if (
          event.kind !== 'change-parameter' ||
          !n ||
          !Number.isFinite(event.time) ||
          event.time < 0 ||
          !value ||
          Object.keys(value).length !== 1 ||
          typeof value.gain !== 'number' ||
          !Number.isFinite(value.gain) ||
          Math.abs(value.gain) >= n.omega0 ||
          (n.response === 'R0' && value.gain !== 0)
        )
          throw new EnvelopeFailure(
            'UNSUPPORTED_MODEL',
            'T03 interventions support change-parameter with value {gain}, |gain| < omega0, at nonnegative times only.',
          );
        return { time: event.time, target: event.target, gain: value.gain };
      })
      .sort((a, b) => a.time - b.time);
    this.perturbations = [...(this.options.perturbations ?? [])]
      .map((perturbation) => ({ ...perturbation }))
      .sort((a, b) => a.time - b.time);
    const perturbationKeys = new Set<string>();
    const perturbationTimes = new Map<string, number[]>();
    for (const perturbation of this.perturbations) {
      const node = scenario.nodes.find(
        (candidate) => candidate.id === perturbation.nodeId,
      );
      if (
        !node ||
        !Number.isFinite(perturbation.time) ||
        perturbation.time <= 0 ||
        !Number.isFinite(perturbation.phaseOffset) ||
        !Number.isFinite(perturbation.frequencyOffset)
      )
        throw new EnvelopeFailure(
          'INVALID_REQUEST',
          'Perturbations require an existing node, positive time, and finite phase/frequency offsets.',
        );
      const key = `${perturbation.time}\u0000${perturbation.nodeId}`;
      const priorTimes = perturbationTimes.get(perturbation.nodeId) ?? [];
      if (
        perturbationKeys.has(key) ||
        priorTimes.some((time) =>
          withinUlps(time, perturbation.time, UNRESOLVABLE_INTERVAL_MAX_ULPS),
        )
      )
        throw new EnvelopeFailure(
          'INVALID_REQUEST',
          'A node may have at most one perturbation at a given time.',
        );
      perturbationKeys.add(key);
      priorTimes.push(perturbation.time);
      perturbationTimes.set(perturbation.nodeId, priorTimes);
    }
    // Carry derivative discontinuities through four transport generations for RK4.
    // Each feedback integration raises differentiability by one; data knots and
    // source startup must still be explicit method-of-steps boundaries.
    const pending = [
      ...scenario.nodes.map((n) => ({ time: 0, nodeId: n.id, depth: 0 })),
      ...this.changes.map((c) => ({
        time: c.time,
        nodeId: c.target,
        depth: 0,
      })),
      ...this.perturbations.map((p) => ({
        time: p.time,
        nodeId: p.nodeId,
        depth: 0,
      })),
      ...(this.options.boundaryInputs?.left ?? []).map((p) => ({
        time: p.time,
        nodeId: scenario.nodes[0]!.id,
        depth: 0,
      })),
      ...(this.options.boundaryInputs?.right ?? []).map((p) => ({
        time: p.time,
        nodeId: scenario.nodes.at(-1)!.id,
        depth: 0,
      })),
      ...(this.options.prehistory ?? []).flatMap((p) =>
        scenario.nodes.map((n) => ({ time: p.time, nodeId: n.id, depth: 0 })),
      ),
    ];
    const boundarySet = new Set<number>();
    const visited = new Set<string>();
    for (let index = 0; index < pending.length; index++) {
      const point = pending[index]!;
      const key = JSON.stringify(point);
      if (visited.has(key)) continue;
      visited.add(key);
      if (point.time >= 0) boundarySet.add(point.time);
      if (point.depth < 4)
        for (const link of scenario.links)
          if (link.source === point.nodeId) {
            const time = point.time + link.delay;
            if (!Number.isFinite(time))
              throw new EnvelopeFailure(
                'NUMERICAL_FAILURE',
                'Delayed discontinuity time overflowed.',
              );
            pending.push({ time, nodeId: link.target, depth: point.depth + 1 });
          }
      if (pending.length > 1000000)
        throw new EnvelopeFailure(
          'INVALID_REQUEST',
          'Too many propagated discontinuity boundaries.',
        );
    }
    this.boundaries = [];
    for (const time of [...boundarySet].sort((a, b) => a - b)) {
      const previous = this.boundaries.at(-1);
      if (
        previous === undefined ||
        !withinUlps(time, previous, UNRESOLVABLE_INTERVAL_MAX_ULPS)
      )
        this.boundaries.push(time);
      this.canonicalBoundaryTimes.set(time, this.boundaries.at(-1)!);
    }
    this.minDelay = Math.min(
      Infinity,
      ...envelopeRoutes(scenario).map((l) => l.delay),
    );
    this.nextStep = Math.min(scenario.solver.step ?? 0.01, this.minDelay);
    this.state = scenario.nodes.flatMap((n) => [n.phi, n.omega, 0, 0]);
    this.validatePrehistory();
    if (snapshot !== undefined) {
      try {
        this.restore(snapshot);
      } catch (error) {
        if (error instanceof EnvelopeFailure) throw error;
        fail('Checkpoint must contain finite, serializable complete history.');
      }
    }
    this.scenario.nodes.forEach((node, index) => {
      this.tickIndex(node.phi);
      this.tickIndex(this.state[index * 4]!);
    });
  }
  private tolerance(x: number) {
    return (
      this.scenario.solver.absoluteTolerance +
      this.scenario.solver.relativeTolerance * Math.abs(x)
    );
  }
  private gain(node: ClockNode, time: number, left = false): number {
    let gain = node.gain;
    for (const change of this.changes)
      if (
        change.target === node.id &&
        (this.canonicalBoundaryTimes.get(change.time)! < time ||
          (!left && this.canonicalBoundaryTimes.get(change.time)! === time))
      )
        gain = change.gain;
    return gain;
  }
  private bounds(
    node: ClockNode,
    time: number,
    left = false,
  ): [number, number] {
    // After a gain decrease, the old state can lie outside the new target interval.
    let radius = Math.abs(node.gain);
    for (const c of this.changes)
      if (
        c.target === node.id &&
        (this.canonicalBoundaryTimes.get(c.time)! < time ||
          (!left && this.canonicalBoundaryTimes.get(c.time)! === time))
      )
        radius = Math.max(radius, Math.abs(c.gain));
    return [node.omega0 - radius, node.omega0 + radius];
  }
  private validatePrehistory() {
    const points = this.options.prehistory;
    if (!points) return;
    if (
      points[0]!.time > this.scenario.initialHistory.startTime ||
      points.at(-1)!.time !== 0
    )
      fail(
        'Explicit prehistory must cover the declared history interval through zero.',
      );
    points.forEach((p, i) => {
      if (
        Object.keys(p.nodes).length !== this.scenario.nodes.length ||
        (i > 0 && p.time <= points[i - 1]!.time)
      )
        fail('History requires all node IDs and strictly increasing times.');
      for (const n of this.scenario.nodes) {
        const v = p.nodes[n.id];
        if (!v) fail(`Missing history node ${n.id}.`);
        if (i === points.length - 1 && (v.phi !== n.phi || v.omega !== n.omega))
          fail('History endpoint must equal the initial state.');
        if (i > 0) {
          const prior = points[i - 1]!,
            a = prior.nodes[n.id]!;
          const [lo, hi] = derivativeRange(
            a.phi,
            v.phi,
            a.omega,
            v.omega,
            p.time - prior.time,
          );
          const [lower, upper] = this.bounds(n, 0, true);
          if (
            !Number.isFinite(lo) ||
            !Number.isFinite(hi) ||
            (lo < lower && !withinUlps(lo, lower, PHYSICAL_BOUND_MAX_ULPS)) ||
            (hi > upper && !withinUlps(hi, upper, PHYSICAL_BOUND_MAX_ULPS)) ||
            lo <= 0
          )
            fail(
              'History phase derivative must remain in the admissible frequency interval, including between knots.',
            );
        }
      }
    });
  }
  private source(time: number, left = false): Vector {
    if (
      time > this.time &&
      withinUlps(time, this.time, UNRESOLVABLE_INTERVAL_MAX_ULPS)
    )
      return [...this.state];
    if (time > this.time)
      throw new EnvelopeFailure(
        'NUMERICAL_FAILURE',
        'Retarded query would use future state.',
      );
    if (time < this.scenario.initialHistory.startTime)
      fail('Retarded query is outside saved prehistory.');
    const jump = [...this.jumps]
      .reverse()
      .find(
        (candidate) =>
          withinUlps(time, candidate.time, UNRESOLVABLE_INTERVAL_MAX_ULPS) &&
          !left,
      );
    if (jump) return [...jump.state];
    if (time <= 0) {
      const points = this.options.prehistory;
      if (!points)
        return this.scenario.nodes.flatMap((n) => [
          n.phi + n.omega * time,
          n.omega,
          0,
          0,
        ]);
      const i = Math.max(
        1,
        points.findIndex((p) => p.time >= time),
      );
      const a = points[i - 1]!,
        b = points[i]!,
        h = b.time - a.time,
        u = (time - a.time) / h;
      return this.scenario.nodes.flatMap((n) => {
        const x = a.nodes[n.id]!,
          y = b.nodes[n.id]!;
        return [
          cubic(x.phi, y.phi, x.omega, y.omega, h, u),
          derivative(x.phi, y.phi, x.omega, y.omega, h, u),
          0,
          0,
        ];
      });
    }
    if (time === this.time) return [...this.state];
    let lo = 0,
      hi = this.segments.length - 1;
    while (lo < hi) {
      const mid = (lo + hi) >>> 1;
      if (this.segments[mid]!.end < time) lo = mid + 1;
      else hi = mid;
    }
    const s = this.segments[lo];
    if (!s || time < s.start || time > s.end)
      fail('Missing evolved history segment.');
    return dense(s, time);
  }
  private reception(time: number, left = false) {
    const inputs = this.scenario.nodes.map(() => [0, 0]);
    const retarded: EnvelopeSample['retarded'] = [];
    for (const l of this.scenario.links) {
      const sourceTime = time - l.delay;
      const j = this.scenario.nodes.findIndex((n) => n.id === l.source),
        i = this.scenario.nodes.findIndex((n) => n.id === l.target);
      const state = this.source(sourceTime, left),
        phi = state[j * 4]!,
        omega = state[j * 4 + 1]!;
      const suppressed =
        this.options.preparation === 'empty-links' &&
        (sourceTime < 0 || (left && sourceTime === 0));
      const rate = suppressed
        ? 0
        : emission(this.scenario.nodes[j]!, phi, omega)[
            l.sourcePort === 'left' ? 0 : 1
          ];
      inputs[i]![l.targetPort === 'left' ? 0 : 1] = rate;
      retarded.push({ linkId: l.id, sourceTime, phi, omega, rate });
    }
    for (const side of ['left', 'right'] as const) {
      const b = this.scenario.boundaries[side];
      if (b.kind !== 'driven') continue;
      let rate = b.rate;
      for (const point of this.options.boundaryInputs?.[side] ?? [])
        if (
          this.canonicalBoundaryTimes.get(point.time)! < time ||
          (!left && this.canonicalBoundaryTimes.get(point.time)! === time)
        )
          rate = point.rate;
      inputs[side === 'left' ? 0 : inputs.length - 1]![
        side === 'left' ? 0 : 1
      ] = rate;
    }
    return { inputs, retarded };
  }
  private rhs(time: number, y: Vector, left = false): Vector {
    const { inputs } = this.reception(time, left);
    return this.scenario.nodes.flatMap((n, i) => {
      const phi = y[i * 4]!,
        omega = y[i * 4 + 1]!;
      const target =
        n.omega0 +
        this.gain(n, time, left) *
          (n.response === 'R2' ? Math.cos(2 * phi) : 1) *
          Math.tanh(
            (inputs[i]![0]! + inputs[i]![1]!) / this.scenario.rateScale,
          );
      const [l, r] = emission(n, phi, omega);
      return [omega, (target - omega) / n.relaxationTime, l, r];
    });
  }
  private applyPerturbations(time: number): TickCrossing[] {
    const due = this.perturbations.filter((perturbation) =>
      withinUlps(
        this.canonicalBoundaryTimes.get(perturbation.time) ?? NaN,
        time,
        UNRESOLVABLE_INTERVAL_MAX_ULPS,
      ),
    );
    if (!due.length) return [];
    const before = new Map(
      this.scenario.nodes.map((node, index) => [
        node.id,
        this.state[index * 4]!,
      ]),
    );
    this.state = [...this.state];
    for (const perturbation of due) {
      const index = this.scenario.nodes.findIndex(
        (node) => node.id === perturbation.nodeId,
      );
      const node = this.scenario.nodes[index]!;
      const k = index * 4;
      this.state[k] = this.state[k]! + perturbation.phaseOffset;
      this.state[k + 1] = this.state[k + 1]! + perturbation.frequencyOffset;
      const [lower, upper] = this.bounds(node, time);
      if (
        !Number.isFinite(this.state[k]!) ||
        !Number.isFinite(this.state[k + 1]!) ||
        this.state[k + 1]! <= 0 ||
        this.state[k + 1]! < lower ||
        this.state[k + 1]! > upper
      )
        throw new EnvelopeFailure(
          'INVALID_REQUEST',
          `Perturbation at ${time} leaves node ${node.id} outside its admissible frequency bounds.`,
        );
    }
    this.jumps.push({ time, state: [...this.state] });
    const ticks: TickCrossing[] = [];
    for (const [index, node] of this.scenario.nodes.entries()) {
      const from = this.tickIndex(before.get(node.id)!);
      const to = this.tickIndex(this.state[index * 4]!);
      if (Math.abs(to - from) > MAX_TICK_CROSSINGS_PER_STEP)
        throw new EnvelopeFailure(
          'NUMERICAL_FAILURE',
          'Tick indices exceed representable or per-step output limits.',
        );
      if (to > from)
        for (let sectionIndex = from + 1; sectionIndex <= to; sectionIndex++)
          ticks.push({ nodeId: node.id, time, sectionIndex, direction: 1 });
      if (to < from)
        for (let sectionIndex = to + 1; sectionIndex <= from; sectionIndex++)
          ticks.push({ nodeId: node.id, time, sectionIndex, direction: -1 });
    }
    return ticks;
  }
  private rk4(t: number, y: Vector, end: number, left: boolean): DenseSegment {
    const h = end - t;
    const add = (k: Vector, scale: number) =>
      y.map((v, i) => v + scale * k[i]!);
    const a = this.rhs(t, y),
      b = this.rhs(t + h / 2, add(a, h / 2)),
      c = this.rhs(t + h / 2, add(b, h / 2)),
      d = this.rhs(end, add(c, h), left);
    const y1 = y.map(
      (v, i) => v + (h * (a[i]! + 2 * b[i]! + 2 * c[i]! + d[i]!)) / 6,
    );
    return {
      start: t,
      end,
      y0: [...y],
      y1,
      d0: a,
      d1: this.rhs(end, y1, left),
    };
  }
  private validSegment(s: DenseSegment): boolean {
    if (![...s.y0, ...s.y1, ...s.d0, ...s.d1].every(Number.isFinite))
      return false;
    return this.scenario.nodes.every((n, i) => {
      const k = i * 4,
        h = s.end - s.start;
      const [lo, hi] = cubicRange(
        s.y0[k + 1]!,
        s.y1[k + 1]!,
        s.d0[k + 1]!,
        s.d1[k + 1]!,
        h,
      );
      const [lower, upper] = this.bounds(n, s.end, true);
      const [phaseRate] = derivativeRange(
        s.y0[k]!,
        s.y1[k]!,
        s.d0[k]!,
        s.d1[k]!,
        h,
      );
      const intensitiesMonotone = [2, 3].every(
        (offset) =>
          derivativeRange(
            s.y0[k + offset]!,
            s.y1[k + offset]!,
            s.d0[k + offset]!,
            s.d1[k + offset]!,
            h,
          )[0] >= 0,
      );
      return (
        lo > 0 &&
        (lo >= lower || withinUlps(lo, lower, PHYSICAL_BOUND_MAX_ULPS)) &&
        (hi <= upper || withinUlps(hi, upper, PHYSICAL_BOUND_MAX_ULPS)) &&
        phaseRate > 0 &&
        intensitiesMonotone
      );
    });
  }
  /** Reproduce the complete acceptance estimate for one retained step pair. */
  private adaptiveError(
    coarse: DenseSegment,
    first: DenseSegment,
    second: DenseSegment,
  ): number {
    let error = Math.max(
      ...second.y1.map(
        (v, i) => Math.abs(v - coarse.y1[i]!) / (15 * this.tolerance(v)),
      ),
    );
    for (const s of [first, second]) {
      const midpoint = this.rk4(s.start, s.y0, (s.start + s.end) / 2, false).y1;
      error = Math.max(
        error,
        ...dense(s, (s.start + s.end) / 2).map(
          (v, i) => Math.abs(v - midpoint[i]!) / this.tolerance(midpoint[i]!),
        ),
      );
    }
    return error;
  }
  /** Apply the same proposal update used after every adaptive trial. */
  private proposedStep(h: number, error: number, valid: boolean): number {
    const factor =
      !Number.isFinite(error) || !valid
        ? 0.5
        : error === 0
          ? 2
          : Math.min(2, Math.max(0.2, 0.9 * error ** -0.2));
    return Math.min(
      this.scenario.solver.step ?? 0.01,
      this.minDelay,
      h * factor,
    );
  }
  private tickIndex(phi: number): number {
    const section = this.options.tickSection ?? 0,
      spacing = Math.max(float64NextSpacing(phi), float64NextSpacing(section)),
      index = Math.floor((phi - section) / TAU),
      lower = section + index * TAU,
      upper = section + (index + 1) * TAU;
    if (
      !Number.isSafeInteger(index) ||
      !Number.isFinite(spacing) ||
      spacing >= TAU ||
      !Number.isFinite(lower) ||
      !Number.isFinite(upper) ||
      !(upper > lower) ||
      phi < lower ||
      phi >= upper
    )
      throw new EnvelopeFailure(
        'NUMERICAL_FAILURE',
        'Tick indices exceed representable or per-step output limits.',
      );
    return index;
  }
  /** Direct and propagated discontinuities are exact step endpoints. */
  private nextBoundary(until: number): number {
    let lo = 0,
      hi = this.boundaries.length;
    while (lo < hi) {
      const mid = (lo + hi) >>> 1;
      if (this.boundaries[mid]! <= this.time) lo = mid + 1;
      else hi = mid;
    }
    return Math.min(until, this.boundaries[lo] ?? Infinity);
  }
  advance(until: number): TickCrossing[] {
    if (
      this.acceptedSteps + this.rejectedSteps >=
      (this.options.maxSteps ?? 100000)
    )
      throw new EnvelopeFailure(
        'NUMERICAL_FAILURE',
        'Step budget exhausted; increase maxSteps or revise the solver settings.',
      );
    const boundary = this.nextBoundary(until);
    let end = Math.min(
      this.time + Math.min(this.nextStep, this.minDelay),
      boundary,
    );
    // Do not create an unresolvable tail solely from floating-point addition.
    if (
      boundary - end <=
      8 * Number.EPSILON * Math.max(Math.abs(boundary), Math.abs(end))
    )
      end = boundary;
    const h = end - this.time;
    if (h <= 0 || this.time + h / 2 === this.time)
      throw new EnvelopeFailure(
        'NUMERICAL_FAILURE',
        'Step underflow; requested tolerance or time scale is not representable.',
      );
    const coarse = this.rk4(this.time, this.state, end, true);
    const first = this.rk4(this.time, this.state, this.time + h / 2, false);
    const second = this.rk4(first.end, first.y1, end, true);
    // Local RK4 error plus midpoint error of the retained cubic dense output.
    const error = this.adaptiveError(coarse, first, second);
    const valid = this.validSegment(first) && this.validSegment(second);
    this.nextStep = this.proposedStep(h, error, valid);
    const accepted = Number.isFinite(error) && error <= 1 && valid;
    this.attempts.push({ end, accepted });
    if (!accepted) {
      this.rejectedSteps++;
      return [];
    }
    const ticks: TickCrossing[] = [];
    for (const s of [first, second])
      for (const [i, n] of this.scenario.nodes.entries()) {
        const section = this.options.tickSection ?? 0,
          from = this.tickIndex(s.y0[i * 4]!),
          to = this.tickIndex(s.y1[i * 4]!);
        if (Math.abs(to - from) > MAX_TICK_CROSSINGS_PER_STEP)
          throw new EnvelopeFailure(
            'NUMERICAL_FAILURE',
            'Tick indices exceed representable or per-step output limits.',
          );
        for (let index = from + 1; index <= to; index++) {
          const target = section + index * TAU;
          let lo = s.start,
            hi = s.end;
          for (let iteration = 0; iteration < 52; iteration++) {
            const mid = (lo + hi) / 2;
            if (dense(s, mid)[i * 4]! < target) lo = mid;
            else hi = mid;
          }
          ticks.push({
            nodeId: n.id,
            time: (lo + hi) / 2,
            sectionIndex: index,
          });
        }
      }
    this.segments.push(first, second);
    this.time = end;
    this.state = second.y1;
    const perturbationTicks = this.applyPerturbations(end);
    this.acceptedSteps++;
    return [...ticks, ...perturbationTicks].sort((a, b) => a.time - b.time);
  }
  sample(): EnvelopeSample {
    const { inputs, retarded } = this.reception(this.time);
    const result = {
      time: this.time,
      retarded,
      nodes: Object.fromEntries(
        this.scenario.nodes.map((n, i) => {
          const phi = this.state[i * 4]!,
            omega = this.state[i * 4 + 1]!,
            [rhoLeft, rhoRight] = emission(n, phi, omega),
            [lower, upper] = this.bounds(n, this.time);
          return [
            n.id,
            {
              phi,
              omega,
              rhoLeft,
              rhoRight,
              integratedLeft: this.state[i * 4 + 2]!,
              integratedRight: this.state[i * 4 + 3]!,
              ticks: this.tickIndex(phi) - this.tickIndex(n.phi),
              boundMargin: Math.min(omega - lower, upper - omega),
              receptionLeft: inputs[i]![0]!,
              receptionRight: inputs[i]![1]!,
            },
          ];
        }),
      ),
    };
    if (
      Object.values(result.nodes).some((n) =>
        Object.values(n).some((v) => !Number.isFinite(v)),
      ) ||
      result.retarded.some(
        (r) => ![r.sourceTime, r.phi, r.omega, r.rate].every(Number.isFinite),
      )
    )
      throw new EnvelopeFailure(
        'NUMERICAL_FAILURE',
        'State, emission or retarded evaluation overflowed.',
      );
    return result;
  }
  snapshot(): EnvelopeSnapshot {
    return structuredClone({
      kind: 'envelope-rk4-v1',
      scenario: this.scenario,
      options: this.options,
      time: this.time,
      state: this.state,
      nextStep: this.nextStep,
      segments: this.segments,
      attempts: this.attempts,
      acceptedSteps: this.acceptedSteps,
      rejectedSteps: this.rejectedSteps,
      jumps: this.jumps,
    });
  }
  private restore(value: unknown) {
    const s = value as EnvelopeSnapshot | null;
    if (
      !s ||
      s.kind !== 'envelope-rk4-v1' ||
      stable(s.scenario) !== stable(this.scenario) ||
      stable(s.options) !== stable(this.options)
    )
      fail(
        'Checkpoint must match the scenario, preparation and solver options.',
      );
    const vector = (v: unknown): v is Vector =>
      Array.isArray(v) &&
      v.length === this.state.length &&
      v.every(Number.isFinite);
    if (
      !Number.isFinite(s.time) ||
      s.time < 0 ||
      !Number.isFinite(s.nextStep) ||
      s.nextStep <= 0 ||
      s.nextStep > Math.min(this.scenario.solver.step ?? 0.01, this.minDelay) ||
      !vector(s.state) ||
      !Array.isArray(s.segments) ||
      !Array.isArray(s.attempts) ||
      (s.jumps !== undefined && !Array.isArray(s.jumps)) ||
      !Number.isSafeInteger(s.acceptedSteps) ||
      s.acceptedSteps < 0 ||
      !Number.isSafeInteger(s.rejectedSteps) ||
      s.rejectedSteps < 0 ||
      s.acceptedSteps + s.rejectedSteps > (this.options.maxSteps ?? 100000) ||
      s.segments.length !== s.acceptedSteps * 2 ||
      s.attempts.length !== s.acceptedSteps + s.rejectedSteps ||
      s.attempts.some(
        (attempt) =>
          !attempt ||
          !Number.isFinite(attempt.end) ||
          typeof attempt.accepted !== 'boolean',
      ) ||
      s.attempts.filter((attempt) => attempt.accepted).length !==
        s.acceptedSteps
    )
      fail('Malformed checkpoint state, step metadata, or attempt budget.');
    let end = 0,
      state = this.state,
      proposedStep = this.nextStep,
      segmentIndex = 0,
      acceptedSteps = 0,
      rejectedSteps = 0;
    for (const attempt of s.attempts) {
      this.time = end;
      this.state = state;
      const step = attempt.end - end,
        midpoint = end + step / 2;
      if (
        step <= 0 ||
        end + step / 2 === end ||
        step > Math.min(proposedStep, this.minDelay) * (1 + 1e-12)
      )
        fail(
          'Checkpoint attempt trace violates adaptive step-size growth controls.',
        );
      if (this.nextBoundary(attempt.end) !== attempt.end)
        fail('Checkpoint RK4 attempt crosses a scheduled solver boundary.');
      const coarse = this.rk4(end, state, attempt.end, true),
        replayFirst = this.rk4(end, state, midpoint, false),
        replaySecond = this.rk4(
          replayFirst.end,
          replayFirst.y1,
          attempt.end,
          true,
        ),
        error = this.adaptiveError(coarse, replayFirst, replaySecond),
        valid =
          this.validSegment(replayFirst) && this.validSegment(replaySecond),
        accepted = Number.isFinite(error) && error <= 1 && valid,
        portableThresholdDisagreement =
          valid &&
          Number.isFinite(error) &&
          Math.abs(error - 1) <= PORTABLE_REPLAY_ABSOLUTE_TOLERANCE;
      if (accepted !== attempt.accepted && !portableThresholdDisagreement)
        fail(
          'Checkpoint attempt outcome disagrees with adaptive controller replay.',
        );
      proposedStep = this.proposedStep(step, error, valid);
      if (!attempt.accepted) {
        rejectedSteps++;
        continue;
      }
      const first = s.segments[segmentIndex++],
        second = s.segments[segmentIndex++];
      if (!first || !second)
        fail('Checkpoint history must contain complete RK4 half-step pairs.');
      if (
        first.start !== end ||
        first.end !== midpoint ||
        second.end !== attempt.end ||
        second.start !== midpoint ||
        !portableReplayEqual(first.y0, state) ||
        stable(second.y0) !== stable(first.y1)
      )
        fail('Checkpoint history must contain contiguous RK4 half-step pairs.');
      for (const [segment, replay] of [
        [first, replayFirst],
        [second, replaySecond],
      ] as const) {
        if (
          !Number.isFinite(segment.start) ||
          !Number.isFinite(segment.end) ||
          segment.end <= segment.start ||
          segment.end - segment.start >
            (Math.min(this.scenario.solver.step ?? 0.01, this.minDelay) / 2) *
              (1 + 1e-12) ||
          ![segment.y0, segment.y1, segment.d0, segment.d1].every(vector) ||
          !this.validSegment(segment)
        )
          fail(
            'Checkpoint history is nonfinite, discontinuous, or outside physical bounds.',
          );
        for (let i = 0; i < this.scenario.nodes.length; i++)
          if (
            segment.d0[i * 4] !== segment.y0[i * 4 + 1] ||
            segment.d1[i * 4] !== segment.y1[i * 4 + 1]
          )
            fail('Saved phase derivatives must equal saved frequency.');
        for (const [actual, expected] of [
          [segment.d0, this.rhs(segment.start, segment.y0)],
          [segment.d1, this.rhs(segment.end, segment.y1, true)],
        ])
          if (
            actual!.some(
              (v, i) =>
                Math.abs(v - expected![i]!) >
                1e-10 * (1 + Math.abs(expected![i]!)),
            )
          )
            fail(
              'Checkpoint derivatives disagree with saved causal inputs and model equations.',
            );
        if (!portableReplayEqual(segment, replay))
          fail(
            'Checkpoint state increments disagree with replayed RK4 history.',
          );
      }
      end = replaySecond.end;
      state = replaySecond.y1;
      this.time = end;
      this.state = state;
      this.segments.push(replayFirst, replaySecond);
      this.applyPerturbations(end);
      state = this.state;
      acceptedSteps++;
    }
    if (
      acceptedSteps !== s.acceptedSteps ||
      rejectedSteps !== s.rejectedSteps ||
      segmentIndex !== s.segments.length
    )
      fail('Checkpoint attempt trace disagrees with saved step counters.');
    if (end !== s.time || !portableReplayEqual(state, s.state))
      fail('Checkpoint endpoint disagrees with complete history.');
    if (!portableReplayEqual(s.nextStep, proposedStep))
      fail('Checkpoint next step disagrees with adaptive controller replay.');
    const savedJumps = s.jumps ?? [];
    if (
      savedJumps.some(
        (jump) =>
          !Number.isFinite(jump.time) ||
          jump.time <= 0 ||
          !Array.isArray(jump.state) ||
          !vector(jump.state),
      ) ||
      !savedJumps.every(
        (jump, index) => jump.time === this.jumps[index]?.time,
      ) ||
      !portableReplayEqual(savedJumps, this.jumps)
    )
      fail('Checkpoint perturbation history disagrees with replay.');
    this.time = s.time;
    this.state = s.state;
    this.nextStep = s.nextStep;
    this.segments = s.segments;
    this.attempts = s.attempts;
    this.acceptedSteps = s.acceptedSteps;
    this.rejectedSteps = s.rejectedSteps;
    this.jumps = savedJumps;
  }
}
