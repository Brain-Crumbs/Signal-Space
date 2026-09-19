import { test, expect } from '@playwright/test';
import { execute } from '@signal-space/sim';
import type { EnvelopeSnapshot } from '@signal-space/sim';
import { createSample } from '@signal-space/experiments';

const researchConfig = {
  schema_version: 'research-experiment-v1',
  experiment_id: 'fixture.synthetic.v1',
  model_id: 'fixture.deterministic-recurrence.v1',
  parameters: {
    steps: 24,
    checkpoint_interval: 6,
    initial_value: 1,
    gain: 0.875,
    forcing: 0.125,
    step_delay_ms: 0,
  },
  units: { step: 'index', value: 'dimensionless' },
  seeds: { root: 37 },
  resources: {
    max_cpu_seconds: 30,
    max_memory_mb: 256,
    max_output_mb: 16,
    max_wall_seconds: 30,
  },
  analysis: { max_abs_error: 1e-14, require_complete: true },
  report: { title: 'Signal Space E00 Synthetic Runtime Fixture' },
  fixture_controls: { interrupt_at_step: null, fail_at_step: null },
};

const researchSchema = {
  type: 'object',
  default: researchConfig,
  properties: {
    schema_version: { const: 'research-experiment-v1' },
    experiment_id: { const: 'fixture.synthetic.v1' },
    model_id: { const: 'fixture.deterministic-recurrence.v1' },
    parameters: {
      type: 'object',
      properties: {
        steps: { type: 'integer', minimum: 2, maximum: 1000000 },
        checkpoint_interval: { type: 'integer', minimum: 1, maximum: 1000000 },
        initial_value: { type: 'number' },
        gain: { type: 'number', minimum: -2, maximum: 2 },
        forcing: { type: 'number' },
        step_delay_ms: { type: 'number', minimum: 0, maximum: 100 },
      },
    },
    units: { type: 'object' },
    seeds: {
      type: 'object',
      properties: {
        root: { type: 'integer', minimum: 0, maximum: 4294967295 },
      },
    },
    resources: {
      type: 'object',
      properties: {
        max_cpu_seconds: { type: 'integer', minimum: 1, maximum: 300 },
        max_memory_mb: { type: 'integer', minimum: 64, maximum: 2048 },
        max_output_mb: { type: 'integer', minimum: 1, maximum: 256 },
        max_wall_seconds: { type: 'number', minimum: 0.1, maximum: 600 },
      },
    },
    analysis: {
      type: 'object',
      properties: {
        max_abs_error: { type: 'number', minimum: 0 },
        require_complete: { type: 'boolean' },
      },
    },
    report: { type: 'object', properties: { title: { type: 'string' } } },
    fixture_controls: {
      type: 'object',
      properties: {
        interrupt_at_step: { type: ['integer', 'null'], minimum: 1 },
        fail_at_step: { type: ['integer', 'null'], minimum: 1 },
      },
    },
  },
};

