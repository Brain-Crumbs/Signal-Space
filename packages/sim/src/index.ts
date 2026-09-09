import { Ajv2020 } from 'ajv/dist/2020.js';
import schema from '@signal-space/model/schema' with { type: 'json' };
import { validateScenario } from '@signal-space/model';
import type { Scenario, Snapshot, ValidationIssue } from '@signal-space/model';

export interface RunRequest {
  runId: string;
  mode: 'inspect';
  scenario: unknown;
}
export interface RunFailure {
  code: 'INVALID_REQUEST' | 'INVALID_SCENARIO' | 'INTERNAL' | 'BUSY';
  message: string;
  details?: ValidationIssue[];
}
export type RunEvent =
  | {
      type: 'progress';
      runId: string;
      fraction: number;
      stage: 'validating' | 'preparing';
    }
  | { type: 'snapshot'; runId: string; snapshot: Snapshot }
  | { type: 'completed'; runId: string; mode: 'inspect' }
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

/** Shared Node/browser execution boundary. T02 only inspects preparation at t=0.
 * It never advances time or claims to integrate the Paper I equations.
 * Exactly one terminal event is yielded; snapshots are detached copies.
 */
export async function* execute(
  request: RunRequest,
  options: RunOptions = {},
): AsyncGenerator<RunEvent> {
  const runId = typeof request?.runId === 'string' ? request.runId : '';
  const cancelled = (): RunEvent => ({ type: 'cancelled', runId });
  try {
    if (!runId || request.mode !== 'inspect') {
      yield {
        type: 'failed',
        runId,
        error: {
          code: 'INVALID_REQUEST',
          message:
            'Provide a runId and mode inspect. Numerical evolution is not implemented.',
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
    try {
      scenario = structuredClone(request.scenario);
      if (hasSharedMemory(scenario))
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
    if (!validateStructure(scenario)) {
      yield {
        type: 'failed',
        runId,
        error: {
          code: 'INVALID_SCENARIO',
          message: 'Scenario does not match paper-i-v1.',
          details: (validateStructure.errors ?? []).map((e) => ({
            path: e.instancePath || '$',
            message: e.message ?? 'Invalid field',
          })),
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
    yield { type: 'progress', runId, fraction: 0.5, stage: 'preparing' };
    await yieldTask();
    if (options.signal?.aborted) {
      yield cancelled();
      return;
    }
    const snapshot: Snapshot = {
      schemaVersion: 1,
      time: 0,
      nodeState: Object.fromEntries(
        scenario.nodes.map((n) => [n.id, { phi: n.phi, omega: n.omega }]),
      ),
      history: structuredClone(scenario.initialHistory),
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
        code: 'INTERNAL',
        message: error instanceof Error ? error.message : 'Execution failed.',
      },
    };
  }
}
