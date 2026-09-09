import assert from 'node:assert/strict';
import { test } from 'node:test';
import { execute } from '@signal-space/sim';
import { EnvelopeSolver } from '../packages/sim/src/envelope.js';
import type {
  EnvelopeOptions,
  EnvelopeSample,
  EnvelopeSnapshot,
  RunEvent,
  TickCrossing,
} from '@signal-space/sim';
import type { DenseSegment } from '../packages/sim/src/envelope.js';
import { createWorkerHandler } from '@signal-space/sim/worker';
import { createSample } from '@signal-space/experiments';
import type { Scenario } from '@signal-space/model';

async function run(
  scenario: Scenario,
  until: number,
  envelope: EnvelopeOptions = {},
  resume?: EnvelopeSnapshot,
) {
  const samples: EnvelopeSample[] = [],
    ticks: TickCrossing[] = [];
  let snapshot: EnvelopeSnapshot | undefined;
  for await (const e of execute({
    runId: 'numeric',
    mode: 'envelope',
    scenario,
    until,
    envelope,
    ...(resume ? { resume } : {}),
  })) {
    if (e.type === 'failed') assert.fail(`${e.error.code}: ${e.error.message}`);
    if (e.type === 'envelope-sample') {
      samples.push(e.sample);
      ticks.push(...e.ticks);
    }
    if (e.type === 'envelope-snapshot') snapshot = e.snapshot;
  }
  assert.ok(snapshot);
  return { samples, ticks, snapshot, last: samples.at(-1)! };
}
const close = (actual: number, expected: number, tolerance = 1e-7) =>
  assert.ok(
    Math.abs(actual - expected) <= tolerance,
    `${actual} != ${expected} (tol ${tolerance})`,
  );
function isolated(): Scenario {
  const s = createSample('isolated');
  s.nodes[0]!.emission = { law: 'E1', q: 3 };
  s.solver.step = 0.2;
  return s;
}
function driven(): Scenario {
  const s = isolated(),
    n = s.nodes[0]!;
  n.gain = 0.5;
  n.response = 'R1';
  n.relaxationTime = 0.7;
  s.boundaries.left = { kind: 'driven', rate: 1.3 };
  return s;
}

test('R0 phase, nonnegative E0/E1 rates, quadrature and section crossings match independent identities', async () => {
  for (const law of ['E0', 'E1'] as const) {
    const s = isolated(),
      n = s.nodes[0]!;
    n.emission = law === 'E0' ? { law, nu: 3 } : { law, q: 3 };
    const duration = (4 * Math.PI) / n.omega0;
    const result = await run(s, duration);
    for (const sample of result.samples) {
      const v = sample.nodes[n.id]!;
      close(v.phi, n.phi + n.omega0 * sample.time);
      close(v.omega, n.omega0);
      assert.ok(v.rhoLeft >= 0 && v.rhoRight >= 0);
      close(
        v.rhoLeft + v.rhoRight,
        law === 'E0' ? 3 : (3 * n.omega0) / (2 * Math.PI),
      );
      close(
        v.integratedLeft + v.integratedRight,
        law === 'E0' ? 3 * sample.time : (3 * (v.phi - n.phi)) / (2 * Math.PI),
      );
    }
    assert.ok(result.ticks.length >= 1);
    for (const tick of result.ticks)
      close(tick.time, (tick.sectionIndex * 2 * Math.PI - n.phi) / n.omega0);
    close(
      result.last.nodes[n.id]!.integratedLeft +
        result.last.nodes[n.id]!.integratedRight,
      law === 'E0' ? 3 * duration : 6,
    );
  }
});

test('constant-input R1 matches exponential frequency and integrated phase for both gain signs', async () => {
  for (const sign of [-1, 1]) {
    const s = driven(),
      n = s.nodes[0]!;
    n.gain *= sign;
    const result = await run(s, 3);
    const target = n.omega0 + n.gain * Math.tanh(1.3 / s.rateScale);
    for (const p of result.samples) {
      close(
        p.nodes[n.id]!.omega,
        target + (n.omega - target) * Math.exp(-p.time / n.relaxationTime),
      );
      close(
        p.nodes[n.id]!.phi,
        n.phi +
          target * p.time +
          (n.omega - target) *
            n.relaxationTime *
            (1 - Math.exp(-p.time / n.relaxationTime)),
      );
      assert.ok(p.nodes[n.id]!.boundMargin >= -1e-10);
    }
  }
});

