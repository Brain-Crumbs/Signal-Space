"""Seeded matrix experiment; direct algebra, no time or space discretization."""

import csv
import os
from pathlib import Path
import numpy as np

from signal_space.models.operators import (
    I, SIGMA, hermitian, lorentz, projector, observer, norm, euclidean, su2,
)
from signal_space.runtime.events import append_event
from signal_space.runtime.io import read_json, write_json


def measure(x, y, j, z, s):
    t = observer(j)
    xp, yp, tp = [s @ m @ s.conj().T for m in (x, y, t)]
    zp = s @ z
    p = projector(z)
    raw_ray = s @ p @ s.conj().T
    weight = float(np.trace(raw_ray).real)
    pp = raw_ray / weight
    rho = float(np.vdot(z, z).real)
    eig, vec = np.linalg.eigh(t)
    whitening = (vec * (1 / np.sqrt(eig))) @ vec.conj().T
    xw = whitening @ x @ whitening.conj().T
    basis = [I, *SIGMA]
    h = np.array([[euclidean(t, a, b) for b in basis] for a in basis])
    return {
        "condition_j": float(np.linalg.cond(j)),
        "det_x": float(np.linalg.det(x).real),
        "g_xy": lorentz(x, y),
        "det_transform_error": abs(np.linalg.det(xp) - np.linalg.det(x)) / max(1, np.linalg.norm(x) ** 2),
        "g_transform_error": abs(lorentz(xp, yp) - lorentz(x, y)) / max(1, np.linalg.norm(x) * np.linalg.norm(y)),
        "sl_error": abs(np.linalg.det(s) - 1),
        "observer_det_error": abs(np.linalg.det(t) - 1),
        "observer_norm": norm(z, t),
        "observer_norm_transformed": norm(zp, tp),
        "norm_transform_error": abs(norm(zp, tp) - norm(z, t)) / max(1, norm(z, t)),
        "norm_identity_error": abs(norm(z, t) - 2 * lorentz(t, np.outer(z, z.conj()))) / max(1, norm(z, t)),
        "projector_error": float(np.linalg.norm(pp @ pp - pp)),
        "projector_trace_error": abs(float(np.trace(pp).real) - 1),
        "weighted_ray_error": float(np.linalg.norm(rho * weight * pp - np.outer(zp, zp.conj())) / max(1, np.vdot(zp, zp).real)),
        "euclidean_error": abs(euclidean(t, x, x) - np.trace(xw @ xw).real / 2) / max(1, abs(euclidean(t, x, x))),
        "euclidean_min_eigenvalue": float(np.linalg.eigvalsh(h)[0]),
    }


def write_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def execute(request_path):
    request = read_json(request_path)
    if request.get("resume_checkpoint"):
        raise ValueError("this bounded algebra experiment has no resume capability")
    attempt = Path(request["attempt_path"])
    raw = attempt / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    events = attempt / "events.jsonl"
    config = request["config"]
    rng = np.random.Generator(np.random.PCG64(request["seed_ledger"]["sampling"]))
    write_json(raw / "rng-start.json", rng.bit_generator.state)
    append_event(events, "worker-started", "run", {"pid": os.getpid(), "algorithm": "direct-matrix-v1"})
    arrays = {key: [] for key in ("x", "y", "j", "z", "s", "constituents")}
    rows = []
    n = config["parameters"]["samples"]
    for index in range(n):
        if (attempt / "cancel.request").exists():
            append_event(events, "cancellation-observed", "run", {"completed": index})
            return 130
        pair = []
        for _ in range(2):
            for trial in range(10000):
                value = hermitian(rng.normal(size=4))
                if np.linalg.cond(value) <= 100:
                    pair.append(value)
                    break
            else:
                raise ValueError("bounded Hermitian rejection sampler exhausted")
        for trial in range(10000):
            a = rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))
            j = a @ a.conj().T
            if np.linalg.cond(j) <= 100:
                break
        else:
            raise ValueError("bounded aggregate rejection sampler exhausted")
        z = rng.normal(size=2) + 1j * rng.normal(size=2)
        rapidity = rng.uniform(-1, 1)
        s = su2(rng) @ np.diag(np.exp([rapidity / 2, -rapidity / 2])) @ su2(rng)
        x, y = pair
        rows.append({"sample": index, **measure(x, y, j, z, s)})
        for key, value in zip(arrays, (x, y, j, z, s, a), strict=True):
            arrays[key].append(value)
    np.savez_compressed(raw / "inputs.npz", **{k: np.array(v) for k, v in arrays.items()})
    write_rows(raw / "measurements.csv", rows)

    directions = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]]) / np.sqrt(3)
    rays = np.array([hermitian(np.r_[1, v]) / 2 for v in directions])
    gram = np.array([[lorentz(a, b) for b in rays] for a in rays])
    # Deterministic boost control: holding the original weight is inconsistent.
    boost = np.diag(np.exp([0.5, -0.5]))
    z = np.array([1, 0], dtype=complex)
    transformed = boost @ z
    corrected = projector(transformed) * np.vdot(transformed, transformed).real
    wrong = projector(transformed)  # deliberately retains rho=1
    controls = {
        "gram": gram.tolist(), "gram_eigenvalues": np.linalg.eigvalsh(gram).tolist(),
        "correct_weight_error": float(np.linalg.norm(corrected - np.outer(transformed, transformed.conj())) / np.vdot(transformed, transformed).real),
        "omitted_weight_error": float(np.linalg.norm(wrong - np.outer(transformed, transformed.conj())) / np.vdot(transformed, transformed).real),
        "expected_omitted_weight_error": float(1 - np.exp(-1)),
    }
    write_json(raw / "controls.json", controls)
    near = []
    for angle in [0.0, *config["parameters"]["near_angles"]]:
        a = np.array([[1, np.cos(angle)], [0, np.sin(angle)]], dtype=complex)
        j = a @ a.conj().T
        condition = float(np.linalg.cond(j)) if angle else None
        try:
            t = observer(j)
            status = "valid"
            error = float(abs(np.linalg.det(t) - 1))
        except ValueError:
            status = "singular" if angle == 0 else "ill-conditioned"
            error = None
        determinant = float(np.linalg.det(j).real)
        near.append({"angle": angle, "condition_j": condition, "det_j": determinant,
                     "expected_det": float(np.sin(angle) ** 2), "status": status,
                     "observer_det_error": error})
    write_json(raw / "conditioning.json", near)
    write_json(raw / "rng-end.json", rng.bit_generator.state)
    write_json(raw / "execution.json", {"samples": n, "root_seed": config["seeds"]["root"],
               "sampling_seed": request["seed_ledger"]["sampling"], "rng": "numpy.PCG64",
               "blas_threads": {k: os.environ.get(k) for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")},
               "physical_evolution": False})
    append_event(events, "worker-completed", "run", {"samples": n, "controls": len(near) + 2})
    return 0
