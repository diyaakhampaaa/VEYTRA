"""Traffic density from vehicle camera sightings.

Density is the number of distinct vehicles in a group, plus the raw
sighting count so repeated detections remain visible.

Time bins are half-open: [interval_start, interval_end).
An event at 08:15 belongs to the next 15-minute window, not the previous one.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

import pandas as pd

from analytics.config import PANDAS_FLOOR_FREQ, WINDOW_DURATION, normalize_window
from analytics.io import load_vehicle_events

COUNT_COLUMNS = ("unique_vehicles", "sightings")


def _empty_frame(columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=columns)


def _counts(grouped) -> pd.DataFrame:
    return grouped.agg(
        unique_vehicles=("vehicle_id", "nunique"),
        sightings=("vehicle_id", "size"),
    ).reset_index()


def _add_time_bins(events: pd.DataFrame, window: str) -> pd.DataFrame:
    freq = PANDAS_FLOOR_FREQ[window]
    duration = WINDOW_DURATION[window]
    out = events.copy()
    out["interval_start"] = out["timestamp"].dt.floor(freq)
    out["interval_end"] = out["interval_start"] + pd.Timedelta(duration)
    return out


def vehicles_per_camera(events: pd.DataFrame) -> pd.DataFrame:
    """Unique vehicles and sightings grouped by camera (full sample)."""
    if events.empty:
        return _empty_frame(["camera_id", *COUNT_COLUMNS])
    result = _counts(events.groupby("camera_id", dropna=False))
    return result.sort_values("camera_id").reset_index(drop=True)


def vehicles_per_segment(events: pd.DataFrame) -> pd.DataFrame:
    """Unique vehicles and sightings grouped by road segment (full sample)."""
    columns = ["road_segment_id", "road_name", *COUNT_COLUMNS]
    if events.empty:
        return _empty_frame(columns)

    work = events.copy()
    if "road_name" not in work.columns:
        work["road_name"] = work["road_segment_id"]

    result = (
        work.groupby("road_segment_id", dropna=False)
        .agg(
            road_name=("road_name", "first"),
            unique_vehicles=("vehicle_id", "nunique"),
            sightings=("vehicle_id", "size"),
        )
        .reset_index()
    )
    return result.sort_values("road_segment_id").reset_index(drop=True)


def vehicles_per_time_interval(events: pd.DataFrame, window: str) -> pd.DataFrame:
    """Unique vehicles and sightings grouped by time window only."""
    columns = ["interval_start", "interval_end", *COUNT_COLUMNS]
    if events.empty:
        return _empty_frame(columns)
    binned = _add_time_bins(events, window)
    result = _counts(binned.groupby(["interval_start", "interval_end"], dropna=False))
    return result.sort_values("interval_start").reset_index(drop=True)


def vehicles_per_camera_time(events: pd.DataFrame, window: str) -> pd.DataFrame:
    """Unique vehicles and sightings grouped by camera and time window."""
    columns = ["camera_id", "interval_start", "interval_end", *COUNT_COLUMNS]
    if events.empty:
        return _empty_frame(columns)
    binned = _add_time_bins(events, window)
    result = _counts(
        binned.groupby(["camera_id", "interval_start", "interval_end"], dropna=False)
    )
    return result.sort_values(["interval_start", "camera_id"]).reset_index(drop=True)


def vehicles_per_segment_time(events: pd.DataFrame, window: str) -> pd.DataFrame:
    """Unique vehicles and sightings grouped by road segment and time window."""
    columns = [
        "road_segment_id",
        "road_name",
        "interval_start",
        "interval_end",
        *COUNT_COLUMNS,
    ]
    if events.empty:
        return _empty_frame(columns)

    binned = _add_time_bins(events, window)
    if "road_name" not in binned.columns:
        binned["road_name"] = binned["road_segment_id"]

    result = (
        binned.groupby(["road_segment_id", "interval_start", "interval_end"], dropna=False)
        .agg(
            road_name=("road_name", "first"),
            unique_vehicles=("vehicle_id", "nunique"),
            sightings=("vehicle_id", "size"),
        )
        .reset_index()
    )
    return result[
        ["road_segment_id", "road_name", "interval_start", "interval_end", *COUNT_COLUMNS]
    ].sort_values(["interval_start", "road_segment_id"]).reset_index(drop=True)


def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
    """JSON-compatible rows (timestamps as ISO-8601 strings)."""
    if df.empty:
        return []
    serialized = df.copy()
    for column in serialized.columns:
        if pd.api.types.is_datetime64_any_dtype(serialized[column]):
            serialized[column] = serialized[column].dt.strftime("%Y-%m-%dT%H:%M:%S%z")
            serialized[column] = serialized[column].str.replace(
                r"(\d{2})(\d{2})$", r"\1:\2", regex=True
            )
        elif pd.api.types.is_integer_dtype(serialized[column]):
            serialized[column] = serialized[column].astype(int)
    return serialized.to_dict(orient="records")


def compute_density(
    events: pd.DataFrame,
    window: str | int = "15min",
    as_json: bool = False,
) -> dict[str, Any]:
    """Compute traffic density tables for one time window.

    Returns a dict of DataFrames by default. Set as_json=True for
    JSON-compatible lists of dictionaries.
    """
    canonical = normalize_window(window)
    payload = {
        "window": canonical,
        "by_camera": vehicles_per_camera(events),
        "by_segment": vehicles_per_segment(events),
        "by_time": vehicles_per_time_interval(events, canonical),
        "by_camera_time": vehicles_per_camera_time(events, canonical),
        "by_segment_time": vehicles_per_segment_time(events, canonical),
    }
    if as_json:
        return {
            "window": canonical,
            **{key: _records(value) for key, value in payload.items() if key != "window"},
        }
    return payload


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute traffic density from sample vehicle events.")
    parser.add_argument(
        "--window",
        default="15min",
        help="Time window: 5min, 15min, or 1h (default: 15min).",
    )
    parser.add_argument(
        "--csv",
        default=None,
        help="Path to vehicle events CSV (default: analytics/data/sample_vehicle_events.csv).",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    events = load_vehicle_events(args.csv)
    result = compute_density(events, window=args.window, as_json=True)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
