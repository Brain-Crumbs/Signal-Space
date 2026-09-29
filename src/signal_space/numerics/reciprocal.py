"""Bounded causal circuit; all physical updates use three local participants."""

import os
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp

from signal_space.models.reciprocal import rhs, exact_gate
from signal_space.models.operators import su2
from signal_space.runtime.events import append_event
from signal_space.runtime.io import read_json, write_json

# Wave wires 0..7 and memory wires 8..11. The last branch stays disconnected.
EVENTS = np.array([[0, 1, 8], [2, 3, 9], [4, 5, 10], [6, 7, 11],
                   [1, 2, 8], [3, 4, 9], [0, 5, 10], [6, 7, 11],
                   [0, 3, 8], [2, 5, 9], [1, 4, 10], [6, 7, 11]])
SCHEDULE = list(range(12))
ALTERNATE = [3, 2, 1, 0, 7, 6, 5, 4, 11, 10, 9, 8]
TIMES = np.linspace(0, 1, 9)


def gate(state, parameters, lam, refinement=1, frozen=False, sample=False):
    result = solve_ivp(rhs, (0, 1), state.ravel(), args=(parameters["kappa"], lam, frozen),
                       method="DOP853", rtol=parameters["rtol"] / refinement,
                       atol=parameters["atol"] / refinement, max_step=0.125,
                       t_eval=TIMES if sample else [1.0])
    if not result.success or not np.all(np.isfinite(result.y)):
        raise ValueError(f"gate integration failed: {result.message}")
    return result.y.T.reshape(-1, 3, 2)


def circuit(initial, parameters, lam, schedule=SCHEDULE, refinement=1, frames=None, exact=False):
    state = initial.copy()
    wire_frames = np.repeat(np.eye(2, dtype=complex)[None], 12, axis=0)
    records = np.zeros((12, 3, 2), complex)
    # Records indexed by event identity, independent of the topological schedule.
    trajectories = np.zeros((12, len(TIMES), 3, 2), complex)
    inputs = np.zeros((12, 3, 2), complex)
    for event in schedule:
        wires = EVENTS[event]
        v = np.eye(2) if frames is None else frames[event]
        # Transport every incoming wire from its previous event frame to this one.
        local = np.array([v @ wire_frames[w].conj().T @ state[w] for w in wires])
        inputs[event] = np.array([v.conj().T @ z for z in local])
        flow = np.array([exact_gate(local, parameters["kappa"], lam, t) for t in TIMES]) if exact else gate(local, parameters, lam, refinement, sample=True)
        trajectories[event] = np.einsum("ab,tjb->tja", v.conj().T, flow)
        records[event] = trajectories[event, -1]
        state[wires] = flow[-1]
        wire_frames[wires] = v
    final = np.array([wire_frames[w].conj().T @ state[w] for w in range(12)])
    return final, inputs, trajectories, records


def dependencies():
    """Boolean structural support from incidence alone, not numerical responses."""
    ancestors = np.eye(12, dtype=bool)
    mask = []
    for wires in EVENTS:
        inherited = np.any(ancestors[wires], axis=0)
        mask.append(inherited.copy())
        ancestors[wires] = inherited
    return np.array(mask)


def directions(initial):
    result, owners = [], []
    for wire in range(12):
        if wire < 8:
            vectors = [np.array([1, 0]), np.array([1j, 0]), np.array([0, 1]), np.array([0, 1j])]
        else:
            w = initial[wire]
            v = np.array([-w[1].conj(), w[0].conj()])
            vectors = [v, 1j * v]  # physical tangent plane of normalized memory ray
        for v in vectors:
            delta = np.zeros_like(initial)
            delta[wire] = v
            result.append(delta)
            owners.append(wire)
    return np.array(result), np.array(owners)


def execute(request_path):
    request = read_json(request_path)
    if request.get("resume_checkpoint"):
        raise ValueError("short circuit audit has no resume capability")
    attempt = Path(request["attempt_path"])
    raw, events = attempt / "raw", attempt / "events.jsonl"
    raw.mkdir(parents=True, exist_ok=True)
    p = request["config"]["parameters"]
    rng = np.random.Generator(np.random.PCG64(request["seed_ledger"]["initialization"]))
    write_json(raw / "rng-start.json", rng.bit_generator.state)
    append_event(events, "worker-started", "run", {"pid": os.getpid(), "algorithm": "DOP853-circuit-v1"})

    def cancelled():
        if (attempt / "cancel.request").exists():
            append_event(events, "cancellation-observed", "run", {})
            return True
        return False

    for sample in range(p["samples"]):
        if cancelled():
            return 130
        initial = rng.normal(size=(12, 2)) + 1j * rng.normal(size=(12, 2))
        initial /= np.linalg.norm(initial, axis=1)[:, None]
        initial[:8] *= rng.uniform(0.35, 0.85, size=(8, 1))
        frames = np.array([su2(rng) * np.exp(1j * rng.uniform(-np.pi, np.pi)) for _ in EVENTS])
        for lam in p["lambdas"]:
            arrays = {"initial": initial, "frames": frames, "events": EVENTS, "times": TIMES}
            for label, kwargs in (("base", {}), ("fine", {"refinement": 2}),
                                  ("permuted", {"schedule": ALTERNATE}),
                                  ("framed", {"frames": frames}), ("exact", {"exact": True})):
                final, inputs, flow, records = circuit(initial, p, lam, **kwargs)
                arrays.update({f"{label}_final": final, f"{label}_inputs": inputs,
                               f"{label}_flow": flow, f"{label}_records": records})
            # Ordered shared-memory control: two otherwise disjoint wave pairs.
            for label, order in (("ordered", [0, 1]), ("reversed", [1, 0])):
                state = initial.copy()
                for event in order:
                    wires = [2 * event, 2 * event + 1, 8]
                    state[wires] = gate(state[wires], p, lam, refinement=2)[-1]
                arrays[label] = state
            local = initial[EVENTS[0]]
            arrays["frozen_flow"] = gate(local, p, lam, refinement=2, frozen=True, sample=True)
            np.savez_compressed(raw / f"sample-{sample:02d}-lambda-{lam:g}.npz", **arrays)
            # Full local-record Jacobian for one preregistered preparation at both lambdas.
            if sample == 0:
                delta, owners = directions(initial)
                perturbed = np.empty((2, len(delta), 2, 12, 3, 2), complex)
                for hindex, epsilon in enumerate(p["jacobian_steps"]):
                    for index, tangent in enumerate(delta):
                        if cancelled():
                            return 130
                        for sign_index, sign in enumerate((-1, 1)):
                            changed = initial + sign * epsilon * tangent
                            changed[8:] /= np.linalg.norm(changed[8:], axis=1)[:, None]
                            perturbed[hindex, index, sign_index] = circuit(changed, p, lam, refinement=2)[-1]
                np.savez_compressed(raw / f"jacobian-lambda-{lam:g}.npz", records=perturbed,
                                    directions=delta, owners=owners, ancestor_mask=dependencies())
            append_event(events, "circuit-completed", "run", {"sample": sample, "lambda": lam})
    write_json(raw / "rng-end.json", rng.bit_generator.state)
    write_json(raw / "execution.json", {"samples": p["samples"], "events": EVENTS.tolist(),
               "schedule": SCHEDULE, "alternate_schedule": ALTERNATE, "seed_ledger": request["seed_ledger"],
               "algorithm": "DOP853", "max_step": 0.125, "gate_interval": [0, 1],
               "thread_environment": {k: os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")}})
    append_event(events, "worker-completed", "run", {"circuits": 2 * p["samples"]})
    return 0
