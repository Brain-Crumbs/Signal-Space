from __future__ import annotations

from signal_space.experiments.base import ExperimentPlugin
from signal_space.experiments.synthetic import SyntheticExperiment

_PLUGINS: dict[str, ExperimentPlugin] = {
    SyntheticExperiment.experiment_id: SyntheticExperiment(),
}


def get_experiment(experiment_id: str) -> ExperimentPlugin:
    try:
        return _PLUGINS[experiment_id]
    except KeyError as error:
        raise ValueError(f"unregistered experiment id: {experiment_id}") from error


def list_experiments() -> list[dict[str, object]]:
    return [plugin.describe() for plugin in _PLUGINS.values()]
