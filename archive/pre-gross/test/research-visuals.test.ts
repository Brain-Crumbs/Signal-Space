import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  chartPoints,
  parseExploration,
  type Exploration,
  type ViewSpec,
} from '../apps/web/src/researchVisuals.js';

const view: ViewSpec = {
  id: 'energy',
  title: 'Energy',
  dataset: 'branch',
  x: 'Q',
  y: 'E',
  x_label: 'Q',
  y_label: 'E',
  x_unit: 'dimensionless',
  y_unit: 'm',
  point_key: 'id',
  parent_key: 'parent_id',
  group: 'branch',
  filters: { status: 'accepted', lane: 'base', kind: ['seed', 'continue'] },
};
function data(): Exploration {
  return {
    schema_version: 'research-exploration-v1',
    tables: {
      branch: [
        {
          id: 'a',
          branch: 'one',
          Q: 10,
          E: 9,
          status: 'accepted',
          lane: 'base',
          kind: 'seed',
          parent_id: null,
        },
        {
          id: 'failure',
          branch: 'one',
          Q: null,
          E: null,
          status: 'failed',
          lane: 'base',
          kind: 'continue',
          parent_id: 'a',
        },
        {
          id: 'b',
          branch: 'one',
          Q: 12,
          E: 11,
          status: 'accepted',
          lane: 'base',
          kind: 'continue',
          parent_id: 'failure',
        },
        {
          id: 'c',
          branch: 'two',
          Q: 11,
          E: 10,
          status: 'accepted',
          lane: 'base',
          kind: 'seed',
          parent_id: null,
        },
        {
          id: 'fine',
          branch: 'one',
          Q: 10,
          E: 9,
          status: 'accepted',
          lane: 'half-step',
          kind: 'seed',
          parent_id: null,
        },
      ],
    },
    views: [view],
    selection: {
      outcome: 'unresolved',
      coverage: false,
      points: [],
      limitations: [],
    },
    sources: [],
    normalization: 'none',
    downsampling: 'none',
    renderer: 'test',
    spectral_budgets: [],
    failures: [],
  };
}
test('branch adapter preserves physical normalization and explicit parent graph across failed/disconnected solves', () => {
  const d = data();
  const points = chartPoints(d, view);
  assert.deepEqual(
    points.map((p) => p.id),
    ['a', 'b', 'c'],
  );
  assert.equal(points[0]!.y, 9);
  assert.equal(points[1]!.parent, 'failure');
  assert.equal(points[2]!.parent, undefined);
  assert.equal(d.tables.branch!.length, 5); // Failures remain in the evidence.
});
test('point and sector selection never mix spectra; numerical error multiplier is explicit', () => {
  const d = data();
  d.tables.spectra = [
    { point: 'a', ell: 0, x: 1, y: 0.02, error: 0.001 },
    { point: 'a', ell: 1, x: 2, y: -0.02, error: null },
    { point: 'b', ell: 1, x: 3, y: 0.03, error: 0.002 },
  ];
  const spec: ViewSpec = {
    ...view,
    id: 'spectrum',
    dataset: 'spectra',
    x: 'x',
    y: 'y',
    point_key: 'point',
    filters: {},
    error: 'error',
    error_multiplier: 3,
  };
  assert.deepEqual(
    chartPoints(d, spec, 'a', '1').map((p) => p.x),
    [2],
  );
  assert.equal(chartPoints(d, spec, 'a', '1')[0]!.error, undefined);
  assert.equal(chartPoints(d, spec, 'b', '1')[0]!.error, 0.006);
});
test('invalid numeric output is rejected instead of silently rendered', () => {
  const d = data();
  d.tables.branch![0]!.E = Number.NaN;
  assert.throws(() => parseExploration(d), /non-finite/);
  assert.throws(
    () => parseExploration({ ...data(), schema_version: 'future' }),
    /Unsupported/,
  );
  assert.throws(
    () =>
      parseExploration({ ...data(), views: [{ ...view, dataset: 'missing' }] }),
    /mapping/,
  );
});