function mockManifest(state = 'completed') {
  return {
    run_id: 'run-browser-fixture',
    experiment_id: 'fixture.synthetic.v1',
    experiment_version: '1.0.0',
    model_id: 'fixture.deterministic-recurrence.v1',
    created_at: '2026-09-18T12:00:00Z',
    updated_at: '2026-09-18T12:00:01Z',
    technical_state: state,
    scientific_classification: 'not-evaluated',
    config_hash: 'a'.repeat(64),
    config_path: 'resolved-config.json',
    attempts: [
      {
        attempt_id: 'attempt-0001',
        parent_attempt_id: null as string | null,
        state,
        path: 'attempts/attempt-0001',
        created_at: '2026-09-18T12:00:00Z',
        updated_at: '2026-09-18T12:00:01Z',
        exit_code: state === 'completed' ? 0 : 77,
        checkpoint: (state === 'completed'
          ? null
          : {
              path: 'attempts/attempt-0001/checkpoints/checkpoint-12.json',
              sha256: 'b'.repeat(64),
              step: 12,
            }) as { path: string; sha256: string; step: number } | null,
        failure: (state === 'completed'
          ? null
          : {
              code: 'PROCESS_INTERRUPTED',
              recoverable: true,
              message: 'fixture disconnect',
            }) as {
          code: string;
          recoverable: boolean;
          message: string | null;
        } | null,
      },
    ],
    analyses: [] as Array<Record<string, unknown>>,
    reports: [] as Array<Record<string, unknown>>,
    artifacts: [
      {
        id: 'config',
        kind: 'config',
        path: 'resolved-config.json',
        sha256: 'c'.repeat(64),
        size: 800,
        media_type: 'application/json',
        source_ids: [],
      },
      {
        id: 'raw',
        kind: 'raw',
        path: 'attempts/attempt-0001/raw/series.csv',
        sha256: 'd'.repeat(64),
        size: 60,
        media_type: 'text/csv',
        source_ids: [],
      },
    ],
    acceptance_criteria: [
      {
        id: 'fixture-complete',
        description: 'all declared fixture steps are present',
        evidence: null as string | null,
      },
      {
        id: 'fixture-recurrence-error',
        description: 'saved output matches the independent recurrence',
        evidence: null as string | null,
      },
    ],
    completeness: {
      config: true,
      provenance: true,
      attempts_terminal: true,
      analysis: false,
      report: false,
    },
    known_gaps: [
      'Synthetic E00 fixture only; no physical solver or scientific claim.',
    ],
    code_identity: {
      revision: 'abc123',
      tree_state: 'clean',
      dirty_patch_hash: '0'.repeat(64),
      runtime_version: '0.1.0',
    },
    seed_ledger: {
      initialization: 1,
      perturbations: 2,
      sampling: 3,
      analysis: 4,
    },
  };
}

