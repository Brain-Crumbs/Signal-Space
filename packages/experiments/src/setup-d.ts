import type { ClockNode, Port, Scenario } from '@signal-space/model';
import {
  EnvelopeSolver,
  type EnvelopeOptions,
  type EnvelopeSample,
  type EnvelopeSnapshot,
} from '@signal-space/sim';
import {
  meanFrequency,
  responseFront,
  retardedPhase,
  type AnalysisSample,
  type RetardedPhasePoint,
} from '@signal-space/analysis';
import pair from '../../../fixtures/scenarios/pair.json' with { type: 'json' };
import {
  setupBVariant,
  type SetupBPreparationId,
  type SetupBVariantId,
} from './setup-b.js';
import type { ExperimentDefinition } from './runs.js';

const TAU = 2 * Math.PI;
const NODE_IDS = ['A', 'B', 'C'] as const;
const DEFAULT_DURATION = 4;
const DEFAULT_CADENCE = 0.05;
const DEFAULT_GAIN = 0.2;
const DEFAULT_BOOST = 0.1;
const DEFAULT_Q = 3;
const ONSET_TOLERANCE = 1e-6;

export type SetupDInterventionId = (typeof NODE_IDS)[number];
export type SetupDNormalizationId =
  'fixed-physical-r-star' | 'degree-normalized-r-star';
export type SetupDReplayProtocolId = 'recorded-endpoint-replay';

export const setupDPreparationIds: readonly SetupBPreparationId[] = [
  'co-phase',
  'pi-reflection',
  'small-offset',
  'seeded-random',
];

export interface SetupDPreparation {
  id: SetupBPreparationId;
  seed: string | null;
  phases: Record<SetupDInterventionId, number>;
  reflection: {
    enabled: boolean;
    nodeMap: Record<SetupDInterventionId, SetupDInterventionId>;
    portMap: Record<Port, Port>;
    lobePhaseShift: number;
  };
  linkHistory: 'established' | 'empty-links';
}

export interface SetupDNormalization {
  id: SetupDNormalizationId;
  label: string;
  physicalRStar: number;
  incomingDegrees: Record<SetupDInterventionId, number>;
  responseRateScales: Record<SetupDInterventionId, number>;
  isolatedNodeRule: string;
}

export interface SetupDRecordedSource {
  endpoint: 'A' | 'C';
  sourcePort: Port;
  receiverBoundary: Port;
  delay: number;
  respondsToReceiver: false;
  output: Array<{ time: number; rate: number }>;
  outputPreserved: true;
}

export interface SetupDReplayControl {
  id: SetupDReplayProtocolId;
  description: string;
  receiverScenario: Scenario;
  envelope: EnvelopeOptions;
  sources: SetupDRecordedSource[];
  samples: EnvelopeSample[];
  finalSnapshot: EnvelopeSnapshot;
}

export interface SetupDNodeMetrics {
  meanFrequency: number;
  meanRhoLeft: number;
  meanRhoRight: number;
  meanReceptionLeft: number;
  meanReceptionRight: number;
  responseLag: Array<{ time: number; targetMinusOmega: number }>;
}

export interface SetupDDiagnostics {
  perNode: Record<SetupDInterventionId, SetupDNodeMetrics>;
  retardedMismatch: Record<string, RetardedPhasePoint[]>;
  disturbancePropagation: ReturnType<typeof responseFront>;
}

export interface SetupDRun {
  schemaVersion: 'setup-d-diagnostic-v1';
  modelVersion: 'paper-i-v1';
  sourceSection: 'Paper I §11.5';
  intervention: {
    kind: 'intrinsic-frequency-increase';
    target: SetupDInterventionId;
    baselineOmega0: number;
    boostedOmega0: number;
    fraction: number;
    time: 0;
  };
  preparation: SetupDPreparation;
  normalization: SetupDNormalization;
  scenario: Scenario;
  envelope: EnvelopeOptions;
  samples: EnvelopeSample[];
  referenceSamples: EnvelopeSample[];
  finalSnapshot: EnvelopeSnapshot;
  replayControl: SetupDReplayControl;
  diagnostics: SetupDDiagnostics;
  limitations: string[];
}

