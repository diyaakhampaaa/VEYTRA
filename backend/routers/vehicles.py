from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import Vehicle, VehicleCameraEvent

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/search")
def search_vehicle(
    plate: str,
    db: Session = Depends(get_db)
):
    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.plate == plate.upper())
        .first()
    )

    if not vehicle:
        return {
            "found": False,
            "vehicle": None
        }

    events = (
        db.query(VehicleCameraEvent)
        .filter(VehicleCameraEvent.vehicle_id == vehicle.vehicle_id)
        .order_by(VehicleCameraEvent.timestamp)
        .all()
    )

    camera_sequence = []

    for event in events:
        location = None

        if event.latitude is not None and event.longitude is not None:
            location = {
                "latitude": event.latitude,
                "longitude": event.longitude
            }

        camera_sequence.append({
            "camera_id": event.camera_id,
            "timestamp": event.timestamp,
            "direction": event.direction,
            "location": location,
            "road_segment_id": event.road_segment_id,
            "road_name": event.road_name,
            "speed_kmh": event.speed_kmh,
            "trajectory_id": event.trajectory_id
        })

    return {
        "found": True,
        "vehicle": {
            "plate": vehicle.plate,
            "vehicle_id": vehicle.vehicle_id,
            "start_time": vehicle.start_time,
            "end_time": vehicle.end_time,
            "source": vehicle.source,
            "camera_sequence": camera_sequence,
            "match_score": {
                "reid_similarity": vehicle.reid_similarity,
                "plate_similarity": vehicle.plate_similarity,
                "temporal_score": vehicle.temporal_score,
                "route_score": vehicle.route_score
            }
        }
    }