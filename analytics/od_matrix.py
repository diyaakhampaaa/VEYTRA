"""Origin-Destination matrix from vehicle trajectories.

An OD matrix counts how many vehicles travel from an origin
camera/road segment to a destination camera/road segment.

The first valid observation in a trajectory is treated as the origin.
The last valid observation is treated as the destination.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

import pandas as pd

from analytics.io import load_vehicle_events

OD_COLUMNS = [
    "origin_camera_id",
    "destination_camera_id",
    "origin_segment_id",
    "destination_segment_id",
    "vehicle_count",
]

TRAJECTORY_COLUMNS = [
    "vehicle_id",
    "trajectory_id",
    "origin_camera_id",
    "destination_camera_id",
    "origin_segment_id",
    "destination_segment_id",
    "origin_timestamp",
    "destination_timestamp",
]


def _empty_frame(columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=columns)


def _prepare(events: pd.DataFrame) -> pd.DataFrame:
    work = events.copy()

    if "trajectory_id" not in work.columns:
        work["trajectory_id"] = work["vehicle_id"]

    if "camera_id" not in work.columns:
        work["camera_id"] = pd.NA

    if "road_segment_id" not in work.columns:
        work["road_segment_id"] = pd.NA

    work["timestamp"] = pd.to_datetime(
        work["timestamp"],
        errors="coerce",
    )

    return work.sort_values(
        ["vehicle_id", "trajectory_id", "timestamp"],
        na_position="last",
    ).reset_index(drop=True)


def build_trajectories(events: pd.DataFrame) -> pd.DataFrame:
    """Create one origin-destination record for every vehicle trajectory."""
    if events.empty:
        return _empty_frame(TRAJECTORY_COLUMNS)

    work = _prepare(events)
    rows: list[dict[str, Any]] = []

    grouped = work.groupby(
        ["vehicle_id", "trajectory_id"],
        dropna=False,
        sort=False,
    )

    for (vehicle_id, trajectory_id), group in grouped:
        group = group.dropna(subset=["timestamp"])

        if group.empty:
            continue

        first = group.iloc[0]
        last = group.iloc[-1]

        rows.append(
            {
                "vehicle_id": vehicle_id,
                "trajectory_id": trajectory_id,
                "origin_camera_id": first["camera_id"],
                "destination_camera_id": last["camera_id"],
                "origin_segment_id": first["road_segment_id"],
                "destination_segment_id": last["road_segment_id"],
                "origin_timestamp": first["timestamp"],
                "destination_timestamp": last["timestamp"],
            }
        )

    if not rows:
        return _empty_frame(TRAJECTORY_COLUMNS)

    return pd.DataFrame(rows, columns=TRAJECTORY_COLUMNS)


def compute_od_matrix(
    events: pd.DataFrame,
    exclude_same_location: bool = True,
    as_json: bool = False,
) -> dict[str, Any]:
    """Compute an origin-destination matrix from vehicle trajectories."""
    trajectories = build_trajectories(events)

    if trajectories.empty:
        matrix = _empty_frame(OD_COLUMNS)
    else:
        work = trajectories.copy()

        if exclude_same_location:
            same_camera = (
                work["origin_camera_id"].notna()
                & work["destination_camera_id"].notna()
                & (
                    work["origin_camera_id"]
                    == work["destination_camera_id"]
                )
            )

            same_segment = (
                work["origin_segment_id"].notna()
                & work["destination_segment_id"].notna()
                & (
                    work["origin_segment_id"]
                    == work["destination_segment_id"]
                )
            )

            work = work[~(same_camera & same_segment)]

        matrix = (
            work.groupby(
                [
                    "origin_camera_id",
                    "destination_camera_id",
                    "origin_segment_id",
                    "destination_segment_id",
                ],
                dropna=False,
            )
            .size()
            .reset_index(name="vehicle_count")
            .sort_values(
                [
                    "origin_camera_id",
                    "destination_camera_id",
                    "origin_segment_id",
                    "destination_segment_id",
                ]
            )
            .reset_index(drop=True)
        )

    if as_json:
        return {
            "by_trajectory": _records(trajectories),
            "od_matrix": _records(matrix),
        }

    return {
        "by_trajectory": trajectories,
        "od_matrix": matrix,
    }


def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert a DataFrame into JSON-compatible records."""
    if df.empty:
        return []

    serialized = df.copy()

    for column in serialized.columns:
        if pd.api.types.is_datetime64_any_dtype(serialized[column]):
            serialized[column] = serialized[column].dt.strftime(
                "%Y-%m-%dT%H:%M:%S%z"
            )
            serialized[column] = serialized[column].str.replace(
                r"(\d{2})(\d{2})$",
                r"\1:\2",
                regex=True,
            )

    records = serialized.to_dict(orient="records")

    cleaned: list[dict[str, Any]] = []

    for record in records:
        cleaned.append(
            {
                key: (
                    None
                    if pd.isna(value)
                    else value.item()
                    if hasattr(value, "item")
                    else value
                )
                for key, value in record.items()
            }
        )

    return cleaned


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute origin-destination traffic matrix."
    )

    parser.add_argument(
        "--csv",
        default=None,
        help=(
            "Path to vehicle events CSV "
            "(default: analytics/data/sample_vehicle_events.csv)."
        ),
    )

    parser.add_argument(
        "--include-same-location",
        action="store_true",
        help="Include trajectories whose origin and destination are the same.",
    )

    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    events = load_vehicle_events(args.csv)

    result = compute_od_matrix(
        events,
        exclude_same_location=not args.include_same_location,
        as_json=True,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()