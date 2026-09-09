"""Density tests against the controlled sample CSV."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analytics.density import compute_density, vehicles_per_camera, vehicles_per_segment
from analytics.io import load_vehicle_events


def _row(df: pd.DataFrame, **equals) -> pd.Series:
    mask = pd.Series(True, index=df.index)
    for column, value in equals.items():
        mask &= df[column] == value
    matched = df.loc[mask]
    assert len(matched) == 1, f"expected one row for {equals}, got {len(matched)}"
    return matched.iloc[0]


@pytest.fixture(scope="module")
def events() -> pd.DataFrame:
    return load_vehicle_events()


def test_sample_has_required_identity_and_location_fields(events: pd.DataFrame) -> None:
    required = {
        "vehicle_id",
        "plate_number",
        "camera_id",
        "timestamp",
        "latitude",
        "longitude",
        "direction",
        "road_segment_id",
        "trajectory_id",
    }
    assert required.issubset(events.columns)
    assert len(events) == 16


def test_repeat_sightings_count_once_per_camera(events: pd.DataFrame) -> None:
    by_camera = vehicles_per_camera(events)
    cam01 = _row(by_camera, camera_id="CAM_01")
    cam02 = _row(by_camera, camera_id="CAM_02")
    cam03 = _row(by_camera, camera_id="CAM_03")

    # V001 appears twice at CAM_01 at 08:03 and 08:04; still one unique vehicle.
    assert int(cam01["unique_vehicles"]) == 4
    assert int(cam01["sightings"]) == 7
    assert int(cam02["unique_vehicles"]) == 4
    assert int(cam02["sightings"]) == 5
    assert int(cam03["unique_vehicles"]) == 3
    assert int(cam03["sightings"]) == 4


def test_vehicles_per_road_segment(events: pd.DataFrame) -> None:
    by_segment = vehicles_per_segment(events)
    a1 = _row(by_segment, road_segment_id="SEG_A1")
    b2 = _row(by_segment, road_segment_id="SEG_B2")
    c3 = _row(by_segment, road_segment_id="SEG_C3")

    assert a1["road_name"] == "Ring Road"
    assert int(a1["unique_vehicles"]) == 3
    assert int(a1["sightings"]) == 6
    assert int(b2["unique_vehicles"]) == 4
    assert int(b2["sightings"]) == 6
    assert int(c3["unique_vehicles"]) == 3
    assert int(c3["sightings"]) == 4


def test_5_minute_windows_split_close_timestamps(events: pd.DataFrame) -> None:
    result = compute_density(events, window="5min")
    by_time = result["by_time"]

    first = _row(by_time, interval_start=pd.Timestamp("2026-09-06T08:00:00+05:30"))
    second = _row(by_time, interval_start=pd.Timestamp("2026-09-06T08:05:00+05:30"))

    # 08:03 and 08:04 IST are one unique vehicle (V001) in the first 5-minute bin.
    assert int(first["unique_vehicles"]) == 1
    assert int(first["sightings"]) == 2
    # 08:06 V002 and 08:07 V003 fall in the next bin.
    assert int(second["unique_vehicles"]) == 2
    assert int(second["sightings"]) == 2


def test_15_minute_window_groups_the_morning_peak(events: pd.DataFrame) -> None:
    result = compute_density(events, window="15min", as_json=True)
    by_time = result["by_time"]
    first = next(row for row in by_time if row["interval_start"].startswith("2026-09-06T08:00:00"))

    assert result["window"] == "15min"
    assert first["unique_vehicles"] == 4
    assert first["sightings"] == 7
    assert first["interval_end"].startswith("2026-09-06T08:15:00")


def test_1_hour_windows(events: pd.DataFrame) -> None:
    result = compute_density(events, window="1h")
    by_time = result["by_time"]
    hour_8 = _row(by_time, interval_start=pd.Timestamp("2026-09-06T08:00:00+05:30"))
    hour_9 = _row(by_time, interval_start=pd.Timestamp("2026-09-06T09:00:00+05:30"))

    assert int(hour_8["unique_vehicles"]) == 5
    assert int(hour_8["sightings"]) == 12
    assert int(hour_9["unique_vehicles"]) == 4
    assert int(hour_9["sightings"]) == 4


def test_window_aliases(events: pd.DataFrame) -> None:
    assert compute_density(events, window=5)["window"] == "5min"
    assert compute_density(events, window="60")["window"] == "1h"


def test_invalid_window_raises(events: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="Unsupported time window"):
        compute_density(events, window="2h")


def test_empty_input_returns_empty_tables() -> None:
    empty = pd.DataFrame(
        columns=["vehicle_id", "camera_id", "timestamp", "road_segment_id", "road_name"]
    )
    result = compute_density(empty, window="15min", as_json=True)
    assert result["by_camera"] == []
    assert result["by_segment"] == []
    assert result["by_time"] == []
    assert result["by_camera_time"] == []
    assert result["by_segment_time"] == []


def test_half_open_bins_do_not_include_boundary_in_previous_window(events: pd.DataFrame) -> None:
    """08:15 IST would start a new 15-minute bin; 08:16 is already in 08:15-08:30."""
    result = compute_density(events, window="15min")
    second = _row(result["by_time"], interval_start=pd.Timestamp("2026-09-06T08:15:00+05:30"))
    assert int(second["sightings"]) == 3
    assert int(second["unique_vehicles"]) == 3
