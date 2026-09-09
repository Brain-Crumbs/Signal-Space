import type { Emission, Intervention, Scenario } from '@signal-space/model';
import { validateScenario } from '@signal-space/model';
import {
  execute,
  type EnvelopeOptions,
  type PacketOptions,
  type RunEvent,
} from '@signal-space/sim';

export const EXPERIMENT_SCHEMA_VERSION = 'paper-i-experiment-v1' as const;
export const MANIFEST_KIND = 'signal-space-run-manifest' as const;
export const CHECKPOINT_KIND = 'signal-space-sweep-checkpoint-v1' as const;

type JsonPrimitive = string | number | boolean | null;
export type ParameterValue = JsonPrimitive;
export type VariantResponse = 'R0' | 'R1' | 'R2';
export type ControlKind = 'analytic' | 'causal' | 'state-bound' | 'statistical';
export type ObservableName =
  | 'phase'
  | 'frequency'
  | 'rates'
  | 'ticks'
  | 'retarded-phase'
  | 'packets'
  | 'observer-records';

export interface ParameterAxis {
  id: string;
  /** Dot paths use nodes.<node id>.<field> for node fields. */
  path: string;
  values: ParameterValue[];
}

export interface ScenarioVariant {
  id: string;
  description?: string;
  response?: Record<string, VariantResponse>;
  emission?: Record<string, Emission>;
}

export interface ExperimentControl {
  id: string;
  kind: ControlKind;
  description?: string;
  parameters?: Record<string, ParameterValue>;
}

export interface ExperimentWindows {
  transient: number;
  measurement: { start: number; end: number };
  nested?: Array<{ start: number; end: number }>;
}

export interface ExperimentBudgets {
  maxJobs: number;
  maxRuns?: number;
  maxSteps?: number;
  maxEvents?: number;
  maxPending?: number;
  checkpointEvery?: number;
}

export interface ExperimentDefinition {
  schemaVersion: typeof EXPERIMENT_SCHEMA_VERSION;
  id: string;
  description?: string;
  scenario: Scenario;
  mode: 'inspect' | 'envelope' | 'packets';
  until: number;
  envelope?: EnvelopeOptions;
  packets?: Omit<PacketOptions, 'seed'>;
  parameters?: ParameterAxis[];
  variants?: ScenarioVariant[];
  controls?: ExperimentControl[];
  interventions?: Intervention[];
  windows: ExperimentWindows;
  tolerances: { absolute: number; relative: number };
  replicates: number;
  seed: string;
  observables: ObservableName[];
  budgets: ExperimentBudgets;
}

export interface ManifestProvenance {
  modelVersion: Scenario['modelVersion'];
  codeRevision: string;
  dirty: boolean;
  createdAt: string;
  source: string;
}

export interface ExperimentManifest {
  kind: typeof MANIFEST_KIND;
  schemaVersion: 1;
  experimentId: string;
  runId: string;
  definitionHash: string;
  scenarioHash: string;
  replicate: number;
  variantId: string;
  controlId: string;
  parameters: Record<string, ParameterValue>;
  scenario: Scenario;
  execution: {
    mode: ExperimentDefinition['mode'];
    until: number;
    envelope?: EnvelopeOptions;
    packets?: Omit<PacketOptions, 'seed'>;
  };
  windows: ExperimentWindows;
  tolerances: ExperimentDefinition['tolerances'];
  observables: ObservableName[];
  budgets: ExperimentBudgets;
  seed?: string;
  provenance: ManifestProvenance;
  continuationOf?: string;
}

export interface ExperimentPlan {
  definition: ExperimentDefinition;
  definitionHash: string;
  manifests: ExperimentManifest[];
}

export interface RunResult {
  runId: string;
  manifest: ExperimentManifest;
  events: RunEvent[];
  status: 'completed' | 'cancelled' | 'failed' | 'incomplete';
}

