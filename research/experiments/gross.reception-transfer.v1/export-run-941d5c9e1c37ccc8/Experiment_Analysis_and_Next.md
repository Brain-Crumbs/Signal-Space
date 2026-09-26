# Test 7 discrete transfer: reviewed results

**Assessment: the controlled extension across both spectra remains unresolved.** The separately registered recovery run passes all nine locked checks, but the forecast-inclusive diagnostic budget fails to resolve the carrier correction. This is not promotion of Test 7. Original run `run-b1677e67610c5870` remains failed (10/12); Test 8 remains blocked.

Run `run-941d5c9e1c37ccc8`; analysis `analysis-0001-792256a8`. Source commit `13b7d51a33d9ded87eafb6f586960a564c04bb28`. The physical solver completed all sixteen cases. Canonical evidence and the reader export verify. The setup PDF (five pages), results PDF (six pages), and four figures were visually inspected.

## What was predicted

The unchanged SS OCF 1 action and fixed readout calibration are retained. The formal neutral terms are A and A^3; core and clock terms are A^0, A^2 and A^4. The quadrature phase includes Im[z4/z0 - (z2/z0)^2/2]. No response coefficient is fitted. See the [derivation](gross-test-07-order4.md) and [discrete-transfer protocol](gross-test-07-transfer.md), mapped to Operator Program v0.2 §§7–10 and §15.7.

The discrete observation matrix uses both Z-weighted inertia and stiffness and the exact RK4 polynomial. Z cancels from the continuum principal speed; the earlier sqrt(Z) optical delay was not the characteristic law of this action. The inverse estimates initial data from b and b_t at r=14. It assumes support [18,26] and v=D_h b, and acquisition shares its discretization. A small surface replay residual alone therefore cannot establish accurate interior reconstruction.

All sixteen surface/input/profile/response hashes and first/last marker forecasts were locked at 05:22:13.017480 UTC on 2026-09-26, before the first nonlinear receiver at 05:22:13.018357. Prediction-lock SHA-256: `170d49dba81064a2f1cb9b041a0a6659578f0e3d2b340f441a13bf3da7b8580a`. The hosted run repeats histories already inspected during the interrupted local attempt; it is reproducibility evidence, not a new held-out prediction claim.

## Nominal interval discrimination

All values below are cycles, at A=0.012, h=0.0125 and dt=0.0025. The observed interval uses measured markers; forecasts use their locked predicted markers.

| Spectrum | Observed interval | Second-order error | Fourth-order error | Locked budget | Forecast-inclusive audit | Maximum discrimination budget |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| broad | -1.464093e-6 | 3.013161e-8 | 4.059571e-11 | 3.857757e-10 | 6.939473e-10 | 7.522753e-9 |
| carrier | 5.602454e-7 | 2.528696e-8 | 6.491810e-10 | 5.196703e-9 | 1.002800e-8 | 6.484036e-9 |

The registered budget takes receiver changes for mesh, time and domain. The post-lock audit takes the larger receiver or forecast change for each of those terms. It preserves the original classification and exposes a limitation of the locked budget. Broad remains resolved under this audit. Carrier does not: its audit budget is 1.55 times the quarter-order target. A close finest-grid match cannot establish the stronger claim.

For carrier, forecast changes contribute 2.408e-9 cycles from mesh refinement and 3.745e-9 from halving the time step; the output-decimation term is 2.857e-9 and inverse-cutoff sensitivity is 9.971e-10. The actual receiver half-step change is only 1.614e-12. Thus the prediction and reconstruction, rather than receiver evolution alone, need tighter controls. Output at 0.025 was compared with 0.05; interpolation still matters.

### Amplitude and sign diagnostics

| Spectrum | A | Signed residual Y - P2 | Derived correction P4 - P2 | Remaining Y - P4 |
| --- | ---: | ---: | ---: | ---: |
| broad | 0.008 | 3.611502e-9 | 4.171795e-9 | -5.602932e-10 |
| broad | 0.012 | 3.013161e-8 | 3.009101e-8 | 4.059571e-11 |
| carrier | 0.008 | 8.702762e-9 | 8.264885e-9 | 4.378767e-10 |
| carrier | 0.012 | 2.528696e-8 | 2.593614e-8 | -6.491810e-10 |

The unfitted correction has the residual's sign and reduces its magnitude in these four comparisons. Positive and negative nominal amplitudes give identical saved intervals and marker times. The fixed absolute marker threshold moves the endpoints when amplitude changes, so these interval ratios are not a clean A^4 scaling measurement. They must not be presented as a fitted or independently resolved power law; the 0.008 rows are diagnostic, outside the nominal budget gate.

## Marker timing and the located inverse limit

