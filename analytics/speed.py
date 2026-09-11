"""Estimated traffic speed from vehicle trajectories.

Speed is never copied from stored camera fields. It is estimated as:

    estimated_speed_kmh = distance_km / travel_time_hours

Distance is the haversine length of consecutive valid (lat, lon) points.
Travel time comes from timestamps. Results are labeled as estimated.
Insufficient trajectories return null speed rather than a substitute value.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

import numpy as np
import pandas as pd

from analytics.io import load_vehicle_events

EARTH_RADIUS_KM = 6371.0
SPEED_TYPE_ESTIMATED = "estimated"
STATUS_OK = "ok"
STATUS_INSUFFICIENT = "insufficient_data"

REASON_TOO_FEW_POINTS = "too_few_points"
REASON_MISSING_COORDINATES = "missing_coordinates"
REASON_NON_POSITIVE_TIME = "non_positive_travel_time"

LEG_COLUMNS = [
    "vehicle_id",
    "trajectory_id",
    "from_event_id",
    "to_event_id",
    "from_camera_id",
    "to_camera_id",
    "from_timestamp",
    "to_timestamp",
    "distance_km",
    "travel_time_seconds",
    "estimated_speed_kmh",
    "speed_type",
    "status",
    "reason",
]

TRAJECTORY_COLUMNS = [
    "vehicle_id",
    "trajectory_id",
    "point_count",
    "valid_point_count",
    "distance_km",
    "travel_time_seconds",
    "estimated_speed_kmh",
    "speed_type",
    "status",
    "reason",
]


def haversine_km(
    lat1: np.ndarray | float,
    lon1: np.ndarray | float,
    lat2: np.ndarray | float,
    lon2: np.ndarray | float,
) -> np.ndarray | float:
    """Great-circle distance in kilometres (WGS84 sphere, radius 6371 km)."""
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    d_phi = np.radians(lat2 - lat1)
    d_lambda = np.radians(lon2 - lon1)
    a = np.sin(d_phi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(d_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def _empty_frame(columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=columns)


def _has_column(events: pd.DataFrame, name: str) -> bool:
    return name in events.columns


def _prepare(events: pd.DataFrame) -> pd.DataFrame:
    work = events.copy()
    if not _has_column(work, "trajectory_id"):
        work["trajectory_id"] = work["vehicle_id"]
    if not _has_column(work, "event_id"):
        work["event_id"] = pd.RangeIndex(start=1, stop=len(work) + 1).astype(str)
    if not _has_column(work, "camera_id"):
        work["camera_id"] = pd.NA

    work["timestamp"] = pd.to_datetime(work["timestamp"], errors="coerce")
    work["latitude"] = pd.to_numeric(work["latitude"], errors="coerce")
    work["longitude"] = pd.to_numeric(work["longitude"], errors="coerce")
    work["coords_valid"] = (
        work["latitude"].notna()
        & work["longitude"].notna()
        & work["latitude"].between(-90, 90)
        & work["longitude"].between(-180, 180)
        & work["timestamp"].notna()
    )
    return work.sort_values(["vehicle_id", "trajectory_id", "timestamp", "event_id"]).reset_index(
        drop=True
    )


def _speed_from_distance_time(distance_km: float, travel_time_seconds: float) -> tuple[float | None, str, str | None]:
    if travel_time_seconds <= 0:
        return None, STATUS_INSUFFICIENT, REASON_NON_POSITIVE_TIME
    hours = travel_time_seconds / 3600.0
    return float(distance_km / hours), STATUS_OK, None


def speed_by_leg(events: pd.DataFrame) -> pd.DataFrame:
    """Estimated speed between consecutive sightings on each trajectory."""
    if events.empty:
        return _empty_frame(LEG_COLUMNS)

    work = _prepare(events)
    rows: list[dict[str, Any]] = []
    grouped = work.groupby(["vehicle_id", "trajectory_id"], dropna=False, sort=False)

    for (vehicle_id, trajectory_id), group in grouped:
        ordered = group.reset_index(drop=True)
        for i in range(len(ordered) - 1):
            start = ordered.iloc[i]
            end = ordered.iloc[i + 1]
            row: dict[str, Any] = {
                "vehicle_id": vehicle_id,
                "trajectory_id": trajectory_id,
                "from_event_id": start["event_id"],
                "to_event_id": end["event_id"],
                "from_camera_id": start["camera_id"],
                "to_camera_id": end["camera_id"],
                "from_timestamp": start["timestamp"],
                "to_timestamp": end["timestamp"],
                "distance_km": np.nan,
                "travel_time_seconds": np.nan,
                "estimated_speed_kmh": np.nan,
                "speed_type": SPEED_TYPE_ESTIMATED,
                "status": STATUS_INSUFFICIENT,
                "reason": None,
            }

            if not bool(start["coords_valid"]) or not bool(end["coords_valid"]):
                row["reason"] = REASON_MISSING_COORDINATES
                rows.append(row)
                continue

            distance = float(
                haversine_km(
                    start["latitude"],
                    start["longitude"],
                    end["latitude"],
                    end["longitude"],
                )
            )
            travel_time = (end["timestamp"] - start["timestamp"]).total_seconds()
            speed, status, reason = _speed_from_distance_time(distance, travel_time)
            row["distance_km"] = distance
            row["travel_time_seconds"] = travel_time
            row["estimated_speed_kmh"] = speed if speed is not None else np.nan
            row["status"] = status
            row["reason"] = reason
            rows.append(row)

    if not rows:
        return _empty_frame(LEG_COLUMNS)
    return pd.DataFrame(rows, columns=LEG_COLUMNS)


def speed_by_trajectory(events: pd.DataFrame) -> pd.DataFrame:
    """Estimated speed over each full vehicle trajectory.

    Invalid coordinates or timestamps fail the whole trajectory. Remaining
    valid points are not joined across the gap.
    """
    if events.empty:
        return _empty_frame(TRAJECTORY_COLUMNS)

    work = _prepare(events)
    rows: list[dict[str, Any]] = []

    for (vehicle_id, trajectory_id), group in work.groupby(
        ["vehicle_id", "trajectory_id"], dropna=False, sort=False
    ):
        ordered = group.reset_index(drop=True)
        point_count = int(len(ordered))
        valid_point_count = int(ordered["coords_valid"].sum())
        row: dict[str, Any] = {
            "vehicle_id": vehicle_id,
            "trajectory_id": trajectory_id,
            "point_count": point_count,
            "valid_point_count": valid_point_count,
            "distance_km": np.nan,
            "travel_time_seconds": np.nan,
            "estimated_speed_kmh": np.nan,
            "speed_type": SPEED_TYPE_ESTIMATED,
            "status": STATUS_INSUFFICIENT,
            "reason": None,
        }

        if point_count < 2:
            row["reason"] = REASON_TOO_FEW_POINTS
            rows.append(row)
            continue

        if not bool(ordered["coords_valid"].all()):
            row["reason"] = REASON_MISSING_COORDINATES
            rows.append(row)
            continue

        distances = haversine_km(
            ordered["latitude"].to_numpy()[:-1],
            ordered["longitude"].to_numpy()[:-1],
            ordered["latitude"].to_numpy()[1:],
            ordered["longitude"].to_numpy()[1:],
        )
        distance = float(np.sum(distances))
        travel_time = (
            ordered["timestamp"].iloc[-1] - ordered["timestamp"].iloc[0]
        ).total_seconds()
        speed, status, reason = _speed_from_distance_time(distance, travel_time)
        row["distance_km"] = distance
        row["travel_time_seconds"] = travel_time
        row["estimated_speed_kmh"] = speed if speed is not None else np.nan
        row["status"] = status
        row["reason"] = reason
        rows.append(row)

    return pd.DataFrame(rows, columns=TRAJECTORY_COLUMNS)


def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
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
            serialized[column] = serialized[column].astype("Int64")
    records = serialized.to_dict(orient="records")
    cleaned: list[dict[str, Any]] = []
    for record in records:
        cleaned.append(
            {
                key: (None if value is pd.NA or (isinstance(value, float) and np.isnan(value)) else value)
                for key, value in record.items()
            }
        )
    return cleaned


def compute_speed(events: pd.DataFrame, as_json: bool = False) -> dict[str, Any]:
    """Estimate trajectory and leg speeds.

    Returns DataFrames by default, or JSON-compatible dicts when as_json=True.
    """
    payload = {
        "speed_type": SPEED_TYPE_ESTIMATED,
        "by_leg": speed_by_leg(events),
        "by_trajectory": speed_by_trajectory(events),
    }
    if as_json:
        return {
            "speed_type": SPEED_TYPE_ESTIMATED,
            "by_leg": _records(payload["by_leg"]),
            "by_trajectory": _records(payload["by_trajectory"]),
        }
    return payload


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Estimate traffic speed from sample vehicle trajectories."
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
    print(json.dumps(compute_speed(events, as_json=True), indent=2))


if __name__ == "__main__":
    main()
