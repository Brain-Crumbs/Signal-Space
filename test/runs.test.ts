import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  createSample,
  createSmokeDefinition,
  smokeSetupIds,
} from '@signal-space/experiments';
import {
  canonicalJson,
  continueRun,
  resolveDefinition,
  runManifest,
  runSweep,
  resumeSweep,
  type ExperimentDefinition,
} from '@signal-space/experiments';

function definition(
  overrides: Partial<ExperimentDefinition> = {},
): ExperimentDefinition {
  return {
    schemaVersion: 'paper-i-experiment-v1',
    id: 'test-sweep',
    scenario: createSample('isolated'),
    mode: 'envelope',
    until: 0.04,
    windows: { transient: 0, measurement: { start: 0, end: 0.04 } },
    tolerances: { absolute: 1e-9, relative: 1e-7 },
    replicates: 2,
    seed: 'test-seed',
    observables: ['phase', 'frequency'],
    budgets: { maxJobs: 2, maxSteps: 1000, checkpointEvery: 1 },
    ...overrides,
  };
}

test('canonical definitions resolve stable identities and hierarchical seeds', async () => {
  const plan = await resolveDefinition(
    definition({
      mode: 'packets',
      packets: {},
      parameters: [{ id: 'gain', path: 'nodes.A.gain', values: [0, 0.1] }],
      replicates: 1,
    }),
    {
      createdAt: '2026-01-01T00:00:00.000Z',
      codeRevision: 'fixture',
      source: 'test',
    },
  );
  assert.equal(plan.manifests.length, 2);
  assert.notEqual(plan.manifests[0]!.runId, plan.manifests[1]!.runId);
  assert.notEqual(
    plan.manifests[0]!.scenarioHash,
    plan.manifests[1]!.scenarioHash,
  );
  assert.notEqual(plan.manifests[0]!.seed, plan.manifests[1]!.seed);
  const reordered = { b: 2, a: 1 };
  assert.equal(canonicalJson(reordered), '{"a":1,"b":2}');
  assert.equal(canonicalJson({ a: 1, b: 2 }), canonicalJson(reordered));
});

test('manifest budgets are enforced in the shared execution request', async () => {
  const plan = await resolveDefinition(
    definition({
      mode: 'packets',
      packets: { maxSteps: 100, maxEvents: 100, maxPending: 100 },
      budgets: { maxJobs: 1, maxSteps: 3, maxEvents: 4, maxPending: 5 },
    }),
    {
      createdAt: '2026-01-01T00:00:00.000Z',
      codeRevision: 'fixture',
      source: 'test',
    },
  );
  assert.deepEqual(plan.manifests[0]!.execution.packets, {
    maxSteps: 3,
    maxEvents: 4,
    maxPending: 5,
  });
});

test('all A-I smoke definitions resolve without launching research-scale work', async () => {
  for (const id of smokeSetupIds) {
    const plan = await resolveDefinition(createSmokeDefinition(id), {
      createdAt: '2026-01-01T00:00:00.000Z',
      codeRevision: 'fixture',
      source: `fixture:${id}`,
    });
    assert.equal(plan.manifests.length, 1);
    assert.equal(plan.manifests[0]!.provenance.source, `fixture:${id}`);
  }
});

test('sweep concurrency does not alter run identities or seeded results', async () => {
  const plan = await resolveDefinition(definition({ replicates: 3 }), {
    createdAt: '2026-01-01T00:00:00.000Z',
    codeRevision: 'fixture',
    source: 'test',
  });
  const serial = await runSweep(plan, { concurrency: 1 });
  const parallel = await runSweep(plan, { concurrency: 2 });
  assert.equal(serial.status, 'completed');
  assert.equal(parallel.status, 'completed');
  assert.deepEqual(
    serial.results.map((result) => [
      result.runId,
      result.status,
      result.events,
    ]),
    parallel.results.map((result) => [
      result.runId,
      result.status,
      result.events,
    ]),
  );
});

test('partial sweep checkpoints resume only unfinished runs', async () => {
  const plan = await resolveDefinition(
    definition({ replicates: 4, budgets: { maxJobs: 1, checkpointEvery: 1 } }),
    {
      createdAt: '2026-01-01T00:00:00.000Z',
      codeRevision: 'fixture',
      source: 'test',
    },
  );
  const controller = new AbortController();
  const partial = await runSweep(plan, {
    signal: controller.signal,
    onRun: (result) => {
      if (result.status === 'completed') controller.abort();
    },
  });
  assert.equal(partial.status, 'cancelled');
  assert.ok(
    partial.results.length >= 1 &&
      partial.results.length < plan.manifests.length,
  );
  const resumed = await resumeSweep(plan, partial.checkpoint, {
    concurrency: 2,
  });
  assert.equal(resumed.status, 'completed');
  assert.equal(resumed.results.length, plan.manifests.length);
  assert.equal(
    new Set(resumed.results.map((result) => result.runId)).size,
    plan.manifests.length,
  );
});

test('resume retries cancelled attempts instead of silently dropping them', async () => {
  const plan = await resolveDefinition(
    definition({ replicates: 2, budgets: { maxJobs: 1, checkpointEvery: 1 } }),
    {
      createdAt: '2026-01-01T00:00:00.000Z',
      codeRevision: 'fixture',
      source: 'test',
    },
  );
  const controller = new AbortController();
  const partial = await runSweep(plan, {
    signal: controller.signal,
    onRun: () => controller.abort(),
  });
  assert.equal(partial.status, 'cancelled');
  const resumed = await resumeSweep(plan, partial.checkpoint, {
    concurrency: 1,
  });
  assert.equal(resumed.status, 'completed');
  assert.equal(resumed.results.length, plan.manifests.length);
});

test('continuation uses the complete solver checkpoint rather than restarting', async () => {
  const shortPlan = await resolveDefinition(
    definition({
      until: 0.02,
      windows: { transient: 0, measurement: { start: 0, end: 0.02 } },
      replicates: 1,
    }),
    {
      createdAt: '2026-01-01T00:00:00.000Z',
      codeRevision: 'fixture',
      source: 'test',
    },
  );
  const short = await runManifest(shortPlan.manifests[0]!);
  const continued = await continueRun(short, 0.04);
  assert.equal(continued.status, 'completed');
  assert.equal(continued.manifest.continuationOf, short.runId);
  assert.equal(continued.events.at(-1)?.type, 'completed');
});
