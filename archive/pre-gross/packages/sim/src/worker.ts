import { execute } from './index.js';
import type { RunEvent, WorkerCommand } from './index.js';
/** Transport adapter shared with tests; owns one cancellable run at a time. */
export function createWorkerHandler(send: (event: RunEvent) => void) {
  let active: { runId: string; controller: AbortController } | undefined;
  return async (command: WorkerCommand): Promise<void> => {
    if (command.type === 'cancel') {
      if (active?.runId === command.runId) active.controller.abort();
      return;
    }
    if (active) {
      send({
        type: 'failed',
        runId: command.request.runId,
        error: { code: 'BUSY', message: 'A run is already active.' },
      });
      return;
    }
    const controller = new AbortController();
    active = { runId: command.request.runId, controller };
    try {
      for await (const event of execute(command.request, {
        signal: controller.signal,
      }))
        send(event);
    } finally {
      active = undefined;
    }
  };
}
