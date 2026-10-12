"""Reusable serial ordered-word and independent coherent-operator integrations."""
import os
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp

from signal_space.models.linked_memory import (EVENTS, CONTROL_WORDS, ROTATION, COMMON_PHASE,
    preparations, gate, lift, operator_rhs, tangent_basis, gate_tangent,
    physical_features, feature_tangent, record_tangent, records, retract)
from signal_space.runtime.events import append_event
from signal_space.runtime.io import read_json, write_json


class PartialTraceError(RuntimeError):
    def __init__(self, message, arrays):
        super().__init__(message)
        self.arrays = arrays


def trace(initial, parameters, cycles, order=(0, 1), operator=False,
          refinement=1, frozen=False, cancelled=lambda: False):
    samples = parameters["samples_per_gate"] if refinement == 1 else parameters["refined_samples_per_gate"]
    times = np.linspace(0, 1, samples)
    total = cycles * len(order)
    if operator:
        w, p = lift(initial)
        current = np.concatenate((w.ravel(), p.ravel()))
        flows = np.empty((total, samples, 44), complex)
    else:
        current = initial.copy()
        flows = np.empty((total, samples, 5, 2), complex)
    identities = np.tile(order, cycles)
    completed = 0
    try:
        for index, event in enumerate(identities):
            if cancelled():
                raise RuntimeError("linked-memory cancellation observed")
            if operator:
                solved = solve_ivp(operator_rhs, (0, 1), current,
                    args=(int(event), parameters["kappa"], frozen), method="DOP853",
                    rtol=parameters["rtol"] / refinement, atol=parameters["atol"] / refinement,
                    max_step=parameters["max_step"], t_eval=times)
                if not solved.success or not np.all(np.isfinite(solved.y)):
                    raise ValueError(f"coherent-operator integration failed: {solved.message}")
                flows[index] = solved.y.T
            else:
                flows[index] = [gate(current, int(event), parameters["kappa"], s, frozen) for s in times]
            current = flows[index, -1].copy()
            completed += 1
    except Exception as error:
        raise PartialTraceError(str(error), {"flow": flows[:completed], "state": current,
            "events": identities[:completed], "times": times}) from error
    return {"flow": flows, "final": current, "events": identities, "times": times}


def endpoint_history(initial, parameters, cycles):
    state, output = initial.copy(), []
    for _ in range(cycles):
        for event in (0, 1):
            state = gate(state, event, parameters["kappa"])
            output.append(state)
    return np.array(output)


def sensitivity(initial, parameters, cancelled=lambda: False):
    count = parameters["sensitivity_cycles"]
    basis = tangent_basis(initial)
    state, delta = initial.copy(), basis.copy()
    base, tangent, derivatives = [], [], []
    for _ in range(count):
        for event in (0, 1):
            if cancelled(): raise PartialTraceError("sensitivity cancellation observed",{
                "base":np.array(base),"tangent":np.array(tangent),"record_derivatives":np.array(derivatives),
                "state":state,"delta":delta,"directions":basis})
            state, delta = gate_tangent(state, delta, event, parameters["kappa"])
            base.append(state.copy())
            tangent.append(feature_tangent(state, delta))
            derivatives.append(record_tangent(state, delta, event))
    finite = np.zeros((2, 2 * count, 28, 16))
    record_errors = np.zeros((2 * count, 16, 2, 3))
    initial_errors = np.zeros((16, 2))
    finite_states=np.zeros((2,16,2,2*count,5,2),complex)
    finite_initials=np.zeros((2,16,2,5,2),complex)
    perturbed_states=np.zeros((16,2,2*count,5,2),complex)
    perturbed_initials=np.zeros((16,2,5,2),complex)
    finite_completed=np.zeros((2,16),bool)
    perturbations_completed=np.zeros((16,2),bool)
    for dindex, direction in enumerate(basis):
        for signindex, sign in enumerate((-1, 1)):
            if cancelled(): raise PartialTraceError("sensitivity cancellation observed",{
                "base":np.array(base),"tangent":np.array(tangent),"record_derivatives":np.array(derivatives),
                "state":state,"delta":delta,"directions":basis,"finite_differences":finite,
                "finite_completed":finite_completed,"record_errors":record_errors,
                "perturbations_completed":perturbations_completed,"initial_errors":initial_errors,
                "finite_states":finite_states,"finite_initials":finite_initials,
                "perturbed_states":perturbed_states,"perturbed_initials":perturbed_initials})
            small = retract(initial, sign * parameters["initial_error"] * direction)
            initial_errors[dindex, signindex] = np.linalg.norm(small - initial)
            history = endpoint_history(small, parameters, count)
            perturbed_states[dindex,signindex]=history
            perturbed_initials[dindex,signindex]=small
            for n, changed in enumerate(history):
                event = n % 2
                record_errors[n, dindex, signindex] = records(changed, event) - records(base[n], event)
            perturbations_completed[dindex,signindex]=True
        for hindex, epsilon in enumerate(parameters["jacobian_steps"]):
            prepared=[retract(initial,sign*epsilon*direction) for sign in (-1,1)]
            histories=[endpoint_history(changed,parameters,count) for changed in prepared]
            finite_states[hindex,dindex]=histories
            finite_initials[hindex,dindex]=prepared
            for n in range(2 * count):
                finite[hindex, n, :, dindex] = (physical_features(histories[1][n])
                    - physical_features(histories[0][n])) / (2 * epsilon)
            finite_completed[hindex,dindex]=True
    return {"base": np.array(base), "directions": basis, "tangent": np.array(tangent),
            "record_derivatives": np.array(derivatives), "finite_differences": finite,
            "record_errors": record_errors, "initial_errors": initial_errors,
            "finite_states":finite_states,"finite_initials":finite_initials,
            "perturbed_states":perturbed_states,"perturbed_initials":perturbed_initials}


