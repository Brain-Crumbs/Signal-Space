import type { Intervention } from '@signal-space/model';
import { PacketSolver } from './packets.js';
import type { PacketSnapshot } from './packets.js';
import { EnvelopeFailure } from './envelope.js';

/** Simulator-only provenance. Never embed this object in observer datasets. */
export interface InterventionLineage {
  runId: string;
  parentRunId: string;
  forkTime: number;
  method: 'replay-parent-prefix-v1';
  interventions: Intervention[];
}

/** Validate the full parent, replay its identical prefix, then re-evolve a branch.
 * Actions must be strictly after the checkpoint (which is already post-event).
 * The caller advances/snapshots the returned solver using ordinary resource limits.
 */
export function branchPacketRun(
  parent: { runId: string; snapshot: PacketSnapshot },
  runId: string,
  interventions: Intervention[],
): { solver: PacketSolver; lineage: InterventionLineage } {
  if (!parent.runId || !runId || parent.runId === runId)
    throw new EnvelopeFailure(
      'INVALID_REQUEST',
      'Distinct nonempty parent and branch run IDs are required.',
    );
  const original = new PacketSolver(
    parent.snapshot.scenario,
    parent.snapshot.options,
    parent.snapshot,
  ).snapshot();
  if (
    original.incomplete ||
    !interventions.length ||
    interventions.some(
      (action) => !Number.isFinite(action.time) || action.time <= original.time,
    )
  )
    throw new EnvelopeFailure(
      'INVALID_REQUEST',
      'Branch a complete checkpoint with interventions strictly after its post-event time.',
    );
  const scenario = structuredClone(original.scenario);
  scenario.interventions.push(...structuredClone(interventions));
  const solver = new PacketSolver(scenario, original.options);
  for (const until of original.advances) solver.advance(until);
  // A new future event can shorten a previously rejected trial that overshot
  // this checkpoint. Never silently return a branch with a different prefix.
  const prefix = solver.snapshot();
  if (
    JSON.stringify({ ...prefix, scenario: null }) !==
    JSON.stringify({ ...original, scenario: null })
  )
    throw new EnvelopeFailure(
      'INVALID_HISTORY',
      'The new action changes a rejected trial in the parent prefix. Choose a later action time or an earlier checkpoint.',
    );
  return {
    solver,
    lineage: {
      runId,
      parentRunId: parent.runId,
      forkTime: original.time,
      method: 'replay-parent-prefix-v1',
      interventions: structuredClone(interventions),
    },
  };
}
