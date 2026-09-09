# T03 deterministic envelopes

Implements Paper I §§3.1–3.5, equations (8)–(13), as transcribed in parent #1; closes task #4. This is a numerical capability and small validation suite, not an executed A–I experiment or a paper finding.

## Use the shared engine

```ts
import { execute } from '@signal-space/sim';

for await (const event of execute({
  runId: 'pair-envelope',
  mode: 'envelope',
  scenario,
  until: 5, // s, absolute aligned simulator time
  envelope: { preparation: 'established', tickSection: 0 },
})) {
  // envelope-sample: states, emissions, integrals, receptions and tick crossings
  // envelope-snapshot: complete restart state on completion or cancellation
  // failed: structured error; completed: successful terminal event
}
```

The CLI accepts `--until seconds`: `node apps/cli/dist/index.js --sample pair --until 1`. Without it, `inspect` retains its t=0-only meaning. The production Web Worker accepts the same request. Interactive solver controls remain T17; this change does not add a second engine to the UI.

## Numerical contract

- Method of steps: each trial is at most the smallest positive link delay and `scenario.solver.step` (default 0.01 s). Delayed sources come only from retained history, never a future stage or integer index shift.
- `method: 'rk4'` uses classical RK4 step doubling. Accepted solutions use two half steps without extrapolation. The estimated local error is the full/half difference divided by 15. Each retained half-step cubic Hermite interpolant is additionally checked at its midpoint against a new RK4 calculation. Both checks use `absoluteTolerance + relativeTolerance * abs(component)` for phase, frequency and each integrated directional intensity. Tolerances must be finite and strictly positive; they are local component error controls, not certified global error bounds.
- Cubic Hermite history stores endpoint values and derivatives for `[phi, omega, integratedLeft, integratedRight]` per node in scenario order. Integrals start at zero. Unwrapped phase and accumulated emission intensity are preserved. E1 integrates to `q * deltaPhi / (2*pi)`; this is intensity, not a random event count.
- Accepted history is checked for finite values, positive and bounded frequency throughout its interpolant, monotone phase and nondecreasing integrated intensities. Rejected trials shrink the step. No phase/frequency clipping occurs. Step underflow, unrepresentable tick indices, overflow and exhausted attempt budgets produce `NUMERICAL_FAILURE`. The default lifetime budget is 100,000 accepted plus rejected steps, configurable through `maxSteps` up to 1,000,000.
- Ticks obey `(t0,t]` and the supplied section (default 0 rad). Each monotone phase cubic is searched by 52 bisection iterations; root accuracy is limited by floating-point resolution and trajectory error. At most 10,000 crossings per node per half step are emitted. Huge unwrapped phases that lose usable tick indices fail explicitly.
- Source startup, driven-input changes, gain interventions and explicit-history knots propagate through four transport generations as exact step endpoints (including empty-link first arrivals). RK endpoint derivatives use the left limit; the next step and reported sample use the right limit. Endpoint arithmetic within eight machine epsilons is aligned to avoid artificial vanishing final steps. Each feedback integration raises differentiability by one; later generations are handled by adaptive error control. More than 1,000,000 scheduled boundary entries fail explicitly.

## Preparation and supported interventions

The default established preparation uses the scenario's constant admissible frequency and linear phase over its declared history interval. `envelope.prehistory` optionally supplies strictly increasing `{time, nodes: {id: {phi, omega}}}` knots covering that interval through zero. They define a cubic Hermite **phase function**, with frequency given by its derivative. Its endpoint must match the scenario and its entire derivative must lie in the admissible frequency interval. Sampling a history function into this data format keeps requests and checkpoints structured-cloneable; executable callbacks are not accepted.

`preparation: 'empty-links'` suppresses every pre-zero source emission on transport links. Clocks still have their declared phase history. Source emissions beginning at zero first arrive at the positive link delay; driven exterior ports are unaffected. Established and empty links are separate preparations.

