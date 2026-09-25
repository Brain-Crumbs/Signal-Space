# Signal Space / GROSS Test 3: router propagation

Tracking: #58. Dependencies: Test 1 (#52), Test 2 (#56), common runtime (#37). Historical epic #1 remains separate.

## Registered sector and derivation

Source: operator program v0.2 §§5.5, 6.1–6.5 and 15.3. Experiment `gross.router-propagation.v1`, model `signal-space.ss-ops-1.router-linear.v1`. This is an explicitly restricted sector of SS OPS 1, not a silent replacement of its full reciprocal event law.

For unit internal directions $\mathbf n_i$, set $P_i^\pm=(I\pm\mathbf n_i\cdot\boldsymbol\sigma)/2$. Here $I$ is the two-component identity and $\boldsymbol\sigma$ are the Pauli matrices. The physical port stencil is $(S_i\psi)(\mathbf m)=P_i^+\psi(\mathbf m-\hat e_i)+P_i^-\psi(\mathbf m+\hat e_i)$, where $\mathbf m$ is an integer label and $\psi$ is the complex two-component wave amplitude.

For $q_i=k_i\ell$, the block is $S_i(q)=\exp(-iq_i\mathbf n_i\cdot\boldsymbol\sigma)$. Forward chronological order (1,2,3) gives $U=S_3S_2S_1$. Since $U=I-i\sum_iq_i\mathbf n_i\cdot\boldsymbol\sigma+O(q^2)$, the leading phase satisfies $\theta^2=q_iG^{ij}q_j$ with $G^{ij}=\mathbf n_i\cdot\mathbf n_j$, $\theta=\omega\tau_c$, and conversion speed $v=\ell/\tau_c$. These scales and the three routing directions are assumed.

The two eigenbands are $e^{\mp i\theta}$, using principal $\theta\in[0,\pi]$. For a right-handed orthogonal triad, $\cos\theta=c_1c_2c_3+s_1s_2s_3$, where $c_i=\cos q_i$ and $s_i=\sin q_i$. Reversing order changes the last sign; it does not change $G$. The continuum generator has zero identity trace, so finite-band opposite-direction asymmetry is not by itself leading drift.

The independent reference uses $(a,\mathbf b)$ for $U=aI-i\mathbf b\cdot\boldsymbol\sigma$. Products obey $(a,\mathbf b)(c,\mathbf d)=(ac-\mathbf b\cdot\mathbf d,a\mathbf d+c\mathbf b+\mathbf b\times\mathbf d)$. Differentiate each factor by replacing $(\cos q_i,\sin q_i\mathbf n_i)$ with $(-\sin q_i,\cos q_i\mathbf n_i)$. Away from $|\mathbf b|=0$, the exact group derivative is $\partial_i\theta=[a\mathbf b\cdot\partial_i\mathbf b/|\mathbf b|-|\mathbf b|\partial_i a]/(a^2+|\mathbf b|^2)$. In units $\ell/\tau_c$, it is the group velocity. At band touchings it is undefined; those nodes remain visible.

## Locked apparatus and decision rules

- **Action:** Exact zero-wave linearization of SS OPS 1 at kappa=pi/2, lambda=0: S_i psi(m)=P_i+ psi(m-e_i)+P_i- psi(m+e_i), U=S3 S2 S1. Memories homogeneous and stationary; this sector registration is not a new full dynamics.
- **Units:** ell=tau_c=1; q=k ell, phase=omega tau_c, group velocity in ell/tau_c. Neither conversion scale is predicted.
- **Domain:** Three fixed unit triads, both routing orders, all 26 normalized nonzero vectors in {-1,0,1}^3, radii 0.02/0.04/0.08/0.16. Full periodic zone [-pi,pi)^3 on 16 and 32 points per axis, including explicit corner and half-pi probes.
- **Boundaries:** Infinite homogeneous lattice via exact Fourier blocks; random periodic boxes 8^3 and 12^3 verify stencil and norm, not a continuum PDE extrapolation. No outgoing boundary or time integrator error.
- **Initial Data:** Triads fixed in configuration. Periodic random complex fields normalized globally using runtime PCG64 sampling stream; rotate all projectors about (1,2,3)/sqrt(14) by 0.731 rad.
- **Solver:** Compose displacement coefficients from the three explicit conditional shifts. Independently compare scipy matrix exponentials, analytic quaternion product and full real-space shifts/FFT. Principal positive quasiphase in [0,pi]; both eigenbands plus/minus phase, branch derivatives undefined at touchings.
- **Tolerances:** Matrices and norm <1e-10. Fine cone residual <0.02 and adjacent halving ratio <0.65 above roundoff floor. Derivative steps 1e-5,5e-6, reference and refinement <1e-6. Full details in each criterion.

