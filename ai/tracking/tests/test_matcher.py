"""Synthetic unit tests for cross-camera matching."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai.tracking.matcher import CrossCameraMatcher


def _track(
    camera_id,
    local_track_id,
    first,
    last,
    embedding=None,
    plate_text=None,
    **extra,
):
    row = {
        "camera_id": camera_id,
        "local_track_id": local_track_id,
        "first_timestamp": first,
        "last_timestamp": last,
        "source": "real",
    }
    if embedding is not None:
        row["embedding"] = embedding
    if plate_text is not None:
        row["plate_text"] = plate_text
    row.update(extra)
    return row


SAME_VEC = [1.0, 0.0, 0.0]
OTHER_VEC = [0.0, 1.0, 0.0]
T0 = "2026-09-06T08:00:00+05:30"
T1 = "2026-09-06T08:00:10+05:30"
T2 = "2026-09-06T08:00:20+05:30"
T3 = "2026-09-06T08:00:30+05:30"
T_HOUR = "2026-09-06T09:00:00+05:30"
T_HOUR2 = "2026-09-06T09:00:10+05:30"


def test_same_vehicle_across_two_cameras():
    matcher = CrossCameraMatcher()
    tracks = [
        _track("C01", 1, T0, T1, embedding=SAME_VEC),
        _track("C02", 3, T2, T3, embedding=SAME_VEC),
    ]
    result = matcher.match(tracks)
    ids = {row["vehicle_id"] for row in result["tracks"]}

    assert len(result["tracks"]) == 2
    assert len(ids) == 1
    assert result["tracks"][0]["local_track_id"] == 1
    assert result["tracks"][1]["local_track_id"] == 3
    assert result["tracks"][0]["camera_id"] == "C01"
    assert result["tracks"][1]["camera_id"] == "C02"
    assert result["matches"][0]["match_score"]["accepted"] is True
    assert result["tracks"][0]["vehicle_id"] == "V001"


def test_same_camera_cannot_merge():
    matcher = CrossCameraMatcher()
    tracks = [
        _track("C01", 1, T0, T1, embedding=SAME_VEC),
        _track("C01", 2, T2, T3, embedding=SAME_VEC),
    ]
    result = matcher.match(tracks)
    score = matcher.score_pair(tracks[0], tracks[1])

    assert score["accepted"] is False
    assert score["reject_reason"] == "same_camera"
    assert result["tracks"][0]["vehicle_id"] != result["tracks"][1]["vehicle_id"]
    assert result["matches"] == []


def test_missing_embeddings():
    matcher = CrossCameraMatcher()
    tracks = [
        _track("C01", 1, T0, T1, embedding=None),
        _track("C02", 1, T2, T3),
    ]
    result = matcher.match(tracks)
    score = matcher.score_pair(tracks[0], tracks[1])

    assert score["accepted"] is False
    assert score["reject_reason"] == "insufficient_cues"
    assert "missing_embedding" in score["missing"]
    assert result["tracks"][0]["vehicle_id"] != result["tracks"][1]["vehicle_id"]


def test_excessive_time_gap():
    matcher = CrossCameraMatcher()
    tracks = [
        _track("C01", 1, T0, T1, embedding=SAME_VEC),
        _track("C02", 1, T_HOUR, T_HOUR2, embedding=SAME_VEC),
    ]
    score = matcher.score_pair(tracks[0], tracks[1])
    result = matcher.match(tracks)

    assert score["accepted"] is False
    assert score["reject_reason"] == "time_gap"
    assert result["tracks"][0]["vehicle_id"] != result["tracks"][1]["vehicle_id"]


def test_spatial_infeasibility():
    matcher = CrossCameraMatcher(
        camera_links={("C01", "C02"): {"min_seconds": 5, "max_seconds": 20}}
    )
    tracks = [
        _track("C01", 1, T0, T1, embedding=SAME_VEC),
        _track("C02", 1, "2026-09-06T08:01:40+05:30", "2026-09-06T08:01:50+05:30", embedding=SAME_VEC),
    ]
    # last C01 is 08:00:10, first C02 is 08:01:40 → gap 90s, window 5–20s
    score = matcher.score_pair(tracks[0], tracks[1])
    result = matcher.match(tracks)

    assert score["reject_reason"] == "spatial_infeasible"
    assert score["accepted"] is False
    assert result["tracks"][0]["vehicle_id"] != result["tracks"][1]["vehicle_id"]


def test_optional_plate():
    matcher = CrossCameraMatcher()
    tracks = [
        _track("C01", 1, T0, T1, embedding=SAME_VEC, plate_text="DL01AB1234"),
        _track("C02", 2, T2, T3, embedding=SAME_VEC, plate_text=None),
    ]
    score = matcher.score_pair(tracks[0], tracks[1])
    result = matcher.match(tracks)

    assert score["accepted"] is True
    assert score["plate"] is None
    assert "missing_plate" in score["missing"]
    assert result["tracks"][0]["vehicle_id"] == result["tracks"][1]["vehicle_id"]


def test_plate_mismatch_veto():
    matcher = CrossCameraMatcher()
    tracks = [
        _track("C01", 1, T0, T1, embedding=SAME_VEC, plate_text="DL01AB1234"),
        _track("C02", 2, T2, T3, embedding=SAME_VEC, plate_text="MH02CD9999"),
    ]
    score = matcher.score_pair(tracks[0], tracks[1])
    result = matcher.match(tracks)

    assert score["accepted"] is False
    assert score["reject_reason"] == "plate_mismatch"
    assert score["verification_eligible"] is True
    assert result["tracks"][0]["vehicle_id"] != result["tracks"][1]["vehicle_id"]
    assert len(result["verification_candidates"]) == 1
    candidate = result["verification_candidates"][0]
    assert candidate["event"]["plate"] == "DL01AB1234"
    assert candidate["supporting_event"]["plate"] == "MH02CD9999"


def test_invalid_input():
    matcher = CrossCameraMatcher()
    none_result = matcher.match(None)
    assert none_result["tracks"] == []
    assert none_result["matches"] == []
    assert "error" in none_result

    mixed = matcher.match(
        [
            _track("C01", 1, T0, T1, embedding=SAME_VEC),
            {"camera_id": "C02", "first_timestamp": T2, "last_timestamp": T3},
            "bad",
        ]
    )
    valid_rows = [row for row in mixed["tracks"] if row.get("local_track_id") is not None]
    skipped = [row for row in mixed["tracks"] if row.get("vehicle_id") is None]
    assert len(valid_rows) == 1
    assert valid_rows[0]["vehicle_id"] == "V001"
    assert skipped[0]["camera_id"] == "C02"


def test_transitivity_assigns_same_vehicle_id():
    matcher = CrossCameraMatcher()
    tracks = [
        _track("C01", 1, T0, T1, embedding=SAME_VEC),
        _track("C02", 1, T2, T3, embedding=SAME_VEC),
        _track("C03", 1, "2026-09-06T08:00:40+05:30", "2026-09-06T08:00:50+05:30", embedding=SAME_VEC),
    ]
    result = matcher.match(tracks)
    ids = {row["vehicle_id"] for row in result["tracks"]}
    assert ids == {"V001"}
    assert len(result["matches"]) >= 2


def test_member2_ocr_field_names_are_accepted():
    matcher = CrossCameraMatcher()
    tracks = [
        _track("C01", 1, T0, T1, embedding=SAME_VEC, plate_text=None),
        _track("C02", 2, T2, T3, embedding=SAME_VEC),
    ]
    tracks[0]["plate"] = "DL01AB1234"
    tracks[0]["confidence"] = 0.61
    tracks[1]["plate"] = "DL01AB1234"
    tracks[1]["confidence"] = 0.95

    score = matcher.score_pair(tracks[0], tracks[1])
    assert score["accepted"] is True
    assert score["plate"] == 1.0
