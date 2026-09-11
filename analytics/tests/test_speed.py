"""Speed tests on synthetic rows and the controlled sample CSV."""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analytics.io import load_vehicle_events
from analytics.speed import (
    EARTH_RADIUS_KM,
    REASON_MISSING_COORDINATES,
    REASON_NON_POSITIVE_TIME,
    REASON_TOO_FEW_POINTS,
    SPEED_TYPE_ESTIMATED,
    STATUS_INSUFFICIENT,
    STATUS_OK,
    compute_speed,
    haversine_km,
    speed_by_trajectory,
)


def _events(rows: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(rows)


def test_haversine_one_degree_at_equator() -> None:
    expected = 2 * EARTH_RADIUS_KM * math.asin(math.sin(math.radians(1) / 2))
    assert haversine_km(0.0, 0.0, 0.0, 1.0) == pytest.approx(expected, rel=1e-9)
    assert haversine_km(0.0, 0.0, 0.0, 0.0) == pytest.approx(0.0)


def test_two_points_produce_estimated_speed_from_distance_over_time() -> None:
    events = _events(
        [
            {
                "event_id": "A",
                "vehicle_id": "VX",
                "trajectory_id": "TX",
                "camera_id": "CAM_A",
                "timestamp": "2026-09-06T08:00:00+05:30",
                "latitude": 0.0,
                "longitude": 0.0,
            },
            {
                "event_id": "B",
                "vehicle_id": "VX",
                "trajectory_id": "TX",
                "camera_id": "CAM_B",
                "timestamp": "2026-09-06T09:00:00+05:30",
                "latitude": 0.0,
                "longitude": 1.0,
            },
        ]
    )
    result = compute_speed(events)
    traj = result["by_trajectory"].iloc[0]
    distance = float(haversine_km(0.0, 0.0, 0.0, 1.0))

    assert traj["status"] == STATUS_OK
    assert traj["speed_type"] == SPEED_TYPE_ESTIMATED
    assert traj["travel_time_seconds"] == 3600.0
    assert traj["distance_km"] == pytest.approx(distance)
    assert traj["estimated_speed_kmh"] == pytest.approx(distance / 1.0)

    leg = result["by_leg"].iloc[0]
    assert leg["from_event_id"] == "A"
    assert leg["to_event_id"] == "B"
    assert leg["estimated_speed_kmh"] == pytest.approx(distance)


def test_does_not_copy_csv_speed_kmh_column() -> None:
    events = _events(
        [
            {
                "event_id": "A",
                "vehicle_id": "VX",
                "trajectory_id": "TX",
                "camera_id": "CAM_A",
                "timestamp": "2026-09-06T08:00:00+05:30",
                "latitude": 0.0,
                "longitude": 0.0,
                "speed_kmh": 99.9,
            },
            {
                "event_id": "B",
                "vehicle_id": "VX",
                "trajectory_id": "TX",
                "camera_id": "CAM_B",
                "timestamp": "2026-09-06T09:00:00+05:30",
                "latitude": 0.0,
                "longitude": 1.0,
                "speed_kmh": 99.9,
            },
        ]
    )
    estimated = compute_speed(events)["by_trajectory"].iloc[0]["estimated_speed_kmh"]
    assert estimated != pytest.approx(99.9)
    assert estimated == pytest.approx(float(haversine_km(0.0, 0.0, 0.0, 1.0)))


def test_single_point_is_insufficient() -> None:
    events = _events(
        [
            {
                "event_id": "A",
                "vehicle_id": "VX",
                "trajectory_id": "TX",
                "camera_id": "CAM_A",
                "timestamp": "2026-09-06T08:00:00+05:30",
                "latitude": 28.63,
                "longitude": 77.22,
            }
        ]
    )
    traj = speed_by_trajectory(events).iloc[0]
    assert traj["status"] == STATUS_INSUFFICIENT
    assert traj["reason"] == REASON_TOO_FEW_POINTS
    assert pd.isna(traj["estimated_speed_kmh"])
    assert compute_speed(events)["by_leg"].empty


def test_identical_timestamps_are_insufficient() -> None:
    events = _events(
        [
            {
                "event_id": "A",
                "vehicle_id": "VX",
                "trajectory_id": "TX",
                "camera_id": "CAM_A",
                "timestamp": "2026-09-06T08:00:00+05:30",
                "latitude": 0.0,
                "longitude": 0.0,
            },
            {
                "event_id": "B",
                "vehicle_id": "VX",
                "trajectory_id": "TX",
                "camera_id": "CAM_B",
                "timestamp": "2026-09-06T08:00:00+05:30",
                "latitude": 0.0,
                "longitude": 1.0,
            },
        ]
    )
    result = compute_speed(events)
    traj = result["by_trajectory"].iloc[0]
    leg = result["by_leg"].iloc[0]
    assert traj["status"] == STATUS_INSUFFICIENT
    assert traj["reason"] == REASON_NON_POSITIVE_TIME
    assert pd.isna(traj["estimated_speed_kmh"])
    assert leg["status"] == STATUS_INSUFFICIENT
    assert leg["reason"] == REASON_NON_POSITIVE_TIME
    assert pd.isna(leg["estimated_speed_kmh"])


def test_missing_coordinates_are_insufficient() -> None:
    events = _events(
        [
            {
                "event_id": "A",
                "vehicle_id": "VX",
                "trajectory_id": "TX",
                "camera_id": "CAM_A",
                "timestamp": "2026-09-06T08:00:00+05:30",
                "latitude": 28.63,
                "longitude": 77.22,
            },
            {
                "event_id": "B",
                "vehicle_id": "VX",
                "trajectory_id": "TX",
                "camera_id": "CAM_B",
                "timestamp": "2026-09-06T08:10:00+05:30",
                "latitude": None,
                "longitude": None,
            },
        ]
    )
    result = compute_speed(events)
    traj = result["by_trajectory"].iloc[0]
    leg = result["by_leg"].iloc[0]
    assert traj["status"] == STATUS_INSUFFICIENT
    assert traj["reason"] == REASON_MISSING_COORDINATES
    assert pd.isna(traj["estimated_speed_kmh"])
    assert leg["reason"] == REASON_MISSING_COORDINATES
    assert pd.isna(leg["estimated_speed_kmh"])


def test_trajectory_does_not_skip_invalid_middle_point() -> None:
    """A bad middle point must not be dropped so first and last are joined."""
    events = _events(
        [
            {
                "event_id": "A",
                "vehicle_id": "VX",
                "trajectory_id": "TX",
                "camera_id": "CAM_A",
                "timestamp": "2026-09-06T08:00:00+05:30",
                "latitude": 0.0,
                "longitude": 0.0,
            },
            {
                "event_id": "B",
                "vehicle_id": "VX",
                "trajectory_id": "TX",
                "camera_id": "CAM_B",
                "timestamp": "2026-09-06T08:30:00+05:30",
                "latitude": None,
                "longitude": None,
            },
            {
                "event_id": "C",
                "vehicle_id": "VX",
                "trajectory_id": "TX",
                "camera_id": "CAM_C",
                "timestamp": "2026-09-06T09:00:00+05:30",
                "latitude": 0.0,
                "longitude": 1.0,
            },
        ]
    )
    result = compute_speed(events)
    traj = result["by_trajectory"].iloc[0]
    skipped_distance = float(haversine_km(0.0, 0.0, 0.0, 1.0))
    skipped_speed = skipped_distance / 1.0

    assert traj["status"] == STATUS_INSUFFICIENT
    assert traj["reason"] == REASON_MISSING_COORDINATES
    assert pd.isna(traj["estimated_speed_kmh"])
    assert pd.isna(traj["distance_km"])
    assert traj["estimated_speed_kmh"] != pytest.approx(skipped_speed)

    legs = result["by_leg"]
    assert len(legs) == 2
    assert (legs["status"] == STATUS_INSUFFICIENT).all()
    assert (legs["reason"] == REASON_MISSING_COORDINATES).all()
    assert legs["estimated_speed_kmh"].isna().all()


def test_empty_input_returns_empty_tables() -> None:
    empty = pd.DataFrame(
        columns=["vehicle_id", "trajectory_id", "timestamp", "latitude", "longitude"]
    )
    result = compute_speed(empty, as_json=True)
    assert result["speed_type"] == SPEED_TYPE_ESTIMATED
    assert result["by_leg"] == []
    assert result["by_trajectory"] == []


def test_sample_trajectories_are_estimated_not_copied_from_csv() -> None:
    events = load_vehicle_events()
    result = compute_speed(events)
    traj = result["by_trajectory"]
    ok = traj[traj["status"] == STATUS_OK]

    assert not ok.empty
    assert (ok["speed_type"] == SPEED_TYPE_ESTIMATED).all()
    assert ok["estimated_speed_kmh"].notna().all()

    v001 = traj.loc[
        (traj["vehicle_id"] == "V001") & (traj["trajectory_id"] == "T001")
    ].iloc[0]
    csv_speeds = set(events.loc[events["vehicle_id"] == "V001", "speed_kmh"].tolist())
    assert v001["point_count"] == 4
    assert v001["status"] == STATUS_OK
    assert v001["estimated_speed_kmh"] not in csv_speeds