async function installResearchMock(
  page: import('@playwright/test').Page,
  initialState = 'completed',
  firstEventSequence = 1,
) {
  const manifest = mockManifest(initialState);
  const events = [
    {
      sequence: firstEventSequence,
      timestamp: '2026-09-18T12:00:00Z',
      type: 'attempt-prepared',
      stage: 'prepare',
      payload: {},
      attempt_id: 'attempt-0001',
      cursor: `attempt-0001:${firstEventSequence}`,
    },
    {
      sequence: firstEventSequence + 1,
      timestamp: '2026-09-18T12:00:01Z',
      type: `attempt-${initialState}`,
      stage: 'runtime',
      payload: {},
      attempt_id: 'attempt-0001',
      cursor: `attempt-0001:${firstEventSequence + 1}`,
    },
  ];
  await page.route('http://127.0.0.1:8765/**', async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const path = url.pathname;
    const headers = {
      'access-control-allow-origin': 'http://127.0.0.1:4173',
      'content-type': 'application/json',
    };
    const json = (value: unknown) =>
      route.fulfill({ status: 200, headers, body: JSON.stringify(value) });
    if (request.method() === 'OPTIONS')
      return route.fulfill({
        status: 204,
        headers: {
          ...headers,
          'access-control-allow-methods': 'GET, POST, OPTIONS',
          'access-control-allow-headers': 'authorization, content-type',
        },
      });
    if (path === '/v1/experiments')
      return json({
        experiments: [
          {
            experiment_id: 'fixture.synthetic.v1',
            version: '1.0.0',
            model_id: 'fixture.deterministic-recurrence.v1',
            name: 'Deterministic synthetic lifecycle fixture',
            claims: 'none',
            equations: ['model:fixture.deterministic-recurrence.v1#recurrence'],
            equation_sources: [
              {
                label: 'E00 recurrence and runtime boundary',
                path: 'docs/research/runtime.md',
                catalog_id: 'e00-runtime-guide',
              },
            ],
            capabilities: ['checkpoint', 'resume', 'analysis', 'report'],
            unavailable_capabilities: [
              'physical-field solver',
              'research-scale sweep',
            ],
          },
        ],
      });
    if (path.endsWith('/schema'))
      return json({
        experiment_id: 'fixture.synthetic.v1',
        schema: researchSchema,
      });
    if (path === '/v1/validate')
      return json({ config: request.postDataJSON() });
    if (path === '/v1/estimate')
      return json({
        accepted: true,
        estimate: {
          cpu_seconds: 0.01,
          memory_mb: 32,
          disk_mb: 0.003,
          wall_seconds: 0.05,
          wall_time_class: 'instant',
        },
        limits: researchConfig.resources,
        rejected_limits: [],
      });
    if (path === '/v1/runs' && request.method() === 'GET')
      return json({ runs: [] });
    if (path === '/v1/runs' && request.method() === 'POST')
      return route.fulfill({
        status: 202,
        headers,
        body: JSON.stringify({ run_id: manifest.run_id, state: 'queued' }),
      });
    if (path.endsWith('/events'))
      return json({ events: url.searchParams.has('cursor') ? [] : events });
    if (path.endsWith('/analyze')) {
      manifest.technical_state = 'analyzed';
      manifest.scientific_classification = 'pass';
      manifest.analyses.push({
        analysis_id: 'analysis-0001',
        path: 'analyses/analysis-0001',
        created_at: '2026-09-18T12:01:00Z',
        raw_source: 'attempts/attempt-0001/raw/series.csv',
        classification: 'pass',
        summary: { max_abs_error: 0 },
      });
      manifest.acceptance_criteria.forEach((criterion) => {
        criterion.evidence = 'analyses/analysis-0001/checks.json';
      });
      return json(manifest.analyses[0]);
    }
    if (path.endsWith('/resume')) {
      manifest.technical_state = 'completed';
      const firstAttempt = manifest.attempts[0];
      if (!firstAttempt) throw new Error('mock attempt is missing');
      manifest.attempts.push({
        ...firstAttempt,
        attempt_id: 'attempt-0002',
        parent_attempt_id: 'attempt-0001',
        state: 'completed',
        exit_code: 0,
        checkpoint: null,
        failure: null,
      });
      return json({
        run_id: manifest.run_id,
        attempt_id: 'attempt-0002',
        state: 'completed',
      });
    }
    if (path.endsWith('/report')) {
      manifest.technical_state = 'analyzed';
      manifest.reports.push(
        {
          report_id: 'report-0000',
          analysis_id: 'analysis-0001',
          path: 'reports/report-0000',
          created_at: '2026-09-18T12:01:30Z',
          outputs: {},
        },
        {
          report_id: 'report-0001',
          analysis_id: 'analysis-0001',
          path: 'reports/report-0001',
          created_at: '2026-09-18T12:02:00Z',
          outputs: {},
        },
      );
      manifest.artifacts.push(
        {
          id: 'old-report-md',
          kind: 'report',
          path: 'reports/report-0000/report.md',
          sha256: '2'.repeat(64),
          size: 200,
          media_type: 'text/markdown',
          source_ids: [],
        },
        {
          id: 'old-plot',
          kind: 'plot-data',
          path: 'reports/report-0000/plot-data/recurrence.csv',
          sha256: '3'.repeat(64),
          size: 200,
          media_type: 'text/csv',
          source_ids: [],
        },
        {
          id: 'old-spec',
          kind: 'figure',
          path: 'reports/report-0000/figures/recurrence.figure.json',
          sha256: '4'.repeat(64),
          size: 200,
          media_type: 'application/json',
          source_ids: [],
        },
        {
          id: 'report-md',
          kind: 'report',
          path: 'reports/report-0001/report.md',
          sha256: 'e'.repeat(64),
          size: 200,
          media_type: 'text/markdown',
          source_ids: [],
        },
        {
          id: 'plot',
          kind: 'plot-data',
          path: 'reports/report-0001/plot-data/recurrence.csv',
          sha256: 'f'.repeat(64),
          size: 200,
          media_type: 'text/csv',
          source_ids: [],
        },
        {
          id: 'spec',
          kind: 'figure',
          path: 'reports/report-0001/figures/recurrence.figure.json',
          sha256: '1'.repeat(64),
          size: 200,
          media_type: 'application/json',
          source_ids: [],
        },
      );
      return json(manifest.reports.at(-1));
    }
    if (path.includes('/artifacts/')) {
      const id = path.split('/').at(-1);
      const artifactHeaders = {
        ...headers,
        'content-type':
          id === 'plot'
            ? 'text/csv'
            : id === 'report-md'
              ? 'text/markdown'
              : 'application/json',
      };
      if (id === 'config')
        return route.fulfill({
          status: 200,
          headers: artifactHeaders,
          body: JSON.stringify(researchConfig),
        });
      if (id === 'plot')
        return route.fulfill({
          status: 200,
          headers: artifactHeaders,
          body: 'step,observed,expected,absolute_error,step_unit,value_unit\n0,1,1,0,index,dimensionless\n1,1,1,0,index,dimensionless\n',
        });
      if (id === 'spec')
        return route.fulfill({
          status: 200,
          headers: artifactHeaders,
          body: JSON.stringify({
            id: 'fixture-recurrence',
            source_datasets: ['plot-data/recurrence.csv'],
            transformations: [],
            axes: {
              x: { label: 'Step', unit: 'index' },
              y: { label: 'Value', unit: 'dimensionless' },
            },
            normalization: 'none',
            downsampling: 'none',
            fit_window: null,
            renderer: 'matplotlib-test',
          }),
        });
      if (id === 'report-md')
        return route.fulfill({
          status: 200,
          headers: artifactHeaders,
          body: '# Fixture report\n\nSynthetic fixture only; no physics claim.',
        });
      if (id === 'old-report-md')
        return route.fulfill({
          status: 200,
          headers: artifactHeaders,
          body: '# Superseded report\n\nThis content must not be previewed.',
        });
      return route.fulfill({
        status: 200,
        headers: artifactHeaders,
        body: 'step,value\n0,1\n',
      });
    }
    if (path === `/v1/runs/${manifest.run_id}`) return json(manifest);
    return route.fulfill({
      status: 404,
      headers,
      body: JSON.stringify({ error: { code: 'NOT_FOUND', message: path } }),
    });
  });
  return manifest;
}

