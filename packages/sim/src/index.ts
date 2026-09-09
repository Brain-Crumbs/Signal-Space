import { PacketSolver } from './packets.js';
import type { PacketOptions, PacketSample, PacketSnapshot } from './packets.js';
export { PacketSolver } from './packets.js';
export type {
  PacketOptions,
  PacketSample,
  PacketSnapshot,
  PacketRecord,
} from './packets.js';
import { EnvelopeSolver, EnvelopeFailure } from './envelope.js';
import type {
  EnvelopeOptions,
  EnvelopeSnapshot,
  EnvelopeSample,
  TickCrossing,
} from './envelope.js';
export type {
  AdaptiveAttempt,
  EnvelopeOptions,
  EnvelopeSnapshot,
  EnvelopeSample,
  TickCrossing,
  HistoryPoint,
} from './envelope.js';
export { emission, envelopeRoutes } from './envelope.js';
import { Ajv2020 } from 'ajv/dist/2020.js';
import schema from '@signal-space/model/schema' with { type: 'json' };
import { validateScenario } from '@signal-space/model';
import type { Scenario, Snapshot, ValidationIssue } from '@signal-space/model';

export interface RunRequest {
  runId: string;
  mode: 'inspect' | 'envelope' | 'packets';
  scenario: unknown;
  until?: number;
  envelope?: EnvelopeOptions;
  resume?: EnvelopeSnapshot;
  packets?: PacketOptions;
  packetResume?: PacketSnapshot;
}
export interface RunFailure {
  code:
    | 'INVALID_REQUEST'
    | 'INVALID_SCENARIO'
    | 'INTERNAL'
    | 'BUSY'
    | 'INVALID_HISTORY'
    | 'UNSUPPORTED_MODEL'
    | 'NUMERICAL_FAILURE';
  message: string;
  details?: ValidationIssue[];
}
export type RunEvent =
  | {
      type: 'progress';
      runId: string;
      fraction: number;
      stage: 'validating' | 'preparing' | 'integrating';
    }
  | { type: 'snapshot'; runId: string; snapshot: Snapshot }
  | {
      type: 'completed';
      runId: string;
      mode: 'inspect' | 'envelope' | 'packets';
    }
  | {
      type: 'envelope-sample';
      runId: string;
      sample: EnvelopeSample;
      ticks: TickCrossing[];
    }
  | { type: 'envelope-snapshot'; runId: string; snapshot: EnvelopeSnapshot }
  | { type: 'packet-sample'; runId: string; sample: PacketSample }
  | { type: 'packet-snapshot'; runId: string; snapshot: PacketSnapshot }
  | { type: 'incomplete'; runId: string; reason: string }
  | { type: 'cancelled'; runId: string }
  | { type: 'failed'; runId: string; error: RunFailure };
export type WorkerCommand =
  { type: 'run'; request: RunRequest } | { type: 'cancel'; runId: string };
export interface RunOptions {
  signal?: AbortSignal;
}
const validateStructure = new Ajv2020({ allErrors: true }).compile<Scenario>(
  schema,
);
const yieldTask = () => new Promise<void>((resolve) => setTimeout(resolve, 0));

/** Return the JSON Schema issues without running the numerical engine. */
export function validateScenarioStructure(value: unknown): ValidationIssue[] {
  if (validateStructure(value)) return [];
  return (validateStructure.errors ?? []).map((error) => ({
    path: error.instancePath || '$',
    message: error.message ?? 'Invalid field',
  }));
}

