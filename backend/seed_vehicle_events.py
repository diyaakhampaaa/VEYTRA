from backend.database import SessionLocal
from backend.models import VehicleCameraEvent

db = SessionLocal()

try:
    events = [
        VehicleCameraEvent(
            vehicle_id="VEH_001",
            camera_id="CAM_01",
            timestamp="18:42:10",
            direction="North",
        ),
        VehicleCameraEvent(
            vehicle_id="VEH_001",
            camera_id="CAM_02",
            timestamp="18:45:23",
            direction="North-East",
        ),
        VehicleCameraEvent(
            vehicle_id="VEH_001",
            camera_id="CAM_03",
            timestamp="18:49:32",
            direction="East",
        ),
    ]

    db.add_all(events)
    db.commit()

    print("Vehicle journey events inserted successfully!")

except Exception as error:
    db.rollback()
    print("Failed to insert vehicle events:")
    print(error)

finally:
    db.close()