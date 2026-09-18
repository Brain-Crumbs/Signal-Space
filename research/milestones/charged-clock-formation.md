# Signal Space formation milestone: conservative formation and causal phase readout

Date: 17 September 2026.

## Result and scope

**The prescribed model has a numerically demonstrated basin of classical charged-clock formation from nonstationary charged Gaussian data.** At the benchmark target charge, all six preparations with $w/R_Q\in\{1,2\}$ and $\nu/m\in\{0.8,0.9,1.0\}$ develop a compact core close to the exact rotating Q-ball branch. Excess energy and charge propagate outward under the original field equations. No friction, absorber, stochastic bath, externally fixed center, or profile replacement is used in the formation evolutions.

For the extended $w/R_Q=2,\nu/m=0.9$ example, the final 800 time units contain **115 clock cycles**, with fitted frequency $0.90340938m$, mean retained core charge $232.01015$, mean profile-fit error **0.473%**, and phase residual **0.004842 radians RMS**. The core charge predicts $\omega=0.90340670m$ independently through the analytic branch. The frequency difference is approximately three parts per million. The phase residual corresponds to a timing residual of about $0.00536/m$, or 0.077% of one cycle; this is deterministic classical modulation, not a quantum linewidth.

Two prepared copies of a numerically formed core also give different local collision records for relative phases $0,\pi/2,\pi$. Refinement preserves the effect. This establishes a causal, interacting classical phase readout within the specified field theory.

**The qualification matters:** the best-settled Gaussian examples start below the free-wave threshold $E=mQ$. Preparations above that threshold retain localized charge but do not all relax to an equally quiet clock, even by $mt=2400$. In particular, a high-frequency preparation retains a substantial oscillating excitation. The calculation therefore supports classical formation and readout in a finite tested parameter region; it does not establish universal cooling from arbitrarily unbound data, formation from neutral radiation, quantum coherence, or emergent spacetime.

A finite parameter scan is evidence for a formation basin, not a mathematical existence theorem for an open basin or a proof of asymptotic convergence. All results below are synthetic calculations of the supplied candidate, not observations of nature.

## 1. The model is unchanged

Use the action supplied in _Signal Space_Ordered_Reception_Charged_Clock_Model.md_:

$$
\mathcal L=\lambda^{-1}\left[|\partial\Phi|^2-U(s)+\frac12 Z(s)(\partial a)^2\right],
\quad s=|\Phi|^2,
$$

$$
U(s)=s-s^2+s^3,\qquad Z(s)=1+0.1s,\qquad\lambda=0.01.
$$

Here $m=g=h=1$ in mass units and the reference metric is $\operatorname{diag}(+1,-1)$. The equations are

$$
\Phi_{tt}-\Phi_{xx}+(1-2s+3s^2)\Phi
-\frac{\epsilon}{2}\Phi(a_t^2-a_x^2)=0,
$$

$$
\partial_t(Za_t)-\partial_x(Za_x)=0.
$$

The charge is global $U(1)$ charge; it has not been identified with electric charge. The neutral field is a massless scalar, not a photon. The common characteristic cone and the potential are inputs, as in the previous report.

The classical control $a=a_t=0$ stays exactly zero. There is no spontaneous classical neutral emission from this control. Its relaxation can export energy through charged $\Phi$ waves, including oppositely charged components where excited by the preparation. An outgoing charge flux measures net charge, not a count of quanta.

The exact reference branch is

$$
f_\omega^2(x)=\frac{2(1-\omega^2)}{1+\sqrt{4\omega^2-3}\cosh(2\sqrt{1-\omega^2}\,x)},
\qquad \Phi=e^{-i\omega t}f_\omega(x).
$$

With $r=\operatorname{artanh}(2\sqrt{1-\omega^2})$,

$$
Q(\omega)=\frac{2\omega r}{\lambda},\qquad
E(\omega)=\frac{(\omega^2+3/4)r+\tfrac14\tanh r}{\lambda}.
$$

The previous stability milestone supplies the fixed-charge linear-stability and breakup results. The present calculation tests whether nonstationary data actually approach this family; it does not infer formation merely from the existence of its exact solution.

## 2. Preparations and the meaning of “unbound”

The primary preparation is exactly the requested Gaussian:

$$
\Phi(0,x)=A e^{-x^2/(2w^2)},\qquad
\dot\Phi(0,x)=-i\nu\Phi(0,x),\qquad
A^2=\frac{\lambda Q_0}{2\nu w\sqrt\pi}.
$$

The coherent phase and nonzero charge are supplied initial data. The spatial density must reorganize dynamically; no stationary profile is inserted. The Gaussian's initial RMS radius is $w/\sqrt2$, so $w/R_Q$ should not be confused with its RMS-radius ratio.

