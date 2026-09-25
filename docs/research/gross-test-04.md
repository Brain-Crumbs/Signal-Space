# Signal Space / GROSS Test 4: complete reciprocal spectrum

Tracking #60; dependencies #56, #58/#59 and #37. Historical epic #1 is separate. Source: operator program v0.2 sections 5, 15.4, 15.11. Registered experiment `gross.full-spectrum.v1`, model `signal-space.ss-ops-1.six-gate.v1`.

## Circuit assumption and exact backgrounds

At each integer cell m there are two complex two-component waves a,b and six normalized memory rays w_j. For each axis i=1,2,3, execute an onsite event (a(m),b(m),w_(2i-2)(m)), then a disjoint bond event (a(m),b(m+e_i),w_(2i-1)(m)). Each event uses the unchanged SS OPS 1 Hamiltonian H=(pi/2)|w†(a-b)|², lambda=0, over event parameter s from 0 to 1. Six gates define one cycle. Gates within a layer are disjoint. Flat transport and this incidence are assumed. The local circuit is unitary only when memories are fixed; the full nonlinear evolution is Hamiltonian and conserves its norm/matrix ledgers.

This is a newly explicit routing ansatz. It is **not** asserted to reproduce Test 3's reduced two-component conditional shift at finite amplitude. Its auxiliary port and all independent memories are retained. One cell carries 8 real wave components and 12 physical memory components, for 20 real tangent dimensions. A memory phase w -> exp(i alpha)w is an exact local redundancy of this law; the two orientation variations orthogonal to w change its projector and cannot be discarded. Global wave phase is retained, not quotiented.

Three preregistered homogeneous period-one physical backgrounds:

- Vacuum: a=b=0; each onsite/bond pair has the +x,+y,+z Pauli rays in chronological axis order.
- Equal: a=b=(1/2,0), with the same noncollinear rays. Every difference d=a-b vanishes, so this is an exact fixed state. Nonzero intensity alone cannot create linear memory feedback here.
- Counter: a=(1/2,0), b=(-1/2,0), with all six rays w=(1,0). Each gate swaps a,b, giving six swaps per period. The waves recur; each memory acquires phase -i while its projector recurs. The physical period is one, the stored spinor representative has period four. This is a collinear active-backreaction control, not a preselected three-dimensional geometry candidate.

These backgrounds are solved analytically from the event equations and independently checked numerically. No optimizer or tuned post-run background is used. Generic non-collinear unequal-port periodic backgrounds remain an open continuation problem. The run is a bounded Test 4 calculation, not completion of every possible background search.

## Tangent derivation and independent controls

For a unit ray w choose v=(-conj(w_2),conj(w_1)); a physical variation is w(c)=(w+c v)/sqrt(1+|c|²), with complex c. The output coordinates are Re(v†P_out w), Im(v†P_out w), where P_out is the memory projector. The eight wave components are interleaved real and imaginary components. The output chart is based on the input background ray, which is unchanged at each registered gate. Centered steps h=2e-5 and 1e-5 differentiate the complete exact gate. DOP853 independently differentiates all six gates using rtol=2e-12, atol=2e-14, maximum event step 0.05.

For q=k ell, a bond gate's local input b carries exp(+i q_i); the output is transported back with exp(-i q_i). Thus its real-coordinate Bloch matrix is D_i^-1 L_i D_i, with L_i the full physical local Jacobian and D_i acting on both real components of b. Compose all six stages, including the twelve memories. This real-field Fourier construction includes q/-q conjugacy and does not mistake complex-linear waves for the complete real tangent system. We save every 20x20 map, all local Jacobians and background stage states.

In vacuum (and equal background), memories have identity evolution and decouple linearly. Independently, each complex wave port obeys U_A=product_i[(I-P_i)+exp(+i q_i)P_i], U_B=product_i[(I-P_i)+exp(-i q_i)P_i]. Products retain chronological matrix order. Their continuum generators have opposite drift vectors: v_A=-(1,1,1)/2, v_B=+(1,1,1)/2, and D=I/4. A shared coordinate drift cannot remove their relative drift. No physical clock or invariant detector record is supplied. These are tilted sectors derived from this circuit, not evidence for drift in Test 3's different stencil.

The upper signed near-origin A quasifrequency is omega_A=-sum(q_i)/2+|q|/2+O(q²). Pair q and -q within that invariant port sector; do not switch eigenbranches to improve a fit. Some signed frequencies are negative because drift exceeds the isotropic speed along some directions. This is not the positive-frequency subcritical fit proposed for later operational Test 11. The exact generator gives a prediction for all directions without a fitted metric; oblique directions are withheld from coefficient derivation.

## Locked bounds and classification

Twenty-six signed axial/oblique directions, four radii 0.02/0.04/0.08/0.16; three spectral paths across [-pi,pi] with 65 points each. Both finite-difference resolutions are saved. All twenty multipliers are shown; phase sorting is for scatter display, not a claim of branch tracking. Memory participation is Euclidean coordinate participation, not energy, and is basis-dependent within degenerate eigenspaces.

A unit memory-orientation impulse is propagated with the tangent stencil for three cycles on 9³ and 13³ periodic cells. It must stay within Chebyshev distance t at cycle t, before any wraparound; common centered regions must agree. Its squared tangent amplitude is a response visualization, not a conserved energy. The one-cycle impulse is independently Fourier checked. Norm, event Hamiltonian, memory norm and matrix charge are checked on 24 random off-background gates. There is no globally conserved circuit Hamiltonian or spacetime momentum asserted.

Numerical gates: recurrence/conservation/phase/causal/domain residuals <1e-10, Jacobian/reference/refinement <2e-6; counter full/frozen difference >1e-3, physical orientation-overlap change >1e-6. Explicit criteria are in the locked plan and plugin. Missing evidence blocks interpretation. Counter exponential instability is rejected only when low-q log modulus exceeds max(1e-5, five times matched eigenvalue-refinement error); otherwise stability remains unresolved. Finite samples and unit moduli cannot rule out Jordan growth or off-path instabilities. A kinetic positivity theorem is not evaluated.

Strong all-sector vacuum common-cone hypothesis: **fail** when the full physical memory identity block persists for all nonzero sampled q while waves propagate, with numerical controls passing. This is a scientific negative outcome and still a valid completed experiment. The equal background has the same obstruction. Counter stability is assessed separately. A geometric sector with a derived material response and autonomous clock remains unresolved; merely labeling flat modes material is not a successful explanation.

Resource ceiling: 180 CPU/wall seconds, 512 MiB RAM, 48 MiB raw output, single-thread BLAS. Immutable raw evidence, analysis and report are separate. Run through `python3 .agents/scripts/run_experiment.py --experiment gross-test-04 --output ../gross-test-04-output`. The same manual Actions recipe produces evidence/reader artifacts without automatically committing them.

## Visual questions and next step

Figures: full 20-mode spectrum with memory participation; multiplier growth and full/frozen effect; causal response to a local physical memory perturbation; paired directional drift and even cone trends; numerical and background-recurrence audit. Each includes exact plot data and Question, Reading, Significance, Limitation.

Next calculation: derive one non-collinear, unequal-port periodic background with active memory response, then lock its complete tangent/stability test. A valid common geometry must predict withheld sectors with independent numerical uncertainty. No clocks, emergent spacetime, particle identity, protected topology or stability from visual resemblance is inferred.
