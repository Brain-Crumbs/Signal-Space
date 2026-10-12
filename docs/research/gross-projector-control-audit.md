# Projector architecture and control/residual source audit

Date: 12 October 2026. Scope: comparison and research-program integration,
not a new scientific run. Companion: [program v0.3](gross-research-program-v0.3.md).

## 1. Finding

The latest projector/memory program does not presume physical spacetime.
The four-dimensional continuum assumption belongs to Candidate B.
The repository entry point obscured this separation by calling the older
two-candidate v0.2 paper the current program, while the later mathematical
program and control/certification work were separate documents.

This revision makes those tracks discoverable together. It preserves the
implemented v0.2 actions, canonical experiment bytes and Tests 1-11 classifications.
An improved control representation does not supply a new physical law.

## 2. Architecture comparison

| Layer | What already exists | Supplied assumptions | Unresolved task / change |
| --- | --- | --- | --- |
| Pauli/projector algebra | Rank-one ray sphere, overlap, complement, balanced frames, determinant polarization | Complex Hilbert inner product; selected matrix dimension and projector rank | Separate internal operator coordinates from physical coordinates; specify higher-dimensional extensions |
| Coherent signals and memory | Complex port amplitudes and independent projector memories; reciprocal Hamiltonian event | Canonical structure, coupling and participating ports | Retain relative port phase; an operator-only description needs coherent blocks, not independent local rays alone |
| Linked/tessellated spaces | Explicit graphs, transports, schedules, exact ordered maps and conditional spectra | Incidence, optional embedding, order, boundaries/delays | Study frame persistence, full active spectra, identification and incidence selection separately |
| Control/residual methods | Adapted structure/phase/remainder coordinates; sensitivity/correction formulas; a specified hoop invariant-region certificate | Model, norm, state region, inverse/twist bounds and approximation hypotheses | Derive these bounds for the actual projector or continuum model; no automatic theorem transfer |
| Candidate B | Closed continuum action, core and bound clock; calibrated radial reception | Four-dimensional domain, coframe metric, universal coupling, Einstein action; flat decoupling for current matter runs | Keep as a separate benchmark; Test 8 is not a foundation prerequisite or emergence theorem |
| Microscopic-to-continuum bridge | Conditional propagation/cone and effective-response calculations | Charts and spectral/scaling conditions where used | Supply the actual map, stable regime, complete memory response, limit and record-error bounds |

## 3. Source identities and freshness

These are mathematical source documents, not newly reverified run packages.
Complete extracted text was retrieved for the later mathematical source PDFs.
The supplied Markdown and relevant thematic PDFs were examined alongside them.
The findings below use the specific sections listed.

