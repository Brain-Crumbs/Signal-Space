from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from signal_space.contracts.validation import ContractError, validate_event, validate_manifest
from signal_space.runtime.errors import IntegrityError
from signal_space.runtime.events import read_events
from signal_space.runtime.io import read_json, safe_child, sha256_file


def verify_package(run_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        manifest = read_json(run_path / "manifest.json")
        validate_manifest(manifest)
    except (OSError, ValueError, ContractError) as error:
        raise IntegrityError(f"invalid manifest: {error}") from error

    expected: dict[str, str] = {}
    try:
        for line in (run_path / "checksums.sha256").read_text().splitlines():
            match = re.fullmatch(r"([a-f0-9]{64})  (.+)", line)
            if not match:
                errors.append(f"malformed checksum line: {line}")
                continue
            expected[match.group(2)] = match.group(1)
        actual_paths = {
            path.relative_to(run_path).as_posix()
            for path in run_path.rglob("*")
            if path.is_file() and path.name != "checksums.sha256"
        }
        if set(expected) != actual_paths:
            errors.append("checksum path set does not match package files")
        for relative, digest in expected.items():
            path = safe_child(run_path, relative)
            if not path.is_file() or sha256_file(path) != digest:
                errors.append(f"checksum mismatch: {relative}")
    except (OSError, ValueError) as error:
        errors.append(f"could not verify checksums: {error}")

    artifact_paths = {item["path"] for item in manifest["artifacts"]}
    if len(artifact_paths) != len(manifest["artifacts"]):
        errors.append("duplicate artifact path")
    for item in manifest["artifacts"]:
        try:
            path = safe_child(run_path, item["path"])
            if not path.is_file() or sha256_file(path) != item["sha256"] or path.stat().st_size != item["size"]:
                errors.append(f"artifact index mismatch: {item['path']}")
        except (OSError, ValueError):
            errors.append(f"invalid artifact path: {item['path']}")

    attempt_ids = {entry["attempt_id"] for entry in manifest["attempts"]}
    if len(attempt_ids) != len(manifest["attempts"]):
        errors.append("duplicate attempt ID")
    terminal = {"completed", "cancelled", "interrupted", "failed"}
    for attempt in manifest["attempts"]:
        if attempt["state"] not in terminal and manifest["technical_state"] not in {"prepared", "running"}:
            errors.append(f"nonterminal attempt {attempt['attempt_id']} under terminal run")
        parent = attempt.get("parent_attempt_id")
        if parent is not None and parent not in attempt_ids:
            errors.append(f"missing attempt parent: {parent}")
        events_path = run_path / attempt["path"] / "events.jsonl"
        try:
            events = read_events(events_path)
            for index, event in enumerate(events, 1):
                validate_event(event)
                if event["sequence"] != index:
                    errors.append(f"event sequence gap in {attempt['attempt_id']}")
                    break
        except (OSError, ValueError, ContractError) as error:
            errors.append(f"invalid event log for {attempt['attempt_id']}: {error}")
        checkpoint = attempt.get("checkpoint")
        if checkpoint:
            try:
                checkpoint_path = safe_child(run_path, checkpoint["path"])
                data = read_json(checkpoint_path)
                if sha256_file(checkpoint_path) != checkpoint["sha256"]:
                    errors.append(f"checkpoint checksum mismatch: {checkpoint['path']}")
                if data["config_hash"] != manifest["config_hash"]:
                    errors.append(f"checkpoint config mismatch: {checkpoint['path']}")
            except (OSError, ValueError, KeyError) as error:
                errors.append(f"invalid checkpoint record: {error}")

    analysis_ids = {entry["analysis_id"] for entry in manifest["analyses"]}
    if len(analysis_ids) != len(manifest["analyses"]):
        errors.append("duplicate analysis ID")
    report_ids = {entry["report_id"] for entry in manifest["reports"]}
    if len(report_ids) != len(manifest["reports"]):
        errors.append("duplicate report ID")
    artifact_ids = {entry["id"] for entry in manifest["artifacts"]}
    if len(artifact_ids) != len(manifest["artifacts"]):
        errors.append("duplicate artifact ID")
    if manifest["scientific_classification"] != "not-evaluated":
        latest = manifest["analyses"][-1] if manifest["analyses"] else None
        if latest is None or "checks.json" not in artifact_paths and f"{latest['path']}/checks.json" not in artifact_paths:
            errors.append("scientific classification lacks check evidence")
    for report in manifest["reports"]:
        if report["analysis_id"] not in analysis_ids:
            errors.append(f"report has missing analysis parent: {report['analysis_id']}")
        for relative in report["required_inputs"]:
            if relative not in artifact_paths:
                errors.append(f"report input is not indexed: {relative}")

    if errors:
        raise IntegrityError("; ".join(errors))
    return {
        "valid": True,
        "run_id": manifest["run_id"],
        "files": len(expected),
        "artifacts": len(manifest["artifacts"]),
        "attempts": len(manifest["attempts"]),
        "analyses": len(manifest["analyses"]),
        "reports": len(manifest["reports"]),
    }
