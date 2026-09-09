import { readFile, writeFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { execute } from '@signal-space/sim';
import { createSample, sampleIds } from '@signal-space/experiments';
import {
  isExperimentManifest,
  isSweepCheckpoint,
  resolveDefinition,
  resumeSweep,
  runManifest,
  runSweep,
  validateDefinition,
} from '@signal-space/experiments';
import type { SweepCheckpoint } from '@signal-space/experiments';
import type { SampleId } from '@signal-space/experiments';

const args = process.argv.slice(2);
const commands = new Set(['validate', 'run', 'sweep', 'resume']);

function option(name: string, values: string[]): string | undefined {
  const index = values.indexOf(name);
  if (index < 0) return undefined;
  const value = values[index + 1];
  if (!value || value.startsWith('--'))
    throw new Error(`${name} requires a value.`);
  return value;
}

function gitMetadata(): { codeRevision: string; dirty: boolean } {
  try {
    const codeRevision = execFileSync('git', ['rev-parse', 'HEAD'], {
      encoding: 'utf8',
    }).trim();
    const dirty =
      execFileSync('git', ['status', '--porcelain'], {
        encoding: 'utf8',
      }).trim().length > 0;
    return { codeRevision, dirty };
  } catch {
    return { codeRevision: 'unknown', dirty: true };
  }
}

async function jsonFile(path: string): Promise<unknown> {
  return JSON.parse(await readFile(path, 'utf8')) as unknown;
}

function emit(value: unknown): void {
  console.log(JSON.stringify(value));
}

async function loadPlan(path: string) {
  const value = await jsonFile(path);
  if (isExperimentManifest(value))
    throw new Error(
      'A run manifest is not a definition; use it with the run command.',
    );
  validateDefinition(value);
  return resolveDefinition(value, { source: path, ...gitMetadata() });
}

async function runDefinitionManifest(path: string): Promise<void> {
  const value = await jsonFile(path);
  if (isExperimentManifest(value)) {
    emit({ type: 'manifest', manifest: value });
    const result = await runManifest(value);
    for (const event of result.events) emit(event);
    return;
  }
  const plan = await loadPlan(path);
  if (plan.manifests.length !== 1)
    throw new Error(
      'run requires a definition resolving to exactly one replicate/variant/control combination. Use sweep for multiple runs.',
    );
  const manifest = plan.manifests[0]!;
  emit({ type: 'manifest', manifest });
  const result = await runManifest(manifest);
  for (const event of result.events) emit(event);
}

async function runSweepCommand(
  path: string,
  checkpointPath: string | undefined,
  concurrencyText: string | undefined,
): Promise<void> {
  const plan = await loadPlan(path);
  const concurrency =
    concurrencyText === undefined ? undefined : Number(concurrencyText);
  if (
    concurrencyText !== undefined &&
    (!Number.isInteger(concurrency) || concurrency! < 1)
  )
    throw new Error('--concurrency must be a positive integer.');
  const save = async (checkpoint: SweepCheckpoint) => {
    if (checkpointPath)
      await writeFile(
        checkpointPath,
        `${JSON.stringify(checkpoint, null, 2)}\n`,
      );
  };
  const outcome = await runSweep(plan, {
    ...(concurrency === undefined ? {} : { concurrency }),
    onRun: (result) => emit({ type: 'run-result', result }),
    onCheckpoint: (checkpoint) => {
      emit({ type: 'checkpoint', checkpoint });
      void save(checkpoint);
    },
  });
  if (checkpointPath) await save(outcome.checkpoint);
  emit({
    type: 'sweep-completed',
    status: outcome.status,
    runCount: outcome.results.length,
  });
}

async function resumeSweepCommand(
  definitionPath: string,
  checkpointPath: string,
  concurrencyText: string | undefined,
): Promise<void> {
  const value = await jsonFile(checkpointPath);
  if (!isSweepCheckpoint(value))
    throw new Error('Checkpoint is not a Signal Space sweep checkpoint.');
  const plan = await loadPlan(definitionPath);
  const concurrency =
    concurrencyText === undefined ? undefined : Number(concurrencyText);
  const outcome = await resumeSweep(plan, value, {
    ...(concurrency === undefined ? {} : { concurrency }),
    onRun: (result) => emit({ type: 'run-result', result }),
  });
  await writeFile(
    checkpointPath,
    `${JSON.stringify(outcome.checkpoint, null, 2)}\n`,
  );
  emit({
    type: 'sweep-completed',
    status: outcome.status,
    runCount: outcome.results.length,
  });
}

async function handleManifestCommand(command: string): Promise<void> {
  const manifestPath = option('--manifest', args.slice(1));
  if (command === 'validate') {
    if (!manifestPath)
      throw new Error('validate requires --manifest definition.json.');
    const plan = await loadPlan(manifestPath);
    emit({
      type: 'validated',
      definitionHash: plan.definitionHash,
      runCount: plan.manifests.length,
    });
    return;
  }
  if (command === 'run') {
    if (!manifestPath)
      throw new Error('run requires --manifest definition.json.');
    await runDefinitionManifest(manifestPath);
    return;
  }
  if (command === 'sweep') {
    if (!manifestPath)
      throw new Error('sweep requires --manifest definition.json.');
    await runSweepCommand(
      manifestPath,
      option('--checkpoint', args.slice(1)),
      option('--concurrency', args.slice(1)),
    );
    return;
  }
  const checkpointPath = option('--checkpoint', args.slice(1));
  if (!manifestPath || !checkpointPath)
    throw new Error(
      'resume requires --manifest definition.json and --checkpoint checkpoint.json.',
    );
  await resumeSweepCommand(
    manifestPath,
    checkpointPath,
    option('--concurrency', args.slice(1)),
  );
}

async function legacy(): Promise<void> {
  const values = [...args];
  const seedIndex = values.indexOf('--seed');
  const seed = seedIndex >= 0 ? values[seedIndex + 1] : undefined;
  if (seedIndex >= 0) values.splice(seedIndex, 2);
  const untilIndex = values.indexOf('--until');
  const untilText = untilIndex >= 0 ? values[untilIndex + 1] : undefined;
  const until = untilText === undefined ? undefined : Number(untilText);
  const invalidUntil =
    untilIndex >= 0 &&
    (untilText === undefined ||
      untilText.trim() === '' ||
      !Number.isFinite(until) ||
      until! < 0);
  if (untilIndex >= 0) values.splice(untilIndex, 2);
  if (
    values.length === 1 &&
    values[0] === '--help' &&
    untilIndex < 0 &&
    seedIndex < 0
  ) {
    console.log(
      'Usage: npm run cli -- [--sample isolated|pair | --file scenario.json] [--until seconds] [--seed physical-seed]\nNew runs: validate|run|sweep|resume --manifest definition.json [--checkpoint file]. Emits JSON Lines. SIGINT cancels.',
    );
    return;
  }
  if (
    invalidUntil ||
    (seedIndex >= 0 && (!seed || seed.startsWith('--') || untilIndex < 0)) ||
    (values.length !== 0 &&
      (values.length !== 2 ||
        !['--sample', '--file'].includes(values[0] ?? '') ||
        !values[1] ||
        (values[0] === '--sample' &&
          !sampleIds.includes(values[1] as SampleId))))
  ) {
    console.error(
      JSON.stringify({
        type: 'failed',
        error: {
          code: 'INVALID_REQUEST',
          message: 'Use --help for supported arguments.',
        },
      }),
    );
    process.exitCode = 1;
    return;
  }
  const controller = new AbortController();
  const cancel = () => controller.abort();
  process.on('SIGINT', cancel);
  try {
    const scenario: unknown =
      values[0] === '--file'
        ? await jsonFile(values[1]!)
        : createSample((values[1] ?? 'isolated') as SampleId);
    for await (const event of execute(
      seedIndex >= 0
        ? {
            runId: 'cli-packets',
            mode: 'packets',
            scenario,
            until: until!,
            packets: { seed: seed! },
          }
        : untilIndex < 0
          ? { runId: 'cli-inspect', mode: 'inspect', scenario }
          : {
              runId: 'cli-envelope',
              mode: 'envelope',
              scenario,
              until: until!,
            },
      { signal: controller.signal },
    )) {
      emit(event);
      if (event.type === 'incomplete') process.exitCode = 2;
      if (event.type === 'failed') process.exitCode = 1;
      if (event.type === 'cancelled') process.exitCode = 130;
    }
  } catch (error) {
    console.error(
      JSON.stringify({
        type: 'failed',
        error: {
          code: 'INPUT_ERROR',
          message:
            error instanceof Error ? error.message : 'Could not read input.',
        },
      }),
    );
    process.exitCode = 1;
  } finally {
    process.off('SIGINT', cancel);
  }
}

try {
  if (commands.has(args[0] ?? '')) await handleManifestCommand(args[0]!);
  else await legacy();
} catch (error) {
  console.error(
    JSON.stringify({
      type: 'failed',
      error: {
        code: 'INPUT_ERROR',
        message:
          error instanceof Error ? error.message : 'Could not process command.',
      },
    }),
  );
  process.exitCode = 1;
}