test('non-grid delay preserves causal onset and refinement converges', async () => {
  const s = createSample('pair');
  s.nodes[1]!.position = 0.137;
  s.links.forEach((l) => (l.delay = 0.137));
  s.nodes.forEach((n) => {
    n.amplitude = 0;
    n.emission = { law: 'E0', nu: 2 };
  });
  s.solver.step = 0.11;
  const r = await run(s, 0.8, { preparation: 'empty-links' });
  assert.ok(r.samples.some((p) => p.time === 0.137));
  for (const p of r.samples) {
    const n = s.nodes[0]!,
      v = p.nodes[n.id]!;
    if (p.time <= 0.137) close(v.omega, n.omega0, 1e-13);
    const dt = Math.max(0, p.time - 0.137),
      target = n.omega0 + n.gain * Math.tanh(1);
    close(v.omega, target + (n.omega0 - target) * Math.exp(-dt), 1e-7);
    assert.ok(p.retarded.every((v) => v.sourceTime <= p.time - 0.137 + 1e-15));
  }
  const errors = [];
  for (const step of [0.11, 0.055, 0.0275]) {
    const c = driven();
    c.solver = {
      method: 'rk4',
      step,
      absoluteTolerance: 1e-3,
      relativeTolerance: 1e-3,
    };
    const out = await run(c, 0.91),
      n = c.nodes[0]!,
      target = n.omega0 + n.gain * Math.tanh(1.3);
    errors.push(
      Math.abs(
        out.last.nodes[n.id]!.omega -
          (target + (n.omega - target) * Math.exp(-0.91 / n.relaxationTime)),
      ),
    );
  }
  assert.ok(
    errors[1]! < errors[0]! / 8 && errors[2]! < errors[1]! / 8,
    `${errors}`,
  );
});

test('saved complete history resumes identically at an accepted step and rejects missing/corrupt history', async () => {
  const s = createSample('pair');
  s.solver.step = 0.08;
  const full = await run(s, 1.7);
  const cut = full.snapshot.segments[19]!.end;
  const first = await run(s, cut);
  const checkpoint = JSON.parse(
    JSON.stringify(first.snapshot),
  ) as EnvelopeSnapshot;
  const resumed = await run(s, 1.7, {}, checkpoint);
  for (const n of s.nodes) {
    close(resumed.last.nodes[n.id]!.phi, full.last.nodes[n.id]!.phi, 2e-8);
    close(resumed.last.nodes[n.id]!.omega, full.last.nodes[n.id]!.omega, 2e-8);
  }
  assert.equal(first.ticks.length + resumed.ticks.length, full.ticks.length);
  for (const mutate of [
    (c: EnvelopeSnapshot) => c.segments.shift(),
    (c: EnvelopeSnapshot) => {
      c.state[0]! += 0.1;
    },
    (c: EnvelopeSnapshot) => {
      c.segments[0]!.d0[0] = 999;
    },
    (c: EnvelopeSnapshot) => {
      c.segments[0]!.y1[2]! += 1;
      for (const segment of c.segments.slice(1)) {
        segment.y0[2]! += 1;
        segment.y1[2]! += 1;
      }
      c.state[2]! += 1;
    },
  ]) {
    const invalid = structuredClone(checkpoint);
    mutate(invalid);
    const events = [];
    for await (const e of execute({
      runId: 'bad',
      mode: 'envelope',
      scenario: s,
      until: 2,
      resume: invalid,
    }))
      events.push(e);
    const last = events.at(-1);
    assert.ok(last?.type === 'failed');
    assert.equal(last.error.code, 'INVALID_HISTORY');
  }
});

