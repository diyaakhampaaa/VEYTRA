"""
Generate GeoJSON LineString features for OD flows.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def od_to_geojson(
    od_data: pd.DataFrame,
    camera_locations: pd.DataFrame,
    output_path: str | Path | None = None,
) -> dict:
    """
    Convert OD data into GeoJSON LineStrings.

    od_data columns:
        origin_camera_id
        destination_camera_id
        vehicle_count

    camera_locations columns:
        camera_id
        latitude
        longitude
    """

    required_od = {
        "origin_camera_id",
        "destination_camera_id",
        "vehicle_count",
    }

    required_locations = {
        "camera_id",
        "latitude",
        "longitude",
    }

    missing_od = required_od - set(od_data.columns)
    missing_locations = required_locations - set(camera_locations.columns)

    if missing_od:
        raise ValueError(f"Missing OD columns: {sorted(missing_od)}")

    if missing_locations:
        raise ValueError(
            f"Missing camera location columns: {sorted(missing_locations)}"
        )

    locations = camera_locations.set_index("camera_id").to_dict("index")

    features = []

    for _, row in od_data.iterrows():
        origin = row["origin_camera_id"]
        destination = row["destination_camera_id"]

        if origin not in locations or destination not in locations:
            continue

        origin_data = locations[origin]
        destination_data = locations[destination]

        features.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [
                            float(origin_data["longitude"]),
                            float(origin_data["latitude"]),
                        ],
                        [
                            float(destination_data["longitude"]),
                            float(destination_data["latitude"]),
                        ],
                    ],
                },
                "properties": {
                    "origin_camera_id": origin,
                    "destination_camera_id": destination,
                    "vehicle_count": int(row["vehicle_count"]),
                },
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