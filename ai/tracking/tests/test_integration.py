"""Integration tests for Member 1/2 -> Member 3 data contracts."""

from __future__ import annotations

from ai.tracking.integration import match_tracked_frames, prepare_track_records, verification_payloads


T0 = "2026-09-06T08:00:00+05:30"
T1 = "2026-09-06T08:00:10+05:30"
T2 = "2026-09-06T08:00:20+05:30"
T3 = "2026-09-06T08:00:30+05:30"

SAME = [1.0, 0.0, 0.0]


def _frame(camera, timestamp, track_id, plate, confidence):
    return {
        "camera_id": camera,
        "timestamp": timestamp,
        "source": "real",
        "detections": [
            {
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
            _frame("C01", T0, 1, "dl01ab1234", 0.61),
            _frame("C01", T1, 1, "DL01AB1234", 0.95),
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


def test_plausible_plate_mismatch_reaches_verification_candidates():
    result = match_tracked_frames(
        [
            _frame("C01", T0, 1, "DL01AB1234", 0.95),
            _frame("C02", T2, 1, "DL01AB1284", 0.61),
        ]
    )
    assert result["matches"] == []
    assert len(result["verification_candidates"]) == 1
    candidate = result["verification_candidates"][0]
    assert candidate["event"]["camera_id"] in {"C01", "C02"}
    assert candidate["supporting_event"]["camera_id"] in {"C01", "C02"}
    assert candidate["event"]["plate"] != candidate["supporting_event"]["plate"]
    assert candidate["match_score"]["reject_reason"] == "plate_mismatch"


def test_verification_payload_marks_lower_confidence_read_as_suspicious():
    result = match_tracked_frames(
        [
            _frame("C01", T0, 1, "DL01AB1234", 0.95),
            _frame("C02", T2, 1, "DL01AB1284", 0.61),
        ]
    )
    payload = verification_payloads(result)[0]
    assert payload["camera_id"] == "C02"
    assert payload["plate"] == "DL01AB1284"
    assert payload["ocr_confidence"] == 0.61
    assert payload["nearby_events"][0]["plate"] == "DL01AB1234"
