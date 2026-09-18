import assert from 'node:assert/strict';
import test from 'node:test';
import type { ResearchConfig } from '@signal-space/research-contracts';
import {
  MAX_DISPLAY_POINTS,
  plotBounds,
  samplePlotRows,
  type PlotRow,
} from '../apps/web/src/ResearchPlot.js';
import { compareResearchConfigs } from '../apps/web/src/ResearchWorkspace.js';

const config: ResearchConfig = {
  schema_version: 'research-experiment-v1',
  experiment_id: 'fixture.synthetic.v1',
  model_id: 'fixture.deterministic-recurrence.v1',
  parameters: { steps: 10 },
  units: { step: 'index', value: 'dimensionless' },
  seeds: { root: 37 },
  resources: { max_memory_mb: 256 },
  analysis: { max_abs_error: 1e-14, require_complete: true },
  report: { title: 'Fixture' },
  fixture_controls: { interrupt_at_step: null, fail_at_step: null },
};

test('comparison exposes every material resolved-config dimension', () => {
  const right = structuredClone(config);
  right.seeds.root = 99;
  right.resources.max_memory_mb = 512;
  const comparison = compareResearchConfigs(config, right);

  assert.equal(comparison.structuralCompatible, true);
  assert.equal(comparison.exactMatch, false);
  assert.equal(
    comparison.dimensions.find(({ label }) => label === 'Seeds')?.matches,
    false,
  );
  assert.equal(
    comparison.dimensions.find(({ label }) => label === 'Resources')?.matches,
    false,
  );
  for (const label of [
    'Parameters',
    'Seeds',
    'Resources',
    'Analysis',
    'Report',
    'Fixture controls',
    'Additional configuration',
  ])
    assert.ok(comparison.dimensions.some((item) => item.label === label));
});

test('million-row plots use iterative bounds and bounded browser rendering', () => {
  const rows: PlotRow[] = Array.from({ length: 1_000_000 }, (_, step) => ({
    step,
    observed: step % 2 === 0 ? -step : step,
    expected: step / 2,
    absolute_error: step / 2,
  }));

  assert.deepEqual(plotBounds(rows), {
    xMin: 0,
    xMax: 999_999,
    yMin: -999_998,
    yMax: 999_999,
  });
  const sampled = samplePlotRows(rows);
  assert.equal(sampled.length, MAX_DISPLAY_POINTS);
  assert.equal(sampled[0], rows[0]);
  assert.equal(sampled.at(-1), rows.at(-1));
});

test('configuration identity ignores JSON key ordering but preserves array order', () => {
  const right = structuredClone(config);
  right.units = { value: 'dimensionless', step: 'index' };
  assert.equal(compareResearchConfigs(config, right).exactMatch, true);
  right.parameters = { sectors: [0, 1, 2] };
  const left = { ...right, parameters: { sectors: [2, 1, 0] } };
  assert.equal(compareResearchConfigs(left, right).exactMatch, false);
});

test('plot parser rejects missing and nonfinite evidence instead of dropping it', async () => {
  const { parsePlotCsv } = await import('../apps/web/src/ResearchPlot.js');
  for (const csv of [
    'step,observed,expected\n0,1,1',
    'step,observed,expected,absolute_error\n0,NaN,1,0',
    'step,observed,expected,absolute_error\n0,,1,0',
  ])
    assert.throws(() => parsePlotCsv(csv));
});
