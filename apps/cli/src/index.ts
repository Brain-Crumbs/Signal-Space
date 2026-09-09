import { readFile } from 'node:fs/promises';
import { execute } from '@signal-space/sim';
import { createSample, sampleIds } from '@signal-space/experiments';
import type { SampleId } from '@signal-space/experiments';

const args = process.argv.slice(2);
const seedIndex = args.indexOf('--seed');
const seed = seedIndex >= 0 ? args[seedIndex + 1] : undefined;
if (seedIndex >= 0) args.splice(seedIndex, 2);
const untilIndex = args.indexOf('--until');
const untilText = untilIndex >= 0 ? args[untilIndex + 1] : undefined;
const until = untilText === undefined ? undefined : Number(untilText);
const invalidUntil =
  untilIndex >= 0 &&
  (untilText === undefined ||
    untilText.trim() === '' ||
    !Number.isFinite(until) ||
    until! < 0);
if (untilIndex >= 0) args.splice(untilIndex, 2);
if (
  args.length === 1 &&
  args[0] === '--help' &&
  untilIndex < 0 &&
  seedIndex < 0
) {
  console.log(
    'Usage: npm run cli -- [--sample isolated|pair | --file scenario.json] [--until seconds] [--seed physical-seed]\nInspects preparation by default; --until evolves envelopes; --seed with --until runs stochastic packets. Emits JSON Lines. SIGINT cancels.',
  );
} else if (
  invalidUntil ||
  (seedIndex >= 0 && (!seed || seed.startsWith('--') || untilIndex < 0)) ||
  (args.length !== 0 &&
    (args.length !== 2 ||
      !['--sample', '--file'].includes(args[0] ?? '') ||
      !args[1] ||
      (args[0] === '--sample' && !sampleIds.includes(args[1] as SampleId))))
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
} else {
  const controller = new AbortController();
  const cancel = () => controller.abort();
  process.on('SIGINT', cancel);
  try {
    const scenario: unknown =
      args[0] === '--file'
        ? JSON.parse(await readFile(args[1]!, 'utf8'))
        : createSample((args[1] ?? 'isolated') as SampleId);
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
      console.log(JSON.stringify(event));
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