| Spectrum | Locked first marker | Observed first marker | Locked last marker | Observed last marker | Absolute last residual |
| --- | ---: | ---: | ---: | ---: | ---: |
| broad | 18.786813489 | 18.786813489 | 48.524599665 | 48.527194373 | 0.002594708 |
| carrier | 19.482027048 | 19.482027048 | 46.610332679 | 46.609709549 | 0.000623130 |

Times are in inverse mass units. All-case maximum residual is 0.0141202, below the unchanged 0.1 gate. However, the first-marker continuum mesh changes are still 0.0616135 (broad) and 0.0812253 (carrier). These dominate the combined timing budgets 0.0703983 and 0.0832888. Near-roundoff first-marker agreement on the same mesh is not a continuum timing result, and a maximum over both events does not tightly constrain the last event.

Last-marker residuals are nonmonotonic across meshes. Broad changes from 0.00293 at h=0.05 to 0.01412 at h=0.025 and 0.00259 at h=0.0125. These data do not demonstrate a uniformly decreasing approximation residual.

The downstream known-source audit propagates the true and reconstructed inputs through the same frozen linear operator. It never feeds the source shape back into the locked prediction.

| Frozen linear audit | Relative local waveform error | Maximum local field error | Reconstructed minus source last marker |
| --- | ---: | ---: | ---: |
| finest-broad | 2.103243e-6 | 8.938561e-7 | -1.715479e-3 |
| finest-carrier | 6.617038e-7 | 3.210294e-7 | 1.622975e-3 |
| time-carrier | 7.276713e-7 | 4.533110e-7 | -1.100463e-3 |

At the finest mesh the inverse retains rank 449 of 641 input columns, while surface relative replay residuals are 1.91e-13 and 1.26e-13. Weakly observed input components can therefore remain relevant at the interior tail. For carrier, halving dt shifts the known-source linear last marker by only 4.76e-7, but the reconstructed last marker moves by about 0.00272. This locates an inverse/late-marker sensitivity before nonlinear response truncation. It does not prove that all remaining phase error has that origin.

## Independent background and health controls

Independently solved core profiles have maximum discrete residual 2.70e-11, below 2e-10. Clock eigenvalues on h=0.1, 0.05, 0.025, 0.0125 are 0.170362489587, 0.170361642436, 0.170361430789, 0.170361377882; adjacent changes shrink by approximately one quarter. Readout omega_chi=0.41274991 was held fixed. This refines the same branch and does not establish its longevity again.

Using the older interpolated profile changes the nominal interval by about 9.98e-11 cycles (broad) and 7.23e-10 (carrier). Maximum charge drift is 1.38e-12; maximum total-energy residual is 9.65e-9 of incident energy. These controls pass their declared gates.

## Decision and next discriminator

Supported: a conditional local response can be forecast from the synthetic exterior record; the derived fourth-order term improves the interval without fitting, and the broad case resolves the correction under the additional audit. Unresolved: controlled prediction across both spectra, uniformly converged marker timing, and attribution of the remaining tail error to response truncation. This evidence does not yet supply a controlled rejection of the quartic clock response.

The next separately locked calculation should bound interior error from the retained and discarded singular directions, or use a causal discrete boundary transfer that avoids initial-state inversion. Keep the known-source replay only as a downstream diagnostic. Predeclare separate first/last timing budgets, include forecast as well as receiver mesh/time changes, and halve output spacing from 0.025 to 0.0125 in a bounded sampling control. Require the combined carrier interval budget below one quarter of its precomputed order separation before interpreting a residual.

If transfer and sampling controls remove the discrepancy, the extension gains support. If a stable timing or phase residual remains beyond those budgets, reject the stated radial response approximation. An a5 marker correction is a subsequent derivation only after inverse uncertainty is controlled. A fresh prediction claim requires another waveform locked after these method choices; neither inspected history may be relabeled as held out.

No two-object survival/recoil, observer or coordinate invariance, gravity, angular stability, or emergent spacetime has been tested. A successful future discriminator would permit a separate Test 7 acceptance review, never automatic promotion.

## Reproducibility and technical recovery

The original hosted pipeline completed the solver, analysis, report and canonical verification, then failed reader packaging because figure question labels differed from the locked plan. A first import also stopped on an empty Git bundle caused by using an unnamed commit as its positive reference. Both failures are retained in workflow logs. The successful import named the pinned source ref, appended a corrected report, and rebuilt the reader without rerunning physics or analysis. The original report and failed pipeline status remain archived.

See [interruption and recovery](gross-test-07-transfer-interruption.md), [locked protocol](gross-test-07-transfer.md), [canonical manifest](../../research/experiments/gross.reception-transfer.v1/run-941d5c9e1c37ccc8/manifest.json), [reader package](../../research/experiments/gross.reception-transfer.v1/export-run-941d5c9e1c37ccc8/README.md), and [source/recovery provenance](../../research/experiments/gross.reception-transfer.v1/provenance-run-941d5c9e1c37ccc8/).
