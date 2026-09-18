import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  createSetupDDefinition,
  createSetupDSmokeDefinitions,
  runSetupD,
  runSetupDPreparationEnsemble,
  validateDefinition,
} from '@signal-space/experiments';

test('Setup D represents the A-B-C neighbor degrees and open outer ports', () => {
  const run = runSetupD({
    duration: 1,
    sampleCadence: 0.1,
    variant: 'E1-R0',
    gain: 0,
  });
  assert.equal(run.scenario.nodes.length, 3);
  assert.equal(
    run.scenario.links.filter((link) => link.target === 'B').length,
    2,
  );
  assert.equal(
    run.scenario.links.filter((link) => link.target === 'A').length,
    1,
  );
  assert.equal(
    run.scenario.links.filter((link) => link.target === 'C').length,
    1,
  );
  assert.deepEqual(run.scenario.boundaries, {
    left: { kind: 'open' },
    right: { kind: 'open' },
  });
  assert.equal(run.samples[0]!.nodes.B!.receptionLeft > 0, true);
  assert.equal(run.samples[0]!.nodes.B!.receptionRight > 0, true);
});

test('Setup D records the reflected C endpoint convention and admissible intrinsic boost', () => {
  const run = runSetupD({
    duration: 1,
    sampleCadence: 0.1,
    intervention: 'C',
    preparation: 'pi-reflection',
  });
  assert.equal(run.preparation.reflection.enabled, true);
  assert.equal(run.preparation.reflection.nodeMap.A, 'C');
  assert.equal(run.preparation.reflection.portMap.left, 'right');
  assert.equal(run.preparation.reflection.lobePhaseShift, Math.PI);
  assert.equal(run.scenario.nodes.find((node) => node.id === 'C')!.omega0, 2.2);
  assert.equal(
    run.scenario.nodes.every((node) => Math.abs(node.gain) < node.omega0),
    true,
  );
});

test('Setup D keeps physical and degree-normalized r-star as distinct conventions', () => {
  const fixed = runSetupD({
    duration: 1,
    sampleCadence: 0.1,
    variant: 'E1-R0',
    gain: 0,
  });
  const degree = runSetupD({
    duration: 1,
    sampleCadence: 0.1,
    variant: 'E1-R0',
    gain: 0,
    normalization: 'degree-normalized-r-star',
  });
  assert.equal(fixed.normalization.id, 'fixed-physical-r-star');
  assert.deepEqual(fixed.normalization.responseRateScales, {
    A: 1,
    B: 1,
    C: 1,
  });
  assert.deepEqual(degree.normalization.incomingDegrees, { A: 1, B: 2, C: 1 });
  assert.deepEqual(degree.normalization.responseRateScales, {
    A: 1,
    B: 2,
    C: 1,
  });
  assert.deepEqual(degree.envelope.responseRateScales, { A: 1, B: 2, C: 1 });
  assert.match(degree.normalization.isolatedNodeRule, /no division by degree/);
});

test('Setup D endpoint replay is a non-responsive receiver-only control preserving schedules', () => {
  const run = runSetupD({
    duration: 1,
    sampleCadence: 0.1,
    variant: 'E1-R0',
    gain: 0,
  });
  const replay = run.replayControl;
  assert.equal(replay.receiverScenario.nodes.length, 1);
  assert.equal(replay.receiverScenario.nodes[0]!.id, 'B');
  assert.deepEqual(replay.receiverScenario.links, []);
  assert.equal(
    replay.sources.every(
      (source) => source.respondsToReceiver === false && source.outputPreserved,
    ),
    true,
  );
  assert.deepEqual(
    replay.sources[0]!.output,
    replay.envelope.boundaryInputs!.left,
  );
  assert.deepEqual(
    replay.sources[1]!.output,
    replay.envelope.boundaryInputs!.right,
  );
});

test('Setup D preparation ensemble keeps independent declared phase preparations', () => {
  const ensemble = runSetupDPreparationEnsemble({
    duration: 1,
    sampleCadence: 0.1,
    variant: 'E1-R0',
    gain: 0,
    preparations: ['co-phase', 'small-offset', 'seeded-random'],
    preparationSeed: 'declared-seed',
  });
  assert.deepEqual(ensemble.preparationIds, [
    'co-phase',
    'small-offset',
    'seeded-random',
  ]);
  assert.deepEqual(
    ensemble.runs.map((run) => run.preparation.id),
    ensemble.preparationIds,
  );
  assert.equal(
    ensemble.runs[2]!.preparation.seed,
    'declared-seed:seeded-random',
  );
  assert.match(ensemble.limitations[0]!, /independent initial-state/);
});

test('Setup D exposes local metrics, retarded mismatches, propagation records, and shared definitions', () => {
  const run = runSetupD({
    duration: 1,
    sampleCadence: 0.1,
    variant: 'E1-R0',
    gain: 0,
  });
  for (const nodeId of ['A', 'B', 'C'] as const) {
    assert.equal(
      Number.isFinite(run.diagnostics.perNode[nodeId].meanFrequency),
      true,
    );
    assert.ok(run.diagnostics.perNode[nodeId].responseLag.length > 1);
  }
  assert.equal(run.diagnostics.retardedMismatch['A-B']!.length > 0, true);
  assert.equal(run.diagnostics.disturbancePropagation.length, 3);
  for (const definition of createSetupDSmokeDefinitions())
    assert.doesNotThrow(() => validateDefinition(definition));
  assert.doesNotThrow(() =>
    validateDefinition(
      createSetupDDefinition({
        duration: 1,
        sampleCadence: 0.1,
        variant: 'E1-R0',
        gain: 0,
      }),
    ),
  );
});

test('Setup D rejects non-admissible baseline gain before evolution', () => {
  assert.throws(() => runSetupD({ gain: 2 }), /must satisfy/);
});
