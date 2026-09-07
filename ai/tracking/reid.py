"""Baseline vehicle appearance embeddings for Member 3.

This module is independent of ``tracker.py``. It consumes:

- an original camera ``frame`` (``numpy.ndarray``) held by the caller
- a ``vehicle_bbox`` of ``[x1, y1, x2, y2]``

and returns a fixed-length appearance vector. The current implementation is
a normalized per-channel RGB histogram. A later neural Re-ID model can
replace ``ReIDEmbedder.embed`` without changing ``embed_tracked_frame``.

The image is never written into tracking JSON.
"""

from __future__ import annotations

from typing import Any

import numpy as np

# 8 bins × 3 channels. Small, deterministic, no learned weights.
_HIST_BINS = 8
_HIST_RANGE = (0.0, 256.0)


def _is_valid_bbox(value: Any) -> bool:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        return False
    try:
        x1, y1, x2, y2 = (float(v) for v in value)
    except (TypeError, ValueError):
        return False
    return x2 > x1 and y2 > y1


def _crop(frame: np.ndarray, vehicle_bbox: Any) -> np.ndarray | None:
    """Return a clipped HxWxC crop, or None if nothing remains."""
    if not isinstance(frame, np.ndarray) or frame.size == 0 or frame.ndim < 2:
        return None
    if not _is_valid_bbox(vehicle_bbox):
        return None

    height, width = frame.shape[0], frame.shape[1]
    x1, y1, x2, y2 = (float(v) for v in vehicle_bbox)
    ix1 = max(0, int(x1))
    iy1 = max(0, int(y1))
    ix2 = min(width, int(x2))
    iy2 = min(height, int(y2))
    if ix2 <= ix1 or iy2 <= iy1:
        return None

    crop = frame[iy1:iy2, ix1:ix2]
    if crop.size == 0:
        return None
    return crop


def _as_rgb(crop: np.ndarray) -> np.ndarray | None:
    """Use the first three channels; repeat a single channel to RGB."""
    if crop.ndim == 2:
        return np.stack([crop, crop, crop], axis=-1)
    if crop.ndim != 3 or crop.shape[2] < 1:
        return None
    if crop.shape[2] == 1:
        channel = crop[:, :, 0]
        return np.stack([channel, channel, channel], axis=-1)
    return crop[:, :, :3]


class ReIDEmbedder:
    """Swappable appearance encoder. Baseline: L2-normalized RGB histograms.

    ``embed(frame, vehicle_bbox)`` is the only method a real vehicle Re-ID
    model needs to replace. Invalid inputs return ``None`` (never raise).
    """

    def __init__(self, bins: int = _HIST_BINS) -> None:
        if bins < 1:
            raise ValueError("bins must be >= 1")
        self.bins = bins

    def embed(self, frame: Any, vehicle_bbox: Any) -> list[float] | None:
        """Return a normalized appearance vector for one vehicle crop."""
        if not isinstance(frame, np.ndarray):
            return None
        crop = _crop(frame, vehicle_bbox)
        if crop is None:
            return None
        rgb = _as_rgb(crop)
        if rgb is None:
            return None

        pixels = np.asarray(rgb, dtype=np.float64).reshape(-1, 3)
        parts: list[np.ndarray] = []
        for channel in range(3):
            hist, _ = np.histogram(
                pixels[:, channel],
                bins=self.bins,
                range=_HIST_RANGE,
            )
            parts.append(hist.astype(np.float64))
        vector = np.concatenate(parts)
        norm = float(np.linalg.norm(vector))
        if norm > 0.0:
            vector = vector / norm
        return vector.tolist()


def embed_tracked_frame(
    frame: Any,
    tracked_dict: Any,
    embedder: ReIDEmbedder | None = None,
) -> dict[str, Any]:
    """Attach ``embedding`` to tracked detections; do not store the image.

    Copies Member 1 / tracker fields. Embeddings are computed only when
    ``local_track_id`` is present and not ``None``. Other detections are
    copied without an ``embedding`` key.
    """
    if not isinstance(tracked_dict, dict):
        return {
            "camera_id": None,
            "timestamp": None,
            "source": None,
            "detections": [],
            "error": "invalid_tracked_dict",
        }

    encoder = embedder if embedder is not None else ReIDEmbedder()
    out: dict[str, Any] = {
        "camera_id": tracked_dict.get("camera_id"),
        "timestamp": tracked_dict.get("timestamp"),
        "source": tracked_dict.get("source"),
        "detections": [],
    }
    for key, value in tracked_dict.items():
        if key not in out and key != "detections":
            out[key] = value

    detections = tracked_dict.get("detections")
    if not isinstance(detections, list):
        out["detections"] = []
        if "error" not in out:
            out["error"] = "detections_not_a_list"
        return out

    tracked_rows: list[dict[str, Any]] = []
    for det in detections:
        if not isinstance(det, dict):
            tracked_rows.append({"invalid_detection": det})
            continue
        row = dict(det)
        track_id = row.get("local_track_id", None)
        if track_id is not None:
            row["embedding"] = encoder.embed(frame, row.get("vehicle_bbox"))
        tracked_rows.append(row)
    out["detections"] = tracked_rows
    return out
