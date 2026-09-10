import assert from 'node:assert/strict';
import test from 'node:test';
import {
  aggregateReplicates,
  circularCoherence,
  classifyPair,
  meanFrequency,
  receptionInventory,
  responseFront,
  retardedPhase,
  slipCount,
  spatialCorrelation,
  tickChange,
} from '@signal-space/analysis';
const series = (wa: number, wb: number, offset = 0) => ({
  samples: Array.from({ length: 21 }, (_, i) => ({
    time: i,
    nodes: {
      a: {
        phi: wa * i + offset,
        omega: wa,
        receptionLeft: i,
        receptionRight: 2 * i,
      },
      b: { phi: wb * i, omega: wb },
    },
  })),
});
const criteria = {
  transientEnd: 0,
  windows: [
    { start: 0, end: 10 },
    { start: 0, end: 20 },
  ],
  frequencyTolerance: 1e-10,
  phaseRangeTolerance: 0.1,
  minimumCycles: 1,
};
test('analytic phase advance, signed slips, and reception inventory', () => {
  const samples = series(2, 1).samples;
  assert.equal(meanFrequency(samples, 'a'), 2);
  assert.equal(slipCount(samples.map((s) => s.nodes.a.phi - s.nodes.b.phi)), 3);
  assert.equal(slipCount([6, 7]), 1);
  assert.deepEqual(receptionInventory(samples.slice(0, 2), 'a')[1], {
    time: 1,
    left: 1,
    right: 2,
    sum: 3,
    difference: 1,
  });
  assert.equal(
    classifyPair(series(2, 1), 'a', 'b', criteria).status,
    'slipping',
  );
});
test('tick totals and spatial correlations use saved physical records', () => {
  const samples = [
    {
      time: 0,
      nodes: {
        a: { phi: 0, omega: 1, ticks: 2 },
        b: { phi: 1, omega: 1, ticks: 4 },
      },
    },
    {
      time: 1,
      nodes: {
        a: { phi: 1, omega: 1, ticks: 3 },
        b: { phi: 3, omega: 1, ticks: 6 },
      },
    },
  ];
  assert.equal(tickChange(samples, 'b'), 2);
  assert.ok(
    Math.abs(spatialCorrelation(samples[0]!, samples[1]!, ['a', 'b'])! - 1) <
      1e-14,
  );
});
test('persistent equal-frequency offset is only a frequency candidate without recovery', () => {
  const result = classifyPair(series(1, 1, 0.25), 'a', 'b', criteria);
  assert.equal(result.status, 'candidate-frequency-locking');
  assert.match(result.definition, /not claimed/);
});
test('perturbation recovery promotes phase candidate while modulation is allowed', () => {
  const input = series(1, 1, 0.02);
  input.samples.forEach((s, i) => {
    s.nodes.a.omega = 1 + 0.2 * Math.sin(i);
    s.nodes.b.omega = 1 + 0.2 * Math.sin(i);
    if (i === 6) s.nodes.a.phi += 0.08;
    if (i === 7) s.nodes.a.phi += 0.04;
  });
  const result = classifyPair(input, 'a', 'b', {
    ...criteria,
    perturbation: { time: 5, recoveryTolerance: 0.05, referenceOffset: 0 },
  });
  assert.equal(result.status, 'candidate-phase-locking');
  assert.equal(result.perturbationRecovery?.displaced, true);
  assert.ok(result.evidence[0]!.frequencyModulation.a!.maximum > 1);
});
test('unchanged offsets do not count as perturbation recovery', () => {
  const result = classifyPair(series(1, 1, 0.02), 'a', 'b', {
    ...criteria,
    perturbation: { time: 5, recoveryTolerance: 0.05, referenceOffset: 0 },
  });
  assert.equal(result.status, 'candidate-frequency-locking');
  assert.equal(result.perturbationRecovery?.demonstrated, false);
});
test('perturbation recovery requires exact matched reference samples', () => {
  assert.throws(
    () =>
      classifyPair(series(1, 1), 'a', 'b', {
        ...criteria,
        perturbation: {
          time: 5,
          recoveryTolerance: 0.05,
          referenceOffset: 0,
          reference: {
            samples: series(1, 1).samples.filter((sample) =>
              [0, 10, 20].includes(sample.time),
            ),
          },
        },
      }),
    /exact sample/,
  );
});
test('uncovered and non-nested windows cannot produce candidates', () => {
  assert.equal(
    classifyPair(series(1, 1), 'a', 'b', {
      ...criteria,
      windows: [{ start: 0, end: 100 }],
    }).status,
    'unresolved',
  );
  assert.throws(
    () =>
      classifyPair(series(1, 1), 'a', 'b', {
        ...criteria,
        windows: [
          { start: 0, end: 20 },
          { start: 0, end: 10 },
        ],
      }),
    /ordered shortest to longest/,
  );
});
test('short windows and failures remain unresolved or failed', () => {
  assert.equal(
    classifyPair(series(1, 1), 'a', 'b', { ...criteria, minimumCycles: 100 })
      .status,
    'unresolved',
  );
  assert.equal(
    classifyPair(
      { samples: [], failed: { code: 'STEP', message: 'bad' } },
      'a',
      'b',
      criteria,
    ).status,
    'numerically-failed',
  );
});
test('retarded phase labels simulator access unless protocol declares it', () => {
  const receiver = [{ time: 2, phi: 4 }],
    source = [{ time: 2, sourceTime: 1, phi: 1 }];
  assert.equal(
    retardedPhase(receiver, source, 0.5)[0]!.access,
    'simulator-only',
  );
  assert.equal(
    retardedPhase(receiver, source, 0.5, true)[0]!.access,
    'observer-protocol',
  );
});
test('replicate interval retains runs and treats runs as independent', () => {
  const result = aggregateReplicates([
    { runId: 'r1', seed: '1', preparationId: 'p', value: 1, sampleCount: 100 },
    { runId: 'r2', seed: '2', preparationId: 'p', value: 3, sampleCount: 200 },
  ]);
  assert.equal(result.mean, 2);
  assert.equal(result.seedCount, 2);
  assert.equal(result.sampleCount, 300);
  assert.equal(result.runs.length, 2);
  assert.match(result.dependence, /time-correlated/);
  assert.throws(
    () =>
      aggregateReplicates([
        {
          runId: 'duplicate-1',
          seed: 'same',
          preparationId: 'p',
          value: 1,
          sampleCount: 1,
        },
        {
          runId: 'duplicate-2',
          seed: 'same',
          preparationId: 'p',
          value: 2,
          sampleCount: 1,
        },
      ]),
    /seeds must be unique/,
  );
});
test('spatial caveat and causal response fronts remain explicit', () => {
  const sample = {
    time: 0,
    nodes: { a: { phi: 0, omega: 1 }, b: { phi: Math.PI, omega: 1 } },
  };
  assert.ok(circularCoherence(sample, ['a', 'b']).magnitude < 1e-12);
  const front = responseFront(
    [{ nodeId: 'b', position: 2, onsetTime: 1 }],
    { position: 0, time: 0 },
    1,
    0,
  );
  assert.equal(front[0]!.status, 'causality-violation');
  assert.equal(front[0]!.causalBound, 2);
  assert.throws(
    () =>
      responseFront(
        [{ nodeId: 'b', position: Number.NaN, onsetTime: 1 }],
        { position: 0, time: 0 },
        1,
        0,
      ),
    /must be finite/,
  );
  assert.throws(
    () =>
      responseFront(
        [{ nodeId: 'b', position: 2, onsetTime: 1 }],
        { position: 0, time: 0 },
        Number.POSITIVE_INFINITY,
        0,
      ),
    /finite and positive/,
  );
});
