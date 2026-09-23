import pandas as pd

from backend.database import SessionLocal
from backend.models import Vehicle, VehicleCameraEvent


CSV_PATH = "analytics/data/sample_vehicle_events.csv"


db = SessionLocal()

try:
    df = pd.read_csv(CSV_PATH)

    for vehicle_id, group in df.groupby("vehicle_id"):

        first_row = group.iloc[0]
        last_row = group.iloc[-1]

        vehicle = (
            db.query(Vehicle)
            .filter(Vehicle.vehicle_id == vehicle_id)
            .first()
        )

        if not vehicle:
            vehicle = Vehicle(
                vehicle_id=vehicle_id,
                plate=first_row["plate_number"],
                start_time=str(first_row["timestamp"]),
                end_time=str(last_row["timestamp"]),
                source="analytics_csv",
            )
            db.add(vehicle)
        else:
            vehicle.plate = first_row["plate_number"]
            vehicle.start_time = str(first_row["timestamp"])
            vehicle.end_time = str(last_row["timestamp"])
            vehicle.source = "analytics_csv"

        for _, row in group.iterrows():
            event = VehicleCameraEvent(
                vehicle_id=vehicle_id,
                camera_id=row["camera_id"],
                timestamp=str(row["timestamp"]),
                direction=row["direction"],
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                road_segment_id=row["road_segment_id"],
                road_name=row["road_name"],
                speed_kmh=float(row["speed_kmh"]),
                trajectory_id=row["trajectory_id"],
            )

            db.add(event)

    db.commit()

    print(f"Imported {len(df)} vehicle events successfully!")
    print(f"Imported {df['vehicle_id'].nunique()} vehicles successfully!")

except Exception as error:
    db.rollback()
    print("Import failed:")
    print(error)

finally:
    db.close()