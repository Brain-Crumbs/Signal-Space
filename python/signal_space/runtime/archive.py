from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from signal_space.runtime.errors import InvalidState
from signal_space.runtime.io import now, write_json
from signal_space.runtime.package import RunPackage
from signal_space.runtime.verify import verify_package


def archive_run(run_path: Path, archive_root: Path, catalog_path: Path | None = None) -> dict[str, Any]:
    verify_package(run_path)
    manifest = json.loads((run_path / "manifest.json").read_text())
    classification = manifest["scientific_classification"]
    if classification not in {"pass", "fail", "unresolved"} or not manifest["completeness"].get("report"):
        raise InvalidState("only verified runs with an explicit scientific classification and report may be archived")
    destination = archive_root / manifest["experiment_id"] / manifest["run_id"]
    if destination.exists():
        raise FileExistsError(f"archive destination already exists: {destination}")
    shutil.copytree(run_path, destination)
    package = RunPackage(destination)
    package.update(lambda value: value.update({"technical_state": "archived"}))
    verify_package(destination)
    if catalog_path:
        catalog = json.loads(catalog_path.read_text())
        entry_id = f"run-{manifest['run_id']}"
        if any(entry["id"] == entry_id for entry in catalog["entries"]):
            raise InvalidState(f"catalog already contains {entry_id}")
        try:
            relative = destination.relative_to(catalog_path.parent.parent).as_posix()
        except ValueError:
            relative = destination.as_posix()
        catalog["entries"].append({
            "id": entry_id,
            "title": f"Archived E00 fixture {manifest['run_id']}",
            "kind": "experiment-run",
            "status": f"scientific {classification}",
            "date": now()[:10],
            "path": f"{relative}/reports/{manifest['reports'][-1]['report_id']}/report.md",
            "summary": f"Verified synthetic lifecycle fixture classified {classification}; no physics claim.",
            "tags": ["E00", "fixture", "runtime", "reproducibility"],
        })
        catalog["updated"] = now()[:10]
        write_json(catalog_path, catalog)
    return {"run_id": manifest["run_id"], "state": "archived", "destination": str(destination)}