export interface SweepCheckpoint {
  kind: typeof CHECKPOINT_KIND;
  schemaVersion: 1;
  sweepId: string;
  definitionHash: string;
  planSize: number;
  completed: RunResult[];
  /** Append-only attempt history, including failed/cancelled/incomplete runs. */
  attempts: RunResult[];
  createdAt: string;
  status: 'partial' | 'completed' | 'cancelled';
}

export interface SweepOutcome {
  status: 'completed' | 'partial' | 'cancelled';
  results: RunResult[];
  checkpoint: SweepCheckpoint;
}

export interface SweepOptions {
  concurrency?: number;
  signal?: AbortSignal;
  checkpoint?: SweepCheckpoint;
  onRun?: (result: RunResult) => void;
  onCheckpoint?: (checkpoint: SweepCheckpoint) => void;
}

export interface ManifestOptions {
  codeRevision?: string;
  dirty?: boolean;
  source?: string;
  createdAt?: string;
}

function invalid(message: string): never {
  throw new Error(`Invalid experiment definition: ${message}`);
}

function isPrimitive(value: unknown): value is JsonPrimitive {
  return (
    value === null ||
    typeof value === 'string' ||
    typeof value === 'boolean' ||
    (typeof value === 'number' && Number.isFinite(value))
  );
}

function compare(a: string, b: string): number {
  return a < b ? -1 : a > b ? 1 : 0;
}

/** Canonical JSON used for hashes and persisted manifests. */
export function canonicalJson(value: unknown, depth = 0): string {
  if (depth > 128) throw new Error('Canonical JSON nesting exceeds 128.');
  if (value === null || typeof value === 'boolean' || typeof value === 'string')
    return JSON.stringify(value);
  if (typeof value === 'number') {
    if (!Number.isFinite(value))
      throw new Error('Canonical JSON requires finite numbers.');
    return JSON.stringify(value);
  }
  if (Array.isArray(value))
    return `[${value.map((entry) => canonicalJson(entry, depth + 1)).join(',')}]`;
  if (typeof value !== 'object' || value === undefined)
    throw new Error('Canonical JSON supports JSON values only.');
  return `{${Object.entries(value)
    .sort(([a], [b]) => compare(a, b))
    .map(
      ([key, entry]) =>
        `${JSON.stringify(key)}:${canonicalJson(entry, depth + 1)}`,
    )
    .join(',')}}`;
}

/** SHA-256 is available in both Node 24 and the browser worker runtime. */
export async function sha256(value: unknown): Promise<string> {
  const bytes = new TextEncoder().encode(canonicalJson(value));
  const digest = await globalThis.crypto.subtle.digest('SHA-256', bytes);
  return Array.from(new Uint8Array(digest), (byte) =>
    byte.toString(16).padStart(2, '0'),
  ).join('');
}

function clone<T>(value: T): T {
  return structuredClone(value);
}

function nodeById(scenario: Scenario, id: string) {
  const node = scenario.nodes.find((entry) => entry.id === id);
  if (!node) invalid(`unknown node ${id}`);
  return node;
}

function setPath(
  scenario: Scenario,
  path: string,
  value: ParameterValue,
): void {
  const parts = path.split('.');
  if (parts.length === 1) {
    const key = parts[0] as keyof Scenario;
    if (!(key in scenario) || !isPrimitive(value))
      invalid(`unsupported parameter path ${path}`);
    (scenario as unknown as Record<string, ParameterValue>)[key] = value;
    return;
  }
  if (parts[0] === 'nodes' && parts.length === 3) {
    const node = nodeById(scenario, parts[1]!);
    const key = parts[2] as
      | 'position'
      | 'omega0'
      | 'omega'
      | 'phi'
      | 'amplitude'
      | 'gain'
      | 'relaxationTime';
    if (!(key in node) || !isPrimitive(value) || typeof value !== 'number')
      invalid(`unsupported node parameter path ${path}`);
    node[key] = value;
    return;
  }
  if (parts[0] === 'scenario') {
    setPath(scenario, parts.slice(1).join('.'), value);
    return;
  }
  invalid(`unsupported parameter path ${path}`);
}