test('checkpoint restore rejects valid RK4 half-steps that fail adaptive acceptance', () => {
  const s = driven();
  s.solver.step = 0.2;
  s.solver.absoluteTolerance = 1e-15;
  s.solver.relativeTolerance = 1e-15;
  const solver = new EnvelopeSolver(s),
    rk4 = (
      solver as unknown as {
        rk4(t: number, y: number[], end: number, left: boolean): DenseSegment;
      }
    ).rk4.bind(solver),
    snapshot = solver.snapshot(),
    first = rk4(0, snapshot.state, 0.1, false),
    second = rk4(first.end, first.y1, 0.2, true);
  snapshot.time = second.end;
  snapshot.state = second.y1;
  snapshot.segments = [first, second];
  snapshot.attempts = [{ end: second.end, accepted: true }];
  snapshot.acceptedSteps = 1;
  assert.throws(
    () => new EnvelopeSolver(s, {}, snapshot),
    (error: unknown) =>
      error instanceof Error &&
      'code' in error &&
      error.code === 'INVALID_HISTORY' &&
      error.message.includes('adaptive controller replay'),
  );
});

test('checkpoint restore rejects RK4 pairs that cross scheduled boundaries', () => {
  const s = driven();
  s.solver.step = 0.2;
  s.solver.absoluteTolerance = 1000;
  s.solver.relativeTolerance = 1000;
  const options: EnvelopeOptions = {
      boundaryInputs: {
        left: [
          { time: 0, rate: 0 },
          { time: 0.08, rate: 1.3 },
        ],
      },
    },
    solver = new EnvelopeSolver(s, options),
    rk4 = (
      solver as unknown as {
        rk4(t: number, y: number[], end: number, left: boolean): DenseSegment;
      }
    ).rk4.bind(solver),
    snapshot = solver.snapshot(),
    first = rk4(0, snapshot.state, 0.1, false),
    second = rk4(first.end, first.y1, 0.2, true);
  snapshot.time = second.end;
  snapshot.state = second.y1;
  snapshot.segments = [first, second];
  snapshot.attempts = [{ end: second.end, accepted: true }];
  snapshot.acceptedSteps = 1;
  assert.throws(
    () => new EnvelopeSolver(s, options, snapshot),
    (error: unknown) =>
      error instanceof Error &&
      'code' in error &&
      error.code === 'INVALID_HISTORY' &&
      error.message.includes('scheduled solver boundary'),
  );
});

test('checkpoint restore rejects adaptive mesh growth unavailable to the controller', () => {
  const s = isolated();
  s.solver.step = 0.2;
  s.solver.absoluteTolerance = 1000;
  s.solver.relativeTolerance = 1000;
  const solver = new EnvelopeSolver(s),
    rk4 = (
      solver as unknown as {
        rk4(t: number, y: number[], end: number, left: boolean): DenseSegment;
      }
    ).rk4.bind(solver),
    snapshot = solver.snapshot(),
    first = rk4(0, snapshot.state, 0.0005, false),
    second = rk4(first.end, first.y1, 0.001, true),
    third = rk4(second.end, second.y1, second.end + 0.05, false),
    fourth = rk4(third.end, third.y1, second.end + 0.1, true);
  snapshot.time = fourth.end;
  snapshot.state = fourth.y1;
  snapshot.segments = [first, second, third, fourth];
  snapshot.attempts = [
    { end: second.end, accepted: true },
    { end: fourth.end, accepted: true },
  ];
  snapshot.acceptedSteps = 2;
  assert.throws(
    () => new EnvelopeSolver(s, {}, snapshot),
    (error: unknown) =>
      error instanceof Error &&
      'code' in error &&
      error.code === 'INVALID_HISTORY' &&
      error.message.includes('adaptive step-size growth'),
  );
});

test('checkpoint restore rejects an impossible saved next-step proposal', () => {
  const s = isolated();
  s.solver.step = 0.2;
  s.solver.absoluteTolerance = 1000;
  s.solver.relativeTolerance = 1000;
  const solver = new EnvelopeSolver(s),
    rk4 = (
      solver as unknown as {
        rk4(t: number, y: number[], end: number, left: boolean): DenseSegment;
      }
    ).rk4.bind(solver),
    snapshot = solver.snapshot(),
    first = rk4(0, snapshot.state, 0.0005, false),
    second = rk4(first.end, first.y1, 0.001, true);
  snapshot.time = second.end;
  snapshot.state = second.y1;
  snapshot.segments = [first, second];
  snapshot.attempts = [{ end: second.end, accepted: true }];
  snapshot.acceptedSteps = 1;
  snapshot.nextStep = 0.2;
  assert.throws(
    () => new EnvelopeSolver(s, {}, snapshot),
    (error: unknown) =>
      error instanceof Error &&
      'code' in error &&
      error.code === 'INVALID_HISTORY' &&
      error.message.includes('adaptive controller replay'),
  );
});