At target $\omega_0=0.90$, $Q_0=241.28062465$ and $R_Q=2.262044$ approximately. The complete requested grid is $w/R_Q=0.5,1,2,4$ crossed with $\nu/m=0.8,0.9,1.0$. The same 12-case grid is also evolved at target frequencies $0.88,0.95,0.98$: **48 distinct primary Gaussian preparations**. All run to $mt=800$; none is discarded based on its outcome.

There is an important correction to the earlier label “unbound-data formation.” A nonstationary Gaussian is not necessarily energetically unbound. Let

$$
I=\int|\Phi(0,x)|^2dx=\frac{\lambda Q_0}{2\nu}.
$$

Direct integration gives

$$
E_G=\lambda^{-1}\left[(1+\nu^2)I+\frac{I}{2w^2}
-\frac{I^2}{w\sqrt{2\pi}}+\frac{I^3}{\pi\sqrt3\,w^2}\right].
$$

For $E_G<mQ_0$, complete dispersal into asymptotic free charged waves is already energetically forbidden. Such data can still be far from a stationary object, and their formation is a genuine dynamical question, but it is not capture of an initially above-threshold ensemble. The narrow benchmark Gaussians have $E_G>mQ_0$; the moderate and broad benchmark Gaussians have $E_G<mQ_0$.

Four additional above-threshold preparations use $w/R_Q=1,2$ with $\nu/m=0.6,1.3$. They are reported as supplementary tests, not substituted for unsuccessful members of the original grid. Initial total momentum is zero for the symmetric formation runs. Formation with net incident momentum is not established by these symmetric preparations; recoil is tested separately below.

## 3. Evolution, boundaries, diagnostics, and conservation

The code implements the specified nearest-neighbor Hamiltonian and the symmetric splitting

$$
A(\Delta t/2)\,B(\Delta t/2)\,C(\Delta t)\,B(\Delta t/2)\,A(\Delta t/2).
$$

It stores $\Phi$, its velocity, $a$, and $b=Za_t$. The $B$ flow includes the corresponding structural-momentum kick; the $C$ flow includes derivatives of the edge coefficients $Z_{j+1/2}$. Thus neutral packets back-react on the structural field. For $a=0$ the method reduces to drift–kick–drift evolution of the complex nonlinear Klein–Gordon field. Each split flow preserves the global discrete $U(1)$ charge.

The primary mesh is $m\Delta x=0.05$, $m\Delta t=0.01$. All 12 benchmark preparations are repeated at $0.025,0.005$. Four representative preparations also use $0.05,0.005$ to separate time-step effects from spatial effects. Two extended cases use both meshes. No fitting parameter is retuned between resolutions.

For duration $T$, the domain half-length is $L=T+\max(90,10w)$, rounded upward to a mesh point. Endpoints are zero; there are no absorbing layers. This puts the boundaries outside the physical measurement cone, with a large initial-tail margin. The scheme's numerical dependence cone is not literally the continuum cone: the nearest-neighbor regulator has dispersive precursors, while its resolved propagation converges under refinement. No use is made of returning boundary radiation. This is a boundary-exclusion design, not a separate domain-enlargement convergence study.

Histories are sampled every $0.2/m$ and complex-field snapshots every $10/m$. Phase fits use the dense histories, not sparsely sampled snapshot phases. Energy and charge fluxes are integrated every step in the final benchmark/refinement runs. Some original exploratory runs at other target charges retain the $0.2/m$ flux quadrature; their larger quadrature residuals are marked by the absence of cumulative-flux columns in the CSV. Their total conservation diagnostics remain valid.

### Local accounting

In the continuum,

$$
\rho_Q=-\frac2\lambda\operatorname{Im}(\Phi^*\dot\Phi),\qquad
j_Q=\frac2\lambda\operatorname{Im}(\Phi^*\Phi_x),\qquad
\partial_t\rho_Q+\partial_xj_Q=0.
$$

The energy flux is

$$
S_E=-\lambda^{-1}\left[2\operatorname{Re}(\dot\Phi^*\Phi_x)+Za_ta_x\right].
$$

For a fixed window $[-W,W]$,

$$
E_W(t)+\int_0^t[S_E(W,t')-S_E(-W,t')]dt'=E_W(0),
$$

and analogously for charge. The code uses the corresponding lattice currents, with half of each bond energy assigned to each endpoint. In the $a=0$ control these are

$$
J^E_{j+1/2}=-\frac{\operatorname{Re}[(\dot\Phi_j^*+\dot\Phi_{j+1}^*)(\Phi_{j+1}-\Phi_j)]}{\lambda\Delta x},
\quad
J^Q_{j+1/2}=\frac{2\operatorname{Im}(\Phi_j^*\Phi_{j+1})}{\lambda\Delta x}.
$$