test('research workspace completes prepare, audit, analysis and report journey', async ({
  page,
}) => {
  await installResearchMock(page);
  await page.goto('/');
  await page.getByLabel('Ephemeral bearer token').fill('browser-token');
  await page.getByRole('button', { name: 'Connect runtime' }).click();
  await expect(page.getByText('Active experiment')).toBeVisible();
  await expect(page.getByText('physical-field solver')).toBeVisible();

  await page.getByLabel('Gain (dimensionless)').fill('0.9');
  await expect(
    page.getByLabel('Experiment preparation').getByRole('status'),
  ).toHaveText('Edited · creates a new run');
  await page.getByRole('button', { name: 'Validate & estimate' }).click();
  await expect(
    page.getByLabel('Experiment preparation').getByRole('status'),
  ).toHaveText('Validated');
  await expect(page.getByText('within limits')).toBeVisible();

  await page.getByRole('button', { name: 'Validate & start run' }).click();
  await expect(
    page.getByText('run-browser-fixture', { exact: true }).first(),
  ).toBeVisible();
  await expect(
    page.getByText('attempt-0001', { exact: true }).first(),
  ).toBeVisible();
  await expect(page.getByText('attempt-completed')).toBeVisible();
  await expect(page.getByText('not-evaluated')).toBeVisible();

  await page.getByRole('button', { name: 'Analyze saved output' }).click();
  await expect(page.getByText('pass', { exact: true }).first()).toBeVisible();
  await page.getByRole('button', { name: 'Regenerate report' }).click();
  await page.getByRole('button', { name: 'Preview latest report' }).click();
  await expect(
    page.getByRole('img', { name: 'Saved recurrence output' }),
  ).toBeVisible();
  await expect(page.getByText('Downsampling')).toBeVisible();
  await expect(
    page.getByText('Synthetic fixture only; no physics claim.'),
  ).toBeVisible();
  await expect(
    page.getByRole('button', { name: 'Download' }).first(),
  ).toBeVisible();
  await page.screenshot({
    path: 'test-results/screenshots/research-workspace-report.png',
    fullPage: true,
  });
});

test('interrupted run stays visible and resumes as a linked attempt on a narrow screen', async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await installResearchMock(page, 'interrupted');
  await page.goto('/');
  await page.getByLabel('Ephemeral bearer token').fill('browser-token');
  await page.getByRole('button', { name: 'Connect runtime' }).click();
  await page.getByRole('button', { name: 'Validate & start run' }).click();
  await expect(
    page.getByRole('alert').filter({ hasText: 'PROCESS_INTERRUPTED' }),
  ).toBeVisible();
  await page.getByRole('button', { name: 'Resume attempt' }).click();
  await expect(
    page.getByText('attempt-0002', { exact: true }).first(),
  ).toBeVisible();
  await expect(page.getByRole('cell', { name: 'attempt-0001' })).toBeVisible();
  await expect(
    page.getByRole('cell', { name: 'completed' }).last(),
  ).toBeVisible();
  await page.keyboard.press('Tab');
  await expect(page.locator(':focus')).toBeVisible();
  await page.screenshot({
    path: 'test-results/screenshots/research-workspace-mobile.png',
    fullPage: true,
  });
});

