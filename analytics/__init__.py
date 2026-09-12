"""VEYTRA traffic analytics (Member 5).

This package currently implements traffic density only.
Imports are lazy so `python -m analytics.density` does not double-load the module.
"""

from typing import Any

__all__ = ["compute_density", "load_vehicle_events"]


def __getattr__(name: str) -> Any:
    if name == "compute_density":
        from analytics.density import compute_density

        return compute_density
    if name == "load_vehicle_events":
        from analytics.io import load_vehicle_events

        return load_vehicle_events
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
