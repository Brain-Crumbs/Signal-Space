import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createSample } from '@signal-space/experiments';
import { PacketSolver, execute } from '@signal-space/sim';
import type {
  PacketOptions,
  PacketSnapshot,
  RunEvent,
} from '@signal-space/sim';

const options: PacketOptions = { seed: 't04-smoke-v1' };
function pair() {
  const s = createSample('pair');
  s.solver.method = 'event';
  for (const n of s.nodes) {
    n.response = 'R0';
    n.gain = 0;
    n.emission = { law: 'E0', nu: 8 };
  }
  return s;
}
function run(solver: PacketSolver, until: number): PacketSnapshot {
  while (solver.time < until && !solver.incomplete) solver.advance(until);
  assert.equal(solver.incomplete, null);
  return solver.snapshot();
}
function close(actual: number, expected: number, tolerance = 1e-9) {
  assert.ok(
    Math.abs(actual - expected) < tolerance,
    `${actual} != ${expected} within ${tolerance}`,
  );
}
test('joint arrivals and analytic exponential filter memory are insertion-order independent', () => {
  const s = pair();
  s.initialHistory.filters.B = { left: 2, right: 3 };
  s.initialHistory.pendingPackets = ['z', 'a', 'm'].map((id) => ({
    id,
    source: 'A',
    target: 'B',
    emissionTime: -0.875,
    arrivalTime: 0.125,
    port: 'left',
  }));
  const first = new PacketSolver(s, options);
  const before = run(first, 0.125).history.at(-1)!.nodes.B!;
  close(before.left, 2 * Math.exp(-1.25) + 30);
  close(before.right, 3 * Math.exp(-1.25));
  const result = run(first, 0.3);
  close(
    result.history.at(-1)!.nodes.B!.left,
    2 * Math.exp(-3) + 30 * Math.exp(-1.75),
  );
  s.initialHistory.pendingPackets.reverse();
  const second = new PacketSolver(s, options);
  run(second, 0.125);
  const reordered = run(second, 0.3);
  assert.deepEqual(result.records, reordered.records);
  assert.deepEqual(result.history, reordered.history);
  // Exact t=0 inventory is applied before the initial sample, with no phase reset.
  s.initialHistory.pendingPackets.forEach((p) => {
    p.emissionTime = -1;
    p.arrivalTime = 0;
  });
  const zero = new PacketSolver(s, options).sample().nodes.B!;
  assert.equal(zero.left, 32);
  assert.equal(zero.phi, s.nodes[1]!.phi);
});
test('R0 rate controls use 64 predeclared seeds and six-sigma aggregate Poisson bands', () => {
  const s = createSample('isolated');
  const n = s.nodes[0]!;
  n.emission = { law: 'E0', nu: 16 };
  n.amplitude = 0;
  const counts: number[][] = [];
  for (let seed = 0; seed < 64; seed++) {
    const snapshot = run(
      new PacketSolver(s, { seed: `rate-control-${seed}` }),
      4,
    );
    counts.push(
      ['left', 'right'].map(
        (port) =>
          snapshot.records.filter(
            (r) => r.kind === 'emitted' && r.port === port,
          ).length,
      ),
    );
  }
  for (let port = 0; port < 2; port++) {
    const values = counts.map((c) => c[port]!);
    const total = values.reduce((a, b) => a + b, 0);
    const expected = 64 * 4 * 8;
    assert.ok(Math.abs(total - expected) < 6 * Math.sqrt(expected));
    const mean = total / 64;
    const variance = values.reduce((a, b) => a + (b - mean) ** 2, 0) / 63;
    assert.ok(
      variance > 12 && variance < 60,
      `Poisson variance control: ${variance}`,
    );
  }
  const covariance =
    counts.reduce((sum, [l, r]) => sum + (l! - 32) * (r! - 32), 0) / 64;
  assert.ok(
    Math.abs(covariance) < 24,
    `Independent port control: ${covariance}`,
  );
});
test('same-runtime replay preserves every raw event, RNG, queue and adaptive continuation', () => {
  const s = createSample('pair');
  const first = new PacketSolver(s, options);
  // Pause on an existing accepted step: resume must not change the mesh.
  for (let i = 0; i < 80; i++) first.advance(2);
  const checkpoint = first.snapshot();
  const resumed = new PacketSolver(
    s,
    options,
    JSON.parse(JSON.stringify(checkpoint)),
  );
  const actual = run(resumed, 2),
    expected = run(first, 2);
  assert.deepEqual(actual, expected);
  assert.deepEqual(run(new PacketSolver(s, options), 2), expected);
  assert.equal(actual.options.seed, options.seed);
  for (const corrupt of [
    'filters',
    'rng',
    'pending',
    'history',
    'seed',
  ] as const) {
    const bad = structuredClone(checkpoint);
    if (corrupt === 'filters') bad.filters[0]! += 1;
    if (corrupt === 'rng') bad.streams[0]!.rng++;
    if (corrupt === 'pending') bad.pending = [];
    if (corrupt === 'history') bad.history[0]!.nodes.A!.phi++;
    if (corrupt === 'seed') bad.options.seed = 'another';
    if (corrupt === 'pending' && checkpoint.pending.length === 0) continue;
    assert.throws(() => new PacketSolver(s, options, bad), /Checkpoint/);
  }
});
test('packet accounting, causal support, no retransmission, positive bounded omega', () => {
  const s = createSample('pair');
  s.nodes.forEach((n) => {
    n.response = 'R2';
    n.gain = -0.7;
    n.emission = { law: 'E1', q: 20 };
  });
  const snapshot = run(new PacketSolver(s, options), 3);
  const terminal = snapshot.records.filter((r) =>
    ['received', 'escaped', 'absorbed'].includes(r.kind),
  );
  assert.equal(new Set(terminal.map((r) => r.packetId)).size, terminal.length);
  const emitted = snapshot.records.filter((r) => r.kind === 'emitted');
  assert.ok(emitted.length > 10);
  assert.equal(emitted.length, terminal.length + snapshot.pending.length);
  for (const r of terminal.filter((r) => r.kind === 'received')) {
    const e = emitted.find((e) => e.packetId === r.packetId)!;
    assert.equal(r.time, e.time + 1);
  }
  for (const sample of snapshot.history)
    for (const n of s.nodes) {
      const v = sample.nodes[n.id]!;
      assert.ok(
        v.omega >= n.omega0 - Math.abs(n.gain) - 1e-14 &&
          v.omega <= n.omega0 + Math.abs(n.gain) + 1e-14,
      );
      if (sample.time < 1) {
        assert.equal(v.left, 0);
        assert.equal(v.right, 0);
      }
    }
});
test('passive detector seed and recording config cannot change physical traces', () => {
  const s = pair();
  const a = run(new PacketSolver(s, { ...options, detectorSeed: 'one' }), 2);
  s.observation = {
    sampleTimes: [0, 0.2],
    visible: ['reported-count'],
    detectorLatency: 10,
  };
  const b = run(
    new PacketSolver(s, {
      ...options,
      detectorSeed: 'two',
      interventionSeed: 'unused',
    }),
    2,
  );
  for (const key of [
    'history',
    'records',
    'streams',
    'pending',
    'state',
    'filters',
  ] as const)
    assert.deepEqual(a[key], b[key]);
});
test('nonlinear R1 filtered forcing agrees with independent convolution quadrature', () => {
  const s = createSample('isolated'),
    n = s.nodes[0]!;
  n.response = 'R1';
  n.gain = -0.4;
  s.initialHistory.filters[n.id]! = { left: 5, right: 0 };
  const snapshot = run(new PacketSolver(s, options), 0.4);
  const t = 0.4,
    panels = 20000,
    h = t / panels;
  let integral = 0;
  for (let i = 0; i <= panels; i++) {
    const u = i * h;
    const f =
      (Math.exp(-(t - u) / n.relaxationTime) *
        n.gain *
        Math.tanh((5 * Math.exp(-u / s.filterWidth)) / s.rateScale)) /
      n.relaxationTime;
    integral += (i === 0 || i === panels ? 1 : i % 2 ? 4 : 2) * f;
  }
  close(snapshot.state[1]!, n.omega0 + (integral * h) / 3, 1e-8);
});
test('resource exhaustion is explicitly incomplete and checkpoint corruption/unsupported laws fail', async () => {
  for (const limits of [{ maxSteps: 1 }, { maxEvents: 1 }, { maxPending: 1 }]) {
    const events: RunEvent[] = [];
    for await (const e of execute({
      runId: 'limit',
      mode: 'packets',
      scenario: pair(),
      packets: { ...options, ...limits },
      until: 2,
    }))
      events.push(e);
    assert.equal(events.at(-1)?.type, 'incomplete');
    assert.ok(events.some((e) => e.type === 'packet-snapshot'));
    assert.ok(!events.some((e) => e.type === 'completed'));
    const checkpoint = events.find((e) => e.type === 'packet-snapshot');
    if (checkpoint?.type === 'packet-snapshot')
      assert.deepEqual(
        new PacketSolver(
          pair(),
          { ...options, ...limits },
          checkpoint.snapshot,
        ).snapshot(),
        checkpoint.snapshot,
      );
  }
  const s = pair();
  s.initialHistory.pendingResponses = [
    { nodeId: 'A', dueTime: 1, payload: {} },
  ];
  assert.throws(() => new PacketSolver(s, options), /T05/);
  s.initialHistory.pendingResponses = [];
  s.initialHistory.pendingPackets = [
    {
      id: 'bad',
      source: 'A',
      target: 'B',
      emissionTime: -1,
      arrivalTime: 0.2,
      port: 'left',
    },
  ];
  assert.throws(() => new PacketSolver(s, options), /route/);
});
test('cancellation yields a complete, restartable physical checkpoint', async () => {
  const controller = new AbortController();
  const events: RunEvent[] = [];
  for await (const e of execute(
    {
      runId: 'cancel',
      mode: 'packets',
      scenario: pair(),
      packets: options,
      until: 3,
    },
    { signal: controller.signal },
  )) {
    events.push(e);
    if (e.type === 'packet-sample' && e.sample.time > 0.1) controller.abort();
  }
  assert.equal(events.at(-1)?.type, 'cancelled');
  const checkpoint = events.find((e) => e.type === 'packet-snapshot');
  assert.ok(checkpoint?.type === 'packet-snapshot');
  const resumed = run(
    new PacketSolver(pair(), options, checkpoint.snapshot),
    3,
  );
  const reference = run(new PacketSolver(pair(), options), 3);
  assert.deepEqual(resumed, reference);
});
