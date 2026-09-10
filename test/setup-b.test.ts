import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  createSetupBDefinition,
  createSetupBProtocol,
  createSetupBScenario,
  createSetupBGainSweep,
  createSetupBSmokeDefinitions,
  runSetupB,
  setupBVariants,
} from '@signal-space/experiments';
import { EnvelopeSolver } from '@signal-space/sim';
import { validateDefinition } from '@signal-space/experiments';

const close = (actual: number, expected: number, tolerance = 1e-8) =>
  assert.ok(
    Math.abs(actual - expected) <= tolerance,
    `${actual} != ${expected} (tol ${tolerance})`,
  );

test('Setup B runs every E/R variant under both symmetric preparations', () => {
  for (const preparation of ['co-phase', 'pi-reflection'] as const) {
    const protocol = createSetupBProtocol('reciprocal', {
      preparation,
      duration: 4,
      preparationDuration: 1,
      perturbation: null,
    });
    for (const variant of setupBVariants) {
      const result = runSetupB(protocol, variant.id);
      assert.ok(result.samples.length > 2);
      assert.equal(result.protocol.preparation.id, preparation);
      assert.equal(result.protocol.routes.length, 2);
      assert.equal(
        result.diagnostics.retardedPhase.aFromB.length,
        result.samples.length,
      );
      assert.equal(
        result.diagnostics.retardedPhase.bFromA.length,
        result.samples.length,
      );
      assert.ok(Number.isFinite(result.diagnostics.meanFrequencyDifference));
      assert.ok(Number.isFinite(result.diagnostics.phase.unwrappedDrift));
    }
  }
});

test('Setup B R0 preserves the analytic uncoupled continuation', () => {
  const protocol = createSetupBProtocol('reciprocal', {
    preparation: 'pi-reflection',
    duration: 3,
    preparationDuration: 1,
    perturbation: null,
  });
  const result = runSetupB(protocol, 'E0-R0');
  for (const sample of result.samples) {
    close(sample.nodes.A!.omega, 2);
    close(sample.nodes.B!.omega, 2);
    close(sample.nodes.A!.phi, protocol.preparation.phaseA + 2 * sample.time);
    close(sample.nodes.B!.phi, protocol.preparation.phaseB + 2 * sample.time);
  }
  close(result.diagnostics.meanFrequencyDifference, 0);
});

test('Setup B default phase perturbation is admissible for zero gain', () => {
  const result = runSetupB(
    createSetupBProtocol('reciprocal', { duration: 3, preparationDuration: 1 }),
    'E0-R0',
  );
  assert.equal(result.variant.gain, 0);
  close(result.diagnostics.meanFrequencyDifference, 0);
  close(result.diagnostics.phase.unwrappedDrift, 0);
  close(result.diagnostics.phase.appliedPairPhaseOffset, -0.15);
  assert.equal(result.diagnostics.recovery?.displaced, true);
  assert.ok(result.diagnostics.recovery);
});

test('Setup B defaults remain valid for short protocols and R0 sweeps', () => {
  const short = createSetupBProtocol('reciprocal', {
    duration: 1,
    preparationDuration: 0.75,
  });
  assert.equal(short.perturbation?.time, 5 / 6);
  const sweep = createSetupBGainSweep(
    createSetupBProtocol('reciprocal', { perturbation: null }),
    'E0-R0',
  );
  assert.deepEqual(
    sweep.points.map((point) => point.gain),
    [0],
  );
});

test('Setup B validates finite overrides, durations, and perturbation nodes', () => {
  const protocol = createSetupBProtocol('reciprocal', {
    duration: 3,
    preparationDuration: 1,
    perturbation: null,
  });
  assert.throws(
    () => createSetupBScenario(protocol, 'E1-R1', { gain: Number.NaN }),
    /finite/,
  );
  assert.throws(
    () => createSetupBProtocol('reciprocal', { duration: Infinity }),
    /finite/,
  );
  assert.throws(
    () =>
      createSetupBProtocol('reciprocal', {
        perturbation: {
          time: 2.5,
          nodeId: 'missing',
          phaseOffset: 0,
          frequencyOffset: 0,
        },
      }),
    /target node A or B/,
  );
});

test('E0 with zero amplitude and R1 does not manufacture phase restoration', () => {
  const protocol = createSetupBProtocol('reciprocal', {
    preparation: 'small-offset',
    amplitude: 0,
    duration: 3,
    preparationDuration: 1,
    perturbation: null,
  });
  const result = runSetupB(protocol, 'E0-R1');
  const initial = result.diagnostics.phase.initialUnwrapped;
  close(result.diagnostics.phase.finalUnwrapped, initial, 2e-7);
  close(result.diagnostics.meanFrequencyDifference, 0, 2e-7);
});

test('Setup B keeps reciprocal, one-way, and prescribed controls distinct', () => {
  const reciprocal = createSetupBProtocol('reciprocal', { perturbation: null });
  const oneWay = createSetupBProtocol('one-way-a-to-b', { perturbation: null });
  const prescribed = createSetupBProtocol('prescribed-drive', {
    perturbation: null,
  });
  assert.notEqual(reciprocal.id, oneWay.id);
  assert.notEqual(oneWay.id, prescribed.id);
  assert.deepEqual(
    oneWay.routes.map((route) => route.id),
    ['A-B'],
  );
  assert.deepEqual(prescribed.routes, []);
  assert.equal(prescribed.prescribedRate, 0.75);
  assert.equal(
    runSetupB(oneWay, 'E1-R1').diagnostics.retardedPhase.aFromB.length,
    0,
  );
  assert.equal(
    runSetupB(prescribed, 'E1-R1').diagnostics.retardedPhase.bFromA.length,
    0,
  );
  assert.equal(
    runSetupB(prescribed, 'E1-R1').diagnostics.classification.evidence.length,
    1,
  );
});