def execute(request_path):
    request = read_json(request_path)
    if request.get("resume_checkpoint"):
        raise ValueError("linked-memory v1 has no restart protocol")
    attempt = Path(request["attempt_path"])
    raw, events = attempt / "raw", attempt / "events.jsonl"
    raw.mkdir(parents=True, exist_ok=True)
    p = request["config"]["parameters"]
    cancelled = lambda: (attempt / "cancel.request").exists()
    append_event(events, "worker-started", "run", {"algorithm": "exact-word/operator-DOP853-v1", "pid": os.getpid()})
    files = []
    current_label = "not-started"
    try:
        for name, initial in preparations().items():
            for label, kwargs in (("exact", {}), ("operator", {"operator": True}),
                                  ("operator-fine", {"operator": True, "refinement": 2}),
                                  ("exact-fine", {"refinement": 2}),
                                  ("frozen", {"frozen": True}),
                                  *((key, {"order": value}) for key, value in CONTROL_WORDS.items()),
                                  ("rotated", {}), ("common-phase", {})):
                current_label = f"{name}-{label}"
                state = initial.copy()
                if label == "rotated": state = state @ ROTATION.T
                if label == "common-phase": state[:3] *= COMMON_PHASE
                arrays = trace(state, p, p["cycles"], cancelled=cancelled, **kwargs)
                arrays["initial"] = state
                filename = current_label + ".npz"
                np.savez_compressed(raw / filename, **arrays)
                files.append(filename)
                append_event(events, "word-completed", "run", {"preparation": name, "variant": label})
            if name in p["sensitivity_preparations"]:
                current_label = f"{name}-sensitivity"
                arrays = sensitivity(initial, p, cancelled)
                filename = current_label + ".npz"
                np.savez_compressed(raw / filename, **arrays)
                files.append(filename)
        write_json(raw / "execution.json", {"preparations": list(preparations()), "files": files,
            "events": [list(e) for e in EVENTS], "parameters": p, "seed_ledger": request["seed_ledger"],
            "deterministic": True, "threads": {k: os.environ.get(k) for k in
                ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")}})
        append_event(events, "worker-completed", "run", {"preparations": 7})
        return 0
    except Exception as error:
        if isinstance(error, PartialTraceError):
            np.savez_compressed(raw / (current_label + "-partial.npz"), **error.arrays)
        write_json(raw / "incomplete.json", {"completed_files": files, "active": current_label,
            "reason": str(error), "cancelled": cancelled()})
        append_event(events, "worker-incomplete", "run", {"active": current_label, "reason": str(error)})
        if cancelled(): return 130
        raise
