import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { createSample } from '@signal-space/experiments';
import {
  PacketSolver,
  branchPacketRun,
  recordObserver,
} from '@signal-space/sim';
const scenario = createSample('pair');
for (const node of scenario.nodes) {
  node.response = 'R1';
  node.gain = 0.5;
  node.emission = { law: 'E0', nu: 0.001 };
}
scenario.initialHistory.pendingPackets = [
  {
    id: 'initial-pulse',
    source: 'A',
    target: 'B',
    port: 'left',
    emissionTime: -0.75,
    arrivalTime: 0.25,
  },
];
const options = { seed: 't05-physical-smoke-v1' };
const solver = new PacketSolver(scenario, options);
const evolve = (engine, until) => {
  while (engine.time < until && !engine.incomplete) engine.advance(until);
  if (engine.incomplete) throw new Error(engine.incomplete);
  return engine.snapshot();
};
const parent = { runId: 't05-baseline', snapshot: evolve(solver, 0.125) };
const removal = branchPacketRun(parent, 't05-removal', [
  { time: 0.25, kind: 'remove-pulse', target: 'initial-pulse' },
]);
const probe = branchPacketRun(parent, 't05-probe', [
  {
    time: 0.25,
    kind: 'add-probe',
    target: 'A',
    value: { linkId: scenario.links.find((l) => l.source === 'A').id },
  },
]);
const until = 1.5;
const baseline = evolve(solver, until),
  removed = evolve(removal.solver, until),
  probed = evolve(probe.solver, until);
const protocol = {
  observerId: 'B-detector',
  nodeId: 'B',
  seed: 't05-detector-smoke-v1',
  retentionProbability: 1,
  timestamp: { kind: 'local-phase' },
  gate: {
    start: baseline.history[0].nodes.B.phi,
    end: baseline.history.at(-1).nodes.B.phi,
  },
  latency: 0,
  jitter: { kind: 'none' },
  quantization: { width: 0.01, origin: 0 },
  readouts: [],
  marks: { kind: 'none' },
};
const digest = (value) => createHash('sha256').update(value).digest('hex');
const paths = [
  'packages/sim/src/observation.ts',
  'packages/sim/src/interventions.ts',
  'packages/sim/src/packets.ts',
  'packages/sim/src/envelope.ts',
  'packages/model/src/validate.js',
  'packages/model/schema/scenario.v1.schema.json',
  'package-lock.json',
  'scripts/observation-smoke.mjs',
];
const sources = Object.fromEntries(
  await Promise.all(
    paths.map(async (path) => [path, digest(await readFile(path))]),
  ),
);
const qa = (snapshot) => ({
  finalSample: snapshot.history.at(-1),
  records: snapshot.records,
  physicalHistorySha256: digest(JSON.stringify(snapshot.history)),
});
console.log(
  JSON.stringify(
    {
      purpose: 'T05 technical acceptance smoke; not paper results',
      command: 'node --import tsx scripts/observation-smoke.mjs',
      runtime: process.version,
      repository: 'https://github.com/Brain-Crumbs/Signal-Space',
      sourceSha256: sources,
      engineVersion: baseline.kind,
      scenario,
      options,
      until,
      lineage: [removal.lineage, probe.lineage],
      observerDatasets: [
        recordObserver({ runId: parent.runId, snapshot: baseline }, protocol),
        recordObserver(
          { runId: parent.runId, snapshot: baseline },
          { ...protocol, observerId: 'B-missed', retentionProbability: 0 },
        ),
      ],
      simulatorOnly: {
        baseline: qa(baseline),
        removed: qa(removed),
        probed: qa(probed),
      },
    },
    null,
    2,
  ),
);