function validateFiniteRange(value: number, name: string, minimum = 0): void {
  if (!Number.isFinite(value) || value < minimum)
    invalid(`${name} must be finite and >= ${minimum}`);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return !!value && typeof value === 'object' && !Array.isArray(value);
}

function validatePositiveInteger(value: unknown, name: string): void {
  if (!Number.isInteger(value) || (value as number) < 1)
    invalid(`${name} must be a positive integer`);
}

function validateEnvelopeOptions(value: unknown): void {
  if (value === undefined) return;
  if (!isRecord(value)) invalid('envelope options must be an object');
  const allowed = new Set([
    'preparation',
    'prehistory',
    'boundaryInputs',
    'tickSection',
    'maxSteps',
  ]);
  if (Object.keys(value).some((key) => !allowed.has(key)))
    invalid('envelope options contain an unknown key');
  if (
    value.preparation !== undefined &&
    value.preparation !== 'established' &&
    value.preparation !== 'empty-links'
  )
    invalid('envelope preparation is invalid');
  if (value.tickSection !== undefined && !Number.isFinite(value.tickSection))
    invalid('envelope tickSection must be finite');
  if (value.maxSteps !== undefined)
    validatePositiveInteger(value.maxSteps, 'envelope.maxSteps');
  if (value.prehistory !== undefined) {
    if (!Array.isArray(value.prehistory) || value.prehistory.length < 2)
      invalid('envelope prehistory needs at least two points');
    for (const point of value.prehistory) {
      if (
        !isRecord(point) ||
        !Number.isFinite(point.time) ||
        (point.time as number) > 0 ||
        !isRecord(point.nodes)
      )
        invalid('envelope prehistory point is invalid');
      for (const node of Object.values(point.nodes)) {
        if (
          !isRecord(node) ||
          !Number.isFinite(node.phi) ||
          !Number.isFinite(node.omega) ||
          (node.omega as number) <= 0
        )
          invalid('envelope prehistory node is invalid');
      }
    }
  }
  if (value.boundaryInputs !== undefined) {
    if (!isRecord(value.boundaryInputs))
      invalid('envelope boundaryInputs must be an object');
    if (
      Object.keys(value.boundaryInputs).some(
        (key) => key !== 'left' && key !== 'right',
      )
    )
      invalid('envelope boundaryInputs contain an unknown side');
    for (const side of ['left', 'right']) {
      const entries = value.boundaryInputs[side];
      if (entries === undefined) continue;
      if (!Array.isArray(entries) || entries.length === 0)
        invalid(`envelope boundaryInputs.${side} must be nonempty`);
      for (const entry of entries) {
        if (
          !isRecord(entry) ||
          !Number.isFinite(entry.time) ||
          !Number.isFinite(entry.rate) ||
          (entry.time as number) < 0 ||
          (entry.rate as number) < 0
        )
          invalid(`envelope boundaryInputs.${side} contains an invalid entry`);
      }
    }
  }
}

function validatePacketOptions(value: unknown): void {
  if (!isRecord(value)) invalid('packet options must be an object');
  const allowed = new Set([
    'detectorSeed',
    'interventionSeed',
    'maxSteps',
    'maxEvents',
    'maxPending',
  ]);
  if (Object.keys(value).some((key) => !allowed.has(key)))
    invalid('packet options contain an unknown key');
  for (const field of ['detectorSeed', 'interventionSeed']) {
    if (
      value[field] !== undefined &&
      (typeof value[field] !== 'string' || value[field].length > 4096)
    )
      invalid(`packets.${field} must be a string of at most 4096 characters`);
  }
  for (const field of allowed) {
    if (
      value[field] !== undefined &&
      field !== 'detectorSeed' &&
      field !== 'interventionSeed'
    )
      validatePositiveInteger(value[field], `packets.${field}`);
  }
}

