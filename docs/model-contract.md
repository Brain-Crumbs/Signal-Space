# Paper I model contract (`paper-i-v1`)

This contract implements the model transcribed in parent issue #1. It is a specification boundary for later solvers, not a claim that an experiment has been run. A material change to an equation or observability rule requires a new `modelVersion`.

## State and units

All serialized physical values use SI: time `s`, position/length `m`, phase `rad`, angular frequency `rad s^-1`, emission/arrival rate and filtered signal density `s^-1`. `c0` is `m s^-1`; amplitude `a`, count-per-cycle `q`, wrapped phase, and `tanh` arguments are dimensionless. Gain `g` and target frequency are `rad s^-1`; relaxation time `Trel`, link delay `tau`, detector latency, and filter width `h` are seconds. `r*` is `s^-1`.

Global simulator time orders integration and delivery but is not node-readable. Centers are finite and strictly ordered. Every directed link has a source and target port consistent with that order, with positive `delay = |xj-xi|/c0`. Open edges discard outward traffic. Mirrors declare positive exterior distance; periodic boundaries declare oriented closure with positive delay.

Phase is stored unwrapped. Display wrapping uses `[-pi, pi)`. The section phase `phi_sec` is protocol data; ticks in `(t0,t]` use `floor((phi(t)-phi_sec)/2pi)-floor((phi(t0)-phi_sec)/2pi)`. Facing/transport offset `chi_ji` is explicit diagnostic configuration, never inferred from a label.

## Equations and variants

Emission is `rho_i^± = nu_i/2 [1 ± a_i cos(phi_i)]`. E0 fixes `nu_i`; E1 uses `nu_i=q_i omega_i/(2pi)`. Feedback is `phi_dot=omega`, `Trel omega_dot=omega_target-omega`, and `omega_target=omega0+g Z(phi)tanh(rSigma/r*)`, where R0 has `g=0`, R1 has `Z=1`, and R2 has `Z=cos(2phi)`. Event filters use `K_h(u)=exp(-u/h)/h` for `u>=0`. Variants (including degree normalization) must receive distinct scenario metadata and must not silently replace these laws.

Required bounds are `c0,Trel,r*,h,omega0>0`, `0<=a<=1`, `|g|<omega0`, and initial `omega` in `omega0 ± |g|`. Prehistory covers `[-tau_max,0]`. Event preparation serializes finite pending packets, nonnegative receiver filters, pending responses, and RNG algorithm/state.

## Information boundary

`PhysicalOutput` may contain packet identities and simulator truth. `ObserverRecord` exposes only fields selected by `ObservationProtocol`: local phase/frequency, reported arrival time, or reported count. It deliberately contains neither packet IDs nor remote/source phase. Detector deletion edits records only. Removing a physical pulse and adding a probe are explicit interventions.

Snapshots include unwrapped phase/frequency, prehistory, filters, pending packets/responses, and RNG state. Current endpoint phases alone are not restartable state. JSON round trips are exact for finite IEEE-754 inputs; numerical tolerances belong to the run manifest.

## Explicit decisions

- The schema uses SI storage; a UI may display scaled units but must convert at its boundary and round-trip them.
- Autonomous emissions never branch on reception. Tagged one-return transponders are a separate protocol.
- No response or inference code may read global time, delayed source phase, private packet ID, or another node's state unless the observation protocol provides a physical measurement.
- `chi`, tick-section choice, E0/E1, R0/R1/R2, preparation, and normalization are declared inputs. There is no implicit synchronization, reset, force, or phase mark.