test('research runtime disconnect is explicit and retryable', async ({
  page,
}) => {
  await installResearchMock(page);
  let disconnect = true;
  await page.route('http://127.0.0.1:8765/v1/experiments', async (route) => {
    if (disconnect) {
      disconnect = false;
      await route.abort('connectionrefused');
    } else await route.fallback();
  });
  await page.goto('/');
  await page.getByLabel('Ephemeral bearer token').fill('browser-token');
  await page.getByRole('button', { name: 'Connect runtime' }).click();
  await expect(page.getByRole('alert')).toContainText('Failed to fetch');
  await page.getByRole('button', { name: 'Retry connection' }).click();
  await expect(page.getByText('Active experiment')).toBeVisible();
  await expect(page.getByText('connected', { exact: true })).toBeVisible();
});

test('event streams report a missing first sequence', async ({ page }) => {
  await installResearchMock(page, 'completed', 2);
  await page.goto('/');
  await page.getByLabel('Ephemeral bearer token').fill('browser-token');
  await page.getByRole('button', { name: 'Connect runtime' }).click();
  await page.getByRole('button', { name: 'Validate & start run' }).click();
  await expect(page.getByRole('alert')).toContainText('expected 1, received 2');
});

test('research collection is searchable and exposes source evidence', async ({
  page,
}) => {
  await page.goto('/');
  await expect(
    page.getByRole('heading', { name: 'Trace theory to evidence' }),
  ).toBeVisible();
  const { readFile } = await import('node:fs/promises');
  const catalog = JSON.parse(await readFile('research/catalog.json', 'utf8'));
  await expect(
    page.getByText(`${catalog.entries.length} records`),
  ).toBeVisible();
  await page.getByLabel('Search collection').fill('radiation');
  await expect(page.getByText('4 results')).toBeVisible();
  await page
    .getByRole('button', { name: /Charged-clock radiation milestone/ })
    .click();
  await expect(
    page.getByRole('heading', {
      name: 'Charged-clock radiation milestone',
      exact: true,
    }),
  ).toBeVisible();
  await expect(
    page.getByRole('article').getByText(/Frequency-resolved fields/),
  ).toBeVisible();
  await expect(
    page.getByRole('link', { name: 'Open source file' }),
  ).toHaveAttribute('href', /\.md$/);
  await page.getByLabel('Search collection').fill('knot topology');
  await page
    .getByRole('button', {
      name: /Knot topology to Standard Model research grid/,
    })
    .click();
  await expect(
    page.locator('.rendered-document .katex-display .katex-html').first(),
  ).toBeVisible();
  await page.getByLabel('Search collection').fill('radiation');
  await page.getByLabel('Material type').selectOption('figure');
  await expect(page.getByText('1 result')).toBeVisible();
  await page.getByLabel('Search collection').fill('');
  await expect(page.getByText('5 results')).toBeVisible();
});

test('production worker renders the same initial snapshot as the shared engine', async ({
  page,
}) => {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('/');
  await expect(
    page.getByRole('heading', { name: 'Signal Space', exact: true }),
  ).toBeVisible();
  await expect(page.getByText('Workspace smoke check')).toBeVisible();
  await page.getByLabel('Sample network').selectOption('pair');
  await page.getByRole('button', { name: 'Inspect preparation' }).click();
  await expect(page.getByRole('status')).toHaveText('Completed');
  const expected = [];
  for await (const e of execute({
    runId: 'expected',
    mode: 'inspect',
    scenario: createSample('pair'),
  }))
    if (e.type === 'snapshot') expected.push(e.snapshot);
  const actual = JSON.parse(
    (await page
      .locator('section[aria-label="Preparation result"] pre')
      .textContent()) ?? 'null',
  );
  expect(actual).toEqual(expected[0]);
  await expect(page.getByRole('progressbar')).toHaveAttribute('value', '1');
  await expect(
    page.getByRole('button', { name: 'Cancel', exact: true }),
  ).toBeDisabled();
  await page.getByLabel('Sample network').selectOption('isolated');
  await expect(page.getByRole('status')).toHaveText('Ready');
  await page.getByRole('button', { name: 'Inspect preparation' }).click();
  await expect(page.getByRole('status')).toHaveText('Completed');
  expect(errors).toEqual([]);
});
test('worker startup failure is visible and allows retry', async ({ page }) => {
  await page.route('**/assets/worker-*.js', (route) => route.abort());
  await page.goto('/');
  await page.getByRole('button', { name: 'Inspect preparation' }).click();
  await expect(page.getByRole('status')).toHaveText('Failed');
  await expect(page.getByRole('alert')).toContainText('worker');
  await expect(
    page.getByRole('button', { name: 'Inspect preparation' }),
  ).toBeEnabled();
});