export function validateDefinition(
  definition: unknown,
): asserts definition is ExperimentDefinition {
  if (!definition || typeof definition !== 'object')
    invalid('definition must be an object');
  const value = definition as Partial<ExperimentDefinition>;
  if (value.schemaVersion !== EXPERIMENT_SCHEMA_VERSION)
    invalid('unsupported schemaVersion');
  if (!value.id || typeof value.id !== 'string') invalid('id is required');
  if (!value.scenario) invalid('scenario is required');
  const scenarioValidation = validateScenario(value.scenario);
  if (!scenarioValidation.ok)
    invalid(
      `scenario violates the model contract at ${scenarioValidation.errors[0]?.path ?? '$'}`,
    );
  if (!value.mode || !['inspect', 'envelope', 'packets'].includes(value.mode))
    invalid('invalid mode');
  const until = value.until;
  validateFiniteRange(until ?? NaN, 'until');
  if (value.mode === 'packets' && value.packets === undefined)
    invalid('packets options are required in packet mode');
  if (value.mode !== 'packets' && value.packets !== undefined)
    invalid('packets options require packet mode');
  if (value.mode !== 'envelope' && value.envelope !== undefined)
    invalid('envelope options require envelope mode');
  validateEnvelopeOptions(value.envelope);
  if (value.packets !== undefined) validatePacketOptions(value.packets);
  if (
    !Number.isInteger(value.replicates) ||
    value.replicates! < 1 ||
    value.replicates! > 10000
  )
    invalid('replicates must be an integer from 1 to 10000');
  if (typeof value.seed !== 'string' || value.seed.length === 0)
    invalid('seed is required');
  const windows = value.windows;
  if (!windows) invalid('windows are required');
  validateFiniteRange(windows.transient, 'windows.transient');
  validateFiniteRange(windows.measurement.start, 'windows.measurement.start');
  validateFiniteRange(windows.measurement.end, 'windows.measurement.end');
  if (
    windows.transient > windows.measurement.start ||
    windows.measurement.start > windows.measurement.end ||
    windows.measurement.end > until!
  )
    invalid(
      'windows must satisfy transient <= measurement.start <= measurement.end <= until',
    );
  for (const window of windows.nested ?? []) {
    validateFiniteRange(window.start, 'nested window start');
    validateFiniteRange(window.end, 'nested window end');
    if (window.start > window.end || window.end > until!)
      invalid('nested windows must be ordered within until');
  }
  if (
    !value.tolerances ||
    !Number.isFinite(value.tolerances.absolute) ||
    !Number.isFinite(value.tolerances.relative) ||
    value.tolerances.absolute <= 0 ||
    value.tolerances.relative <= 0
  )
    invalid('finite positive tolerances are required');
  if (!Array.isArray(value.observables))
    invalid('observables must be an array');
  const budgets = value.budgets;
  if (
    !budgets ||
    !Number.isInteger(budgets.maxJobs) ||
    budgets.maxJobs < 1 ||
    budgets.maxJobs > 64
  )
    invalid('budgets.maxJobs must be an integer from 1 to 64');
  for (const [name, limit] of Object.entries(budgets))
    if (
      name !== 'maxJobs' &&
      (!Number.isInteger(limit) || (limit as number) < 1)
    )
      invalid(`${name} must be a positive integer`);
  if (budgets.maxRuns !== undefined && budgets.maxRuns > 1_000_000)
    invalid('budgets.maxRuns must not exceed 1000000');
  if (value.mode === 'packets') {
    for (const name of ['maxSteps', 'maxEvents', 'maxPending'] as const) {
      const limit = value.packets?.[name] ?? budgets[name];
      if (limit !== undefined && limit > 100_000)
        invalid(`packet ${name} must not exceed 100000`);
    }
  }
  if (value.mode === 'envelope') {
    const limit = value.envelope?.maxSteps ?? budgets.maxSteps;
    if (limit !== undefined && limit > 1_000_000)
      invalid('envelope maxSteps must not exceed 1000000');
  }
  const axes = value.parameters ?? [];
  const axisIds = new Set<string>();
  for (const axis of axes) {
    if (!axis.id || axisIds.has(axis.id) || !axis.path || !axis.values.length)
      invalid('parameter axes need unique ids, paths and values');
    axisIds.add(axis.id);
    if (axis.values.some((entry) => !isPrimitive(entry)))
      invalid(`parameter axis ${axis.id} contains a non-JSON value`);
    const uniqueValues = new Set(
      axis.values.map((entry) => canonicalJson(entry)),
    );
    if (uniqueValues.size !== axis.values.length)
      invalid(`parameter axis ${axis.id} contains duplicate values`);
  }
  const variants = value.variants ?? [];
  const variantIds = new Set<string>();
  for (const variant of variants) {
    if (!variant.id || variantIds.has(variant.id))
      invalid('variants need unique ids');
    variantIds.add(variant.id);
    for (const nodeId of Object.keys(variant.response ?? {}))
      nodeById(value.scenario, nodeId);
    for (const nodeId of Object.keys(variant.emission ?? {}))
      nodeById(value.scenario, nodeId);
  }
  const controls = value.controls ?? [];
  const controlIds = new Set<string>();
  for (const control of controls) {
    if (!control.id || controlIds.has(control.id))
      invalid('controls need unique ids');
    controlIds.add(control.id);
  }
}

