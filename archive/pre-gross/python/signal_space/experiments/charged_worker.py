"""Restartable point-level continuation and refinement tasks. Failures are data."""

import shutil
from pathlib import Path
import numpy as np
from signal_space.runtime.io import read_json, write_json
from signal_space.runtime.events import append_event
from signal_space.numerics.charged_radial import solve_profile, observables, interpolate
from signal_space.numerics.charged_spectrum import spectrum


def initial_state(p):
    queue = []
    for lane in ("base", "half-step") if p["refinements"] else ("base",):
        for index, width in enumerate(p["seed_radii"]):
            queue.append(
                {
                    "kind": "seed",
                    "lane": lane,
                    "branch": f"seed-{index}",
                    "omega": p["omega_seed"],
                    "seed_radius": width,
                    "parent": None,
                    "step": p["omega_step"] / (2 if lane == "half-step" else 1),
                }
            )
    return {"queue": queue, "records": [], "branch_points": 0, "step": 0}


def checkpoint(request, state, path):
    write_json(
        path / f'checkpoint-{state["step"]:08d}.json',
        {
            "schema_version": "research-checkpoint-v1",
            "checkpoint_format_version": 1,
            "producing_attempt_id": request["attempt_id"],
            "parent_attempt_id": request.get("parent_attempt_id"),
            "config_hash": request["config_hash"],
            "code_identity_hash": request["code_identity_hash"],
            "solver_state": {"step": state["step"], "algorithm": "e01-point-queue-v1"},
            "continuation_state": state,
            "adaptive_state": {
                "policy": "halve failed step; grow successful step up to declared initial step"
            },
            "domain": request["config"]["parameters"],
            "rng_states": request["seed_ledger"],
            "pending_work": state["queue"],
            "accumulated_diagnostics": {"records": len(state["records"])},
        },
        canonical=True,
    )