test('production worker integrates the same causal history as Node', async ({
  page,
}) => {
  const workerUrls: string[] = [];
  page.on('worker', (worker) => workerUrls.push(worker.url()));
  await page.goto('/');
  await page.getByRole('button', { name: 'Inspect preparation' }).click();
  await expect(page.getByRole('status')).toHaveText('Completed');
  expect(workerUrls.length).toBe(1);
  const scenario = createSample('pair');
  const result = await page.evaluate(
    async ({ url, scenario }) => {
      const worker = new Worker(url, { type: 'module' });
      const events: unknown[] = [];
      return await new Promise<unknown[]>((resolve, reject) => {
        worker.onerror = () => {
          worker.terminate();
          reject(new Error('Worker failed'));
        };
        worker.onmessage = ({ data }) => {
          events.push(data);
          if (['completed', 'failed', 'cancelled'].includes(data.type)) {
            worker.terminate();
            resolve(events);
          }
        };
        worker.postMessage({
          type: 'run',
          request: {
            runId: 'browser-envelope',
            mode: 'envelope',
            scenario,
            until: 0.17,
          },
        });
      });
    },
    { url: workerUrls[0]!, scenario },
  );
  const expected = [];
  for await (const event of execute({
    runId: 'browser-envelope',
    mode: 'envelope',
    scenario,
    until: 0.17,
  }))
    expected.push(event);
  // Math transcendental functions may differ in the final bits across V8 builds.
  // Keep exact event structure and compare every numeric field far more tightly
  // than the solver tolerance, including the complete restart history.
  const compare = (actual: unknown, reference: unknown): void => {
    if (typeof reference === 'number') {
      expect(typeof actual).toBe('number');
      expect(actual as number).toBeCloseTo(reference, 12);
    } else if (Array.isArray(reference)) {
      expect(Array.isArray(actual)).toBe(true);
      expect((actual as unknown[]).length).toBe(reference.length);
      reference.forEach((v, i) => compare((actual as unknown[])[i], v));
    } else if (reference && typeof reference === 'object') {
      expect(actual).not.toBeNull();
      expect(typeof actual).toBe('object');
      expect(Object.keys(actual as object)).toEqual(Object.keys(reference));
      for (const [key, value] of Object.entries(reference))
        compare((actual as Record<string, unknown>)[key], value);
    } else expect(actual).toBe(reference);
  };
  compare(result, expected);
  const browserSnapshot = (
    result as Array<{ type: string; snapshot?: EnvelopeSnapshot }>
  ).find((event) => event.type === 'envelope-snapshot')?.snapshot;
  expect(browserSnapshot).toBeDefined();
  if (!browserSnapshot) throw new Error('Browser snapshot missing');
  const resumed = [];
  for await (const event of execute({
    runId: 'node-resume',
    mode: 'envelope',
    scenario,
    until: 0.2,
    resume: browserSnapshot,
  }))
    resumed.push(event);
  expect(resumed.at(-1)?.type).toBe('completed');
});