interface Identity {
  experimentId: string;
  variantId: string;
  controlId: string;
  parameters: Record<string, ParameterValue>;
  replicate: number;
}

function combinations(
  axes: ParameterAxis[],
): Array<Record<string, ParameterValue>> {
  const ordered = [...axes].sort((a, b) => compare(a.id, b.id));
  return ordered.reduce<Array<Record<string, ParameterValue>>>(
    (rows, axis) =>
      rows.flatMap((row) =>
        axis.values.map((entry) => ({ ...row, [axis.id]: entry })),
      ),
    [{}],
  );
}

function applyVariant(scenario: Scenario, variant: ScenarioVariant): void {
  for (const [nodeId, response] of Object.entries(variant.response ?? {}))
    nodeById(scenario, nodeId).response = response;
  for (const [nodeId, emission] of Object.entries(variant.emission ?? {}))
    nodeById(scenario, nodeId).emission = clone(emission);
}

function applyControl(scenario: Scenario, control: ExperimentControl): void {
  for (const [path, value] of Object.entries(control.parameters ?? {}))
    setPath(scenario, path, value);
}

function boundedExecution(
  definition: ExperimentDefinition,
): ExperimentManifest['execution'] {
  const execution: ExperimentManifest['execution'] = {
    mode: definition.mode,
    until: definition.until,
  };
  const maxSteps = definition.budgets.maxSteps;
  if (
    definition.mode === 'envelope' &&
    (definition.envelope !== undefined || maxSteps !== undefined)
  ) {
    execution.envelope = {
      ...(definition.envelope ? clone(definition.envelope) : {}),
      ...(maxSteps === undefined
        ? {}
        : {
            maxSteps: Math.min(
              definition.envelope?.maxSteps ?? maxSteps,
              maxSteps,
            ),
          }),
    };
  }
  if (definition.packets) {
    const packets = clone(definition.packets);
    for (const field of ['maxSteps', 'maxEvents', 'maxPending'] as const) {
      const budget = definition.budgets[field];
      const requested = packets[field];
      if (budget !== undefined)
        packets[field] = Math.min(requested ?? budget, budget);
    }
    execution.packets = packets;
  }
  return execution;
}

function stripIdentity(definition: ExperimentDefinition): unknown {
  const copy = clone(definition) as unknown as Record<string, unknown>;
  delete copy.description;
  return copy;
}

