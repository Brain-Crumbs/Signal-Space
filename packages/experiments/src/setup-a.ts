import type { Scenario } from '@signal-space/model';
import {
  EnvelopeSolver,
  type EnvelopeOptions,
  type EnvelopeSample,
  type TickCrossing,
} from '@signal-space/sim';
import isolated from '../../../fixtures/scenarios/isolated.json' with { type: 'json' };
import type { ExperimentDefinition } from './runs.js';

const TAU = 2 * Math.PI;
const NODE_ID = 'A';
const DEFAULT_DURATION = 2;
const DEFAULT_GAIN = 0.5;

export type SetupAProtocolId =
  | 'isolated'
  | 'equal-constant'
  | 'unequal-fixed-sum'
  | 'periodic'
  | 'finite-pulse'
  | 'equal-integral-early'
  | 'equal-integral-late';
export type SetupAVariantId =
  'R0' | 'R1-positive' | 'R1-negative' | 'R2-positive' | 'R2-negative';

export interface SetupAInputPoint {
  time: number;
  left: number;
  right: number;
}

export interface SetupAProtocol {
  id: SetupAProtocolId;
  label: string;
  description: string;
  duration: number;
  points: SetupAInputPoint[];
  inputSemantics: 'none' | 'piecewise-constant';
  filterRole: 'diagnostic-only';
}

export interface SetupAVariant {
  id: SetupAVariantId;
  response: 'R0' | 'R1' | 'R2';
  gain: number;
  label: string;
}

export interface SetupAPresetMetadata {
  id: SetupAProtocolId;
  label: string;
  units: { time: 's'; rate: 's^-1'; phase: 'rad' };
  assumptions: string[];
  protocol: SetupAProtocolId;
}

export interface SetupAFilterSample {
  left: number;
  right: number;
  sum: number;
}

export interface SetupATrajectorySample {
  time: number;
  phi: number;
  omega: number;
  phaseDisplacement: number;
  omegaTarget: number;
  boundMargin: number;
  inputLeft: number;
  inputRight: number;
  inputSum: number;
  filter: SetupAFilterSample;
}

export interface SetupARunSummary {
  initialOmega: number;
  finalOmega: number;
  minimumOmega: number;
  maximumOmega: number;
  minimumBoundMargin: number;
  finalPhaseDisplacement: number;
  inputIntegral: number;
  filterPeak: number;
  relaxation: {
    finalTarget: number;
    finalError: number;
    timeToTolerance: number | null;
    tolerance: number;
  };
  nextTick: {
    time: number;
    sectionIndex: number;
  } | null;
  nextTickStatus: 'in-window' | 'missing-in-window';
}

export interface SetupARun {
  schemaVersion: 'setup-a-diagnostic-v1';
  modelVersion: 'paper-i-v1';
  protocol: SetupAProtocol;
  variant: SetupAVariant;
  scenario: Scenario;
  envelope: EnvelopeOptions;
  samples: SetupATrajectorySample[];
  ticks: TickCrossing[];
  summary: SetupARunSummary;
  limitations: string[];
}

export interface SetupAResponsePoint {
  protocol: SetupAProtocolId;
  variant: SetupAVariantId;
  pulsePhase: number | null;
  pulseAmplitude: number | null;
  inputIntegral: number;
  finalPhaseDisplacement: number;
  finalOmega: number;
  finalOmegaTarget: number;
  minimumBoundMargin: number;
  filterPeak: number;
  nextTick: number | null;
  nextTickStatus: 'in-window' | 'missing-in-window';
}

export interface SetupAResponseCurve {
  schemaVersion: 'setup-a-response-curve-v1';
  protocol: 'finite-pulse';
  variant: SetupAVariantId;
  points: SetupAResponsePoint[];
  controls: {
    sameIntegratedInput: boolean;
    phaseDefinition: string;
    scientificInterpretation: 'deferred';
  };
  limitations: string[];
}

export const setupAVariants: readonly SetupAVariant[] = [
  { id: 'R0', response: 'R0', gain: 0, label: 'R0: no feedback' },
  {
    id: 'R1-positive',
    response: 'R1',
    gain: DEFAULT_GAIN,
    label: 'R1: positive gain',
  },
  {
    id: 'R1-negative',
    response: 'R1',
    gain: -DEFAULT_GAIN,
    label: 'R1: negative gain',
  },
  {
    id: 'R2-positive',
    response: 'R2',
    gain: DEFAULT_GAIN,
    label: 'R2: positive gain',
  },
  {
    id: 'R2-negative',
    response: 'R2',
    gain: -DEFAULT_GAIN,
    label: 'R2: negative gain',
  },
];

