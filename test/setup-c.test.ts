import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  createSetupCCell,
  createSetupCDefinition,
  createSetupCSmokeDefinitions,
  runSetupCScan,
} from '@signal-space/experiments';
import { validateDefinition } from '@signal-space/experiments';

test('Setup C converts dimensionless coordinates into an admissible pair scenario', () => {
  const run = createSetupCCell({
    detuning: 0.1,
    delay: 0.5,
    gain: -0.05,
    contrast: 0.4,
    relaxationTime: 2,
  });
  assert.equal(run.parameters.delay, 0.5);
  assert.equal(run.physical.delay, 0.25);
  assert.equal(run.scenario.nodes[1]!.omega0, 2.2);
  assert.equal(run.scenario.nodes[1]!.position, 0.25);
  assert.equal(run.scenario.links[0]!.delay, 0.25);
  assert.equal(run.physical.gain.A, -0.1);
  assert.equal(run.scenario.nodes[0]!.relaxationTime, 1);
  assert.equal(run.scenario.nodes[0]!.emission.law, 'E1');
  assert.equal(run.diagnostics.windows.length, 2);
  assert.ok(
    run.samples.some(
      (sample) => sample.time === run.diagnostics.windows[0]!.start,
    ),
  );
  assert.equal(run.finalSnapshot.kind, 'envelope-rk4-v1');
});

test('Setup C E0 baseline matching follows each detuned clock', () => {
  const e0 = createSetupCCell(
    { detuning: 0.25, delay: 1, gain: 0, contrast: 0, relaxationTime: 1 },
    { variant: 'E0-R0', duration: 2, preparationDuration: 0.5 },
  );
  const e1 = createSetupCCell(
    { detuning: 0.25, delay: 1, gain: 0, contrast: 0, relaxationTime: 1 },
    { variant: 'E1-R0', duration: 2, preparationDuration: 0.5 },
  );
  assert.equal(e0.scenario.nodes[0]!.emission.law, 'E0');
  assert.equal(e0.scenario.nodes[1]!.emission.law, 'E0');
  assert.equal(
    e0.scenario.nodes[0]!.emission.law === 'E0'
      ? e0.scenario.nodes[0]!.emission.nu
      : 0,
    e1.scenario.nodes[0]!.emission.law === 'E1'
      ? (3 * e1.scenario.nodes[0]!.omega0) / (2 * Math.PI)
      : 0,
  );
  assert.equal(
    e0.scenario.nodes[1]!.emission.law === 'E0'
      ? e0.scenario.nodes[1]!.emission.nu
      : 0,
    (3 * e0.scenario.nodes[1]!.omega0) / (2 * Math.PI),
  );
});

test('Setup C controls expose no-feedback, zero-contrast, and positive-delay controls', () => {
  const noFeedback = createSetupCCell(
    { detuning: 0, delay: 1, gain: 0.1, contrast: 1, relaxationTime: 1 },
    { control: 'no-feedback', duration: 2 },
  );
  const zeroContrast = createSetupCCell(
    { detuning: 0, delay: 1, gain: 0.1, contrast: 1, relaxationTime: 1 },
    { control: 'zero-contrast', duration: 2 },
  );
  const smallDelay = createSetupCCell(
    { detuning: 0, delay: 1, gain: 0.1, contrast: 1, relaxationTime: 1 },
    { control: 'small-positive-delay', duration: 2 },
  );
  assert.equal(noFeedback.parameters.gain, 0);
  assert.equal(zeroContrast.parameters.contrast, 0);
  assert.ok(smallDelay.parameters.delay > 0);
  assert.equal(smallDelay.scenario.links[0]!.delay, 0.025);
});

test('Setup C maps preserve cell identity and distinguish unrun cells', () => {
  const scan = runSetupCScan({
    axes: {
      detuning: [0, 0.01],
      delay: [0.5],
      gain: [0],
      contrast: [0],
      relaxationTime: [1],
    },
    variant: 'E1-R0',
    duration: 2,
    preparationDuration: 0.5,
    maxCells: 1,
  });
  assert.equal(scan.cells.length, 2);
  assert.equal(scan.runs.length, 1);
  assert.equal(scan.cells[0]!.status, 'unresolved');
  assert.equal(scan.cells[1]!.status, 'unrun');
  assert.deepEqual(scan.masks.unrun, [false, true]);
  assert.equal(scan.cells[0]!.trajectoryRunIds.length, 1);
  assert.equal(scan.metadata.varied.detuning.length, 2);
  assert.equal(scan.metadata.sourceSection, 'Paper I §11.4');
});

test('Setup C reverse continuation retains complete prior snapshots separately from restarts', () => {
  const scan = runSetupCScan({
    axes: {
      detuning: [0, 0.01],
      delay: [0.5],
      gain: [0],
      contrast: [0],
      relaxationTime: [1],
    },
    variant: 'E1-R0',
    duration: 2,
    preparationDuration: 0.5,
    direction: 'reverse',
  });
  assert.equal(scan.continuation.direction, 'reverse');
  assert.equal(scan.continuation.orderedCellKeys[0], scan.cells[1]!.key);
  assert.equal(scan.continuation.handoffs.length, 1);
  assert.equal(scan.continuation.handoffs[0]!.snapshot.kind, 'envelope-rk4-v1');
  assert.equal(scan.continuation.restarts.length, 2);
  assert.notEqual(
    scan.continuation.restarts[0]!.runId,
    scan.continuation.restarts[1]!.runId,
  );
});

test('Setup C definitions use the shared manifest contract', () => {
  for (const definition of createSetupCSmokeDefinitions())
    assert.doesNotThrow(() => validateDefinition(definition));
  const definition = createSetupCDefinition({
    detuning: 0,
    delay: 1,
    gain: 0,
    contrast: 0,
    relaxationTime: 1,
  });
  assert.equal(definition.mode, 'envelope');
  assert.equal(definition.windows.nested?.length, 1);
  assert.equal(definition.scenario.modelVersion, 'paper-i-v1');
});

test('Setup C can compare distinct initial preparations and refine selected cells', () => {
  const scan = runSetupCScan({
    axes: {
      detuning: [0],
      delay: [0.5],
      gain: [0],
      contrast: [0],
      relaxationTime: [1],
    },
    variant: 'E1-R0',
    preparations: ['co-phase', 'pi-reflection'],
    duration: 2,
    preparationDuration: 0.5,
    refineNear: [
      {
        detuning: 0.01,
        delay: 0.5,
        gain: 0,
        contrast: 0,
        relaxationTime: 1,
      },
    ],
  });
  assert.equal(scan.cells[0]!.preparationIds.length, 2);
  assert.equal(scan.runs.length, 3);
  assert.equal(scan.refinement.runIds.length, 1);
  assert.equal(
    scan.refinement.interpretation,
    'selective-diagnostic-refinement',
  );
});

test('Setup C rejects nonpositive delay and invalid contrast', () => {
  assert.throws(
    () =>
      createSetupCCell({
        detuning: 0,
        delay: 0,
        gain: 0,
        contrast: 0,
        relaxationTime: 1,
      }),
    /strictly positive/,
  );
  assert.throws(
    () =>
      createSetupCCell({
        detuning: 0,
        delay: 1,
        gain: 0,
        contrast: 2,
        relaxationTime: 1,
      }),
    /contrast must be in/,
  );
});
