import { readFile } from 'node:fs/promises';
import { execute } from '@signal-space/sim';
import { createSample, sampleIds } from '@signal-space/experiments';
import type { SampleId } from '@signal-space/experiments';

const args = process.argv.slice(2);
if (args.length === 1 && args[0] === '--help') {
  console.log(
    'Usage: npm run cli -- [--sample isolated|pair | --file scenario.json]\nInspects initial state only; emits JSON Lines. SIGINT cancels.',
  );
} else if (
  args.length !== 0 &&
  (args.length !== 2 ||
    !['--sample', '--file'].includes(args[0] ?? '') ||
    !args[1] ||
    (args[0] === '--sample' && !sampleIds.includes(args[1] as SampleId)))
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
      { runId: 'cli-inspect', mode: 'inspect', scenario },
      { signal: controller.signal },
    )) {
      console.log(JSON.stringify(event));
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
