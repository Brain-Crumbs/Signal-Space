import type { Scenario } from '@signal-space/model';
import isolated from '../../../fixtures/scenarios/isolated.json' with { type: 'json' };
import pair from '../../../fixtures/scenarios/pair.json' with { type: 'json' };
export * from './runs.js';
export * from './setup-a.js';
export * from './setup-b.js';
export * from './setup-c.js';
export * from './setup-d.js';
export type SampleId = 'isolated' | 'pair';
export const sampleIds: readonly SampleId[] = ['isolated', 'pair'];
/** Contract smoke fixtures, not executed scientific protocols. Return independent state. */
export function createSample(id: SampleId): Scenario {
  return structuredClone(id === 'isolated' ? isolated : pair) as Scenario;
}

export type SmokeSetupId =
  | 'setup-a'
  | 'setup-b'
  | 'setup-c'
  | 'setup-d'
  | 'setup-e'
  | 'setup-f'
  | 'setup-g'
  | 'setup-h'
  | 'setup-i';
export const smokeSetupIds: readonly SmokeSetupId[] = [
  'setup-a',
  'setup-b',
  'setup-c',
  'setup-d',
  'setup-e',
  'setup-f',
  'setup-g',
  'setup-h',
  'setup-i',
];

/** Small protocol-shaped definitions for wiring checks; they are not paper results. */
export function createSmokeDefinition(id: SmokeSetupId) {
  const scenario = createSample(id === 'setup-a' ? 'isolated' : 'pair');
  return {
    schemaVersion: 'paper-i-experiment-v1' as const,
    id: `${id}-smoke`,
    description: `${id} inexpensive wiring fixture; not a research manifest.`,
    scenario,
    mode: id === 'setup-a' ? ('envelope' as const) : ('packets' as const),
    until: 0.1,
    ...(id === 'setup-a'
      ? {}
      : { packets: { maxSteps: 1000, maxEvents: 1000, maxPending: 1000 } }),
    windows: { transient: 0, measurement: { start: 0, end: 0.1 } },
    tolerances: { absolute: 1e-9, relative: 1e-7 },
    replicates: 1,
    seed: `signal-space-${id}-smoke-v1`,
    observables: ['phase' as const, 'frequency' as const],
    budgets: { maxJobs: 1, maxSteps: 1000, maxEvents: 1000, maxPending: 1000 },
  };
}
