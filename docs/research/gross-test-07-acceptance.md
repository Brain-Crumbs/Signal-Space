# Test 7: full known-incident acceptance protocol

Issue #80 and PR #81. Registered experiment `gross.reception-acceptance.v1` tests Program v0.2 section 15.7 in the unchanged flat spherical SS OCF 1 model. It is a new complete acceptance suite, not another linear reconstruction prerequisite. Scientific acceptance is conditional on every locked check passing.

## Scope decision before execution

The program asks whether an independently calibrated clock predicts its response to a known incident field. This predictor is explicitly given the prepared incident initial field and the accepted frozen receiver calibration. The linear upstream surface history is independently recorded before receiver evolution. No interior sample from the coupled receiver or fitted receiver response enters prediction. Robust recovery of unknown initial data from surface records is a stronger, separate extension; earlier failures of that extension remain failures.

The first and last marker events are fixed local proper-time sampling events at 10 and 60 on the stationary probe at radius 0.1, with the common preparation event setting zero. They apply unchanged to every amplitude, sign, phase, quiet preparation and grid. This is a controlled flat-frame local diagnostic with an externally specified timer, not an autonomous pulse detector. It uses neither first/last threshold-crossing selection nor source labels read by the receiver. The interval begins before expected reception and extends through reflected-shell overlap and the delayed response. The endpoint choice is locked before any new receiver results. Legacy event failures are not reclassified.

## Action and forecast

Retain the accepted frequency 0.9 core, clock eigenmode and frequency 0.41274991, clock amplitude 0.001, neutral coupling 0.2, positive neutral inertia and the registered discrete Hamiltonian. With `b=r*a`, evolve formal neutral coefficients `b=A*b1+A^3*b3` and charged/clock coefficients through fourth order. The full time-dependent tangent equations and fourth-order sources are those already independently tested in `gross-test-07-order4.md`; no adiabatic approximation, new interaction or fitted response coefficient is introduced.

For local complex quadrature `z=chi-i*chi_dot/Omega`, the phase forecast in radians is `A^2 Im(z2/z0)+A^4 Im(z4/z0-(z2/z0)^2/2)`. The primary observable is the predicted accumulated pulse-minus-quiet phase between the two fixed events divided by `2*pi`. The complete receiver's local quadrature relative to its matched quiet preparation supplies the withheld actual record. Second order is retained separately to verify the weak response and expose the effect of the derived fourth-order correction. Local core-density response and the neutral derivative invariant are recorded as mechanism checks.

## Fresh preparation and controls

Two compact incoming `cos^4` radial shells have centers 19 and 27 and half-width 3.25. Their initial temporal derivatives equal their radial derivatives. They start outside the surface at radius14. The inner shell reflects at the regular origin and meets the still-incoming second shell; counterpropagation is radial, not two independent planar beams. Width is comparable to the prior calibrated broad forcing; the full time-dependent response avoids needing an adiabatic separation from the measured core spectrum.

Execute all ten preparations: quiet; first pulse at amplitudes 0.002, 0.004, 0.008 and -0.004; second only at0.004; both at0.004 and -0.004; changed-phase quiet; first pulse at0.004 with clock phase pi/3. The separately evolved frozen-core Taylor control suppresses neutral-induced core response and must give zero clock perturbation. Individual-pulse subtraction tests the pair interaction. All twenty forecast cases (four per numerical variant) and the frozen-core control are saved and hashed before the first of fifty coupled receiver preparations begins.

Three meshes use h=0.1,0.05,0.025 at R80 with timesteps0.01,0.01,0.005. The independent time control halves dt at h0.05; the domain control doubles R to160 at h0.1. The finest mesh interpolates the accepted h0.05 profile and mode with zero radial endpoints; it tests evolution of that fixed calibrated preparation, not a new continuum eigenproblem. Duration65 precedes an outer-boundary return. Output every0.05 and a0.1 decimation control preserve both fixed event times exactly. Their timing is prescribed, so an arrival-reconstruction tolerance is not an acceptance gate for this protocol.

## Locked acceptance

The executable config contains the exact checks. For each nonquiet preparation, sum the absolute finest/fine, fine/time and base/wide changes in both the measured and predicted interval, the output-sampling change, and a1e-11-cycle floor. The measured record must exceed five times this combined budget. Its forecast error must be at most the larger of5% of the measured record or that budget. All eight nonquiet preparations, including both signs and the amplitude ladder, must meet these gates.

Require resolved and accurately predicted pair-minus-individual phase response, sign-even phase response, the weak quadratic amplitude law, vanishing quiet and frozen-core responses, and accurate local phase/clock/density traces. Demand a contracting phase-trace spatial difference separately for actual and forecast, with independent time/domain controls. Require relative charge and total energy drift below1e-5 and matched energy residual below1% of initial incident energy on every grid. A missing record or excessive uncertainty is unresolved; a resolved discrepancy is a failure. No threshold or endpoint is adjusted after inspecting results.

This includes the full program controls while making the known preparation and fixed event convention explicit. A pass supports Test7 reception prediction in the calibrated radial sector and permits planning Test8. It does not establish unknown-input reconstruction, autonomous timing, two-object survival/recoil, observer invariance, gravity or emergent spacetime. A failed old run is never overwritten by this new classification.

## Figures and reproduction

Six planned figures show shell propagation/overlap, incident forcing and core/clock response, predicted versus actual local phase histories, interval/error-budget comparisons, sign/amplitude/overlap controls, and convergence/conservation. Exact plotted data and four-part interpretations accompany the standard report. Raw data and figures remain outside Git.

Run the registered recipe `gross-test-07-acceptance` through `.agents/scripts/run_experiment.py`. The plan is locked before execution; source must be committed and clean. The runner preserves failed stages and immutable raw evidence. Analyze and report from saved output, verify canonical evidence, and validate the paired reader export before interpreting acceptance.
