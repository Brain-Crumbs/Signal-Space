"""Audit saved circuit states; never integrate the physical model during analysis."""

import numpy as np

from signal_space.numerics.operators import write_rows
from signal_space.runtime.io import read_json, write_json


def outer(z):
    return np.einsum("...a,...b->...ab", z, z.conj())


def ledger(states, kappa, lam):
    """Independent algebra on saved states, including every within-gate sample."""
    z1, z2, w = np.moveaxis(states, -2, 0)
    d = z1 - z2
    n = np.sum(abs(z1) ** 2 + abs(z2) ** 2, axis=-1)
    m = np.sum(abs(w) ** 2, axis=-1)
    charge = outer(z1) + outer(z2) + outer(w)
    energy = kappa * abs(np.sum(w.conj() * d, axis=-1)) ** 2 + lam * n ** 2 / 2
    return n, m, charge, energy


def relative(a, b):
    return float(np.linalg.norm(a - b) / max(1.0, np.linalg.norm(b)))


def overlaps(states):
    a, b, w = np.moveaxis(states, -2, 0)
    result = []
    for x, y in ((a, b), (a, w), (b, w)):
        den = np.sum(abs(x) ** 2, axis=-1) * np.sum(abs(y) ** 2, axis=-1)
        if np.any(den < 1e-20):
            raise ValueError("overlap record is undefined for a zero participant")
        result.append(abs(np.sum(x.conj() * y, axis=-1)) ** 2 / den)
    return np.array(result).T