/** Inspect the clone, whose accessors/custom prototypes have already been removed. */
function hasSharedMemory(value: unknown, seen = new Set<object>()): boolean {
  if (value === null || typeof value !== 'object') return false;
  if (
    typeof SharedArrayBuffer !== 'undefined' &&
    value instanceof SharedArrayBuffer
  )
    return true;
  if (seen.has(value)) return false;
  seen.add(value);
  if (ArrayBuffer.isView(value)) return hasSharedMemory(value.buffer, seen);
  if (typeof WebAssembly !== 'undefined' && value instanceof WebAssembly.Memory)
    return hasSharedMemory(value.buffer, seen);
  if (value instanceof Map)
    for (const [key, entry] of value)
      if (hasSharedMemory(key, seen) || hasSharedMemory(entry, seen))
        return true;
  if (value instanceof Set)
    for (const entry of value) if (hasSharedMemory(entry, seen)) return true;
  return Object.getOwnPropertyNames(value).some((key) =>
    hasSharedMemory(Reflect.get(value, key), seen),
  );
}

/** Shared Node/browser execution boundary. Inspect returns preparation only;
 * envelope integrates the deterministic Paper I equations.
 * Exactly one terminal event is yielded; snapshots are detached copies.
 */
export async function* execute(
  request: RunRequest,
  options: RunOptions = {},
): AsyncGenerator<RunEvent> {
  const runId = typeof request?.runId === 'string' ? request.runId : '';
  const cancelled = (): RunEvent => ({ type: 'cancelled', runId });
  try {
    if (!runId || !['inspect', 'envelope', 'packets'].includes(request.mode)) {
      yield {
        type: 'failed',
        runId,
        error: {
          code: 'INVALID_REQUEST',
          message: 'Provide a runId and mode inspect, envelope or packets.',
        },
      };
      return;
    }
    if (options.signal?.aborted) {
      yield cancelled();
      return;
    }
    // Own the input before the first yield so callers cannot mutate an active run.
    let scenario: unknown;
    let owned: RunRequest;
    try {
      owned = structuredClone(request);
      scenario = owned.scenario;
      if (hasSharedMemory(owned))
        throw new Error('Shared memory is not owned input.');
    } catch {
      yield {
        type: 'failed',
        runId,
        error: {
          code: 'INVALID_SCENARIO',
          message:
            'Scenario must be structured-cloneable without shared memory.',
          details: [
            {
              path: '$',
              message: 'Input cannot be cloned into detached state.',
            },
          ],
        },
      };
      return;
    }
    yield { type: 'progress', runId, fraction: 0, stage: 'validating' };
    await yieldTask();
    if (options.signal?.aborted) {
      yield cancelled();
      return;
    }
    const structureErrors = validateScenarioStructure(scenario);
    if (structureErrors.length > 0) {
      yield {
        type: 'failed',
        runId,
        error: {
          code: 'INVALID_SCENARIO',
          message: 'Scenario does not match paper-i-v1.',
          details: structureErrors,
        },
      };
      return;
    }
    const validation = validateScenario(scenario);
    if (!validation.ok) {
      yield {
        type: 'failed',
        runId,
        error: {
          code: 'INVALID_SCENARIO',
          message: 'Scenario violates the model contract.',
          details: validation.errors,
        },
      };
      return;
    }
    const validatedScenario = scenario as Scenario;
    yield { type: 'progress', runId, fraction: 0.5, stage: 'preparing' };
    await yieldTask();
    if (options.signal?.aborted) {
      yield cancelled();
      return;
    }
    if (owned.mode === 'packets') {
      if (owned.resume !== undefined || owned.envelope !== undefined)
        throw new EnvelopeFailure(
          'INVALID_REQUEST',
          'Envelope state/options cannot be used in packet mode.',
        );
      const until = owned.until;
      if (
        typeof until !== 'number' ||
        !Number.isFinite(until) ||
        until < 0 ||
        !owned.packets
      )
        throw new EnvelopeFailure(
          'INVALID_REQUEST',
          'Provide packet options with a seed and a finite nonnegative until time.',
        );
      const solver = new PacketSolver(
        validatedScenario,
        owned.packets,
        owned.packetResume,
      );
      if (until < solver.time)
        throw new EnvelopeFailure(
          'INVALID_REQUEST',
          'until precedes checkpoint time.',
        );
      yield { type: 'packet-sample', runId, sample: solver.sample() };
      let attempts = 0;
      while (solver.time < until && !solver.incomplete) {
        if (options.signal?.aborted) {
          yield { type: 'packet-snapshot', runId, snapshot: solver.snapshot() };
          yield cancelled();
          return;
        }
        const previous = solver.time;
        solver.advance(until);
        if (solver.time > previous)
          yield { type: 'packet-sample', runId, sample: solver.sample() };
        if (++attempts % 32 === 0) await yieldTask();
      }
      yield { type: 'packet-snapshot', runId, snapshot: solver.snapshot() };
      if (solver.incomplete)
        yield { type: 'incomplete', runId, reason: solver.incomplete };
      else if (options.signal?.aborted) yield cancelled();
      else yield { type: 'completed', runId, mode: 'packets' };
      return;
    }
    if (owned.packets !== undefined || owned.packetResume !== undefined)
      throw new EnvelopeFailure(
        'INVALID_REQUEST',
        'Packet options/checkpoints require packet mode.',
      );
    if (owned.mode === 'envelope') {
      const until = owned.until;
      if (typeof until !== 'number' || !Number.isFinite(until) || until < 0)
        throw new EnvelopeFailure(
          'INVALID_REQUEST',
          'Provide a finite nonnegative until time.',
        );
      const solver = new EnvelopeSolver(
        validatedScenario,
        owned.envelope,
        owned.resume,
      );
      if (until < solver.time)
        throw new EnvelopeFailure(
          'INVALID_REQUEST',
          'until must not precede the checkpoint.',
        );
      const start = solver.time;
      yield {
        type: 'envelope-sample',
        runId,
        sample: solver.sample(),
        ticks: [],
      };
      let attempts = 0;
      while (solver.time < until) {
        if (options.signal?.aborted) {
          yield {
            type: 'envelope-snapshot',
            runId,
            snapshot: solver.snapshot(),
          };
          yield cancelled();
          return;
        }
        const previous = solver.time;
        const ticks = solver.advance(until);
        if (solver.time > previous)
          yield {
            type: 'envelope-sample',
            runId,
            sample: solver.sample(),
            ticks,
          };
        if (++attempts % 32 === 0) {
          yield {
            type: 'progress',
            runId,
            fraction: (solver.time - start) / (until - start),
            stage: 'integrating',
          };
          await yieldTask();
        }
      }
      yield { type: 'envelope-snapshot', runId, snapshot: solver.snapshot() };
      await yieldTask();
      if (options.signal?.aborted) {
        yield cancelled();
        return;
      }
      yield { type: 'progress', runId, fraction: 1, stage: 'integrating' };
      if (options.signal?.aborted) {
        yield cancelled();
        return;
      }
      yield { type: 'completed', runId, mode: 'envelope' };
      return;
    }
    const snapshot: Snapshot = {
      schemaVersion: 1,
      time: 0,
      nodeState: Object.fromEntries(
        validatedScenario.nodes.map((n) => [
          n.id,
          { phi: n.phi, omega: n.omega },
        ]),
      ),
      history: structuredClone(validatedScenario.initialHistory),
    };
    yield { type: 'snapshot', runId, snapshot };
    await yieldTask();
    if (options.signal?.aborted) {
      yield cancelled();
      return;
    }
    yield { type: 'progress', runId, fraction: 1, stage: 'preparing' };
    if (options.signal?.aborted) {
      yield cancelled();
      return;
    }
    yield { type: 'completed', runId, mode: 'inspect' };
  } catch (error) {
    yield {
      type: 'failed',
      runId,
      error: {
        code: error instanceof EnvelopeFailure ? error.code : 'INTERNAL',
        message: error instanceof Error ? error.message : 'Execution failed.',
      },
    };
  }
}

export { branchPacketRun } from './interventions.js';
export type { InterventionLineage } from './interventions.js';
export {
  recordObserver,
  isObserverDataset,
  observerDatasetSchema,
} from './observation.js';
export type {
  DetectorProtocol,
  LocalArrival,
  ObserverDataset,
} from './observation.js';
