from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.models import Camera

router = APIRouter(prefix="/cameras", tags=["Cameras"])


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_cameras(db: Session = Depends(get_db)):
    cameras = db.query(Camera).all()

    result = []

    for camera in cameras:
        location = None

        if camera.location:
            try:
                latitude, longitude = map(
                    float,
                    camera.location.split(",")
                )

                location = {
                    "latitude": latitude,
                    "longitude": longitude,
                }
            except (ValueError, AttributeError):
                location = None

        result.append(
            {
                "camera_id": camera.camera_id,
                "status": camera.status,
                "vehicles_detected": camera.vehicles_detected,
                "source": camera.source,
                "location": location,
            }
        )

    return {"cameras": result}
