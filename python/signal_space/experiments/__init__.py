"""Plugin exports without loading every plugin while importing a base class."""

__all__ = ["get_experiment", "list_experiments"]


def __getattr__(name: str):
    if name in __all__:
        from signal_space.experiments import registry
        return getattr(registry, name)
    raise AttributeError(name)
