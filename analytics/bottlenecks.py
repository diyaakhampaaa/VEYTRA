"""Identify possible traffic bottlenecks.

A bottleneck is a road segment with consistently high congestion.
This is a rule-based indicator, not a scientifically validated model.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

import pandas as pd

from analytics.congestion import compute_congestion
from analytics.io import load_vehicle_events

BOTTLENECK_COLUMNS = [
    "road_segment_id",
    "road_name",
    "congestion_score",
    "vehicle_count",
    "average_speed_kmh",
    "congestion_level",
    "high_congestion_intervals",
    "is_bottleneck",
]

DEFAULT_CONGESTION_THRESHOLD = 0.60
DEFAULT_MIN_HIGH_INTERVALS = 2


def _empty_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=BOTTLENECK_COLUMNS)


def compute_bottlenecks(
    events: pd.DataFrame,
    window: str | int = "15min",
    congestion_threshold: float = DEFAULT_CONGESTION_THRESHOLD,
    min_high_intervals: int = DEFAULT_MIN_HIGH_INTERVALS,
    as_json: bool = False,
) -> dict[str, Any]:
    """Find segments with repeated high congestion."""
    if not 0 <= congestion_threshold <= 1:
        raise ValueError("congestion_threshold must be between 0 and 1.")

    if min_high_intervals < 1:
        raise ValueError("min_high_intervals must be at least 1.")

    congestion_result = compute_congestion(
        events,
        window=window,
        as_json=False,
    )

    congestion = congestion_result["by_segment_time"]

    if congestion.empty:
        result = _empty_frame()
    else:
        work = congestion.copy()

        work["is_high_congestion"] = (
            work["congestion_score"] >= congestion_threshold
        )

        result = (
            work.groupby(
                ["road_segment_id", "road_name"],
                dropna=False,
            )
            .agg(
                congestion_score=("congestion_score", "mean"),
                vehicle_count=("vehicle_count", "mean"),
                average_speed_kmh=("average_speed_kmh", "mean"),
                congestion_level=("congestion_level", "last"),
                high_congestion_intervals=("is_high_congestion", "sum"),
            )
            .reset_index()
        )

        result["is_bottleneck"] = (
            result["high_congestion_intervals"] >= min_high_intervals
        )

        result["congestion_score"] = result["congestion_score"].round(4)
        result["vehicle_count"] = result["vehicle_count"].round(2)
        result["average_speed_kmh"] = result["average_speed_kmh"].round(2)

        result = result[
            BOTTLENECK_COLUMNS
        ].sort_values(
            ["is_bottleneck", "congestion_score"],
            ascending=[False, False],
        ).reset_index(drop=True)

    payload = {
        "window": congestion_result["window"],
        "congestion_threshold": congestion_threshold,
        "min_high_intervals": min_high_intervals,
        "bottlenecks": result,
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

    records = df.to_dict(orient="records")

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
        description="Identify possible traffic bottlenecks."
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
        "--threshold",
        type=float,
        default=DEFAULT_CONGESTION_THRESHOLD,
        help="Congestion score threshold.",
    )

    parser.add_argument(
        "--min-high-intervals",
        type=int,
        default=DEFAULT_MIN_HIGH_INTERVALS,
        help="Minimum number of high-congestion intervals.",
    )

    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    events = load_vehicle_events(args.csv)

    result = compute_bottlenecks(
        events,
        window=args.window,
        congestion_threshold=args.threshold,
        min_high_intervals=args.min_high_intervals,
        as_json=True,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()