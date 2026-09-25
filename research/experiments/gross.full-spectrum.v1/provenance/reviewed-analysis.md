# Test 4: full reciprocal spectrum - interpretation and next calculation

Run `run-5a55cb5041050589`; analysis `analysis-0001-bceef551`; report `report-0001`. Technical pipeline completed in 22.774 seconds. Scientific classification: **fail for the strong all-sector vacuum common-cone hypothesis**. This is not a failure of the numerical pipeline or a verdict on every nonzero background.

## What this calculation establishes

The model is SS OPS 1 with a newly explicit six-gate routing ansatz: two wave spinors and six independent memory projectors per cell, onsite then nearest-neighbor events in each axis. The local Hamiltonian is unchanged. The circuit is not asserted equivalent to Test 3's reduced two-component stencil. Its incidence, label axes, and conversion scales remain assumptions.

All 20 physical real tangent dimensions are retained: eight wave components and twelve memory orientations. Only the six unobservable memory-spinor phases are removed. Changing a physical orientation changes a projector overlap by 9.999e-5 in the control, whereas a memory phase change produces at most 1.67e-16 output difference. These distinguish physical stationary modes from redundant coordinates.

| Background | Verified behavior | Scientific interpretation |
| --- | --- | --- |
| Vacuum, noncollinear memories | Twelve stationary memory dimensions coexist with propagating wave sectors; memory identity error 1.122e-10 | Fails strong all-sector nondegenerate common-cone claim at this vacuum |
| Equal nonzero waves, noncollinear memories | Same linear decoupling; full/frozen difference 1.618e-10 | Nonzero intensity alone does not remove the obstruction; the gate's incoming difference remains zero |
| Opposing nonzero waves, collinear memories | Full/frozen difference 0.4444444445; physical memory perturbation seeds propagating wave response | Genuine reciprocal linear response is activated. This collinear control is not an accepted three-dimensional common-geometry background |

The opposing-wave background has no detected exponential instability at the sampled points: maximum low-q log multiplier modulus is 3.931e-11 per cycle, versus eigenvalue-refinement difference 7.914e-10 and a preregistered minimum growth gate of 1e-5. Its largest sampled eigenvector condition number is 10.83. **Stability remains unresolved**: finite points, unit moduli and these conditioning observations do not prove the absence of Jordan growth, unsampled instability or nonlinear instability. No kinetic-positivity theorem has been evaluated.

The exact nonzero backgrounds were obtained analytically from the event law, then numerically checked, without tuning a search to an observed spectrum. Every stage's wave/memory spinors are saved. For opposing waves, projectors and waves recur after one cycle; memory spinor representatives acquire -i per cycle and recur after four. The quotient does not discard physical orientation dynamics.

## Accuracy and causal checks

All eight implementation/control criteria pass. Strong vacuum geometry fails; counter stability is unresolved. See `results/tables/checks.json`, `results/tables/analysis.json`, and `results/data/plot-data/summary.json`.

| Check | Largest measured residual |
| --- | ---: |
| Physical period-one recurrence | 3.674e-16 |
| Local norm, memory norm, Hamiltonian and matrix-charge conservation | 1.984e-15 |
| Full-map differential step refinement | 4.712e-10 |
| Independent DOP853 local Jacobian | 6.106e-11 |
| Independent vacuum Fourier construction | 1.571e-10 |
| One-cycle local impulse versus Fourier map | 1.390e-16 |
| Outside causal support after three cycles | 0 in saved arithmetic |
| 9-cubed versus 13-cubed centered-domain response | 0 in saved arithmetic |

There are 17,940 saved mode rows: 20 multipliers for each of 104 low-wave-number samples and 195 spectral-path samples, for three backgrounds. Full-map refinement is measured at the low-wave-number points; full-zone paths are diagnostic samples, not a complete stability scan. Every physical branch is retained. Phase-sorted scatter is not continuous mode tracking, and degenerate eigenvector participation depends on the chosen basis.

The local impulse remains inside the causal support fixed by the circuit. This supports locality of this implementation. It does not derive physical distance from the cell labels. Its squared tangent amplitude is not physical energy. The event Hamiltonian is locally conserved during each gate; a global conserved circuit Hamiltonian or spacetime momentum has not been established.

## Directional propagation and Test 11

For vacuum/equal backgrounds, the exact independent wave-port generators give opposite drift vectors, v_A=-(1,1,1)/2 and v_B=+(1,1,1)/2, with spatial cone matrix D=I/4 in declared label units. Pairing signed near-origin frequencies agrees with this leading prediction while retaining finite-band corrections. All oblique directions were predicted from the generator rather than fitted.

Different directional speeds do not alone exclude a metric. Here, however, the two retained physical port sectors have different drift vectors, and one common coordinate shift cannot remove their difference. Stationary memory branches provide a further independent obstruction to the strong all-sector claim. The drift magnitude exceeds the isotropic speed in some directions, so these are signed-frequency diagnostics, not the subcritical positive-frequency fitting protocol of the later operational Test 11. No autonomous clock or invariant detector record is measured.

## What the figures change

- `complete-spectrum`: exposes the physical flat branches that the wave-only Test 3 could not test, and the changed spectrum when opposing waves activate memory response.
- `growth-backreaction`: separates a clear reciprocal response from the much stronger, still unresolved stability claim.
- `causal-memory-response`: shows an orientation perturbation remaining stationary in two backgrounds and driving a local causal response in the opposing-wave case.
- `directional-sectors`: keeps routing-derived drift distinct from finite-band asymmetry and from a coordinate-only relabeling.
- `accuracy-audit`: ties these interpretations to background recurrence, independent integration/differentiation, conserved quantities and domain controls.

Five figures and all twelve setup/results PDF pages were visually reviewed. Exact plot data, source specifications and four-part interpretations are included. Local full validation passed: 172 JavaScript tests, 73 Python tests, agent contract tests, lint/types, archive/export checks and builds. Browser integration could not launch Chromium; OS dependency installation is denied in this environment. The GitHub-hosted dispatch/upload has not been run; the full local Actions recipe completed.

## Next discriminating calculation

Derive a **noncollinear, unequal-port periodic background** of this same explicit circuit with active memory response. The present equal-port solution has independent axes but no linear memory feedback; the opposing-port solution has feedback but collinear projectors. The next question is whether those two properties can coexist in a self-consistent solution.

Before a broader scan, write a reduced periodicity system using the exact event map, expose symmetries and conservation constraints, and bound a continuation or root-finding search. Save failures as well as accepted roots. Then lock a separate calculation of its full physical Floquet map, with differential and domain refinements.

Competing signatures: (1) an accepted background yields a stable candidate signal sector whose derived cone predicts withheld port and memory sectors; (2) memory response persists but distinct propagation structures or growth remain; (3) no periodic solution is found in the declared bounded family, leaving existence unresolved outside that family. A material-response interpretation needs an independent response law and an autonomous clock; it cannot be accepted by relabeling unexplained branches.

This result supports investigating background-dependent memory response. It does not establish emergent spacetime, protected topology, a particle spectrum or a viable clock. The independent continuum path, Tests 5 then 6, remains available.

## Attempt history

A first preflight stopped before execution because formatting changed configuration bytes after the stored hash. The configuration hash and plan lock were corrected before any scientific run. An early completed numerical run encountered an analysis-directory creation error, then was reanalyzed from its preserved raw bytes. A second completed numerical run encountered a plotting API error. The corrected full recipe produced the selected final run. Equations, numerical settings and scientific thresholds were unchanged during these pipeline fixes. Prior canonical runs and failure logs are preserved in the repository provenance directory; none is relabeled as the final run.
