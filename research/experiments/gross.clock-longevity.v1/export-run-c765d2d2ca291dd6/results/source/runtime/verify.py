from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from signal_space.contracts.validation import ContractError, validate_event, validate_manifest
from signal_space.runtime.errors import IntegrityError
from signal_space.runtime.events import read_events
from signal_space.runtime.io import canonical_bytes, read_json, safe_child, sha256_bytes, sha256_file
from signal_space.runtime.package import run_identity


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
            if path.is_file() and path.name not in {"checksums.sha256", ".package.lock"}
        }
        if set(expected) != actual_paths:
            errors.append("checksum path set does not match package files")
        for relative, digest in expected.items():
            path = safe_child(run_path, relative)
            if not path.is_file() or sha256_file(path) != digest:
                errors.append(f"checksum mismatch: {relative}")
    except (OSError, ValueError) as error:
        errors.append(f"could not verify checksums: {error}")

    try:
        config = read_json(safe_child(run_path, manifest["config_path"]))
        run_id, config_hash = run_identity(config, manifest["code_identity"], manifest["execution_identity"])
        if config_hash != manifest["config_hash"] or run_id != manifest["run_id"]:
            errors.append("resolved configuration/provenance does not match run identity")
        if any(config[key] != manifest[key] for key in ("experiment_id", "model_id")):
            errors.append("configuration model/experiment does not match manifest")
    except (OSError, ValueError, KeyError) as error:
        errors.append(f"invalid resolved configuration: {error}")

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
    seen_attempts: set[str] = set()
    for attempt in manifest["attempts"]:
        if attempt["state"] not in terminal and manifest["technical_state"] not in {"prepared", "running"}:
            errors.append(f"nonterminal attempt {attempt['attempt_id']} under terminal run")
        parent = attempt.get("parent_attempt_id")
        if parent is not None and parent not in seen_attempts:
            errors.append(f"missing or nonpreceding attempt parent: {parent}")
        seen_attempts.add(attempt["attempt_id"])
        try:
            attempt_path = safe_child(run_path, attempt["path"])
            detail = read_json(attempt_path / "attempt.json")
            if any(detail.get(key) != value for key, value in attempt.items()):
                errors.append(f"attempt record differs from manifest: {attempt['attempt_id']}")
            events = read_events(attempt_path / "events.jsonl")
            if not events:
                errors.append(f"empty event log: {attempt['attempt_id']}")
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
                if data["code_identity_hash"] != sha256_bytes(canonical_bytes(manifest["code_identity"])):
                    errors.append(f"checkpoint code mismatch: {checkpoint['path']}")
                if data["producing_attempt_id"] != attempt["attempt_id"] or data["solver_state"]["step"] != checkpoint["step"]:
                    errors.append(f"checkpoint producer/progress mismatch: {checkpoint['path']}")
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
    indexed = {item["path"]: item for item in manifest["artifacts"]}
    seen_analyses: set[str] = set()
    for analysis in manifest["analyses"]:
        for relative, digest in analysis["input_artifacts"].items():
            if relative not in indexed or indexed[relative]["sha256"] != digest:
                errors.append(f"analysis input identity mismatch: {relative}")
        if analysis["raw_source"] not in analysis["input_artifacts"]:
            errors.append("analysis raw_source lacks input identity")
        if analysis["supersedes"] is not None and analysis["supersedes"] not in seen_analyses:
            errors.append("analysis supersedes a missing or nonpreceding analysis")
        seen_analyses.add(analysis["analysis_id"])
        try:
            path = safe_child(run_path, analysis["path"])
            if read_json(path / "analysis.json") != analysis:
                errors.append("analysis record differs from manifest")
            checks = read_json(path / "checks.json")["checks"]
            ids = [check["id"] for check in checks]
            if len(set(ids)) != len(ids) or any(check["status"] not in {"pass", "fail", "unresolved", "not-evaluated"} for check in checks):
                errors.append("invalid or duplicate analysis checks")
            if not {item["id"] for item in manifest["acceptance_criteria"]}.issubset(ids):
                errors.append("analysis lacks preregistered check evidence")
            for check in checks:
                evidence = safe_child(path, check["evidence"])
                if evidence.relative_to(run_path.resolve()).as_posix() not in artifact_paths:
                    errors.append(f"check evidence is not indexed: {check['id']}")
        except (OSError, ValueError, KeyError, TypeError) as error:
            errors.append(f"invalid analysis evidence: {error}")
    if manifest["scientific_classification"] != "not-evaluated" and manifest["analyses"] and manifest["scientific_classification"] != manifest["analyses"][-1]["classification"]:
        errors.append("scientific classification differs from latest analysis")
    for criterion in manifest["acceptance_criteria"]:
        if manifest["scientific_classification"] != "not-evaluated" and criterion["evidence"] not in artifact_paths:
            errors.append(f"criterion lacks indexed evidence: {criterion['id']}")
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
