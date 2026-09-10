import type { Scenario } from '@signal-space/model';
import {
  EnvelopeFailure,
  EnvelopeSolver,
  type EnvelopeOptions,
  type EnvelopeSample,
  type EnvelopeSnapshot,
} from '@signal-space/sim';
import {
  classifyPair,
  pairPhase,
  type AnalysisSample,
  type PairClassification,
} from '@signal-space/analysis';
import pair from '../../../fixtures/scenarios/pair.json' with { type: 'json' };
import {
  setupBVariants,
  type SetupBEmissionId,
  type SetupBPreparationId,
  type SetupBResponseId,
} from './setup-b.js';
import type { ExperimentDefinition } from './runs.js';

const TAU = 2 * Math.PI;
const OMEGA_REFERENCE = 2;
const DEFAULT_Q = 3;
const DEFAULT_DURATION = 4;
const DEFAULT_PREPARATION_DURATION = 1;
const DEFAULT_MINIMUM_CYCLES = 1;
const DEFAULT_SMALL_DELAY = 0.05;
const DEFAULT_FREQUENCY_TOLERANCE = 1e-3;
const DEFAULT_PHASE_RANGE_TOLERANCE = 0.2;
const DEFAULT_SAMPLE_CADENCE = 0.1;
const MAX_REPLICATES = 100;
const MAX_SCAN_RUNS = 10_000;
const MAX_DIAGNOSTIC_SAMPLES = 10_000;
const NODE_A = 'A';
const NODE_B = 'B';

export type SetupCParameterId =
  'detuning' | 'delay' | 'gain' | 'contrast' | 'relaxationTime';

/** Dimensionless scan coordinates. The physical conversion is saved per cell. */
export interface SetupCParameters {
  /** (omega0_B - omega0_A) / omegaReference; must be greater than -1. */
  detuning: number;
  /** omegaReference * tau; strictly positive. */
  delay: number;
  /** gain / omegaReference; signed and subject to the node bound. */
  gain: number;
  /** Directional contrast a; in [0, 1]. */
  contrast: number;
  /** omegaReference * relaxationTime; strictly positive. */
  relaxationTime: number;
}

export interface SetupCPhysicalParameters {
  omegaReference: number;
  omega0: Record<string, number>;
  delay: number;
  gain: Record<string, number>;
  relaxationTime: Record<string, number>;
  contrast: Record<string, number>;
}

export type SetupCControlId =
  'baseline' | 'no-feedback' | 'zero-contrast' | 'small-positive-delay';
export type SetupCContinuationDirection = 'forward' | 'reverse' | 'independent';

export interface SetupCControl {
  id: SetupCControlId;
  label: string;
  description: string;
  fixedParameter?: SetupCParameterId;
  fixedValue?: number;
}

export interface SetupCPreparation {
  id: SetupBPreparationId;
  seed: string | null;
  phaseA: number;
  phaseB: number;
  linkHistory: 'established' | 'empty-links';
}

export interface SetupCScanOptions {
  axes?: Partial<Record<SetupCParameterId, number[]>>;
  variant?: SetupCVariantId;
  preparation?: SetupBPreparationId;
  preparations?: SetupBPreparationId[];
  preparationSeed?: string;
  linkHistory?: 'established' | 'empty-links';
  duration?: number;
  preparationDuration?: number;
  minimumCycles?: number;
  control?: SetupCControlId;
  direction?: SetupCContinuationDirection;
  replicates?: number;
  maxCells?: number;
  seed?: string;
  /** Declared spacing for finite-window diagnostic samples. */
  sampleCadence?: number;
  /** Explicit extra cells selected after inspecting a coarse map. */
  refineNear?: SetupCParameters[];
}

export interface SetupCCellOptions {
  variant?: SetupCVariantId;
  preparation?: SetupBPreparationId;
  preparationSeed?: string;
  linkHistory?: 'established' | 'empty-links';
  duration?: number;
  preparationDuration?: number;
  minimumCycles?: number;
  runId?: string;
  replicate?: number;
  control?: SetupCControlId;
  continuationFrom?: EnvelopeSnapshot;
  /** Declared spacing for finite-window diagnostic samples. */
  sampleCadence?: number;
}

export type SetupCVariantId = `${SetupBEmissionId}-${SetupBResponseId}`;

export interface SetupCWindow {
  start: number;
  end: number;
}

export interface SetupCDiagnostics {
  classification: PairClassification;
  meanFrequencyDifference: number;
  phaseDrift: number;
  phaseRange: number;
  frequencyModulation: Record<string, { minimum: number; maximum: number }>;
  windows: SetupCWindow[];
  criteria: {
    frequencyTolerance: number;
    phaseRangeTolerance: number;
    minimumCycles: number;
    sampleCadence: number;
  };
  irregularity: {
    phaseIncrementRange: number;
    frequencyIncrementRange: number;
    interpretation: 'diagnostic-only';
  };
}