test('Setup B gain sweep records signed values through zero without a locking claim', () => {
  const sweep = createSetupBGainSweep(
    createSetupBProtocol('reciprocal', { duration: 3, perturbation: null }),
    'E1-R1',
    [-0.4, 0, 0.4],
  );
  assert.deepEqual(
    sweep.points.map((point) => point.gain),
    [-0.4, 0, 0.4],
  );
  assert.equal(sweep.controls.includesZeroGain, true);
  assert.equal(sweep.controls.signedGain, true);
  assert.equal(sweep.controls.interpretation, 'deferred');
  assert.ok(sweep.points.every((point) => Number.isFinite(point.phaseDrift)));
  assert.equal(
    runSetupB(protocolValueForSweep(), 'E1-R1', { gain: -0.4 }).variant.gain,
    -0.4,
  );
});

function protocolValueForSweep() {
  return createSetupBProtocol('reciprocal', {
    duration: 3,
    perturbation: null,
  });
}

test('Setup B perturbations land at preparation boundaries and replay with history', () => {
  const protocol = createSetupBProtocol('reciprocal', {
    duration: 4,
    preparationDuration: 1,
    perturbation: {
      time: 1.5,
      nodeId: 'B',
      phaseOffset: 0.15,
      frequencyOffset: 0.04,
    },
  });
  const scenario = createSetupBScenario(protocol, 'E1-R1');
  const result = runSetupB(protocol, 'E1-R1');
  const solver = new EnvelopeSolver(scenario, result.envelope);
  while (solver.time < 2) solver.advance(2);
  const checkpoint = solver.snapshot();
  assert.equal(checkpoint.jumps.length, 1);
  const shifted = structuredClone(checkpoint);
  shifted.jumps[0]!.time += 5e-13;
  assert.throws(
    () => new EnvelopeSolver(scenario, result.envelope, shifted),
    /perturbation history/,
  );
  const resumed = new EnvelopeSolver(scenario, result.envelope, checkpoint);
  while (resumed.time < protocol.duration) resumed.advance(protocol.duration);
  assert.deepEqual(resumed.snapshot().jumps, checkpoint.jumps);
  assert.ok(
    Math.abs(
      result.samples.at(-1)!.nodes.B!.phi -
        result.referenceSamples.at(-1)!.nodes.B!.phi,
    ) > 0.1,
  );
});

test('Setup B rejects phase jumps beyond the tick crossing output cap', () => {
  const protocol = createSetupBProtocol('reciprocal', {
    duration: 2,
    preparationDuration: 0.5,
    perturbation: {
      time: 1,
      nodeId: 'B',
      phaseOffset: 1e9,
      frequencyOffset: 0,
    },
  });
  const solver = new EnvelopeSolver(createSetupBScenario(protocol, 'E0-R1'), {
    preparation: 'established',
    perturbations: [protocol.perturbation!],
  });
  assert.throws(() => {
    while (solver.time < protocol.duration) solver.advance(protocol.duration);
  }, /per-step output limits/);
});

test('Setup B phase jumps emit directed tick crossings', () => {
  const protocol = createSetupBProtocol('reciprocal', {
    duration: 2,
    preparationDuration: 0.5,
    perturbation: {
      time: 1,
      nodeId: 'B',
      phaseOffset: 2 * Math.PI,
      frequencyOffset: 0,
    },
  });
  const scenario = createSetupBScenario(protocol, 'E0-R1');
  const solver = new EnvelopeSolver(scenario, {
    preparation: 'established',
    perturbations: [protocol.perturbation!],
  });
  const crossings = [];
  while (solver.time < protocol.duration)
    crossings.push(...solver.advance(protocol.duration));
  assert.ok(
    crossings.some(
      (crossing) =>
        crossing.nodeId === 'B' &&
        crossing.time === 1 &&
        crossing.direction === 1,
    ),
  );
});

test('Setup B rejects perturbations merged by canonical boundary time', () => {
  const protocol = createSetupBProtocol('reciprocal', {
    perturbation: null,
  });
  const scenario = createSetupBScenario(protocol, 'E0-R1');
  assert.throws(
    () =>
      new EnvelopeSolver(scenario, {
        perturbations: [
          { time: 0.3, nodeId: 'B', phaseOffset: 0, frequencyOffset: 0 },
          {
            time: 0.1 + 0.2,
            nodeId: 'B',
            phaseOffset: 0,
            frequencyOffset: 0,
          },
        ],
      }),
    /at most one perturbation/,
  );
});

test('Setup B definitions are shared-API schema-compatible', async () => {
  const definitions = createSetupBSmokeDefinitions();
  assert.equal(definitions.length, 12);
  for (const definition of definitions) {
    assert.doesNotThrow(() => validateDefinition(definition));
    assert.equal(definition.mode, 'envelope');
  }
  const edited = createSetupBDefinition(
    'prescribed-drive',
    'E0-R2',
    'pi-reflection',
  );
  assert.equal(
    edited.scenario.id,
    'setup-b-prescribed-drive-E0-R2-pi-reflection',
  );
  assert.equal(edited.envelope?.boundaryInputs?.right?.[0]?.rate, 0.75);
  assert.equal(edited.envelope?.perturbations?.[0]?.nodeId, 'B');
  const invalid = structuredClone(edited);
  invalid.envelope!.perturbations![0]!.nodeId = 'missing';
  assert.throws(() => validateDefinition(invalid), /unknown node/);
});
