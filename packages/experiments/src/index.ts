import type { Scenario } from '@signal-space/model';
import isolated from '../../../fixtures/scenarios/isolated.json' with { type: 'json' };
import pair from '../../../fixtures/scenarios/pair.json' with { type: 'json' };
export type SampleId = 'isolated' | 'pair';
export const sampleIds: readonly SampleId[] = ['isolated', 'pair'];
/** Contract smoke fixtures, not executed scientific protocols. Return independent state. */
export function createSample(id: SampleId): Scenario {
  return structuredClone(id === 'isolated' ? isolated : pair) as Scenario;
}
