import assert from 'node:assert/strict';
import { test } from 'node:test';
import { execute } from '@signal-space/sim';
import type { RunEvent, RunRequest } from '@signal-space/sim';
import { createWorkerHandler } from '@signal-space/sim/worker';
import { createSample } from '@signal-space/experiments';
const request = (): RunRequest => ({
  runId: 'test',
  mode: 'inspect',
  scenario: createSample('pair'),
});
const collect = async (input: RunRequest) => {
  const events: RunEvent[] = [];
  for await (const event of execute(input)) events.push(event);
  return events;
};

test('sample preparation preserves complete initial state without advancing physics', async () => {
  const scenario = createSample('pair');
  const before = structuredClone(scenario);
  const events = await collect({ ...request(), scenario });
  assert.deepEqual(
    events.map((e) => e.type),
    ['progress', 'progress', 'snapshot', 'progress', 'completed'],
  );
  const snapshot = events.find((e) => e.type === 'snapshot');
  assert.ok(snapshot?.type === 'snapshot');
  assert.equal(snapshot.snapshot.time, 0);
  assert.deepEqual(
    snapshot.snapshot.nodeState,
    Object.fromEntries(
      before.nodes.map((n) => [n.id, { phi: n.phi, omega: n.omega }]),
    ),
  );
  assert.deepEqual(snapshot.snapshot.history, before.initialHistory);
  snapshot.snapshot.history.pendingPackets.length = 0;
  snapshot.snapshot.history.nodes['A']!.omega = 999;
  assert.deepEqual(scenario, before);
});
test('execution owns the request before yielding control to the caller', async () => {
  const input = request();
  const scenario = input.scenario as ReturnType<typeof createSample>;
  const iterator = execute(input);
  await iterator.next();
  scenario.nodes[0]!.omega = 999;
  const events: RunEvent[] = [];
  for await (const event of iterator) events.push(event);
  const snapshot = events.find((e) => e.type === 'snapshot');
  assert.ok(snapshot?.type === 'snapshot');
  assert.equal(snapshot.snapshot.nodeState['A']!.omega, 2);
});
test('invalid structures and semantic bounds produce field-level failures, no snapshots', async () => {
  const bad = createSample('isolated');
  bad.nodes[0]!.gain = 3;
  for (const scenario of [
    null,
    { nodes: [null] },
    { ...bad, initialHistory: null },
    bad,
  ]) {
    const events = await collect({ ...request(), scenario });
    const final = events.at(-1);
    assert.ok(final?.type === 'failed');
    assert.equal(final.error.code, 'INVALID_SCENARIO');
    assert.ok(final.error.details?.length);
    assert.ok(!events.some((e) => e.type === 'snapshot'));
  }
});
test('unimplemented modes fail explicitly', async () => {
  const events = await collect({
    ...request(),
    mode: 'evolve',
  } as unknown as RunRequest);
  assert.equal(events.length, 1);
  assert.equal(events[0]?.type, 'failed');
});
test('pre-start and in-flight cancellation yield one terminal event and no completion', async () => {
  for (const abortAtStart of [true, false]) {
    const controller = new AbortController();
    if (abortAtStart) controller.abort();
    const events: RunEvent[] = [];
    for await (const event of execute(request(), {
      signal: controller.signal,
    })) {
      events.push(event);
      if (event.type === 'progress') controller.abort();
    }
    assert.equal(events.at(-1)?.type, 'cancelled');
    assert.equal(
      events.filter((e) =>
        ['completed', 'failed', 'cancelled'].includes(e.type),
      ).length,
      1,
    );
    assert.ok(!events.some((e) => e.type === 'snapshot'));
  }
});
test('worker and direct execution emit identical structured-cloneable events', async () => {
  const direct = await collect(request());
  const workerEvents: RunEvent[] = [];
  const handle = createWorkerHandler((e) =>
    workerEvents.push(structuredClone(e)),
  );
  await handle({ type: 'run', request: request() });
  assert.deepEqual(workerEvents, direct);
});
test('worker cancels only matching run, rejects overlap, and accepts a later run', async () => {
  const events: RunEvent[] = [];
  const handle = createWorkerHandler((e) => events.push(e));
  const pending = handle({ type: 'run', request: request() });
  await handle({ type: 'cancel', runId: 'unrelated' });
  await handle({ type: 'run', request: { ...request(), runId: 'overlap' } });
  await handle({ type: 'cancel', runId: 'test' });
  await pending;
  assert.ok(events.some((e) => e.type === 'failed' && e.error.code === 'BUSY'));
  assert.ok(events.some((e) => e.type === 'cancelled' && e.runId === 'test'));
  await handle({ type: 'run', request: { ...request(), runId: 'later' } });
  assert.ok(events.some((e) => e.type === 'completed' && e.runId === 'later'));
});

test('nested preparation fields cannot cross the typed execution boundary malformed', async () => {
  const base = createSample('isolated');
  for (const scenario of [
    {
      ...base,
      initialHistory: { ...base.initialHistory, pendingPackets: null },
    },
    {
      ...base,
      initialHistory: {
        ...base.initialHistory,
        filters: { A: { left: -1, right: 0 } },
      },
    },
    { ...base, initialHistory: { ...base.initialHistory, nodes: { A: true } } },
    { ...base, observation: { ...base.observation, sampleTimes: 'tomorrow' } },
    { ...base, solver: { ...base.solver, method: 'unknown' } },
    { ...base, units: { ...base.units, time: 'minutes' } },
  ]) {
    const events = await collect({ ...request(), scenario });
    const final = events.at(-1);
    assert.ok(final?.type === 'failed');
    assert.equal(final.error.code, 'INVALID_SCENARIO');
    assert.ok(final.error.details?.length);
    assert.ok(!events.some((e) => e.type === 'snapshot'));
  }
});
