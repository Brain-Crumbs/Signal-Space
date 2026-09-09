import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { createSample } from '@signal-space/experiments';
import { execute } from '@signal-space/sim';
import type { RunEvent } from '@signal-space/sim';
const cli = (...args: string[]) =>
  spawnSync(
    process.execPath,
    ['--import', 'tsx', 'apps/cli/src/index.ts', ...args],
    { encoding: 'utf8' },
  );
test('CLI sample and direct engine have identical output', async () => {
  const result = cli('--sample', 'pair');
  assert.equal(result.status, 0, result.stderr);
  const expected: RunEvent[] = [];
  for await (const e of execute({
    runId: 'cli-inspect',
    mode: 'inspect',
    scenario: createSample('pair'),
  }))
    expected.push(e);
  assert.deepEqual(
    result.stdout
      .trim()
      .split('\n')
      .map((line) => JSON.parse(line)),
    expected,
  );
});
test('CLI rejects invalid flags and file failures with nonzero exit and structured errors', () => {
  for (const args of [
    ['--sample', 'unknown'],
    ['--file', 'missing.json'],
    ['--sample'],
    ['--unexpected'],
  ]) {
    const result = cli(...args);
    assert.equal(result.status, 1);
    assert.equal(JSON.parse(result.stderr).type, 'failed');
  }
});

test('CLI --until runs the shared deterministic engine and validates duration', async () => {
  const result = cli('--sample', 'pair', '--until', '0.13');
  assert.equal(result.status, 0, result.stderr);
  const actual = result.stdout
    .trim()
    .split('\n')
    .map((line) => JSON.parse(line));
  const expected = [];
  for await (const event of execute({
    runId: 'cli-envelope',
    mode: 'envelope',
    scenario: createSample('pair'),
    until: 0.13,
  }))
    expected.push(event);
  assert.deepEqual(actual, expected);
  for (const value of ['-1', 'NaN', 'Infinity', ''])
    assert.equal(cli('--until', value).status, 1);
  assert.equal(cli('--until').status, 1);
});
