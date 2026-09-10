import type { Scenario } from '@signal-space/model';
import {
  EnvelopeSolver,
  type EnvelopeOptions,
  type EnvelopePerturbation,
  type EnvelopeSample,
} from '@signal-space/sim';
import {
  classifyPair,
  meanFrequency,
  pairPhase,
  retardedPhase,
  slipCount,
  type AnalysisSample,
  type PairClassification,
  type RetardedPhasePoint,
} from '@signal-space/analysis';
import pair from '../../../fixtures/scenarios/pair.json' with { type: 'json' };
import type { ExperimentDefinition } from './runs.js';

const TAU = 2 * Math.PI;
const NODE_A = 'A';
const NODE_B = 'B';
const DEFAULT_DURATION = 8;
const DEFAULT_PREPARATION_DURATION = 2;
const DEFAULT_GAIN = 0.2;
const DEFAULT_Q = 3;
const DEFAULT_PRESCRIBED_RATE = 0.75;

export type SetupBProtocolId =
  'reciprocal' | 'one-way-a-to-b' | 'prescribed-drive';
export type SetupBPreparationId =
  'co-phase' | 'pi-reflection' | 'small-offset' | 'seeded-random';
export type SetupBEmissionId = 'E0' | 'E1';
export type SetupBResponseId = 'R0' | 'R1' | 'R2';
export type SetupBVariantId = `${SetupBEmissionId}-${SetupBResponseId}`;

export interface SetupBPreparation {
  id: SetupBPreparationId;
  seed: string | null;
  phaseA: number;
  phaseB: number;
  linkHistory: 'established' | 'empty-links';
  description: string;
}

export type SetupBPerturbation = EnvelopePerturbation;

export interface SetupBProtocol {
  id: SetupBProtocolId;
  label: string;
  description: string;
  duration: number;
  preparationDuration: number;
  preparation: SetupBPreparation;
  perturbation: SetupBPerturbation | null;
  amplitude: number;
  prescribedRate: number | null;
  routes: Array<{
    id: string;
    source: string;
    target: string;
    sourcePort: 'left' | 'right';
    targetPort: 'left' | 'right';
  }>;
}

export interface SetupBVariant {
  id: SetupBVariantId;
  emission: SetupBEmissionId;
  response: SetupBResponseId;
  gain: number;
  label: string;
}

export interface SetupBPresetMetadata {
  id: string;
  label: string;
  protocol: SetupBProtocolId;
  preparation: SetupBPreparationId;
  units: { time: 's'; rate: 's^-1'; phase: 'rad'; frequency: 'rad s^-1' };
  assumptions: string[];
}

export interface SetupBDiagnostics {
  meanFrequency: Record<string, number>;
  meanFrequencyDifference: number;
  phase: {
    initialUnwrapped: number;
    finalUnwrapped: number;
    unwrappedDrift: number;
    minimum: number;
    maximum: number;
    slipCount: number;
    appliedPairPhaseOffset: number;
  };
  retardedPhase: {
    aFromB: RetardedPhasePoint[];
    bFromA: RetardedPhasePoint[];
  };
  recovery: PairClassification['perturbationRecovery'];
  collectiveModulation: {
    meanFrequencyMinimum: number;
    meanFrequencyMaximum: number;
    differenceMinimum: number;
    differenceMaximum: number;
  };
  classification: PairClassification;
}

export interface SetupBRun {
  schemaVersion: 'setup-b-diagnostic-v1';
  modelVersion: 'paper-i-v1';
  protocol: SetupBProtocol;
  variant: SetupBVariant;
  scenario: Scenario;
  envelope: EnvelopeOptions;
  samples: EnvelopeSample[];
  /** Matched no-perturbation continuation for attraction evidence. */
  referenceSamples: EnvelopeSample[];
  diagnostics: SetupBDiagnostics;
  limitations: string[];
}

export interface SetupBProtocolOptions {
  duration?: number;
  preparationDuration?: number;
  preparation?: SetupBPreparationId;
  preparationSeed?: string;
  linkHistory?: 'established' | 'empty-links';
  perturbation?: SetupBPerturbation | null;
  amplitude?: number;
  prescribedRate?: number;
}

export interface SetupBRunOptions {
  gain?: number;
}