The source also implements the variable-$Z$ neutral contribution, including the bond-energy redistribution term. Time quadrature and the split integrator leave convergent finite-step residuals; the ledger is checked rather than enforced by rescaling.

### Core and phase diagnostics

For symmetric formation the center remains zero. Report charge and energy in $|x|\le20,30,40$, and use the smallest window for the principal core estimate. Fit

$$
\theta(t)=\operatorname{unwrap}\arg\int_{-20}^{20} f_{\omega_0}(x)\Phi(t,x)\,dx
=\theta_c-\omega_{\rm fit}t+\delta\theta(t).
$$

The projection reference is fixed in advance. Independently infer $\omega_Q$ by inverting the exact charge curve using the mean retained charge. Also minimize the relative complex-field $L^2$ residual against $e^{i\theta}f_\omega(x-X)$ over $|x-X|\lesssim12$. There is no free amplitude normalization. Translations are fitted for the moving perturbed control and neutral-packet experiments. Fits to a single profile are not used to classify the two-object collision as one clock.

For $T=800$, the fitting interval is $400\le mt\le800$. Extended runs use their last 800 time units. Reported fit radii are RMS radii of the best-fit profile **truncated to the fit interval**, not infinite-line radii; raw density moments in larger windows remain sensitive to outgoing radiation. Phase is insensitive to the window at late times to the displayed precision, while retained charge has a small window dependence.

## 4. The complete benchmark scan

The following results use the refined mesh and averages over $400\le mt\le800$. Profile error is the mean relative complex-field fit residual on the declared fit window. “Near branch” is a descriptive post-analysis label: these six cases have mean profile error below 2%, phase RMS below 0.05 rad, frequency within 0.5% of the charge prediction, and less than 0.5% change of core charge over the last 200 time units. These thresholds summarize the data; they are not a preregistered success definition or an asymptotic theorem.

| $w/R_Q$ | $\nu/m$ | $E_0/m-Q_0$ | Mean core $Q$ | $\omega_{fit}/m$ | Profile error | Phase RMS / rad | Outcome at $mt=800$ |
| ------: | ------: | ----------: | ------------: | ---------------: | ------------: | --------------: | ------------------- |
|     0.5 |     0.8 |      34.025 |        64.042 |         0.986043 |        11.28% |          0.1511 | Unsettled at 800    |
|     0.5 |     0.9 |      24.954 |        76.566 |         0.983893 |        11.12% |          0.1656 | Unsettled at 800    |
|     0.5 |       1 |      21.040 |        84.818 |         0.981817 |        10.93% |          0.1120 | Unsettled at 800    |
|       1 |     0.8 |      -7.022 |       228.941 |         0.904154 |         1.66% |          0.0451 | Near branch         |
|       1 |     0.9 |      -8.600 |       229.175 |         0.904571 |         1.44% |          0.0034 | Near branch         |
|       1 |       1 |      -7.574 |       229.195 |         0.904169 |         1.62% |          0.0397 | Near branch         |
|       2 |     0.8 |      -7.258 |       232.098 |         0.902889 |         1.44% |          0.0475 | Near branch         |
|       2 |     0.9 |      -9.067 |       232.104 |         0.903412 |         1.14% |          0.0053 | Near branch         |
|       2 |       1 |      -8.310 |       232.060 |         0.903158 |         1.30% |          0.0340 | Near branch         |
|       4 |     0.8 |      -2.304 |       198.866 |         0.921415 |        11.73% |          0.0715 | Unsettled at 800    |
|       4 |     0.9 |      -5.223 |       200.506 |         0.922654 |        12.84% |          0.0535 | Unsettled at 800    |
|       4 |       1 |      -5.286 |       200.253 |         0.922632 |        12.70% |          0.0545 | Unsettled at 800    |

The narrow preparations eject a large fraction of their initial charge, and their central profiles are still oscillating or contaminated by slow radiation at $mt=800$. The broad preparations are still redistributing charge and relaxing. The six unsettled cases have **not** been proved to disperse or to lack a stable remnant.

The other target charges show a consistent qualitative pattern: moderate widths fit the branch better than the extreme widths during this window. At target $\omega_0=0.88$, the moderate-width profile errors are approximately 0.73–0.94%; at 0.95 they are 2.29–4.12%; at 0.98 they are 2.44–4.44%. These other-charge scans are exploratory at $\Delta x=0.05$ and have not all received independent refinement. They must not inherit the benchmark's quantitative convergence claim.

The complete 48-case table is included in Appendix A and `formation_scan.csv`.

## 5. A well-settled formation example

Take $\omega_0=0.90$, $w/R_Q=2$, $\nu/m=0.9$ and evolve to $mt=1600$. On the fine mesh:

