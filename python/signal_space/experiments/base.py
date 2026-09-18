from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class ExperimentPlugin(ABC):
    """The shared experiment contract used by CLI, service, and tests."""

    experiment_id: str
    version: str
    model_id: str

    @abstractmethod
    def describe(self) -> dict[str, Any]: ...

    @abstractmethod
    def validate(self, config: Any) -> dict[str, Any]: ...

    @abstractmethod
    def estimate(self, config: dict[str, Any]) -> dict[str, Any]: ...

    @abstractmethod
    def prepare(self, config: dict[str, Any], run_path: Path, attempt_path: Path, resume: dict[str, Any] | None) -> dict[str, Any]: ...

    @abstractmethod
    def run(self, request_path: Path) -> int: ...

    @abstractmethod
    def analyze(self, run_path: Path, analysis_path: Path, config: dict[str, Any]) -> dict[str, Any]: ...

    @abstractmethod
    def classify(self, checks: dict[str, Any], config: dict[str, Any]) -> str: ...

    @abstractmethod
    def report(self, run_path: Path, report_path: Path, manifest: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]: ...