export const setupAPresets: readonly SetupAPresetMetadata[] = [
  {
    id: 'isolated',
    label: 'Isolated B',
    protocol: 'isolated',
    units: { time: 's', rate: 's^-1', phase: 'rad' },
    assumptions: [
      'No links or driven boundary inputs.',
      'R0 is the analytic baseline.',
    ],
  },
  {
    id: 'equal-constant',
    label: 'Equal constant inputs',
    protocol: 'equal-constant',
    units: { time: 's', rate: 's^-1', phase: 'rad' },
    assumptions: [
      'Left and right rates are equal and constant.',
      'The scalar feedback input is their sum.',
    ],
  },
  {
    id: 'unequal-fixed-sum',
    label: 'Unequal inputs with fixed sum',
    protocol: 'unequal-fixed-sum',
    units: { time: 's', rate: 's^-1', phase: 'rad' },
    assumptions: [
      'Port rates switch at declared times.',
      'The total input remains fixed at each schedule segment.',
    ],
  },
  {
    id: 'periodic',
    label: 'Periodic piecewise input',
    protocol: 'periodic',
    units: { time: 's', rate: 's^-1', phase: 'rad' },
    assumptions: [
      'Periodic means an explicitly saved piecewise-constant schedule.',
      'No smooth periodic forcing is inferred.',
    ],
  },
  {
    id: 'finite-pulse',
    label: 'Finite pulse',
    protocol: 'finite-pulse',
    units: { time: 's', rate: 's^-1', phase: 'rad' },
    assumptions: [
      'The pulse is a prescribed boundary input.',
      'Pulse phase is converted to a start time using the initial omega.',
    ],
  },
  {
    id: 'equal-integral-early',
    label: 'Equal-integral sequence: early',
    protocol: 'equal-integral-early',
    units: { time: 's', rate: 's^-1', phase: 'rad' },
    assumptions: [
      'This is a temporal-order control, not an equality claim for the response.',
      'Integrated input is matched to the late sequence.',
    ],
  },
  {
    id: 'equal-integral-late',
    label: 'Equal-integral sequence: late',
    protocol: 'equal-integral-late',
    units: { time: 's', rate: 's^-1', phase: 'rad' },
    assumptions: [
      'This is a temporal-order control, not an equality claim for the response.',
      'Integrated input is matched to the early sequence.',
    ],
  },
];

export interface SetupAProtocolOptions {
  duration?: number;
  pulsePhase?: number;
  pulseAmplitude?: number;
  pulseWidth?: number;
}

function finite(value: number, name: string): void {
  if (!Number.isFinite(value)) throw new RangeError(`${name} must be finite.`);
}

function clone<T>(value: T): T {
  return structuredClone(value);
}

function validatePoints(points: SetupAInputPoint[], duration: number): void {
  if (!points.length || points[0]!.time !== 0)
    throw new RangeError('Setup A schedules must begin at t=0.');
  let previous = -Infinity;
  for (const point of points) {
    finite(point.time, 'input schedule time');
    finite(point.left, 'left input rate');
    finite(point.right, 'right input rate');
    if (point.time <= previous || point.time < 0 || point.time >= duration)
      throw new RangeError(
        'Setup A schedule times must increase within the run.',
      );
    if (point.left < 0 || point.right < 0)
      throw new RangeError('Setup A input rates must be nonnegative.');
    previous = point.time;
  }
}

function protocol(
  id: SetupAProtocolId,
  label: string,
  description: string,
  points: SetupAInputPoint[],
  duration = DEFAULT_DURATION,
): SetupAProtocol {
  finite(duration, 'Setup A duration');
  if (duration <= 0) throw new RangeError('Setup A duration must be positive.');
  validatePoints(points, duration);
  return {
    id,
    label,
    description,
    duration,
    points: clone(points),
    inputSemantics: id === 'isolated' ? 'none' : 'piecewise-constant',
    filterRole: 'diagnostic-only',
  };
}

