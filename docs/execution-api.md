# T02 execution boundary

Engineering foundation for Paper I §11; parent #1, task #3. This adds no physical equations. The original Paper III attachment is background only and is not an implementation source for this task.

Both adapters call `execute({ runId, mode: 'inspect', scenario }, { signal })` from `@signal-space/sim`. It is an async generator of structured-cloneable `RunEvent` values, independent of React and Node APIs. A run owns a cloned input before its first progress yield. The nested history, observation, solver, intervention and unit fields are structurally constrained at the runtime boundary. JSON Schema validation precedes semantic validation, so malformed collections cannot reach the semantic validator. Failures contain codes, messages and field paths.

| Event       | Meaning                                                                                                          |
| ----------- | ---------------------------------------------------------------------------------------------------------------- |
| `progress`  | Fraction in [0,1] and validating/preparing stage                                                                 |
| `snapshot`  | Detached initial `Snapshot` at t=0, including supplied history, filters, pending packets/responses and RNG state |
| `completed` | Terminal inspection success; explicitly identifies inspect mode                                                  |
| `cancelled` | Terminal cooperative cancellation                                                                                |
| `failed`    | Terminal structured failure; invalid request/scenario, internal error or worker busy                             |

`WorkerCommand` is a discriminated union of run and cancel. Cancellation is scoped to `runId`; a different ID cannot abort an active request. Each worker adapter handles one run and rejects overlapping requests as BUSY. Use a unique ID for each request. The UI creates a worker per run and terminates it on completion, failure or unmount. It ignores responses for stale IDs.

The engine yields to the task queue between preparation stages so worker cancel messages can be delivered. Synchronous validation itself is not interruptible; large inputs may postpone cancellation until the next stage. Callers must consume the generator to a terminal event (or deliberately stop it). An abort before completion produces exactly one cancelled event and no completed event. A snapshot may already have been delivered; it is still the supplied preparation, not evidence of a completed simulation.

The smoke fixtures only validate plumbing and expose the user-supplied initial state. A snapshot at t=0 is not a solved trajectory, restart algorithm, evolved history, event realization, observer record or completed A–I protocol. Other execution modes fail explicitly until implemented. T03 must extend this interface with actual integration and complete evolving history; T04 owns stochastic scheduling and T07 owns run manifests/checkpoints/provenance. No tolerance or convergence claim is made here.

Source-first private workspaces are bundled by Vite/esbuild and run in development through tsx. Strict TypeScript applies to new TS code; the existing T01 JavaScript validator remains unchanged and is exposed through declarations. ESLint forbids Node/React imports in shared source and Node/CLI imports in the web app.
