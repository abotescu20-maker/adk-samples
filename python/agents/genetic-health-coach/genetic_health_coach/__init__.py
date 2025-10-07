"""Genetic health coach agent package."""

try:  # pragma: no cover - optional dependency for local testing
    from .agent import root_agent  # type: ignore F401
except ModuleNotFoundError:  # pragma: no cover
    root_agent = None  # type: ignore[assignment]

try:  # pragma: no cover - optional demo server
    from .webapp import run_demo_server  # type: ignore F401
except ModuleNotFoundError:  # pragma: no cover
    run_demo_server = None  # type: ignore[assignment]

__all__ = ["root_agent", "run_demo_server"]
