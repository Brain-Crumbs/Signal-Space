# Test 8 doublet startup qualification

The unchanged-action implementation pilot completed all 13 locked cases in
43.795 pipeline wall seconds. Run `run-527cfda410152d85`, analysis
`analysis-0001-dc79c580`: seven engineering checks pass, long clocks and
exchange/recoil are not evaluated; the scientific classification is unresolved.
The [protocol](gross-test-08-evolution.md) and [locked
plan](plans/gross-test-08-evolution-pilot.json) define its exact scope.

The window is 8 time units, 0.526 signed periods, before nominal source arrival.
Both doublet components and freely evolving local records are retained. The
pair preparation residual falls to 0.1916776473 of its initial value; the
isolated residual falls to 0.1869289287. Pair maximum local tick discrepancy
against nominal isolated calibration falls from 0.00120482 to 0.000380584.
Similar isolated improvement points toward spatial embedding/startup error;
this is not a pair stability result or a nonlinear residual-to-error bound.

A separately locked [quadrature-clock
control](plans/gross-test-08-clock-phase-pilot.json) repeats all 13 cases with
B's independent initial clock phase at pi/2. Run `run-40d81f37cf3c7599`, analysis
`analysis-0001-c7351bd6`, report `report-0001`, completed in 46.276 pipeline
seconds. Again seven engineering checks pass and both physical gates are not
evaluated. A retains one simple crossing; B retains two in this window. Base
pair slope fractions are 0.998975 and approximately 1.0. The reduced preparation
changes maximum tick discrepancy from 0.00120478 to 0.000380625 for A, and from
0.00104617 to 0.000868918 for B. The smaller benefit for quadrature B is a
useful limitation: preparation improvement is phase dependent. Two sampled
phases are not an all-phase nonlinear guarantee.

The largest E/Q fractional ledger residuals are 1.89130e-10 / 1.90500e-10.
Pair-base energy error is 0.591119% of the initial projected clock energy;
halving dt reduces it to 0.0189071%. Fixed-dt spatial refinement changes the
local waveform by 0.261358% of its initial envelope; the time control changes
it by 4.10249e-9 and the wider domain by 4.35e-16. Domain agreement before a
boundary signal can return does not qualify a long outgoing boundary. No zero
available-control difference is interpreted as zero physical uncertainty.

Independent review checked all 1,944 derived CSV rows against raw local
samples, conservation maxima, exact neutral whole-field parity, initial/final
spatial arrays and figure/data identities. It also caught an omitted discrete
neutral redistribution current before execution; the independent cellwise
Hamiltonian/current test then passed. Later report revisions correct clipped
labels and make the short prearrival scope explicit without changing raw data
or rerunning physics. Earlier report bytes are retained.

Validation: 89 Python tests (6 optional compiled-backend skips), 13 workflow
tests, repository/archive/plan validation, math formatting and diff whitespace
checks pass. Twelve new tests cover both complex components, independent
Hamiltonian derivatives, internal unitary covariance, scalar reduction,
energy/charge currents, neutral symmetry/null, measured residual descent,
convective/proper-time extraction, tick conversion, corruption rejection and
complete-worker restart across midcase/case boundaries with prior bytes intact.

Solver source is frozen at local commit `e31f0824baf3639dbed3feb870408a6b5b719dea` (the complete identity
and exact source archive are in canonical provenance). Subsequent commits
change report presentation and this result index. Both source states are
retained in the handoff. The nominal Test 6 source and the prior quiet-pair
canonical package were reverified. The earlier accepted Test 7 classification
is preserved; its full canonical package was not present in this workspace
and must be reverified before full exchange launch.

Next: a separate long quiet-pair qualification with independent preparation,
space/time/domain, local crossing slopes, all weak channels, angular-sector
limits and conservation budgets on the weak clock scale. Held-out source
selection, causal reception, impulse/stress closure, 20 postinteraction periods
and Test 9 retention remain later gates. No Tests 1-11 status is promoted.
