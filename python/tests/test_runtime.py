from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from copy import deepcopy
from pathlib import Path

from signal_space.contracts.validation import ContractError, validate_config
from signal_space.runtime.archive import archive_run
from signal_space.runtime.errors import CheckpointMismatch, IntegrityError
from signal_space.runtime.io import sha256_file
from signal_space.runtime.runner import ResearchRuntime
from signal_space.service.api import ResearchAPI

ROOT = Path(__file__).resolve().parents[2]


def fixture() -> dict:
    return json.loads((ROOT / "fixtures/research/synthetic.json").read_text())


class RuntimeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="signal-space-e00-")
        self.workspace = Path(self.temporary.name) / "work"
        self.runtime = ResearchRuntime()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_closed_validation_units_finite_numbers_and_estimate(self) -> None:
        config = fixture()
        resolved = self.runtime.validate(config)
        self.assertEqual(resolved["units"]["value"], "dimensionless")
        self.assertTrue(self.runtime.estimate(config)["accepted"])
        for mutate in (
            lambda value: value.update({"unknown": 1}),
            lambda value: value["parameters"].update({"gain": float("nan")}),
            lambda value: value["units"].update({"value": "meters"}),
            lambda value: value["parameters"].update({"steps": 0}),
        ):
            invalid = deepcopy(config)
            mutate(invalid)
            with self.assertRaises(ContractError):
                validate_config(invalid)

    def test_complete_reanalysis_report_integrity_and_archive(self) -> None:
        result = self.runtime.run(fixture(), self.workspace)
        self.assertEqual(result["state"], "completed")
        run_id = result["run_id"]
        manifest = self.runtime.status(self.workspace, run_id)
        run_path = self.workspace / manifest["experiment_id"] / run_id
        raw = run_path / manifest["attempts"][0]["path"] / "raw/series.csv"
        before = sha256_file(raw)
        first = self.runtime.analyze(self.workspace, run_id)
        second = self.runtime.analyze(self.workspace, run_id)
        self.assertNotEqual(first["analysis_id"], second["analysis_id"])
        self.assertEqual(second["supersedes"], first["analysis_id"])
        self.assertEqual(before, sha256_file(raw))
        report = self.runtime.report(self.workspace, run_id, second["analysis_id"])
        report_path = run_path / report["path"]
        self.assertTrue((report_path / "report.pdf").read_bytes().startswith(b"%PDF"))
        for extension in ("png", "svg", "pdf"):
            self.assertTrue((report_path / f"figures/recurrence.{extension}").is_file())
        verified = self.runtime.verify(self.workspace, run_id)
        self.assertTrue(verified["valid"])

        archive_root = Path(self.temporary.name) / "archive"
        catalog = Path(self.temporary.name) / "research/catalog.json"
        catalog.parent.mkdir()
        catalog.write_text('{"schema_version":1,"updated":"2026-09-18","entries":[]}\n')
        archived = archive_run(run_path, archive_root, catalog)
        self.assertEqual(archived["state"], "archived")
        self.assertEqual(json.loads(catalog.read_text())["entries"][0]["kind"], "experiment-run")

    def test_corrupt_artifact_is_explicit(self) -> None:
        result = self.runtime.run(fixture(), self.workspace)
        manifest = self.runtime.status(self.workspace, result["run_id"])
        run_path = self.workspace / manifest["experiment_id"] / result["run_id"]
        raw = run_path / manifest["attempts"][0]["path"] / "raw/series.csv"
        raw.write_text(raw.read_text() + "999,999\n")
        with self.assertRaisesRegex(IntegrityError, "checksum mismatch"):
            self.runtime.verify(self.workspace, result["run_id"])

    def test_interruption_resume_and_checkpoint_mismatch(self) -> None:
        config = fixture()
        config["parameters"].update({"steps": 18, "checkpoint_interval": 5})
        config["fixture_controls"]["interrupt_at_step"] = 7
        result = self.runtime.run(config, self.workspace)
        self.assertEqual(result["state"], "interrupted")
        self.assertTrue(result["resumable"])
        run_id = result["run_id"]
        resumed = self.runtime.resume(self.workspace, run_id)
        self.assertEqual(resumed["state"], "completed")
        manifest = self.runtime.status(self.workspace, run_id)
        self.assertEqual(manifest["attempts"][1]["parent_attempt_id"], "attempt-0001")
        analysis = self.runtime.analyze(self.workspace, run_id)
        self.assertEqual(analysis["classification"], "pass")

        other = deepcopy(config)
        other["seeds"]["root"] += 1
        failed = self.runtime.run(other, self.workspace)
        other_manifest = self.runtime.status(self.workspace, failed["run_id"])
        package = self.workspace / other_manifest["experiment_id"] / failed["run_id"]
        checkpoint = package / other_manifest["attempts"][0]["checkpoint"]["path"]
        checkpoint.write_text(checkpoint.read_text() + " ")
        with self.assertRaises(CheckpointMismatch):
            self.runtime.resume(self.workspace, failed["run_id"])

        controlled = deepcopy(config)
        controlled["seeds"]["root"] += 2
        controlled["fixture_controls"].update(
            {"interrupt_at_step": None, "fail_at_step": 6}
        )
        failure = self.runtime.run(controlled, self.workspace)
        self.assertEqual(failure["state"], "failed")
        self.assertTrue(failure["resumable"])

    def test_external_cancel_is_terminal_and_resumable(self) -> None:
        config = fixture()
        config["parameters"].update({"steps": 300, "checkpoint_interval": 10, "step_delay_ms": 5})
        config_path = Path(self.temporary.name) / "cancel.json"
        config_path.write_text(json.dumps(config))
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(ROOT / "python")
        process = subprocess.Popen(
            [sys.executable, "-m", "signal_space", "--workspace", str(self.workspace), "run", "--config", str(config_path)],
            cwd=ROOT,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        run_id = None
        deadline = time.time() + 10
        while time.time() < deadline:
            manifests = list(self.workspace.glob("*/run-*/manifest.json"))
            if manifests:
                manifest = json.loads(manifests[0].read_text())
                run_id = manifest["run_id"]
                if manifest["technical_state"] == "running":
                    break
            time.sleep(0.02)
        self.assertIsNotNone(run_id)
        cancelled = self.runtime.cancel(self.workspace, run_id)
        self.assertEqual(cancelled["state"], "cancellation-requested")
        stdout, stderr = process.communicate(timeout=10)
        self.assertEqual(process.returncode, 130, stderr)
        self.assertEqual(json.loads(stdout)["state"], "cancelled")
        resumed = self.runtime.resume(self.workspace, run_id)
        self.assertEqual(resumed["state"], "completed")

    def test_service_uses_same_validation_and_enforces_origin_token(self) -> None:
        origin = "http://127.0.0.1:4173"
        server = ResearchAPI(("127.0.0.1", 0), self.workspace, origin)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_port}"

        def request(path: str, body: dict | None = None, request_origin: str = origin):
            data = json.dumps(body).encode() if body is not None else None
            value = urllib.request.Request(
                base + path,
                data=data,
                method="POST" if data is not None else "GET",
                headers={"Origin": request_origin, "Authorization": f"Bearer {server.token}", "Content-Type": "application/json"},
            )
            with urllib.request.urlopen(value, timeout=5) as response:
                return json.loads(response.read())

        try:
            service = request("/v1/validate", fixture())["config"]
            self.assertEqual(service, self.runtime.validate(fixture()))
            with self.assertRaises(urllib.error.HTTPError) as forbidden:
                request("/v1/experiments", request_origin="http://attacker.invalid")
            self.assertEqual(forbidden.exception.code, 403)
            result = request("/v1/runs", fixture())
            events = request(f"/v1/runs/{result['run_id']}/events")["events"]
            self.assertGreater(len(events), 1)
            after = request(f"/v1/runs/{result['run_id']}/events?cursor={events[0]['cursor']}")["events"]
            self.assertEqual(len(after), len(events) - 1)
            manifest = request(f"/v1/runs/{result['run_id']}")
            artifact = next(item for item in manifest["artifacts"] if item["kind"] == "raw")
            value = urllib.request.Request(
                base + f"/v1/runs/{result['run_id']}/artifacts/{artifact['id']}",
                headers={"Origin": origin, "Authorization": f"Bearer {server.token}"},
            )
            with urllib.request.urlopen(value, timeout=5) as response:
                self.assertIn(b"step,value", response.read())
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