export function createSetupAProtocol(
  id: SetupAProtocolId,
  options: SetupAProtocolOptions = {},
): SetupAProtocol {
  const duration =
    options.duration ?? (id === 'finite-pulse' ? 4 : DEFAULT_DURATION);
  if (id === 'isolated')
    return protocol(
      id,
      'Isolated B',
      'An isolated clock with no generated or prescribed arrivals.',
      [{ time: 0, left: 0, right: 0 }],
      duration,
    );
  if (id === 'equal-constant')
    return protocol(
      id,
      'Equal constant inputs',
      'Two equal prescribed rates provide a constant scalar input.',
      [{ time: 0, left: 0.5, right: 0.5 }],
      duration,
    );
  if (id === 'unequal-fixed-sum')
    return protocol(
      id,
      'Unequal inputs with fixed sum',
      'Port shares change while the total prescribed input remains one.',
      [
        { time: 0, left: 0.25, right: 0.75 },
        { time: duration / 3, left: 0.75, right: 0.25 },
        { time: (2 * duration) / 3, left: 0.1, right: 0.9 },
      ],
      duration,
    );
  if (id === 'periodic') {
    const period = duration / 4;
    return protocol(
      id,
      'Periodic piecewise input',
      'A saved alternating port schedule with constant total rate.',
      [
        { time: 0, left: 0.25, right: 0.75 },
        { time: period, left: 0.75, right: 0.25 },
        { time: 2 * period, left: 0.25, right: 0.75 },
        { time: 3 * period, left: 0.75, right: 0.25 },
      ],
      duration,
    );
  }
  if (id === 'finite-pulse') {
    const phase = options.pulsePhase ?? 0;
    const amplitude = options.pulseAmplitude ?? 1;
    const width = options.pulseWidth ?? 0.4;
    finite(phase, 'pulsePhase');
    finite(amplitude, 'pulseAmplitude');
    finite(width, 'pulseWidth');
    if (phase < 0 || phase >= TAU || amplitude < 0 || width <= 0)
      throw new RangeError(
        'Pulse phase, amplitude, and width are outside their domains.',
      );
    const start = phase / 2;
    const end = start + width;
    if (end >= duration)
      throw new RangeError(
        'Finite pulse must end inside the requested duration.',
      );
    const points =
      start === 0
        ? [
            { time: 0, left: amplitude, right: 0 },
            { time: end, left: 0, right: 0 },
          ]
        : [
            { time: 0, left: 0, right: 0 },
            { time: start, left: amplitude, right: 0 },
            { time: end, left: 0, right: 0 },
          ];
    return protocol(
      id,
      'Finite pulse',
      'A prescribed one-sided pulse with a saved phase and amplitude.',
      points,
      duration,
    );
  }
  if (id === 'equal-integral-early')
    return protocol(
      id,
      'Equal-integral sequence: early',
      'The same total input as the late sequence, concentrated early.',
      [
        { time: 0, left: 1, right: 0 },
        { time: duration / 2, left: 0, right: 0 },
      ],
      duration,
    );
  if (id === 'equal-integral-late')
    return protocol(
      id,
      'Equal-integral sequence: late',
      'The same total input as the early sequence, concentrated late.',
      [
        { time: 0, left: 0, right: 0 },
        { time: duration / 2, left: 1, right: 0 },
      ],
      duration,
    );
  throw new RangeError(`Unknown Setup A protocol ${id}.`);
}

export function setupAVariant(id: SetupAVariantId): SetupAVariant {
  const variant = setupAVariants.find((candidate) => candidate.id === id);
  if (!variant) throw new RangeError(`Unknown Setup A variant ${id}.`);
  return clone(variant);
}

function boundarySchedule(protocolValue: SetupAProtocol) {
  if (protocolValue.id === 'isolated') return {};
  return {
    left: protocolValue.points.map(({ time, left }) => ({ time, rate: left })),
    right: protocolValue.points.map(({ time, right }) => ({
      time,
      rate: right,
    })),
  } satisfies NonNullable<EnvelopeOptions['boundaryInputs']>;
}

export function createSetupAScenario(
  protocolValue: SetupAProtocol,
  variantId: SetupAVariantId,
): Scenario {
  const variant = setupAVariant(variantId);
  const scenario = clone(isolated) as Scenario;
  const node = scenario.nodes[0]!;
  node.response = variant.response;
  node.gain = variant.gain;
  scenario.id = `setup-a-${protocolValue.id}-${variant.id}`;
  scenario.boundaries =
    protocolValue.id === 'isolated'
      ? { left: { kind: 'open' }, right: { kind: 'open' } }
      : {
          left: { kind: 'driven', rate: 0 },
          right: { kind: 'driven', rate: 0 },
        };
  scenario.observation.sampleTimes = [0, protocolValue.duration];
  scenario.solver.step = Math.min(scenario.solver.step ?? 0.01, 0.02);
  return scenario;
}

function inputAt(points: SetupAInputPoint[], time: number): SetupAInputPoint {
  let active = points[0]!;
  for (const point of points) {
    if (point.time > time) break;
    active = point;
  }
  return active;
}