export async function resolveDefinition(
  definition: ExperimentDefinition,
  options: ManifestOptions = {},
): Promise<ExperimentPlan> {
  validateDefinition(definition);
  const definitionHash = await sha256(stripIdentity(definition));
  const variants = definition.variants?.length
    ? definition.variants
    : [{ id: 'baseline' }];
  const controls = definition.controls?.length
    ? definition.controls
    : [{ id: 'baseline', kind: 'analytic' as const }];
  const maxRuns = definition.budgets.maxRuns ?? 100_000;
  let runCount = variants.length * controls.length * definition.replicates;
  for (const axis of definition.parameters ?? []) {
    if (axis.values.length > maxRuns || runCount > maxRuns / axis.values.length)
      invalid('resolved Cartesian run plan exceeds budgets.maxRuns');
    runCount *= axis.values.length;
  }
  if (runCount > maxRuns)
    invalid('resolved Cartesian run plan exceeds budgets.maxRuns');
  const provenance: ManifestProvenance = {
    modelVersion: definition.scenario.modelVersion,
    codeRevision: options.codeRevision ?? 'unknown',
    dirty: options.dirty ?? false,
    createdAt: options.createdAt ?? new Date().toISOString(),
    source: options.source ?? 'user-supplied experiment definition',
  };
  const manifests: ExperimentManifest[] = [];
  for (const variant of variants) {
    for (const control of controls) {
      for (const parameters of combinations(definition.parameters ?? [])) {
        for (
          let replicate = 0;
          replicate < definition.replicates;
          replicate++
        ) {
          const identity: Identity = {
            experimentId: definition.id,
            variantId: variant.id,
            controlId: control.id,
            parameters,
            replicate,
          };
          const runHash = await sha256(identity);
          const scenario = clone(definition.scenario);
          for (const axis of definition.parameters ?? [])
            setPath(scenario, axis.path, parameters[axis.id]!);
          applyVariant(scenario, variant);
          applyControl(scenario, control);
          if (definition.interventions)
            scenario.interventions = clone(definition.interventions);
          const resolvedValidation = validateScenario(scenario);
          if (!resolvedValidation.ok)
            invalid(
              `resolved scenario violates the model contract at ${resolvedValidation.errors[0]?.path ?? '$'}`,
            );
          const scenarioHash = await sha256(scenario);
          const base: ExperimentManifest = {
            kind: MANIFEST_KIND,
            schemaVersion: 1,
            experimentId: definition.id,
            runId: `${definition.id}:${runHash.slice(0, 24)}`,
            definitionHash,
            scenarioHash,
            replicate,
            variantId: variant.id,
            controlId: control.id,
            parameters: clone(parameters),
            scenario,
            execution: boundedExecution(definition),
            windows: clone(definition.windows),
            tolerances: clone(definition.tolerances),
            observables: [...definition.observables],
            budgets: clone(definition.budgets),
            provenance,
          };
          if (definition.mode === 'packets')
            base.seed = await sha256([
              'physical-run-v1',
              definition.seed,
              runHash,
            ]);
          manifests.push(base);
        }
      }
    }
  }
  return { definition: clone(definition), definitionHash, manifests };
}

export function isExperimentManifest(
  value: unknown,
): value is ExperimentManifest {
  return (
    !!value &&
    typeof value === 'object' &&
    (value as Partial<ExperimentManifest>).kind === MANIFEST_KIND
  );
}

export function isSweepCheckpoint(value: unknown): value is SweepCheckpoint {
  return (
    !!value &&
    typeof value === 'object' &&
    (value as Partial<SweepCheckpoint>).kind === CHECKPOINT_KIND
  );
}

export async function validateManifest(value: unknown): Promise<void> {
  if (!isExperimentManifest(value))
    throw new Error('Invalid Signal Space run manifest.');
  if (
    value.schemaVersion !== 1 ||
    !value.runId ||
    !value.definitionHash ||
    !value.scenarioHash
  )
    throw new Error('Run manifest is missing its identity fields.');
  const validation = validateScenario(value.scenario);
  if (!validation.ok)
    throw new Error('Run manifest contains an invalid scenario.');
  const actualScenarioHash = await sha256(value.scenario);
  if (actualScenarioHash !== value.scenarioHash)
    throw new Error('Run manifest scenarioHash does not match its scenario.');
  if (!Number.isFinite(value.execution.until) || value.execution.until < 0)
    throw new Error('Run manifest contains an invalid until time.');
  if (
    value.execution.mode === 'packets' &&
    (!value.seed || !value.execution.packets)
  )
    throw new Error(
      'Packet manifests require a derived seed and packet options.',
    );
  if (value.execution.mode !== 'packets' && value.seed !== undefined)
    throw new Error('Only packet manifests may contain a physical seed.');
}