export interface SetupDOptions {
  intervention?: SetupDInterventionId;
  variant?: SetupBVariantId;
  normalization?: SetupDNormalizationId;
  preparation?: SetupBPreparationId;
  preparationSeed?: string;
  linkHistory?: 'established' | 'empty-links';
  duration?: number;
  sampleCadence?: number;
  intrinsicFrequencyIncrease?: number;
  gain?: number;
}

export interface SetupDPreparationEnsemble {
  schemaVersion: 'setup-d-preparation-ensemble-v1';
  preparationIds: SetupBPreparationId[];
  runs: SetupDRun[];
  limitations: string[];
}

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

function reflectNode(id: SetupDInterventionId): SetupDInterventionId {
  return id === 'A' ? 'C' : id === 'C' ? 'A' : 'B';
}

function preparationFor(
  id: SetupBPreparationId,
  seed: string,
  reflected: boolean,
  linkHistory: 'established' | 'empty-links',
): SetupDPreparation {
  if (!setupDPreparationIds.includes(id))
    throw new RangeError(`Unknown Setup D preparation ${id}.`);
  const random = phaseFromSeed(seed);
  const base: Record<SetupDInterventionId, number> = {
    A: 0,
    B: id === 'pi-reflection' ? Math.PI : id === 'small-offset' ? 0.05 : random,
    C: id === 'pi-reflection' ? Math.PI : 0,
  };
  if (id === 'co-phase') base.B = 0;
  const phases = Object.fromEntries(
    NODE_IDS.map((node) => [
      node,
      reflected ? base[reflectNode(node)] + Math.PI : base[node],
    ]),
  ) as Record<SetupDInterventionId, number>;
  return {
    id,
    seed: id === 'seeded-random' ? seed : null,
    phases,
    reflection: {
      enabled: reflected,
      nodeMap: { A: 'C', B: 'B', C: 'A' },
      portMap: { left: 'right', right: 'left' },
      lobePhaseShift: reflected ? Math.PI : 0,
    },
    linkHistory,
  };
}

function node(scenario: Scenario, id: SetupDInterventionId): ClockNode {
  const result = scenario.nodes.find((candidate) => candidate.id === id);
  if (!result) throw new Error(`Setup D missing node ${id}.`);
  return result;
}

function emissionRate(
  nodeValue: ClockNode,
  phi: number,
  omega: number,
  port: Port,
) {
  const nu =
    nodeValue.emission.law === 'E0'
      ? nodeValue.emission.nu
      : (nodeValue.emission.q * omega) / TAU;
  const lobe = nodeValue.amplitude * Math.cos(phi);
  return (nu / 2) * (port === 'left' ? 1 - lobe : 1 + lobe);
}

function validateOptions(
  options: Required<
    Pick<
      SetupDOptions,
      'duration' | 'sampleCadence' | 'intrinsicFrequencyIncrease' | 'gain'
    >
  >,
): void {
  finite(options.duration, 'Setup D duration');
  finite(options.sampleCadence, 'Setup D sampleCadence');
  finite(
    options.intrinsicFrequencyIncrease,
    'Setup D intrinsicFrequencyIncrease',
  );
  finite(options.gain, 'Setup D gain');
  if (!(options.duration > 0))
    throw new RangeError('Setup D duration must be positive.');
  if (
    !(options.sampleCadence > 0) ||
    options.duration / options.sampleCadence > 10000
  )
    throw new RangeError(
      'Setup D sampleCadence must be positive with at most 10,000 samples.',
    );
  if (!(options.intrinsicFrequencyIncrease > 0))
    throw new RangeError(
      'Setup D intrinsicFrequencyIncrease must be positive.',
    );
  if (Math.abs(options.gain) >= 2)
    throw new RangeError(
      'Setup D gain must satisfy |gain| < the baseline omega0.',
    );
}