test('production worker runs and resumes seeded packets using the shared engine', async ({
  page,
}) => {
  const workerUrls: string[] = [];
  page.on('worker', (worker) => workerUrls.push(worker.url()));
  await page.goto('/');
  await page.getByRole('button', { name: 'Inspect preparation' }).click();
  await expect(page.getByRole('status')).toHaveText('Completed');
  const scenario = createSample('pair');
  // A declared inventory guarantees reception coverage without requiring a
  // particular random count from a short low-intensity realization.
  scenario.initialHistory.pendingPackets = [
    {
      id: 'browser-initial',
      source: 'A',
      target: 'B',
      emissionTime: -0.875,
      arrivalTime: 0.125,
      port: 'left',
    },
  ];
  scenario.nodes.forEach((node) => {
    node.emission = { law: 'E1', q: 20 };
  });
  const result = await page.evaluate(
    async ({ url, scenario }) => {
      const worker = new Worker(url, { type: 'module' });
      return await new Promise<{ checkpoint: unknown; terminal: string }>(
        (resolve, reject) => {
          let checkpoint: unknown;
          let resumed = false;
          worker.onerror = () => {
            worker.terminate();
            reject(new Error('Worker failed'));
          };
          worker.onmessage = ({ data }) => {
            if (data.type === 'packet-snapshot' && !resumed)
              checkpoint = data.snapshot;
            if (['failed', 'incomplete', 'cancelled'].includes(data.type)) {
              worker.terminate();
              reject(new Error(JSON.stringify(data)));
            }
            if (data.type === 'completed') {
              if (resumed) {
                worker.terminate();
                resolve({ checkpoint, terminal: data.type });
              } else {
                resumed = true;
                worker.postMessage({
                  type: 'run',
                  request: {
                    runId: 'resume',
                    mode: 'packets',
                    scenario,
                    until: 1.3,
                    packets: { seed: 'browser-packets' },
                    packetResume: checkpoint,
                  },
                });
              }
            }
          };
          worker.postMessage({
            type: 'run',
            request: {
              runId: 'packets',
              mode: 'packets',
              scenario,
              until: 1.2,
              packets: { seed: 'browser-packets' },
            },
          });
        },
      );
    },
    { url: workerUrls[0]!, scenario },
  );
  expect(result.terminal).toBe('completed');
  let nodeSnapshot;
  for await (const event of execute({
    runId: 'node',
    mode: 'packets',
    scenario,
    until: 1.2,
    packets: { seed: 'browser-packets' },
  }))
    if (event.type === 'packet-snapshot') nodeSnapshot = event.snapshot;
  expect(nodeSnapshot).toBeDefined();
  const browser = result.checkpoint as NonNullable<typeof nodeSnapshot>;
  expect(
    browser.records.some(
      (record) =>
        record.packetId === 'browser-initial' && record.kind === 'received',
    ),
  ).toBe(true);
  expect(browser.records.length).toBe(nodeSnapshot!.records.length);
  browser.records.forEach((record, i) => {
    const reference = nodeSnapshot!.records[i]!;
    expect({ ...record, time: 0 }).toEqual({ ...reference, time: 0 });
    expect(record.time).toBeCloseTo(reference.time, 12);
  });
  browser.state.forEach((value, i) =>
    expect(value).toBeCloseTo(nodeSnapshot!.state[i]!, 12),
  );
});

test('preparation retains nested solver settings and angular-sector arrays', async ({
  page,
}) => {
  await installResearchMock(page);
  const schema = structuredClone(researchSchema) as unknown as Record<
    string,
    unknown
  >;
  const config = {
    ...structuredClone(researchConfig),
    solver: { tolerance: 1e-7, sectors: [0, 1, 2] },
  };
  schema.default = config;
  (schema.properties as Record<string, unknown>).solver = {
    type: 'object',
    properties: {
      tolerance: { type: 'number' },
      sectors: { type: 'array', items: { type: 'integer' } },
      continuation: {
        type: 'object',
        properties: { step: { type: 'number' } },
      },
    },
  };
  await page.route('**/v1/experiments/*/schema', (route) => {
    if (route.request().method() === 'OPTIONS') return route.fallback();
    return route.fulfill({
      json: { experiment_id: researchConfig.experiment_id, schema },
      headers: { 'access-control-allow-origin': 'http://127.0.0.1:4173' },
    });
  });
  await page.goto('/');
  await page.getByLabel('Ephemeral bearer token').fill('browser-token');
  await page.getByRole('button', { name: 'Connect runtime' }).click();
  await page.getByLabel('Sectors (JSON)').fill('[0,1,2,3]');
  await page.locator('#config-solver-continuation-step').fill('0.002');
  const submitted = page.waitForRequest(
    (request) =>
      request.url().endsWith('/v1/validate') && request.method() === 'POST',
  );
  await page.getByRole('button', { name: 'Validate & estimate' }).click();
  expect((await submitted).postDataJSON().solver).toEqual({
    tolerance: 1e-7,
    sectors: [0, 1, 2, 3],
    continuation: { step: 0.002 },
  });
});

