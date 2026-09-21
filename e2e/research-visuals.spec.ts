import { test, expect } from '@playwright/test';
import { spawn, type ChildProcess } from 'node:child_process';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

let server: ChildProcess;
let workspace: string;
let endpoint: { port: number; token: string };
test.beforeAll(async () => {
  test.setTimeout(120_000);
  workspace = await mkdtemp(join(tmpdir(), 'signal-visuals-'));
  server = spawn(
    'python3',
    [
      '-u',
      '-c',
      `
import sys
from pathlib import Path
from signal_space.runtime.runner import ResearchRuntime
from signal_space.runtime.io import read_json
from signal_space.service.api import serve
w=Path(sys.argv[1]); rt=ResearchRuntime()
for seed in (1001,1002):
    c=read_json(Path('fixtures/research/e01-smoke.json')); c['seeds']['root']=seed
    result=rt.run(c,w)
    assert result['state']=='completed',result
    rt.analyze(w,result['run_id']); rt.report(w,result['run_id'])
serve(w,'http://127.0.0.1:4173')
`,
      workspace,
    ],
    {
      env: { ...process.env, PYTHONPATH: 'python', OPENBLAS_NUM_THREADS: '1' },
    },
  );
  endpoint = await new Promise((resolve, reject) => {
    let out = '',
      err = '';
    const timer = setTimeout(
      () => reject(new Error(`Runtime startup timeout: ${err}`)),
      110_000,
    );
    server.stderr!.on('data', (chunk) => {
      err += String(chunk);
    });
    server.stdout!.on('data', (chunk) => {
      out += String(chunk);
      if (out.includes('\n')) {
        clearTimeout(timer);
        try {
          resolve(JSON.parse(out.split('\n')[0]!));
        } catch (e) {
          reject(e);
        }
      }
    });
    server.on('exit', (code) => {
      clearTimeout(timer);
      reject(new Error(`Runtime exit ${code}: ${err}`));
    });
  });
});
test.afterAll(async () => {
  server?.kill();
  if (workspace) await rm(workspace, { recursive: true, force: true });
});

test('real E01 reports support linked selection, progress, exports and compatible overlays', async ({
  page,
}) => {
  test.setTimeout(60_000);
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('/');
  await page
    .getByLabel('Runtime API path or URL')
    .fill(`http://127.0.0.1:${endpoint.port}`);
  await page.getByLabel('Ephemeral bearer token').fill(endpoint.token);
  await page.getByRole('button', { name: 'Connect runtime' }).click();
  await page.getByRole('button', { name: '2 · Run audit' }).click();
  const explorer = page.getByRole('region', {
    name: 'Research visual explorer',
  });
  await expect(
    explorer.getByRole('img', { name: 'Energy and charge', exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole('region', { name: 'Provisional run progress' }),
  ).toBeVisible();
  await expect(explorer.getByText('Scientific outcome:')).toContainText(
    'unresolved',
  );
  const picker = page.getByLabel('Selected solution');
  const options = await picker
    .locator('option')
    .evaluateAll((nodes) => nodes.map((n) => (n as HTMLOptionElement).value));
  expect(options.length).toBe(3);
  const energyChart = explorer.locator('figure').filter({
    has: page.getByRole('heading', { name: 'Energy and charge', exact: true }),
  });
  const selectablePoints = energyChart.locator('circle[role="button"]');
  await expect(selectablePoints).toHaveCount(3);
  await selectablePoints.nth(1).press('Enter');
  await expect(
    explorer.getByRole('heading', { name: `Solution ${options[1]}` }),
  ).toBeVisible();
  await picker.selectOption(options[1]!);
  await expect(
    explorer.getByRole('heading', { name: `Solution ${options[1]}` }),
  ).toBeVisible();
  await page.getByLabel('Overlay profile').selectOption(options[0]!);
  await page.getByLabel('Angular sector').selectOption('1');
  const download = page.waitForEvent('download');
  await page.getByRole('button', { name: 'Export reproducible view' }).click();
  const exported = JSON.parse(
    await readFile(await (await download).path(), 'utf8'),
  );
  expect(exported.selection.point).toBe(options[1]);
  expect(exported.selection.sector).toBe('1');
  expect(exported.data.tables.profiles.length).toBeGreaterThan(1000);
  expect(
    exported.artifacts.some((a: { sha256: string }) => a.sha256.length === 64),
  ).toBe(true);
  const spectrum = explorer.locator('figure').filter({
    has: page.getByRole('heading', {
      name: 'Charge-constrained spectrum',
      exact: true,
    }),
  });
  await spectrum.getByText('Inspect exact chart data').click();
  await expect(spectrum.locator('tbody')).toContainText('ell: 1');
  await expect(spectrum.locator('tbody')).not.toContainText('ell: 0');
  const svgDownload = page.waitForEvent('download');
  await spectrum.getByRole('button', { name: 'Export SVG' }).click();
  expect(await readFile(await (await svgDownload).path(), 'utf8')).toContain(
    'research-view-export-v1',
  );
  await page.screenshot({
    path: 'test-results/screenshots/e01-linked-explorer.png',
    fullPage: true,
  });
  await page.getByRole('button', { name: '4 · Reports' }).click();
  const gallery = page.getByRole('region', { name: 'Saved figure gallery' });
  await expect(gallery.locator('img')).toHaveCount(5);
  await expect
    .poll(() =>
      gallery
        .locator('img')
        .evaluateAll((imgs) =>
          imgs.every((img) => (img as HTMLImageElement).naturalWidth > 0),
        ),
    )
    .toBe(true);
  await page.getByRole('button', { name: 'Preview latest report' }).click();
  await expect(
    page.getByRole('heading', { name: 'Outcome', exact: true }),
  ).toBeVisible();
  await page.getByRole('button', { name: '3 · Compare' }).click();
  const comparison = page.getByRole('region', {
    name: 'Visual run comparison',
  });
  await expect(
    comparison.getByRole('img', {
      name: 'Compare Energy and charge',
      exact: true,
    }),
  ).toBeVisible();
  await expect(
    comparison.getByRole('img', {
      name: 'Compare Radial amplitude',
      exact: true,
    }),
  ).toBeVisible();
  await page.getByRole('button', { name: '2 · Run audit' }).click();
  const runPicker = page.getByLabel('Saved run');
  const runIds = await runPicker
    .locator('option')
    .evaluateAll((nodes) =>
      nodes.map((n) => (n as HTMLOptionElement).value).filter(Boolean),
    );
  await runPicker.selectOption(runIds[1]!);
  await expect(explorer).toContainText(`Run ${runIds[1]}`);
  await expect(explorer).not.toContainText(`Run ${runIds[0]}`);
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(
    explorer.getByRole('img', { name: 'Radial amplitude', exact: true }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth + 1,
    ),
  ).toBe(true);
  await page.screenshot({
    path: 'test-results/screenshots/e01-linked-mobile.png',
    fullPage: true,
  });
  expect(errors).toEqual([]);
});