Triads: orthogonal Cartesian axes; oblique (1,0,0), (0.6,0.8,0), (0.3,0.4,sqrt(0.75)); collinear all (0,0,1). The oblique Gram is positive definite; no measured-data fit changes its coefficients. Random periodic boxes are implementation checks, not a claim of continuum volume convergence. Surface figures use a 101×101 qz=0 grid on [-0.35,0.35]² at phase 0.16.

- **coverage:** Save all 3 triads, 2 orders, 26 signed directions, 4 radii, both zone and box sizes, rotation and derivative comparisons.
- **fourier-circuit:** Stencil matrix agrees with independent matrix exponentials and real-space fields with FFT reference to <1e-10.
- **conservation:** Matrix unitarity, det U=1 and total wave norm errors <1e-10.
- **continuum:** Maximum |phase^2-q.G.q|/|q|^2 <0.02 at radius 0.02; each adjacent fine/coarse error envelope ratio <0.65 unless coarse error <=1e-10.
- **triad-rank:** Gram matrix ranks [3,3,1] for orthogonal, oblique, collinear, with rank tolerance 1e-10.
- **order-control:** Orthogonal trace matches the signed triple-sine formula to <1e-10; maximum order phase difference >1e-4 for each independent triad.
- **rotation:** Common SU(2) conjugation agrees with rotated-projector stencil to <1e-10.
- **group-refinement:** Central steps 1e-5 and 5e-6 agree with independent analytic quaternion derivative and each other to <1e-6 away from band touchings (vector norm >1e-6).
- **full-zone:** Both 16^3/32^3 periodic-zone samples agree with quaternion reference to <1e-10; nested samples agree <1e-10; explicit node probes agree <1e-10; orthogonal grids detect >1 zero node and >=1 pi node.

The full-zone grids include their periodic negative endpoints, not duplicated positive endpoints. All eight {-pi,0} corners and eight {±pi/2} points receive separate matrix probes. Node counts use distance <1e-10 to zero or pi; no exhaustive nodal or topological-charge claim. Errors are deterministic engineering tolerances, not confidence intervals. Missing/nonfinite evidence blocks a pass.

## Figures and limits

- **cone-sections:** Which projector arrangements yield an isotropic, anisotropic or degenerate cone? Three exact low-frequency contours over leading Gram contours in the qz=0 plane.
- **continuum-convergence:** Does the actual circuit approach its predicted cone as wavelength grows? Maximum squared-phase residual by radius and triad, for both orders.
- **order-and-direction:** Is opposite-direction asymmetry a finite-band order effect or leading drift? Signed order differences and omega odd divided by |q| for a fixed body diagonal.
- **full-zone-spectrum:** What additional low and pi-quasifrequency modes are hidden outside the origin? Six full-zone sections at qz=0 and -pi/2 with sampled node counts at both resolutions.
- **group-directions:** Does the energy-transport direction follow the wavevector in the oblique case? Measured and leading-cone group vectors for xy directions at smallest radius.
- **numerical-audit:** Do explicit port shifts conserve amplitude and agree with the independent Fourier reference? Norm/FFT residuals for both finite periodic boxes and global matrix/refinement checks.

Each figure preserves exact plot data and Question, Reading, Significance, Limitation. Rendering cannot alter analysis classifications. The complete physical memory branches belong to Test 4; freezing the background for this exact linear wave block does not show their absence. A Test 3 pass does not establish a clock, detector, particle species or emergent spacetime.

## Execution and next calculation

Resource ceiling: 120 CPU/wall seconds, 512 MiB memory, 32 MiB raw output. Single-thread BLAS. Execute through the locked registered gateway, using `python3 .agents/scripts/run_experiment.py --experiment gross-test-03 --output ../gross-test-03-output`. The same recipe is available in Actions > Run experiment > gross-test-03 after merge. No result is automatically committed.

Next discriminator: Test 4 complete zero-wave tangent map with physical memory variation, before a bounded search for a self-consistent nonzero periodic background. Track Test 11 directional diagnostics without promoting them to an invariant detector record.