| Quantity                                     |    Executed value |
| -------------------------------------------- | ----------------: |
| Initial charge                               |    241.2806246494 |
| Initial total energy / $m$                   |    232.2137493748 |
| Mean core charge, $                          |                 x | \le20$, $800\le mt\le1600$ | 232.01015145 |
| Mean core energy / $m$, same window          |      222.56300299 |
| Branch frequency from that mean charge / $m$ |      0.9034067023 |
| Fitted phase frequency / $m$                 |      0.9034093810 |
| Phase residual RMS / rad                     |        0.00484170 |
| Maximum absolute phase residual / rad        |        0.00890549 |
| Mean / maximum profile residual              | 0.4733% / 0.8066% |
| Charge change in the last $200/m$            |       −0.00365564 |
| Final charge outside $                       |                 x | \le30$                     | 9.27093672   |
| Final energy outside $                       |                 x | \le30$, in mass units      | 9.65125857   |

The late core retains approximately **96.16%** of the initial charge. Its mean energy is only about $0.01765m$ above the exact branch at its mean retained charge. This small positive remainder and the nonzero phase residual are explicitly retained; the core is not declared an exact relative equilibrium.

The final energy ledger at $mt=1600$ is

$$
232.2137591411=222.5625005738+9.6512585674,
$$

where the terms are total, $|x|\le30$ core, and exterior energy. The independently integrated outward energy flux is $9.6512261676m$. The full-history core-plus-flux mismatch is at most $1.07\times10^{-7}$ of initial total energy. The integrated outward charge is $9.2708746300$; the corresponding charge-ledger mismatch is at most $2.57\times10^{-7}$ of initial charge.

Late mean charges in windows 20, 30, and 40 are 232.01015, 232.04120, and 232.09034. Their phase fits all give $0.90340938m$. This shows both the small residual charge in slow tails and the robustness of the phase estimate.

The fine/coarse differences in the extended example are approximately $6.7\times10^{-7}$ in relative frequency, $6.2\times10^{-6}$ in mean core energy, and $1.3\times10^{-5}$ in fitted radius. Across **all 12** benchmark cases, the maximum corresponding differences are about 0.0032%, 0.084%, and 0.083%, respectively: below the specified 0.5% numerical agreement target, including for physical outcomes that remain unsettled.

Numerical convergence of an unsettled run is evidence that its unsettled behavior is resolved; it does not turn that behavior into successful equilibration.

![Formation, charge retention, profile comparison, and phase residual](Signal Space_Formation_Diagnostics.png)

## 6. Extended and above-threshold tests

The broad benchmark case $w/R_Q=4,\nu/m=0.9$ is extended to $mt=2400$ on the primary mesh. Over its last 800 units, it has mean core charge 189.198, fitted frequency $0.92245210m$, charge-predicted frequency $0.92247962m$, mean profile residual 1.51%, and phase RMS 0.01715 rad. Thus a run that was unsettled at 800 can approach the branch later. This extended broad run has not itself been repeated on the fine mesh; its $T=800$ preparation was refined.

The above-threshold narrow case $w/R_Q=0.5,\nu/m=1.0$ is also extended to 2400. It retains a core with mean charge about 80.98, fitted frequency $0.98104m$, profile residual 5.61%, and phase RMS 0.0711 rad over the last 800 units. It has shed roughly two thirds of the original charge. This is evidence of a long-lived localized rotating remnant, with appreciable modulation, not a comparably quiet copy of the main clock.

The four supplemental preparations at $\nu/m=0.6,1.3$ all have $E_0>mQ_0$. At $T=800$ their mean profile residuals are approximately 2.7–3.3% and phase RMS values 0.13–0.15 rad. They retain substantial localized charge but do not meet the near-branch summary criteria above.

The $w/R_Q=2,\nu/m=1.3$ case is extended to 2400 **on both meshes**. Fine-mesh results over $1600\le mt\le2400$ are:

| Quantity                                      |           Value |
| --------------------------------------------- | --------------: |
| Initial energy / $m$                          |    245.02313783 |
| Initial energy above $mQ_0$ / $m$             |      3.74251318 |
| Mean core charge                              |    231.84582855 |
| Mean core energy / $m$                        |    234.69180499 |
| Exact branch energy at mean core charge / $m$ |    222.39689824 |
| Remaining mean excitation energy / $m$        |     12.29490675 |
| Fitted phase frequency / $m$                  |      0.89991241 |
| Charge-predicted branch frequency / $m$       |      0.90346944 |
| Mean / maximum profile residual               | 2.560% / 6.117% |
| Phase residual RMS / rad                      |        0.129921 |