| ID | Source/version | Relevant evidence |
| --- | --- | --- |
| S1 | Signal Space Operator Foundations Roadmap v0.1, 24 September 2026, sections 1-8 | Objective explicitly excludes an assumed Minkowski manifold; incidence may be primitive; operator geometry and physical geometry distinct |
| S2 | [Operator Models and Experimental Program v0.2](../../research/papers/gross-operator-program-v0.2.md), retained directional revision, sections 2-9, 13, 15-17 | Candidate A event assumptions versus Candidate B four-dimensional continuum/coframe and Einstein completion |
| S3 | 00 Common Derivations, revision 1.1, 2 October 2026, M-21-M-36 | Current qualifications; active recurrence/instability, clocks, memory elimination, dimension, energy and observation |
| S4 | Polyhedral Projector Derivations, version 1.0, 2 October 2026, P-01-P-16 | Finite families of rank-one 2 by 2 projectors; internal designs and conditional cone-data reconstruction |
| S5 | Tessellation Operational Geometry, analytical candidate v1, sections 1-3 and rigidity/spectrum results | Supplied FCC embedding and face-normal identification; exact routing; no automatic shared cone or invariant rigid frame |
| S6 | Projector Geometry and Memory Research Program, version 1.0, 4 October 2026, sections 2, 4-10, 12-14 | Pure mathematics before physical-network use; six packages; four distinct geometries and explicit standing assumptions |
| S7 | Projector Geometry and Memory Theorem Atlas, version 1.0, 4 October 2026, A-G and evidence ledger | Stable result identifiers; exact gates, gluing, frame invariance, predictive quotients and bounded numerical evidence |
| S8 | GROSS Mathematical Fields and Novelty Review, 4 October 2026 | Established mathematics versus model-specific classification, inverse, architecture and obstruction opportunities |
| S9 | Perturbed Soliton and Hoop Worked Study, 10 October 2026, sections 1-6 | Exact NLS invariants; phase versus orbital structure; radiation and truncation caveats; residual-plus-stability requirement |
| S10 | Hoop and Bead Intuition Guide Verified, current Library version 2, modified 9 October 2026; section 21.7 and later sections 27-30 / Appendix A | Small residual versus inverse correction; later reported all-time invariant-region certificate for one specified motor/release family |
| S11 | Supplied thematic PDFs: Closed Active Background, Complete Physical Spectrum, Objects/Internal Clocks, Observer Geometry, Emergent Dimension and Autonomous Universal Geometry, revision 1.1 | Current active failures, operational limitations, dimension non-selection and conditional shared-geometry interpretation |
| S12 | Repository main at commit 6f04ade0f5c83fe0548bfb70159bcd7b0b4584d1 and [Test 8 draft PR #88](https://github.com/Brain-Crumbs/Signal-Space/pull/88), head 21119dba3939822211ba7a2371cc195000cb1d2f | Actual runtime/docs baseline versus unmerged doublet startup work; neither is silently replaced |

S3 and S11 explicitly label older baseline pages as historical where later
revision pages change their interpretation. S10 likewise contains earlier
open questions followed by a completed, specifically scoped barrier
certificate. Reading only an earlier section would incorrectly report the
whole guide's invariant-region problem as still uncompleted.

The separate Brain-Crumbs/CCR repository was checked at main
571c3328cc74582e46e2f693789146c1e6ee19ba. Its README/tree describe predictive
cortex and market/software work, not the hoop/projector certificate sources.
This revision does not attribute those mathematical proofs to that repository
or modify it.

## 4. Important claim corrections

### Pauli matrices, rays and dimension

Pauli matrices are Hermitian involutions, not orthogonal projectors.
The ray projector is $(I+\mathbf n\cdot\boldsymbol\sigma)/2$.
One may choose many rays in the same $\mathbb C^2$ without enlarging the
matrix. A polygon or polyhedron organizes those rays internally.

The four real coefficients of $\mathrm{Herm}(2,\mathbb C)$ admit the exact
determinant form of signature $(1,3)$. That algebraic relation does not supply
a manifold, physical derivative, incidence or causal detector records.
The original constitution already made this distinction [S1-S4].

For larger matrices, operator dimension, projector-manifold dimension,
graph dimension and measured propagation dimension remain different.
The two-component law admits chain, lattice and tree incidences [S11].
A three-component Bloch representation does not select a three-dimensional
physical graph. More internal directions do not fix the ordered dynamics.

### An exact operator reformulation retains coherence

Program v0.3 section 3 gives a direct outer-product derivation:
$W=ZZ^\dagger$ and $\dot W=-i[K(P),W]$, with
$dd^\dagger=W_{11}+W_{22}-W_{12}-W_{21}$.
Differentiating the outer product proves the first identity; expanding
$(z_1-z_2)(z_1-z_2)^\dagger$ proves the second.
Together with $\dot P=-i\kappa[dd^\dagger,P]$, they are closed for the
retained pure-state baseline with $\lambda=0$.

This specialization uses established outer-product dynamics. It establishes
representation equivalence up to common phase, not a sparse/local implementation,
a mixed-state ensemble closure or emergent spacetime.
Independent local ray projection would discard the off-diagonal information;
the opposite-phase witness in the program exposes the failure exactly.

### Residuals require a sensitivity or inverse bound

Use the declared convention $r=\dot y-f(y)$.
The exact error equation and conditional Lipschitz bound in program v0.3
follow by subtraction and Gronwall's inequality. They remain finite-time
claims unless a stronger invariant-region argument is established.
The approximate and exact states must remain within the certified region.

For a periodic or invariant object, the relevant inverse must be controlled
after valid gauge/phase treatment. A small residual near resonance can require
a large correction or admit no solution [S10 section 21.7].
Correcting the orbit does not prove its nonlinear stability.

The current hoop guide reports an invariant region containing the phase-zero
release ellipse with scaled radius $r_0\le0.04$, and whole-cycle angle bounds
0.9932 to 1.0996 radians. The entrance ellipse is not itself the invariant barrier.
Its exact motor, interval/analytic bounds, torsion and all-mode tail conditions
are essential. This audit reads the reported certificate; it neither reruns its
verifier nor transfers that result to a projector graph [S10 Appendix A].

### Current negative results remain useful

Common Derivations M-24-M-25 and Closed Active Background report an exact
connected active family and three unstable selections, not a stable extended
clock medium. Their selected values are $q=10/3,4,14/3$.
The strongest instability already occurs for homogeneous perturbations.
An exact conserved-charge differential annihilates a growing eigenvector
whose multiplier differs from one, so fixing charge cannot remove that mode
as if it were unphysical.

The registered Test 4 result in the main ledger is a different preserved
package. The supplemental active-resonance package was not rehydrated and
reverified here; its reported result is not promoted into that ledger.
An exact recurrent circuit, positive frame and small conservation error each
answer a different question from stable localization and readable timing.

## 5. What changes in the repository

| Document | Change |
| --- | --- |
| README | New research-program entry point; foundation/certification/benchmark distinction |
| Program v0.3 | Revised priorities, primitive inventory, faithful operator lift, residual obligations and scoped next work |
| This audit | Source/version comparison, current-versus-historical qualifications and integration rationale |
| [Claim register](gross-claim-register.md) | Assumptions, exact results, reported evidence and conjectures distinguished |
| [Execution architecture](architecture.md) | Software layers linked to scientific tracks |
| [Progress ledger](gross-progress.md) | Planning notice only; existing Test 1-11 classifications preserved |
| [Artifact contract](artifact-contract.md) | Claim-scope and residual-certification practices made explicit |
| Research catalog/index | New design documents discoverable; intentional index update without changed canonical evidence |

The preserved v0.2 paper is not edited. Runtime code, experiment registry,
schemas, configurations and locked criteria are not changed. PR #88 remains
separate. The new research roadmap is not an executable locked plan.

## 6. Primary mathematical anchors

- John C. Baez, [The Octonions, section 3.3](https://math.ucr.edu/home/baez/octonions/node11.html):
  established spin-factor, projective-line and Hermitian/Lorentz correspondence;
  the operator identity is not this model's physical emergence theorem.
- T. Katsaounis and I. Kyza, [A posteriori error analysis for evolution nonlinear
  Schrodinger equations up to the critical exponent](https://arxiv.org/abs/1601.02430):
  model-specific residual error estimation. Its estimator is not implemented
  by this documentation change.

No first-in-literature claim is made. The potential contribution remains a
precise result for the coupled projector law, accessible records or certified
prediction, with its nearest precedents and proof hypotheses compared.