test('checkpoint restore rejects counters beyond the lifetime attempt budget', () => {
  const s = isolated(),
    options: EnvelopeOptions = { maxSteps: 1 },
    snapshot = new EnvelopeSolver(s, options).snapshot();
  snapshot.rejectedSteps = 2;
  assert.throws(
    () => new EnvelopeSolver(s, options, snapshot),
    (error: unknown) =>
      error instanceof Error &&
      'code' in error &&
      error.code === 'INVALID_HISTORY' &&
      error.message.includes('attempt budget'),
  );
});

test('checkpoint restore rejects rejection counters without a replayable controller attempt', () => {
  const s = isolated(),
    options: EnvelopeOptions = { maxSteps: 1 },
    snapshot = new EnvelopeSolver(s, options).snapshot();
  snapshot.rejectedSteps = 1;
  snapshot.attempts = [{ end: snapshot.nextStep, accepted: false }];
  assert.throws(
    () => new EnvelopeSolver(s, options, snapshot),
    (error: unknown) =>
      error instanceof Error &&
      'code' in error &&
      error.code === 'INVALID_HISTORY' &&
      error.message.includes('next step'),
  );
});

test('checkpoint restore replays a genuine rejected adaptive attempt', () => {
  const s = driven();
  s.solver.step = 0.2;
  s.solver.absoluteTolerance = 1e-15;
  s.solver.relativeTolerance = 1e-15;
  const solver = new EnvelopeSolver(s);
  solver.advance(0.2);
  const snapshot = solver.snapshot();
  assert.equal(snapshot.acceptedSteps, 0);
  assert.equal(snapshot.rejectedSteps, 1);
  assert.deepEqual(new EnvelopeSolver(s, {}, snapshot).snapshot(), snapshot);
});

test('checkpoint restore tolerates portable last-bit replay differences', async () => {
  const s = createSample('pair'),
    checkpoint = (await run(s, 0.3)).snapshot,
    difference = 1e-14;
  for (const segment of checkpoint.segments) {
    segment.d0[1]! += difference;
    segment.d1[1]! -= difference;
  }
  assert.doesNotThrow(() => new EnvelopeSolver(s, {}, checkpoint));
});

test('checkpoint restore tolerates a last-bit acceptance-threshold flip', () => {
  const s = isolated();
  s.solver.absoluteTolerance = 1000;
  s.solver.relativeTolerance = 1000;
  const source = new EnvelopeSolver(s);
  source.advance(0.001);
  const checkpoint = source.snapshot(),
    restorer = new EnvelopeSolver(s),
    internals = restorer as unknown as {
      adaptiveError(): number;
      proposedStep(): number;
      restore(value: unknown): void;
    };
  internals.adaptiveError = () => 1 + 5e-13;
  internals.proposedStep = () => checkpoint.nextStep;
  assert.doesNotThrow(() => internals.restore(checkpoint));
});

test('checkpoint restore rejects cumulative sub-threshold RK4 increment changes', async () => {
  const s = createSample('pair'),
    checkpoint = (await run(s, 1.7)).snapshot,
    increment = 1e-11;
  let offset = 0;
  for (const segment of checkpoint.segments) {
    segment.y0[2]! += offset;
    offset += increment;
    segment.y1[2]! += offset;
  }
  checkpoint.state[2]! += offset;
  assert.throws(
    () => new EnvelopeSolver(s, {}, checkpoint),
    (error: unknown) =>
      error instanceof Error &&
      'code' in error &&
      error.code === 'INVALID_HISTORY' &&
      error.message.includes('state increments'),
  );
});

