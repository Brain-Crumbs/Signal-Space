# Test 6 prerequisites: frozen longevity and predicted radial response

Issue #69, following #66. Source: Operator Program v0.2 sections 7-9 and 15.6-15.7. Test 6 passed its selected-branch criteria, not every attempted branch or every receiver prerequisite. The two low-frequency BVP failures remain unresolved; a successful radial clock does not establish nonspherical stability. Its 20-period controls did not establish refined 100-period longevity. Its historical energy estimator could not resolve clock radiation.

Two independently locked runs close specific gaps, without starting a two-object experiment. Inputs are the exact nominal, fine and wide omega_Q=0.900 profile and eigenmode files of run-080a63d117abd84d. Their hashes are in both configurations and copied to each run. No profile is re-solved. The nominal frequency Omega=0.41274991 sets the calibration and common duration. A refinement retains its saved discretized eigenmode, with no frequency refitting. Local chi is sampled at the same physical radius r=0.1 on all grids, correcting the moving readout location r=h used in the older control comparisons.

## 6a: full refined baseline

Run the original reciprocal core/clock scheme for 100 nominal periods on h=0.1, dt=0.04; h=0.05, dt=0.02; and h=0.1, dt=0.02. Peak initial chi is 0.001. Keep R=80 and the logged original sponge beyond r=60. Measure local positive-going crossings, eigenmode energy fraction, charge plus sink, and the original energy diagnostic. The last remains background limited and cannot become a clock-radiation claim. The existing Test 6 wide-box control was shorter; this run does not claim a 100-period infinite-volume limit.

## 6b: action-derived prediction before receiver evolution

Use the same flat SS OCF 1 action with an active neutral field. Register Z(s)=1+epsilon*s, epsilon=0.2, M0=m=1; s=|Phi| squared. Test 6 had a=0, so it did not calibrate epsilon. This value is an explicit new experiment parameter, not a measured constant. U(s)=s-s squared+s cubed; V(s)=0.25-0.4s+0.2s squared; clock self-coupling zeta=0.1.

The exact continuum core forcing is `+(epsilon/2) [(d_t a)^2-(d_r a)^2] Phi` in the acceleration equation. A locally planar single null wave has zero contraction; radial spreading, material scattering and counterpropagation can make it nonzero. Quadratic amplitude order alone does not ensure a large or nonzero clock response.

Let A be the signed incident packet coefficient and expand `a=A*a1+O(A^3)`, `Phi=Phi0+A^2*dPhi2+O(A^4)`, `chi=chi0+A^2*dchi2+O(A^4)`. The subscript 0 denotes the fully evolving matched no-pulse preparation, including clock backreaction, not an artificially static core. Define `ds2=2 Re(Phi0* dPhi2)`, where the star is complex conjugation. The neutral first-order field solves `div(Z(s0) grad a1)=0`. With `C=U_s+V_s*chi0^2/2`, the second-order core equation is

`d_tt dPhi2 = Laplacian(dPhi2) - C*dPhi2 - [(U_ss+V_ss*chi0^2/2)*ds2 + V_s*chi0*dchi2]*Phi0 + (epsilon/2)*(partial a1)^2*Phi0`.

The second-order clock equation is

`d_tt dchi2 = Laplacian(dchi2) - [V(s0)+3*zeta*chi0^2]*dchi2 - V_s*ds2*chi0`.

Here U_s and V_s denote derivatives with respect to s; dPhi2 and dchi2 start at zero. These equations predict the coefficient of A squared with no fitted coefficient. The worker saves and hashes predictions on every grid before evolving any full nonlinear pulse-driven receiver. The nonlinear action is exactly even under global a sign reversal. The local difference should approach the predicted A-squared coefficient; sign evenness alone cannot validate that coefficient.

Radial fields are u=r*Phi, w=r*chi and b=r*a. The neutral canonical momentum is p=Z*dot(b). A positive discrete neutral Hamiltonian is `H_a/(4*pi*h)=sum[p^2/(2*Z)]+sum[Z_face*(G*b)^2/2]`, with `G*b=r_face*diff(b/r)/h` and arithmetic face Z. Its gradients give both neutral propagation and reciprocal core forcing. Core and clock use the original second-difference radial Laplacian. RK4 integrates the complete Hamilton equations; energy diagnostics use this same discrete Hamiltonian. This discretization is separately registered rather than silently replacing Test 6's solver.

The incoming compact packet is `b=A*c*cos^4(pi*(r-c)/(2*width))` for `abs(r-c)<width`, zero elsewhere; c=18, width=3. Its initial dot(b)=+b-prime. Record a(t) on the upstream sphere r=14. A is the radial packet coefficient, not exactly the peak value of a. The counterpropagating control adds an outward packet with c=4, width=2 and dot(b)=-b-prime. It is an explicitly prepared inner shell, not a second distant beam. Sign-reverse both packets together. Initial amplitudes are 0, 0.002, 0.004, 0.008, -0.004, plus +/-0.004 counter controls. Neutral shapes and momenta are fixed for each grid before prediction.

Evolve to t=100, h=0.1, dt=0.02, R=80. Independently halve h (dt=0.01), halve dt at fixed h, and double R. No sponge is used in this short window; outer reflections cannot reach the receiver during it. Save local samples every 0.1 time units and radial views every 2. No global spectral fit substitutes for local chi.

Positive-going local chi zeros define ticks. Anchor their ordinal labels in the common initial preparation, require equal counts and unique pairing within a quarter nominal period, and record `delta_N=-Omega*(t_pulse-t_no_pulse)/(2*pi)`. This sign convention reports a later tick as a negative clock advance. Predict the same root shifts from the saved baseline plus A-squared tangent trace. This is an ideal local probe in the fixed flat rest frame. It is not yet the coordinate-invariant emission/reception marker protocol of Tests 7 and 9.

All thresholds, missing-data rules, numerical error estimates, figure questions and resource ceilings are in the locked plans. A technical run may fail scientifically. In particular, unresolved local signal or tick pairing cannot be promoted using a large global projection. No action, threshold or profile is adjusted after seeing receiver data.