export interface SetupBGainSweep {
  schemaVersion: 'setup-b-gain-sweep-v1';
  variant: SetupBVariantId;
  protocol: SetupBProtocolId;
  points: Array<{
    gain: number;
    meanFrequencyDifference: number;
    phaseDrift: number;
    classificationStatus: PairClassification['status'];
  }>;
  controls: {
    includesZeroGain: boolean;
    signedGain: boolean;
    interpretation: 'deferred';
  };
  limitations: string[];
}

export const setupBVariants: readonly SetupBVariant[] = [
  { id: 'E0-R0', emission: 'E0', response: 'R0', gain: 0, label: 'E0 + R0' },
  {
    id: 'E0-R1',
    emission: 'E0',
    response: 'R1',
    gain: DEFAULT_GAIN,
    label: 'E0 + R1',
  },
  {
    id: 'E0-R2',
    emission: 'E0',
    response: 'R2',
    gain: DEFAULT_GAIN,
    label: 'E0 + R2',
  },
  { id: 'E1-R0', emission: 'E1', response: 'R0', gain: 0, label: 'E1 + R0' },
  {
    id: 'E1-R1',
    emission: 'E1',
    response: 'R1',
    gain: DEFAULT_GAIN,
    label: 'E1 + R1',
  },
  {
    id: 'E1-R2',
    emission: 'E1',
    response: 'R2',
    gain: DEFAULT_GAIN,
    label: 'E1 + R2',
  },
];

function clone<T>(value: T): T {
  return structuredClone(value);
}

function finite(value: number, name: string): void {
  if (!Number.isFinite(value)) throw new RangeError(`${name} must be finite.`);
}

function phaseFromSeed(seed: string): number {
  let hash = 2166136261;
  for (const character of seed) {
    hash ^= character.codePointAt(0)!;
    hash = Math.imul(hash, 16777619);
  }
  return ((hash >>> 0) / 2 ** 32) * TAU;
}

function preparation(
  id: SetupBPreparationId,
  seed: string,
  linkHistory: 'established' | 'empty-links',
): SetupBPreparation {
  const phaseB =
    id === 'co-phase'
      ? 0
      : id === 'pi-reflection'
        ? Math.PI
        : id === 'small-offset'
          ? 0.05
          : phaseFromSeed(seed);
  return {
    id,
    seed: id === 'seeded-random' ? seed : null,
    phaseA: 0,
    phaseB,
    linkHistory,
    description:
      id === 'co-phase'
        ? 'Both initial phases are equal; persistence is not attraction evidence.'
        : id === 'pi-reflection'
          ? 'The B phase is offset by pi, the declared reflection-related convention.'
          : id === 'small-offset'
            ? 'A small nonzero phase offset tests nearby continuation behavior.'
            : 'A deterministic seed selects B phase; the seed is saved with the preparation.',
  };
}

function validatePreparation(value: SetupBPreparation): void {
  finite(value.phaseA, 'preparation phaseA');
  finite(value.phaseB, 'preparation phaseB');
  if (value.id === 'seeded-random' && !value.seed)
    throw new RangeError('Seeded-random preparations require a nonempty seed.');
}

function validatePerturbation(
  value: SetupBPerturbation | null,
  duration: number,
  preparationDuration: number,
): void {
  if (!value) return;
  finite(value.time, 'perturbation time');
  finite(value.phaseOffset, 'perturbation phase offset');
  finite(value.frequencyOffset, 'perturbation frequency offset');
  if (value.time <= preparationDuration || value.time >= duration)
    throw new RangeError(
      'Setup B perturbations must occur after preparation and before the run ends.',
    );
  if (value.nodeId !== NODE_A && value.nodeId !== NODE_B)
    throw new RangeError('Setup B perturbations must target node A or B.');
}

