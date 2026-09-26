# Test 7 discriminator: discrete surface transfer

This protocol follows issue #75 and the fourth-order follow-up. The original Test 7 failure remains fixed; this run cannot automatically promote Test 7 or start Test 8. The action is Operator Program v0.2 §§7–10, with the question in §15.7.

## Exact discrete transfer

Keep the registered radial variables $b=ra$, $u=r\Phi$, $w=r\chi$. On the independently calibrated, frozen background define

$$
M=\mathrm{diag}(1+\varepsilon|u/r|^2),\qquad K=G^T\mathrm{diag}(Z_f)G.
$$

The positive discrete Hamiltonian gives $\dot b=M^{-1}p$ and $\dot p=-Kb$. Both inertia and spatial stiffness contain $Z$. In the continuum their principal factors cancel: a local speed $\sqrt Z$ is not the characteristic speed of this action. The earlier optical inverse is therefore an approximation to replace, not a transport law to preserve. This run uses the actual matrices, including their radial factors and dispersion.

Write $x=(b,p)$ and $F=[0,M^{-1};-K,0]$. With the registered RK4 polynomial $R$, the sampled surface map is

$$
y_k=C R(\Delta t F)^k Bq,\qquad Bq=(q,M D_hq).
$$

Here $q$ is unknown initial neutral data supported in the declared exterior interval $[18,26]$, $D_h$ is the centered derivative with zero extension, and $C$ reads $b$ and $\dot b$ at $r=14$. The preparation $\dot b=D_hb$ is declared before acquisition; the predictor gets no pulse width, carrier, shape, or receiver history. The rows are computed efficiently by evolving the two adjoint surface impulses:

$$
\ell_{k+1}=R(\Delta t F^T)\ell_k,\qquad H_k=B^T\ell_k.
$$

Because RK4 is a polynomial, this is the exact adjoint of the same discrete acquisition. A fixed relative singular-value cutoff $10^{-10}$ defines $q=H^+y$. A $10^{-8}$ control measures sensitivity. This inverse estimates initial data from a surface record; it does not fit any clock-response coefficient. Rank, all singular values, replay residual and later source audit are saved. The support and incoming rule are genuine prior information and limit the claim.

## Response and independent profile refinement

Evolve the unchanged formal expansion $a=Aa_1+A^3a_3+\cdots$, $\Phi=\Phi_0+A^2\Phi_2+A^4\Phi_4+\cdots$, and the analogous clock expansion, using the sources derived in [the fourth-order protocol](gross-test-07-order4.md). For $z=\chi-i\dot\chi/\Omega_\chi$, the phase is

$$
\Delta\theta=A^2\mathrm{Im}(z_2/z_0)+A^4\mathrm{Im}\left[z_4/z_0-\tfrac12(z_2/z_0)^2\right]+O(A^6).
$$

At each primary mesh, independently solve the same $\omega_Q=0.900$ core BVP, project by discrete Newton, and solve its clock eigenproblem. Freeze those profiles before any surface acquisition. The readout calibration $\Omega_\chi=0.41274991$, clock amplitude $0.001$, local radius $0.1$ and phase zero are fixed. A separately labeled interpolated old-profile control identifies preparation bias; it is not an alternative acceptance target. No new clock longevity claim follows from this refinement.

## Locked cases and sequence

Two compact envelopes are centered at 22: width 3.25 with zero carrier, and width 2.5 multiplied by $\cos[1.4(r-22)]$. These are new spectral tests under the discrete incoming preparation. Amplitudes are $0.008,+0.012,-0.012$, with $0.012$ nominal. Each full receiver includes a matched quiet case.

Primary meshes are $h=0.1,0.05,0.025,0.0125$, with steps $0.005,0.005,0.005,0.0025$. A finest-grid half-step control, $R=100$ box at $h=0.025$, alternate inverse cutoff, and old-profile diagnostic are separate variants. All ordinary boxes have $R=80$; duration is 60, before any outer reflection can return. Surface acquisition ends at 16 and samples every 0.025. Receiver output every 0.025 is compared with decimated 0.05.

All reconstructed inputs, profiles, complete Taylor histories, and numerical first-rise/last-fall marker and interval forecasts are hashed before **any** full nonlinear receiver starts. Markers are the first rising and last falling $|a|=10^{-4}$ crossings in the declared duration, located by cubic Hermite using local $a_t$. The same predicted order-three neutral markers are used for both order-two and order-four phase forecasts, isolating their response difference. Each observed interval uses its own measured markers. Phase interpolation uses cubic splines; decimation uncertainty includes phase and marker sampling together.

## Predeclared error budget and decision

Let $Y$ be the measured interval in cycles and $P_2,P_4$ its forecasts. For each nominal spectrum define the conservative, unextrapolated budget

$$
B=|Y_{h/2}-Y_h|+|Y_{dt/2}-Y_{dt}|+|Y_{R100}-Y_{R80}|+|P_{4,c8}-P_{4,c10}|+E_{\mathrm{sample}}+2\times10^{-11}.
$$

The first pair is finest/finer; the time pair is finest/time; the domain pair is wide/finer. Sampling error is the larger finest actual or fourth-order interval change under decimation. The old interpolated profile comparison is diagnostic; discretization uncertainty of the independently solved profile is included in the mesh sequence. No Richardson division reduces this budget.

- Convergence requires the finest interval change to be at most 0.6 times the preceding change plus the nonspatial terms. Otherwise order discrimination is unresolved.
- Resolving the order requires $B\le|P_4-P_2|/4$ and $|Y|>5B$. The 5% original Test 7 tolerance cannot be used to resolve this correction.
- With those controls resolved, require $|Y-P_4|\le B$ and $|Y-P_2|>3B$. A resolved violation fails this approximation; insufficient resolution remains unresolved.
- All marker forecasts retain the original absolute 0.1 time gate. Nominal finest residuals must also lie within the analogous direct mesh/time/domain/inverse/sampling timing budget plus $10^{-6}$, and decrease from the fine-grid residual or already lie below that budget.
- Independently solved profiles require residual below $2\times10^{-10}$ and convergent eigenvalues. Surface replay residual must be below $10^{-7}$. Charge drift must be below $10^{-5}$ and energy residual below 1% of incident energy.

The exact machine criteria and figure plan are locked in `plans/gross-test-07-transfer.json`. Both spectra must satisfy the order discrimination; a good result on only one is reported as such. Missing marker or convergence evidence prevents promotion. The useful outcome is either a resolved extension on this preparation, a localized numerical limit, or a controlled rejection. Two-object survival/recoil, observer and coordinate invariance, gravity, angular stability and emergent spacetime remain outside this calculation.


## Separately labeled post-lock audit and execution recovery

After all sixteen forecasts in the local attempt were locked and the first receiver comparisons were inspected, a downstream diagnostic was added. It preserves the nine registered checks and their original budget. It separately reports an audit budget using the larger receiver or forecast change for each mesh, time, and domain term. This diagnostic cannot promote or rewrite the registered result; it can expose a limit in what those checks establish.

The audit compares frozen linear propagation from recovered input with propagation from the known source on the finest grid, and the carrier time control. The known shape is used only in this downstream diagnostic, never in the original inverse or forecast. See [the interruption record](gross-test-07-transfer-interruption.md) for the inaccessible partial local attempt and the separate hosted recovery. Repeating a previously inspected history is reproducibility evidence, not a new held-out claim.
