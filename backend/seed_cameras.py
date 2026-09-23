from backend.database import SessionLocal
from backend.models import Camera

db = SessionLocal()

try:
    cameras = [
        Camera(
            camera_id="CAM_01",
            status="Active",
            vehicles_detected=12,
            source="simulated",
            location="28.6139,77.2090",
        ),
        Camera(
            camera_id="CAM_02",
            status="Active",
            vehicles_detected=8,
            source="simulated",
            location="28.6170,77.2150",
        ),
        Camera(
            camera_id="CAM_03",
            status="Active",
            vehicles_detected=15,
            source="simulated",
            location="28.6130,77.2210",
        ),
    ]

    db.add_all(cameras)
    db.commit()

    print("Demo cameras inserted successfully!")

except Exception as error:
    db.rollback()
    print("Failed to insert cameras:")
    print(error)

finally:
    db.close()