export interface SetupCCellRun {
  schemaVersion: 'setup-c-cell-v1';
  modelVersion: 'paper-i-v1';
  runId: string;
  replicate: number;
  variant: SetupCVariantId;
  control: SetupCControl;
  preparation: SetupCPreparation;
  parameters: SetupCParameters;
  physical: SetupCPhysicalParameters;
  scenario: Scenario;
  envelope: EnvelopeOptions;
  samples: EnvelopeSample[];
  finalSnapshot: EnvelopeSnapshot;
  diagnostics: SetupCDiagnostics;
  limitations: string[];
}

export interface SetupCReplicateUncertainty {
  replicateCount: number;
  values: number[];
  mean: number;
  standardDeviation: number;
  normalApproximationHalfWidth: number | null;
  interpretation: 'independent-replicate-diagnostic';
}

export interface SetupCScanCell {
  key: string;
  parameters: SetupCParameters;
  status: 'resolved' | 'unresolved' | 'numerically-failed' | 'unrun';
  runIds: string[];
  trajectoryRunIds: string[];
  classificationStatuses: PairClassification['status'][];
  preparationIds: SetupBPreparationId[];
  replicateUncertainty: SetupCReplicateUncertainty | null;
  replicateUncertaintyByPreparation: Partial<
    Record<SetupBPreparationId, SetupCReplicateUncertainty>
  >;
  criteria: {
    windows: SetupCWindow[];
    minimumCycles: number;
    frequencyTolerance: number;
    phaseRangeTolerance: number;
    sampleCadence: number;
  };
  failure?: { message: string };
}

export interface SetupCContinuationRecord {
  direction: SetupCContinuationDirection;
  orderedCellKeys: string[];
  handoffs: Array<{
    fromRunId: string;
    toRunId: string;
    kind: 'full-state-snapshot';
    snapshot: EnvelopeSnapshot;
  }>;
  restarts: Array<{ runId: string; cellKey: string; preparationId: string }>;
  interpretation: string;
}

export interface SetupCScan {
  schemaVersion: 'setup-c-scan-v1';
  modelVersion: 'paper-i-v1';
  variant: SetupCVariantId;
  control: SetupCControl;
  metadata: {
    varied: Record<SetupCParameterId, number[]>;
    rawVaried: Record<SetupCParameterId, number[]>;
    fixed: Record<string, number | string>;
    dimensionlessDefinitions: Record<SetupCParameterId, string>;
    baselineMatchingRule: string;
    sourceSection: 'Paper I §11.4';
  };
  cells: SetupCScanCell[];
  runs: SetupCCellRun[];
  masks: {
    unresolved: boolean[];
    numericalFailure: boolean[];
    unrun: boolean[];
  };
  continuation: SetupCContinuationRecord;
  refinement: {
    requested: SetupCParameters[];
    runIds: string[];
    interpretation: 'selective-diagnostic-refinement';
  };
  limitations: string[];
}

export const setupCControls: readonly SetupCControl[] = [
  {
    id: 'baseline',
    label: 'Baseline',
    description:
      'Uses the requested scan coordinates without a control override.',
  },
  {
    id: 'no-feedback',
    label: 'Weak/no feedback',
    description:
      'Sets the signed gain to zero while retaining the other coordinates.',
    fixedParameter: 'gain',
    fixedValue: 0,
  },
  {
    id: 'zero-contrast',
    label: 'Zero contrast',
    description:
      'Sets directional contrast to zero while retaining total emission.',
    fixedParameter: 'contrast',
    fixedValue: 0,
  },
  {
    id: 'small-positive-delay',
    label: 'Small positive delay',
    description:
      'Uses a declared strictly positive dimensionless delay control.',
    fixedParameter: 'delay',
    fixedValue: DEFAULT_SMALL_DELAY,
  },
];

export const setupCDefaultAxes: Readonly<Record<SetupCParameterId, number[]>> =
  {
    detuning: [-0.05, 0, 0.05],
    delay: [0.5, 1],
    gain: [-0.1, 0, 0.1],
    contrast: [0, 1],
    relaxationTime: [0.5, 1],
  };

const dimensionlessDefinitions: Record<SetupCParameterId, string> = {
  detuning: '(omega0_B - omega0_A) / omegaReference',
  delay: 'omegaReference * tau',
  gain: 'g / omegaReference',
  contrast: 'directional contrast a in [0, 1]',
  relaxationTime: 'omegaReference * T_rel',
};

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

const setupCPreparationIds: readonly SetupBPreparationId[] = [
  'co-phase',
  'pi-reflection',
  'small-offset',
  'seeded-random',
];

function validatePreparationId(id: string): asserts id is SetupBPreparationId {
  if (!setupCPreparationIds.includes(id as SetupBPreparationId))
    throw new RangeError(`Unknown Setup C preparation ${id}.`);
}

function preparation(
  id: SetupBPreparationId,
  seed: string,
  linkHistory: 'established' | 'empty-links',
): SetupCPreparation {
  validatePreparationId(id);
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
  };
}

