import type { Snapshot } from '@signal-space/model';
/** Inventory only; numerical diagnostics are implemented in T06. */
export function summarizeSnapshot(snapshot: Snapshot) {
  return {
    time: snapshot.time,
    nodeCount: Object.keys(snapshot.nodeState).length,
    pendingPacketCount: snapshot.history.pendingPackets.length,
  };
}
