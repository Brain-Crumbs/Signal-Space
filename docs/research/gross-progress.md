# Signal Space / GROSS progress ledger

This ledger tracks Tests 1-11 of the operator program v0.2. These numbers are independent of the older E01-E11 charged/knot sequence.

| Test | Scope                                 | Prerequisites                                           | Status                                                                                   |
| ---- | ------------------------------------- | ------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| 1    | Operator and observer identities      | Source audit; registered algebra plugin; locked plan    | Registered and locked under #52; full execution pending                                  |
| 2    | Reciprocal event law and rescheduling | 1; complete registered event circuit                    | Not evaluated                                                                            |
| 3    | Router propagation                    | 1-2; exact routing benchmark                            | Analytical prediction available; numerical test not evaluated                            |
| 4    | Complete microscopic spectrum         | 2-3; self-consistent background                         | Zero-wave strong all-sector hypothesis analytically fails; nonzero background unresolved |
| 5    | Continuum action and characteristics  | 1; registered action audit                              | Analytical factorization available; numerical test not evaluated                         |
| 6    | Bound readable clock                  | 1,5; core profile and spectrum                          | Not evaluated                                                                            |
| 7    | Predicted reception                   | Accepted 6 and frozen calibration                       | Not evaluated                                                                            |
| 8    | Two objects, exchange and recoil      | Accepted 6-7                                            | Not evaluated                                                                            |
| 9    | Observer/coordinate invariance        | Accepted local record, beginning with 6-7               | Not evaluated                                                                            |
| 10   | Spatial topology extension            | Explicit new action, domain, invariant and health audit | Not evaluated                                                                            |
| 11   | Drift and mode dependence             | Dispersion: 3-4; operational part: accepted clock and 9 | Analytical protocol available; numerical test not evaluated                              |

A pass of Test 1 validates operator algebra and its implementation only. It does not pass Candidate A or B, establish a clock or derive spacetime. A successful Candidate B clock would not satisfy Candidate A's autonomous-clock requirement.

Runtime status: the repository's common runtime is available. The operator identity plugin is registered separately from the synthetic and charged-scalar plugins. SS OPS 1 and SS OCF 1 evolution are not registered by this change.

The user-authorized workflow is a focused branch, locked experiment, verified evidence and reader export, then a PR. Raw data and prior classifications stay immutable. PR review and merge are separate from scientific classification.