function validateParameters(parameters: SetupCParameters): void {
  for (const id of [
    'detuning',
    'delay',
    'gain',
    'contrast',
    'relaxationTime',
  ] as const)
    finite(parameters[id], `Setup C ${id}`);
  if (!(parameters.detuning > -1))
    throw new RangeError('Setup C detuning must be greater than -1.');
  if (!(parameters.delay > 0))
    throw new RangeError('Setup C delay must be strictly positive.');
  if (parameters.contrast < 0 || parameters.contrast > 1)
    throw new RangeError('Setup C contrast must be in [0, 1].');
  if (!(parameters.relaxationTime > 0))
    throw new RangeError('Setup C relaxationTime must be strictly positive.');
}

function controlFor(id: SetupCControlId): SetupCControl {
  const control = setupCControls.find((candidate) => candidate.id === id);
  if (!control) throw new RangeError(`Unknown Setup C control ${id}.`);
  return clone(control);
}

function effectiveParameters(
  input: SetupCParameters,
  control: SetupCControl,
): SetupCParameters {
  const parameters = clone(input);
  if (control.fixedParameter)
    parameters[control.fixedParameter] = control.fixedValue!;
  validateParameters(parameters);
  return parameters;
}

function validatePreparationDuration(
  duration: number,
  preparationDuration: number,
) {
  finite(duration, 'Setup C duration');
  finite(preparationDuration, 'Setup C preparation duration');
  if (
    !(duration > 0) ||
    preparationDuration < 0 ||
    preparationDuration >= duration
  )
    throw new RangeError(
      'Setup C duration must exceed its nonnegative preparation duration.',
    );
}

