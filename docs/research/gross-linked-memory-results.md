# v0.3 linked-memory campaign: deformation and finite-time records

Executed 13 October 2026 using the unchanged SS OPS 1 model and the
[validation-v2 lock](plans/gross-linked-memory-v2.json). The full campaign
technically completed: seven preparations over 64 A-B cycles, all six controls,
both operator tolerances and exact sample grids, and two 32-cycle sensitivity
studies with all 16 physical directions. All 72 expected raw datasets are saved.
The formal scientific result is **fail: 5 pass, 2 fail, 2 unresolved**.

The strongest conclusion is exact: complementarity alone does not persist
continuously or guarantee return after a linked A-B cycle. A post-run exact
first-cycle counterexample is independently reviewed below. The frozen
numerical endpoint criterion remains unresolved; its required global numerical
comparison fails at long horizon. No threshold, horizon, preparation or equation
was changed after seeing the result.

## Exact mechanism and endpoint counterexample

During one active event, the other memory is fixed. With
$C=P_A+P_B-I$, $D=dd^\dagger$ and $d=z_i-z_j$,
$C'=-i\kappa[D,P_{\mathrm{active}}]$.
For active-plus and active-minus,
$\|C'_A(0)\|_F=\sqrt{2}\kappa/3=0.740480489693\ldots>0$.
This analytically refutes universal continuous complementarity. The dark word
and isolated commuting events remain valid restricted persistence controls.

The unchanged initially commuting preparation has
$z_1=e_1/\sqrt2$, $z_2=0$, $z_3=e_2/\sqrt2$,
$P_A=e_1e_1^\dagger$, $P_B=e_2e_2^\dagger$.
Event A swaps its wave into shared port 2 at $\kappa=\pi/2$ while $P_A$ stays
fixed. Event B therefore starts with $d=(e_1-e_2)/\sqrt2$. Its exact gate uses

$$
S_B=D_B+2P_B=
\begin{pmatrix}1/2&-1/2\\-1/2&5/2\end{pmatrix}
=\frac32I+M,\qquad M^2=\frac54I.
$$

Up to an irrelevant memory spinor phase,
$w_B(s)=\exp(-i\kappa Ms)e_2$. Hence

$$
|e_1^\dagger w_B(1)|^2=\frac15\sin^2\!\left(\frac{\kappa\sqrt5}{2}\right),
\qquad
c_{AB}=\sqrt{\frac25}\left|\sin\!\left(\frac{\pi\sqrt5}{4}\right)\right|
=0.621616026790\ldots>0.
$$

Here $c=\|C\|_F$ and $c^2=2\mathrm{tr}(P_AP_B)$ for the two unit rays.
The sine is nonzero because $\sqrt5/4$ is not an integer. The saved exact-gate
first A-B endpoint is 0.6216160267903694; closed-form evaluation is
0.6216160267903696. This is a **post-run exact-law endpoint counterexample**,
separate from the frozen unresolved numerical endpoint check. It does not
retroactively change that check or the locked plan.

## Frozen checks and numerical limits

| Check | Status | Recorded maximum or reason |
| --- | --- | --- |
| coverage | pass | 72 expected raw files |
| coherent-equivalence | fail | 1.0750772e-6, against 1e-9 |
| conservation | pass | 9.3254139e-11, against 1e-9 |
| null-commuting | pass | 8.8817842e-16, against 1e-9 |
| description-controls | pass | 1.2904808e-10, against 1e-9 |
| tangent-refinement | pass | 1.7701681e-6, against 1e-4 |
| continuous-complement | fail | exact nonzero initial derivative |
| endpoint-complement | unresolved | required global numerical comparison fails |
| prediction-certification | unresolved | loose bound; missing numerical/readout enclosures |

Coherence-minus first exceeds the comparison threshold in A of cycle 22
(zero-based gate 42); initially-commuting first exceeds it in A of cycle 57
(gate 112). Both active preparations meet the comparison limit through all
64 cycles, with maxima 8.59425e-11 and 8.54686e-11. These per-case prefixes
are descriptive saved-data diagnostics, not newly accepted run horizons.

The pure coherent lift is derived algebraically, retaining all cross-port
blocks. Its numerical implementation comparison fails globally; this does not
refute the mathematical lift or establish chaos, a convergence rate or physical
instability. The normalized phase witnesses have identical independent local
wave rays and initial event energies 0 and $\kappa$ for total wave norm 1.
Mixed-state closure remains unestablished. Good N/J and event-H ledgers do not
certify trajectory accuracy; H is conserved inside a gate, not across switching.