Its charge is nearly stationary in the core, but its excitation energy remains substantial. A Fourier diagnostic of the phase residual has its dominant nonzero angular-frequency bin near $1.7274m$ on both meshes; the bin spacing is about $0.00785m$. That is an observed nonlinear modulation, not a newly proved localized normal mode. The previous stability report excluded resolved nonzero modes _below_ the lowest continuum edge around the stationary benchmark; it did not exclude nonlinear breathing or resonances within the continuum.

The target-$0.98$, $w/R_Q=1,\nu/m=0.8$ case is also extended on the primary mesh. It likewise retains charge with residual modulation (mean profile error about 3.81%, phase RMS about 0.0745 rad). No claim is made that simply running longer must eliminate these oscillations.

**This is the unresolved part of a stronger formation claim:** the supplied dynamics has not yet demonstrated reliable relaxation of all tested above-threshold preparations to the lowest-energy charged branch. More simulation time alone is not a derived cooling mechanism.

## 7. Controls, neutral reception, and recoil

### Exact and perturbed object controls

The continuum exact profile evolved on the primary mesh has fitted frequency $0.90000027m$, phase RMS $2.83\times10^{-6}$ rad, and mean profile residual $2.90\times10^{-5}$. The small discrepancy is expected because an exact continuum profile is not exactly stationary on a finite spatial mesh. Its maximum relative total-energy drift is $1.37\times10^{-10}$.

For the perturbed control, the initial real field is multiplied by $1+0.02e^{-x^2/8}\cos(1.3x)$; add real velocity $0.01 f(x)\sin(0.7x)$ while retaining the original imaginary velocity. This declared perturbation changes the charge slightly and imparts momentum. The fitted center moves about 1.10 units by $T=800$, with late speed about 0.00136. Once that translation is fitted, the mean profile residual is 0.273%. Comparing only with a profile pinned at zero would incorrectly count ordinary translation as loss of the bound object.

### Prepared neutral packets

Use the actual $T=800$ field from the successful Gaussian evolution. For separate reception experiments, extract its central Cauchy data with a taper equal to one for $|x|\le12$, zero for $|x|\ge18$, and a raised cosine between. This is an explicit new preparation, with its own initial energy and charge ledger. It removes outgoing radiation; it does not renormalize the core or replace it with the exact solution.

The extracted core has $E_0\simeq222.57568m$ and $Q_0\simeq232.02315$ on the primary mesh. Its zero-packet control accounts for further relaxation caused by the extraction. This extraction is not claimed to be an autonomous physical manipulation with zero cost.

Packets use $\sigma=3/m$, $k=m$, center $x=-45/m$, and $a_t=-a_x$ for rightward incidence. Symmetric incidence adds the reflected leftward packet at $+45/m$. Amplitudes are calibrated to total neutral energies $0.001,0.01,0.05$ times the original benchmark rest energy $230.90437m$; for two-sided incidence this is the combined packet energy. All six combinations plus the zero-packet control run for $240/m$.

The core remains localized and rotating in all of these tests. One-sided incidence gives a small positive recoil. For the 5% packet, final structural momentum inside $|x|<20$ is $2.27011\times10^{-5}m$ on the primary mesh and $2.26204\times10^{-5}m$ on the fine mesh, a 0.36% difference. The primary-mesh total-momentum drift is $1.60\times10^{-7}m$, substantially smaller than this recoil. Symmetric incidence keeps total and core momentum zero within arithmetic error.

For the 5% symmetric preparation, final minus initial neutral energy is approximately $-0.002585m$ on the primary mesh and $-0.002627m$ on the fine mesh: a small net transfer **from the prepared neutral waves into the structural field**, rather than automatic cooling. The small exchange itself differs by about 1.6% between meshes, so its precision is more limited than the total-energy ledger. One-sided 5% incidence instead gains roughly $1.48\times10^{-5}m$ of neutral energy. Preparation and timing matter.

Two additional runs seed 1% one-sided or symmetric neutral packets during Gaussian formation, starting at $x=\mp30/m$ and using the same $\sigma,k$. They retain the same qualitative formation behavior; they do not establish a universal bath-induced cooling law. Their detailed results remain in the archive. No seed is inserted into the $a=0$ formation controls.

## 8. Causal two-object phase readout after formation

The readout uses two copies of the _evolved_, tapered $T=800$ core, not exact analytic Q-balls. Place their centers at $x=\pm60/m$. For each copy, with $\xi$ its local coordinate, apply

$$
\Phi\mapsto e^{i k\xi+i\theta_s}\Phi_c(\xi),\qquad
\dot\Phi\mapsto e^{i k\xi+i\theta_s}[\dot\Phi_c(\xi)-\beta_s\partial_\xi\Phi_c(\xi)],
$$