function scenarioFor(
  parameters: SetupCParameters,
  variantId: SetupCVariantId,
  prep: SetupCPreparation,
): { scenario: Scenario; physical: SetupCPhysicalParameters } {
  validateParameters(parameters);
  const variant = setupBVariants.find(
    (candidate) => candidate.id === variantId,
  );
  if (!variant) throw new RangeError(`Unknown Setup C variant ${variantId}.`);
  const scenario = clone(pair) as Scenario;
  const omegaA = OMEGA_REFERENCE;
  const omegaB = omegaA * (1 + parameters.detuning);
  const delay = parameters.delay / OMEGA_REFERENCE;
  const gain = parameters.gain * OMEGA_REFERENCE;
  const relaxationTime = parameters.relaxationTime / OMEGA_REFERENCE;
  if (variant.response === 'R0' && gain !== 0)
    throw new RangeError('Setup C R0 requires zero dimensionless gain.');
  if (Math.abs(gain) >= Math.min(omegaA, omegaB))
    throw new RangeError('Setup C gain must satisfy |g| < every omega0.');
  scenario.id = `setup-c-${variantId}-${parameters.detuning}-${parameters.delay}-${parameters.gain}-${parameters.contrast}-${parameters.relaxationTime}`;
  scenario.nodes[0]!.omega0 = omegaA;
  scenario.nodes[1]!.omega0 = omegaB;
  scenario.nodes[0]!.omega = omegaA;
  scenario.nodes[1]!.omega = omegaB;
  for (const node of scenario.nodes) {
    node.phi = node.id === NODE_A ? prep.phaseA : prep.phaseB;
    node.amplitude = parameters.contrast;
    node.gain = gain;
    node.relaxationTime = relaxationTime;
    node.emission =
      variant.emission === 'E0'
        ? { law: 'E0', nu: (DEFAULT_Q * node.omega0) / TAU }
        : { law: 'E1', q: DEFAULT_Q };
    node.response = variant.response;
    scenario.initialHistory.nodes[node.id] = {
      phiAtZero: node.phi,
      omega: node.omega,
    };
  }
  scenario.nodes[1]!.position = delay * scenario.c0;
  scenario.links = [
    {
      id: 'A-B',
      source: NODE_A,
      target: NODE_B,
      sourcePort: 'right',
      targetPort: 'left',
      delay,
    },
    {
      id: 'B-A',
      source: NODE_B,
      target: NODE_A,
      sourcePort: 'left',
      targetPort: 'right',
      delay,
    },
  ];
  scenario.initialHistory.startTime = -delay;
  scenario.initialHistory.nodes[NODE_A]!.omega = omegaA;
  scenario.initialHistory.nodes[NODE_B]!.omega = omegaB;
  scenario.solver.step = Math.min(scenario.solver.step ?? 0.01, 0.02);
  return {
    scenario,
    physical: {
      omegaReference: OMEGA_REFERENCE,
      omega0: { A: omegaA, B: omegaB },
      delay,
      gain: { A: gain, B: gain },
      relaxationTime: { A: relaxationTime, B: relaxationTime },
      contrast: { A: parameters.contrast, B: parameters.contrast },
    },
  };
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

function windowsFor(
  duration: number,
  preparationDuration: number,
): SetupCWindow[] {
  const start = preparationDuration + (duration - preparationDuration) / 2;
  const middle = start + (duration - start) / 2;
  return [
    { start, end: middle },
    { start, end: duration },
  ];
}

function runEnvelope(
  scenario: Scenario,
  envelope: EnvelopeOptions,
  duration: number,
  sampleTimes: number[],
  sampleCadence: number,
  continuationFrom?: EnvelopeSnapshot,
): { samples: EnvelopeSample[]; snapshot: EnvelopeSnapshot } {
  const solver = new EnvelopeSolver(scenario, envelope);
  if (continuationFrom) solver.adoptParameterContinuation(continuationFrom);
  const samples = [solver.sample()];
  const end = solver.time + duration;
  const cadenceTargets: number[] = [];
  const cadenceCount = Math.ceil(duration / sampleCadence);
  for (let index = 1; index <= cadenceCount; index++)
    cadenceTargets.push(Math.min(end, solver.time + index * sampleCadence));
  for (const target of [
    ...new Set([solver.time, ...sampleTimes, ...cadenceTargets, end]),
  ].sort((a, b) => a - b)) {
    if (target < solver.time) continue;
    while (solver.time < target) {
      const previous = solver.time;
      solver.advance(target);
      if (solver.time > previous) samples.push(solver.sample());
    }
  }
  return { samples, snapshot: solver.snapshot() };
}

function analysisSamples(samples: EnvelopeSample[]): AnalysisSample[] {
  return samples.map((sample) => ({ time: sample.time, nodes: sample.nodes }));
}

function diagnosticsFor(
  samples: EnvelopeSample[],
  windows: SetupCWindow[],
  minimumCycles: number,
  sampleCadence: number,
): SetupCDiagnostics {
  const series = analysisSamples(samples);
  const criteria = {
    transientEnd: windows[0]!.start,
    windows,
    frequencyTolerance: DEFAULT_FREQUENCY_TOLERANCE,
    phaseRangeTolerance: DEFAULT_PHASE_RANGE_TOLERANCE,
    minimumCycles,
  };
  const classification = classifyPair(
    series.length ? { samples: series } : { samples: [] },
    NODE_A,
    NODE_B,
    criteria,
  );
  const phases = pairPhase(series, NODE_A, NODE_B).map(
    (point) => point.unwrapped,
  );
  const frequencyValues = Object.fromEntries(
    [NODE_A, NODE_B].map((id) => [
      id,
      series.map((sample) => sample.nodes[id]!.omega),
    ]),
  ) as Record<string, number[]>;
  const frequencies = Object.fromEntries(
    Object.entries(frequencyValues).map(([id, values]) => [
      id,
      { minimum: Math.min(...values), maximum: Math.max(...values) },
    ]),
  );
  const phaseIncrements = phases
    .slice(1)
    .map((value, index) => value - phases[index]!);
  const frequencyIncrements = series
    .slice(1)
    .map(
      (sample, index) =>
        sample.nodes[NODE_A]!.omega - series[index]!.nodes[NODE_A]!.omega,
    );
  return {
    classification,
    meanFrequencyDifference:
      classification.evidence[0]?.frequencyMismatch ?? Number.POSITIVE_INFINITY,
    phaseDrift: phases.at(-1)! - phases[0]!,
    phaseRange: Math.max(...phases) - Math.min(...phases),
    frequencyModulation: frequencies,
    windows,
    criteria: {
      frequencyTolerance: DEFAULT_FREQUENCY_TOLERANCE,
      phaseRangeTolerance: DEFAULT_PHASE_RANGE_TOLERANCE,
      minimumCycles,
      sampleCadence,
    },
    irregularity: {
      phaseIncrementRange: phaseIncrements.length
        ? Math.max(...phaseIncrements) - Math.min(...phaseIncrements)
        : 0,
      frequencyIncrementRange: frequencyIncrements.length
        ? Math.max(...frequencyIncrements) - Math.min(...frequencyIncrements)
        : 0,
      interpretation: 'diagnostic-only',
    },
  };
}

function keyFor(parameters: SetupCParameters): string {
  return [
    parameters.detuning,
    parameters.delay,
    parameters.gain,
    parameters.contrast,
    parameters.relaxationTime,
  ]
    .map((value) => value.toString())
    .join('|');
}

export function createSetupCCell(
  parameters: SetupCParameters,
  options: SetupCCellOptions = {},
): SetupCCellRun {
  const variant = options.variant ?? 'E1-R1';
  const control = controlFor(options.control ?? 'baseline');
  const effective = effectiveParameters(parameters, control);
  const duration = options.duration ?? DEFAULT_DURATION;
  const preparationDuration =
    options.preparationDuration ?? DEFAULT_PREPARATION_DURATION;
  validatePreparationDuration(duration, preparationDuration);
  const sampleCadence = options.sampleCadence ?? DEFAULT_SAMPLE_CADENCE;
  finite(sampleCadence, 'Setup C sampleCadence');
  if (!(sampleCadence > 0) || duration / sampleCadence > MAX_DIAGNOSTIC_SAMPLES)
    throw new RangeError(
      `Setup C sampleCadence must be positive and produce at most ${MAX_DIAGNOSTIC_SAMPLES} samples.`,
    );
  const prep = preparation(
    options.preparation ?? 'co-phase',
    options.preparationSeed ?? `signal-space-setup-c-${keyFor(effective)}`,
    options.linkHistory ?? 'established',
  );
  const { scenario, physical } = scenarioFor(effective, variant, prep);
  const continuationTime = options.continuationFrom?.time ?? 0;
  const windows = windowsFor(duration, preparationDuration).map((window) => ({
    start: window.start + continuationTime,
    end: window.end + continuationTime,
  }));
  const envelope: EnvelopeOptions = {
    preparation: prep.linkHistory,
    prehistory: prehistoryFor(scenario),
  };
  const run = runEnvelope(
    scenario,
    envelope,
    duration,
    windows.flatMap((window) => [window.start, window.end]),
    sampleCadence,
    options.continuationFrom,
  );
  return {
    schemaVersion: 'setup-c-cell-v1',
    modelVersion: 'paper-i-v1',
    runId:
      options.runId ??
      `setup-c:${variant}:${options.preparation ?? 'co-phase'}:${keyFor(effective)}:${options.replicate ?? 0}`,
    replicate: options.replicate ?? 0,
    variant,
    control,
    preparation: prep,
    parameters: effective,
    physical,
    scenario,
    envelope,
    samples: run.samples,
    finalSnapshot: run.snapshot,
    diagnostics: diagnosticsFor(
      run.samples,
      windows,
      options.minimumCycles ?? DEFAULT_MINIMUM_CYCLES,
      sampleCadence,
    ),
    limitations: [
      'Setup C classifications are finite-window evidence and never assert locking, coexistence, or chaos.',
      'Irregularity values are descriptive diagnostics; no chaos classifier is implemented.',
      'Independent mode uses separate restarts; forward/reverse mode adopts the predecessor full solver state for the first replicate of each successor cell.',
    ],
  };
}

function valuesFor(
  axes: Partial<Record<SetupCParameterId, number[]>> | undefined,
): Record<SetupCParameterId, number[]> {
  const result = {} as Record<SetupCParameterId, number[]>;
  for (const id of Object.keys(setupCDefaultAxes) as SetupCParameterId[]) {
    const values = axes?.[id] ?? setupCDefaultAxes[id];
    if (!values?.length)
      throw new RangeError(`Setup C axis ${id} needs at least one value.`);
    values.forEach((value) => finite(value, `Setup C axis ${id}`));
    if (new Set(values).size !== values.length)
      throw new RangeError(`Setup C axis ${id} contains duplicate values.`);
    result[id] = [...values];
  }
  return result;
}

function combinations(
  axes: Record<SetupCParameterId, number[]>,
): SetupCParameters[] {
  const ids = Object.keys(axes) as SetupCParameterId[];
  return ids.reduce<SetupCParameters[]>(
    (rows, id) =>
      rows.flatMap((row) =>
        axes[id]!.map((value) => ({ ...row, [id]: value }) as SetupCParameters),
      ),
    [{} as SetupCParameters],
  );
}

function replicateUncertainty(values: number[]): SetupCReplicateUncertainty {
  const mean = values.reduce((sum, value) => sum + value, 0) / values.length;
  const variance =
    values.length > 1
      ? values.reduce((sum, value) => sum + (value - mean) ** 2, 0) /
        (values.length - 1)
      : 0;
  return {
    replicateCount: values.length,
    values: [...values],
    mean,
    standardDeviation: Math.sqrt(variance),
    normalApproximationHalfWidth:
      values.length > 1 ? 1.96 * Math.sqrt(variance / values.length) : null,
    interpretation: 'independent-replicate-diagnostic',
  };
}

function uncertaintyByPreparation(
  runs: SetupCCellRun[],
): Partial<Record<SetupBPreparationId, SetupCReplicateUncertainty>> {
  const result: Partial<
    Record<SetupBPreparationId, SetupCReplicateUncertainty>
  > = {};
  for (const preparationId of new Set(runs.map((run) => run.preparation.id))) {
    result[preparationId] = replicateUncertainty(
      runs
        .filter((run) => run.preparation.id === preparationId)
        .map((run) => run.diagnostics.meanFrequencyDifference),
    );
  }
  return result;
}

function classifyCell(
  runs: SetupCCellRun[],
  parameters: SetupCParameters,
  minimumCycles: number,
  sampleCadence: number,
): SetupCScanCell {
  const statuses = runs.map((run) => run.diagnostics.classification.status);
  const failed = statuses.includes('numerically-failed');
  const unresolved = statuses.includes('unresolved');
  const valuesByPreparation = uncertaintyByPreparation(runs);
  const values =
    Object.keys(valuesByPreparation).length === 1
      ? Object.values(valuesByPreparation)[0]!
      : null;
  const firstDiagnostics = runs[0]?.diagnostics;
  return {
    key: keyFor(parameters),
    parameters,
    status: failed
      ? 'numerically-failed'
      : unresolved
        ? 'unresolved'
        : 'resolved',
    runIds: runs.map((run) => run.runId),
    trajectoryRunIds: runs.map((run) => run.runId),
    classificationStatuses: statuses,
    preparationIds: [...new Set(runs.map((run) => run.preparation.id))],
    replicateUncertainty: values,
    replicateUncertaintyByPreparation: valuesByPreparation,
    criteria: {
      windows: firstDiagnostics?.windows ?? [],
      minimumCycles,
      frequencyTolerance:
        firstDiagnostics?.criteria.frequencyTolerance ??
        DEFAULT_FREQUENCY_TOLERANCE,
      phaseRangeTolerance:
        firstDiagnostics?.criteria.phaseRangeTolerance ??
        DEFAULT_PHASE_RANGE_TOLERANCE,
      sampleCadence: firstDiagnostics?.criteria.sampleCadence ?? sampleCadence,
    },
    ...(failed
      ? { failure: { message: 'At least one replicate failed numerically.' } }
      : {}),
  };
}

export function runSetupCScan(options: SetupCScanOptions = {}): SetupCScan {
  const rawAxes = valuesFor(options.axes);
  const control = controlFor(options.control ?? 'baseline');
  const axes = {
    ...rawAxes,
    ...(control.fixedParameter
      ? { [control.fixedParameter]: [control.fixedValue!] }
      : {}),
  } as Record<SetupCParameterId, number[]>;
  const variant = options.variant ?? 'E1-R1';
  if (!setupBVariants.some((candidate) => candidate.id === variant))
    throw new RangeError(`Unknown Setup C variant ${variant}.`);
  const direction = options.direction ?? 'independent';
  const minimumCycles = options.minimumCycles ?? DEFAULT_MINIMUM_CYCLES;
  finite(minimumCycles, 'Setup C minimumCycles');
  if (minimumCycles < 0)
    throw new RangeError('Setup C minimumCycles must be nonnegative.');
  const replicateCount = options.replicates ?? 1;
  if (
    !Number.isInteger(replicateCount) ||
    replicateCount < 1 ||
    replicateCount > MAX_REPLICATES
  )
    throw new RangeError(
      `Setup C replicates must be an integer from 1 through ${MAX_REPLICATES}.`,
    );
  const cells = combinations(axes);
  if (variant.endsWith('-R0') && axes.gain.some((gain) => gain !== 0))
    throw new RangeError('Setup C R0 scans require a zero gain axis.');
  const preparations = options.preparations ?? [
    options.preparation ?? 'co-phase',
  ];
  if (!preparations.length)
    throw new RangeError('Setup C needs at least one preparation.');
  if (new Set(preparations).size !== preparations.length)
    throw new RangeError('Setup C preparations must be unique.');
  preparations.forEach(validatePreparationId);
  const ordered = direction === 'reverse' ? [...cells].reverse() : cells;
  const maxCells = options.maxCells ?? ordered.length;
  if (!Number.isInteger(maxCells) || maxCells < 0)
    throw new RangeError('Setup C maxCells must be a nonnegative integer.');
  const sampleCadence = options.sampleCadence ?? DEFAULT_SAMPLE_CADENCE;
  finite(sampleCadence, 'Setup C sampleCadence');
  if (!(sampleCadence > 0))
    throw new RangeError('Setup C sampleCadence must be positive.');
  const duration = options.duration ?? DEFAULT_DURATION;
  const preparationDuration =
    options.preparationDuration ?? DEFAULT_PREPARATION_DURATION;
  validatePreparationDuration(duration, preparationDuration);
  if (duration / sampleCadence > MAX_DIAGNOSTIC_SAMPLES)
    throw new RangeError(
      `Setup C sampleCadence must produce at most ${MAX_DIAGNOSTIC_SAMPLES} samples.`,
    );
  const plannedCellCount = Math.min(maxCells, ordered.length);
  const plannedRuns =
    plannedCellCount * preparations.length * replicateCount +
    (options.refineNear?.length ?? 0);
  if (plannedRuns > MAX_SCAN_RUNS)
    throw new RangeError(
      `Setup C scan exceeds the ${MAX_SCAN_RUNS}-run diagnostic budget.`,
    );
  for (const parameters of cells)
    scenarioFor(
      effectiveParameters(parameters, control),
      variant,
      preparation('co-phase', 'setup-c-validation', 'established'),
    );
  const runs: SetupCCellRun[] = [];
  const scanCells: SetupCScanCell[] = [];
  const handoffs: SetupCContinuationRecord['handoffs'] = [];
  const restarts: SetupCContinuationRecord['restarts'] = [];
  let previous: SetupCCellRun | undefined;
  for (const [index, rawParameters] of ordered.entries()) {
    const parameters = effectiveParameters(rawParameters, control);
    const key = keyFor(parameters);
    if (index >= maxCells) {
      scanCells.push({
        key,
        parameters,
        status: 'unrun',
        runIds: [],
        trajectoryRunIds: [],
        classificationStatuses: [],
        preparationIds: preparations,
        replicateUncertainty: null,
        replicateUncertaintyByPreparation: {},
        criteria: {
          windows: [],
          minimumCycles,
          frequencyTolerance: DEFAULT_FREQUENCY_TOLERANCE,
          phaseRangeTolerance: DEFAULT_PHASE_RANGE_TOLERANCE,
          sampleCadence,
        },
      });
      continue;
    }
    const cellRuns: SetupCCellRun[] = [];
    const previousCell = previous;
    try {
      for (const preparationId of preparations)
        for (let replicate = 0; replicate < replicateCount; replicate++) {
          const seed = `${options.preparationSeed ?? options.seed ?? 'signal-space-setup-c-v1'}:${key}:${preparationId}:${replicate}`;
          const run = createSetupCCell(parameters, {
            variant,
            preparation: preparationId,
            preparationSeed: seed,
            linkHistory: options.linkHistory ?? 'established',
            duration: options.duration ?? DEFAULT_DURATION,
            preparationDuration:
              options.preparationDuration ?? DEFAULT_PREPARATION_DURATION,
            sampleCadence,
            minimumCycles,
            replicate,
            control: 'baseline',
            runId: `setup-c:${variant}:${preparationId}:${key}:${replicate}`,
            ...(direction === 'independent' ||
            replicate !== 0 ||
            preparationId !== preparations[0] ||
            !previousCell
              ? {}
              : { continuationFrom: previousCell.finalSnapshot }),
          });
          cellRuns.push(run);
          runs.push(run);
          const isHandoff =
            direction !== 'independent' &&
            preparationId === preparations[0] &&
            replicate === 0 &&
            previousCell !== undefined;
          if (isHandoff) {
            handoffs.push({
              fromRunId: previousCell.runId,
              toRunId: run.runId,
              kind: 'full-state-snapshot',
              snapshot: clone(previousCell.finalSnapshot),
            });
          } else {
            restarts.push({
              runId: run.runId,
              cellKey: key,
              preparationId: run.preparation.id,
            });
          }
        }
      previous = cellRuns.find(
        (run) => run.preparation.id === preparations[0] && run.replicate === 0,
      );
      scanCells.push(
        classifyCell(cellRuns, parameters, minimumCycles, sampleCadence),
      );
    } catch (error) {
      if (
        !(error instanceof EnvelopeFailure) ||
        error.code !== 'NUMERICAL_FAILURE'
      )
        throw error;
      scanCells.push({
        key,
        parameters,
        status: 'numerically-failed',
        runIds: cellRuns.map((run) => run.runId),
        trajectoryRunIds: cellRuns.map((run) => run.runId),
        classificationStatuses: cellRuns.map(
          (run) => run.diagnostics.classification.status,
        ),
        preparationIds: [...new Set(cellRuns.map((run) => run.preparation.id))],
        replicateUncertainty:
          preparations.length === 1 && cellRuns.length
            ? replicateUncertainty(
                cellRuns.map((run) => run.diagnostics.meanFrequencyDifference),
              )
            : null,
        replicateUncertaintyByPreparation: uncertaintyByPreparation(cellRuns),
        criteria: {
          windows: cellRuns[0]?.diagnostics.windows ?? [],
          minimumCycles,
          frequencyTolerance:
            cellRuns[0]?.diagnostics.criteria.frequencyTolerance ??
            DEFAULT_FREQUENCY_TOLERANCE,
          phaseRangeTolerance:
            cellRuns[0]?.diagnostics.criteria.phaseRangeTolerance ??
            DEFAULT_PHASE_RANGE_TOLERANCE,
          sampleCadence:
            cellRuns[0]?.diagnostics.criteria.sampleCadence ?? sampleCadence,
        },
        failure: {
          message:
            error instanceof Error ? error.message : 'Setup C cell failed.',
        },
      });
    }
  }
  const refinementRuns: SetupCCellRun[] = [];
  for (const [index, requested] of (options.refineNear ?? []).entries()) {
    const parameters = effectiveParameters(requested, control);
    const run = createSetupCCell(parameters, {
      variant,
      preparation: preparations[0]!,
      linkHistory: options.linkHistory ?? 'established',
      duration: options.duration ?? DEFAULT_DURATION,
      preparationDuration:
        options.preparationDuration ?? DEFAULT_PREPARATION_DURATION,
      sampleCadence,
      preparationSeed: `${options.preparationSeed ?? options.seed ?? 'signal-space-setup-c-v1'}:refined:${index}`,
      minimumCycles,
      replicate: 0,
      control: 'baseline',
      runId: `setup-c:${variant}:${preparations[0]}:${keyFor(parameters)}:refined-${index}`,
    });
    refinementRuns.push(run);
    runs.push(run);
  }
  const byKey = new Map(scanCells.map((cell) => [cell.key, cell]));
  const cellsInMapOrder = cells.map((raw) =>
    byKey.get(keyFor(effectiveParameters(raw, control)))!,
  );
  return {
    schemaVersion: 'setup-c-scan-v1',
    modelVersion: 'paper-i-v1',
    variant,
    control,
    metadata: {
      varied: axes,
      rawVaried: rawAxes,
      fixed: {
        omegaReference: OMEGA_REFERENCE,
        q: DEFAULT_Q,
        preparation:
          preparations.length === 1 ? preparations[0]! : preparations.join(','),
        duration: options.duration ?? DEFAULT_DURATION,
        preparationDuration:
          options.preparationDuration ?? DEFAULT_PREPARATION_DURATION,
        control: control.id,
        sampleCadence,
        preparationSeed:
          options.preparationSeed ?? options.seed ?? 'signal-space-setup-c-v1',
        frequencyTolerance: DEFAULT_FREQUENCY_TOLERANCE,
        phaseRangeTolerance: DEFAULT_PHASE_RANGE_TOLERANCE,
      },
      dimensionlessDefinitions,
      baselineMatchingRule:
        'E0 nu_i = E1 q omega0_i / (2 pi), with q fixed at 3.',
      sourceSection: 'Paper I §11.4',
    },
    cells: cellsInMapOrder,
    runs,
    masks: {
      unresolved: cellsInMapOrder.map((cell) => cell.status === 'unresolved'),
      numericalFailure: cellsInMapOrder.map(
        (cell) => cell.status === 'numerically-failed',
      ),
      unrun: cellsInMapOrder.map((cell) => cell.status === 'unrun'),
    },
    continuation: {
      direction,
      orderedCellKeys: ordered.map((raw) =>
        keyFor(effectiveParameters(raw, control)),
      ),
      handoffs,
      restarts,
      interpretation:
        direction === 'independent'
          ? 'Every cell is a separate restart; no continuation state is implied.'
          : 'The first replicate of each successor cell adopts the predecessor complete solver snapshot; other preparations and replicates remain separate restarts. No phase reset or hidden observer state is introduced.',
    },
    refinement: {
      requested: clone(options.refineNear ?? []),
      runIds: refinementRuns.map((run) => run.runId),
      interpretation: 'selective-diagnostic-refinement',
    },
    limitations: [
      'This is a small deterministic scan layer for technical validation, not a publication-scale parameter survey.',
      'Unresolved, numerically failed, and unrun cells are distinct and carry no inferred regime label.',
      'Coexistence is not asserted by a finite-window status; multiple preparations should be compared explicitly.',
      'Irregularity diagnostics do not constitute a chaos classifier or a Lyapunov result.',
    ],
  };
}

export function createSetupCDefinition(
  parameters: SetupCParameters = {
    detuning: 0,
    delay: 1,
    gain: 0.1,
    contrast: 1,
    relaxationTime: 1,
  },
  options: SetupCCellOptions = {},
): ExperimentDefinition {
  const run = createSetupCCell(parameters, options);
  return {
    schemaVersion: 'paper-i-experiment-v1',
    id: `setup-c-${run.runId.replaceAll(':', '-')}`,
    description:
      'Setup C pair-scan cell; technical diagnostic, not a paper result.',
    scenario: run.scenario,
    mode: 'envelope',
    until: options.duration ?? DEFAULT_DURATION,
    envelope: run.envelope,
    parameters: [],
    controls: [
      {
        id: run.control.id,
        kind: 'analytic',
        description: run.control.description,
      },
    ],
    windows: {
      transient: options.preparationDuration ?? DEFAULT_PREPARATION_DURATION,
      measurement: {
        start: run.diagnostics.windows[0]!.start,
        end: run.diagnostics.windows.at(-1)!.end,
      },
      nested: run.diagnostics.windows.slice(0, -1),
    },
    tolerances: {
      absolute: run.scenario.solver.absoluteTolerance,
      relative: run.scenario.solver.relativeTolerance,
    },
    replicates: 1,
    seed: 'signal-space-setup-c-v1',
    observables: ['phase', 'frequency', 'retarded-phase'],
    budgets: { maxJobs: 1, maxSteps: 10000, checkpointEvery: 1 },
  };
}

export function createSetupCSmokeDefinitions(): ExperimentDefinition[] {
  return [
    createSetupCDefinition({
      detuning: 0,
      delay: 0.5,
      gain: 0,
      contrast: 0,
      relaxationTime: 1,
    }),
    createSetupCDefinition({
      detuning: 0.02,
      delay: 1,
      gain: -0.05,
      contrast: 1,
      relaxationTime: 0.5,
    }),
  ];
}
