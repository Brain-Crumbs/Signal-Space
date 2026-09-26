# Test 7: surface-only predicted reception

This implements program v0.2 sections 7–10 and 15.7 in the accepted flat spherical SS OCF 1 sector. It follows the verified Test 6 longevity and response prerequisites, without changing their action, frozen core, clock eigenmode, coupling or frequency. Issue #71 tracks this work.

## Physical question and prediction boundary

Can a calibrated receiver predict a local clock record from an incident waveform measured upstream, without access to the interior neutral history or the eventual nonlinear receiver? The competing explanation is that the earlier agreement depended on a supplied interior history or on an unresolved tiny local record.

Let `r` be radius, `t` flat-frame proper time at a fixed probe, `a` the neutral field and `b=r*a`. The upstream sphere is at `R_s=14`. In its approximately vacuum exterior,

`b = F(t+r-R_s) + G(t-r+R_s)`.

The incoming and outgoing characteristic derivatives are

`I = (R_s*a_t + a + R_s*a_r)/2 = F'`,

`O = (R_s*a_t - a - R_s*a_r)/2 = G'`.

The acquisition stage evolves only the linear neutral equation on the frozen core and exports the surface values `a,a_t,a_r`. The prediction stage reloads that artifact and integrates `I` over `0<=t<=16`. A cubic antiderivative with zero initial value reconstructs `F`; a documented linear closure correction sets its final value to zero. Replay initial data are `b(r,0)=F(r-R_s)` and `b_t(r,0)=F'(r-R_s)`, with compact support in the acquisition window. This is an approximate inverse propagation map, not an exact identity of the lattice. Spatial refinement tests it. The full surface record extends to t=55 and shows reflected radiation separately.

No receiver interior samples cross this boundary. The predictor does receive the frozen core and mode, their quiet evolution and the independently declared clock phase. All surface, replay, calibration and prediction artifacts are hashed before the first nonlinear receiver-start event.

## Action and response

Use `c=hbar=m=1`, `s=|Phi|^2`, `U(s)=s-s^2+s^3`, `Z(s)=1+0.2s`, `V(s)=0.25-0.4s+0.2s^2`, and clock quartic coefficient 0.1. The registered discrete Hamiltonian is unchanged from Test 6's response prerequisite. It has reciprocal neutral kinetic and gradient terms, with regular-origin radial fields and zero outer boundary. No sponge is used over t=0..100.

Write `a=A*a1+O(A^3)`, `Phi=Phi0+A^2*Phi2+O(A^4)`, `chi=chi0+A^2*chi2+O(A^4)`. Neutral gradients drive the second-order core with `0.1*(partial a1)^2*Phi0`; the resulting density coefficient `s2=2 Re(conj(Phi0)*Phi2)` drives the clock with `-V'(s0)*s2*chi0`. The worker integrates these full time-dependent Taylor equations, including reciprocal core/clock terms, on the matched quiet history. No adiabatic approximation or fitted susceptibility is used. Suppressing core response gives an executed deliberately incomplete replay with zero induced clock response.

## Preparations and controls

Two compact incoming pulses use `b=A*c*cos^4(pi*(r-c)/(2w))` inside `|r-c|<w`, with centers c=18 and 26, width w=3 and `b_t=b_r`. Both begin outside the upstream sphere. The earlier pulse reflects at the regular origin and travels outward through the later inward pulse. These are counterpropagating radial shells, not independent planar beams. Each pulse alone and both together isolate the interaction term by subtraction. This avoids the earlier control's initially unmeasured inner shell.

Run amplitudes 0, 0.002, 0.004, 0.008 and -0.004 for the first pulse; nominal second-only, both and sign-reversed both; and nominal first with clock phase pi/3 plus its matched quiet baseline. Initial clock amplitude is 0.001, core frequency 0.9 and frozen eigenfrequency Omega=0.41274991. Readout radius is 0.1 on every grid.

The independent numerical controls are h=0.1, 0.05, 0.025 at R=80, dt=0.02, 0.01, 0.005 respectively; dt=0.01 at h=0.1; and R=160 at h=0.1. The new h=0.025 grid uses natural cubic interpolation of the frozen h=0.05 core and mode with zero radial endpoints. It does not refit the profile, eigenfrequency or amplitude calibration. This tests propagation/evolution refinement with a fixed prepared object; it is not a new profile-existence proof.

## Local marker and cycle record

The operational phase definition is `theta=unwrap atan2(-chi_dot/Omega,chi)`, measured at r=0.1. It uses a local field and its local proper-time derivative. It is a defined quadrature record, not a claim of an exact nonlinear angle variable. Start is the first rising crossing of `|a|=1e-4`; end is the last falling crossing in the registered t=0..100 local acquisition window. Selection of the last crossing is retrospective. Missing markers are unresolved, not fabricated.

The interval record is the pulse-minus-quiet accumulated local phase between those two events, divided by `2*pi`. The quiet reference is sampled at the same event proper times as a counterfactual diagnostic; a quiet receiver does not physically detect a nonexistent pulse. This does not establish a standalone instrument without that reference. The prediction supplies its own neutral marker times and the linearized phase correction before nonlinear evolution. Its scalar interval forecast is compared against the actual scalar interval, so receiver marker times cannot be used to tune the forecast.

For nominal first, second, both and changed phase, the cycle error budget is the sum of direct finer/fine, base/time and base/wide interval differences plus 1e-11 cycles. A nonzero record must exceed five times this budget. Forecast error must be below the larger of 5% of the record or that budget. Separate local trace, sign, amplitude, overlap, conservation and numerical controls are locked in the plan. No threshold is changed after execution.

## Reproduction and limitations

Use `.agents/scripts/run_plan.py` with `docs/research/plans/gross-test-07.json`, the repository root, an external workspace and `--execute`. Analyze, report and verify through the registered runtime, then build the reader export using `.agents/scripts/package_experiment.py`. The ad hoc workflow recipe is `gross-test-07`.

A technically completed run may fail or remain unresolved scientifically. This experiment does not establish angular stability, two-object recoil, transformed-coordinate invariance, gravity, autonomous Candidate A clocks or emergent spacetime. Tests 8 and 9 remain separate. A local interval that is unresolved blocks an unqualified Test 7 pass even if a full-history response curve agrees well.