with inward $\beta_s=\mp0.15$, $k=\omega_0\beta_s$, and relative phases $0,\pi/2,\pi$. This is a declared momentum/phase preparation. It is **not** described as an exact Lorentz boost of nonstationary Cauchy data. The field subsequently evolves freely under the same equations; centers are not driven along prescribed trajectories.

The compact preparations have disjoint support, so their initial total energy and charge are independent of relative phase: approximately $450.18592m$ and 464.04629 on the primary mesh. Relative phase cannot be detected by reading the density of either isolated copy. Their local signals must propagate into a common region.

Use the local observable $s(t,0)=|\Phi(t,0)|^2$ and the comparison statistic

$$
\mathcal J(\Delta\theta)=\int_{300/m}^{600/m}s(t,0)\,dt.
$$

This is a field-observable readout calculation. It does not include a separate finite detector apparatus, its noise, or its measurement cost.

| Prepared relative phase | $m\mathcal J$, primary mesh | $m\mathcal J$, fine mesh |
| ----------------------- | --------------------------: | -----------------------: |
| $0$                     |                    74.29123 |                 74.29565 |
| $\pi/2$                 |                    3.003919 |                 3.004157 |
| $\pi$                   |         $7.8\times10^{-27}$ |      $2.1\times10^{-27}$ |

The near-zero midpoint signal for $\pi$ follows from the antisymmetry of this precisely symmetric preparation; it is not a universal quantum visibility or a robustness claim for noisy clocks. The three outcomes do not define a sinusoidal detector fringe or a globally invertible phase estimator. They demonstrate that known phase choices produce distinguishable local records under full interacting evolution.

Before $mt=40$, the midpoint intensity is below $5\times10^{-33}$ on the primary mesh. The nearest initial support lies 42 units from the midpoint; the continuum signal front cannot reach it before $mt=42$. The tiny earlier numerical tail is a regulator precursor, not a claimed superluminal physical signal. The large phase-dependent collision record develops much later, around $mt\sim350$–450.

The outcomes also show back-action: the in-phase cores merge into an excited central object during the observed interval, whereas the other preparations separate after their encounter; the $\pi/2$ preparation produces strongly unequal outgoing energy partitions. On the primary mesh its final left/right energies are about $162.17m$ and $288.02m$. Momentum is still balanced: its maximum total-momentum drift decreases from $0.002649m$ to $0.000662m$ on refinement, approximately the expected factor of four. Total energy and charge meet the numerical conservation targets.

This passes a minimal interacting classical phase-readout test. It does not demonstrate a nondestructive clock comparator, a device that measures an arbitrary unknown phase without ambiguity, a calibrated moving-clock time-dilation experiment, or protected coherent capture.

![Phase-dependent collisions and the local readout](Signal Space_Formation_Readout.png)

## 9. Numerical acceptance and reproducibility

There are **99 executed evolutions**, including repeated controls, refinement runs, and extended tests; this number is not a count of independent physical preparations. Their machine-readable diagnostics are in `results/analysis.json`, with complete time histories and metadata in the archive.

Across all completed runs, maximum relative charge drift is $6.3\times10^{-14}$ and maximum relative total-energy drift is $3.18\times10^{-5}$. For the 12 fine benchmark cases, the corresponding maxima are about $2.50\times10^{-14}$ and $3.75\times10^{-6}$. The fine benchmark's largest energy-window-plus-flux mismatch is also below $3.75\times10^{-6}$ of initial energy. These satisfy the supplied numerical goals of charge drift below $10^{-8}$ and energy error below $10^{-4}$.

This validation combines an exact-profile control, a moving perturbed control, analytic Gaussian energy and charge, full-domain conservation, independently integrated local fluxes, fixed-$\Delta x$ time refinement, and joint space/time refinement. Momentum is a continuum diagnostic, not an exactly conserved lattice charge; the collision test explicitly checks its convergence.

The source requires a C++17 compiler plus Python with NumPy, SciPy, and Matplotlib. `run_all.py` compiles and executes the declared runs, then writes analysis and figures. It uses up to four local subprocesses; no external data or network service is needed. `README.md` specifies the steps and outputs. The analysis JSON preserves all fit statistics, including window sensitivity and late-time fit samples. The archive includes all time histories, model/stability source documents, and selected raw field snapshots needed to reproduce the displayed figures. Additional raw fields regenerate from the source.

The figure snapshots are every $10/m$ and are suitable for showing envelopes and motion. Do not infer rapid oscillation frequencies from them; use the $0.2/m$ histories for that purpose. No rounding of continuous classical charge into integer quantum sectors is performed.

## 10. What this establishes and the next missing calculation