def execute(request_path):
    request = read_json(request_path)
    attempt = Path(request["attempt_path"])
    raw = attempt / "raw"
    raw.mkdir(exist_ok=True)
    checkpoints = attempt / "checkpoints"
    checkpoints.mkdir(exist_ok=True)
    events = attempt / "events.jsonl"
    p = request["config"]["parameters"]
    resume = request.get("resume_checkpoint")
    state = resume["continuation_state"] if resume else initial_state(p)
    if resume:
        prior = Path(request["prior_attempt_path"]) / "raw"
        for row in state["records"]:
            for name in row["files"]:
                shutil.copyfile(prior / name, raw / name)

    def save():
        write_json(raw / "branch.json", {"schema_version": "e01-raw-v1", **state})
        checkpoint(request, state, checkpoints)

    save()
    append_event(
        events, "worker-started", "run", {"tasks_pending": len(state["queue"])}
    )
    while state["queue"]:
        if (attempt / "cancel.request").exists():
            save()
            append_event(
                events, "cancellation-observed", "run", {"step": state["step"]}
            )
            return 130
        task = state["queue"][0]
        if (
            task["kind"] in ("seed", "continue")
            and state["branch_points"] >= p["max_points"]
        ):
            append_event(
                events,
                "point-budget-exhausted",
                "run",
                {"pending": len(state["queue"])},
            )
            break
        state["queue"].pop(0)
        number = state["step"] + 1
        name = f"point-{number:06d}.json"
        seed = read_json(raw / task["parent"])["profile"] if task["parent"] else None
        radius = p["radius"] * (p["volume_factor"] if task["kind"] == "volume" else 1)
        nodes = p["nodes"] * (2 if task["kind"] == "spacing" else 1)
        if task["kind"] == "volume":
            nodes = int(np.ceil((p["nodes"] - 1) * p["volume_factor"])) + 1
        samples = p["sample_points"] * (2 if task["kind"] == "spacing" else 1)
        if task["kind"] == "volume":
            samples = int(np.ceil((p["sample_points"] - 1) * p["volume_factor"])) + 1
        if samples % 2 == 0:
            samples += 1
        tol = p["solver_tolerance"] / (10 if task["kind"] == "tolerance" else 1)
        row = {"id": f"point-{number:06d}", "file": name, "files": [name], **task}
        data = {}
        try:
            profile = solve_profile(
                task["omega"],
                radius,
                nodes,
                tol,
                p["max_nodes"],
                samples,
                seed,
                task.get("seed_radius", 4.0),
            )
            row["status"] = profile["status"]
            data = {"task": task, "profile": profile}
            if profile["status"] == "accepted":
                data["observables"] = observables(profile)
                spec_nodes = p["spectral_nodes"] * (
                    2 if task["kind"] == "spectral" else 1
                )
                if task["kind"] == "volume":
                    spec_nodes = (
                        int(np.ceil((p["spectral_nodes"] + 1) * p["volume_factor"])) - 1
                    )
                if (
                    task["kind"] in ("seed", "continue", "spectral", "volume")
                    and task["lane"] == "base"
                ):
                    try:
                        spec = spectrum(profile, spec_nodes, p["ell_max"])
                        for sector in spec["sectors"]:
                            vectors = f'point-{number:06d}-ell-{sector["ell"]}.npz'
                            np.savez_compressed(
                                raw / vectors,
                                real=sector.pop("eigenvectors_real"),
                                imag=sector.pop("eigenvectors_imag"),
                                r=sector["r"],
                            )
                            sector["eigenvectors_file"] = vectors
                            row["files"].append(vectors)
                        data["spectrum"] = spec
                    except (ValueError, RuntimeError, np.linalg.LinAlgError) as error:
                        data["spectrum_error"] = str(error)
                if seed:
                    grid = np.asarray(profile["r"])
                    previous = interpolate(seed, grid)[0]
                    difference = np.asarray(profile["f"]) - previous
                    dw = profile["omega"] - seed["omega"]
                    data["tangent"] = {
                        "delta_omega": dw,
                        "profile_derivative": (
                            (difference / dw).tolist() if dw else None
                        ),
                        "relative_profile_change": float(
                            np.linalg.norm(difference)
                            / max(np.linalg.norm(previous), 1e-30)
                        ),
                    }
                    if (
                        task["kind"] == "continue"
                        and data["tangent"]["relative_profile_change"] > 0.5
                    ):
                        row["status"] = "ill-conditioned"
                        profile["status"] = "ill-conditioned"
            write_json(raw / name, data)
        except (ValueError, RuntimeError, np.linalg.LinAlgError) as error:
            row["status"] = "failed"
            row["error"] = str(error)
            write_json(raw / name, {"task": task, "error": str(error)})
        if task["kind"] in ("seed", "continue"):
            state["branch_points"] += 1
            accepted = row["status"] == "accepted"
            # Deduplicate only coincident seed profiles within the SAME lane.
            if accepted and task["kind"] == "seed":
                for old in state["records"]:
                    if (
                        old["kind"] == "seed"
                        and old["lane"] == task["lane"]
                        and old["status"] == "accepted"
                    ):
                        old_p = read_json(raw / old["file"])["profile"]
                        if abs(old_p["f"][0] - profile["f"][0]) < 1e-5:
                            row["status"] = "duplicate-seed"
                            row["same_branch_as"] = old["branch"]
                            accepted = False
                            break
            if accepted:
                if p["refinements"] and task["lane"] == "base":
                    for kind in ("spacing", "volume", "tolerance", "spectral"):
                        state["queue"].append({**task, "kind": kind, "parent": name})
                directions = (-1, 1) if task["kind"] == "seed" else (task["direction"],)
                for direction in directions:
                    endpoint = p["omega_start"] if direction < 0 else p["omega_end"]
                    cap = p["omega_step"] / (2 if task["lane"] == "half-step" else 1)
                    step = min(cap, task["step"] * 1.25)
                    next_omega = profile["omega"] + direction * min(
                        step, abs(endpoint - profile["omega"])
                    )
                    if abs(next_omega - profile["omega"]) > 1e-12:
                        state["queue"].append(
                            {
                                **task,
                                "kind": "continue",
                                "omega": float(next_omega),
                                "parent": name,
                                "direction": direction,
                                "step": step,
                            }
                        )
            elif task["kind"] == "continue" and task["step"] / 2 >= p["min_omega_step"]:
                previous = read_json(raw / task["parent"])["profile"]["omega"]
                state["queue"].append(
                    {
                        **task,
                        "omega": (previous + task["omega"]) / 2,
                        "step": task["step"] / 2,
                    }
                )
            elif task["kind"] == "continue":
                row["endpoint_unresolved"] = True
        state["records"].append(row)
        state["step"] = number
        save()
        append_event(
            events,
            "point-completed",
            "run",
            {
                "step": number,
                "snapshot_version": "e01-progress-v1",
                "point_id": row["id"],
                "lane": task["lane"],
                "parent": task["parent"],
                "observables": {
                    key: data["observables"][key]
                    for key in ("E", "Q", "radius")
                } if row["status"] == "accepted" and "observables" in data else {},
                "provisional": True,
                "status": row["status"],
                "omega": task["omega"],
                "kind": task["kind"],
                "branch": task["branch"],
                "pending": len(state["queue"]),
            },
        )
    save()
    append_event(
        events,
        "worker-completed",
        "run",
        {"points": len(state["records"]), "pending": len(state["queue"])},
    )
    return 0
