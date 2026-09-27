# Test 7: causal exterior memory and prospective event prerequisite

Issue #80 follows #77. Registered experiment `gross.boundary-memory.v1` retains the frozen SS OCF 1 neutral action and profiles. This is a linear prerequisite. Full Test 7 acceptance additionally requires a fresh nonlinear phase forecast and all Program v0.2 section 15.7 controls.

## Derivation

Let $b=ra$ be the radial neutral field, with neutral amplitude $a$ and radius $r$. The frozen equation is $M\ddot b=-Kb$. $M$ is the positive diagonal inertia and $K$ is the symmetric nearest-neighbor stiffness obtained from the registered radial Hamiltonian. Natural units are $c=\hbar=m=1$.

Partition the nodes at recording radius 14 into interior $x$ and exterior $y$. The two interface nodes are measured. With subscripts denoting matrix blocks,

$$
M_I\ddot x+K_{II}x+K_{IE}y=0,
\qquad
M_E\ddot y+K_{EE}y+K_{EI}x=0.
$$

Define $A_E=M_E^{-1}K_{EE}$ and $G_E(t)=A_E^{-1/2}\sin(A_E^{1/2}t)$. The exact exterior solution is

$$
y(t)=y_{\rm free}(t)-\int_0^t G_E(t-s)M_E^{-1}K_{EI}x(s)\,ds.
$$

The free term depends on exterior initial conditions. The convolution is the exterior response to earlier interior motion. Discarding either term is an approximation. A boundary memory kernel alone cannot recover an unknown free input.

Only the measured surface value of $x$ enters $K_{EI}x$. Evolve an auxiliary exterior state $s$ from zero with $M_E\ddot s+K_{EE}s=-K_{EI}x_{\rm measured}$. Then the measured adjacent exterior node supplies $y_{\rm free}=y_{\rm measured}-s$ at the interface. This de-embedding is causal and receives no interior history beyond the surface node and no source initial data.

The predictor starts from zero and evolves $z=(x,\widetilde y)$ with the full frozen operator and forcing $-K_{IE}y_{\rm free}$ only at the interior interface node. The auxiliary exterior $\widetilde y$ is retained. It realizes the memory integral exactly in space without a dense convolution or an initial-state inverse. The true field inside equals the predictor when the source initially lies outside the interface. The source wave is used only for synthetic acquisition and a later independent local audit.

## Explicit protocol change

The primary predictor uses the two-site synthetic surface record through time 60, acquired before replay. It evaluates this record only at its current integration time. This is more information than the preceding record ending at 16; it is not a claim of a complete forecast from that shorter record. A simultaneous control cuts only the recovered incoming drive at 16 while retaining exterior memory. A second control discards exterior memory while retaining complete incoming drive.

Primary local events are the first rise of $|a|$ through $10^{-4}$ and its first subsequent fall. This first complete excursion can be selected prospectively from a local trace. The historical first-rise/last-fall events remain separate diagnostics. No historical result or threshold is relabeled. The new event choice must later demonstrate a resolved nonlinear clock interval; a linear pass cannot establish that.

## Locked calculation

Reuse the hashed independent profiles at spacings 0.05, 0.025 and 0.0125. Domain radius is 80, with a radius-100 control at spacing 0.025. Time step is 0.0025, with an independent 0.00125 control on the finest grid. Record every 0.0125 through 60. Independently decimate surface and local output records to 0.025. Probe radius is 0.1 and amplitude is 0.012. The broad, carrier and third waveform from the prior linear audit are reused as diagnostics of the new method; none is presented as a fresh nonlinear forecast.

Each variant locks surface and prediction hashes before its known-source local audit. The source acquisition and predictor share the same spatial operator; source local integration is repeated only after the forecast lock. Independent dense-matrix and causal-prefix unit controls validate the interface implementation before execution. No receiver calibration or response coefficient is fitted.

## Gates

- Every frozen input and prediction hash verifies and prediction precedes local audit.
- Every complete-acquisition relative local waveform error is at most $10^{-5}$.
- Frozen unforced source energy drift is at most $10^{-6}$ over the full interval.
- For each primary event and spectrum on the finest grid, residual and residual budget are at most $10^{-4}$; residual must also lie within that budget. The budget is the sum of changes in residual under mesh, time and domain controls, source/predictor output sampling, surface sampling, and a $10^{-7}$ floor. No fitted Richardson factor is used. Missing events or an excessive budget are unresolved; a resolved excess residual fails.
- For source and complete prediction separately, the last absolute event mesh change is at most 0.6 of the previous change plus nonspatial differences, and mesh plus nonspatial uncertainty is at most 0.1. Failure to resolve this is unresolved. This does not assert absolute continuum precision of $10^{-4}$.
- Each primary finest event changes at most $10^{-4}$ under surface or output decimation; otherwise unresolved.

The cutoff-16 and no-memory controls, and all retrospective last-event results, are retained even if adverse. They cannot substitute for the complete-input primary gates. A prerequisite failure or unresolved result stops the dependent nonlinear acceptance stage. A pass permits a separately locked fresh nonlinear protocol; it does not itself pass Test 7 or open Test 8.

## Resource and visual plan

Bound: 3,600 CPU seconds, 4,000 wall seconds, 1,024 MiB memory and 150 MiB output. Fifteen linear cases, three replay methods and a separate surface-decimation control are included. No nonlinear receiver is evolved here.

Four figures show local waveform and event neighborhoods, the measured/free/exterior-response boundary decomposition, separate event error budgets, and absolute event convergence versus acquisition and output sampling. Exact displayed data and four-part interpretations accompany the standard evidence and reader packages. Raw data and figures remain outside Git.