| Initially complementary case | First full A-B endpoint c | Largest full A-B endpoint c | Cycle-64 c |
| --- | ---: | ---: | ---: |
| dark | 0 | 0 | 0 |
| initially-commuting | 0.621616 | 0.621616 | 0.194227 |
| active-plus | 0.464434 | 0.608929 | 0.252383 |
| active-minus | 0.260592 | 0.547344 | 0.061716 |

The canonical endpoint criterion includes *all* A and B endpoints. For example,
initially-commuting has maximum 0.625965 over all gate endpoints, which differs
from its full-A-B-endpoint maximum 0.621616. Sampled returns cannot establish
continuous or universal invariance.

## Useful empirical records, unresolved certificate

Both centered steps and their direct difference pass the unchanged state and
record derivative gate at all 64 saved prefixes of each 32-cycle active study.
The input chart retains 12 real wave directions and two horizontal directions
for each memory, including orientation and changes of conserved quantities.

| Quantity, all saved prefixes through 32 cycles | active-plus | active-minus |
| --- | ---: | ---: |
| Peak finite-time singular amplification | 168.27847 | 103.51826 |
| Final-prefix singular amplification | 159.67835 | 103.51826 |
| Max signed 1e-6 basis record error | 2.888845e-5 | 2.242405e-5 |

The maxima include A/half-cycle prefixes. All tested gate-endpoint records are
below the 2.5e-4 preparation allocation and 1e-3 total target. This does not
bound arbitrary combinations in the whole initial-error ball, every within-gate
readout or later times. No verified recurrence is supplied, so the singular
amplifications are not Floquet stability data.

The exact-region comparison gives the conditional preparation bound
$\min(2n,K\epsilon\exp(2LC))$, where $n=(1+\epsilon)^2$,
$L=|\kappa|(1+n+\sqrt{(1-n)^2+16n})$ and $K=4\sqrt{n+n^2}$.
At $\epsilon=10^{-6}$ it reaches the range cap 2.000004000002 after one full
cycle, leaving zero useful conservative full cycles. It never resets at a
switch. This loose upper bound does not prove an observed prediction failure.
Validated accumulated numerical residual/roundoff and readout enclosures are
absent; end-to-end certification remains unresolved.

## Evidence, review and next question

Run `run-e350aab835156851`, attempt `attempt-0001`, analysis
`analysis-0001-3daf98c8`, original canonical report `report-0001`; source clean
merged commit `2a00525036008fb3fd7d8bc119cd1a0929957618`, plugin 1.0.1.
The plan lock, normalized config identity, full packet hashes and durable
artifact locators are in the [compact result record](gross-linked-memory-results.json).
The packet is `GROSS_v03_Linked_Memory_Executed_Test_Packet.zip`; the standalone
intuition report is `GROSS_v03_Linked_Memory_Results_and_Interpretation.pdf`.

A fresh independent reviewer reconstructed comparisons and signed records from
raw arrays, checked the first-word proof and found no blocker to these
negative/limited conclusions. Its original reporting objections and resolutions
are preserved with scripts and measurements. All 8 intuition PDF pages, 7
reader-results pages and 6 setup pages were rendered and visually checked.
The canonical run and both original/reviewed reader exports verify together;
all original evidence and report bytes remain unchanged. Integrity verification
is not a numerical certificate. Worker wall time is about 21.36 seconds and
pipeline time 47.385 seconds; CPU/RSS metrics are unavailable, not measured zero.
The original 300 CPU/wall-second, 1024 MiB and 128 MiB ceilings were retained.

Next: derive a trajectory-dependent uniform record-error bound around the same
active seeds through 32 cycles, for every physical initial discrepancy at most
1e-6. Retain all wave/memory directions, nonlinear remainders and accumulated
residual/roundoff/readout enclosures. Compare to the unchanged allocations;
identify the obstruction before any newly locked numerical run. Restricted
non-dark complementary-family classification and a separate coherence-minus
precision diagnosis remain ranked follow-ups. No follow-up has run.

This F0/F2/C1 seed changes no Tests 1-11 classification or prerequisite, and
does not establish the four-ray classification, physical space, binding, proper
time or an autonomous clock. Candidate B continuum results remain separate.
Literature originality was not assessed.
