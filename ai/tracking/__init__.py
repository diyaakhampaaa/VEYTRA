"""VEYTRA Member 3 — per-camera vehicle tracking.

This package currently implements a simple IoU tracker that consumes
Member 1 detection JSON and assigns ``local_track_id`` values.

Cross-camera matching, Re-ID, SUMO, and trajectory reconstruction are
intentionally out of scope here.
"""

from ai.tracking.tracker import IoUAssociator, PerCameraTracker, track_sequence

__all__ = ["IoUAssociator", "PerCameraTracker", "track_sequence"]
