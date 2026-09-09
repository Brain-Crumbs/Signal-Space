import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createSample } from '@signal-space/experiments';
import {
  PacketSolver,
  branchPacketRun,
  recordObserver,
  isObserverDataset,
  execute,
} from '@signal-space/sim';
import type {
  DetectorProtocol,
  PacketSnapshot,
  RunEvent,
} from '@signal-space/sim';
import { createWorkerHandler } from '@signal-space/sim/worker';

function scenario() {
  const s = createSample('pair');
  s.nodes.forEach((n) => {
    n.response = 'R1';
    n.gain = 0.5;
    n.emission = { law: 'E0', nu: 0.001 };
  });
  s.initialHistory.pendingPackets = [0.125, 0.25, 0.375, 0.5].map(
    (time, i) => ({
      id: `initial-${i}`,
      source: 'A',
      target: 'B',
      port: 'left',
      emissionTime: time - 1,
      arrivalTime: time,
    }),
  );
  return s;
}
const options = { seed: 'observer-physical-control' };
function finish(solver: PacketSolver, until: number): PacketSnapshot {
  while (solver.time < until && !solver.incomplete) solver.advance(until);
  assert.equal(solver.incomplete, null);
  return solver.snapshot();
}
function detector(): DetectorProtocol {
  return {
    observerId: 'observer-B',
    nodeId: 'B',
    seed: 'detector-control',
    retentionProbability: 1,
    timestamp: {
      kind: 'calibrated-time',
      channel: 'externally-calibrated-test-clock',
    },
    gate: { start: 0, end: 0.75 },
    latency: 0,
    jitter: { kind: 'none' },
    quantization: { width: 0.125, origin: 0 },
    readouts: [],
    marks: { kind: 'none' },
  };
}
function frozen<T>(value: T): T {
  if (value && typeof value === 'object') {
    Object.values(value).forEach(frozen);
    Object.freeze(value);
  }
  return value;
}
test('retention 0/1 changes only detached observer records; no missing-event inventory leaks', () => {
  const snapshot = frozen(finish(new PacketSolver(scenario(), options), 0.75));
  const before = JSON.stringify(snapshot);
  const truth = { runId: 'physical-1', snapshot };
  const all = recordObserver(truth, detector());
  const none = recordObserver(truth, {
    ...detector(),
    retentionProbability: 0,
  });
  assert.equal(all.arrivals.length, 4);
  assert.deepEqual(none.arrivals, []);
  assert.equal(all.physicalRunId, none.physicalRunId);
  assert.deepEqual(none.missingness, {
    kind: 'independent-bernoulli',
    realizedMissingCount: 'unknown',
  });
  assert.equal(JSON.stringify(snapshot), before);
  assert.deepEqual(Object.keys(all.arrivals[0]!).sort(), ['side', 'timestamp']);
  all.arrivals[0]!.timestamp = 999;
  all.protocol.nodeId = 'mutated';
  assert.equal(JSON.stringify(snapshot), before);
});
test('half-open gate and bins, detector latency, and jitter order are explicit', () => {
  const snapshot = finish(new PacketSolver(scenario(), options), 0.75);
  const p = detector();
  p.gate = { start: 0.25, end: 0.5 };
  assert.deepEqual(
    recordObserver({ runId: 'bin', snapshot }, p).arrivals.map(
      (r) => r.timestamp,
    ),
    [0.25, 0.375],
  );
  p.latency = 0.125;
  assert.deepEqual(
    recordObserver({ runId: 'bin', snapshot }, p).arrivals.map(
      (r) => r.timestamp,
    ),
    [0.375, 0.5],
  );
  const negative = { ...detector(), quantization: { width: 1, origin: 0.2 } };
  assert.equal(
    recordObserver({ runId: 'bin', snapshot }, negative).arrivals[0]!.timestamp,
    -0.8,
  );
  const jittered = recordObserver(
    { runId: 'bin', snapshot },
    {
      ...detector(),
      jitter: { kind: 'uniform', halfWidth: 2 },
      readouts: ['local-phase'],
    },
  );
  assert.ok(
    jittered.arrivals.every(
      (r, i, a) => i === 0 || r.timestamp >= a[i - 1]!.timestamp,
    ),
  );
  assert.ok(
    jittered.arrivals.some(
      (r, i, a) => i > 0 && r.localPhase! < a[i - 1]!.localPhase!,
    ),
    'jitter reverses reported order',
  );
  assert.deepEqual(
    snapshot.records.filter((r) => r.kind === 'received').map((r) => r.time),
    [0.125, 0.25, 0.375, 0.5],
  );
});
test('local-phase timestamps need no global time channel; readable source tags require a declared channel', () => {
  const snapshot = finish(new PacketSolver(scenario(), options), 0.75);
  const p: DetectorProtocol = {
    ...detector(),
    timestamp: { kind: 'local-phase' },
    gate: {
      start: snapshot.history[0]!.nodes.B!.phi,
      end: snapshot.history.at(-1)!.nodes.B!.phi,
    },
    readouts: ['local-phase', 'local-frequency'],
  };
  const local = recordObserver({ runId: 'local', snapshot }, p);
  assert.equal(local.timestampUnit, 'rad');
  assert.ok(isObserverDataset(local));
  assert.ok(
    local.arrivals.every(
      (r) =>
        r.localPhase !== undefined &&
        r.localFrequency !== undefined &&
        !('sourceTag' in r),
    ),
  );
  const tagged = recordObserver(
    { runId: 'local', snapshot },
    { ...p, marks: { kind: 'source-tag', channel: 'readable-emitter-labels' } },
  );
  assert.ok(tagged.arrivals.every((r) => r.sourceTag === 'A'));
  assert.ok(isObserverDataset(tagged));
});
test('observer datasets reject hidden fields at type, schema and runtime boundaries', () => {
  const snapshot = finish(new PacketSolver(scenario(), options), 0.75);
  const data = recordObserver({ runId: 'physical-1', snapshot }, detector());
  for (const field of [
    'packetId',
    'source',
    'remotePhase',
    'physicalTime',
    'deletedEvents',
    'rng',
  ]) {
    const bad = structuredClone(data);
    Object.assign(bad.arrivals[0]!, { [field]: 'hidden' });
    assert.equal(isObserverDataset(bad), false);
    assert.equal(isObserverDataset({ ...data, [field]: [] }), false);
  }
  const bad = structuredClone(data);
  bad.arrivals[0]!.sourceTag = 'A';
  assert.equal(isObserverDataset(bad), false);
  delete bad.arrivals[0]!.sourceTag;
  bad.arrivals[0]!.localPhase = 1;
  assert.equal(isObserverDataset(bad), false);
  // @ts-expect-error Observer API has no physical packet identifier.
  const packetId = data.arrivals[0]!.packetId;
  assert.equal(packetId, undefined);
  // @ts-expect-error Observer API has no remote phase channel.
  const remotePhase = data.arrivals[0]!.remotePhase;
  assert.equal(remotePhase, undefined);
});
test('independent observer streams are repeatable and share one unchanged physical history', () => {
  const s = scenario();
  s.initialHistory.pendingPackets = Array.from({ length: 80 }, (_, i) => ({
    id: `batch-${i}`,
    source: 'A',
    target: 'B',
    port: 'left',
    emissionTime: 0.01 + i * 0.005 - 1,
    arrivalTime: 0.01 + i * 0.005,
  }));
  const snapshot = finish(new PacketSolver(s, options), 0.75),
    truth = { runId: 'same-run', snapshot };
  const p = {
    ...detector(),
    retentionProbability: 0.5,
    quantization: { width: 0.001, origin: 0 },
  };
  const a = recordObserver(truth, p),
    b = recordObserver(truth, { ...p, observerId: 'independent-B' });
  assert.deepEqual(a, recordObserver(truth, p));
  assert.notDeepEqual(a.arrivals, b.arrivals);
  assert.equal(a.physicalRunId, b.physicalRunId);
  assert.equal(
    snapshot.records.filter((r) => r.kind === 'received').length,
    80,
  );
});
test('invalid, unsupported and uncovered detector protocols fail before exporting', () => {
  const snapshot = finish(new PacketSolver(scenario(), options), 0.75);
  for (const changes of [
    { retentionProbability: NaN },
    { retentionProbability: -1 },
    { retentionProbability: 1.1 },
    { jitter: { kind: 'gaussian' } },
    { latency: -1 },
    { quantization: { width: 0, origin: 0 } },
    { gate: { start: 0, end: 1 } },
    { gate: { start: 0.5, end: 0.5 } },
    { nodeId: 'remote' },
    { timestamp: { kind: 'calibrated-time' } },
    { marks: { kind: 'source-tag' } },
    { packetId: 'secret' },
    { readouts: ['remote-phase'] },
    { quantization: { width: Number.MIN_VALUE, origin: 0 } },
  ])
    assert.throws(() =>
      recordObserver({ runId: 'invalid', snapshot }, {
        ...detector(),
        ...changes,
      } as DetectorProtocol),
    );
  for (const runId of [42, true, { length: 1 }])
    assert.throws(() =>
      recordObserver(
        { runId, snapshot } as unknown as {
          runId: string;
          snapshot: PacketSnapshot;
        },
        detector(),
      ),
    );
});
test('physical removal branches and re-evolves filters/frequency, preserving the parent and common prefix', () => {
  const solver = new PacketSolver(scenario(), options);
  const checkpoint = finish(solver, 0.1),
    saved = JSON.stringify(checkpoint);
  const branch = branchPacketRun(
    { runId: 'parent', snapshot: checkpoint },
    'removed',
    [{ time: 0.125, kind: 'remove-pulse', target: 'initial-0' }],
  );
  assert.deepEqual(branch.solver.snapshot().history, checkpoint.history);
  const removed = finish(branch.solver, 0.2),
    original = finish(solver, 0.2);
  assert.equal(JSON.stringify(checkpoint), saved);
  assert.equal(removed.filters[2], 0);
  assert.ok(Math.abs(original.filters[2]! - 10 * Math.exp(-0.75)) < 1e-12);
  assert.ok(original.state[3]! > removed.state[3]!);
  assert.deepEqual(
    removed.records
      .filter((r) => r.packetId === 'initial-0')
      .map((r) => r.kind),
    ['pending', 'absorbed'],
  );
  assert.equal(branch.lineage.parentRunId, 'parent');
  assert.equal(branch.lineage.forkTime, 0.1);
  const replay = new PacketSolver(
    removed.scenario,
    removed.options,
    JSON.parse(JSON.stringify(removed)),
  );
  assert.deepEqual(finish(replay, 0.75), finish(branch.solver, 0.75));
});
test('a probe follows positive-delay transport, changes the receiving law, and carries physical lineage', () => {
  const s = scenario();
  s.initialHistory.pendingPackets = [];
  const solver = new PacketSolver(s, options),
    checkpoint = finish(solver, 0.1);
  const linkId = s.links.find((l) => l.source === 'A')!.id;
  const branch = branchPacketRun(
    { runId: 'baseline', snapshot: checkpoint },
    'probe',
    [{ time: 0.125, kind: 'add-probe', target: 'A', value: { linkId } }],
  );
  assert.equal(finish(branch.solver, 1.12).filters[2], 0);
  const arrival = finish(branch.solver, 1.125);
  assert.equal(arrival.filters[2], 10);
  const result = finish(branch.solver, 1.25),
    baseline = finish(solver, 1.25);
  assert.ok(result.state[3]! > baseline.state[3]!);
  const records = result.records.filter((r) => r.packetId === 'probe:0');
  assert.deepEqual(
    records.map((r) => r.kind),
    ['emitted', 'pending', 'received'],
  );
  assert.equal(records[0]!.interventionIndex, 0);
  assert.equal(records[2]!.time - records[0]!.time, 1);
  assert.equal(branch.lineage.interventions[0]!.kind, 'add-probe');
});
test('branch lineage requires distinct bounded string IDs at untyped boundaries', () => {
  const snapshot = new PacketSolver(scenario(), options).snapshot();
  const interventions = [
    { time: 0.125, kind: 'remove-pulse', target: 'initial-0' },
  ] as const;
  const saved = JSON.stringify(snapshot);
  for (const invalid of [
    undefined,
    null,
    42,
    true,
    {},
    { length: 1 },
    '',
    'x'.repeat(4097),
  ]) {
    for (const [parentId, branchId] of [
      [invalid, 'branch'],
      ['parent', invalid],
    ]) {
      assert.throws(
        () =>
          branchPacketRun(
            { runId: parentId as string, snapshot },
            branchId as string,
            [...interventions],
          ),
        { code: 'INVALID_REQUEST', message: /run IDs must be strings/ },
      );
    }
  }
  assert.throws(
    () =>
      branchPacketRun({ runId: 'same', snapshot }, 'same', [...interventions]),
    { code: 'INVALID_REQUEST' },
  );
  for (const [parentId, branchId] of [
    ['p', 'b'],
    ['p'.repeat(4096), 'b'.repeat(4096)],
  ]) {
    const { lineage } = branchPacketRun(
      { runId: parentId!, snapshot },
      branchId!,
      [...interventions],
    );
    assert.equal(lineage.parentRunId, parentId);
    assert.equal(lineage.runId, branchId);
  }
  assert.equal(JSON.stringify(snapshot), saved);
});
test('bad physical actions fail; simultaneous removal precedes joint arrivals and respects budgets', () => {
  const s = scenario();
  for (const action of [
    { time: 0, kind: 'remove-pulse', target: 'missing' },
    { time: 0, kind: 'remove-pulse', target: 'initial-0', value: {} },
    {
      time: 0,
      kind: 'add-probe',
      target: 'B',
      value: { linkId: s.links[0]!.id },
    },
    { time: 0, kind: 'change-parameter', target: 'B' },
  ] as const)
    assert.throws(
      () => new PacketSolver({ ...s, interventions: [action] }, options),
    );
  const checkpoint = new PacketSolver(s, options).snapshot();
  assert.throws(() =>
    branchPacketRun({ runId: 'p', snapshot: checkpoint }, 'p', []),
  );
  assert.throws(() =>
    branchPacketRun({ runId: 'p', snapshot: checkpoint }, 'b', [
      { time: 0, kind: 'remove-pulse', target: 'initial-0' },
    ]),
  );
  s.initialHistory.pendingPackets[1]!.arrivalTime = 0.125;
  s.initialHistory.pendingPackets[1]!.emissionTime = -0.875;
  s.interventions = [
    { time: 0.125, kind: 'remove-pulse', target: 'initial-0' },
  ];
  assert.equal(finish(new PacketSolver(s, options), 0.125).filters[2], 10);
  s.interventions = [
    {
      time: 0,
      kind: 'add-probe',
      target: 'A',
      value: { linkId: s.links[0]!.id },
    },
  ];
  const limited = new PacketSolver(s, { ...options, maxPending: 4 });
  assert.equal(limited.incomplete, 'maxPending');
  assert.equal(
    limited.snapshot().records.filter((r) => r.packetId.startsWith('probe:'))
      .length,
    0,
  );
});
test('physical intervention execution agrees across the shared direct/worker API', async () => {
  const s = scenario();
  s.interventions = [
    { time: 0.125, kind: 'remove-pulse', target: 'initial-0' },
  ];
  const request = {
    runId: 'worker-intervention',
    mode: 'packets' as const,
    scenario: s,
    packets: options,
    until: 0.5,
  };
  const direct: RunEvent[] = [],
    worker: RunEvent[] = [];
  for await (const e of execute(request)) direct.push(e);
  await createWorkerHandler((e) => worker.push(e))({ type: 'run', request });
  assert.deepEqual(worker, direct);
  assert.equal(direct.at(-1)!.type, 'completed');
});

test('branching rejects a future action that changes a previously rejected trial', () => {
  const s = createSample('pair');
  s.solver.absoluteTolerance = 1e-30;
  s.solver.relativeTolerance = 1e-30;
  s.initialHistory.filters.B!.left = 1;
  const solver = new PacketSolver(s, { seed: 'branch-rejection' });
  solver.advance(1);
  const snapshot = solver.snapshot();
  assert.equal(snapshot.time, 0);
  assert.equal(snapshot.steps, 1);
  assert.throws(
    () =>
      branchPacketRun({ runId: 'parent', snapshot }, 'branch', [
        {
          time: 0.00001,
          kind: 'add-probe',
          target: 'A',
          value: { linkId: 'A-B' },
        },
      ]),
    /changes a rejected trial/,
  );
  // A later action leaves the entire prefix (including the rejected step) intact.
  const valid = branchPacketRun({ runId: 'parent', snapshot }, 'branch', [
    { time: 0.1, kind: 'add-probe', target: 'A', value: { linkId: 'A-B' } },
  ]);
  assert.equal(valid.solver.time, snapshot.time);
  assert.equal(valid.solver.snapshot().nextStep, snapshot.nextStep);
});
