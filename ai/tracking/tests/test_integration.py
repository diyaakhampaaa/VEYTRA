"""Integration tests for Member 1/2 -> Member 3 data contracts."""

from __future__ import annotations

from ai.tracking.integration import (
    match_tracked_frames,
    prepare_track_records,
    verification_payloads,
)


T0 = "2026-09-06T08:00:00+05:30"
T1 = "2026-09-06T08:00:10+05:30"
T2 = "2026-09-06T08:00:20+05:30"
T3 = "2026-09-06T08:00:30+05:30"

SAME = [1.0, 0.0, 0.0]


def _frame(camera, timestamp, track_id, plate, confidence, event_id):
    return {
        "camera_id": camera,
        "timestamp": timestamp,
        "source": "real",
        "detections": [
            {
                "event_id": event_id,
                "vehicle_bbox": [10, 10, 100, 100],
                "local_track_id": track_id,
                "embedding": SAME,
                # Exact Member 2 output names:
                "plate": plate,
                "confidence": confidence,
                "alternatives": [],
            }
        ],
    }


def test_prepare_track_records_consumes_member2_contract():
    records = prepare_track_records(
        [
            _frame("C01", T0, 1, "dl01ab1234", 0.61, "E001"),
            _frame("C01", T1, 1, "DL01AB1234", 0.95, "E002"),
        ]
    )

    assert len(records) == 1

    record = records[0]

    assert record["camera_id"] == "C01"
    assert record["local_track_id"] == 1
    assert record["first_timestamp"] == T0
    assert record["last_timestamp"] == T1
    assert record["plate_text"] == "DL01AB1234"
    assert record["ocr_confidence"] == 0.95
    assert len(record["plate_history"]) == 2

    # Member 1 event identity must survive Member 3 aggregation.
    assert record["event_ids"] == ["E001", "E002"]

    assert len(record["observations"]) == 2
    assert record["observations"][0]["event_id"] == "E001"
    assert record["observations"][1]["event_id"] == "E002"


def test_plausible_plate_mismatch_reaches_verification_candidates():
    result = match_tracked_frames(
        [
            _frame("C01", T0, 1, "DL01AB1234", 0.95, "E001"),
            _frame("C02", T2, 1, "DL01AB1284", 0.61, "E002"),
        ]
    )

    assert result["matches"] == []
    assert len(result["verification_candidates"]) == 1

    candidate = result["verification_candidates"][0]

    assert candidate["event"]["camera_id"] in {"C01", "C02"}
    assert candidate["supporting_event"]["camera_id"] in {"C01", "C02"}

    assert candidate["event"]["plate"] != candidate["supporting_event"]["plate"]

    # The matcher must preserve the original Member 1 event IDs.
    assert candidate["event"]["event_id"] in {"E001", "E002"}
    assert candidate["supporting_event"]["event_id"] in {"E001", "E002"}

    assert candidate["event"]["event_id"] != candidate["supporting_event"]["event_id"]

    assert candidate["match_score"]["reject_reason"] == "plate_mismatch"


def test_verification_payload_marks_lower_confidence_read_as_suspicious():
    result = match_tracked_frames(
        [
            _frame("C01", T0, 1, "DL01AB1234", 0.95, "E001"),
            _frame("C02", T2, 1, "DL01AB1284", 0.61, "E002"),
        ]
    )

    payload = verification_payloads(result)[0]

    assert payload["camera_id"] == "C02"
    assert payload["plate"] == "DL01AB1284"
    assert payload["ocr_confidence"] == 0.61

    assert payload["event_id"] == "E002"

    assert payload["nearby_events"][0]["plate"] == "DL01AB1234"
    assert payload["nearby_events"][0]["event_id"] == "E001"

def test_match_tracked_frames_reconstructs_trajectory_with_event_provenance():
    result = match_tracked_frames(
        [
            _frame("C01", T0, 1, "DL01AB1234", 0.95, "E001"),
            _frame("C02", T2, 1, "DL01AB1234", 0.92, "E002"),
        ]
    )

    # Cross-camera matching should identify the two local tracks
    # as the same global vehicle.
    assert len(result["matches"]) == 1
    assert result["matches"][0]["vehicle_id"].startswith("V")

    # Trajectory reconstruction must happen after matching.
    assert "trajectories" in result
    assert len(result["trajectories"]) == 1

    trajectory = result["trajectories"][0]

    # Global identity must survive reconstruction.
    assert trajectory["vehicle_id"] == result["matches"][0]["vehicle_id"]

    # The trajectory must preserve the original Member 1 event IDs.
    assert trajectory["event_ids"] == ["E001", "E002"]

    # Event-level observations must also survive.
    assert len(trajectory["event_observations"]) == 2
    assert trajectory["event_observations"][0]["event_id"] == "E001"
    assert trajectory["event_observations"][1]["event_id"] == "E002"

    # Camera order must be preserved chronologically.
    assert trajectory["camera_sequence"] == ["C01", "C02"]

    # The trajectory should retain its temporal boundaries.
    assert trajectory["start_time"] == T0
    assert trajectory["end_time"] == T2