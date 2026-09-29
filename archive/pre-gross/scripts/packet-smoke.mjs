import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { createSample } from '@signal-space/experiments';
import { PacketSolver } from '@signal-space/sim';

// A small reproducible technical run, never an A–I result or ensemble estimate.
const scenario = createSample('pair');
const options = { seed: 't04-saved-smoke-v1' };
const solver = new PacketSolver(scenario, options);
while (solver.time < 2 && !solver.incomplete) solver.advance(2);
if (solver.incomplete) throw new Error(solver.incomplete);
const snapshot = solver.snapshot();
const digest = (value) => createHash('sha256').update(value).digest('hex');
const paths = [
  'packages/sim/src/packets.ts',
  'packages/sim/src/envelope.ts',
  'packages/model/src/validate.js',
  'packages/model/schema/scenario.v1.schema.json',
  'package-lock.json',
];
const sources = Object.fromEntries(
  await Promise.all(
    paths.map(async (path) => [path, digest(await readFile(path))]),
  ),
);
console.log(
  JSON.stringify(
    {
      purpose: 'T04 technical smoke, not a paper finding',
      command: 'node --import tsx scripts/packet-smoke.mjs',
      repository: 'https://github.com/Brain-Crumbs/Signal-Space',
      engineVersion: snapshot.kind,
      runtime: process.version,
      sourceSha256: sources,
      scenario,
      options,
      until: 2,
      outcome: 'completed',
      counts: Object.fromEntries(
        ['emitted', 'pending', 'received', 'escaped', 'absorbed'].map(
          (kind) => [
            kind,
            snapshot.records.filter((record) => record.kind === kind).length,
          ],
        ),
      ),
      finalSample: solver.sample(),
      pendingInventory: snapshot.pending.length,
      rawRecordsSha256: digest(JSON.stringify(snapshot.records)),
      note: 'Exact raw record checksum is a same-runtime diagnostic. Full raw events and restart state are available through packet-snapshot or CLI --seed output.',
    },
    null,
    2,
  ),
);