function scenarioFor(
  intervention: SetupDInterventionId,
  variantId: SetupBVariantId,
  prep: SetupDPreparation,
  boost: number,
  gain: number,
): Scenario {
  const variant = setupBVariant(variantId);
  if (variant.response === 'R0' && gain !== 0)
    throw new RangeError('Setup D R0 requires zero gain.');
  const scenario = clone(pair) as Scenario;
  scenario.id = `setup-d-${intervention}-${variantId}-${prep.id}-${prep.reflection.enabled ? 'reflected' : 'direct'}`;
  scenario.nodes = NODE_IDS.map((id, index) => ({
    ...clone(pair.nodes[0]!),
    id,
    position: index,
    phi: prep.phases[id],
    omega0: id === intervention ? 2 * (1 + boost) : 2,
    omega: id === intervention ? 2 * (1 + boost) : 2,
    gain,
    response: variant.response,
    emission:
      variant.emission === 'E0'
        ? {
            law: 'E0' as const,
            nu: (DEFAULT_Q * (id === intervention ? 2 * (1 + boost) : 2)) / TAU,
          }
        : { law: 'E1' as const, q: DEFAULT_Q },
  }));
  scenario.links = [
    {
      id: 'A-B',
      source: 'A',
      target: 'B',
      sourcePort: 'right',
      targetPort: 'left',
      delay: 1,
    },
    {
      id: 'B-A',
      source: 'B',
      target: 'A',
      sourcePort: 'left',
      targetPort: 'right',
      delay: 1,
    },
    {
      id: 'B-C',
      source: 'B',
      target: 'C',
      sourcePort: 'right',
      targetPort: 'left',
      delay: 1,
    },
    {
      id: 'C-B',
      source: 'C',
      target: 'B',
      sourcePort: 'left',
      targetPort: 'right',
      delay: 1,
    },
  ];
  scenario.boundaries = { left: { kind: 'open' }, right: { kind: 'open' } };
  scenario.initialHistory.startTime = -1;
  scenario.initialHistory.nodes = Object.fromEntries(
    scenario.nodes.map((entry) => [
      entry.id,
      { phiAtZero: entry.phi, omega: entry.omega },
    ]),
  );
  scenario.initialHistory.filters = Object.fromEntries(
    scenario.nodes.map((entry) => [entry.id, { left: 0, right: 0 }]),
  );
  scenario.observation.sampleTimes = [0];
  return scenario;
}

function degreeNormalization(
  scenario: Scenario,
  id: SetupDNormalizationId,
): SetupDNormalization {
  const incomingDegrees = Object.fromEntries(
    NODE_IDS.map((nodeId) => [
      nodeId,
      scenario.links.filter((link) => link.target === nodeId).length,
    ]),
  ) as Record<SetupDInterventionId, number>;
  const responseRateScales = Object.fromEntries(
    NODE_IDS.map((nodeId) => {
      const degree = incomingDegrees[nodeId];
      // With no incoming link the summed input is identically zero. Retain the
      // physical scale rather than construct a zero denominator.
      return [
        nodeId,
        id === 'degree-normalized-r-star' && degree > 0
          ? degree * scenario.rateScale
          : scenario.rateScale,
      ];
    }),
  ) as Record<SetupDInterventionId, number>;
  return {
    id,
    label:
      id === 'fixed-physical-r-star'
        ? 'Fixed physical r*'
        : 'Degree-normalized r* -> d_i r*',
    physicalRStar: scenario.rateScale,
    incomingDegrees,
    responseRateScales,
    isolatedNodeRule:
      'An isolated node has zero summed reception; its stored response scale remains physical r* and no division by degree is performed.',
  };
}