export function createSetupBProtocol(
  id: SetupBProtocolId,
  options: SetupBProtocolOptions = {},
): SetupBProtocol {
  const duration = options.duration ?? DEFAULT_DURATION;
  const preparationDuration =
    options.preparationDuration ?? DEFAULT_PREPARATION_DURATION;
  const preparationId = options.preparation ?? 'co-phase';
  const linkHistory = options.linkHistory ?? 'established';
  const prep = preparation(
    preparationId,
    options.preparationSeed ?? `signal-space-setup-b-${preparationId}-v1`,
    linkHistory,
  );
  const perturbation =
    options.perturbation === undefined
      ? {
          time: preparationDuration + (duration - preparationDuration) / 3,
          nodeId: NODE_B,
          phaseOffset: 0.15,
          frequencyOffset: 0,
        }
      : options.perturbation;
  const amplitude = options.amplitude ?? 1;
  const prescribedRate =
    id === 'prescribed-drive'
      ? (options.prescribedRate ?? DEFAULT_PRESCRIBED_RATE)
      : null;
  if (!Number.isFinite(duration) || !Number.isFinite(preparationDuration))
    throw new RangeError('Setup B durations must be finite.');
  if (!(duration > 0) || !(preparationDuration >= 0))
    throw new RangeError('Setup B durations must be positive and ordered.');
  if (preparationDuration >= duration)
    throw new RangeError('Setup B preparation must end before the run ends.');
  finite(amplitude, 'Setup B amplitude');
  if (amplitude < 0 || amplitude > 1)
    throw new RangeError('Setup B amplitude must be in [0, 1].');
  if (
    prescribedRate !== null &&
    (!Number.isFinite(prescribedRate) || prescribedRate < 0)
  )
    throw new RangeError(
      'Prescribed drive rate must be finite and nonnegative.',
    );
  validatePreparation(prep);
  validatePerturbation(perturbation, duration, preparationDuration);
  const routes =
    id === 'reciprocal'
      ? [
          {
            id: 'A-B',
            source: NODE_A,
            target: NODE_B,
            sourcePort: 'right' as const,
            targetPort: 'left' as const,
          },
          {
            id: 'B-A',
            source: NODE_B,
            target: NODE_A,
            sourcePort: 'left' as const,
            targetPort: 'right' as const,
          },
        ]
      : id === 'one-way-a-to-b'
        ? [
            {
              id: 'A-B',
              source: NODE_A,
              target: NODE_B,
              sourcePort: 'right' as const,
              targetPort: 'left' as const,
            },
          ]
        : [];
  return {
    id,
    label:
      id === 'reciprocal'
        ? 'Reciprocal pair'
        : id === 'one-way-a-to-b'
          ? 'One-way A to B control'
          : 'Prescribed drive control',
    description:
      id === 'reciprocal'
        ? 'Identical A/B clocks exchange only the two declared delayed inner links.'
        : id === 'one-way-a-to-b'
          ? 'Only rho_A^+ reaches B; no reverse link is present.'
          : 'B receives a declared right-port drive without physical pair coupling.',
    duration,
    preparationDuration,
    preparation: prep,
    perturbation: clone(perturbation),
    amplitude,
    prescribedRate,
    routes,
  };
}

export function setupBVariant(id: SetupBVariantId): SetupBVariant {
  const variant = setupBVariants.find((candidate) => candidate.id === id);
  if (!variant) throw new RangeError(`Unknown Setup B variant ${id}.`);
  return clone(variant);
}

export const setupBPresets: readonly SetupBPresetMetadata[] = [
  ...(['co-phase', 'pi-reflection'] as const).flatMap((prep) =>
    (['reciprocal', 'one-way-a-to-b', 'prescribed-drive'] as const).map(
      (protocol): SetupBPresetMetadata => ({
        id: `setup-b-${protocol}-${prep}`,
        label: `${protocol} / ${prep}`,
        protocol,
        preparation: prep,
        units: { time: 's', rate: 's^-1', phase: 'rad', frequency: 'rad s^-1' },
        assumptions: [
          'A and B have the same omega0 and relaxation time.',
          'The declared route table is the complete physical link set.',
          'Perturbation recovery is evidence only; no locking outcome is required.',
        ],
      }),
    ),
  ),
] satisfies readonly SetupBPresetMetadata[];