Open external ports receive zero and outward emission escapes. A driven port can override its constant rate with `boundaryInputs.left` or `.right`: a nonempty array of `{time, rate}`, beginning at zero, strictly increasing in time, finite and nonnegative. The last rate persists. This is a piecewise constant external input, not a new autonomous clock.

T03 supports `change-parameter` interventions with a declared node target and `value: {gain: number}`. They preserve phase and frequency, change only future response, and retain `|gain| < omega0` (R0 still requires zero). Equal-time changes apply in supplied order. After reducing the target interval, an existing frequency may lie outside that new interval during relaxation: diagnostics use the invariant envelope spanning the initial state and all target intervals reached so far. Other parameter changes and event interventions fail explicitly; event pulses/filters belong to T04–T05.

Mirror and periodic boundaries fail explicitly pending T13. `envelopeRoutes` exposes detached positive-delay link descriptors as the transport seam for those later adapters. Event packet inventories, pending responses and nonzero filters are rejected in envelope mode; they are not silently ignored or evolved by the wrong model. The unused initial RNG metadata is retained in the scenario.

## Records and restart

`envelope-sample` is **simulator truth** at t=0/resume and each accepted step. Per clock it reports phase (rad), angular frequency (rad s^-1), outgoing/incoming directional rates (s^-1), integrated intensities (counts), ticks (integer), and invariant frequency-bound margin (rad s^-1). Retarded entries include the link ID, source time, phase, frequency and delivered rate. These private labels/phases are not exposed as observer records; observation schedules, detector latency and inference remain later tasks.

`envelope-snapshot` has the version `envelope-rk4-v1`, original scenario/options, time, complete dense history, the accepted/rejected adaptive-attempt trace, current state, proposed next step and counters. All history is retained in this first implementation, covering at least the maximum delay; memory is O(nodes * accepted steps + rejected steps). History pruning and file-bundle provenance remain later tasks. Snapshots are detached copies.

To resume, pass the same scenario and envelope options with `resume: snapshot` and an absolute `until >= snapshot.time`. Scenario/options are compared independent of object key order. The snapshot records every accepted and rejected adaptive attempt. Restore deterministically replays that trace, including each controller outcome and the exact resulting next-step proposal; checks finite dimensions, uninterrupted history from zero, admissible interpolants, endpoint/state agreement, exact RK4 half-step state and derivative reproduction, coarse-versus-half-step and dense-midpoint acceptance, the solver-boundary partition, and accepted-plus-rejected counters against the lifetime attempt budget. Deleting history, changing parameters or accumulated intensities, cumulatively perturbing otherwise sub-threshold increments, forging rejection counters, substituting tolerance-rejected RK4 steps, crossing a scheduled discontinuity, inserting a solver-inaccessible step-size jump, or exceeding the declared attempt budget does not produce a valid restart. Declared future gain/input changes are already retained in the scenario/options.

Cooperative cancellation yields a snapshot at the last accepted step and then `cancelled`; rejected trials enter the controller trace but never the dense causal history. The worker task queue is serviced every 32 attempts. A cancellation checkpoint resumes the same integration state; stopping at an arbitrary requested time can split a step and change the adaptive mesh, so numerical equality within declared error controls is the contract, not universal bitwise equality. Node and Chromium transcendental functions can also differ in their last bits; the browser parity control compares all numeric fields to 12 decimal places and requires identical event structure.

## Validation and limits

`test/envelope.test.ts` checks analytic R0 and constant-input R1 (both gain signs), nonnegative emissions, E1 intensity per cycle, non-grid causal startup, RK refinement against independent nonlinear convolution, history restart and corruption rejection, R2 reflection, piecewise forcing/gain changes, explicit-history consistency, structured failure and worker cancellation. CLI parity and a production Chromium worker test verify the shared path.

These small controls establish implementation behavior. Long-time convergence, delayed-network regime classification, stochastic means, publication scans, prescribed motion, binding and conservation claims remain outside T03.