def analyze(run_path, output, config):
    paths = sorted((run_path / "attempts").glob("*/raw/execution.json"))
    if not paths:
        raise ValueError("no completed circuit measurements")
    raw = paths[-1].parent
    p, criteria = config["parameters"], config["analysis"]
    rows, responses, balance, controls = [], [], [], []
    maxima = {key: 0.0 for key in ("conservation", "projector", "cut_charge", "exact", "refinement", "rescheduling", "frame", "frozen_exact", "jacobian_outside", "jacobian_refinement")}
    minima = {key: float("inf") for key in ("order_signal", "frozen_charge", "memory_response", "jacobian_inside")}
    execution = read_json(raw / "execution.json")
    expected_events = np.array(p["events"])
    if execution["events"] != p["events"] or execution["schedule"] != list(range(12)) or execution["alternate_schedule"] != p["alternate_schedule"]:
        raise ValueError("raw incidence or schedule differs from locked circuit")
    # Reconstruct causal ancestors independently from the locked directed wires.
    sources = [{i} for i in range(12)]
    ancestor_mask = np.zeros((12, 12), bool)
    for event, wires in enumerate(expected_events):
        causal = set().union(*(sources[w] for w in wires))
        ancestor_mask[event, list(causal)] = True
        for w in wires:
            sources[w] = causal.copy()

    def maximum(key, value):
        maxima[key] = max(maxima[key], float(value))

    for sample in range(p["samples"]):
        for lam in p["lambdas"]:
            path = raw / f"sample-{sample:02d}-lambda-{lam:g}.npz"
            with np.load(path, allow_pickle=False) as saved:
                a = dict(saved)
            if any(not np.all(np.isfinite(v)) for v in a.values()) or not np.array_equal(a["events"], expected_events):
                raise ValueError("nonfinite or inconsistent raw circuit states")
            for label in ("base", "fine", "permuted", "framed", "exact"):
                if a[f"{label}_flow"].shape != (12, 9, 3, 2) or a[f"{label}_inputs"].shape != (12, 3, 2) or a[f"{label}_final"].shape != (12, 2):
                    raise ValueError("incomplete circuit coverage")
            initial = a["initial"]
            if initial.shape != (12, 2) or np.max(abs(np.linalg.norm(initial[8:], axis=1) - 1)) > 1e-12 or np.max(np.linalg.norm(initial[:8], axis=1)) > 0.85 + 1e-12:
                raise ValueError("initial state violates locked bounded norm domain")
            for label in ("base", "fine"):
                for event, flow in enumerate(a[f"{label}_flow"]):
                    n, m, j, h = ledger(flow, p["kappa"], lam)
                    residuals = [max(abs(n - n[0])) / max(1, abs(n[0])),
                                 max(abs(m - m[0])) / max(1, abs(m[0])),
                                 max(np.linalg.norm(j - j[0], axis=(-2, -1))) / max(1, np.linalg.norm(j[0])),
                                 max(abs(h - h[0])) / max(1, abs(h[0]))]
                    maximum("conservation", max(residuals))
                    pw = outer(flow[:, 2])
                    maximum("projector", np.max(np.linalg.norm(pw @ pw - pw, axis=(-2, -1))))
                    memory_change = np.linalg.norm(pw[-1] - pw[0])
                    rows.append({"sample": sample, "lambda": lam, "resolution": label, "event": event,
                                 "N_error": residuals[0], "memory_norm_error": residuals[1], "J_error": residuals[2],
                                 "H_error": residuals[3], "memory_change": memory_change})
                maximum("cut_charge", relative(np.sum(outer(a[f"{label}_final"]), axis=0), np.sum(outer(initial), axis=0)))
            maximum("exact", relative(a["base_flow"], a["exact_flow"]))
            maximum("exact", relative(a["fine_flow"], a["exact_flow"]))
            for label, key in (("fine", "refinement"), ("permuted", "rescheduling"), ("framed", "frame")):
                maximum(key, relative(a[f"{label}_flow"], a["base_flow"]))
                maximum(key, np.max(abs(overlaps(a[f"{label}_records"]) - overlaps(a["base_records"]))))
            # Order control must change a ray or an invariant overlap, not merely a phase.
            order_signal = np.linalg.norm(outer(a["ordered"][8]) - outer(a["reversed"][8]))
            minima["order_signal"] = min(minima["order_signal"], float(order_signal))
            frozen = a["frozen_flow"]
            z1, z2, w = initial[expected_events[0]]
            d, total = z1 - z2, z1 + z2
            n0 = np.vdot(z1, z1).real + np.vdot(z2, z2).real
            pj = outer(w)
            frozen_reference = []
            for t in a["times"]:
                phase = np.exp(-1j * lam * n0 * t)
                dt = (np.eye(2) + (np.exp(-2j * p["kappa"] * t) - 1) * pj) @ d
                frozen_reference.append([phase * (total + dt) / 2, phase * (total - dt) / 2, w])
            maximum("frozen_exact", relative(frozen, np.array(frozen_reference)))
            jf = ledger(frozen, p["kappa"], lam)[2]
            minima["frozen_charge"] = min(minima["frozen_charge"], relative(jf[-1], jf[0]))
            reciprocal = a["fine_flow"][0]
            minima["memory_response"] = min(minima["memory_response"], float(np.linalg.norm(outer(reciprocal[-1, 2]) - outer(reciprocal[0, 2]))))
            controls.append({"sample": sample, "lambda": lam, "order_signal": order_signal,
                             "frozen_charge": relative(jf[-1], jf[0]),
                             "memory_response": float(np.linalg.norm(outer(reciprocal[-1, 2]) - outer(reciprocal[0, 2])))})
            if sample == 0:
                for mode, flow in (("reciprocal", reciprocal), ("frozen", frozen)):
                    j = ledger(flow, p["kappa"], lam)[2]
                    wave = outer(flow[:, 0]) + outer(flow[:, 1])
                    memory = outer(flow[:, 2])
                    for ti, t in enumerate(a["times"]):
                        balance.append({"lambda": lam, "mode": mode, "s": t,
                                        "wave_change": float(np.linalg.norm(wave[ti] - wave[0])),
                                        "memory_change": float(np.linalg.norm(memory[ti] - memory[0])),
                                        "wave_z_change": float((wave[ti, 0, 0] - wave[0, 0, 0] - wave[ti, 1, 1] + wave[0, 1, 1]).real),
                                        "memory_z_change": float((memory[ti, 0, 0] - memory[0, 0, 0] - memory[ti, 1, 1] + memory[0, 1, 1]).real),
                                        "total_change": float(np.linalg.norm(j[ti] - j[0]))})
                records = overlaps(a["fine_records"])
                for event in range(12):
                    responses.append({"lambda": lam, "event": event, "port_overlap": records[event, 0],
                                      "port1_memory_overlap": records[event, 1], "port2_memory_overlap": records[event, 2]})

    jacobians = []
    for lam in p["lambdas"]:
        with np.load(raw / f"jacobian-lambda-{lam:g}.npz", allow_pickle=False) as saved:
            records, owners = saved["records"], saved["owners"]
            if records.shape != (2, 40, 2, 12, 3, 2) or owners.tolist() != [w for w in range(12) for _ in range(4 if w < 8 else 2)] or not np.array_equal(saved["ancestor_mask"], ancestor_mask) or not np.all(np.isfinite(records)):
                raise ValueError("incomplete or inconsistent causal Jacobian")
        derivatives = [(records[i, :, 1] - records[i, :, 0]) / (2 * step) for i, step in enumerate(p["jacobian_steps"])]
        maximum("jacobian_refinement", np.max(abs(derivatives[0] - derivatives[1])))
        # Maximum Frobenius response across real/tangent directions owned by each input wire.
        for i, step in enumerate(p["jacobian_steps"]):
            response = np.linalg.norm(derivatives[i], axis=(-2, -1))
            for event in range(12):
                for wire in range(12):
                    value = float(np.max(response[owners == wire, event]))
                    inside = bool(ancestor_mask[event, wire])
                    if not inside:
                        maximum("jacobian_outside", value)
                    jacobians.append({"lambda": lam, "step": step, "event": event, "input_wire": wire,
                                      "ancestor": int(inside), "response": value})
            minima["jacobian_inside"] = min(minima["jacobian_inside"], float(np.max(response)))

    limit, detected = criteria["max_residual"], criteria["min_control_signal"]
    values = {
        "coverage": (True, len(rows)),
        "conservation": (max(maxima[k] for k in ("conservation", "cut_charge", "projector")) < limit, max(maxima[k] for k in ("conservation", "cut_charge", "projector"))),
        "exact-reference": (max(maxima["exact"], maxima["frozen_exact"]) < limit, max(maxima["exact"], maxima["frozen_exact"])),
        "tolerance-refinement": (maxima["refinement"] < limit, maxima["refinement"]),
        "rescheduling": (maxima["rescheduling"] < limit, maxima["rescheduling"]),
        "local-frames": (maxima["frame"] < limit, maxima["frame"]),
        "causal-jacobian": (maxima["jacobian_outside"] < limit and minima["jacobian_inside"] > detected, maxima["jacobian_outside"]),
        "jacobian-refinement": (maxima["jacobian_refinement"] < criteria["max_jacobian_difference"], maxima["jacobian_refinement"]),
        "shared-memory-order": (minima["order_signal"] > detected, minima["order_signal"]),
        "frozen-memory": (minima["frozen_charge"] > detected and minima["memory_response"] > detected, minima["frozen_charge"]),
    }
    target = output / "derived"
    target.mkdir(parents=True, exist_ok=True)
    for name, data in (("residuals", rows), ("balance", balance), ("jacobian", jacobians), ("overlaps", responses), ("controls", controls)):
        write_rows(target / f"{name}.csv", data)
    write_json(target / "incidence.json", {"events": expected_events.tolist(), "ancestor_mask": ancestor_mask.tolist()})
    summary = {"samples": p["samples"], "circuits": 2 * p["samples"], "events_per_circuit": 12,
               "maxima": maxima, "minima": minima, "threshold": limit}
    write_json(target / "summary.json", summary)
    checks = {"schema_version": "research-checks-v1", "checks": [
        {"id": key, "status": "pass" if passed else "fail", "value": value, "evidence": "derived/summary.json"}
        for key, (passed, value) in values.items()]}
    write_json(output / "checks.json", checks)
    return {"raw_source": paths[-1].relative_to(run_path).as_posix(), "checks": checks, "summary": summary}
