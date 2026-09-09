import { test, expect } from '@playwright/test';
import { execute } from '@signal-space/sim';
import { createSample } from '@signal-space/experiments';

test('production worker renders the same initial snapshot as the shared engine', async ({
  page,
}) => {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto('/');
  await expect(
    page.getByRole('heading', { name: 'Signal Space' }),
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
    (await page.locator('pre').textContent()) ?? 'null',
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
  expect(result).toEqual(expected);
});