test('report preview does not require synthetic recurrence files', async ({
  page,
}) => {
  const manifest = await installResearchMock(page);
  manifest.experiment_id = 'test.profile.v1';
  await page.goto('/');
  await page.getByLabel('Ephemeral bearer token').fill('browser-token');
  await page.getByRole('button', { name: 'Connect runtime' }).click();
  await page.getByRole('button', { name: 'Validate & start run' }).click();
  await page.getByRole('button', { name: 'Analyze saved output' }).click();
  await page.getByRole('button', { name: 'Regenerate report' }).click();
  manifest.artifacts = manifest.artifacts.filter(
    (artifact) => !['plot', 'spec'].includes(artifact.id),
  );
  await page.getByRole('button', { name: 'Preview latest report' }).click();
  await expect(
    page.getByText('Synthetic fixture only; no physics claim.'),
  ).toBeVisible();
  await expect(
    page.getByRole('img', { name: 'Saved recurrence output' }),
  ).toHaveCount(0);
});

test('E01 research preset is explicit and loading it never launches a run', async ({
  page,
}) => {
  const { readFile } = await import('node:fs/promises');
  const smoke = JSON.parse(
    await readFile('fixtures/research/e01-smoke.json', 'utf8'),
  );
  const research = JSON.parse(
    await readFile('fixtures/research/e01-research.json', 'utf8'),
  );
  const schema = JSON.parse(
    await readFile('contracts/research/e01.schema.json', 'utf8'),
  );
  schema.default = smoke;
  schema['x-presets'] = [
    { name: 'Small validation fixture', config: smoke },
    { name: 'Author research run (opt-in)', config: research },
  ];
  await installResearchMock(page);
  let launched = 0;
  page.on('request', (request) => {
    if (request.url().endsWith('/v1/runs') && request.method() === 'POST')
      launched += 1;
  });
  const headers = {
    'access-control-allow-origin': 'http://127.0.0.1:4173',
    'content-type': 'application/json',
  };
  await page.route('http://127.0.0.1:8765/v1/experiments', async (route) => {
    if (route.request().method() === 'OPTIONS') return route.fallback();
    await route.fulfill({
      headers,
      json: {
        experiments: [
          {
            experiment_id: 'e01-charged-branch',
            version: '1.0.0',
            model_id: 'charged-scalar-3d-v1',
            name: 'E01 · 3D charged recurrence branch and stability',
            claims: 'conditional',
            equations: [
              'charged-recurrence-winding-hopf.md sections 2–10,14–15,23',
            ],
            capabilities: ['radial-continuation', 'constrained-spectra'],
            unavailable_capabilities: ['particle identification'],
          },
        ],
      },
    });
  });
  await page.route(
    'http://127.0.0.1:8765/v1/experiments/e01-charged-branch/schema',
    async (route) => {
      if (route.request().method() === 'OPTIONS') return route.fallback();
      await route.fulfill({
        headers,
        json: { experiment_id: 'e01-charged-branch', schema },
      });
    },
  );
  await page.goto('/');
  await page.getByLabel('Ephemeral bearer token').fill('browser-token');
  await page.getByRole('button', { name: 'Connect runtime' }).click();
  await expect(
    page.getByLabel('Research Run', { exact: true }),
  ).not.toBeChecked();
  await page
    .getByRole('button', { name: 'Author research run (opt-in)' })
    .click();
  await expect(page.getByLabel('Research Run', { exact: true })).toBeChecked();
  await expect(page.getByLabel('Omega Start (m)', { exact: true })).toHaveValue(
    '0.875',
  );
  await expect(page.getByLabel('Omega End (m)', { exact: true })).toHaveValue(
    '0.995',
  );
  await expect(
    page.getByLabel('Lambda (dimensionless)', { exact: true }),
  ).toBeDisabled();
  await page.getByRole('button', { name: 'Validate & estimate' }).click();
  await expect(
    page.getByLabel('Experiment preparation').getByRole('status'),
  ).toHaveText('Validated');
  expect(launched).toBe(0);
  await page.screenshot({
    path: 'test-results/screenshots/e01-author-preset.png',
    fullPage: true,
  });
});