function scenarioFor(
  protocolValue: SetupBProtocol,
  variant: SetupBVariant,
  gain: number,
): Scenario {
  finite(gain, 'Setup B gain');
  if (Math.abs(gain) >= 2)
    throw new RangeError(
      'Setup B gain must satisfy |gain| < omega0 (2 rad s^-1).',
    );
  if (variant.response === 'R0' && gain !== 0)
    throw new RangeError('R0 requires zero gain.');
  const scenario = clone(pair) as Scenario;
  scenario.id = `setup-b-${protocolValue.id}-${variant.id}-${protocolValue.preparation.id}`;
  const e0Nu = (DEFAULT_Q * scenario.nodes[0]!.omega0) / TAU;
  for (const node of scenario.nodes) {
    node.amplitude = protocolValue.amplitude;
    node.response = variant.response;
    node.gain = gain;
    node.emission =
      variant.emission === 'E0'
        ? { law: 'E0', nu: e0Nu }
        : { law: 'E1', q: DEFAULT_Q };
  }
  const phases = {
    [NODE_A]: protocolValue.preparation.phaseA,
    [NODE_B]: protocolValue.preparation.phaseB,
  };
  for (const node of scenario.nodes) {
    node.phi = phases[node.id as keyof typeof phases];
    node.omega = node.omega0;
    scenario.initialHistory.nodes[node.id] = {
      phiAtZero: node.phi,
      omega: node.omega,
    };
  }
  scenario.links = protocolValue.routes.map((route) => ({
    ...route,
    delay: 1,
  }));
  scenario.boundaries =
    protocolValue.id === 'prescribed-drive'
      ? { left: { kind: 'open' }, right: { kind: 'driven', rate: 0 } }
      : { left: { kind: 'open' }, right: { kind: 'open' } };
  scenario.observation.sampleTimes = [0, protocolValue.duration];
  scenario.solver.step = Math.min(scenario.solver.step ?? 0.01, 0.02);
  return scenario;
}

function prehistoryFor(
  scenario: Scenario,
): NonNullable<EnvelopeOptions['prehistory']> {
  const startTime = scenario.initialHistory.startTime;
  return [
    {
      time: startTime,
      nodes: Object.fromEntries(
        scenario.nodes.map((node) => [
          node.id,
          { phi: node.phi + node.omega * startTime, omega: node.omega },
        ]),
      ),
    },
    {
      time: 0,
      nodes: Object.fromEntries(
        scenario.nodes.map((node) => [
          node.id,
          { phi: node.phi, omega: node.omega },
        ]),
      ),
    },
  ];
}

function envelopeFor(
  protocolValue: SetupBProtocol,
  scenario: Scenario,
  includePerturbation: boolean,
): EnvelopeOptions {
  const envelope: EnvelopeOptions = {
    preparation: protocolValue.preparation.linkHistory,
    prehistory: prehistoryFor(scenario),
  };
  if (protocolValue.prescribedRate !== null)
    envelope.boundaryInputs = {
      right: [{ time: 0, rate: protocolValue.prescribedRate }],
    };
  if (includePerturbation && protocolValue.perturbation)
    envelope.perturbations = [clone(protocolValue.perturbation)];
  return envelope;
}

function runEnvelope(
  scenario: Scenario,
  envelope: EnvelopeOptions,
  duration: number,
  sampleTimes: number[] = [],
): EnvelopeSample[] {
  const solver = new EnvelopeSolver(scenario, envelope);
  const samples = [solver.sample()];
  const targets = [...new Set([0, ...sampleTimes, duration])].sort(
    (a, b) => a - b,
  );
  for (const target of targets) {
    if (target < 0 || target > duration)
      throw new RangeError('Setup B sample times must lie inside the run.');
    while (solver.time < target) {
      const previous = solver.time;
      solver.advance(target);
      if (solver.time > previous) samples.push(solver.sample());
    }
  }
  return samples;
}

function analysisSamples(samples: EnvelopeSample[]): AnalysisSample[] {
  return samples.map((sample) => ({
    time: sample.time,
    nodes: Object.fromEntries(
      Object.entries(sample.nodes).map(([id, node]) => [id, node]),
    ),
  }));
}

function retardedFor(
  samples: EnvelopeSample[],
  linkId: string,
  receiverId: string,
  chi: number,
): RetardedPhasePoint[] {
  const points = samples.flatMap((sample) => {
    const link = sample.retarded.find(
      (candidate) => candidate.linkId === linkId,
    );
    const receiver = sample.nodes[receiverId];
    return link && receiver
      ? [{ time: sample.time, phi: receiver.phi, link }]
      : [];
  });
  return retardedPhase(
    points.map((point) => ({ time: point.time, phi: point.phi })),
    points.map((point) => ({
      time: point.time,
      sourceTime: point.link.sourceTime,
      phi: point.link.phi,
    })),
    chi,
  );
}

