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
from unittest import mock

from signal_space.contracts.validation import (
    ContractError,
    validate_config,
    validate_manifest,
)
from signal_space.cli import _sweep
from signal_space.numerics.synthetic import recurrence
from signal_space.runtime.archive import archive_run
from signal_space.runtime.errors import CheckpointMismatch, IntegrityError
from signal_space.runtime.io import read_json, sha256_file, write_json
from signal_space.runtime.package import RunPackage, run_identity
from signal_space.runtime.runner import (
    ResearchRuntime,
    _monitor_process,
    _terminate_process,
)
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
        with self.assertRaisesRegex(IntegrityError, "immutable artifact changed"):
            self.runtime.analyze(self.workspace, result["run_id"])
        with self.assertRaisesRegex(IntegrityError, "checksum mismatch"):
            self.runtime.verify(self.workspace, result["run_id"])

    def test_run_identity_includes_execution_provenance(self) -> None:
        config = self.runtime.validate(fixture())
        code = {
            "revision": "abc",
            "tree_state": "clean",
            "dirty_patch_hash": "0" * 64,
            "runtime_version": "1",
        }
        first = {
            "environment": {"python": "3.12", "os": "one"},
            "dependencies": {"sha256": "1" * 64},
        }
        second = deepcopy(first)
        second["environment"]["os"] = "two"
        self.assertNotEqual(
            run_identity(config, code, first)[0],
            run_identity(config, code, second)[0],
        )

    def test_manifest_update_is_not_visible_before_artifact_reseal(self) -> None:
        created = self.runtime.create_run(fixture(), self.workspace)
        package = self.runtime._package(self.workspace, created["run_id"])
        entered_seal = threading.Event()
        release_seal = threading.Event()
        original_seal = RunPackage._seal_locked

        def delayed_seal(
            current: RunPackage,
            manifest: dict,
            mutable_prefixes: tuple[str, ...],
        ) -> None:
            entered_seal.set()
            self.assertTrue(release_seal.wait(timeout=5))
            original_seal(current, manifest, mutable_prefixes)

        with mock.patch.object(RunPackage, "_seal_locked", delayed_seal):
            update = threading.Thread(
                target=lambda: package.update(
                    lambda manifest: manifest.update(
                        {"technical_state": "prepared"}
                    )
                )
            )
            update.start()
            self.assertTrue(entered_seal.wait(timeout=5))
            self.assertEqual(package.manifest["technical_state"], "validated")
            release_seal.set()
            update.join(timeout=5)

        self.assertFalse(update.is_alive())
        self.assertEqual(package.manifest["technical_state"], "prepared")

    def test_manifest_rejects_open_or_empty_child_records(self) -> None:
        result = self.runtime.run(fixture(), self.workspace)
        manifest = self.runtime.status(self.workspace, result["run_id"])
        manifest["attempts"] = [{}]
        with self.assertRaisesRegex(ContractError, "missing"):
            validate_manifest(manifest)

    def test_analysis_reference_is_independent_of_worker_primitive(self) -> None:
        with mock.patch(
            "signal_space.models.synthetic.advance", return_value=999.0
        ):
            self.assertEqual(recurrence(1.0, 0.5, 0.25, 2), [1.0, 0.75, 0.625])

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

    def test_resume_reconciles_orphaned_running_attempt(self) -> None:
        config = fixture()
        config["parameters"].update({"steps": 18, "checkpoint_interval": 5})
        config["fixture_controls"]["interrupt_at_step"] = 7
        result = self.runtime.run(config, self.workspace)
        package = self.runtime._package(self.workspace, result["run_id"])
        manifest = package.manifest
        attempt_path = package.path / manifest["attempts"][0]["path"]
        detail = read_json(attempt_path / "attempt.json")
        detail.update({"state": "running", "worker_pid": 2**30})
        write_json(attempt_path / "attempt.json", detail)
        manifest["attempts"][0].update(
            {"state": "running", "exit_code": None, "failure": None}
        )
        manifest["technical_state"] = "running"
        write_json(package.manifest_path, manifest)
        resumed = self.runtime.resume(self.workspace, result["run_id"])
        self.assertEqual(resumed["state"], "completed")
        repaired = package.manifest["attempts"][0]
        self.assertEqual(repaired["state"], "interrupted")
        self.assertEqual(repaired["failure"]["code"], "ORPHANED_WORKER")

    @unittest.skipUnless(os.name == "posix", "process-group signal test")
    def test_hard_termination_kills_uncooperative_worker(self) -> None:
        process = subprocess.Popen(
            [
                sys.executable,
                "-c",
                "import signal,time; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(30)",
            ],
            start_new_session=True,
        )
        time.sleep(0.1)
        _terminate_process(process, cooperative_seconds=0)
        self.assertIsNotNone(process.poll())

    def test_aggregate_output_limit_stops_many_small_files(self) -> None:
        attempt = Path(self.temporary.name) / "quota-attempt"
        attempt.mkdir()
        script = (
            "import pathlib,sys,time; p=pathlib.Path(sys.argv[1]); "
            "[(p / f'part-{i}.bin').write_bytes(b'x' * 131072) for i in range(20)]; "
            "time.sleep(30)"
        )
        process = subprocess.Popen(
            [sys.executable, "-c", script, str(attempt)],
            start_new_session=os.name == "posix",
        )
        reason, _ = _monitor_process(
            process,
            attempt,
            {"max_wall_seconds": 5, "max_output_mb": 1},
        )
        self.assertEqual(reason, "output")
        _terminate_process(process, cooperative_seconds=0)
        self.assertIsNotNone(process.poll())

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
            self.assertEqual(result["state"], "queued")
            deadline = time.time() + 10
            while time.time() < deadline:
                manifest = request(f"/v1/runs/{result['run_id']}")
                if manifest["technical_state"] in {
                    "completed",
                    "cancelled",
                    "interrupted",
                    "failed",
                }:
                    break
                time.sleep(0.02)
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

            preflight = urllib.request.Request(
                base + "/v1/runs",
                method="OPTIONS",
                headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": "POST",
                    "Access-Control-Request-Headers": "authorization, content-type",
                },
            )
            with urllib.request.urlopen(preflight, timeout=5) as response:
                self.assertEqual(response.status, 204)
                self.assertEqual(
                    response.headers["Access-Control-Allow-Origin"], origin
                )
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_service_returns_run_id_before_long_job_finishes(self) -> None:
        origin = "http://127.0.0.1:4173"
        server = ResearchAPI(("127.0.0.1", 0), self.workspace, origin)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        config = fixture()
        config["parameters"].update(
            {"steps": 200, "checkpoint_interval": 10, "step_delay_ms": 5}
        )
        request = urllib.request.Request(
            f"http://127.0.0.1:{server.server_port}/v1/runs",
            data=json.dumps(config).encode(),
            method="POST",
            headers={
                "Origin": origin,
                "Authorization": f"Bearer {server.token}",
                "Content-Type": "application/json",
            },
        )
        try:
            started = time.monotonic()
            with urllib.request.urlopen(request, timeout=5) as response:
                result = json.loads(response.read())
            elapsed = time.monotonic() - started
            self.assertEqual(response.status, 202)
            self.assertEqual(result["state"], "queued")
            self.assertLess(elapsed, 0.5)
            manifest = self.runtime.status(self.workspace, result["run_id"])
            self.assertNotEqual(manifest["technical_state"], "completed")
            deadline = time.time() + 10
            while time.time() < deadline:
                manifest = self.runtime.status(self.workspace, result["run_id"])
                if manifest["technical_state"] == "completed":
                    break
                time.sleep(0.02)
            self.assertEqual(manifest["technical_state"], "completed")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_concurrent_reports_receive_unique_ids_and_provenance(self) -> None:
        result = self.runtime.run(fixture(), self.workspace)
        analysis = self.runtime.analyze(self.workspace, result["run_id"])
        reports: list[dict] = []

        def create_report() -> None:
            reports.append(
                self.runtime.report(
                    self.workspace, result["run_id"], analysis["analysis_id"]
                )
            )

        threads = [threading.Thread(target=create_report) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=20)
        self.assertEqual(len(reports), 2)
        self.assertEqual(len({item["report_id"] for item in reports}), 2)
        self.assertTrue(all("render_provenance" in item for item in reports))
        self.assertTrue(self.runtime.verify(self.workspace, result["run_id"])["valid"])

    def test_archive_preserves_unresolved_scientific_result(self) -> None:
        config = fixture()
        config["fixture_controls"]["fail_at_step"] = 6
        result = self.runtime.run(config, self.workspace)
        analysis = self.runtime.analyze(self.workspace, result["run_id"])
        self.assertEqual(analysis["classification"], "unresolved")
        self.runtime.report(self.workspace, result["run_id"])
        package = self.runtime._package(self.workspace, result["run_id"])
        archived = archive_run(
            package.path, Path(self.temporary.name) / "negative-archive"
        )
        self.assertEqual(archived["state"], "archived")

    def test_sweep_propagates_failed_member_state(self) -> None:
        config = fixture()
        config["fixture_controls"]["fail_at_step"] = 6
        sweep = _sweep(
            self.runtime,
            config,
            ["parameters.gain=0.75"],
            self.workspace,
        )
        self.assertEqual(sweep["state"], "failed")
        self.assertEqual(sweep["members"][0]["status"], "failed")


if __name__ == "__main__":
    unittest.main()