export async function validateSweepCheckpoint(value: unknown): Promise<void> {
  if (!isSweepCheckpoint(value) || value.schemaVersion !== 1 || !value.sweepId)
    throw new Error('Invalid Signal Space sweep checkpoint.');
  if (!Array.isArray(value.completed))
    throw new Error('Sweep checkpoint is missing completed results.');
  const attempts = value.attempts ?? value.completed;
  if (!Array.isArray(attempts))
    throw new Error('Sweep checkpoint is missing attempt history.');
  const completedIds = new Set<string>();
  for (const result of value.completed) {
    if (completedIds.has(result.runId) || result.status !== 'completed')
      throw new Error('Sweep checkpoint completed results are inconsistent.');
    await validateManifest(result.manifest);
    if (
      result.runId !== result.manifest.runId ||
      statusFor(result.events) !== result.status
    )
      throw new Error('Sweep checkpoint completed result is inconsistent.');
    completedIds.add(result.runId);
  }
  for (const result of attempts) {
    await validateManifest(result.manifest);
    if (result.runId !== result.manifest.runId)
      throw new Error('Sweep checkpoint result and manifest IDs differ.');
    if (statusFor(result.events) !== result.status)
      throw new Error(
        'Sweep checkpoint result status does not match its terminal event.',
      );
  }
}

function requestFor(
  manifest: ExperimentManifest,
  resume?: RunEvent,
): Parameters<typeof execute>[0] {
  const request: Parameters<typeof execute>[0] = {
    runId: manifest.runId,
    mode: manifest.execution.mode,
    scenario: manifest.scenario,
    until: manifest.execution.until,
  };
  if (manifest.execution.envelope)
    request.envelope = clone(manifest.execution.envelope);
  if (manifest.execution.packets)
    request.packets = {
      ...clone(manifest.execution.packets),
      seed: manifest.seed ?? '',
    };
  if (resume?.type === 'envelope-snapshot')
    request.resume = clone(resume.snapshot);
  if (resume?.type === 'packet-snapshot')
    request.packetResume = clone(resume.snapshot);
  return request;
}

function statusFor(events: RunEvent[]): RunResult['status'] {
  const terminal = events.at(-1);
  if (terminal?.type === 'completed') return 'completed';
  if (terminal?.type === 'incomplete') return 'incomplete';
  if (terminal?.type === 'cancelled') return 'cancelled';
  return 'failed';
}

export async function runManifest(
  manifest: ExperimentManifest,
  signal?: AbortSignal,
  resume?: RunEvent,
): Promise<RunResult> {
  await validateManifest(manifest);
  const events: RunEvent[] = [];
  const options = signal ? { signal } : {};
  for await (const event of execute(requestFor(manifest, resume), options))
    events.push(event);
  return {
    runId: manifest.runId,
    manifest: clone(manifest),
    events,
    status: statusFor(events),
  };
}

function latestSnapshot(result: RunResult): RunEvent | undefined {
  return [...result.events]
    .reverse()
    .find(
      (event) =>
        event.type === 'envelope-snapshot' || event.type === 'packet-snapshot',
    );
}

/** Continue a run from its complete solver snapshot; this is distinct from restarting it. */
export async function continueRun(
  result: RunResult,
  until: number,
  signal?: AbortSignal,
): Promise<RunResult> {
  if (result.status === 'failed')
    throw new Error('Cannot continue a failed run.');
  if (result.status === 'incomplete')
    throw new Error(
      'Cannot continue an incomplete run; create a new run with revised immutable budgets.',
    );
  if (!Number.isFinite(until) || until < result.manifest.execution.until)
    throw new Error('Continuation until must extend the previous run.');
  const snapshot = latestSnapshot(result);
  if (!snapshot)
    throw new Error('Run has no complete checkpoint for continuation.');
  const manifest = clone(result.manifest);
  manifest.execution.until = until;
  manifest.continuationOf = result.runId;
  return runManifest(manifest, signal, snapshot);
}