test('reflection exchanges ports, adds pi, and preserves R2 histories and total emissions', async () => {
  const s = createSample('pair');
  s.nodes.forEach((n) => {
    n.response = 'R2';
  });
  s.nodes[1]!.gain = -0.15;
  const reflected = structuredClone(s);
  reflected.nodes.reverse().forEach((n) => {
    n.position = -n.position;
    n.phi += Math.PI;
    reflected.initialHistory.nodes[n.id]!.phiAtZero += Math.PI;
  });
  reflected.links.forEach((l) => {
    l.sourcePort = l.sourcePort === 'left' ? 'right' : 'left';
    l.targetPort = l.targetPort === 'left' ? 'right' : 'left';
  });
  const [a, b] = await Promise.all([run(s, 2), run(reflected, 2)]);
  for (const n of s.nodes) {
    const x = a.last.nodes[n.id]!,
      y = b.last.nodes[n.id]!;
    close(y.phi, x.phi + Math.PI);
    close(y.omega, x.omega);
    close(y.integratedLeft, x.integratedRight);
    close(y.rhoRight, x.rhoLeft);
  }
});

test('piecewise inputs and gain changes use exact discontinuity boundaries without phase resets', async () => {
  const s = driven(),
    n = s.nodes[0]!;
  s.boundaries.left = { kind: 'driven', rate: 0 };
  s.interventions = [
    {
      time: 0.333,
      kind: 'change-parameter',
      target: n.id,
      value: { gain: -0.25 },
    },
  ];
  const r = await run(s, 1, {
    boundaryInputs: {
      left: [
        { time: 0, rate: 0 },
        { time: 0.137, rate: 1.3 },
        { time: 0.731, rate: 0 },
      ],
    },
  });
  for (const t of [0.137, 0.333, 0.731])
    assert.ok(r.samples.some((p) => p.time === t));
  let phi = n.phi,
    omega = n.omega,
    previous = 0;
  for (const [end, gain, rate] of [
    [0.137, 0.5, 0],
    [0.333, 0.5, 1.3],
    [0.731, -0.25, 1.3],
    [1, -0.25, 0],
  ]) {
    const dt = end! - previous,
      target = n.omega0 + gain! * Math.tanh(rate!);
    phi +=
      target * dt +
      (omega - target) *
        n.relaxationTime *
        (1 - Math.exp(-dt / n.relaxationTime));
    omega = target + (omega - target) * Math.exp(-dt / n.relaxationTime);
    previous = end!;
    const sample = r.samples.find((p) => p.time === end)!;
    close(sample.nodes[n.id]!.phi, phi);
    close(sample.nodes[n.id]!.omega, omega);
  }
});

test('sampled prehistory uses phase Hermite derivative and rejects hidden between-knot frequency violations', async () => {
  const s = createSample('pair');
  const points = [-1, 0].map((time) => ({
    time,
    nodes: Object.fromEntries(
      s.nodes.map((n) => [
        n.id,
        { phi: n.phi + n.omega * time, omega: n.omega },
      ]),
    ),
  }));
  const a = await run(s, 0.3),
    b = await run(s, 0.3, { prehistory: points });
  close(a.last.nodes['A']!.phi, b.last.nodes['A']!.phi, 1e-12);
  points[0]!.nodes['A']!.phi -= 2;
  const events = [];
  for await (const e of execute({
    runId: 'bad-history',
    mode: 'envelope',
    scenario: s,
    until: 1,
    envelope: { prehistory: points },
  }))
    events.push(e);
  const last = events.at(-1);
  assert.ok(last?.type === 'failed');
  assert.equal(last.error.code, 'INVALID_HISTORY');
});

test('prehistory uses gain bounds immediately before a time-zero intervention', async () => {
  const s = createSample('pair'),
    changed = s.nodes[0]!,
    start = s.initialHistory.startTime,
    duration = -start,
    historyOmega = changed.omega0 + Math.abs(changed.gain) + 0.1;
  s.interventions = [
    {
      time: 0,
      kind: 'change-parameter',
      target: changed.id,
      value: { gain: Math.abs(changed.gain) + 0.2 },
    },
  ];
  const points = [
    {
      time: start,
      nodes: Object.fromEntries(
        s.nodes.map((node) => [
          node.id,
          node.id === changed.id
            ? {
                phi: node.phi - ((historyOmega + node.omega) * duration) / 2,
                omega: historyOmega,
              }
            : {
                phi: node.phi + node.omega * start,
                omega: node.omega,
              },
        ]),
      ),
    },
    {
      time: 0,
      nodes: Object.fromEntries(
        s.nodes.map((node) => [node.id, { phi: node.phi, omega: node.omega }]),
      ),
    },
  ];
  const events: RunEvent[] = [];
  for await (const event of execute({
    runId: 'time-zero-history-bounds',
    mode: 'envelope',
    scenario: s,
    until: 0.1,
    envelope: { prehistory: points },
  }))
    events.push(event);
  const last = events.at(-1);
  assert.ok(last?.type === 'failed');
  assert.equal(last.error.code, 'INVALID_HISTORY');
});

