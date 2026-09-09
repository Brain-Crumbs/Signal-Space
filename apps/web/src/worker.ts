import { createWorkerHandler } from '@signal-space/sim/worker';
import type { RunEvent, WorkerCommand } from '@signal-space/sim';
const handle = createWorkerHandler((event: RunEvent) => postMessage(event));
addEventListener('message', (event: MessageEvent<WorkerCommand>) => {
  void handle(event.data);
});
