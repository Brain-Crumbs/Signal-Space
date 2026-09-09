import assert from 'node:assert/strict';
import { test } from 'node:test';
import { createSample } from '@signal-space/experiments';
import { validateScenario } from '@signal-space/model';
import { execute } from '@signal-space/sim';
import type { RunEvent } from '@signal-space/sim';

const preparation = () => {
  const scenario = createSample('pair');
  scenario.initialHistory.pendingPackets = [
    {
      id: 'in-flight',
      source: 'A',
      target: 'B',
      port: 'left',
      emissionTime: -0.25,
      arrivalTime: 0.75,
    },
  ];
  scenario.initialHistory.pendingResponses = [
    {
      nodeId: 'B',
      dueTime: 0.8,
      payload: { kind: 'filter', nested: { amount: 1 } },
    },
  ];
  scenario.interventions = [
    {
      time: 1,
      kind: 'change-parameter',
      target: 'A',
      value: { gain: 0.1 },
    },
  ];
  return scenario;
};
const collect = async (scenario: unknown) => {
  const events: RunEvent[] = [];
  for await (const event of execute({
    runId: 'review',
    mode: 'inspect',
    scenario,
  }))
    events.push(event);
  return events;
};
const rejects = async (scenario: unknown) => {
  const events = await collect(scenario);
  const final = events.at(-1);
  assert.ok(final?.type === 'failed');
  assert.equal(final.error.code, 'INVALID_SCENARIO');
  assert.ok(final.error.details?.length);
  assert.ok(
    !events.some((e) => e.type === 'snapshot' || e.type === 'completed'),
  );
};

test('undeclared fields are rejected across closed nested shapes', async () => {
  const selectors = [
    (s: ReturnType<typeof preparation>) => s.nodes[0]!,
    (s: ReturnType<typeof preparation>) => s.nodes[0]!.emission,
    (s: ReturnType<typeof preparation>) => s.links[0]!,
    (s: ReturnType<typeof preparation>) => s.boundaries,
    (s: ReturnType<typeof preparation>) => s.boundaries.left,
    (s: ReturnType<typeof preparation>) => s.initialHistory,
    (s: ReturnType<typeof preparation>) => s.initialHistory.nodes['A']!,
    (s: ReturnType<typeof preparation>) => s.initialHistory.filters['A']!,
    (s: ReturnType<typeof preparation>) => s.initialHistory.pendingPackets[0]!,
    (s: ReturnType<typeof preparation>) =>
      s.initialHistory.pendingResponses[0]!,
    (s: ReturnType<typeof preparation>) => s.initialHistory.rngState!,
    (s: ReturnType<typeof preparation>) => s.interventions[0]!,
    (s: ReturnType<typeof preparation>) => s.observation,
    (s: ReturnType<typeof preparation>) => s.solver,
    (s: ReturnType<typeof preparation>) => s.units,
  ];
  for (const select of selectors) {
    const scenario = preparation();
    Object.assign(select(scenario), { sourcePhase: 123 });
    await rejects(scenario);
  }
});

test('history and filter maps require exactly the scenario node IDs', async () => {
  for (const key of ['nodes', 'filters'] as const) {
    for (const mutation of ['empty', 'missing', 'extra'] as const) {
      const scenario = preparation();
      if (mutation === 'empty') scenario.initialHistory[key] = {};
      if (mutation === 'missing') delete scenario.initialHistory[key]['B'];
      if (mutation === 'extra')
        Object.assign(scenario.initialHistory[key], {
          ghost: scenario.initialHistory[key]['A'],
        });
      const validation = validateScenario(scenario);
      assert.equal(validation.ok, false);
      assert.ok(
        validation.errors.some((e) =>
          e.path.startsWith(`initialHistory.${key}.`),
        ),
      );
      await rejects(scenario);
    }
  }
});

