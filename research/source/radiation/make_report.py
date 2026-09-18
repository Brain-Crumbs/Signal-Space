import json,pathlib
R=pathlib.Path(__file__).resolve().parent;O=R/'deliverables'
s=json.loads((R/'results/kick_fine_200_1000_spectrum.json').read_text());diag=json.loads((R/'results/diagnostics.json').read_text());d=diag[1]
lines={l['n']:l for l in s['lines']}
report=r'''# Signal Space charged-clock radiation milestone

Date: 17 September 2026.

## Result

**The persistent excited remnant is measurably radiating. Its slow relaxation is quantitatively explained by weak charged-wave emission in the original equations.** Most of the fitted noncarrier field norm is in a counterrotating component below the free-wave threshold. The radiating components are much smaller, and their nonlinear source has a small overlap with the spatial pattern of an outgoing wave.

For the selected remnant, two harmonic bands carry approximately 89.3% and 10.7% of the resolved harmonic radiated power. Their energy and charge fluxes predict an excitation-energy loss rate of about $2.807\times10^{-5}m^2$. Direct measurement of the core gives $2.815\times10^{-5}m^2$, a difference of 0.27%, smaller than the approximately 0.8% change under spatial refinement. A separate Fourier cross-spectrum agrees with the coherent harmonic flux extraction.

This identifies a concrete radiation mechanism. It does not require adding friction or a neutral bath to explain the measured decline in this preparation. It also does not prove that the remnant will eventually reach the ground branch, establish a constant exponential decay law, identify a complex resonance pole, or rule out nonradiating solutions elsewhere in the model.

## 1. State, equations, and continuation

Continue the actual final Cauchy data from `unbound_settled_fine`, the formation run with target $\omega_0=0.90$, $w/R_Q=2$, $\nu/m=1.3$, $\Delta x=0.025/m$, and original final time $t_0=2400/m$. The saved state is provided in the source archive. It is not replaced by a fitted Q-ball or assigned an extra oscillator.

Use the unchanged $a=0$ invariant sector:

$$
\Phi_{tt}-\Phi_{xx}+\Phi-2|\Phi|^2\Phi+3|\Phi|^4\Phi=0,
\qquad \lambda=0.01,
$$

in units $m=g=h=1$. The neutral coupling is still part of the parent model, but $a=a_t=0$ stays zero exactly. This calculation concerns classical charged radiation only.

Continue for $1000/m$ and analyze the final $800/m$, corresponding to original formation times $2600\le mt\le3400$. The domain is $|x|\le1200/m$. All saved data inside $|x|<1150/m$ are retained; only the outer interval $1150<|mx|<1200$ is tapered to zero. This distant taper prevents a boundary discontinuity. It cannot influence the innermost-to-outermost diagnostic region $|mx|\le80$ during the $1000/m$ continuation in the continuum domain of dependence. It is not a core extraction or a cooling operation on the object. The numerical stencil has dispersive precursors; the causal statement refers to the continuum model and the resolved propagation limit.

Three continuations use $(m\Delta x,m\Delta t)=(0.05,0.01),(0.025,0.005),(0.025,0.0025)$. They sample the same saved fine-grid state; the coarse initial state is obtained by restriction. Thus these checks resolve the continuation and radiation analysis, not a new independent refinement of the entire initial formation history.

## 2. Measure the field, not just its phase trace

Record complex fields over $|mx|\le30$ at spatial spacing $0.05/m$ and temporal spacing $0.1/m$, together with field, velocity, and spatial derivative at detectors $mx=\pm20,\pm30,\pm40,\pm60,\pm80$ and at the center. Record core energy and charge in windows 20, 40, and 60 every $1/m$.

Fit the center field to a slowly varying harmonic expansion,

$$
\Phi(t,x)\simeq\sum_{n=-4}^{4} A_n(t,x)
 e^{-i[\theta_c(t)+n\Theta(t)]},
$$

$$
\dot\theta_c(t_c)=\omega_c,\qquad
\dot\Theta(t_c)=\Omega,\qquad
\sigma_n=\omega_c+n\Omega.
$$

Quadratic temporal phases allow a small chirp. Frequencies are estimated with constant complex harmonic coefficients and Hann weighting; spatial coefficients are then fit with constant and linear complex envelopes. This separation avoids an artificial first-order degeneracy between fitted frequency and the phase of a free linear envelope.

At continuation midpoint $mt_c=600$ (original time 3000), the fine result is

$$
\omega_c=0.8999232m,\qquad
\Omega=1.7284747m.
$$

The weighted relative center-field residual is $2.21\times10^{-4}$. These are fit parameters of an approximately quasiperiodic, slowly evolving field, not exact eigenfrequencies. Half-window fits shift them by a few parts in $10^6$ and recover the same radiation strengths. Digits beyond the stated convergence should not be interpreted as physical precision.

### Actual frequency components

The free vacuum equation implies $\sigma^2=k^2+m^2$. Negative signed frequency denotes opposite complex phase rotation and opposite charge for a free wave; its energy remains positive.

| Harmonic $n$ | Measured signed $\sigma_n/m$ | Vacuum channel | $\int_{-12/m}^{12/m}|A_n|^2dx$, in $1/m$ |
|---:|---:|---|---:|
| $0$ | 0.899923 | Closed carrier | 1.32728 |
| $-1$ | −0.828551 | Closed oscillating component | $4.27613\times10^{-2}$ |
| $+1$ | 2.628398 | Open, positive-charge radiation | $2.01594\times10^{-5}$ |
| $-2$ | −2.557026 | Open, negative-charge radiation | $3.46489\times10^{-7}$ |
| $+2$ | 4.356873 | Open, much weaker radiation | $6.73291\times10^{-8}$ |

Among the fitted $n\ne0$ harmonics, **99.952% of the core field norm is in the closed $n=-1$ component**. Its norm is about 2121 times that of $n=+1$. This is an amplitude-squared field norm on a stated window, not a fraction of total energy or a quantum occupation probability. Nonlinear interaction energy cannot be allocated to independent harmonics by simply reading this table.

The closed component's amplitude tail over $8\le mx\le14$ decays with fitted exponent $\kappa/m\simeq0.55949$, compared with the regulator-adjusted free prediction $0.55991$. This checks that the inferred subthreshold component actually has an evanescent spatial tail.

The earlier two-component conjecture is therefore supported by the field itself, with one important extension: the next negative-frequency harmonic is also a significant radiation channel.

## 3. Frequency-resolved energy and charge flux

For the structural field,

$$
S_E=-\frac2\lambda\operatorname{Re}(\Phi_t^*\Phi_x),
\qquad
j_Q=\frac2\lambda\operatorname{Im}(\Phi^*\Phi_x).
$$

Extract each harmonic independently in $\Phi$, $\Phi_t$, and $\Phi_x$. At a right-hand detector its time-averaged contribution is

$$
P_n^{R}=-\frac2\lambda\operatorname{Re}(V_n^*G_n),
\qquad
J_n^{R}=\frac2\lambda\operatorname{Im}(A_n^*G_n).
$$

The preparation and evolution are reflection symmetric. Both outward directions contribute equal positive energy flux, so the reported outward power is twice the right-hand value. Oppositely directed radiation does not cancel its energy; it cancels total emitted momentum in this symmetric experiment.

At $x=40/m$ on the fine mesh:

| Harmonic | Outward power, both sides / $m^2$ | Fraction of fitted harmonic power |
|---|---:|---:|
| $n=+1$, $\sigma\simeq2.6284m$ | $3.43063\times10^{-5}$ | 89.308% |
| $n=-2$, $\sigma\simeq-2.5570m$ | $4.10650\times10^{-6}$ | 10.690% |
| $n=+2$, $\sigma\simeq4.3569m$ | $6.67907\times10^{-10}$ | 0.00174% |
| All fitted open harmonics | $3.84136\times10^{-5}$ | 100% |

The net outward charge rate in the fitted open harmonics is

$$
J_{\mathrm{harm}}=1.14462\times10^{-5}m.
$$

The negative-frequency channel carries negative charge out, while carrying positive energy out. Both facts are included in the ledger.

Across detectors from 20 to 80, the main outgoing amplitudes are essentially constant after accounting for the propagation phase. For $n=+1$ the right-moving amplitude is approximately $1.159\times10^{-4}$; for $n=-2$ it is $4.131\times10^{-5}$. The inferred incoming components are tiny compared with these outgoing components. The reported small incoming values depend on the fit, finite window, and derivative convention; they are not a numerical assertion of an exactly zero incoming field.

### Independent Fourier check and slow formation tails

Compute the Fourier cross-spectrum of the actual velocity and spatial derivative using a Hann window. With $V_k,G_k$ defined as FFT coefficients divided by sample count,

$$
P_k^{\rm both}=-\frac4\lambda
\frac{\operatorname{Re}(V_k^*G_k)}{\langle w^2\rangle}.
$$

Its sum obeys Parseval's identity and equals the directly window-weighted outward power. Integrating bands of half-width $0.04m$ around the two main signed frequencies gives $3.43061\times10^{-5}m^2$ and $4.10647\times10^{-6}m^2$, agreeing with the harmonic extraction to better than $10^{-4}$ relative. Parseval closure itself is near floating-point precision; it checks normalization, not continuum accuracy.

There is also a broad, near-threshold component left from formation. It has appreciable field amplitude at distant detectors but low group speed. Consequently **harmonic radiation is not all exterior radiation**: the directly averaged total outward power grows from approximately $3.89\times10^{-5}m^2$ at $x=20/m$ to $4.99\times10^{-5}m^2$ at $x=60/m$ over this finite window as different parts of the older dispersed field cross the detectors. These different radii sample different radiation histories; equal-time totals need not be radius independent. The persistent narrow harmonic bands, by contrast, agree across radii.

## 4. Test spatial cancellation using the actual nonlinear source

Rewrite the same field equation as

$$
(\partial_t^2-\partial_x^2+1)\Phi=S[\Phi],
\qquad
S=2|\Phi|^2\Phi-3|\Phi|^4\Phi.
$$

Project $S[\Phi(t,x)]$ onto the **same measured temporal harmonics**. No independently adjustable source, coupling, or oscillator is introduced. For an approximately monochromatic open component,

$$
A_n''+k_n^2 A_n=-S_n,
\qquad k_n=\sqrt{\sigma_n^2-1}.
$$

With outgoing boundary conditions, the right-going amplitude is

$$
\boxed{
A_{n,R}^{\rm pred}=-\frac{1}{2i\,\operatorname{sgn}(\sigma_n)k_n}
\int_{-\infty}^{\infty}S_n(x)
 e^{-i\operatorname{sgn}(\sigma_n)k_nx}\,dx .
}
$$

For negative signed frequency, a right-going group velocity requires negative wavenumber. The sign in this formula is therefore essential. It is not an assignment of negative energy.

The numerical comparison uses the corresponding discrete dispersion and Green-function factor described in Section 7. Source integration uses the measured core field; outgoing amplitude is measured separately at distant detectors. The source is itself extracted from a nonlinear solution, so this is an on-solution radiation reconstruction and overlap diagnostic, not a parameter-free prediction from an independently prescribed source or a small-amplitude Born approximation.

### Measured overlap

Define

$$
\mathcal C_n=
\frac{\left|\int S_n(x)e^{-i\operatorname{sgn}(\sigma_n)k_nx}dx\right|}
{\int |S_n(x)|dx}.
$$

This compares the coherent outgoing source sum with the sum of its absolute contributions. For an even source the numerator can also be written as the magnitude of $2\int_0^\infty S_n(x)\cos(k_nx)dx$, making the alternating spatial contributions explicit.

| Channel | $\int|S_n|dx$ | Magnitude of outgoing source integral | $\mathcal C_n$ |
|---|---:|---:|---:|
| $n=+1$ | 0.0720417 | $5.63127\times10^{-4}$ | 0.0078167 |
| $n=-2$ | 0.0063141 | $1.94357\times10^{-4}$ | 0.0307808 |
| $n=+2$ | 0.0101507 | about $2.548\times10^{-6}$ | 0.0002510 |

For the dominant channel, only **0.782%** of the sum of source magnitudes survives in the outgoing amplitude. Squaring gives approximately $6.11\times10^{-5}$ relative to a hypothetical fully aligned source sum. This is a diagnostic normalization, not a physically realized alternative preparation: arbitrarily aligning all source contributions would change the dynamics.

The reconstructed dominant outgoing amplitude is approximately $1.159\times10^{-4}$, matching the detector amplitude within about $2\times10^{-5}$ relative in the primary fitting window. The $n=-2$ match is within approximately $7\times10^{-5}$. These very small reconstruction residuals characterize consistency on a given grid; the physical rate still has roughly percent-level spatial-regulator uncertainty.

Source integration stabilizes quickly once the whole core is included. For $n=+1$, the integral magnitudes at half-widths $5,8,12,20,30$ are respectively about $9.8124\times10^{-4}$, $5.6265\times10^{-4}$, $5.63136\times10^{-4}$, $5.63127\times10^{-4}$, and $5.63127\times10^{-4}$. A calculation that retained only the central region would give the wrong radiation amplitude.

The cubic and quintic source terms also partially cancel. For $n=+1$, the ratio $|I_3+I_5|/(|I_3|+|I_5|)$ is about 0.34 after outgoing-wave projection. This and the small net spatial overlap are complementary descriptions of one source. Likewise, the weak open field component and source cancellation should **not** be multiplied as independent suppression probabilities.

The directly established mechanism is therefore a large confined component with weak conversion into propagating harmonics, whose outgoing source contributions largely cancel. This calculation does not establish that the cancellation is symmetry-protected, universal under parameter changes, or caused by exact integrability.

## 5. Does that radiation explain the observed persistence?

A charged object loses both energy and charge. Its ground-branch energy therefore changes while it radiates. Define the core excitation energy as

$$
\Delta E(t)=E_{\rm core}(t)-M(Q_{\rm core}(t)),
\qquad \frac{dM}{dQ}=\omega_Q.
$$

The frequency $\omega_Q$ comes from the exact equilibrium branch at the current core charge; it is not silently replaced by the excited remnant's measured carrier frequency. The corresponding balance is

$$
\boxed{-\dot{\Delta E}=P_{\rm out}-\omega_Q J_{\rm out}.}
$$

Over the measured window, $\omega_Q\simeq0.9034744m$ and the mean core excitation energy inside $|mx|\le20$ is $12.26662m$. The resolved open harmonics give

$$
P_{\rm harm}-\omega_Q J_{\rm harm}
=2.80722\times10^{-5}m^2.
$$

A linear regression of the directly recorded $E_{20}(t)-M(Q_{20}(t))$ gives

$$
-\dot{\Delta E}_{\rm measured}
=2.81476\times10^{-5}m^2.
$$

The agreement is approximately **0.27%**. The small difference is consistent with additional near-threshold radiation, finite-window definitions, and numerical effects. At larger core windows the inferred excitation decline includes more of the remaining dispersing field; it increases to approximately $2.856\times10^{-5}m^2$ at window 40 and $2.955\times10^{-5}m^2$ at window 60. The window-20 estimate is the principal localized-core diagnostic; the window sensitivity is retained rather than hidden.

Thus the persistent narrow-band radiation accounts for almost all of the measured core relaxation in this interval. The earlier observation of little decay over a few thousand time units did not imply zero coupling.

### Rate scale, not an extrapolated lifetime

The current excess energy divided by its measured loss rate is

$$
\tau_{\rm rate}\equiv\frac{\Delta E}{-\dot{\Delta E}}
\simeq4.36\times10^5/m,
$$

or about **62,400 carrier cycles** at the current phase rate. The original formation calculation lasted only $2400/m$. A slow loss of this size can therefore be resolved spectrally and through energy accounting while leaving the object visibly excited over the original observation window.

This ratio is not a measured lifetime or proof of exponential damping. The harmonic amplitudes, charge, coupling overlap, and relative importance of different channels can change as the object relaxes. We have not evolved it for $4\times10^5/m$ or proved its eventual final state.

## 6. Interpretation for Signal Space

The qualitative suspicion is now supported by three distinct measurements:

1. The large counterrotating component has the predicted evanescent tail outside the object.
2. Small, propagating harmonics are actually present and carry positive energy outward.
3. The nonlinear source integral exhibits strong spatial cancellation and reconstructs those outgoing amplitudes, while the energy/charge ledger predicts the core's measured decline.

For this particular remnant, an additional cooling mechanism is unnecessary to explain the observed slow relaxation. The existing charged field already provides a weak outlet. The remaining question is the long-term relaxation law and whether the radiation coupling remains nonzero as the excitation becomes smaller.

This is a long-lived **radiating excitation**, not evidence for an exactly nonradiating breather. The finite nonlinear calculation does not by itself classify the state as a linear resonance; locating an outgoing-wave pole or computing a Floquet spectrum would be required for that stronger identification. It also does not rule out special nonradiating states elsewhere in the theory.

The cancellation occurs among source contributions to each outgoing wave. It is not cancellation of leftward against rightward radiation energy, and it is not a quantum common-record or coherence result. Split-complex bookkeeping, emergent metric claims, photon identification, and microscopic origins of the potential remain outside this calculation.

## 7. Numerical checks and reproducibility

The original drift–kick–drift evolution is used unchanged in the charged sector. For source reconstruction, record the kick-position variable $\psi_{j}^{n+1/2}=\Phi_j^n+(\Delta t/2)\dot\Phi_j^n$. It satisfies the exact second-order centered recurrence

$$
\frac{\psi^{n+3/2}-2\psi^{n+1/2}+\psi^{n-1/2}}{\Delta t^2}
=D_x^2\psi^{n+1/2}-\psi^{n+1/2}+S(\psi^{n+1/2}).
$$

For a harmonic of frequency $\sigma$, use

$$
\widehat\sigma=\frac2{\Delta t}\sin\frac{\sigma\Delta t}{2},\qquad
\widehat\sigma^2=1+\left(\frac2{\Delta x}\sin\frac{k\Delta x}{2}\right)^2.
$$

The outgoing Green factor replaces $k$ by $\sin(k\Delta x)/\Delta x$. Integer-time position coefficients at detectors are divided by $\cos(\sigma\Delta t/2)$ when compared with the kick-position source. Spatial source quadrature uses the dense smooth profiles sampled at $0.05/m$; finite integration-window checks are given above. Slow chirps and envelope evolution make a finite-window harmonic approximation necessary; no claim of an exact time-periodic solution is made.

The complete finite-domain energy diagnostic includes both boundary bonds. Charge conservation follows from the discrete $U(1)$ symmetry. Energy is conserved by the continuous-time lattice Hamiltonian and only approximately by the time splitting. The final source and supplied ledgers use the full boundary-bond convention; the spectra and core diagnostics do not depend on this outer-boundary bookkeeping.

| Mesh $(m\Delta x,m\Delta t)$ | Harmonic outward power / $m^2$ | Predicted excitation loss / $m^2$ | Measured core excitation loss / $m^2$ |
|---|---:|---:|---:|
%%CONVERGENCE%%

The coarse-to-fine harmonic power changes by approximately 0.82%. Halving the time step at fixed fine spatial mesh changes it by only 0.010%. The two major flux bands and the cancellation result are therefore resolved to roughly percent accuracy in space and substantially better in time; no sub-percent continuum certification is claimed. The smallest higher harmonics have larger relative spatial uncertainty but contribute negligibly to the total power.

Splitting the fine time window into $200$–$600$ and $600$–$1000$ changes the dominant power by only about 0.033%, with the slight decline expected from a relaxing state. Source-to-detector reconstruction remains accurate in each half. A separate FFT cross-spectrum provides the power normalization check described above.

Maximum relative charge drift in these continuations is below $3\times10^{-14}$. The exact executed full-energy drift values are included in `results/diagnostics.json` and are %%ENERGY_DRIFTS%% for the three meshes in table order. The source archive preserves the initial state, complete detector histories, core ledgers, extracted spatial harmonics, source profiles, and analysis outputs. Large dense space-time field files regenerate from the supplied code rather than being required as downloads.

Run `python run_all.py` with a C++17 compiler and Python NumPy, SciPy, and Matplotlib. The three continuations run locally, with no external data or network service required. The initial-state provenance is the saved formation milestone, not a new fitting ansatz. `README.md` explains the file formats, sampling, and regeneration steps.

![Field components, radiated spectrum, source cancellation, and energy balance](Signal_Space_Charged_Clock_Radiation_Diagnostics.png)

## 8. Next discriminating calculation

Vary the excitation amplitude at fixed total charge, and determine how the dominant radiated power scales with that amplitude while the ground-state profile and charge shift are controlled. Combine that with an outgoing-wave resonance calculation about the stationary branch or a Floquet calculation about the excited recurrence. This would distinguish approximately exponential weak-resonance decay from higher-order nonlinear damping and test whether a special zero-radiation limit exists.

The present rate estimate supplies a concrete benchmark for that calculation. Repeating longer evolutions without first establishing the amplitude dependence would not justify extrapolating a lifetime.

## Sources

The model, initial state, and previous diagnostics come from the saved *Signal_Space_Charged_Clock_Formation_Milestone.md*, its source archive, *Signal_Space_Ordered_Reception_Charged_Clock_Model.md*, and *Signal_Space_Charged_Clock_Stability_Milestone.md*. This report's frequencies, source overlaps, fluxes, and continued evolutions were calculated for that supplied candidate.

Long-lived Q-ball oscillations and their relation to deformed breather dynamics have established precedent: Bowcock, Foster, and Sutcliffe, [Q-balls, Integrability and Duality](https://arxiv.org/abs/0809.3895). That literature motivates possible later interpretations; it does not establish integrability of this polynomial potential or replace the measurements above. No novelty claim is made for Q-balls, sidebands, or outgoing Green-function reconstruction.
'''
rows=[]
for item in diag:
 name=item['name'];mesh={'kick_coarse':'0.05, 0.01','kick_fine':'0.025, 0.005','kick_timefine':'0.025, 0.0025'}[name]
 rows.append(f"| {mesh} | {item['harmonic_energy_flux']:.7g} | {item['predicted_excess_decay_rate']:.7g} | {item['measured_excess_decay_rate']:.7g} |")
report=report.replace('%%CONVERGENCE%%','\n'.join(rows)).replace('%%ENERGY_DRIFTS%%',', '.join(f"{x['energy_drift']:.3g}" for x in diag))
(O/'Signal_Space_Charged_Clock_Radiation_Milestone.md').write_text(report)
print('Report written:',len(report.split()),'words')
