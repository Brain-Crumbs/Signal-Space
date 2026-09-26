"""Isolated execution stage for the non-physical synthetic plugin."""

from __future__ import annotations

import csv
import math
import os
import time
from pathlib import Path
from typing import Any

from signal_space.models.synthetic import advance
from signal_space.runtime.events import append_event
from signal_space.runtime.io import read_json, write_json
from signal_space.runtime.seeds import next_state


def _checkpoint(
    path: Path,
    request: dict[str, Any],
    step: int,
    value: float,
    states: dict[str, int],
) -> Path:
    checkpoint = {
        "schema_version": "research-checkpoint-v1",
        "checkpoint_format_version": 1,
        "producing_attempt_id": request["attempt_id"],
        "parent_attempt_id": request.get("parent_attempt_id"),
        "config_hash": request["config_hash"],
        "code_identity_hash": request["code_identity_hash"],
        "solver_state": {
            "step": step,
            "value": value,
            "algorithm": "direct-recurrence-v1",
        },
        "domain": {
            "start": 0,
            "end": request["config"]["parameters"]["steps"],
        },
        "adaptive_state": None,
        "continuation_state": None,
        "rng_states": states,
        "pending_work": {"next_step": step + 1},
        "accumulated_diagnostics": {"rows_written": step + 1},
    }
    target = path / f"checkpoint-{step:08d}.json"
    write_json(target, checkpoint, canonical=True)
    return target


def execute(request_path: Path) -> int:
    request = read_json(request_path)
    attempt_path = Path(request["attempt_path"])
    events = attempt_path / "events.jsonl"
    raw = attempt_path / "raw/series.csv"
    checkpoints = attempt_path / "checkpoints"
    cancel = attempt_path / "cancel.request"
    raw.parent.mkdir(parents=True, exist_ok=True)
    checkpoints.mkdir(parents=True, exist_ok=True)
    config = request["config"]
    parameters = config["parameters"]
    controls = config["fixture_controls"]
    resume = request.get("resume_checkpoint")
    if resume:
        state = resume["solver_state"]
        start_step = int(state["step"])
        value = float(state["value"])
        states = {
            key: int(item) for key, item in resume["rng_states"].items()
        }
        prior_raw = Path(request["prior_attempt_path"]) / "raw/series.csv"
        with prior_raw.open(newline="") as source, raw.open(
            "w", newline=""
        ) as target:
            reader = csv.reader(source)
            writer = csv.writer(target)
            writer.writerow(next(reader))
            for row in reader:
                if int(row[0]) <= start_step:
                    writer.writerow(row)
        mode = "a"
    else:
        start_step = 0
        value = float(parameters["initial_value"])
        states = {
            key: int(item) for key, item in request["seed_ledger"].items()
        }
        mode = "w"

    append_event(
        events,
        "worker-started",
        "run",
        {
            "pid": os.getpid(),
            "resumed_from_step": start_step if resume else None,
        },
    )
    with raw.open(mode, newline="") as stream:
        writer = csv.writer(stream)
        if not resume:
            writer.writerow(["step", "value"])
            writer.writerow([0, format(value, ".17g")])
            stream.flush()
            os.fsync(stream.fileno())
        for step in range(
            start_step + 1, int(parameters["steps"]) + 1
        ):
            if cancel.exists():
                checkpoint = _checkpoint(
                    checkpoints, request, step - 1, value, states
                )
                append_event(
                    events,
                    "cancellation-observed",
                    "run",
                    {"step": step - 1, "checkpoint": checkpoint.name},
                )
                return 130
            value = advance(
                value,
                float(parameters["gain"]),
                float(parameters["forcing"]),
            )
            if not math.isfinite(value):
                append_event(events, "non-finite-output", "run", {"step": step})
                return 2
            for name in states:
                states[name] = next_state(states[name])
            writer.writerow([step, format(value, ".17g")])
            stream.flush()
            os.fsync(stream.fileno())
            if (
                step % int(parameters["checkpoint_interval"]) == 0
                or step == int(parameters["steps"])
            ):
                checkpoint = _checkpoint(
                    checkpoints, request, step, value, states
                )
                append_event(
                    events,
                    "checkpoint-written",
                    "run",
                    {"step": step, "checkpoint": checkpoint.name},
                )
            if (
                not request.get("parent_attempt_id")
                and controls.get("fail_at_step") == step
            ):
                append_event(
                    events, "fixture-failure", "run", {"step": step}
                )
                return 2
            if (
                not request.get("parent_attempt_id")
                and controls.get("interrupt_at_step") == step
            ):
                stream.flush()
                os.fsync(stream.fileno())
                os._exit(77)
            delay = float(parameters["step_delay_ms"]) / 1000
            if delay:
                time.sleep(delay)
    append_event(
        events,
        "worker-completed",
        "run",
        {"steps": parameters["steps"]},
    )
    return 0
