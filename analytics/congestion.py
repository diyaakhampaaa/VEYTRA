"""Explainable traffic congestion scoring.

Congestion is calculated from:
- vehicle density
- estimated average speed

The score is configurable and is not presented as a scientifically
validated traffic model.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

import numpy as np
import pandas as pd

from analytics.density import compute_density
from analytics.io import load_vehicle_events
from analytics.speed import speed_by_trajectory

CONGESTION_COLUMNS = [
    "road_segment_id",
    "road_name",
    "interval_start",
    "interval_end",
    "vehicle_count",
    "average_speed_kmh",
    "density_score",
    "speed_score",
    "congestion_score",
    "congestion_level",
]

DEFAULT_DENSITY_THRESHOLD = 10.0
DEFAULT_SPEED_REFERENCE_KMH = 50.0
DEFAULT_DENSITY_WEIGHT = 0.5
DEFAULT_SPEED_WEIGHT = 0.5


def _empty_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=CONGESTION_COLUMNS)


def _clip_score(value: float) -> float:
    return float(np.clip(value, 0.0, 1.0))


def _congestion_level(score: float) -> str:
    if score < 0.25:
        return "low"
    if score < 0.50:
        return "moderate"
    if score < 0.75:
        return "high"
    return "severe"


def _prepare_events(events: pd.DataFrame) -> pd.DataFrame:
    """Normalize incoming vehicle events before analytics processing."""

    if events is None:
        return pd.DataFrame()

    work = events.copy()

    if work.empty:
        return work

    # API requests send timestamps as strings.
    # Convert them BEFORE any pandas .dt operations happen.
    if "timestamp" in work.columns:
        work["timestamp"] = pd.to_datetime(
            work["timestamp"],
            errors="coerce",
        )

        # Remove rows where timestamp could not be parsed.
        work = work.dropna(subset=["timestamp"]).copy()

    # Normalize common identifier columns.
    if "vehicle_id" in work.columns:
        work["vehicle_id"] = work["vehicle_id"].astype("string")

    if "camera_id" in work.columns:
        work["camera_id"] = work["camera_id"].astype("string")

    if "road_segment_id" in work.columns:
        work["road_segment_id"] = work["road_segment_id"].astype("string")

    return work


def _prepare_speed(events: pd.DataFrame) -> pd.DataFrame:
    """Calculate average valid speed per road segment."""

    if events.empty:
        return pd.DataFrame(
            columns=["road_segment_id", "average_speed_kmh"]
        )

    if "road_segment_id" not in events.columns:
        return pd.DataFrame(
            columns=["road_segment_id", "average_speed_kmh"]
        )

    work = events.copy()

    # If the event already contains an estimated/measured speed,
    # use it directly. This is the preferred API path.
    if "speed_kmh" in work.columns:
        work["speed_kmh"] = pd.to_numeric(
            work["speed_kmh"],
            errors="coerce",
        )

        valid = work.dropna(
            subset=["road_segment_id", "speed_kmh"]
        ).copy()

        if not valid.empty:
            return (
                valid.groupby("road_segment_id", dropna=False)
                .agg(
                    average_speed_kmh=("speed_kmh", "mean")
                )
                .reset_index()
            )

    # Otherwise fall back to the trajectory-based speed calculation.
    if "vehicle_id" not in work.columns:
        return pd.DataFrame(
            columns=["road_segment_id", "average_speed_kmh"]
        )

    if "trajectory_id" not in work.columns:
        work["trajectory_id"] = work["vehicle_id"]

    work["road_segment_id"] = work["road_segment_id"].astype("string")

    trajectory_speeds = speed_by_trajectory(work)

    if trajectory_speeds.empty:
        return pd.DataFrame(
            columns=["road_segment_id", "average_speed_kmh"]
        )

    if "status" in trajectory_speeds.columns:
        valid_speeds = trajectory_speeds[
            trajectory_speeds["status"] == "ok"
        ].copy()
    else:
        valid_speeds = trajectory_speeds.copy()

    if valid_speeds.empty:
        return pd.DataFrame(
            columns=["road_segment_id", "average_speed_kmh"]
        )

    required_columns = {
        "vehicle_id",
        "trajectory_id",
        "estimated_speed_kmh",
    }

    if not required_columns.issubset(valid_speeds.columns):
        return pd.DataFrame(
            columns=["road_segment_id", "average_speed_kmh"]
        )

    segment_speeds = (
        work[
            [
                "vehicle_id",
                "trajectory_id",
                "road_segment_id",
            ]
        ]
        .drop_duplicates()
        .merge(
            valid_speeds[
                [
                    "vehicle_id",
                    "trajectory_id",
                    "estimated_speed_kmh",
                ]
            ],
            on=["vehicle_id", "trajectory_id"],
            how="inner",
        )
    )

    if segment_speeds.empty:
        return pd.DataFrame(
            columns=["road_segment_id", "average_speed_kmh"]
        )

    return (
        segment_speeds.groupby(
            "road_segment_id",
            dropna=False,
        )
        .agg(
            average_speed_kmh=("estimated_speed_kmh", "mean")
        )
        .reset_index()
    )


def compute_congestion(
    events: pd.DataFrame,
    window: str | int = "15min",
    density_threshold: float = DEFAULT_DENSITY_THRESHOLD,
    speed_reference_kmh: float = DEFAULT_SPEED_REFERENCE_KMH,
    density_weight: float = DEFAULT_DENSITY_WEIGHT,
    speed_weight: float = DEFAULT_SPEED_WEIGHT,
    as_json: bool = False,
) -> dict[str, Any]:
    """Compute explainable congestion scores by road segment and time."""

    if density_threshold <= 0:
        raise ValueError(
            "density_threshold must be greater than zero."
        )

    if speed_reference_kmh <= 0:
        raise ValueError(
            "speed_reference_kmh must be greater than zero."
        )

    if density_weight < 0 or speed_weight < 0:
        raise ValueError(
            "Congestion weights cannot be negative."
        )

    total_weight = density_weight + speed_weight

    if total_weight == 0:
        raise ValueError(
            "At least one congestion weight must be greater than zero."
        )

    density_weight /= total_weight
    speed_weight /= total_weight

    # IMPORTANT:
    # Normalize API data before passing it to density.py.
    events = _prepare_events(events)

    density_result = compute_density(
        events,
        window=window,
        as_json=False,
    )

    density = density_result["by_segment_time"].copy()

    if density.empty:
        result = _empty_frame()

    else:
        speed = _prepare_speed(events)

        result = density.merge(
            speed,
            on="road_segment_id",
            how="left",
        )

        result["average_speed_kmh"] = pd.to_numeric(
            result["average_speed_kmh"],
            errors="coerce",
        )

        result["density_score"] = (
            result["unique_vehicles"] / density_threshold
        ).apply(_clip_score)

        result["speed_score"] = (
            1
            - result["average_speed_kmh"] / speed_reference_kmh
        ).fillna(0.0).apply(_clip_score)

        result["congestion_score"] = (
            density_weight * result["density_score"]
            + speed_weight * result["speed_score"]
        ).round(4)

        result["congestion_level"] = result[
            "congestion_score"
        ].apply(_congestion_level)

        result = result.rename(
            columns={
                "unique_vehicles": "vehicle_count",
            }
        )

        result = result[
            [
                "road_segment_id",
                "road_name",
                "interval_start",
                "interval_end",
                "vehicle_count",
                "average_speed_kmh",
                "density_score",
                "speed_score",
                "congestion_score",
                "congestion_level",
            ]
        ].sort_values(
            ["interval_start", "road_segment_id"]
        ).reset_index(drop=True)

    payload = {
        "window": density_result["window"],
        "density_threshold": density_threshold,
        "speed_reference_kmh": speed_reference_kmh,
        "density_weight": density_weight,
        "speed_weight": speed_weight,
        "by_segment_time": result,
    }

    if as_json:
        return {
            key: (
                _records(value)
                if isinstance(value, pd.DataFrame)
                else value
            )
            for key, value in payload.items()
        }

    return payload


def _records(df: pd.DataFrame) -> list[dict[str, Any]]:
    if df.empty:
        return []

    serialized = df.copy()

    for column in serialized.columns:
        if pd.api.types.is_datetime64_any_dtype(
            serialized[column]
        ):
            serialized[column] = serialized[column].dt.strftime(
                "%Y-%m-%dT%H:%M:%S%z"
            )

            serialized[column] = serialized[column].str.replace(
                r"(\d{2})(\d{2})$",
                r"\1:\2",
                regex=True,
            )

    records = serialized.to_dict(
        orient="records"
    )

    return [
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
        for record in records
    ]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute explainable traffic congestion scores."
    )

    parser.add_argument(
        "--window",
        default="15min",
        help="Time window: 5min, 15min, or 1h.",
    )

    parser.add_argument(
        "--csv",
        default=None,
        help="Path to vehicle events CSV.",
    )

    parser.add_argument(
        "--density-threshold",
        type=float,
        default=DEFAULT_DENSITY_THRESHOLD,
        help="Vehicle count considered fully dense.",
    )

    parser.add_argument(
        "--speed-reference",
        type=float,
        default=DEFAULT_SPEED_REFERENCE_KMH,
        help="Reference speed in km/h.",
    )

    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    events = load_vehicle_events(args.csv)

    result = compute_congestion(
        events,
        window=args.window,
        density_threshold=args.density_threshold,
        speed_reference_kmh=args.speed_reference,
        as_json=True,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()