"""Synthetic tests for trajectory reconstruction."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai.tracking.reconstruct import TrajectoryReconstructor, reconstruct


def _obs(
    vehicle_id,
    camera_id,
    local_track_id,
    first,
    last,
    **extra,
):
    row = {
        "vehicle_id": vehicle_id,
        "camera_id": camera_id,
        "local_track_id": local_track_id,
        "first_timestamp": first,
        "last_timestamp": last,
        "source": "real",
    }
    row.update(extra)
    return row


T0 = "2026-09-06T08:00:00+05:30"
T1 = "2026-09-06T08:00:10+05:30"
T2 = "2026-09-06T08:00:20+05:30"
T3 = "2026-09-06T08:00:30+05:30"


def test_two_camera_journey_preserves_local_track_ids():
    result = reconstruct(
        {
            "tracks": [
                _obs("V001", "C01", 1, T0, T1, road_segment_id="SEG_A1"),
                _obs("V001", "C02", 3, T2, T3, road_segment_id="SEG_B2"),
            ],
            "matches": [],
        }
    )
    traj = result["trajectories"][0]
    assert traj["vehicle_id"] == "V001"
    assert traj["trajectory_id"] == "T001"
    assert traj["camera_sequence"] == ["C01", "C02"]
    assert traj["observation_count"] == 2
    assert traj["observations"][0]["local_track_id"] == 1
    assert traj["observations"][1]["local_track_id"] == 3
    assert len(traj["legs"]) == 1
    assert traj["legs"][0]["status"] == "consecutive"
    assert traj["gap_count"] == 0


def test_chronological_sort_when_input_is_reversed():
    result = reconstruct(
        [
            _obs("V001", "C02", 3, T2, T3),
            _obs("V001", "C01", 1, T0, T1),
        ]
    )
    cameras = [obs["camera_id"] for obs in result["trajectories"][0]["observations"]]
    assert cameras == ["C01", "C02"]


def test_single_observation_still_builds_a_trajectory():
    result = reconstruct([_obs("V002", "C01", 4, T0, T1, match_score=None)])
    traj = result["trajectories"][0]
    assert traj["vehicle_id"] == "V002"
    assert traj["trajectory_id"] == "T001"
    assert traj["observation_count"] == 1
    assert traj["legs"] == []
    assert traj["gap_count"] == 0
    assert traj["camera_sequence"] == ["C01"]


def test_two_vehicles_get_stable_trajectory_ids_in_first_seen_order():
    result = reconstruct(
        [
            _obs("V001", "C01", 1, T0, T1),
            _obs("V002", "C02", 1, T2, T3),
        ]
    )
    ids = [(t["vehicle_id"], t["trajectory_id"]) for t in result["trajectories"]]
    assert ids == [("V001", "T001"), ("V002", "T002")]
    assert result["trajectories"][0]["observations"][0]["camera_id"] == "C01"
    assert result["trajectories"][1]["observations"][0]["camera_id"] == "C02"


def test_invalid_input_does_not_raise():
    reconstructor = TrajectoryReconstructor()
    none_result = reconstructor.reconstruct(None)
    assert none_result["trajectories"] == []
    assert none_result["skipped"] == []
    assert "error" in none_result

    mixed = reconstruct(
        [
            _obs("V001", "C01", 1, T0, T1),
            {"camera_id": "C02", "local_track_id": 2, "first_timestamp": T2},
            {"vehicle_id": "V003", "camera_id": "C03", "local_track_id": 1},
            "bad",
        ]
    )
    assert len(mixed["trajectories"]) == 1
    assert mixed["trajectories"][0]["vehicle_id"] == "V001"
    skipped_ids = [row.get("camera_id") for row in mixed["skipped"]]
    assert "C02" in skipped_ids
    assert "C03" in skipped_ids


def test_duplicate_observation_kept_once():
    result = reconstruct(
        [
            _obs("V001", "C01", 1, T0, T1, road_segment_id="SEG_A1"),
            _obs("V001", "C01", 1, T0, T1, road_segment_id="SEG_A1"),
            _obs("V001", "C02", 2, T2, T3),
        ]
    )
    traj = result["trajectories"][0]
    assert traj["observation_count"] == 2
    keys = [(o["camera_id"], o["local_track_id"]) for o in traj["observations"]]
    assert keys == [("C01", 1), ("C02", 2)]


def test_large_gap_is_marked_without_inventing_cameras():
    later_first = "2026-09-06T08:03:30+05:30"
    later_last = "2026-09-06T08:03:40+05:30"
    result = reconstruct(
        [
            _obs("V001", "C01", 1, T0, T1),
            _obs("V001", "C03", 1, later_first, later_last),
        ],
        gap_threshold=120.0,
    )
    traj = result["trajectories"][0]
    assert traj["observation_count"] == 2
    assert traj["camera_sequence"] == ["C01", "C03"]
    assert traj["gap_count"] == 1
    assert traj["legs"][0]["status"] == "gap"
    assert traj["legs"][0]["gap_seconds"] == 200.0


def test_road_and_direction_passthrough():
    agreed = reconstruct(
        [
            _obs("V001", "C01", 1, T0, T1, road_segment_id="SEG_A1", direction="NB"),
            _obs("V001", "C02", 2, T2, T3, road_segment_id="SEG_B2", direction="NB"),
        ]
    )
    traj = agreed["trajectories"][0]
    assert traj["road_sequence"] == ["SEG_A1", "SEG_B2"]
    assert traj["direction_sequence"] == ["NB"]
    assert traj["direction"] == "NB"

    conflicted = reconstruct(
        [
            _obs("V001", "C01", 1, T0, T1, road_segment_id="SEG_A1", direction="NB"),
            _obs("V001", "C02", 2, T2, T3, road_segment_id="SEG_A1", direction="EB"),
        ]
    )
    other = conflicted["trajectories"][0]
    assert other["road_sequence"] == ["SEG_A1"]
    assert other["direction_sequence"] == ["NB", "EB"]
    assert other["direction"] is None


def test_shuffled_observations_across_multiple_vehicles():
    result = reconstruct(
        [
            _obs("V002", "C03", 9, T2, T3),
            _obs("V001", "C02", 2, T2, T3),
            _obs("V002", "C01", 8, T0, T1),
            _obs("V001", "C01", 1, T0, T1),
        ]
    )
    by_vehicle = {t["vehicle_id"]: t for t in result["trajectories"]}
    assert [t["vehicle_id"] for t in result["trajectories"]] == ["V002", "V001"]
    assert by_vehicle["V002"]["trajectory_id"] == "T001"
    assert by_vehicle["V001"]["trajectory_id"] == "T002"
    assert by_vehicle["V001"]["camera_sequence"] == ["C01", "C02"]
    assert by_vehicle["V002"]["camera_sequence"] == ["C01", "C03"]


def test_deterministic_order_when_timestamps_are_identical():
    same = T0
    result = reconstruct(
        [
            _obs("V001", "C02", 2, same, same),
            _obs("V001", "C01", 5, same, same),
            _obs("V001", "C01", 1, same, same),
        ]
    )
    keys = [(o["camera_id"], o["local_track_id"]) for o in result["trajectories"][0]["observations"]]
    assert keys == [("C01", 1), ("C01", 5), ("C02", 2)]
    again = reconstruct(
        [
            _obs("V001", "C02", 2, same, same),
            _obs("V001", "C01", 5, same, same),
            _obs("V001", "C01", 1, same, same),
        ]
    )
    assert again == result
