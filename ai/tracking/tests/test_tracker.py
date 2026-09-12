"""Tests for the dependency-free ByteTrack-style local tracker."""

from __future__ import annotations

import sys
from pathlib import Path

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


def test_one_vehicle_keeps_id_with_motion():
    tracker = PerCameraTracker()
    first = tracker.update(_frame([_det([100, 100, 200, 220])]))
    second = tracker.update(_frame([_det([110, 105, 210, 225])],
                                    timestamp="2026-09-06T15:30:01"))
    assert first["detections"][0]["local_track_id"] == 1
    assert second["detections"][0]["local_track_id"] == 1


def test_high_confidence_detections_get_different_ids():
    tracker = PerCameraTracker()
    result = tracker.update(_frame([
        _det([10, 10, 80, 90]),
        _det([300, 10, 380, 90]),
    ]))
    ids = [d["local_track_id"] for d in result["detections"]]
    assert ids == [1, 2]


def test_low_confidence_detection_can_match_existing_track():
    tracker = PerCameraTracker(high_threshold=0.5, low_threshold=0.1)
    first = tracker.update(_frame([_det([100, 100, 200, 200], confidence=0.95)]))
    second = tracker.update(_frame([_det([105, 103, 205, 203], confidence=0.25)]))
    assert first["detections"][0]["local_track_id"] == 1
    assert second["detections"][0]["local_track_id"] == 1


def test_unmatched_low_confidence_detection_does_not_create_track():
    tracker = PerCameraTracker(high_threshold=0.5, low_threshold=0.1)
    result = tracker.update(_frame([
        _det([10, 10, 80, 90], confidence=0.25)
    ]))
    assert result["detections"][0]["local_track_id"] is None


def test_empty_and_invalid_inputs_do_not_crash():
    tracker = PerCameraTracker()
    tracker.update(_frame([_det([10, 10, 80, 90])]))
    assert tracker.update(_frame([]))["detections"] == []
    assert tracker.update({"camera_id": "C01", "timestamp": "t", "source": "real"})["detections"] == []
    assert "error" in tracker.update(None)
    assert "error" in tracker.update(_frame("not-a-list"))


def test_track_is_removed_after_max_age():
    tracker = PerCameraTracker(max_age=1)
    tracker.update(_frame([_det([10, 10, 80, 90])]))
    tracker.update(_frame([]))
    tracker.update(_frame([]))
    reappeared = tracker.update(_frame([_det([10, 10, 80, 90])]))
    assert reappeared["detections"][0]["local_track_id"] == 2


def test_cameras_have_independent_local_ids():
    tracker = PerCameraTracker()
    cam1 = tracker.update(_frame([_det([10, 10, 80, 90])], camera_id="C01"))
    cam2 = tracker.update(_frame([_det([10, 10, 80, 90])], camera_id="C02"))
    assert cam1["detections"][0]["local_track_id"] == 1
    assert cam2["detections"][0]["local_track_id"] == 1


def test_member1_fields_are_preserved():
    out = track_sequence([
        _frame([_det([10, 10, 80, 90], vehicle_type="Bus")]),
        _frame([_det([12, 12, 82, 92], vehicle_type="Bus")]),
    ])
    assert out[0]["source"] == "real"
    assert out[0]["detections"][0]["vehicle_type"] == "Bus"
    assert out[1]["detections"][0]["local_track_id"] == 1


def test_invalid_detection_entries_receive_null_id():
    result = PerCameraTracker().update(_frame([
        "bad",
        _det([10, 10, 80, 90]),
        {"vehicle_bbox": [1, 2]},
    ]))
    assert result["detections"][0]["local_track_id"] is None
    assert result["detections"][1]["local_track_id"] == 1
    assert result["detections"][2]["local_track_id"] is None


def test_iou_is_bounded():
    assert 0.0 <= bbox_iou([0, 0, 10, 10], [5, 5, 15, 15]) <= 1.0
