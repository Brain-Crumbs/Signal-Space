import { test } from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
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
  for (const args of [
    [
      'validate',
      '--manifest',
      'definition.json',
      '--checkpoint',
      'checkpoint.json',
    ],
    [
      'sweep',
      '--manifest',
      'definition.json',
      '--checkpiont',
      'checkpoint.json',
    ],
    ['sweep', '--manifest', 'definition.json', '--manifest', 'other.json'],
    ['resume', '--manifest', 'definition.json', '--concurrency', '0'],
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

test('CLI --seed selects shared packet execution and requires a duration', async () => {
  const result = cli(
    '--sample',
    'pair',
    '--until',
    '0.3',
    '--seed',
    'cli-smoke',
  );
  assert.equal(result.status, 0, result.stderr);
  const expected = [];
  for await (const event of execute({
    runId: 'cli-packets',
    mode: 'packets',
    scenario: createSample('pair'),
    until: 0.3,
    packets: { seed: 'cli-smoke' },
  }))
    expected.push(event);
  assert.deepEqual(
    result.stdout
      .trim()
      .split('\n')
      .map((line) => JSON.parse(line)),
    expected,
  );
  for (const args of [
    ['--seed'],
    ['--seed', 'x'],
    ['--until', '1', '--seed', ''],
  ])
    assert.equal(cli(...args).status, 1);
});

test('CLI propagates incomplete run status and persists append-only sweep attempts', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'signal-space-cli-'));
  const definitionPath = join(directory, 'definition.json');
  const checkpointPath = join(directory, 'checkpoint.json');
  const definition = {
    schemaVersion: 'paper-i-experiment-v1',
    id: 'cli-incomplete',
    scenario: createSample('isolated'),
    mode: 'packets',
    until: 0.04,
    windows: { transient: 0, measurement: { start: 0, end: 0.04 } },
    tolerances: { absolute: 1e-9, relative: 1e-7 },
    replicates: 1,
    seed: 'cli-test',
    observables: ['phase'],
    packets: {},
    budgets: { maxJobs: 1, maxSteps: 1, checkpointEvery: 1 },
  };
  try {
    await writeFile(definitionPath, `${JSON.stringify(definition)}\n`);
    const run = cli('run', '--manifest', definitionPath);
    assert.equal(run.status, 2, run.stderr);
    const sweep = cli(
      'sweep',
      '--manifest',
      definitionPath,
      '--checkpoint',
      checkpointPath,
    );
    assert.equal(sweep.status, 2, sweep.stderr);
    const checkpoint = JSON.parse(await readFile(checkpointPath, 'utf8')) as {
      attempts: unknown[];
      completed: unknown[];
    };
    assert.equal(checkpoint.completed.length, 0);
    assert.equal(checkpoint.attempts.length, 1);
    const checkpointEvent = sweep.stdout
      .trim()
      .split('\n')
      .map((line) => JSON.parse(line))
      .find((event) => event.type === 'checkpoint');
    assert.ok(checkpointEvent);
    assert.equal(checkpointEvent.attemptCount, 1);
    assert.equal('checkpoint' in checkpointEvent, false);
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
