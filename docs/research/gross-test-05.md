# Signal Space / GROSS Test 5: continuum action audit

Source: operator program v0.2 §§7–8, 12.3, 15.5. This is Candidate B, SS OCF 1, distinct from the SS OPS 1 circuit in Tests 2–4. The registered experiment is `gross.continuum-action.v1` and the action-audit model is `signal-space.ss-ocf-1.action-audit.v1`. Its locked plan and config are in `docs/research/plans/gross-test-05.json` and `fixtures/research/gross-test-05.json`.

## Question and method

Does direct differentiation of the written SS OCF 1 action yield the proposed common matter principal structure, including backgrounds with nonzero core and neutral gradients and nonzero clock field? Use $c=\hbar=m=M_0=1$, signature $(+---)$, and the flat internal connection in a local trivialization. This is an off-shell local calculation: a smooth local jet need not solve the nonlinear equations or Einstein constraints. The metric and four-dimensional differentiable domain are assumptions of this candidate.

Write $\Phi=((q_1+iq_2),(q_3+iq_4))/\sqrt2$, $s=\sum_Iq_I^2/2$, $Z=1+0.1s$, $U=s-0.5s^2+0.25s^3$, and $V_\chi=1-0.5s+0.25s^2$; set $\zeta=0.1$. These choices satisfy $0<\beta^2<4\gamma m^2$ and $m_\chi^2>\nu^2/(4\eta)$. The density being differentiated is

$$
\mathcal L_m=\frac12\sum_I g^{\mu\nu}\partial_\mu q_I\partial_\nu q_I+\frac12 Zg^{\mu\nu}\partial_\mu a\partial_\nu a+\frac12 g^{\mu\nu}\partial_\mu\chi\partial_\nu\chi-U-\frac12V_\chi\chi^2-\frac\zeta4\chi^4.
$$

Sample 200 seeded invertible operator coframes $e^a{}_{\mu}$ with lapse $N\in[0.8,1.2]$, shifts $b^i\in[-0.2,0.2]$, and spatial coframe $L=I+[-0.15,0.15]$ entrywise; reject condition number above 3. Save each six-field jet, its gradients and symmetric second derivatives. Independently polarize the action in all 24 derivative slots to get the Hessian. Compare with $H_{AB}g^{\mu\nu}$, $H=\mathrm{diag}(1,1,1,1,Z,1)$. Compute action field derivatives using complex step and compare Euler–Lagrange local-jet equations with §8.1, including $Z_s\nabla s\cdot\nabla a$, $Z_s(\partial a)^2$, and $V_{\chi,s}\chi^2$. For each coframe, evaluate both characteristic roots for all six fields in 20 declared sphere directions. Save all roots and independently check the null polynomial. The operator-metric determinant polarization is separately checked.

Artificially set $Z=-0.5$ to detect loss of positive kinetic health. A _separate model_, `signal-space.ss-ocf-1.orientation-quartic-control.v1`, adds $-\kappa_H\mathcal H_{\mu\nu}\mathcal H^{\mu\nu}/4$ for a unit orientation $\mathbf n$, $\mathcal H_{\mu\nu}=\mathbf n\cdot(\partial_\mu\mathbf n\times\partial_\nu\mathbf n)$. On the flat background $\partial_x\mathbf n=(0.6,0,0)$, use $\kappa_H=0.4$ and polarize this separate action in a transverse orientation perturbation. It predicts $v^2=K/(K+\kappa_Hp^2)$ with $K=1$. This control is excluded from SS OCF 1; a nonmetric cone here establishes the audit can detect a split.

For gravity, name the harmonic (de Donder) hyperbolic gauge. On 20 flat transverse-traceless Fourier jets, check the linearized Einstein principal symbol $-\xi^2\bar h_{\mu\nu}/2$, harmonic constraints $\xi^\mu\bar h_{\mu\nu}=0$, and linearized flat Hamiltonian/momentum constraints. This does **not** solve the nonlinear Einstein constraints or test their propagation. These are explicitly recorded as untested prerequisites for future curved evolution.

## Locked decision and uncertainty

The action Hessian, equations, operator metric, characteristic roots, and flat gravity-symbol residuals must be below $10^{-10}$ after the declared normalization. Valid field-space kinetic eigenvalues must be positive; negative $Z$ must fail. The separate orientation speed must differ from metric speed by more than $10^{-3}$ with reference error below $10^{-10}$. Missing/nonfinite evidence is unresolved. The 200 samples are a seeded implementation screen, not a proof for every smooth background. No spatial grid, time stepping, boundary, evolving conservation, or invariant detector record is tested, so no numerical convergence or boundary claim applies.

The reader export has a root comparison in shifted frames, action/equation residual versus coframe conditioning, and both failure controls. Each uses exact saved plot data and four-part figure interpretation. The next experiment is the Test 6 Q-ball profile, independent bound-clock spectrum, lifetime, and trapping-off controls. Test 5 success alone does not provide a clock or derive the coframe from the microscopic projector theory.

Run after merge with `python3 .agents/scripts/run_experiment.py --experiment gross-test-05 --output ../gross-test-05-output`, or select `gross-test-05` in the manual Actions workflow. The workflow uploads evidence and reader artifacts without committing them.
