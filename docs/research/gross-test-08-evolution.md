# Test 8: freely evolving doublet pair implementation

This stage implements the first dynamical successor to the quiet-pair spectrum
supplement. It registers `gross.two-object-evolution.v1`, model restriction
`signal-space.ss-ocf-1.flat-axisymmetric-doublet.v1`. The action is unchanged.
The new model ID identifies retained internal degrees of freedom and numerical
restriction, not an altered potential or coupling. It does not replace either
historical Test 8 registration or accept the full exchange campaign of issue #82.

## Evidence and the question

The supplied `Candidate_B_Quiet_Pair_Derivation_and_Results.pdf` (12 October
2026, run `run-fa0c8e4cdc561952`, analysis `analysis-0001-582b7454`) finds
separation-dependent collective clocks. D=40 is the first sampled reduced
candidate meeting its timing/slope bounds; it is not a physical survival
certificate. Orthogonal doublets and quadrature matter phases share a frozen
density but different coherent reception. Both complex components must be
retained to test that distinction dynamically.

The question here is narrower: can the registered solver freely evolve those
preparations, retain actual local records, and diagnose preparation and
conservation errors without holding the pair in place?

The prior [full campaign design](test-08-acceptance-plan.md), [quiet
protocol](gross-test-08-quiet.md), and [spatial action mapping](gross-test-08.md)
remain applicable. Their G0-G9 thresholds are unchanged. The old six-period
configuration and all canonical evidence retain their exact bytes.

## Unchanged action and retained variables

Units are c=hbar=m=1. The complex doublet is Phi=(phi1,phi2), with density
s=|phi1|^2+|phi2|^2. Its kinetic term has no factor 1/2. U=s-s^2+s^3,
Z=1+0.2s, Vchi=0.25-0.4s+0.2s^2 and zeta=0.1. Both matter momenta are
Pi=partial_t Phi; the neutral canonical momentum is pi_a=Z partial_t a.
The real clock and its momentum are chi and pchi. Equations and normalization
are Program v0.2 sections 7-10 and 15.8.

Annular cell volumes, face conductances and the discrete Hamiltonian are shared
with the existing action-consistent reference. Each matter component receives
the same density-dependent force. A global internal unitary transformation
commutes with the equations. The exactly zero second component recovers the
old scalar restriction. The neutral homogeneous zero sector remains exactly
zero unless initial neutral data are explicitly seeded.

Outer damping is a numerical intervention in a declared buffer. Energy,
charge and axial momentum sink rates are integrated with the same RK4 stages
as the fields. Axial momentum uses continuum-consistent central derivatives;
it is not an exact conserved discrete momentum in the bounded mirror box.

The cell-energy sum shares each bond equally between its endpoints. Because
the neutral face stiffness depends on density, the exact discrete energy
current includes an extra Z_s/8 conductance times (delta a)^2 times
(sdot_left-sdot_right). Its coefficient is 0.025. This vanishes on continuum
refinement but is necessary for the cellwise discrete conservation test.
Energy and charge currents are checked independently against Hamiltonian
directional derivatives, including nonzero neutral data.

## Measured preparations, then free evolution

Each core uses the original byte-locked Test 6 omega_Q=0.900 profile and nominal
clock stencil. The clock reference is Omega=0.41274991, not forced into an
eigensolve and not fitted to these trajectories. The latest continuum reference
0.41274854361 belongs to a different calibration discretization. This pilot
does not transplant its D=40 continuum timing bound or precision allowance.

The naive rotating matter data sum two translated profiles with an internal
angle and matter phase. The clock data are independently seeded cosine/sine
quadratures, rather than imposed collective-mode velocities. Both terms of the
initial velocity are retained. Their startup is part of the measured record.

The comparison preparation takes bounded linear defect-correction steps at
chi=0. Its real-linear Hessian acts on four real matter components in
volume-weighted variables. The correction is orthogonal to each core's
amplitude, phase and translation tangents. Damped least squares and an explicit
backtracking check reduce the actual unprojected residual. Iterations and
linear work are bounded. The per-iteration correction cap, total applied
correction, actual residual and preparation E/Q changes are retained. A
nondecreasing step is rejected and recorded. The clock is added afterward;
the additional clock-dressed residual is also saved. No pins, residual-removal
force or later relaxation acts during evolution. This constructs improved
initial data, not a jointly stationary solution or a nonlinear error bound.

## Source preparations and what they do not test yet

Neutral and structural sources are compact initial perturbations about A.
Their smooth bump is exp(1-1/(1-r^2/Rs^2)) inside support and zero outside.
Neutral a uses amplitude times bump times cos(k(z-zA)+phase), with the
right-moving vacuum ansatz pi_a=-Z partial_z a. That ansatz is not an exact
material-core propagation law; subsequent dynamics use the full equations.
Structural data add amplitude times bump times exp(i(k(z-zA)+phase)) to the
first component and its rotating canonical velocity. Channel, phase, spatial
carrier, radius and signed amplitude are effective, retained inputs.

