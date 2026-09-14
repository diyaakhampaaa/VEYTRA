from fastapi import APIRouter, HTTPException
from typing import Any

from analytics.io import load_vehicle_events
from analytics.density import compute_density
from analytics.congestion import compute_congestion
from analytics.bottlenecks import compute_bottlenecks
from analytics.od_matrix import compute_od_matrix


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)


@router.get("")
def get_analytics():
    """
    Run the traffic analytics pipeline using the project's
    available vehicle observations.

    Pipeline:
        vehicle observations
            -> density
            -> congestion
            -> bottlenecks
            -> origin/destination movement
            -> spatial segment data
    """

    try:
        # ---------------------------------------------------------
        # 1. Load the existing vehicle observations
        # ---------------------------------------------------------
        events = load_vehicle_events()

        # ---------------------------------------------------------
        # 2. Density / vehicle flow
        # ---------------------------------------------------------
        density = compute_density(
            events,
            window="15min",
            as_json=True,
        )

        # ---------------------------------------------------------
        # 3. Congestion
        # ---------------------------------------------------------
        congestion = compute_congestion(
            events,
            window="15min",
            as_json=True,
        )

        # ---------------------------------------------------------
        # 4. Bottlenecks
        # ---------------------------------------------------------
        bottlenecks = compute_bottlenecks(
            events,
            window="15min",
            as_json=True,
        )

        # ---------------------------------------------------------
        # 5. Origin-Destination / movement patterns
        # ---------------------------------------------------------
        od = compute_od_matrix(
            events,
            exclude_same_location=True,
            as_json=True,
        )

        # ---------------------------------------------------------
        # 6. Build spatial lookup for road segments
        #
        # The existing vehicle observations already contain
        # latitude and longitude. We calculate the representative
        # location of each road segment from those observations.
        #
        # Nothing is hardcoded for the map.
        # ---------------------------------------------------------
        segment_locations = {}

        required_spatial_columns = {
            "road_segment_id",
            "latitude",
            "longitude",
        }

        if required_spatial_columns.issubset(events.columns):

            spatial_events = events[
                [
                    "road_segment_id",
                    "latitude",
                    "longitude",
                ]
            ].copy()

            spatial_events["latitude"] = (
                spatial_events["latitude"]
                .astype(float)
            )

            spatial_events["longitude"] = (
                spatial_events["longitude"]
                .astype(float)
            )

            spatial_events = spatial_events.dropna(
                subset=[
                    "road_segment_id",
                    "latitude",
                    "longitude",
                ]
            )

            if not spatial_events.empty:

                grouped_locations = (
                    spatial_events
                    .groupby("road_segment_id")
                    [["latitude", "longitude"]]
                    .mean()
                    .reset_index()
                )

                for _, location in grouped_locations.iterrows():

                    segment_id = location["road_segment_id"]

                    segment_locations[segment_id] = {
                        "latitude": round(
                            float(location["latitude"]),
                            6,
                        ),
                        "longitude": round(
                            float(location["longitude"]),
                            6,
                        ),
                    }

        # ---------------------------------------------------------
        # 7. Build segment-level response
        # ---------------------------------------------------------
        congestion_rows = congestion.get(
            "by_segment_time",
            []
        )

        segments = []

        for row in congestion_rows:

            segment_id = row.get(
                "road_segment_id"
            )

            location = segment_locations.get(
                segment_id,
                {}
            )

            segments.append(
                {
                    "segment_id": segment_id,
                    "road_name": row.get("road_name"),
                    "timestamp": row.get("interval_start"),
                    "interval_end": row.get("interval_end"),
                    "vehicle_count": row.get(
                        "vehicle_count",
                        0,
                    ),
                    "average_speed": row.get(
                        "average_speed_kmh"
                    ),
                    "density_score": row.get(
                        "density_score"
                    ),
                    "congestion_score": row.get(
                        "congestion_score"
                    ),
                    "congestion_level": row.get(
                        "congestion_level"
                    ),

                    # -------------------------------------------------
                    # Spatial information for GIS / heatmap
                    # -------------------------------------------------
                    "latitude": location.get(
                        "latitude"
                    ),
                    "longitude": location.get(
                        "longitude"
                    ),
                }
            )

        # ---------------------------------------------------------
        # 8. Summary
        # ---------------------------------------------------------
        total_vehicles = int(
            events["vehicle_id"].nunique()
        ) if not events.empty else 0

        valid_speeds = events["speed_kmh"].dropna()

        average_speed = (
            round(
                float(valid_speeds.mean()),
                2,
            )
            if not valid_speeds.empty
            else None
        )

        congestion_scores = [
            row.get("congestion_score")
            for row in congestion_rows
            if row.get("congestion_score") is not None
        ]

        average_congestion = (
            round(
                sum(congestion_scores)
                / len(congestion_scores),
                4,
            )
            if congestion_scores
            else None
        )

        bottleneck_rows = bottlenecks.get(
            "bottlenecks",
            []
        )

        active_bottlenecks = [
            row
            for row in bottleneck_rows
            if row.get("is_bottleneck") is True
        ]

        # ---------------------------------------------------------
        # 9. Movement flows
        # ---------------------------------------------------------
        movement_flows = od.get(
            "od_matrix",
            []
        )

        # ---------------------------------------------------------
        # 10. Return complete analytics response
        # ---------------------------------------------------------
        return {
            "status": "success",

            "source": {
                "type": "controlled_vehicle_observations",
                "file": "analytics/data/sample_vehicle_events.csv",
                "note": (
                    "Analytics are computed from the available "
                    "vehicle-event observations."
                ),
            },

            "summary": {
                "total_vehicles": total_vehicles,
                "average_speed_kmh": average_speed,
                "average_congestion": average_congestion,
                "bottleneck_count": len(active_bottlenecks),
            },

            "segments": segments,

            "bottlenecks": bottleneck_rows,

            "movement_flows": movement_flows,

            "density": density,

            "od": od,

        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Analytics processing failed: {str(error)}",
        )


@router.post("/congestion")
def congestion(data: list[dict[str, Any]]):
    """
    Preserve the existing congestion endpoint for compatibility.

    This endpoint is still available for callers that provide
    their own vehicle-event observations.
    """

    try:
        import pandas as pd

        events = pd.DataFrame(data)

        result = compute_congestion(
            events,
            as_json=True,
        )

        return {
            "status": "success",
            "data": result,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Congestion analysis failed: {str(error)}",
        )