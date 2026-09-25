from __future__ import annotations

from signal_space.experiments.base import ExperimentPlugin
from signal_space.experiments.synthetic import SyntheticExperiment
from signal_space.experiments.charged import ChargedExperiment
from signal_space.experiments.operators import OperatorExperiment
from signal_space.experiments.reciprocal import ReciprocalExperiment
from signal_space.experiments.router import RouterExperiment
from signal_space.experiments.floquet import FloquetExperiment

_PLUGINS: dict[str, ExperimentPlugin] = {
    SyntheticExperiment.experiment_id: SyntheticExperiment(),
    ChargedExperiment.experiment_id: ChargedExperiment(),
    OperatorExperiment.experiment_id: OperatorExperiment(),
    ReciprocalExperiment.experiment_id: ReciprocalExperiment(),
    RouterExperiment.experiment_id: RouterExperiment(),
    FloquetExperiment.experiment_id: FloquetExperiment(),
}


def get_experiment(experiment_id: str) -> ExperimentPlugin:
    try:
        return _PLUGINS[experiment_id]
    except KeyError as error:
        raise ValueError(f"unregistered experiment id: {experiment_id}") from error


def list_experiments() -> list[dict[str, object]]:
    return [plugin.describe() for plugin in _PLUGINS.values()]
