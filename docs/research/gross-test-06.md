# Signal Space / GROSS Test 6: localized clock calibration

Source: operator program v0.2 §§7, 9, 15.6. This is the **flat decoupling limit** of Candidate B (`SS OCF 1`), following Test 1's operator identities and Test 5's continuum action audit. The registered variant is `signal-space.ss-ocf-1.flat-clock.v1`; its current locked plan and config live in `docs/research/plans/gross-test-06-v2.json` and `fixtures/research/gross-test-06.json`. The first locked plan is retained in `gross-test-06.json` with its run; its low-frequency BVP guesses did not converge, motivating the documented numerical continuation added in v2.

## Physical question

Does a charge supported, spatially localized core make a real clock field oscillate in a bound mode for 100 periods, with a frequency measurable from a local field trace? A rotating core phase cannot serve as the autonomous record: its density and internal projector are static. The clock field $\chi$ must provide a local sequence of zero crossings.

In units $c=\hbar=m=1$, set the constant internal direction $u_0$ and the neutral field $a=0$. The model action of §§7–8 gives

$$
\Phi=F(r)e^{-i\omega_Q t}u_0,\qquad
F''+\frac{2}{r}F'=(1-\omega_Q^2)F-2F^3+3F^5.
$$

The boundary conditions are $F'(0)=0$ and $F(\infty)=0$. For $s=F^2$, solve the distinct clock eigenproblem

$$
\left[-\nabla^2+V_\chi(s)\right]f_\chi=\Omega_\chi^2 f_\chi,
\qquad V_\chi(s)=0.25-0.4s+0.2s^2.
$$

The continuum starts at $0.25$. A bound mode requires $0<\Omega_\chi^2<0.25$ with a margin exceeding five times the mesh and box error. Removing $\nu=0.4$ while keeping the positive quadratic correction $0.2s^2$ is an independent no-well control. The full radial matter evolution retains reciprocal $\chi^2$ backreaction on the core and $0.1\chi^3$ clock nonlinearity.

## Locked bounded method

Try $\omega_Q=0.868,0.875,0.90,0.94$ at $R=80$, $h=0.1$, with declared BVP seed radii 5, 10, 20, 40, 60. When these fail to converge, continue the nearest higher solved core in frequency steps no larger than 0.005, saving the failed fixed-seed attempts. Project a regular BVP solution onto the exact evolution stencil with Newton iteration. Select the smallest trial frequency with a positive nodeless profile, a bound clock eigenvalue and $E_Q/Q<1$. Refine **independently** to $h=0.05$ at $R=80$ and $R=160$ at $h=0.1$; no new trial frequencies are introduced after seeing results.

For the accepted profile, initialize $\chi$ with the independent eigenfunction at peak field $0$, $5\times10^{-4}$, $10^{-3}$ and $2\times10^{-3}$; the clock canonical momentum starts at zero. Evolve the nominal amplitude for 100 eigenperiods and all three control preparations for 20. Also evolve the nominal amplitude on refined and enlarged grids for 20 periods. A local receiver samples $\chi$ at $r=h$. Its positive-going zero crossings, obtained by interpolation between adjacent saved samples, determine the recorded frequency. The global mode projection is only a leakage diagnostic, never substituted for the local record.

Use radial variables $u=r\Phi$ and $w=r\chi$, regular zero conditions at the origin, and Dirichlet values at the finite outer radius. The outer 20 radial units have declared momentum damping; save its energy and charge sink with the core charge balance. The nominal Verlet step is $\Delta t=0.04$, halved with the fine grid. Save the actual samples and solver provenance. The finite sponge is part of the registered numerical model, not a claimed transparent boundary condition.

The radial core $L_+$ and $L_-$ Hessian eigenvalues, a neighboring branch charge slope, $E_Q/Q$, and 100-period core peak drift provide a **bounded radial branch screen**. This does not rule out higher angular or nonlinear fragmentation. The separate 20-period grid/domain runs estimate frequency error, not a 100-period continuum lifetime. Full criteria and figure questions are fixed in the plan before execution. A failed physical criterion remains a valid completed calculation.

## Reading and next decision

The figures show the core and mass well, independent bound/trapping controls, local early and late ticks, and the mode/charge ledgers. Each has exact plot data and a four-part interpretation. Test 7 may freeze this calibration only if its bound, record, lifetime, controls and numerical checks pass within their stated spherical regime. This result cannot establish emergent spacetime, a photon, protected knots, full stable Q-balls, or an invariant remote detector record.

The manual Actions recipe is `gross-test-06`. It uploads evidence and a reader package; it does not automatically commit results. The branch PR is associated with #66 and remains for user review/merge.
