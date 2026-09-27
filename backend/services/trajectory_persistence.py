from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from ai.ocr.plate_validator import validate_plate
from backend.models import Vehicle, VehicleCameraEvent


def persist_trajectories(
    db: Session,
    trajectories: list[dict[str, Any]],
) -> int:
    """
    Persist reconstructed M3 trajectories into the backend database.

    Valid OCR plates are stored in Vehicle.
    Trajectories without a valid plate still have their camera events persisted.
    """

    persisted_events = 0

    for trajectory in trajectories:
        vehicle_id = trajectory.get("vehicle_id")
        trajectory_id = trajectory.get("trajectory_id")

        if not vehicle_id or not trajectory_id:
            continue

        observations = trajectory.get("event_observations", [])

        if not observations:
            continue

        raw_plate = trajectory.get("plate")
        plate_alternatives = trajectory.get(
            "plate_alternatives",
            [],
        )

        ocr_confidence = trajectory.get(
            "ocr_confidence"
        )

        if ocr_confidence is None:
            event_confidences = [
                float(
                    obs.get(
                        "ocr_confidence",
                        0.0,
                    )
                    or 0.0
                )
                for obs in observations
                if isinstance(obs, dict)
            ]

            ocr_confidence = max(
                event_confidences,
                default=0.0,
            )

        validation = validate_plate(
            raw_plate,
            ocr_confidence,
        )

        plate = validation["plate"]

        if plate is None:
            for alternative in plate_alternatives:
                alternative_validation = validate_plate(
                    alternative,
                    ocr_confidence,
                )

                if (
                    alternative_validation["plate"]
                    is not None
                ):
                    plate = alternative_validation[
                        "plate"
                    ]
                    break

        match_score = trajectory.get(
            "match_score",
            {},
        )

        # Only create/update Vehicle when there is a valid plate.
        vehicle = None

        if plate:
            vehicle = (
                db.query(Vehicle)
                .filter(
                    Vehicle.vehicle_id
                    == vehicle_id
                )
                .first()
            )

            if vehicle is None:
                vehicle = Vehicle(
                    vehicle_id=vehicle_id,
                    plate=plate,
                    start_time=str(
                        trajectory.get(
                            "start_time",
                            "",
                        )
                    ),
                    end_time=str(
                        trajectory.get(
                            "end_time",
                            "",
                        )
                    ),
                    source=str(
                        trajectory.get(
                            "source",
                            "tracking",
                        )
                    ),
                    reid_similarity=match_score.get(
                        "reid_similarity"
                    ),
                    plate_similarity=match_score.get(
                        "plate_similarity"
                    ),
                    temporal_score=match_score.get(
                        "temporal_score"
                    ),
                    route_score=match_score.get(
                        "route_score"
                    ),
                    ocr_confidence=ocr_confidence,
                )

                db.add(vehicle)

            else:
                vehicle.plate = plate

                vehicle.start_time = str(
                    trajectory.get(
                        "start_time",
                        vehicle.start_time,
                    )
                )

                vehicle.end_time = str(
                    trajectory.get(
                        "end_time",
                        vehicle.end_time,
                    )
                )

                vehicle.source = str(
                    trajectory.get(
                        "source",
                        vehicle.source,
                    )
                )

                vehicle.reid_similarity = match_score.get(
                    "reid_similarity",
                    vehicle.reid_similarity,
                )

                vehicle.plate_similarity = match_score.get(
                    "plate_similarity",
                    vehicle.plate_similarity,
                )

                vehicle.temporal_score = match_score.get(
                    "temporal_score",
                    vehicle.temporal_score,
                )

                vehicle.route_score = match_score.get(
                    "route_score",
                    vehicle.route_score,
                )

                vehicle.ocr_confidence = (
                    ocr_confidence
                )

        # Make repeated /tracking/match calls idempotent.
        existing_event_ids = {
            row.event_id
            for row in (
                db.query(VehicleCameraEvent)
                .filter(
                    VehicleCameraEvent.trajectory_id
                    == trajectory_id
                )
                .all()
            )
            if row.event_id
        }

        for observation in observations:
            event_id = observation.get(
                "event_id"
            )

            if not event_id:
                continue

            if event_id in existing_event_ids:
                continue

            event = VehicleCameraEvent(
                event_id=event_id,
                vehicle_id=vehicle_id,
                camera_id=observation.get(
                    "camera_id"
                ),
                timestamp=str(
                    observation.get(
                        "timestamp",
                        "",
                    )
                ),
                direction=observation.get(
                    "direction"
                ),
                latitude=observation.get(
                    "latitude"
                ),
                longitude=observation.get(
                    "longitude"
                ),
                road_segment_id=observation.get(
                    "road_segment_id"
                ),
                road_name=observation.get(
                    "road_name"
                ),
                speed_kmh=observation.get(
                    "speed_kmh"
                ),
                trajectory_id=trajectory_id,
            )

            db.add(event)
            existing_event_ids.add(event_id)
            persisted_events += 1

    db.commit()

    return persisted_events