No source acts after t=0. Energy, charge and momentum changes against the
identical quiet initial preparation are recorded. Neutral sign reversal is an
exact field symmetry with even matter/clock response; structural sign reversal
is generally phase sensitive. Neither channel is interpreted as spontaneously
generated emission or a resolved received signal in this pilot.

## Local records and flux accounting

Charge centroids are tracked in nonoverlapping, fixed cylindrical tubes. Their
instantaneous velocities follow from the discrete charge derivative and the
centroid quotient, not a fitted trajectory. Tracking fails explicitly for
nonpositive charge, a non-timelike worldline, or departure from the locked
tracking region. Regular-axis extrapolation and axial interpolation sample
chi at each measured center. Its material derivative is pchi+v partial_z chi;
division by sqrt(1-v^2) gives the proper-time derivative. Proper time is derived
from the saved timelike rate using declared trapezoidal quadrature; its error
is not yet qualified.

The sign-invariant clock phase is arg[(chi-i dchi_dtau/Omega)^2]. Unwrapped
phase divided by 2pi is invariant ticks; signed-field cycles are half that
count. Derivative-informed Hermite interpolation locates simple local zeros
and their slopes. An engineering record gate requires a positive envelope and
at least one zero with slope above 10% of the initial nominal slope. It cannot
be passed by an indefinitely static nonzero field. It is not a survival gate.

Fixed-tube energy/charge flux and continuum stress flux are saved independently
of total sinks. Analysis retains the mismatch between tube change and
integrated flux/sink rates. Stress, quadrature, extraction, moving-tube and
weak-excitation error budgets remain unqualified for recoil acceptance.

## Locked bounded pilot and limits

The 13 cases use D=40, clock peak 0.001, h=0.8, dt=0.02, rho<24, |z|<48,
buffer width 4 and strength 0.12. Spatial refinement changes h to 0.4 at the
same dt. Temporal refinement halves dt at fixed h. Domain enlargement changes
only both extents, retaining h/dt/buffer width/strength. Matched isolated and
residual-reduced cases, quadrature matter phase, orthogonal internal orientation,
and neutral/structural +/- source controls complete the matrix.

The duration is 8 time units, approximately 0.526 signed clock periods. It
ends before source arrival at B, including at its fixed extraction tube.
The compact neutral momentum stencil extends support by at most one axial
cell; source support remains separated from B. This is a startup and software
qualification, not a six-period repeat, a quiet-survival result or reception.
The engineering gates require <0.1% total E/Q ledger residual, <5% waveform
control differences, actual residual reduction, usable extraction and exact
neutral symmetry/null. The future weak-mode energy allowance is shown but not
substituted for these gates. Long clocks and exchange/recoil are not evaluated.

Resources: one serial NumPy worker, native threads bounded, maximum 1,200 CPU
seconds, 1,500 wall seconds, 1,536 MiB RAM and 256 MiB retained output. The
reference preserves both components without introducing an unchecked compiled
doublet kernel. Those ceilings authorize only this bounded pilot, not the
publication-scale campaign.

Atomic checkpoints retain all six vector/real fields, three sink integrals,
geometry, full sample history, preparation, pending case/index, completed
outputs and exact identities. Resume creates a new attempt and preserves prior
bytes. Proper-time/phase/flux integrations are deterministic saved-data analysis,
so their complete input histories are retained. This does not supply Test 9
tilted-slice reconstruction slabs or production campaign storage qualification.

## Execution and next gates

```sh
OPENBLAS_NUM_THREADS=1 PYTHONPATH=src python3 .agents/scripts/run_plan.py \
  --plan docs/research/plans/gross-test-08-evolution-pilot.json \
  --repo-root . --workspace /absolute/new-evidence --execute
```

The registered CLI's analyze, report and verify stages consume saved output.

A separate [clock-phase control](plans/gross-test-08-clock-phase-pilot.json)
repeats the 13-case startup matrix with B's clock in quadrature (pi/2) relative
to A. Both clocks still use independent isolated-profile velocities, not an
imposed collective eigenmode. The isolated A cases have no B and ignore the
relative B phase. The new plan/configuration are separately locked and retain
the first run unchanged. This tests one additional phase, not all phases.
The same short horizon and resource ceilings apply. Its recipe is
`gross-test-08-clock-phase-pilot`.

The standard reader packager supplies exact plot data and the two contract PDFs.
The next registration must qualify isolated and free quiet-pair clocks over
their actual long horizons with preparation, independent grids/time/domain and
weak-mode conservation budgets. Only a qualified quiet reference permits
held-out signal selection, causal reception and recoil. Full exchange G0-G9,
20-period postinteraction survival and Test 9 remain separate implementation
and execution gates; no ledger status is promoted by this pilot.