function integratedInput(points: SetupAInputPoint[], duration: number): number {
  return points.reduce((sum, point, index) => {
    const end = points[index + 1]?.time ?? duration;
    return sum + (point.left + point.right) * (end - point.time);
  }, 0);
}

function filterAt(
  points: SetupAInputPoint[],
  time: number,
  width: number,
): SetupAFilterSample {
  const value = { left: 0, right: 0 };
  let cursor = 0;
  for (const [index, point] of points.entries()) {
    if (point.time > time) break;
    const end = Math.min(points[index + 1]?.time ?? time, time);
    const dt = Math.max(0, end - cursor);
    value.left = point.left + (value.left - point.left) * Math.exp(-dt / width);
    value.right =
      point.right + (value.right - point.right) * Math.exp(-dt / width);
    cursor = end;
    if (cursor >= time) break;
  }
  return {
    left: value.left,
    right: value.right,
    sum: value.left + value.right,
  };
}

function runSolver(
  scenario: Scenario,
  envelope: EnvelopeOptions,
  duration: number,
): { samples: EnvelopeSample[]; ticks: TickCrossing[] } {
  const solver = new EnvelopeSolver(scenario, envelope);
  const samples = [solver.sample()];
  const ticks: TickCrossing[] = [];
  while (solver.time < duration) {
    ticks.push(...solver.advance(duration));
    if (solver.time > samples.at(-1)!.time) samples.push(solver.sample());
  }
  return { samples, ticks };
}

export function runSetupA(
  protocolValue: SetupAProtocol,
  variantId: SetupAVariantId,
): SetupARun {
  const scenario = createSetupAScenario(protocolValue, variantId);
  const envelope: EnvelopeOptions = {
    ...(protocolValue.id === 'isolated'
      ? {}
      : { boundaryInputs: boundarySchedule(protocolValue) }),
    tickSection: 0,
  };
  const result = runSolver(scenario, envelope, protocolValue.duration);
  const node = scenario.nodes[0]!;
  const samples = result.samples.map((sample) => {
    const state = sample.nodes[NODE_ID]!;
    const point = inputAt(protocolValue.points, sample.time);
    const target =
      node.omega0 +
      node.gain *
        (node.response === 'R2' ? Math.cos(2 * state.phi) : 1) *
        Math.tanh((point.left + point.right) / scenario.rateScale);
    return {
      time: sample.time,
      phi: state.phi,
      omega: state.omega,
      phaseDisplacement: state.phi - (node.phi + node.omega * sample.time),
      omegaTarget: target,
      boundMargin: state.boundMargin,
      inputLeft: point.left,
      inputRight: point.right,
      inputSum: point.left + point.right,
      filter: filterAt(protocolValue.points, sample.time, scenario.filterWidth),
    } satisfies SetupATrajectorySample;
  });
  const final = samples.at(-1)!;
  const lastChange = protocolValue.points.at(-1)!.time;
  const tolerance = Math.max(1e-6, scenario.solver.absoluteTolerance * 100);
  const afterChange = samples.filter((sample) => sample.time >= lastChange);
  const timeToTolerance =
    afterChange.find(
      (sample) => Math.abs(sample.omega - final.omegaTarget) <= tolerance,
    )?.time ?? null;
  const nextTick = result.ticks.find(
    (tick) => tick.time >= 0 && tick.time <= protocolValue.duration,
  );
  return {
    schemaVersion: 'setup-a-diagnostic-v1',
    modelVersion: 'paper-i-v1',
    protocol: clone(protocolValue),
    variant: setupAVariant(variantId),
    scenario,
    envelope,
    samples,
    ticks: clone(result.ticks),
    summary: {
      initialOmega: samples[0]!.omega,
      finalOmega: final.omega,
      minimumOmega: Math.min(...samples.map((sample) => sample.omega)),
      maximumOmega: Math.max(...samples.map((sample) => sample.omega)),
      minimumBoundMargin: Math.min(
        ...samples.map((sample) => sample.boundMargin),
      ),
      finalPhaseDisplacement: final.phaseDisplacement,
      inputIntegral: integratedInput(
        protocolValue.points,
        protocolValue.duration,
      ),
      filterPeak: Math.max(...samples.map((sample) => sample.filter.sum)),
      relaxation: {
        finalTarget: final.omegaTarget,
        finalError: Math.abs(final.omega - final.omegaTarget),
        timeToTolerance,
        tolerance,
      },
      nextTick: nextTick
        ? { time: nextTick.time, sectionIndex: nextTick.sectionIndex }
        : null,
      nextTickStatus: nextTick ? 'in-window' : 'missing-in-window',
    },
    limitations: [
      'The envelope uses prescribed rates; event arrivals and physical receiver filters belong to the packet engine.',
      'The exponential filter fields are diagnostic-only and do not alter the envelope feedback input.',
      'These finite smoke trajectories do not establish a scientific response curve or regime finding.',
    ],
  };
}