| Question                                                                              | Status after this calculation                                                                                 |
| ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| Can a nonstationary charged profile organize into a persistent self-bound recurrence? | Yes, numerically, for a tested region of Gaussian preparations.                                               |
| Does the same local conservative evolution remove excess energy?                      | Yes, with charged outgoing flux in the $a=0$ control.                                                         |
| Is the surviving phase rate predicted by the charge-supported branch?                 | Yes to high accuracy for the well-settled example; appreciably excited remnants deviate and oscillate.        |
| Can a relative phase produce a causal local record?                                   | Yes, through full collisions of prepared formed cores, with back-action.                                      |
| Does neutral radiation automatically cool every preparation?                          | No. Vacuum classical $a=0$ stays zero; prepared packets can add or remove small amounts of structural energy. |
| Have all above-threshold preparations relaxed to the ground branch?                   | No. Long-lived excited remnants remain.                                                                       |
| Has quantum coherence, a common outgoing record, or emergent geometry been derived?   | No; none is computed here.                                                                                    |

The concrete gain for Signal Space is an autonomous _binding and classical phase recurrence_ mechanism within the supplied local field theory, together with an explicit way for formed objects to compare phase by causal contact. The object is not held together by prescribed cavity walls, and its defining recurrence is not an appended decaying shape oscillator.

The next unresolved dynamical question is now sharper: **is the persistent excited remnant a slowly decaying resonance, a nonlinear periodic/quasiperiodic object, or a configuration with a parametrically inefficient radiation channel?** Analyze its amplitude/phase sidebands and outgoing spectral flux, and calculate the corresponding nonlinear decay channel rather than adding friction or assuming a bath. The $\nu=1.3$ example supplies a concrete conserved-charge background and a resolved modulation frequency for that test. A nonlinear/Floquet analysis would be needed before calling it a new trapped mode.

For the already quiet formed branch, the separate next quantum gate remains the dressed charge-sector spectrum and the full radiation-plus-recoil record for a relational clock. Classical phase retention and collision contrast do not calculate that quantum channel. The present work makes those questions concrete without claiming that they are already solved.

## Sources and attribution

The calculation uses the attached _Signal Space_Ordered_Reception_Charged_Clock_Model.md_ and _Signal Space_Charged_Clock_Stability_Milestone.md_ as its model and benchmark specifications. The attached _Signal Space_Full_Theory_Research_Architecture-1.md_ and _Signal Space_Part_II.md_ supply the distinctions between reference geometry, autonomous binding, clock calibration, and quantum claims.