function prehistoryFor(
  scenario: Scenario,
): NonNullable<EnvelopeOptions['prehistory']> {
  return [
    {
      time: scenario.initialHistory.startTime,
      nodes: Object.fromEntries(
        scenario.nodes.map((entry) => [
          entry.id,
          {
            phi: entry.phi + entry.omega * scenario.initialHistory.startTime,
            omega: entry.omega,
          },
        ]),
      ),
    },
    {
      time: 0,
      nodes: Object.fromEntries(
        scenario.nodes.map((entry) => [
          entry.id,
          { phi: entry.phi, omega: entry.omega },
        ]),
      ),
    },
  ];
}

function envelopeFor(
  scenario: Scenario,
  prep: SetupDPreparation,
  normalization: SetupDNormalization,
): EnvelopeOptions {
  return {
    preparation: prep.linkHistory,
    prehistory: prehistoryFor(scenario),
    responseRateScales: clone(normalization.responseRateScales),
  };
}

function sampleTargets(duration: number, cadence: number): number[] {
  const values = [0, duration];
  for (let index = 1; index * cadence < duration; index++)
    values.push(index * cadence);
  return [...new Set(values)].sort((a, b) => a - b);
}

function runEnvelope(
  scenario: Scenario,
  envelope: EnvelopeOptions,
  duration: number,
  cadence: number,
) {
  const solver = new EnvelopeSolver(scenario, envelope);
  const samples: EnvelopeSample[] = [solver.sample()];
  for (const target of sampleTargets(duration, cadence)) {
    while (solver.time < target) {
      const previous = solver.time;
      solver.advance(target);
      if (solver.time > previous) samples.push(solver.sample());
      // Adaptive integration can land within a few representable values of a
      // decimal diagnostic target. Do not retry an unresolvable remainder.
      if (target - solver.time <= 16 * Number.EPSILON * Math.max(1, target))
        break;
    }
  }
  return { samples, finalSnapshot: solver.snapshot() };
}

function analysisSamples(samples: EnvelopeSample[]): AnalysisSample[] {
  return samples.map((sample) => ({ time: sample.time, nodes: sample.nodes }));
}

