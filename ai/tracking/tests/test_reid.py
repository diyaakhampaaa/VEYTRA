"""Unit tests for the baseline Re-ID embedder."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai.tracking.reid import ReIDEmbedder, embed_tracked_frame


def _solid_frame(color, height=40, width=40):
    return np.full((height, width, 3), color, dtype=np.uint8)


def _tracked(detections, camera_id="C01", timestamp="2026-09-06T15:30:00", source="real"):
    return {
        "camera_id": camera_id,
        "timestamp": timestamp,
        "source": source,
        "detections": detections,
    }


def test_valid_vehicle_crop_produces_an_embedding():
    frame = _solid_frame((10, 80, 200))
    embedding = ReIDEmbedder().embed(frame, [5, 5, 25, 25])

    assert embedding is not None
    assert isinstance(embedding, list)
    assert len(embedding) == 24
    assert all(isinstance(v, float) for v in embedding)
    assert abs(sum(v * v for v in embedding) - 1.0) < 1e-6


def test_same_crop_produces_the_same_embedding():
    frame = _solid_frame((30, 140, 90))
    bbox = [2, 2, 18, 18]
    embedder = ReIDEmbedder()

    first = embedder.embed(frame, bbox)
    second = embedder.embed(frame, bbox)

    assert first is not None
    assert first == second


def test_different_appearance_produces_a_different_embedding():
    red = _solid_frame((200, 10, 10))
    blue = _solid_frame((10, 10, 200))
    bbox = [0, 0, 40, 40]
    embedder = ReIDEmbedder()

    red_vec = embedder.embed(red, bbox)
    blue_vec = embedder.embed(blue, bbox)

    assert red_vec is not None
    assert blue_vec is not None
    assert red_vec != blue_vec


def test_invalid_bbox_returns_none():
    frame = _solid_frame((40, 40, 40))
    embedder = ReIDEmbedder()

    assert embedder.embed(frame, [10, 10, 10, 20]) is None
    assert embedder.embed(frame, [1, 2]) is None
    assert embedder.embed(frame, None) is None
    assert embedder.embed(frame, "bad") is None


def test_empty_frame_returns_none():
    embedder = ReIDEmbedder()
    bbox = [0, 0, 10, 10]

    assert embedder.embed(None, bbox) is None
    assert embedder.embed(np.array([]), bbox) is None
    assert embedder.embed(np.zeros((0, 0, 3), dtype=np.uint8), bbox) is None


def test_embed_tracked_frame_preserves_existing_fields():
    frame = _solid_frame((15, 90, 160))
    tracked = _tracked(
        [
            {
                "vehicle_bbox": [4, 4, 20, 20],
                "vehicle_type": "Sedan",
                "vehicle_confidence": 0.91,
                "vehicle_detector": "VehicleNet-Y26x",
                "plate_bbox": None,
                "plate_confidence": 0.0,
                "local_track_id": 1,
            }
        ]
    )
    original = {
        "camera_id": tracked["camera_id"],
        "timestamp": tracked["timestamp"],
        "source": tracked["source"],
        "detections": [dict(tracked["detections"][0])],
    }

    result = embed_tracked_frame(frame, tracked)

    assert result["camera_id"] == "C01"
    assert result["timestamp"] == "2026-09-06T15:30:00"
    assert result["source"] == "real"
    det = result["detections"][0]
    assert det["vehicle_bbox"] == [4, 4, 20, 20]
    assert det["vehicle_type"] == "Sedan"
    assert det["vehicle_confidence"] == 0.91
    assert det["vehicle_detector"] == "VehicleNet-Y26x"
    assert det["plate_bbox"] is None
    assert det["plate_confidence"] == 0.0
    assert det["local_track_id"] == 1
    assert isinstance(det["embedding"], list)
    assert "frame" not in result
    assert "image" not in result
    assert tracked == original


def test_detections_without_local_track_id_do_not_get_an_embedding():
    frame = _solid_frame((80, 80, 80))
    tracked = _tracked(
        [
            {
                "vehicle_bbox": [4, 4, 20, 20],
                "local_track_id": None,
            },
            {
                "vehicle_bbox": [4, 4, 20, 20],
            },
            {
                "vehicle_bbox": [4, 4, 20, 20],
                "local_track_id": 2,
            },
        ]
    )

    result = embed_tracked_frame(frame, tracked)
    missing, omitted, assigned = result["detections"]

    assert "embedding" not in missing
    assert "embedding" not in omitted
    assert assigned["local_track_id"] == 2
    assert isinstance(assigned["embedding"], list)