export interface SetupAResponseCurveOptions {
  phases?: number[];
  amplitudes?: number[];
  variant?: SetupAVariantId;
  duration?: number;
  pulseWidth?: number;
}

export function createSetupAResponseCurve(
  options: SetupAResponseCurveOptions = {},
): SetupAResponseCurve {
  const phases = options.phases ?? [0, Math.PI / 2, Math.PI, (3 * Math.PI) / 2];
  const amplitudes = options.amplitudes ?? [0.5, 1];
  const variant = options.variant ?? 'R1-positive';
  const points: SetupAResponsePoint[] = [];
  for (const phase of phases) {
    for (const amplitude of amplitudes) {
      const run = runSetupA(
        createSetupAProtocol('finite-pulse', {
          ...(options.duration === undefined
            ? {}
            : { duration: options.duration }),
          pulsePhase: phase,
          pulseAmplitude: amplitude,
          ...(options.pulseWidth === undefined
            ? {}
            : { pulseWidth: options.pulseWidth }),
        }),
        variant,
      );
      points.push({
        protocol: 'finite-pulse',
        variant,
        pulsePhase: phase,
        pulseAmplitude: amplitude,
        inputIntegral: run.summary.inputIntegral,
        finalPhaseDisplacement: run.summary.finalPhaseDisplacement,
        finalOmega: run.summary.finalOmega,
        finalOmegaTarget: run.summary.relaxation.finalTarget,
        minimumBoundMargin: run.summary.minimumBoundMargin,
        filterPeak: run.summary.filterPeak,
        nextTick: run.summary.nextTick?.time ?? null,
        nextTickStatus: run.summary.nextTickStatus,
      });
    }
  }
  return {
    schemaVersion: 'setup-a-response-curve-v1',
    protocol: 'finite-pulse',
    variant,
    points,
    controls: {
      sameIntegratedInput:
        points.length < 2 ||
        new Set(points.map((point) => point.inputIntegral)).size === 1,
      phaseDefinition:
        'pulsePhase is an initial-clock phase in [0, 2pi), converted to start time by phi/omega0.',
      scientificInterpretation: 'deferred',
    },
    limitations: [
      'Pulse phase and amplitude are saved as inputs; no fitted response law is claimed.',
      'The filter peak is an observer-facing diagnostic of the declared exponential kernel only.',
    ],
  };
}

function definitionFor(
  protocolId: SetupAProtocolId,
  variantId: SetupAVariantId,
): ExperimentDefinition {
  const protocolValue = createSetupAProtocol(protocolId);
  const scenario = createSetupAScenario(protocolValue, variantId);
  const envelope: EnvelopeOptions = {
    ...(protocolId === 'isolated'
      ? {}
      : { boundaryInputs: boundarySchedule(protocolValue) }),
  };
  return {
    schemaVersion: 'paper-i-experiment-v1',
    id: `setup-a-${protocolId}-${variantId.toLowerCase()}`,
    description: `${protocolValue.label}; ${setupAVariant(variantId).label}. Technical smoke protocol, not a paper result.`,
    scenario,
    mode: 'envelope',
    until: protocolValue.duration,
    ...(Object.keys(envelope).length ? { envelope } : {}),
    windows: {
      transient: 0,
      measurement: { start: 0, end: protocolValue.duration },
    },
    tolerances: {
      absolute: scenario.solver.absoluteTolerance,
      relative: scenario.solver.relativeTolerance,
    },
    replicates: 1,
    seed: `signal-space-setup-a-${protocolId}-${variantId}-v1`,
    observables: ['phase', 'frequency', 'rates', 'ticks'],
    budgets: { maxJobs: 1, maxSteps: 10000, checkpointEvery: 1 },
  };
}

export function createSetupADefinition(
  protocolId: SetupAProtocolId,
  variantId: SetupAVariantId = 'R1-positive',
): ExperimentDefinition {
  return definitionFor(protocolId, variantId);
}

export function createSetupASmokeDefinitions(): ExperimentDefinition[] {
  return setupAPresets.flatMap((preset) =>
    setupAVariants
      .slice(0, 3)
      .map((variant) => definitionFor(preset.protocol, variant.id)),
  );
}
