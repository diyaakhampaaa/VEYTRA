from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from backend.models import Vehicle, VehicleCameraEvent


def persist_trajectories(
    db: Session,
    trajectories: list[dict[str, Any]],
) -> int:
    """
    Persist reconstructed M3 trajectories into the backend database.

    Returns the number of event observations persisted.
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

        plate = trajectory.get("plate") or ""
        match_score = trajectory.get("match_score", {})

        # Create or update the vehicle.
        vehicle = (
            db.query(Vehicle)
            .filter(Vehicle.vehicle_id == vehicle_id)
            .first()
        )

        if vehicle is None:
            vehicle = Vehicle(
                vehicle_id=vehicle_id,
                plate=plate,
                start_time=str(trajectory.get("start_time", "")),
                end_time=str(trajectory.get("end_time", "")),
                source=str(trajectory.get("source", "tracking")),
                reid_similarity=match_score.get("reid_similarity"),
                plate_similarity=match_score.get("plate_similarity"),
                temporal_score=match_score.get("temporal_score"),
                route_score=match_score.get("route_score"),
            )
            db.add(vehicle)

        else:
            if plate:
                vehicle.plate = plate

            vehicle.start_time = str(
                trajectory.get("start_time", vehicle.start_time)
            )
            vehicle.end_time = str(
                trajectory.get("end_time", vehicle.end_time)
            )
            vehicle.source = str(
                trajectory.get("source", vehicle.source)
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

        # Make repeated /tracking/match calls idempotent.
        existing_event_ids = {
            row.event_id
            for row in db.query(VehicleCameraEvent)
            .filter(VehicleCameraEvent.trajectory_id == trajectory_id)
            .all()
            if row.event_id
        }

        for observation in observations:
            event_id = observation.get("event_id")

            if not event_id:
                continue

            if event_id in existing_event_ids:
                continue

            event = VehicleCameraEvent(
                event_id=event_id,
                vehicle_id=vehicle_id,
                camera_id=observation.get("camera_id"),
                timestamp=str(observation.get("timestamp", "")),
                direction=observation.get("direction"),
                latitude=observation.get("latitude"),
                longitude=observation.get("longitude"),
                road_segment_id=observation.get("road_segment_id"),
                road_name=observation.get("road_name"),
                speed_kmh=observation.get("speed_kmh"),
                trajectory_id=trajectory_id,
            )

            db.add(event)
            existing_event_ids.add(event_id)
            persisted_events += 1

    db.commit()

    return persisted_events
