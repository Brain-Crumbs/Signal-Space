from __future__ import annotations

import json
import re
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

from signal_space.runtime.archive import archive_run
from signal_space.runtime.events import read_events
from signal_space.runtime.io import safe_child
from signal_space.runtime.runner import ResearchRuntime


ID = re.compile(r"^[a-zA-Z0-9._-]+$")


class ResearchAPI(ThreadingHTTPServer):
    def __init__(self, address: tuple[str, int], workspace: Path, origin: str, archive_root: Path | None = None, catalog_path: Path | None = None):
        super().__init__(address, ResearchHandler)
        self.runtime = ResearchRuntime()
        self.workspace = workspace
        self.origin = origin
        self.token = secrets.token_urlsafe(32)
        self.archive_root = archive_root
        self.catalog_path = catalog_path


class ResearchHandler(BaseHTTPRequestHandler):
    server: ResearchAPI

    def log_message(self, format: str, *args: object) -> None:
        return

    def _authorize(self) -> bool:
        if self.headers.get("Origin") != self.server.origin or self.headers.get("Authorization") != f"Bearer {self.server.token}":
            self._json(403, {"error": {"code": "FORBIDDEN", "message": "origin/token validation failed"}})
            return False
        return True

    def _json(self, status: int, value: Any) -> None:
        body = (json.dumps(value, sort_keys=True, allow_nan=False) + "\n").encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> Any:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 2 * 1024 * 1024:
            raise ValueError("request exceeds 2 MiB")
        return json.loads(self.rfile.read(length))

    def _run_id(self, part: str) -> str:
        if not ID.fullmatch(part):
            raise ValueError("invalid catalog identifier")
        return part

    def do_GET(self) -> None:
        if not self._authorize(): return
        try:
            parsed = urlparse(self.path)
            parts = parsed.path.strip("/").split("/")
            if parts == ["v1", "experiments"]:
                self._json(200, {"experiments": self.server.runtime.list()})
                return
            if len(parts) == 3 and parts[:2] == ["v1", "runs"]:
                self._json(200, self.server.runtime.status(self.server.workspace, self._run_id(parts[2])))
                return
            if len(parts) == 4 and parts[:2] == ["v1", "runs"] and parts[3] == "events":
                manifest = self.server.runtime.status(self.server.workspace, self._run_id(parts[2]))
                query = parse_qs(parsed.query)
                cursor = query.get("cursor", [""])[0]
                found = cursor == ""
                events = []
                for attempt in manifest["attempts"]:
                    for event in read_events(self.server.workspace / manifest["experiment_id"] / manifest["run_id"] / attempt["path"] / "events.jsonl"):
                        current = f"{attempt['attempt_id']}:{event['sequence']}"
                        if found:
                            events.append({**event, "attempt_id": attempt["attempt_id"], "cursor": current})
                        elif current == cursor:
                            found = True
                if cursor and not found:
                    self._json(409, {"error": {"code": "INVALID_CURSOR", "message": "event cursor is not present"}})
                else:
                    self._json(200, {"events": events})
                return
            if len(parts) == 5 and parts[:2] == ["v1", "runs"] and parts[3] == "artifacts":
                run_id, artifact_id = self._run_id(parts[2]), self._run_id(parts[4])
                manifest = self.server.runtime.status(self.server.workspace, run_id)
                artifact = next((item for item in manifest["artifacts"] if item["id"] == artifact_id), None)
                if artifact is None:
                    self._json(404, {"error": {"code": "ARTIFACT_NOT_FOUND", "message": "unknown artifact catalog id"}})
                    return
                run_path = self.server.workspace / manifest["experiment_id"] / run_id
                path = safe_child(run_path, artifact["path"])
                body = path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", artifact["media_type"])
                self.send_header("Content-Length", str(len(body)))
                self.send_header("X-Content-Type-Options", "nosniff")
                self.end_headers()
                self.wfile.write(body)
                return
            self._json(404, {"error": {"code": "NOT_FOUND", "message": "unknown API route"}})
        except Exception as error:
            self._error(error)

    def do_POST(self) -> None:
        if not self._authorize(): return
        try:
            path = urlparse(self.path).path
            parts = path.strip("/").split("/")
            if parts == ["v1", "validate"]:
                self._json(200, {"config": self.server.runtime.validate(self._body())})
                return
            if parts == ["v1", "estimate"]:
                self._json(200, self.server.runtime.estimate(self._body()))
                return
            if parts == ["v1", "runs"]:
                self._json(201, self.server.runtime.run(self._body(), self.server.workspace))
                return
            if len(parts) == 4 and parts[:2] == ["v1", "runs"]:
                run_id, action = self._run_id(parts[2]), parts[3]
                if action == "cancel": result = self.server.runtime.cancel(self.server.workspace, run_id)
                elif action == "resume": result = self.server.runtime.resume(self.server.workspace, run_id)
                elif action == "analyze": result = self.server.runtime.analyze(self.server.workspace, run_id)
                elif action == "report": result = self.server.runtime.report(self.server.workspace, run_id)
                elif action == "verify": result = self.server.runtime.verify(self.server.workspace, run_id)
                elif action == "archive" and self.server.archive_root: result = archive_run((self.server.runtime._package(self.server.workspace, run_id)).path, self.server.archive_root, self.server.catalog_path)
                else:
                    self._json(404, {"error": {"code": "NOT_FOUND", "message": "unknown or unavailable action"}})
                    return
                self._json(200, result)
                return
            self._json(404, {"error": {"code": "NOT_FOUND", "message": "unknown API route"}})
        except Exception as error:
            self._error(error)

    def _error(self, error: Exception) -> None:
        code = getattr(
            error,
            "code",
            "INVALID_REQUEST"
            if isinstance(error, (ValueError, KeyError))
            else "INTERNAL_ERROR",
        )
        self._json(400 if code != "INTERNAL_ERROR" else 500, {"error": {"code": code, "message": str(error)}})


def serve(workspace: Path, origin: str, host: str = "127.0.0.1", port: int = 0, archive_root: Path | None = None, catalog_path: Path | None = None) -> None:
    if host not in {"127.0.0.1", "::1", "localhost"}:
        raise ValueError("research service may bind to loopback only")
    server = ResearchAPI((host, port), workspace, origin, archive_root, catalog_path)
    print(json.dumps({"host": host, "port": server.server_port, "origin": origin, "token": server.token}), flush=True)
    server.serve_forever()
