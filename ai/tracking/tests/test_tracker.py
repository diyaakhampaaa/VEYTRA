"""Unit tests for the per-camera IoU tracker."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Repo root so `from ai.tracking ...` works without installing the package.
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai.tracking.tracker import PerCameraTracker, bbox_iou, track_sequence


def _det(bbox, vehicle_type="Sedan", confidence=0.9):
    return {
        "vehicle_bbox": bbox,
        "vehicle_type": vehicle_type,
        "vehicle_confidence": confidence,
        "vehicle_detector": "VehicleNet-Y26x",
        "plate_bbox": None,
        "plate_confidence": 0.0,
    }


def _frame(detections, camera_id="C01", timestamp="2026-09-06T15:30:00", source="real"):
    return {
        "camera_id": camera_id,
        "timestamp": timestamp,
        "source": source,
        "detections": detections,
    }


def test_one_vehicle_across_two_frames_keeps_the_same_local_track_id():
    tracker = PerCameraTracker()
    box_a = [100, 100, 200, 220]
    box_b = [110, 105, 210, 225]  # same vehicle, slight motion — high IoU

    first = tracker.update(_frame([_det(box_a)], timestamp="2026-09-06T15:30:00"))
    second = tracker.update(_frame([_det(box_b)], timestamp="2026-09-06T15:30:01"))

    assert first["detections"][0]["local_track_id"] == 1
    assert second["detections"][0]["local_track_id"] == first["detections"][0]["local_track_id"]
    assert bbox_iou(box_a, box_b) >= 0.3


def test_two_vehicles_receive_different_ids():
    tracker = PerCameraTracker()
    left = _det([10, 10, 80, 90])
    right = _det([300, 10, 380, 90])

    result = tracker.update(_frame([left, right]))
    ids = [det["local_track_id"] for det in result["detections"]]

    assert ids[0] is not None
    assert ids[1] is not None
    assert ids[0] != ids[1]


def test_empty_frame_does_not_crash():
    tracker = PerCameraTracker()
    tracker.update(_frame([_det([10, 10, 80, 90])]))

    empty = tracker.update(_frame([]))
    assert empty["detections"] == []
    assert empty["camera_id"] == "C01"

    missing = tracker.update(
        {"camera_id": "C01", "timestamp": "t", "source": "real"}
    )
    assert missing["detections"] == []
    assert "error" in missing

    none_result = tracker.update(None)
    assert none_result["detections"] == []
    assert "error" in none_result

    bad_list = tracker.update(_frame("not-a-list"))
    assert bad_list["detections"] == []
    assert "error" in bad_list


def test_a_new_vehicle_gets_a_new_id():
    tracker = PerCameraTracker()
    first = tracker.update(_frame([_det([10, 10, 80, 90])]))
    existing_id = first["detections"][0]["local_track_id"]

    # Far from the first box, so IoU is ~0 and this must be a new track.
    second = tracker.update(
        _frame(
            [
                _det([10, 10, 80, 90]),
                _det([400, 300, 500, 420]),
            ]
        )
    )
    ids = [det["local_track_id"] for det in second["detections"]]

    assert existing_id in ids
    assert any(track_id != existing_id for track_id in ids)
    assert len(set(ids)) == 2


def test_disappeared_vehicle_is_dropped_after_max_age_and_does_not_crash():
    tracker = PerCameraTracker(max_age=1)
    tracker.update(_frame([_det([10, 10, 80, 90])]))
    tracker.update(_frame([]))  # miss 1 — still alive
    after_drop = tracker.update(_frame([]))  # miss 2 — track removed
    assert after_drop["detections"] == []

    # A later detection at the same place is a new identity (no Re-ID yet).
    reappeared = tracker.update(_frame([_det([10, 10, 80, 90])]))
    assert reappeared["detections"][0]["local_track_id"] == 2


def test_cameras_do_not_share_track_state():
    tracker = PerCameraTracker()
    cam1 = tracker.update(_frame([_det([10, 10, 80, 90])], camera_id="C01"))
    cam2 = tracker.update(_frame([_det([10, 10, 80, 90])], camera_id="C02"))

    assert cam1["detections"][0]["local_track_id"] == 1
    assert cam2["detections"][0]["local_track_id"] == 1


def test_track_sequence_preserves_member1_fields():
    frames = [
        _frame([_det([10, 10, 80, 90], vehicle_type="Bus")]),
        _frame([_det([12, 12, 82, 92], vehicle_type="Bus")]),
    ]
    out = track_sequence(frames)
    assert out[0]["source"] == "real"
    assert out[0]["detections"][0]["vehicle_type"] == "Bus"
    assert "vehicle_bbox" in out[0]["detections"][0]
    assert out[0]["detections"][0]["local_track_id"] == out[1]["detections"][0]["local_track_id"]


def test_invalid_detection_entries_get_null_id_not_an_exception():
    tracker = PerCameraTracker()
    result = tracker.update(
        _frame(
            [
                "bad",
                _det([10, 10, 80, 90]),
                {"vehicle_bbox": [1, 2]},
            ]
        )
    )
    assert len(result["detections"]) == 3
    assert result["detections"][0]["local_track_id"] is None
    assert result["detections"][1]["local_track_id"] == 1
    assert result["detections"][2]["local_track_id"] is None