function average(values: number[]): number {
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function retardedMismatches(
  samples: EnvelopeSample[],
): Record<string, RetardedPhasePoint[]> {
  const result: Record<string, RetardedPhasePoint[]> = {};
  for (const linkId of ['A-B', 'B-A', 'B-C', 'C-B']) {
    const points = samples.flatMap((sample) => {
      const link = sample.retarded.find(
        (candidate) => candidate.linkId === linkId,
      );
      const receiverId = linkId.split('-')[1]!;
      const receiver = sample.nodes[receiverId];
      return link && receiver ? [{ time: sample.time, receiver, link }] : [];
    });
    result[linkId] = retardedPhase(
      points.map((point) => ({ time: point.time, phi: point.receiver.phi })),
      points.map((point) => ({
        time: point.time,
        sourceTime: point.link.sourceTime,
        phi: point.link.phi,
      })),
      0,
    );
  }
  return result;
}

function diagnosticsFor(
  scenario: Scenario,
  normalization: SetupDNormalization,
  samples: EnvelopeSample[],
  referenceSamples: EnvelopeSample[],
  intervention: SetupDInterventionId,
): SetupDDiagnostics {
  const series = analysisSamples(samples);
  const reference = new Map(
    referenceSamples.map((sample) => [sample.time, sample]),
  );
  const perNode = Object.fromEntries(
    NODE_IDS.map((id) => {
      const source = node(scenario, id);
      const metrics = samples.map((sample) => sample.nodes[id]!);
      return [
        id,
        {
          meanFrequency: meanFrequency(series, id),
          meanRhoLeft: average(metrics.map((entry) => entry.rhoLeft)),
          meanRhoRight: average(metrics.map((entry) => entry.rhoRight)),
          meanReceptionLeft: average(
            metrics.map((entry) => entry.receptionLeft),
          ),
          meanReceptionRight: average(
            metrics.map((entry) => entry.receptionRight),
          ),
          responseLag: samples.map((sample) => {
            const current = sample.nodes[id]!;
            const target =
              source.omega0 +
              source.gain *
                (source.response === 'R2' ? Math.cos(2 * current.phi) : 1) *
                Math.tanh(
                  (current.receptionLeft + current.receptionRight) /
                    normalization.responseRateScales[id],
                );
            return {
              time: sample.time,
              targetMinusOmega: target - current.omega,
            };
          }),
        } satisfies SetupDNodeMetrics,
      ];
    }),
  ) as Record<SetupDInterventionId, SetupDNodeMetrics>;
  const sourceNode = node(scenario, intervention);
  const onsets = scenario.nodes.map((entry) => {
    const onsetTime = samples.find((sample) => {
      const baseline = reference.get(sample.time)?.nodes[entry.id];
      return (
        baseline !== undefined &&
        Math.abs(sample.nodes[entry.id]!.omega - baseline.omega) >
          ONSET_TOLERANCE
      );
    })?.time;
    return {
      nodeId: entry.id,
      position: entry.position,
      ...(onsetTime === undefined ? {} : { onsetTime }),
    };
  });
  return {
    perNode,
    retardedMismatch: retardedMismatches(samples),
    disturbancePropagation: responseFront(
      onsets,
      { position: sourceNode.position, time: 0 },
      scenario.c0,
      ONSET_TOLERANCE,
    ),
  };
}

function sourceSchedule(
  scenario: Scenario,
  samples: EnvelopeSample[],
  endpoint: 'A' | 'C',
  port: Port,
  duration: number,
  cadence: number,
): Array<{ time: number; rate: number }> {
  const source = node(scenario, endpoint);
  return sampleTargets(duration, cadence).map((arrivalTime) => {
    const sourceTime = arrivalTime - 1;
    if (sourceTime < 0)
      return {
        time: arrivalTime,
        rate: emissionRate(
          source,
          source.phi + source.omega * sourceTime,
          source.omega,
          port,
        ),
      };
    const recorded = samples.reduce((closest, candidate) =>
      Math.abs(candidate.time - sourceTime) <
      Math.abs(closest.time - sourceTime)
        ? candidate
        : closest,
    );
    if (Math.abs(recorded.time - sourceTime) > 1e-10)
      throw new Error(
        'Setup D replay schedule lacks a recorded endpoint output.',
      );
    return {
      time: arrivalTime,
      rate:
        port === 'left'
          ? recorded.nodes[endpoint]!.rhoLeft
          : recorded.nodes[endpoint]!.rhoRight,
    };
  });
}

function replayControlFor(
  sourceScenario: Scenario,
  sourceEnvelope: EnvelopeOptions,
  sourceSamples: EnvelopeSample[],
  duration: number,
  cadence: number,
): SetupDReplayControl {
  const receiverScenario = clone(sourceScenario);
  const receiver = node(receiverScenario, 'B');
  receiverScenario.id = `${sourceScenario.id}-recorded-endpoint-replay`;
  receiverScenario.nodes = [receiver];
  receiverScenario.links = [];
  receiverScenario.boundaries = {
    left: { kind: 'driven', rate: 0 },
    right: { kind: 'driven', rate: 0 },
  };
  receiverScenario.initialHistory.nodes = {
    B: clone(receiverScenario.initialHistory.nodes.B!),
  };
  receiverScenario.initialHistory.filters = { B: { left: 0, right: 0 } };
  const left = sourceSchedule(
    sourceScenario,
    sourceSamples,
    'A',
    'right',
    duration,
    cadence,
  );
  const right = sourceSchedule(
    sourceScenario,
    sourceSamples,
    'C',
    'left',
    duration,
    cadence,
  );
  const envelope: EnvelopeOptions = {
    preparation: sourceEnvelope.preparation ?? 'established',
    prehistory: prehistoryFor(receiverScenario),
    responseRateScales: {
      B: sourceEnvelope.responseRateScales?.B ?? receiverScenario.rateScale,
    },
    boundaryInputs: { left, right },
  };
  const replay = runEnvelope(receiverScenario, envelope, duration, cadence);
  return {
    id: 'recorded-endpoint-replay',
    description:
      'B receives delayed schedules copied from the reciprocal run’s A-right and C-left endpoint outputs; the records have no receiver-to-source route.',
    receiverScenario,
    envelope,
    sources: [
      {
        endpoint: 'A',
        sourcePort: 'right',
        receiverBoundary: 'left',
        delay: 1,
        respondsToReceiver: false,
        output: left,
        outputPreserved: true,
      },
      {
        endpoint: 'C',
        sourcePort: 'left',
        receiverBoundary: 'right',
        delay: 1,
        respondsToReceiver: false,
        output: right,
        outputPreserved: true,
      },
    ],
    samples: replay.samples,
    finalSnapshot: replay.finalSnapshot,
  };
}

/** Three-clock A-B-C diagnostic preset. It records comparisons; it asserts no dynamics. */
export function runSetupD(options: SetupDOptions = {}): SetupDRun {
  const resolved = {
    duration: options.duration ?? DEFAULT_DURATION,
    sampleCadence: options.sampleCadence ?? DEFAULT_CADENCE,
    intrinsicFrequencyIncrease:
      options.intrinsicFrequencyIncrease ?? DEFAULT_BOOST,
    gain: options.gain ?? DEFAULT_GAIN,
  };
  validateOptions(resolved);
  const intervention = options.intervention ?? 'A';
  const variantId = options.variant ?? 'E1-R1';
  const normalizationId = options.normalization ?? 'fixed-physical-r-star';
  const prep = preparationFor(
    options.preparation ?? 'co-phase',
    options.preparationSeed ?? 'signal-space-setup-d-v1',
    intervention === 'C',
    options.linkHistory ?? 'established',
  );
  const scenario = scenarioFor(
    intervention,
    variantId,
    prep,
    resolved.intrinsicFrequencyIncrease,
    resolved.gain,
  );
  const normalization = degreeNormalization(scenario, normalizationId);
  const envelope = envelopeFor(scenario, prep, normalization);
  const primary = runEnvelope(
    scenario,
    envelope,
    resolved.duration,
    resolved.sampleCadence,
  );
  const referenceScenario = scenarioFor(
    intervention,
    variantId,
    prep,
    0,
    resolved.gain,
  );
  const referenceNormalization = degreeNormalization(
    referenceScenario,
    normalizationId,
  );
  const reference = runEnvelope(
    referenceScenario,
    envelopeFor(referenceScenario, prep, referenceNormalization),
    resolved.duration,
    resolved.sampleCadence,
  );
  const replayControl = replayControlFor(
    scenario,
    envelope,
    primary.samples,
    resolved.duration,
    resolved.sampleCadence,
  );
  return {
    schemaVersion: 'setup-d-diagnostic-v1',
    modelVersion: 'paper-i-v1',
    sourceSection: 'Paper I §11.5',
    intervention: {
      kind: 'intrinsic-frequency-increase',
      target: intervention,
      baselineOmega0: 2,
      boostedOmega0: 2 * (1 + resolved.intrinsicFrequencyIncrease),
      fraction: resolved.intrinsicFrequencyIncrease,
      time: 0,
    },
    preparation: prep,
    normalization,
    scenario,
    envelope,
    samples: primary.samples,
    referenceSamples: reference.samples,
    finalSnapshot: primary.finalSnapshot,
    replayControl,
    diagnostics: diagnosticsFor(
      scenario,
      normalization,
      primary.samples,
      reference.samples,
      intervention,
    ),
    limitations: [
      'The intrinsic-frequency change is a declared t=0 comparison intervention, not a derived force or binding law.',
      'Recorded endpoint replay is a deterministic envelope-rate control; it is not a physical packet record or an observer-readable source label.',
      'Degree normalization is an explicitly named response-scale variant. The fixed physical r* convention remains the default.',
      'Finite diagnostics record propagation and mismatch without claiming synchronization, attraction, gravity, electromagnetism, or a paper result.',
    ],
  };
}

export function createSetupDDefinition(
  options: SetupDOptions = {},
): ExperimentDefinition {
  const run = runSetupD(options);
  return {
    schemaVersion: 'paper-i-experiment-v1',
    id: `setup-d-${run.intervention.target}-${run.normalization.id}`,
    description:
      'Setup D A-B-C three-clock diagnostic; technical wiring check, not a paper result.',
    scenario: run.scenario,
    mode: 'envelope',
    until: options.duration ?? DEFAULT_DURATION,
    envelope: run.envelope,
    controls: [
      {
        id: run.normalization.id,
        kind: 'analytic',
        description: run.normalization.label,
      },
      {
        id: run.replayControl.id,
        kind: 'causal',
        description: run.replayControl.description,
      },
    ],
    windows: {
      transient: 0,
      measurement: { start: 0, end: options.duration ?? DEFAULT_DURATION },
    },
    tolerances: {
      absolute: run.scenario.solver.absoluteTolerance,
      relative: run.scenario.solver.relativeTolerance,
    },
    replicates: 1,
    seed: options.preparationSeed ?? 'signal-space-setup-d-v1',
    observables: ['phase', 'frequency', 'rates', 'retarded-phase'],
    budgets: { maxJobs: 1, maxSteps: 10000, checkpointEvery: 1 },
  };
}

/** Independent declared initial-phase preparations; no shared state is handed off. */
export function runSetupDPreparationEnsemble(
  options: Omit<SetupDOptions, 'preparation' | 'preparationSeed'> & {
    preparations?: SetupBPreparationId[];
    preparationSeed?: string;
  } = {},
): SetupDPreparationEnsemble {
  const preparationIds = options.preparations ?? [...setupDPreparationIds];
  if (!preparationIds.length)
    throw new RangeError(
      'Setup D preparation ensemble needs at least one preparation.',
    );
  if (new Set(preparationIds).size !== preparationIds.length)
    throw new RangeError(
      'Setup D preparation ensemble preparations must be unique.',
    );
  preparationIds.forEach((id) => {
    if (!setupDPreparationIds.includes(id))
      throw new RangeError(`Unknown Setup D preparation ${id}.`);
  });
  const inherited: SetupDOptions = {
    ...(options.intervention === undefined
      ? {}
      : { intervention: options.intervention }),
    ...(options.variant === undefined ? {} : { variant: options.variant }),
    ...(options.normalization === undefined
      ? {}
      : { normalization: options.normalization }),
    ...(options.linkHistory === undefined
      ? {}
      : { linkHistory: options.linkHistory }),
    ...(options.duration === undefined ? {} : { duration: options.duration }),
    ...(options.sampleCadence === undefined
      ? {}
      : { sampleCadence: options.sampleCadence }),
    ...(options.intrinsicFrequencyIncrease === undefined
      ? {}
      : { intrinsicFrequencyIncrease: options.intrinsicFrequencyIncrease }),
    ...(options.gain === undefined ? {} : { gain: options.gain }),
  };
  return {
    schemaVersion: 'setup-d-preparation-ensemble-v1',
    preparationIds: [...preparationIds],
    runs: preparationIds.map((preparation) =>
      runSetupD({
        ...inherited,
        preparation,
        preparationSeed: `${options.preparationSeed ?? 'signal-space-setup-d-v1'}:${preparation}`,
      }),
    ),
    limitations: [
      'Preparations are independent initial-state comparisons; no trajectory is continued from another preparation.',
      'The ensemble records diagnostics only and does not infer an attracting state or a paper result.',
    ],
  };
}

export function createSetupDSmokeDefinitions(): ExperimentDefinition[] {
  return [
    createSetupDDefinition({
      intervention: 'A',
      variant: 'E1-R0',
      gain: 0,
      normalization: 'fixed-physical-r-star',
    }),
    createSetupDDefinition({
      intervention: 'C',
      variant: 'E1-R1',
      normalization: 'degree-normalized-r-star',
      preparation: 'pi-reflection',
    }),
  ];
}
