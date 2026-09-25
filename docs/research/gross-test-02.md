# Signal Space / GROSS Test 2

Tracking: #56. Dependencies: Test 1 (#52) and registered runtime (#37). Historical epic #1 is a separate scope. Source: [operator program v0.2](../../research/papers/gross-operator-program-v0.2.md), sections 5 and 15.2. The supplied September 24 directional revision has SHA-256 `c733c958fde54c810c38889e5096de54358a77cc10e69d9f885870832595e123`.

Experiment `gross.reciprocal-events.v1` registers Candidate A as model `signal-space.ss-ops-1.v1`. It does not modify the algebra plugin, Candidate B, or historical charged-scalar equations. The Hamiltonian and canonical symplectic law are assumptions; the following conserved quantities and exact solution are derived from them.

## Equations and exact control

At one event, $z_1,z_2\in\mathbb C^2$ are incoming waves and $w\in\mathbb C^2$ is a unit memory. Let $d=z_1-z_2$, $P=ww^\dagger$, $N=z_1^\dagger z_1+z_2^\dagger z_2$, and $s\in[0,1]$ be a dimensionless gate parameter. All amplitudes and couplings are dimensionless. $s$ is not calibrated proper time.

$$
H=\kappa d^\dagger P d+\frac{\lambda}{2}N^2,
\quad i\dot z_1=\kappa Pd+\lambda Nz_1,
\quad i\dot z_2=-\kappa Pd+\lambda Nz_2,
\quad i\dot w=\kappa dd^\dagger w.
$$

Set $D=dd^\dagger$. Then $\dot D=-2i\kappa[P,D]$ and $\dot P=-i\kappa[D,P]$. Therefore $S=D+2P$ is constant. The scalars $q=d^\dagger d$, $m=w^\dagger w$, and $N$ are constant too. For $a=z_1+z_2$ and $R(s)=\exp(-i\kappa Ss)$,

$$
a(s)=e^{-i\lambda Ns}a(0),\quad
d(s)=e^{i(\kappa q-\lambda N)s}R(s)d(0),\quad
w(s)=e^{2i\kappa ms}R(s)w(0),\quad
z_{1,2}(s)=\frac{a(s)\pm d(s)}2.
$$

This independent constant-matrix solution audits DOP853 integration. The primary solver integrates all three participants; it never freezes or renormalizes a memory during evolution. $N$, $m$, $J_e=z_1z_1^\dagger+z_2z_2^\dagger+P$ and $H$ are conserved during each gate. With flat wire transport, the complete-cut sum of all wave outer products and all memories is conserved. There is no asserted global circuit energy or identification of $J_e$ with spacetime energy-momentum.

## Locked apparatus

Four seeded noncollinear preparations use eight wave wires numbered 0-7 and four memory wires numbered 8-11. Independent complex Gaussian directions are normalized; wave norms are independently uniform in [0.35,0.85], memory norms equal one. PCG64 uses the runtime initialization stream from root seed 2026092502. No realization is rejected after observing a control.

Each row lists two wave wires and one memory wire. Earlier rows on a shared wire are causal predecessors. Physical wire transport is identity; no hidden interactions or additional routing occurs.

| Layer | Events and participants                            |
| ----- | -------------------------------------------------- |
| 0     | E0=(0,1,8); E1=(2,3,9); E2=(4,5,10); E3=(6,7,11)   |
| 1     | E4=(1,2,8); E5=(3,4,9); E6=(0,5,10); E7=(6,7,11)   |
| 2     | E8=(0,3,8); E9=(2,5,9); E10=(1,4,10); E11=(6,7,11) |

Events within a layer are disjoint. The primary order is 0 through 11; the alternative reverses each layer: 3,2,1,0,7,6,5,4,11,10,9,8. The branch on waves 6,7 and memory 11 stays disconnected. Reuse follows ordered memory wires, never an instantaneous cycle.

Use $\kappa=\pi/2$ and both $\lambda=0,0.1$. DOP853 uses relative tolerance $2\times10^{-12}$, absolute tolerance $2\times10^{-14}$ and maximum internal step 0.125. Repeat at half both tolerances; save nine equally spaced gate samples. Independently compare entire circuit histories to the exact solution. No spatial grid exists; mesh or box convergence is inapplicable. The complete cut and disconnected branch are the relevant boundary/accounting controls.

