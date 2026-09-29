# T08 Setup A diagnostics

Setup A implements the isolated and boundary-driven response protocols from
Paper I §11.2. It is a deterministic envelope diagnostic layer over the
shared `EnvelopeSolver`; it does not duplicate the equations in a script or in
the UI.

## Protocols and variants

`packages/experiments/src/setup-a.ts` exposes saved, typed presets for:

- isolated B;
- equal constant left/right rates;
- unequal port rates with a fixed time-dependent sum;
- periodic piecewise-constant rates;
- finite pulses with phase and amplitude;
- equal-integrated-input sequences with early versus late temporal ordering.

Every protocol can be paired with R0, R1 positive/negative gain, and R2
positive/negative gain. `createSetupADefinition` produces the ordinary T07
experiment-definition format, so CLI and browser consumers resolve the same
canonical manifest. `createSetupASmokeDefinitions` supplies inexpensive
schema-validated definitions for protocol wiring checks.

## Saved diagnostics

`runSetupA` returns the complete trajectory and records unwrapped phase
displacement from the no-input continuation, frequency and target-frequency
relaxation, physical bound margin, input integrals, tick crossings, and
out-of-window next-tick status. It also records an exponential-kernel response
for the declared input schedule. This filter is explicitly diagnostic-only: it
does not change the deterministic envelope feedback law. Physical event
filters and arrivals remain in the packet engine.

`createSetupAResponseCurve` saves pulse phase, amplitude, integral, phase
displacement, terminal frequency, bounds, filter peak, and tick status. The
dataset marks scientific interpretation as deferred; these smoke trajectories
are not a response-curve finding.

## Scope and units

Times are seconds, rates are s^-1, and phases are radians. Rates are
nonnegative prescribed inputs. “Periodic” is an explicit piecewise schedule,
not an inferred smooth forcing. Pulse phase is the initial clock phase mapped
to a start time using the initial angular frequency. Publication-scale scans,
regime classification, and conclusions remain outside T08.
