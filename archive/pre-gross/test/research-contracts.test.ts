import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import type {
  ArtifactRecord,
  ResearchConfig,
  ResearchEvent,
} from '@signal-space/research-contracts';

test('generated research boundary types match the versioned fixture', async () => {
  const config = JSON.parse(
    await readFile('fixtures/research/synthetic.json', 'utf8'),
  ) as ResearchConfig;
  assert.equal(config.schema_version, 'research-experiment-v1');
  const event: ResearchEvent = {
    schema_version: 'research-event-v1',
    sequence: 1,
    timestamp: '2026-09-18T00:00:00Z',
    type: 'fixture',
    stage: 'runtime',
    payload: {},
  };
  const artifact: ArtifactRecord = {
    id: 'artifact-fixture',
    kind: 'raw',
    path: 'attempts/attempt-0001/raw/series.csv',
    sha256: '0'.repeat(64),
    size: 0,
    media_type: 'text/csv',
  };
  assert.equal(event.sequence, 1);
  assert.equal(artifact.kind, 'raw');
});