test('pending packets reject future emission, past arrival, zero transit and nonfinite times', async () => {
  for (const [emissionTime, arrivalTime] of [
    [1, -1],
    [0.25, 1.25],
    [-1.25, -0.25],
    [0, 0],
    [NaN, 1],
    [-Infinity, 1],
    [-1, Infinity],
  ]) {
    const scenario = preparation();
    Object.assign(scenario.initialHistory.pendingPackets[0]!, {
      emissionTime,
      arrivalTime,
    });
    assert.equal(validateScenario(scenario).ok, false);
    await rejects(scenario);
  }
});

test('causal boundary packets and declared arbitrary payloads survive inspection', async () => {
  for (const [emissionTime, arrivalTime] of [
    [-1, 0],
    [0, 1],
    [-0.25, 0.75],
  ]) {
    const scenario = preparation();
    Object.assign(scenario.initialHistory.pendingPackets[0]!, {
      emissionTime,
      arrivalTime,
    });
    assert.equal(validateScenario(scenario).ok, true);
    const events = await collect(scenario);
    assert.equal(events.at(-1)?.type, 'completed');
    const snapshot = events.find((e) => e.type === 'snapshot');
    assert.ok(snapshot?.type === 'snapshot');
    assert.deepEqual(snapshot.snapshot.history, scenario.initialHistory);
  }
});

test('history endpoints must match initial phase and frequency exactly', async () => {
  for (const field of ['phiAtZero', 'omega'] as const) {
    const scenario = preparation();
    scenario.initialHistory.nodes['A']![field] += 0.1;
    const validation = validateScenario(scenario);
    assert.equal(validation.ok, false);
    assert.ok(
      validation.errors.some(
        (e) => e.path === `initialHistory.nodes.A.${field}`,
      ),
    );
    await rejects(scenario);
  }
  const scenario = preparation();
  scenario.nodes[0]!.phi += 4 * Math.PI;
  scenario.initialHistory.nodes['A']!.phiAtZero = scenario.nodes[0]!.phi;
  assert.equal((await collect(scenario)).at(-1)?.type, 'completed');
});

test('pending responses must target a declared clock', async () => {
  const scenario = preparation();
  scenario.initialHistory.pendingResponses[0]!.nodeId = 'ghost';
  const validation = validateScenario(scenario);
  assert.equal(validation.ok, false);
  assert.ok(
    validation.errors.some(
      (e) => e.path === 'initialHistory.pendingResponses[0].nodeId',
    ),
  );
  await rejects(scenario);
});

test('pending packet source and target must be declared clocks', async () => {
  for (const endpoint of ['source', 'target'] as const) {
    const scenario = preparation();
    scenario.initialHistory.pendingPackets[0]![endpoint] = 'ghost';
    const validation = validateScenario(scenario);
    assert.equal(validation.ok, false);
    assert.ok(
      validation.errors.some(
        (e) => e.path === `initialHistory.pendingPackets[0].${endpoint}`,
      ),
    );
    await rejects(scenario);
  }
});

test('mirror round trips contribute to the required history horizon', async () => {
  const scenario = preparation();
  scenario.boundaries.left = { kind: 'mirror', exteriorDistance: 2 };
  // c0=1 and distance=2 require four seconds of history, not the link's one.
  const validation = validateScenario(scenario);
  assert.equal(validation.ok, false);
  assert.ok(
    validation.errors.some((e) => e.path === 'initialHistory.startTime'),
  );
  await rejects(scenario);
  scenario.initialHistory.startTime = -4;
  assert.equal((await collect(scenario)).at(-1)?.type, 'completed');
  scenario.boundaries.right = { kind: 'mirror', exteriorDistance: 3 };
  await rejects(scenario);
  scenario.initialHistory.startTime = -6;
  assert.equal((await collect(scenario)).at(-1)?.type, 'completed');
});

test('uncloneable extension values are invalid scenarios, not internal failures', async () => {
  for (const value of [() => 1, Symbol('invalid')]) {
    const response = preparation();
    response.initialHistory.pendingResponses[0]!.payload = value;
    await rejects(response);
    const intervention = preparation();
    intervention.interventions[0]!.value = value;
    await rejects(intervention);
  }
});