function diagnosticsFor(
  protocolValue: SetupBProtocol,
  samples: EnvelopeSample[],
  referenceSamples: EnvelopeSample[],
): SetupBDiagnostics {
  const series = analysisSamples(samples);
  const perturbation = protocolValue.perturbation;
  const measurementStart = Math.max(
    perturbation?.time ?? 0,
    protocolValue.duration / 2,
  );
  const measurementSeries = series.filter(
    (sample) => sample.time >= measurementStart,
  );
  const phases = pairPhase(measurementSeries, NODE_A, NODE_B).map(
    (point) => point.unwrapped,
  );
  const frequencies = {
    [NODE_A]: meanFrequency(measurementSeries, NODE_A),
    [NODE_B]: meanFrequency(measurementSeries, NODE_B),
  };
  const differences = series.map(
    (sample) => sample.nodes[NODE_A]!.omega - sample.nodes[NODE_B]!.omega,
  );
  const means = series.map(
    (sample) => (sample.nodes[NODE_A]!.omega + sample.nodes[NODE_B]!.omega) / 2,
  );
  const referenceOffset =
    protocolValue.preparation.phaseA - protocolValue.preparation.phaseB;
  const criteria = {
    transientEnd: perturbation?.time ?? 0,
    windows: [
      {
        start: Math.max(perturbation?.time ?? 0, protocolValue.duration / 2),
        end: protocolValue.duration,
      },
    ],
    frequencyTolerance: 1e-3,
    phaseRangeTolerance: 0.2,
    minimumCycles: 1,
    ...(perturbation
      ? {
          perturbation: {
            time: perturbation.time,
            recoveryTolerance: 0.1,
            referenceOffset,
            reference: { samples: analysisSamples(referenceSamples) },
          },
        }
      : {}),
  };
  const classification = classifyPair(
    { samples: series },
    NODE_A,
    NODE_B,
    criteria,
  );
  return {
    meanFrequency: frequencies,
    meanFrequencyDifference: Math.abs(
      frequencies[NODE_A]! - frequencies[NODE_B]!,
    ),
    phase: {
      initialUnwrapped: phases[0]!,
      finalUnwrapped: phases.at(-1)!,
      unwrappedDrift: phases.at(-1)! - phases[0]!,
      minimum: Math.min(...phases),
      maximum: Math.max(...phases),
      slipCount: slipCount(phases),
      appliedPairPhaseOffset:
        perturbation && perturbation.nodeId === NODE_A
          ? perturbation.phaseOffset
          : perturbation?.phaseOffset
            ? -perturbation.phaseOffset
            : 0,
    },
    retardedPhase: {
      aFromB: retardedFor(samples, 'B-A', NODE_A, 0),
      bFromA: retardedFor(samples, 'A-B', NODE_B, 0),
    },
    recovery: classification.perturbationRecovery,
    collectiveModulation: {
      meanFrequencyMinimum: Math.min(...means),
      meanFrequencyMaximum: Math.max(...means),
      differenceMinimum: Math.min(...differences),
      differenceMaximum: Math.max(...differences),
    },
    classification,
  };
}

export function createSetupBScenario(
  protocolValue: SetupBProtocol,
  variantId: SetupBVariantId,
  options: SetupBRunOptions = {},
): Scenario {
  const variant = setupBVariant(variantId);
  return scenarioFor(protocolValue, variant, options.gain ?? variant.gain);
}

