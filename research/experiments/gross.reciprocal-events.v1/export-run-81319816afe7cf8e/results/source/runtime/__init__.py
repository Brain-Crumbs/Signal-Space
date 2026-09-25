"""Runtime exports without eagerly importing the experiment registry."""

__all__ = ["ResearchRuntime"]


def __getattr__(name: str):
    if name == "ResearchRuntime":
        from signal_space.runtime.runner import ResearchRuntime
        return ResearchRuntime
    raise AttributeError(name)
