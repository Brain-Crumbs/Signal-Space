from __future__ import annotations

import hashlib
import mimetypes
import os
import platform
import shutil
import subprocess
import sys
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator

from signal_space import __version__
from signal_space.runtime.io import canonical_bytes, now, read_json, sha256_bytes, sha256_file, write_json
from signal_space.runtime.seeds import seed_ledger

ROOT = Path(__file__).resolve().parents[3]
_LOCKS_GUARD = threading.Lock()
_LOCKS: dict[Path, threading.RLock] = {}


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


def environment_identity() -> dict[str, Any]:
    return {
        "python": sys.version,
        "implementation": platform.python_implementation(),
        "os": platform.platform(),
        "architecture": platform.machine(),
        "numeric_libraries": {
            "numpy": _module_version("numpy"),
            "matplotlib": _module_version("matplotlib"),
        },
        "accelerator": "none",
    }


def dependency_identity() -> dict[str, str]:
    lock = ROOT / "python/requirements-lock.txt"
    return {"path": "python/requirements-lock.txt", "sha256": sha256_file(lock)}


def execution_identity() -> dict[str, Any]:
    return {
        "environment": environment_identity(),
        "dependencies": dependency_identity(),
    }


def run_identity(
    config: dict[str, Any], identity: dict[str, Any], execution: dict[str, Any]
) -> tuple[str, str]:
    config_hash = sha256_bytes(canonical_bytes(config))
    key = {
        "config_hash": config_hash,
        "code_identity": identity,
        "execution_identity": execution,
    }
    return f"run-{sha256_bytes(canonical_bytes(key))[:16]}", config_hash


class RunPackage:
    def __init__(self, path: Path):
        self.path = path
        self.manifest_path = path / "manifest.json"

    @property
    def manifest(self) -> dict[str, Any]:
        return read_json(self.manifest_path)

    @property
    def _lock(self) -> threading.RLock:
        key = self.path.resolve()
        with _LOCKS_GUARD:
            return _LOCKS.setdefault(key, threading.RLock())

    @contextmanager
    def locked(self) -> Iterator[None]:
        with self._lock:
            yield

    @classmethod
    def create(cls, workspace: Path, config: dict[str, Any], experiment_version: str) -> "RunPackage":
        identity = code_identity()
        execution = execution_identity()
        run_id, config_hash = run_identity(config, identity, execution)
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
        write_json(provenance / "environment.json", execution["environment"])
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
            "execution_identity": execution,
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
        with self._lock:
            manifest = self.manifest
            mutable = _mutable_attempt_prefixes(manifest)
            self._verify_indexed(manifest, mutable)
            change(manifest)
            manifest["updated_at"] = now()
            # Publish the changed manifest only after resealing has discovered
            # every newly created artifact.  Writing here would expose a brief
            # terminal-state manifest with the previous artifact catalog to
            # concurrent status/API readers.
            self._seal_locked(manifest, mutable)
            return manifest

    def verify_immutable(self) -> None:
        with self._lock:
            manifest = self.manifest
            self._verify_indexed(manifest, _mutable_attempt_prefixes(manifest))

    def seal(self) -> None:
        with self._lock:
            manifest = self.manifest
            mutable = _mutable_attempt_prefixes(manifest)
            self._verify_indexed(manifest, mutable)
            self._seal_locked(manifest, mutable)

    def _verify_indexed(
        self, manifest: dict[str, Any], mutable_prefixes: tuple[str, ...]
    ) -> None:
        for artifact in manifest.get("artifacts", []):
            relative = artifact["path"]
            if relative.startswith(mutable_prefixes):
                continue
            path = self.path / relative
            if (
                not path.is_file()
                or path.stat().st_size != artifact["size"]
                or sha256_file(path) != artifact["sha256"]
            ):
                from signal_space.runtime.errors import IntegrityError

                raise IntegrityError(
                    f"immutable artifact changed before package update: {relative}"
                )

    def _seal_locked(
        self, manifest: dict[str, Any], mutable_prefixes: tuple[str, ...]
    ) -> None:
        indexed = {item["path"]: item for item in manifest.get("artifacts", [])}
        artifacts = []
        for path in sorted(self.path.rglob("*")):
            if (
                not path.is_file()
                or path.name in {"manifest.json", "checksums.sha256"}
                or path.name.endswith(".jsonl.lock")
                or path.name.startswith(".")
            ):
                continue
            relative = path.relative_to(self.path).as_posix()
            existing = indexed.get(relative)
            digest = sha256_file(path)
            size = path.stat().st_size
            if (
                existing is not None
                and not relative.startswith(mutable_prefixes)
                and (existing["sha256"] != digest or existing["size"] != size)
            ):
                from signal_space.runtime.errors import IntegrityError

                raise IntegrityError(
                    f"immutable artifact changed while sealing package: {relative}"
                )
            artifacts.append(
                existing
                if existing is not None
                and existing["sha256"] == digest
                and existing["size"] == size
                else {
                    "id": "artifact-"
                    + hashlib.sha256(relative.encode()).hexdigest()[:16],
                    "kind": _artifact_kind(relative),
                    "path": relative,
                    "sha256": digest,
                    "size": size,
                    "media_type": mimetypes.guess_type(path.name)[0]
                    or "application/octet-stream",
                    "source_ids": existing.get("source_ids", []) if existing else [],
                }
            )
        missing = set(indexed) - {item["path"] for item in artifacts}
        immutable_missing = {
            path for path in missing if not path.startswith(mutable_prefixes)
        }
        if immutable_missing:
            from signal_space.runtime.errors import IntegrityError

            raise IntegrityError(
                "immutable artifacts disappeared while sealing package: "
                + ", ".join(sorted(immutable_missing))
            )
        manifest["artifacts"] = artifacts
        write_json(self.manifest_path, manifest)
        lines = []
        for path in sorted(self.path.rglob("*")):
            if (
                path.is_file()
                and path.name != "checksums.sha256"
                and not path.name.endswith(".jsonl.lock")
                and not path.name.startswith(".")
            ):
                lines.append(f"{sha256_file(path)}  {path.relative_to(self.path).as_posix()}")
        (self.path / "checksums.sha256").write_text("\n".join(lines) + "\n")


def _mutable_attempt_prefixes(manifest: dict[str, Any]) -> tuple[str, ...]:
    return tuple(
        entry["path"].rstrip("/") + "/"
        for entry in manifest.get("attempts", [])
        if entry.get("state") in {"prepared", "running"}
    )


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
