from backend.database import SessionLocal
from backend.models import Vehicle


db = SessionLocal()

try:
    vehicle = Vehicle(
        vehicle_id="VEH_001",
        plate="DL01AB1234",
        start_time="18:42:10",
        end_time="18:49:32",
        source="simulated",
        reid_similarity=0.94,
        plate_similarity=0.98,
        temporal_score=0.91,
        route_score=0.89
    )

    db.add(vehicle)
    db.commit()

    print("Demo vehicle inserted successfully!")

except Exception as error:
    db.rollback()
    print("Failed to insert vehicle:")
    print(error)

finally:
    db.close()