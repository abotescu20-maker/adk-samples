"""Genetic health coach agent package."""

try:  # pragma: no cover - optional dependency for local testing
    from .agent import root_agent  # type: ignore F401
except ModuleNotFoundError:  # pragma: no cover
    root_agent = None  # type: ignore[assignment]

__all__ = ["root_agent"]
