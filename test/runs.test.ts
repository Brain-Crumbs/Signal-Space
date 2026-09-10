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
  validateDefinition,
  validateManifest,
  validateSweepCheckpoint,
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
      parameters: [{ id: 'c0', path: 'c0', values: [1, 1.1] }],
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

test('envelope budgets apply when solver options are omitted', async () => {
  const plan = await resolveDefinition(
    definition({ budgets: { maxJobs: 1, maxSteps: 7 } }),
    {
      createdAt: '2026-01-01T00:00:00.000Z',
      codeRevision: 'fixture',
      source: 'test',
    },
  );
  assert.equal(plan.manifests[0]!.execution.envelope?.maxSteps, 7);
});

test('resolved manifests reject scenario hash tampering', async () => {
  const plan = await resolveDefinition(definition(), {
    createdAt: '2026-01-01T00:00:00.000Z',
    codeRevision: 'fixture',
    source: 'test',
  });
  const tampered = structuredClone(plan.manifests[0]!);
  tampered.scenario.c0 += 0.1;
  await assert.rejects(runManifest(tampered), /scenarioHash does not match/);
});

test('packet manifests reject root-seed tampering', async () => {
  const plan = await resolveDefinition(
    definition({ mode: 'packets', packets: {}, replicates: 1 }),
  );
  const tampered = structuredClone(plan.manifests[0]!);
  tampered.rootSeed = 'different-root-seed';
  await assert.rejects(validateManifest(tampered), /seed does not match/);
});

test('definition validation rejects invalid resolved values and unbounded plans', async () => {
  await assert.rejects(
    resolveDefinition(
      definition({
        parameters: [{ id: 'omega', path: 'nodes.A.omega', values: [-1] }],
      }),
    ),
    /resolved scenario violates/,
  );
  await assert.rejects(
    resolveDefinition(
      definition({
        parameters: [{ id: 'gain', path: 'nodes.A.gain', values: [0, 0] }],
      }),
    ),
    /duplicate values/,
  );
  await assert.rejects(
    resolveDefinition(
      definition({
        replicates: 2,
        budgets: { maxJobs: 1, maxRuns: 1 },
      }),
    ),
    /exceeds budgets.maxRuns/,
  );
  await assert.rejects(
    resolveDefinition(
      definition({
        mode: 'packets',
        packets: { maxSteps: 0 },
      }),
    ),
    /packets.maxSteps/,
  );
  await assert.rejects(
    resolveDefinition(
      definition({
        tolerances: { absolute: Infinity, relative: 1e-7 },
      }),
    ),
    /finite positive tolerances/,
  );
  assert.throws(
    () =>
      validateDefinition(
        definition({
          budgets: { maxJobs: 1, maxEvent: 1 } as never,
        }),
      ),
    /unknown key/,
  );
  assert.throws(
    () =>
      validateDefinition(
        definition({
          envelope: {
            perturbations: [
              {
                time: 0.02,
                nodeId: 'A',
                phaseOffset: 0,
                frequencyOffset: 0,
                phaseOffest: 0,
              },
            ],
          } as never,
        }),
      ),
    /envelope perturbation is invalid/,
  );
  assert.throws(
    () =>
      validateDefinition(
        definition({
          parameters: [
            { id: 'first', path: 'c0', values: [1.1] },
            { id: 'second', path: 'c0', values: [1.2] },
          ],
        }),
      ),
    /same path/,
  );
  assert.throws(
    () =>
      validateDefinition(
        definition({
          windows: {
            transient: 0.02,
            measurement: { start: 0.02, end: 0.04 },
            nested: [{ start: 0.01, end: 0.03 }],
          },
        }),
      ),
    /post-transient/,
  );
  await assert.rejects(
    resolveDefinition(
      definition({
        variants: [{ id: 'bad-response', response: { A: 'invalid' as never } }],
      }),
    ),
    /resolved scenario violates the model schema/,
  );
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
  assert.ok(partial.checkpoint.attempts.length >= partial.results.length);
  assert.deepEqual(
    partial.checkpoint.completed.map((result) => result.runId),
    partial.checkpoint.attempts
      .filter((result) => result.status === 'completed')
      .map((result) => result.runId),
  );
  const resumed = await resumeSweep(plan, partial.checkpoint, {
    concurrency: 1,
  });
  assert.equal(resumed.status, 'completed');
  assert.equal(resumed.results.length, plan.manifests.length);
});

test('resource-incomplete attempts remain auditable and cannot continue', async () => {
  const plan = await resolveDefinition(
    definition({
      mode: 'packets',
      packets: {},
      replicates: 1,
      budgets: { maxJobs: 1, maxSteps: 1, checkpointEvery: 1 },
    }),
    {
      createdAt: '2026-01-01T00:00:00.000Z',
      codeRevision: 'fixture',
      source: 'test',
    },
  );
  const outcome = await runSweep(plan);
  assert.equal(outcome.status, 'partial');
  assert.equal(outcome.checkpoint.completed.length, 0);
  assert.equal(outcome.checkpoint.attempts[0]!.status, 'incomplete');
  await assert.rejects(
    continueRun(outcome.checkpoint.attempts[0]!, 0.08),
    /Cannot continue an incomplete run/,
  );
});

test('checkpoint validation checks plan result identity and terminal status', async () => {
  const plan = await resolveDefinition(definition({ replicates: 1 }), {
    createdAt: '2026-01-01T00:00:00.000Z',
    codeRevision: 'fixture',
    source: 'test',
  });
  const outcome = await runSweep(plan);
  const badStatus = structuredClone(outcome.checkpoint);
  badStatus.attempts[0]!.status = 'failed';
  await assert.rejects(validateSweepCheckpoint(badStatus), /terminal event/);
  const badId = structuredClone(outcome.checkpoint);
  badId.attempts[0]!.runId = 'foreign-run';
  await assert.rejects(validateSweepCheckpoint(badId), /IDs differ/);
  await assert.rejects(
    resumeSweep(plan, {
      ...outcome.checkpoint,
      attempts: outcome.checkpoint.attempts.map((result) => ({
        ...result,
        manifest: { ...result.manifest, definitionHash: 'foreign' },
      })),
    }),
    /scenarioHash|definitionHash|IDs differ|outside the current plan/,
  );
  const relabeled = structuredClone(outcome.checkpoint);
  relabeled.attempts[0]!.runId = 'test-sweep:foreign';
  relabeled.attempts[0]!.manifest.runId = 'test-sweep:foreign';
  await assert.rejects(resumeSweep(plan, relabeled), /runId does not match/);
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
