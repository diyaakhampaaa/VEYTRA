"""
Generate heatmap-ready GeoJSON from traffic density data.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def density_to_geojson(
    density: pd.DataFrame,
    output_path: str | Path | None = None,
) -> dict:
    """
    Convert density data into GeoJSON Point features.

    Required columns:
        segment_id or camera_id
        latitude
        longitude
        vehicle_count

    Optional columns:
        density
        window_start
        window_end
    """

    density = density.copy()

    if "segment_id" not in density.columns:
        if "camera_id" in density.columns:
            density["segment_id"] = density["camera_id"]
        else:
            raise ValueError("Density data needs segment_id or camera_id.")

    required = {
        "segment_id",
        "latitude",
        "longitude",
        "vehicle_count",
    }

    missing = required - set(density.columns)

    if missing:
        raise ValueError(f"Missing density columns: {sorted(missing)}")

    features = []

    for _, row in density.iterrows():
        if pd.isna(row["latitude"]) or pd.isna(row["longitude"]):
            continue

        properties = {
            "segment_id": row["segment_id"],
            "vehicle_count": int(row["vehicle_count"]),
        }

        for column in [
            "density",
            "window_start",
            "window_end",
            "camera_id",
            "road_name",
        ]:
            if column in density.columns and not pd.isna(row[column]):
                value = row[column]

                if hasattr(value, "isoformat"):
                    value = value.isoformat()

                properties[column] = value

        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        float(row["longitude"]),
                        float(row["latitude"]),
                    ],
                },
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