Relative-phase-dependent Q-ball interactions are established phenomena; see Bowcock, Foster, and Sutcliffe, [Q-balls, Integrability and Duality](https://arxiv.org/abs/0809.3895). That work provides context for the interaction test, not the numerical results of this report. Q-balls and phase-sensitive soliton collisions are not claimed as novel Signal Space predictions.

## Appendix A. All primary Gaussian preparations

The following table uses the original $\Delta x=0.05$, $\Delta t=0.01$, $T=800$ runs for consistent comparison across target charges. Benchmark refined results are given in Section 4. A larger profile residual is a recorded outcome, not an omitted run.

| Target $\omega_0/m$ | $w/R_Q$ | $\nu/m$ | $E_0/m-Q_0$ | Late core $Q$ | Fitted $\omega/m$ | Profile residual | Phase RMS / rad |
| ------------------: | ------: | ------: | ----------: | ------------: | ----------------: | ---------------: | --------------: |
|                0.90 |     0.5 |     0.8 |      34.014 |        63.987 |          0.986074 |           11.31% |          0.1516 |
|                0.90 |     0.5 |     0.9 |      24.945 |        76.537 |          0.983899 |           11.13% |          0.1655 |
|                0.90 |     0.5 |       1 |      21.031 |        84.797 |          0.981834 |           10.93% |          0.1119 |
|                0.90 |       1 |     0.8 |      -7.023 |       228.943 |          0.904153 |            1.66% |          0.0451 |
|                0.90 |       1 |     0.9 |      -8.601 |       229.177 |          0.904570 |            1.44% |          0.0034 |
|                0.90 |       1 |       1 |      -7.574 |       229.198 |          0.904168 |            1.62% |          0.0397 |
|                0.90 |       2 |     0.8 |      -7.258 |       232.097 |          0.902890 |            1.44% |          0.0475 |
|                0.90 |       2 |     0.9 |      -9.067 |       232.102 |          0.903413 |            1.14% |          0.0053 |
|                0.90 |       2 |       1 |      -8.310 |       232.059 |          0.903159 |            1.30% |          0.0340 |
|                0.90 |       4 |     0.8 |      -2.304 |       198.879 |          0.921416 |           11.75% |          0.0715 |
|                0.90 |       4 |     0.9 |      -5.223 |       200.521 |          0.922655 |           12.86% |          0.0535 |
|                0.90 |       4 |       1 |      -5.286 |       200.268 |          0.922633 |           12.72% |          0.0545 |
|                0.88 |     0.5 |     0.8 |      67.041 |        17.976 |          0.997759 |            6.37% |          0.0704 |
|                0.88 |     0.5 |     0.9 |      45.739 |        36.386 |          0.995460 |            9.91% |          0.0549 |
|                0.88 |     0.5 |       1 |      35.197 |        85.495 |          0.981885 |           13.68% |          0.1952 |
|                0.88 |       1 |     0.8 |     -13.816 |       304.278 |          0.883226 |            0.94% |          0.0387 |
|                0.88 |       1 |     0.9 |     -16.155 |       304.696 |          0.883089 |            0.83% |          0.0044 |
|                0.88 |       1 |       1 |     -14.636 |       304.253 |          0.883239 |            0.94% |          0.0423 |
|                0.88 |       2 |     0.8 |     -15.722 |       309.115 |          0.882323 |            0.83% |          0.0354 |
|                0.88 |       2 |     0.9 |     -17.164 |       308.848 |          0.882310 |            0.73% |          0.0066 |
|                0.88 |       2 |       1 |     -15.378 |       309.039 |          0.882372 |            0.90% |          0.0444 |
|                0.88 |       4 |     0.8 |      -7.043 |       252.889 |          0.897997 |            7.06% |          0.0503 |
|                0.88 |       4 |     0.9 |     -10.182 |       253.879 |          0.898521 |            7.83% |          0.0160 |
|                0.88 |       4 |       1 |      -9.704 |       253.173 |          0.898431 |            7.54% |          0.0325 |
|                0.95 |     0.5 |     0.8 |       8.234 |        58.789 |          0.988109 |            8.81% |          0.1196 |
|                0.95 |     0.5 |     0.9 |       5.984 |        56.182 |          0.990542 |            7.99% |          0.1048 |
|                0.95 |     0.5 |       1 |       5.476 |        58.408 |          0.989642 |            8.09% |          0.1041 |
|                0.95 |       1 |     0.8 |      -0.391 |       133.472 |          0.951930 |            3.55% |          0.0644 |
|                0.95 |       1 |     0.9 |      -1.921 |       133.150 |          0.953608 |            3.25% |          0.0298 |
|                0.95 |       1 |       1 |      -1.868 |       133.209 |          0.953530 |            3.23% |          0.0314 |
|                0.95 |       2 |     0.8 |      -0.018 |       134.151 |          0.951228 |            4.12% |          0.0675 |
|                0.95 |       2 |     0.9 |      -1.899 |       134.511 |          0.952552 |            2.80% |          0.0294 |
|                0.95 |       2 |       1 |      -2.086 |       134.540 |          0.952671 |            2.29% |          0.0231 |
|                0.95 |       4 |     0.8 |       1.340 |       120.477 |          0.963832 |           14.96% |          0.1601 |
|                0.95 |       4 |     0.9 |      -0.894 |       121.583 |          0.964753 |           15.17% |          0.1474 |
|                0.95 |       4 |       1 |      -1.331 |       121.792 |          0.964916 |           15.10% |          0.1440 |
|                0.98 |     0.5 |     0.8 |       2.802 |        33.065 |          0.995843 |            5.84% |          0.1062 |
|                0.98 |     0.5 |     0.9 |       1.482 |        28.882 |          0.996638 |            5.63% |          0.0466 |
|                0.98 |     0.5 |       1 |       1.192 |        28.494 |          0.996726 |            5.63% |          0.0143 |
|                0.98 |       1 |     0.8 |       1.093 |        79.634 |          0.980134 |            4.33% |          0.0814 |
|                0.98 |       1 |     0.9 |      -0.198 |        79.217 |          0.981320 |            3.35% |          0.0566 |
|                0.98 |       1 |       1 |      -0.441 |        79.143 |          0.981557 |            3.34% |          0.0513 |
|                0.98 |       2 |     0.8 |       1.244 |        79.619 |          0.980327 |            4.44% |          0.0807 |
|                0.98 |       2 |     0.9 |      -0.162 |        79.917 |          0.981151 |            2.96% |          0.0475 |
|                0.98 |       2 |       1 |      -0.480 |        79.980 |          0.981331 |            2.44% |          0.0363 |
|                0.98 |       4 |     0.8 |       1.570 |        70.798 |          0.985204 |           12.49% |          0.2042 |
|                0.98 |       4 |     0.9 |       0.075 |        71.176 |          0.986221 |           11.69% |          0.1882 |
|                0.98 |       4 |       1 |      -0.305 |        71.267 |          0.986486 |           11.60% |          0.1819 |