test('segments ending at gain changes use left-limit bounds', () => {
  const s = createSample('isolated'),
    node = s.nodes[0]!;
  node.gain = 0.2;
  node.response = 'R1';
  s.interventions = [
    {
      time: 1,
      kind: 'change-parameter',
      target: node.id,
      value: { gain: 0.8 },
    },
  ];
  const segment: DenseSegment = {
    start: 0,
    end: 1,
    y0: [0, 2.1, 0, 0],
    y1: [2.1, 2.1, 1, 1],
    d0: [2.1, 1, 1, 1],
    d1: [2.1, -1, 1, 1],
  };
  const solver = new EnvelopeSolver(s),
    validSegment = (
      solver as unknown as {
        validSegment(candidate: DenseSegment): boolean;
      }
    ).validSegment.bind(solver);
  assert.equal(validSegment(segment), false);
});

test('dense intensity history cannot decrease between increasing endpoints', () => {
  const s = isolated(),
    solver = new EnvelopeSolver(s),
    validSegment = (
      solver as unknown as {
        validSegment(candidate: DenseSegment): boolean;
      }
    ).validSegment.bind(solver),
    segment: DenseSegment = {
      start: 0,
      end: 1,
      y0: [0, 2, 0, 0],
      y1: [2, 2, 1, 1],
      d0: [2, 0, 10, 10],
      d1: [2, 0, 10, 10],
    };
  assert.ok(segment.y1[2]! >= segment.y0[2]!);
  assert.ok(segment.y1[3]! >= segment.y0[3]!);
  assert.equal(validSegment(segment), false);
});

test('unsupported physics and exhausted error control fail structurally without clipping', async () => {
  for (const [mutate, code] of [
    [
      (s: Scenario) => {
        s.solver.method = 'dopri5';
      },
      'UNSUPPORTED_MODEL',
    ],
    [
      (s: Scenario) => {
        s.initialHistory.filters[s.nodes[0]!.id]!.left = 1;
      },
      'UNSUPPORTED_MODEL',
    ],
    [
      (s: Scenario) => {
        s.solver.absoluteTolerance = 0;
      },
      'INVALID_REQUEST',
    ],
  ] as const) {
    const s = driven();
    mutate(s);
    const events = [];
    for await (const e of execute({
      runId: 'failure',
      mode: 'envelope',
      scenario: s,
      until: 1,
    }))
      events.push(e);
    const last = events.at(-1);
    assert.ok(last?.type === 'failed');
    assert.ok([code, 'INVALID_SCENARIO'].includes(last.error.code));
  }
  const events = [];
  for await (const e of execute({
    runId: 'budget',
    mode: 'envelope',
    scenario: driven(),
    until: 2,
    envelope: { maxSteps: 1 },
  }))
    events.push(e);
  const last = events.at(-1);
  assert.ok(last?.type === 'failed');
  assert.equal(last.error.code, 'NUMERICAL_FAILURE');
});

test('non-finite envelope option values fail at the request boundary', async () => {
  const s = createSample('pair'),
    point = (time: number) => ({
      time,
      nodes: Object.fromEntries(
        s.nodes.map((node) => [
          node.id,
          { phi: node.phi + node.omega * time, omega: node.omega },
        ]),
      ),
    }),
    invalidOptions: EnvelopeOptions[] = [
      { tickSection: Number.NaN },
      { maxSteps: Number.POSITIVE_INFINITY },
      {
        boundaryInputs: {
          left: [
            { time: 0, rate: 1 },
            { time: Number.NaN, rate: 2 },
          ],
        },
      },
      {
        boundaryInputs: { left: [{ time: 0, rate: Number.POSITIVE_INFINITY }] },
      },
      {
        prehistory: [point(s.initialHistory.startTime), point(0)],
      },
    ];
  invalidOptions.at(-1)!.prehistory![0]!.nodes[s.nodes[0]!.id]!.phi =
    Number.NaN;
  for (const envelope of invalidOptions) {
    const events: RunEvent[] = [];
    for await (const event of execute({
      runId: 'non-finite-options',
      mode: 'envelope',
      scenario: s,
      until: 0.1,
      envelope,
    }))
      events.push(event);
    const last = events.at(-1);
    assert.ok(last?.type === 'failed');
    assert.equal(last.error.code, 'INVALID_REQUEST');
  }
});

