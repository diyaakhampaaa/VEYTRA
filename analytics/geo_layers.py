"""Create GIS-ready GeoJSON layers from traffic analytics data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from analytics.bottlenecks import compute_bottlenecks
from analytics.congestion import compute_congestion
from analytics.io import load_vehicle_events

EARTH_RADIUS_KM = 6371.0


def _empty_feature_collection() -> dict[str, Any]:
    return {
        "type": "FeatureCollection",
        "features": [],
    }


def _point_feature(
    longitude: float,
    latitude: float,
    properties: dict[str, Any],
) -> dict[str, Any]:
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [longitude, latitude],
        },
        "properties": properties,
    }


def _line_feature(
    coordinates: list[list[float]],
    properties: dict[str, Any],
) -> dict[str, Any]:
    return {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": coordinates,
        },
        "properties": properties,
    }


def _clean_value(value: Any) -> Any:
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    return value


def _clean_properties(properties: dict[str, Any]) -> dict[str, Any]:
    return {
        key: _clean_value(value)
        for key, value in properties.items()
    }


def cameras_geojson(events: pd.DataFrame) -> dict[str, Any]:
    """Create camera point features."""
    if events.empty:
        return _empty_feature_collection()

    required = {"camera_id", "latitude", "longitude"}

    if not required.issubset(events.columns):
        return _empty_feature_collection()

    work = events.copy()

    work["latitude"] = pd.to_numeric(
        work["latitude"],
        errors="coerce",
    )
    work["longitude"] = pd.to_numeric(
        work["longitude"],
        errors="coerce",
    )

    work = work.dropna(
        subset=["camera_id", "latitude", "longitude"]
    ).drop_duplicates("camera_id")

    features = []

    for _, row in work.iterrows():
        features.append(
            _point_feature(
                longitude=float(row["longitude"]),
                latitude=float(row["latitude"]),
                properties={
                    "camera_id": row["camera_id"],
                    "road_segment_id": row.get("road_segment_id"),
                    "road_name": row.get("road_name"),
                },
            )
        )

    return {
        "type": "FeatureCollection",
        "features": features,
    }


def trajectories_geojson(events: pd.DataFrame) -> dict[str, Any]:
    """Create LineString features for vehicle trajectories."""
    required = {
        "vehicle_id",
        "timestamp",
        "latitude",
        "longitude",
    }

    if events.empty or not required.issubset(events.columns):
        return _empty_feature_collection()

    work = events.copy()

    if "trajectory_id" not in work.columns:
        work["trajectory_id"] = work["vehicle_id"]

    work["timestamp"] = pd.to_datetime(
        work["timestamp"],
        errors="coerce",
    )
    work["latitude"] = pd.to_numeric(
        work["latitude"],
        errors="coerce",
    )
    work["longitude"] = pd.to_numeric(
        work["longitude"],
        errors="coerce",
    )

    work = work.dropna(
        subset=[
            "vehicle_id",
            "trajectory_id",
            "timestamp",
            "latitude",
            "longitude",
        ]
    ).sort_values(
        ["vehicle_id", "trajectory_id", "timestamp"]
    )

    features = []

    for (vehicle_id, trajectory_id), group in work.groupby(
        ["vehicle_id", "trajectory_id"],
        sort=False,
    ):
        coordinates = [
            [float(row["longitude"]), float(row["latitude"])]
            for _, row in group.iterrows()
        ]

        if len(coordinates) < 2:
            continue

        features.append(
            _line_feature(
                coordinates=coordinates,
                properties={
                    "vehicle_id": vehicle_id,
                    "trajectory_id": trajectory_id,
                    "point_count": len(coordinates),
                },
            )
        )

    return {
        "type": "FeatureCollection",
        "features": features,
    }


def congestion_geojson(
    events: pd.DataFrame,
    window: str | int = "15min",
) -> dict[str, Any]:
    """Create point features representing congested road segments.

    The point is the average observed location of each road segment.
    """
    required = {
        "road_segment_id",
        "latitude",
        "longitude",
    }

    if events.empty or not required.issubset(events.columns):
        return _empty_feature_collection()

    congestion = compute_congestion(
        events,
        window=window,
        as_json=False,
    )["by_segment_time"]

    if congestion.empty:
        return _empty_feature_collection()

    locations = events.copy()

    locations["latitude"] = pd.to_numeric(
        locations["latitude"],
        errors="coerce",
    )
    locations["longitude"] = pd.to_numeric(
        locations["longitude"],
        errors="coerce",
    )

    locations = (
        locations.dropna(
            subset=[
                "road_segment_id",
                "latitude",
                "longitude",
            ]
        )
        .groupby("road_segment_id")
        .agg(
            latitude=("latitude", "mean"),
            longitude=("longitude", "mean"),
        )
        .reset_index()
    )

    summary = (
        congestion.groupby(
            ["road_segment_id", "road_name"],
            dropna=False,
        )
        .agg(
            congestion_score=("congestion_score", "mean"),
            vehicle_count=("vehicle_count", "mean"),
            average_speed_kmh=("average_speed_kmh", "mean"),
            congestion_level=("congestion_level", "last"),
        )
        .reset_index()
    )

    merged = summary.merge(
        locations,
        on="road_segment_id",
        how="inner",
    )

    features = []

    for _, row in merged.iterrows():
        features.append(
            _point_feature(
                longitude=float(row["longitude"]),
                latitude=float(row["latitude"]),
                properties=_clean_properties(
                    {
                        "road_segment_id": row["road_segment_id"],
                        "road_name": row["road_name"],
                        "congestion_score": row["congestion_score"],
                        "vehicle_count": row["vehicle_count"],
                        "average_speed_kmh": row["average_speed_kmh"],
                        "congestion_level": row["congestion_level"],
                    }
                ),
            )
        )

    return {
        "type": "FeatureCollection",
        "features": features,
    }


def bottlenecks_geojson(
    events: pd.DataFrame,
    window: str | int = "15min",
) -> dict[str, Any]:
    """Create point features for detected bottlenecks."""
    required = {
        "road_segment_id",
        "latitude",
        "longitude",
    }

    if events.empty or not required.issubset(events.columns):
        return _empty_feature_collection()

    bottlenecks = compute_bottlenecks(
        events,
        window=window,
        as_json=False,
    )["bottlenecks"]

    if bottlenecks.empty:
        return _empty_feature_collection()

    locations = events.copy()

    locations["latitude"] = pd.to_numeric(
        locations["latitude"],
        errors="coerce",
    )
    locations["longitude"] = pd.to_numeric(
        locations["longitude"],
        errors="coerce",
    )

    locations = (
        locations.dropna(
            subset=[
                "road_segment_id",
                "latitude",
                "longitude",
            ]
        )
        .groupby("road_segment_id")
        .agg(
            latitude=("latitude", "mean"),
            longitude=("longitude", "mean"),
        )
        .reset_index()
    )

    merged = bottlenecks.merge(
        locations,
        on="road_segment_id",
        how="inner",
    )

    merged = merged[merged["is_bottleneck"]]

    features = []

    for _, row in merged.iterrows():
        features.append(
            _point_feature(
                longitude=float(row["longitude"]),
                latitude=float(row["latitude"]),
                properties=_clean_properties(
                    {
                        "road_segment_id": row["road_segment_id"],
                        "road_name": row["road_name"],
                        "congestion_score": row["congestion_score"],
                        "vehicle_count": row["vehicle_count"],
                        "average_speed_kmh": row["average_speed_kmh"],
                        "congestion_level": row["congestion_level"],
                        "high_congestion_intervals": row[
                            "high_congestion_intervals"
                        ],
                        "is_bottleneck": row["is_bottleneck"],
                    }
                ),
            )
        )

    return {
        "type": "FeatureCollection",
        "features": features,
    }


def export_geojson(
    layers: dict[str, dict[str, Any]],
    output_directory: str | Path = "analytics/output",
) -> list[Path]:
    """Write GeoJSON layers to disk."""
    output_dir = Path(output_directory)
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = []

    for layer_name, geojson in layers.items():
        path = output_dir / f"{layer_name}.geojson"

        with path.open("w", encoding="utf-8") as file:
            json.dump(
                geojson,
                file,
                indent=2,
            )

        paths.append(path)

    return paths


def build_geo_layers(
    events: pd.DataFrame,
    window: str | int = "15min",
) -> dict[str, dict[str, Any]]:
    """Build all GIS-ready layers."""
    return {
        "cameras": cameras_geojson(events),
        "trajectories": trajectories_geojson(events),
        "congestion": congestion_geojson(events, window),
        "bottlenecks": bottlenecks_geojson(events, window),
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create GIS-ready GeoJSON traffic layers."
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
        "--output",
        default="analytics/output",
        help="Directory where GeoJSON files will be saved.",
    )

    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    events = load_vehicle_events(args.csv)

    layers = build_geo_layers(
        events,
        window=args.window,
    )

    paths = export_geojson(
        layers,
        output_directory=args.output,
    )

    print("Generated GeoJSON layers:")

    for path in paths:
        print(path)


if __name__ == "__main__":
    main()