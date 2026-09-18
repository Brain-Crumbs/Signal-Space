from __future__ import annotations

import hashlib
import mimetypes
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from signal_space import __version__
from signal_space.runtime.io import canonical_bytes, now, read_json, sha256_bytes, sha256_file, write_json
from signal_space.runtime.seeds import seed_ledger

ROOT = Path(__file__).resolve().parents[3]


def code_identity() -> dict[str, Any]:
    def git(*args: str) -> str:
        try:
            return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            return "unknown"

    revision = git("rev-parse", "HEAD")
    status = git("status", "--porcelain=v1", "--untracked-files=all")
    digest = hashlib.sha256()
    diff = subprocess.run(["git", "diff", "--binary", "HEAD"], cwd=ROOT, capture_output=True).stdout
    digest.update(diff)
    if status not in {"", "unknown"}:
        for line in status.splitlines():
            path_text = line[3:]
            if " -> " in path_text:
                path_text = path_text.split(" -> ", 1)[1]
            path = ROOT / path_text
            if line.startswith("??") and path.is_file():
                digest.update(path_text.encode())
                digest.update(path.read_bytes())
    return {
        "revision": revision,
        "tree_state": "clean" if status == "" else "dirty" if status != "unknown" else "unknown",
        "dirty_patch_hash": digest.hexdigest(),
        "runtime_version": __version__,
    }


def run_identity(config: dict[str, Any], identity: dict[str, Any]) -> tuple[str, str]:
    config_hash = sha256_bytes(canonical_bytes(config))
    key = {"config_hash": config_hash, "code_identity": identity}
    return f"run-{sha256_bytes(canonical_bytes(key))[:16]}", config_hash


class RunPackage:
    def __init__(self, path: Path):
        self.path = path
        self.manifest_path = path / "manifest.json"

    @property
    def manifest(self) -> dict[str, Any]:
        return read_json(self.manifest_path)

    @classmethod
    def create(cls, workspace: Path, config: dict[str, Any], experiment_version: str) -> "RunPackage":
        identity = code_identity()
        run_id, config_hash = run_identity(config, identity)
        path = workspace / config["experiment_id"] / run_id
        if path.exists():
            raise FileExistsError(f"run package already exists: {run_id}")
        path.mkdir(parents=True)
        package = cls(path)
        created = now()
        ledger = seed_ledger(int(config["seeds"]["root"]))
        write_json(path / "resolved-config.json", config, canonical=True)
        provenance = path / "provenance"
        write_json(provenance / "code.json", identity)
        write_json(provenance / "environment.json", {
            "python": sys.version,
            "implementation": platform.python_implementation(),
            "os": platform.platform(),
            "architecture": platform.machine(),
            "numeric_libraries": {"numpy": _module_version("numpy"), "matplotlib": _module_version("matplotlib")},
            "accelerator": "none",
        })
        shutil.copy2(ROOT / "python/requirements-lock.txt", provenance / "dependencies.lock")
        write_json(provenance / "inputs.json", {"config_hash": config_hash, "resolved_config": "resolved-config.json"})
        manifest = {
            "schema_version": "research-run-manifest-v1",
            "package_version": 1,
            "experiment_id": config["experiment_id"],
            "experiment_version": experiment_version,
            "model_id": config["model_id"],
            "run_id": run_id,
            "parent_run_id": None,
            "created_at": created,
            "updated_at": created,
            "technical_state": "validated",
            "scientific_classification": "not-evaluated",
            "config_hash": config_hash,
            "config_path": "resolved-config.json",
            "code_identity": identity,
            "seed_algorithm": "sha256-stream-v1",
            "seed_ledger": ledger,
            "attempts": [],
            "analyses": [],
            "reports": [],
            "artifacts": [],
            "acceptance_criteria": [
                {"id": "fixture-complete", "description": "all declared fixture steps are present", "evidence": None},
                {"id": "fixture-recurrence-error", "description": "saved output matches the independent recurrence within the declared threshold", "evidence": None},
            ],
            "completeness": {"config": True, "provenance": True, "attempts_terminal": False, "analysis": False, "report": False},
            "known_gaps": ["Synthetic E00 fixture only; no physical solver or scientific claim."],
            "checksum_algorithm": "sha256",
            "checksum_path": "checksums.sha256",
        }
        write_json(package.manifest_path, manifest)
        package.seal()
        return package

    def update(self, change: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
        manifest = self.manifest
        change(manifest)
        manifest["updated_at"] = now()
        write_json(self.manifest_path, manifest)
        self.seal()
        return manifest

    def seal(self) -> None:
        if self.manifest_path.exists():
            manifest = read_json(self.manifest_path)
            artifacts = []
            for path in sorted(self.path.rglob("*")):
                if not path.is_file() or path.name in {"manifest.json", "checksums.sha256"}:
                    continue
                relative = path.relative_to(self.path).as_posix()
                artifacts.append({
                    "id": "artifact-" + hashlib.sha256(relative.encode()).hexdigest()[:16],
                    "kind": _artifact_kind(relative),
                    "path": relative,
                    "sha256": sha256_file(path),
                    "size": path.stat().st_size,
                    "media_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
                    "source_ids": [],
                })
            manifest["artifacts"] = artifacts
            write_json(self.manifest_path, manifest)
        lines = []
        for path in sorted(self.path.rglob("*")):
            if path.is_file() and path.name != "checksums.sha256":
                lines.append(f"{sha256_file(path)}  {path.relative_to(self.path).as_posix()}")
        (self.path / "checksums.sha256").write_text("\n".join(lines) + "\n")


def _module_version(name: str) -> str:
    try:
        module = __import__(name)
        return str(module.__version__)
    except ImportError:
        return "unavailable"


def _artifact_kind(path: str) -> str:
    if path == "resolved-config.json": return "config"
    if path.startswith("provenance/"): return "provenance"
    if path.endswith("events.jsonl"): return "event-log"
    if "/checkpoints/" in path: return "checkpoint"
    if "/raw/" in path: return "raw"
    if path.endswith("checks.json"): return "check"
    if "/derived/" in path: return "derived"
    if "/plot-data/" in path: return "plot-data"
    if "/figures/" in path: return "figure"
    if "/reports/" in path or path.endswith(("report.md", "report.html", "report.pdf")): return "report"
    return "provenance"
