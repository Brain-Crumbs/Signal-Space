import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  createSetupAProtocol,
  createSetupAResponseCurve,
  createSetupAScenario,
  createSetupASmokeDefinitions,
  runSetupA,
  setupAVariants,
  type SetupAProtocol,
} from '@signal-space/experiments';
import { validateDefinition } from '@signal-space/experiments';

const close = (actual: number, expected: number, tolerance = 1e-8) =>
  assert.ok(
    Math.abs(actual - expected) <= tolerance,
    `${actual} != ${expected} (tol ${tolerance})`,
  );

function analyticR1Trajectory(
  time: number,
  points: SetupAProtocol['points'],
  duration: number,
) {
  let cursor = 0;
  let phi = 0;
  let omega = 2;
  for (const [index, point] of points.entries()) {
    if (point.time > time) break;
    const end = Math.min(points[index + 1]?.time ?? duration, time);
    const dt = end - cursor;
    if (dt <= 0) {
      cursor = end;
      continue;
    }
    const target = 2 + 0.5 * Math.tanh(point.left + point.right);
    const decay = Math.exp(-dt);
    phi += target * dt + (omega - target) * (1 - decay);
    omega = target + (omega - target) * decay;
    cursor = end;
    if (cursor >= time) break;
  }
  return { phi, omega };
}

test('Setup A isolated baseline has uniform recurrence and no arrivals', () => {
  const result = runSetupA(createSetupAProtocol('isolated'), 'R0');
  assert.ok(result.samples.length > 1);
  for (const sample of result.samples) {
    close(sample.phi, 2 * sample.time);
    close(sample.omega, 2);
    close(sample.phaseDisplacement, 0);
    assert.equal(sample.inputSum, 0);
    assert.equal(sample.filter.sum, 0);
  }
  assert.equal(result.summary.inputIntegral, 0);
  assert.equal(result.summary.nextTickStatus, 'missing-in-window');
  assert.equal(result.ticks.length, 0);
});

test('Setup A R0 and constant-input R1 controls cover both gain signs', () => {
  const protocol = createSetupAProtocol('equal-constant', { duration: 1.2 });
  const r0 = runSetupA(protocol, 'R0');
  for (const sample of r0.samples) {
    close(sample.omega, 2);
    close(sample.phaseDisplacement, 0);
  }
  for (const variant of ['R1-positive', 'R1-negative'] as const) {
    const result = runSetupA(protocol, variant);
    const gain = variant === 'R1-positive' ? 0.5 : -0.5;
    const target = 2 + gain * Math.tanh(1);
    for (const sample of result.samples) {
      close(sample.omega, target + (2 - target) * Math.exp(-sample.time), 2e-7);
      close(
        sample.phi,
        target * sample.time + (2 - target) * (1 - Math.exp(-sample.time)),
        2e-7,
      );
    }
  }
});

test('Setup A preserves scalar response when equal total input switches sides', () => {
  const base = createSetupAProtocol('equal-constant', { duration: 0.8 });
  const left = structuredClone(base) as SetupAProtocol;
  const right = structuredClone(base) as SetupAProtocol;
  left.points = [{ time: 0, left: 1, right: 0 }];
  right.points = [{ time: 0, left: 0, right: 1 }];
  const leftRun = runSetupA(left, 'R1-positive');
  const rightRun = runSetupA(right, 'R1-positive');
  assert.equal(leftRun.samples.length, rightRun.samples.length);
  for (const [index, sample] of leftRun.samples.entries()) {
    const other = rightRun.samples[index]!;
    close(sample.phi, other.phi, 2e-9);
    close(sample.omega, other.omega, 2e-9);
  }
});

test('Setup A records fixed-sum switching, pulse ordering, bounds, ticks, and filters', () => {
  const fixed = runSetupA(
    createSetupAProtocol('unequal-fixed-sum'),
    'R2-positive',
  );
  for (const sample of fixed.samples) close(sample.inputSum, 1);
  assert.ok(fixed.samples.every((sample) => sample.boundMargin >= -1e-9));
  assert.ok(fixed.samples.some((sample) => sample.filter.sum > 0));

  const early = runSetupA(
    createSetupAProtocol('equal-integral-early'),
    'R1-positive',
  );
  const late = runSetupA(
    createSetupAProtocol('equal-integral-late'),
    'R1-positive',
  );
  close(early.summary.inputIntegral, late.summary.inputIntegral);
  assert.notEqual(
    early.protocol.points[0]!.left + early.protocol.points[0]!.right,
    late.protocol.points[0]!.left + late.protocol.points[0]!.right,
  );
  for (const result of [early, late]) {
    for (const sample of result.samples) {
      const expected = analyticR1Trajectory(
        sample.time,
        result.protocol.points,
        result.protocol.duration,
      );
      close(sample.phi, expected.phi, 2e-7);
      close(sample.omega, expected.omega, 2e-7);
    }
  }

  const pulse = runSetupA(
    createSetupAProtocol('finite-pulse', {
      duration: 4,
      pulsePhase: 0,
      pulseAmplitude: 1,
      pulseWidth: 0.4,
    }),
    'R1-positive',
  );
  assert.ok(pulse.summary.inputIntegral > 0);
  assert.equal(pulse.summary.nextTickStatus, 'in-window');
  assert.ok(pulse.summary.nextTick);
  assert.ok(pulse.summary.filterPeak > 0);
});

test('Setup A response curve saves pulse phase/amplitude and defers interpretation', () => {
  const defaultCurve = createSetupAResponseCurve();
  assert.equal(defaultCurve.points.length, 8);
  const curve = createSetupAResponseCurve({
    phases: [0, Math.PI],
    amplitudes: [0.5, 1],
  });
  assert.equal(curve.points.length, 4);
  assert.equal(curve.controls.scientificInterpretation, 'deferred');
  assert.equal(new Set(curve.points.map((point) => point.pulsePhase)).size, 2);
  assert.equal(
    new Set(curve.points.map((point) => point.pulseAmplitude)).size,
    2,
  );
  assert.equal(curve.controls.sameIntegratedInput, false);
  for (const point of curve.points) {
    assert.equal(point.protocol, 'finite-pulse');
    assert.ok(point.minimumBoundMargin >= -1e-9);
    assert.ok(
      point.nextTickStatus === 'in-window' ||
        point.nextTickStatus === 'missing-in-window',
    );
  }
});

test('Setup A definitions are schema-compatible across protocols and variants', () => {
  assert.equal(setupAVariants.length, 5);
  assert.throws(
    () => createSetupAProtocol('unknown' as never),
    /Unknown Setup A protocol unknown/,
  );
  for (const definition of createSetupASmokeDefinitions()) {
    assert.doesNotThrow(() => validateDefinition(definition));
    assert.equal(definition.mode, 'envelope');
    assert.equal(definition.scenario.modelVersion, 'paper-i-v1');
  }
  const r2 = createSetupAScenario(
    createSetupAProtocol('equal-constant'),
    'R2-negative',
  );
  assert.equal(r2.nodes[0]!.response, 'R2');
  assert.equal(r2.nodes[0]!.gain, -0.5);
});
