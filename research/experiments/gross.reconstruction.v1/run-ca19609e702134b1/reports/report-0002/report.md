# Test 7: bounded reconstruction and event timing

Run run-ca19609e702134b1; analysis analysis-0001-a8cc0c93; classification fail.
No nonlinear receiver or new clock-phase forecast was executed. Original Test 7 remains failed and Test 8 remains blocked.

causal-capture: pass
causal-timing: unresolved
continuum-events: unresolved
decomposition: pass
inverse-observability: fail
prediction-first: pass
sampling: unresolved
source-energy: pass
surface-replay: pass
broad first: causal error 6.205580e-08; budget 2.981606e-06; target 1.0e-04 inverse-mass units.
broad last: causal error 7.064919e+00; budget 3.197129e+00; target 1.0e-04 inverse-mass units.
carrier first: causal error 1.197330e-07; budget 4.281598e-06; target 1.0e-04 inverse-mass units.
carrier last: causal error 4.009644e+00; budget 5.390440e+00; target 1.0e-04 inverse-mass units.
new first: causal error 1.762566e-08; budget 3.751641e-07; target 1.0e-04 inverse-mass units.
new last: causal error 7.332622e+00; budget 3.211918e+00; target 1.0e-04 inverse-mass units.

local-reconstruction
Question: How do the inverse and causal surface capture reproduce the local waveform and its late tail?
Reading: The main pulses overlap closely. Near the source last event, the inverse has a small ripple while finite causal capture has rapid ringing. Its last event moves by 4.01 to 7.33 time units on the finest grid.
Significance: A close overall waveform can still produce a sensitive late threshold time.
Limitation: Causal capture uses an extra neighboring surface site. The known-source curve is a downstream audit; no nonlinear clock is evolved.

singular-observability
Question: Which surface singular directions remain relevant to each local event?
Reading: The inverse retains 451 of 641 directions. Discarded directions have almost no first-event coefficient, while substantial last-event coefficients persist beyond the cutoff. Surface-consistent finite witnesses move the last event by over 11 time units.
Significance: Observability depends on interior sensitivity as well as the size of the surface singular value.
Limitation: The norm radii and surface tolerance are declared conditional assumptions; root linearization is checked with finite witnesses but is not a global event theorem.

event-budgets
Question: Are first and last reconstruction errors separately below their uncertainty budgets?
Reading: All three causal first events meet the 1e-4 target and their separate budgets. Every last-event budget exceeds that target; inverse last-event errors are 1.49e-3 to 3.51e-3.
Significance: Tests a strict reconstruction prerequisite with target 1e-4 time units, preserving the original Test 7 thresholds.
Limitation: Budgets are direct difference estimates. They measure reconstruction residuals; absolute continuum event shifts and nonlinear phase acceptance are separate.

sampling-continuum
Question: How much do sampling and mesh changes move each event?
Reading: First-event mesh shifts remain 0.043 to 0.081 despite excellent same-mesh reconstruction. Last-event convergence is uneven; the broad causal last event moves 0.209 under output decimation.
Significance: Separates absolute event convergence from agreement between source and reconstruction on one grid.
Limitation: The h=0.0125 source is not an exact continuum reference. Surface-sampling and independent time/domain components are also retained in the saved budgets.
