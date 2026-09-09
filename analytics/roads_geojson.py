"""
Generate road-segment GeoJSON.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def roads_to_geojson(
    roads: pd.DataFrame,
    output_path: str | Path | None = None,
) -> dict:
    """
    Convert road data into GeoJSON.

    Required columns:
        segment_id
        latitude
        longitude

    Optional columns:
        road_name
        start_latitude
        start_longitude
        end_latitude
        end_longitude
    """

    required = {
        "segment_id",
        "latitude",
        "longitude",
    }

    missing = required - set(roads.columns)

    if missing:
        raise ValueError(f"Missing road columns: {sorted(missing)}")

    features = []

    for _, row in roads.iterrows():
        if pd.isna(row["latitude"]) or pd.isna(row["longitude"]):
            continue

        if {
            "start_latitude",
            "start_longitude",
            "end_latitude",
            "end_longitude",
        }.issubset(roads.columns):
            geometry = {
                "type": "LineString",
                "coordinates": [
                    [
                        float(row["start_longitude"]),
                        float(row["start_latitude"]),
                    ],
                    [
                        float(row["end_longitude"]),
                        float(row["end_latitude"]),
                    ],
                ],
            }
        else:
            geometry = {
                "type": "Point",
                "coordinates": [
                    float(row["longitude"]),
                    float(row["latitude"]),
                ],
            }

        properties = {
            "segment_id": row["segment_id"],
        }

        for column in ["road_name", "vehicle_count", "average_speed"]:
            if column in roads.columns and not pd.isna(row[column]):
                properties[column] = row[column]

        features.append(
            {
                "type": "Feature",
                "geometry": geometry,
                "properties": properties,
            }
        )

    geojson = {
        "type": "FeatureCollection",
        "features": features,
    }

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as file:
            json.dump(geojson, file, indent=2, default=str)

    return geojson