import pandas as pd

from analytics.density_geojson import density_to_geojson
from analytics.od_geojson import od_to_geojson
from analytics.roads_geojson import roads_to_geojson


def test_density_geojson():
    density = pd.DataFrame(
        [
            {
                "segment_id": "SEG_A1",
                "latitude": 17.385,
                "longitude": 78.486,
                "vehicle_count": 15,
            }
        ]
    )

    result = density_to_geojson(density)

    assert result["type"] == "FeatureCollection"
    assert len(result["features"]) == 1
    assert result["features"][0]["geometry"]["type"] == "Point"


def test_od_geojson():
    od = pd.DataFrame(
        [
            {
                "origin_camera_id": "CAM_01",
                "destination_camera_id": "CAM_02",
                "vehicle_count": 10,
            }
        ]
    )

    locations = pd.DataFrame(
        [
            {
                "camera_id": "CAM_01",
                "latitude": 17.385,
                "longitude": 78.486,
            },
            {
                "camera_id": "CAM_02",
                "latitude": 17.400,
                "longitude": 78.500,
            },
        ]
    )

    result = od_to_geojson(od, locations)

    assert len(result["features"]) == 1
    assert result["features"][0]["geometry"]["type"] == "LineString"


def test_roads_geojson():
    roads = pd.DataFrame(
        [
            {
                "segment_id": "SEG_A1",
                "latitude": 17.385,
                "longitude": 78.486,
            }
        ]
    )

    result = roads_to_geojson(roads)

    assert len(result["features"]) == 1
    assert result["features"][0]["properties"]["segment_id"] == "SEG_A1"