"""VEYTRA Member 3 — per-camera vehicle tracking.

IoU tracking is stdlib-only. The Re-ID baseline depends on numpy and is
imported lazily so ``from ai.tracking import PerCameraTracker`` does not
require numpy.
"""

from typing import Any

from ai.tracking.tracker import IoUAssociator, PerCameraTracker, track_sequence

__all__ = [
    "IoUAssociator",
    "PerCameraTracker",
    "ReIDEmbedder",
    "embed_tracked_frame",
    "track_sequence",
]


def __getattr__(name: str) -> Any:
    if name in ("ReIDEmbedder", "embed_tracked_frame"):
        from ai.tracking.reid import ReIDEmbedder, embed_tracked_frame

        exports = {
            "ReIDEmbedder": ReIDEmbedder,
            "embed_tracked_frame": embed_tracked_frame,
        }
        return exports[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