function checkpointFor(
  plan: ExperimentPlan,
  attempts: RunResult[],
  status: SweepCheckpoint['status'],
): SweepCheckpoint {
  return {
    kind: CHECKPOINT_KIND,
    schemaVersion: 1,
    sweepId: plan.definition.id,
    definitionHash: plan.definitionHash,
    planSize: plan.manifests.length,
    completed: attempts
      .filter((result) => result.status === 'completed')
      .map(clone),
    attempts: attempts.map(clone),
    createdAt: new Date().toISOString(),
    status,
  };
}

export async function runSweep(
  plan: ExperimentPlan,
  options: SweepOptions = {},
): Promise<SweepOutcome> {
  const concurrency = Math.min(
    options.concurrency ?? plan.definition.budgets.maxJobs,
    plan.definition.budgets.maxJobs,
  );
  if (!Number.isInteger(concurrency) || concurrency < 1)
    throw new Error('Sweep concurrency must be a positive integer.');
  const prior = options.checkpoint;
  if (prior) {
    await validateSweepCheckpoint(prior);
    if (
      prior.definitionHash !== plan.definitionHash ||
      prior.planSize !== plan.manifests.length
    )
      throw new Error('Checkpoint does not belong to this experiment plan.');
  }
  const priorAttempts = prior ? (prior.attempts ?? prior.completed) : [];
  const plannedIds = new Set(plan.manifests.map((manifest) => manifest.runId));
  for (const result of priorAttempts) {
    if (
      !plannedIds.has(result.runId) ||
      result.manifest.definitionHash !== plan.definitionHash
    )
      throw new Error('Checkpoint contains a result outside the current plan.');
  }
  // A cancelled, failed, or resource-incomplete attempt is retained in the
  // checkpoint for audit but is eligible for a fresh attempt on resume.
  const results = priorAttempts.map(clone);
  const completedIds = new Set(
    priorAttempts
      .filter((result) => result.status === 'completed')
      .map((result) => result.runId),
  );
  const pending = plan.manifests.filter(
    (manifest) => !completedIds.has(manifest.runId),
  );
  let cursor = 0;
  const worker = async (): Promise<void> => {
    while (cursor < pending.length) {
      if (options.signal?.aborted) return;
      const manifest = pending[cursor++];
      if (!manifest) return;
      const result = await runManifest(manifest, options.signal);
      results.push(result);
      options.onRun?.(clone(result));
      if (results.length % (plan.definition.budgets.checkpointEvery ?? 1) === 0)
        options.onCheckpoint?.(checkpointFor(plan, results, 'partial'));
    }
  };
  await Promise.all(Array.from({ length: concurrency }, () => worker()));
  const allCompleted = plan.manifests.every((manifest) =>
    results.some(
      (result) =>
        result.runId === manifest.runId && result.status === 'completed',
    ),
  );
  const status: SweepOutcome['status'] = options.signal?.aborted
    ? 'cancelled'
    : allCompleted
      ? 'completed'
      : 'partial';
  const checkpoint = checkpointFor(
    plan,
    results,
    status === 'completed' ? 'completed' : status,
  );
  options.onCheckpoint?.(clone(checkpoint));
  return {
    status,
    results: results.sort((a, b) => compare(a.runId, b.runId)),
    checkpoint,
  };
}

export async function resumeSweep(
  plan: ExperimentPlan,
  checkpoint: SweepCheckpoint,
  options: Omit<SweepOptions, 'checkpoint'> = {},
): Promise<SweepOutcome> {
  await validateSweepCheckpoint(checkpoint);
  return runSweep(plan, { ...options, checkpoint });
}
