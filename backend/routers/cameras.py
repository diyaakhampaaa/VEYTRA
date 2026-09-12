from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

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

    return {
        "cameras": [
            {
                "camera_id": camera.camera_id,
                "status": camera.status,
                "vehicles_detected": camera.vehicles_detected,
                "source": camera.source,
                "location": (
                    {
                        "longitude": float(
                            db.query(
                                func.ST_X(camera.location)
                            ).scalar()
                        ),
                        "latitude": float(
                            db.query(
                                func.ST_Y(camera.location)
                            ).scalar()
                        ),
                    }
                    if camera.location is not None
                    else None
                ),
            }
            for camera in cameras
        ]
    }