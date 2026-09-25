# Test 3: findings, interpretation and next calculation

Run `run-915ed88048939f8f`, analysis `analysis-0001-53e821db`, report `report-0001`. Technical execution completed; all nine locked scientific checks passed. This is the requested homogeneous linear router audit, with 624 low-wave-number comparisons. The same manual-workflow recipe completed locally in 19.618 seconds. Hosted dispatch and artifact upload have not been executed.

## What the evidence establishes

The actual conditional port shifts reproduce the independently calculated Fourier operator: maximum matrix/field reference error 6.78e-16, and maximum unitarity/determinant/norm residual 6.66e-16 against the locked 1e-10 limits. A global rotation of all projectors changes the matrix representation by the expected conjugation (5.55e-16 residual). Both periodic box sizes and both routing orders were checked.

The leading propagation shape is controlled by the projector Gram matrix G, whose entries are the internal direction overlaps. Orthogonal directions give eigenvalues (1,1,1); the oblique arrangement gives approximately (0.349341,0.706878,1.943781); collinear directions give (0,0,3), up to roundoff. The same internal two-component algebra therefore permits a nondegenerate anisotropic cone or a rank-one propagation law, depending on the supplied routing geometry.

The maximum squared-phase discrepancy divided by |q| squared is 0.00774245 at |q|=0.02, against the locked 0.02 gate. The largest adjacent fine/coarse error ratio above the numerical floor is 0.497147, below the locked 0.65 limit. This supports the derived long-wavelength expansion for this sector. The value is a normalized squared-dispersion residual, not a universal relative speed error or statistical uncertainty.

Reversing the block order changes the signed triple-sine correction while preserving the leading Gram cone. Opposite directions have finite-band differences even though this benchmark has no leading identity drift. The order-control effect exceeds the frozen 1e-4 detection threshold. The smallest of the two independent triads' maximum order differences is 0.00987207 radians. The analytic group derivative and central-difference measurement agree to 1.12e-7; step halving changes it by at most 8.39e-8. Band touchings are explicitly excluded from derivatives, not from the spectrum.

The orthogonal circuit has eight sampled zero-quasiphase points and eight sampled pi-quasiphase points at both 16^3 and 32^3 resolution, for each order. Explicit corner and half-pi matrix probes corroborate the selected nodes. The oblique grid detects four of each at these resolutions; this lower count is not evidence that other off-grid nodes are absent. Collinear zero/pi sets grow from 256 to 1024 sampled points as the grid doubles, consistent with nodal surfaces. These are sampling observations, not a complete topological classification.

## How to read the figures

- **Cone sections:** the circle, tilted ellipse and pair of lines visualize isotropy, anisotropy and loss of nondegeneracy. They are qz=0 sections through a predicted frequency surface, not reconstructed physical space.
- **Continuum convergence:** compare errors across radii. The independent-triad envelopes shrink with wavelength; collinear errors are already at roundoff. No metric coefficients were fitted to achieve agreement.
- **Order and direction:** the odd directional contribution divided by |q| decreases toward the origin. This distinguishes the observed finite-band correction from a leading drift term in this specified benchmark.
- **Full-zone spectrum:** the extra zero and pi branches prevent a near-origin cone from being mistaken for a unique physical species. All data are wave-sector data; stationary memory degrees of freedom require the next test.
- **Group directions:** oblique geometry sends group transport in directions that need not align with the wavevector. The figure projects the vectors onto xy; the CSV retains all components. No wavepacket or receiver was evolved.
- **Numerical audit:** norm and independent Fourier checks are near machine precision. Derivative residuals have a different, explicitly looser threshold. The two periodic boxes audit implementation, not continuum volume convergence.

The report and all six figures were visually inspected, including all five setup PDF pages and all eight results PDF pages. Each figure has its own Question, Reading, Significance and Limitation in `figures/figure_index.json` and the results PDF. Exact plot data remain in `results/data/plot-data/`; the checks are in `results/tables/checks.json`.

## What remains open

The incidence graph, three translation directions, homogeneous background and conversion scales ell and tau_c are supplied. The calculation does not show their autonomous emergence. Wave-norm conservation is not an identification of physical energy-momentum. The full reciprocal model's memory orientations are physical stationary modes at the zero-wave vacuum; freezing the background for this linear wave block does not eliminate them from the full theory.

There is no bound clock, recoil experiment, invariant receiver record, gravitational dynamics, protected knot or identified fermion species. Directional drift and geometry with material response remain viable hypotheses for other backgrounds or separately specified laws. This run does not update Tests 4–10 to numerical pass, and its directional diagnostics are only preliminary evidence for the spectral part of Test 11.

## Next discriminating calculation

Run the smallest part of Test 4: derive and evaluate the complete one-cycle tangent map of a fully specified reciprocal routing circuit at zero wave amplitude, retaining every independent physical projector perturbation and explicit port transport. Separate a memory ray's redundant common phase from physical changes in its orientation and overlaps. Compare full-memory and frozen-memory spectra without deleting stationary branches.

The strong shared-cone hypothesis predicts that every physical sector belongs to the same nondegenerate characteristic family. The existing analytical prediction instead gives propagating wave branches plus stationary physical memory branches at this vacuum. Numerically confirming that obstruction would reject the strong hypothesis here while leaving a wave geometry coupled to material memory as an open interpretation. That weaker interpretation still needs a derived response law and independent clock/transport predictions; a label does not establish it.

Only after the complete circuit is specified should a separate bounded plan seek one self-consistent nonzero periodic background and its full tangent spectrum. Do not select an arbitrary nonzero wave on externally frozen projectors and call it a background solution. Candidate B's action/clock tests can proceed independently of this microscopic obstruction.
