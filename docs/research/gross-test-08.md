# Test 8: spatial foundation and acceptance dependency

This protocol implements the first spatial prerequisite of [issue #82](https://github.com/Brain-Crumbs/Signal-Space/issues/82). It is **not** the full exchange experiment. The full `gross.two-object-exchange.v1` registration and held-out matrix remain pending. The separate pilot ID is `gross.two-object-calibration.v1`; the model ID is `signal-space.ss-ocf-1.flat-axisymmetric-neutral-clock.v1`.

## Action and numerical mapping

Program v0.2 §§7–10 and 15.8 give the flat action and its equations. The model uses (c=\hbar=m=1), metric (+---), (s=|\phi|^2), (U=s-s^2+s^3), (Z=1+0.2s), (V_\chi=0.25-0.4s+0.2s^2), and (\zeta=0.1). The exact fixed-internal-direction reduction is (\Phi=(\phi,0)). No source term, center force, evolution-time drive or gravitational dynamics is introduced.

For the neutral field the canonical momentum is (\pi_a=Z\dot a). At cell (i), the discrete Hamiltonian is

```math
H=\sum_i V_i\left[|\Pi_i|^2+U(s_i)+\tfrac12 p_{\chi i}^2+\tfrac12V_\chi(s_i)\chi_i^2+\tfrac\zeta4\chi_i^4+\tfrac{\pi_{a i}^2}{2Z(s_i)}\right]
+\sum_{\langle ij\rangle}\frac{A_{ij}}{\ell_{ij}}\left[|\phi_j-\phi_i|^2+\tfrac12(\chi_j-\chi_i)^2+\tfrac12Z_{ij}(a_j-a_i)^2\right].
```

(V_i=2\pi\rho_i h^2) is an annular cell volume, (A_{ij}) a physical face area, (\ell_{ij}=h) the center distance, and (Z_{ij}=[Z(s_i)+Z(s_j)]/2). The radial face area is (2\pi\rho_{i+1/2}h), the axial face area (2\pi\rho_i h); the axis has zero area. Face antisymmetry implements the regular axis and mirror outer faces. The variational derivative gives the reciprocal (+0.1[(\pi_a/Z)^2-|\nabla a|^2_{\mathrm{face}}]\phi) backreaction in (\ddot\phi), with the face-gradient square defined by the same discrete Hamiltonian. Its sign and coefficient are checked by a numerical Hamiltonian derivative independent of the RHS expression. The neutral update is (\dot a=\pi_a/Z), (\dot\pi_a=\operatorname{div}(Z_{\mathrm{face}}\nabla a)). The fixed-direction charge is (Q=\sum_i V_i[-2\operatorname{Im}(\phi_i^*\Pi_i)]). No absorber or flux through the mirror box is included.

This mirror box can constrain spatial embedding, discretization and short conservative evolution. It is **not** an outgoing-boundary exchange solver. The spatial grid is calibrated from the byte-locked Test 6 (\omega_Q=0.900) profile and (\Omega_\chi=0.41274991) eigenmode, with local peak (\chi=10^{-3}). The 99.9% charge and mode radii are approximately 15.3 and 17.8. The pilot freezes separation (d=72>4(17.8)=71.2), zero relative core/clock phase, and compares isolated cores against naive pair superposition. This pair has not been relaxed. Boundary, timestep and initial-data errors require independent controls before it can be adopted as a quiet baseline.

## Stage decisions

The locked [pilot plan](plans/gross-test-08-calibration.json) asks whether the new spatial implementation reproduces regular-axis equations, the exact zero-neutral sector, and short energy/charge ledgers on two meshes. A resolved failure blocks the next stage. Even a pass of these numerical checks leaves 100-period isolated usability, joint relaxation, source-only feasibility, both channels, recoil closure, full control matrix, 20-period postinteraction survival, and Test 9 reconstruction unassessed. Issue #82's G0–G9 cannot be promoted from these pilot checks. The local field samples at (\rho=h/2) are diagnostics, not a physical record at (\rho=0).

For full acceptance, design an outgoing or large-domain control with measured face stress/charge fluxes; isolate the localized mode and define moving worldtubes, timelike velocities, local proper-time marker events and independent momentum accounts. Estimate the 100-period spatial resources before locking a full comparison. Fix all acceptance thresholds before inspecting the held-out receiver runs.
