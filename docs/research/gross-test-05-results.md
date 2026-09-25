# Test 5: reviewed analysis and next calculation

**Run:** `run-d3333c7602af3e47`; **analysis:** `analysis-0001-4dbb966f`; **report:** `report-0001`. Technical pipeline completed. All seven locked checks **pass for their bounded scope**. The local pipeline took about six seconds; source provenance and hashes are in the canonical package. This review uses the saved raw jets, derived rows, checks, rendered figures, and both PDFs.

## Physical question

In the SS OCF 1 continuum candidate, an invertible Hermitian coframe $E_\mu=e^a{}_{\mu}\sigma_a$ defines $g_{\mu\nu}=e^a{}_{\mu}\eta_{ab}e^b{}_{\nu}$. Here $\eta=\mathrm{diag}(1,-1,-1,-1)$. The six real matter fields are four real components of a complex core doublet $\Phi$, a neutral field $a$, and a clock candidate $\chi$. The proposed action gives $Z(s)=1+0.1s$, where $s=\Phi^\dagger\Phi=\sum_Iq_I^2/2$. Its two-derivative matter Hessian should be

$$
\frac{\partial^2\mathcal L_m}{\partial(\partial_\mu\varphi_A)\partial(\partial_\nu\varphi_B)}=H_{AB}g^{\mu\nu},\qquad H=\mathrm{diag}(1,1,1,1,Z,1).
$$

For a local covector $\xi_\mu$, a characteristic satisfies $g^{\mu\nu}\xi_\mu\xi_\nu=0$. Universal coupling to the chosen metric makes this prediction analytically expected. The useful failure condition is an independent derivative or equation implementation that produces a split or an unhealthy sign.

## Evidence and classification

| Check                                                            |                                                             Observed | Locked decision                          |
| ---------------------------------------------------------------- | -------------------------------------------------------------------: | ---------------------------------------- |
| Saved coverage                                                   | 200 local coframes, 20 directions, 6 sectors, 2 roots = 48,000 roots | Pass                                     |
| Action Hessian and operator metric                               |                  maximum normalized discrepancy $8.88\times10^{-16}$ | Pass, below $10^{-10}$                   |
| Full local matter equations                                      |                  maximum normalized discrepancy $4.88\times10^{-16}$ | Pass, below $10^{-10}$                   |
| Characteristic roots and null polynomial                         |                                         maximum $1.77\times10^{-15}$ | Pass, below $10^{-10}$                   |
| Valid kinetic matrix; artificial negative $Z$                    |                smallest valid field eigenvalue $1$; control $Z=-0.5$ | Pass; control correctly fails positivity |
| Separate quartic orientation action                              |           $K_t=1.144$, $K_x=1$, $v=0.934947$ versus metric speed $1$ | Pass; split $0.065053>10^{-3}$           |
| Flat linearized harmonic-gauge gravity symbol and TT constraints |                                maximum residual $3.43\times10^{-16}$ | Pass for the registered linearized check |

The derivative Hessian was obtained by polarizing the action in all 24 first-derivative slots, including off-diagonal coframe components. An independent complex-step derivative of the full matter Lagrangian checks the field forces and the written local Euler–Lagrange expressions. The neutral background gradient and the clock field are nonzero; consequently the $Z_s(\partial a)^2$ and $V_{\chi,s}\chi^2$ reciprocal terms are exercised. The roots were checked against the independently inverted coframe null polynomial. These are deterministic floating-point residuals, not measured statistical confidence intervals.

**Figure reading.** The characteristic overlay shows four illustrative coframes: coordinate frequencies vary with shift, while core and neutral roots coincide; all saved sectors enter the numerical check. The action-audit plot shows every sample below the preregistered residual line across the sampled conditioning range. The control figure shows two distinct alarms: a negative neutral kinetic coefficient and a slower orientation perturbation in the _separate_ quartic model. Exact plotted rows and their transformations are included in the reader export. Each figure carries its Question, Reading, Significance and Limitation in the index and results PDF.

## Interpretation and limits

This result validates the **implemented, chosen** common principal structure of SS OCF 1 on the sampled off-shell smooth local jets. It does not derive a coframe or four-dimensional domain from ordered receptions, and does not show that Candidate A's complete reciprocal memory spectrum becomes Candidate B. Test 4's stationary physical memories are a result of a different action/circuit; the present calculation neither repairs nor contradicts that observation. The orientation control illustrates how a material derivative law can add a cone while the geometric signal sector remains meaningful. A common coordinate shift cannot generally erase this relative speed difference.

The gravity check is restricted to flat linearized transverse-traceless perturbations in harmonic gauge. Its gauge, Hamiltonian, and momentum constraints are identities on that declared family. **Nonlinear Einstein initial constraints, curved-background gauge propagation, and coupled Einstein–matter evolution were not evaluated.** The 200 local jets are not on-shell backgrounds. There is no spatial grid or evolved boundary here, so grid convergence, flux accounting, long-time conservation, nonlinear stability, and boundary sensitivity are outside this run. No autonomous bound clock or invariant local detector record was measured.

Two preliminary pipeline exports failed without altering equations or thresholds: the first detected an immutable event-log checksum mismatch at report stage; the second reached a verified source report but found a reader interpretation question different from the locked plan. Their statuses, source commits, logs and saved raw attempts are kept in `provenance/pipeline-attempts/`. The final run uses atomic canonical PDF publication and aligned figure questions. Its canonical and reader packages have been verified again after generation.

## Next discriminating calculation

Run **Test 6** in the flat gravity-decoupling limit using the exact potential family recorded in this plan. First solve the radial Q-ball branches at $\omega_Q/m=0.868,0.875,0.90,0.94$ and the independent $\chi$ eigenvalue problem. A usable clock requires a stable core, a bound eigenvalue separated from zero and the continuum threshold by more than five numerical errors, and under $1\%$ clock-mode energy loss and core charge drift over 100 calibrated periods after boundary flux is accounted for. Halve radial spacing from $0.1/m$ to $0.05/m$ and enlarge the radius from $80/m$ to $160/m$ when the tail warrants it. Turn off trapping ($\nu=0$) and run an unexcited $\chi=0$ core as controls. A missing bound eigenvalue or short lifetime defeats the proposed clock in that regime even though Test 5's local action audit passes. Reception and operational geometry tests depend on that independently readable clock.