export function runSetupB(
  protocolValue: SetupBProtocol,
  variantId: SetupBVariantId,
  options: SetupBRunOptions = {},
): SetupBRun {
  const variant = setupBVariant(variantId);
  const scenario = createSetupBScenario(protocolValue, variantId, options);
  const actualGain = options.gain ?? variant.gain;
  const envelope = envelopeFor(protocolValue, scenario, true);
  const referenceEnvelope = envelopeFor(protocolValue, scenario, false);
  const sampleTimes = [
    protocolValue.perturbation?.time,
    Math.max(protocolValue.perturbation?.time ?? 0, protocolValue.duration / 2),
  ].filter((time): time is number => time !== undefined);
  const samples = runEnvelope(
    scenario,
    envelope,
    protocolValue.duration,
    sampleTimes,
  );
  const referenceSamples = runEnvelope(
    scenario,
    referenceEnvelope,
    protocolValue.duration,
    samples.map((sample) => sample.time),
  );
  const actualVariant: SetupBVariant = {
    ...variant,
    gain: actualGain,
    label:
      actualGain === variant.gain
        ? variant.label
        : `${variant.label} (gain ${actualGain})`,
  };
  return {
    schemaVersion: 'setup-b-diagnostic-v1',
    modelVersion: 'paper-i-v1',
    protocol: clone(protocolValue),
    variant: actualVariant,
    scenario,
    envelope,
    samples,
    referenceSamples,
    diagnostics: diagnosticsFor(protocolValue, samples, referenceSamples),
    limitations: [
      'Pair classifications are finite-window evidence and do not claim locking, attraction, or a paper result.',
      'The reference continuation is a matched deterministic run; it is not an observer-accessible signal.',
      'Retarded phases are simulator-only because no readable delayed source mark is declared.',
      'Event packet statistics, physical receiver filters, mirror/ring boundaries, and research-scale scans remain deferred.',
    ],
  };
}

export function createSetupBGainSweep(
  protocolValue: SetupBProtocol,
  variantId: SetupBVariantId,
  gains?: number[],
): SetupBGainSweep {
  const sweepGains =
    gains ??
    (variantId.endsWith('-R0') ? [0] : [-DEFAULT_GAIN, 0, DEFAULT_GAIN]);
  if (!sweepGains.length)
    throw new RangeError('Gain sweep needs at least one value.');
  const points = sweepGains.map((gain) => {
    finite(gain, 'gain sweep value');
    const run = runSetupB(protocolValue, variantId, { gain });
    return {
      gain,
      meanFrequencyDifference: run.diagnostics.meanFrequencyDifference,
      phaseDrift: run.diagnostics.phase.unwrappedDrift,
      classificationStatus: run.diagnostics.classification.status,
    };
  });
  return {
    schemaVersion: 'setup-b-gain-sweep-v1',
    variant: variantId,
    protocol: protocolValue.id,
    points,
    controls: {
      includesZeroGain: points.some((point) => point.gain === 0),
      signedGain:
        points.some((point) => point.gain < 0) &&
        points.some((point) => point.gain > 0),
      interpretation: 'deferred',
    },
    limitations: [
      'The sweep preserves signed input gains and records finite-window evidence only.',
      'No gain interval is labeled stable, attracting, synchronized, or scientifically resolved.',
    ],
  };
}

function definitionFor(
  protocolId: SetupBProtocolId,
  preparationId: SetupBPreparationId,
  variantId: SetupBVariantId,
): ExperimentDefinition {
  const protocolValue = createSetupBProtocol(protocolId, {
    preparation: preparationId,
  });
  const scenario = createSetupBScenario(protocolValue, variantId);
  const envelope = envelopeFor(protocolValue, scenario, true);
  return {
    schemaVersion: 'paper-i-experiment-v1',
    id: `setup-b-${protocolId}-${preparationId}-${variantId.toLowerCase()}`,
    description: `${protocolValue.label}; ${preparationId}; ${variantId}. Technical smoke protocol, not a paper result.`,
    scenario,
    mode: 'envelope',
    until: protocolValue.duration,
    envelope,
    windows: {
      transient: protocolValue.preparationDuration,
      measurement: {
        start: protocolValue.duration / 2,
        end: protocolValue.duration,
      },
    },
    tolerances: {
      absolute: scenario.solver.absoluteTolerance,
      relative: scenario.solver.relativeTolerance,
    },
    replicates: 1,
    seed: `signal-space-setup-b-${protocolId}-${preparationId}-${variantId}-v1`,
    observables: ['phase', 'frequency', 'retarded-phase'],
    budgets: { maxJobs: 1, maxSteps: 10000, checkpointEvery: 1 },
  };
}

export function createSetupBDefinition(
  protocolId: SetupBProtocolId,
  variantId: SetupBVariantId = 'E1-R1',
  preparationId: SetupBPreparationId = 'co-phase',
): ExperimentDefinition {
  return definitionFor(protocolId, preparationId, variantId);
}

export function createSetupBSmokeDefinitions(): ExperimentDefinition[] {
  return (['co-phase', 'pi-reflection'] as const).flatMap((preparationId) =>
    setupBVariants.map((variant) =>
      definitionFor('reciprocal', preparationId, variant.id),
    ),
  );
}