test('unrepresentable initial tick indices fail before exposing a sample', async () => {
  const s = isolated(),
    node = s.nodes[0]!;
  node.phi = 1e20;
  s.initialHistory.nodes[node.id]!.phiAtZero = node.phi;
  const events: RunEvent[] = [];
  for await (const event of execute({
    runId: 'unsafe-ticks',
    mode: 'envelope',
    scenario: s,
    until: 0,
  }))
    events.push(event);
  assert.ok(!events.some((event) => event.type === 'envelope-sample'));
  const last = events.at(-1);
  assert.ok(last?.type === 'failed');
  assert.equal(last.error.code, 'NUMERICAL_FAILURE');
});

test('worker envelope cancellation emits a resumable checkpoint and no completion', async () => {
  const events: RunEvent[] = [];
  const handle = createWorkerHandler((e) => {
    events.push(structuredClone(e));
    if (e.type === 'envelope-sample' && e.sample.time > 0)
      void handle({ type: 'cancel', runId: 'worker' });
  });
  await handle({
    type: 'run',
    request: {
      runId: 'worker',
      mode: 'envelope',
      scenario: driven(),
      until: 3,
    },
  });
  assert.equal(events.at(-1)?.type, 'cancelled');
  assert.ok(
    events.some((e) => e.type === 'envelope-snapshot' && e.snapshot.time > 0),
  );
  assert.ok(!events.some((e) => e.type === 'completed'));
});

test('nonlinear retarded source history converges against independent convolution quadrature', async () => {
  const s = createSample('pair'),
    source = s.nodes[0]!,
    receiver = s.nodes[1]!;
  source.gain = 0.5;
  source.response = 'R1';
  s.boundaries.left = { kind: 'driven', rate: 1.3 };
  receiver.position = 0.137;
  s.links = s.links.filter((l) => l.source === source.id);
  s.links[0]!.delay = 0.137;
  const until = 1.3,
    delay = 0.137;
  const target = source.omega0 + source.gain * Math.tanh(1.3 / s.rateScale);
  const forcing = (time: number) => {
    const z = time - delay;
    const omega =
      z <= 0
        ? source.omega
        : target +
          (source.omega - target) * Math.exp(-z / source.relaxationTime);
    const phi =
      z <= 0
        ? source.phi + source.omega * z
        : source.phi +
          target * z +
          (source.omega - target) *
            source.relaxationTime *
            (1 - Math.exp(-z / source.relaxationTime));
    const rate = ((3 * omega) / (4 * Math.PI)) * (1 + Math.cos(phi));
    return (
      (receiver.gain *
        Math.tanh(rate / s.rateScale) *
        Math.exp(-(until - time) / receiver.relaxationTime)) /
      receiver.relaxationTime
    );
  };
  // Composite Simpson convolution, independently split at the source startup delay.
  const integrate = (a: number, b: number) => {
    const count = 4000,
      h = (b - a) / count;
    let total = forcing(a) + forcing(b);
    for (let i = 1; i < count; i++)
      total += (i % 2 ? 4 : 2) * forcing(a + i * h);
    return (h * total) / 3;
  };
  const expected =
    receiver.omega0 + integrate(0, delay) + integrate(delay, until);
  const errors: number[] = [];
  for (const step of [0.12, 0.06, 0.03]) {
    s.solver = {
      method: 'rk4',
      step,
      absoluteTolerance: 1e-3,
      relativeTolerance: 1e-3,
    };
    const result = await run(s, until);
    errors.push(Math.abs(result.last.nodes[receiver.id]!.omega - expected));
  }
  assert.ok(
    errors[1]! < errors[0]! / 4 && errors[2]! < errors[1]! / 4,
    `${errors}`,
  );
  assert.ok(errors[2]! < 1e-8, `${errors}`);
});