At each event, sample three normalized squared overlaps $|x^\dagger y|^2/(|x|^2|y|^2)$ for the pairs $(z_1,z_2),(z_1,w),(z_2,w)$. A zero participant makes the overlap undefined and stops analysis; no regularization is silently added. These are local scalar diagnostics, not readings of an established clock.

## Controls and decision criteria

- **Conservation:** divide changes in scalar quantities by $\max(1,|Q(0)|)$, and matrix changes by $\max(1,\|Q(0)\|_F)$. Require every sampled event ledger, projector residual and complete-cut charge residual below $10^{-9}$ at both tolerances. Projector idempotence uses an absolute Frobenius residual.
- **Equivalent histories:** state-array Frobenius differences divided by $\max(1,\|\mathrm{reference}\|_F)$ and maximum absolute overlap differences must be below $10^{-9}$ for tolerance halving, legal schedules and independent local frames. Exact-solution comparison is below $10^{-9}$ too.
- **Local frames:** draw independent $U(2)$ matrices $V_e$ per event. Store outgoing wires in their producing frame; transport into the next event with $V_eV_{\mathrm{previous}}^\dagger$. Compare outputs after transforming back and compare invariant overlaps. This tests the entire circuit, not just one global rotation. Flat physical transport remains unchanged.
- **Causal Jacobian:** for preparation 0 at each lambda, perturb all 32 real wave directions and eight physical memory-ray tangent directions. A unit memory $w=(a,b)$ has complex orthogonal tangent $v=(-\overline{b},\overline{a})$; use $v,iv$ and normalize the perturbed initial memory. Central-difference steps are $10^{-5}$ and $5\times10^{-6}$. Retain all 12 event participant outputs. Ancestor sets are constructed from incidence alone. Maximum outside-ancestor response must be below $10^{-9}$; maximum inside response must exceed $10^{-4}$ at each step and lambda. Maximum componentwise step-halving difference must be below $10^{-6}$.
- **Shared-memory reversal:** two gates on wave pairs (0,1) and (2,3) share memory 8. Reverse their order, changing the physical incidence. Their final memory projectors must differ by more than $10^{-4}$ in every preparation/coupling. Compare rays, not a physically irrelevant common memory phase.
- **Frozen-memory intervention:** evolve E0 with $\dot w=0$ only for this deliberately external-memory control. Its exact solution is $d(s)=e^{-i\lambda Ns}[I+(e^{-2i\kappa s}-1)P]d(0)$ and $a(s)=e^{-i\lambda Ns}a(0)$. Numerical agreement must be below $10^{-9}$. Relative total matrix-charge defect and the primary model's memory-projector response must each exceed $10^{-4}$ in every preparation/coupling.

These are prospective engineering thresholds, not confidence levels. Completed evidence violating any criterion fails; missing/nonfinite evidence is unresolved and never passes. The legal-schedule Jacobian null does not prove locality for every possible input. Directional speed, drift, anisotropy, full spectra and clocks remain unevaluated.

## Resources, figures and execution

Solver limits: 120 CPU seconds, 120 wall seconds, 512 MiB memory, 32 MiB attempt output. The registered estimate is conservative, not a benchmark. Single-thread BLAS is recorded. No checkpoint/resume is advertised; partial attempts and failure logs remain evidence.

Four required figures show causal incidence/Jacobian support, reciprocal matrix balance, numerical accuracy and description invariance, and physical order/frozen-memory interventions. Raw state arrays, exact plot data and four-part interpretations accompany the standard PDFs. Log display floors never replace saved zeros.

Use **Actions > Run experiment > Run workflow > gross-test-02** after merging the PR. The same clean-checkout recipe runs locally:

```sh
python3 .agents/scripts/run_experiment.py --experiment gross-test-02 --output ../gross-test-02-output
```

The recipe validates the locked plan/config, runs through `.agents/scripts/run_plan.py`, analyzes, renders, verifies and packages. Choose a new output directory each time. GitHub uploads evidence and reader artifacts; no results are automatically committed and no npm test suite is added to CI. A completed scientific failure remains downloadable.

If Test 2 passes, the next discriminator is Test 3's exact router dispersion and full-zone controls, with Test 4 memory modes retained and Test 11 directional comparisons kept open. Finite causal support alone is not a metric.
