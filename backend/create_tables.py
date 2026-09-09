from backend.database import Base, engine
from backend.models import Camera, Vehicle, VehicleCameraEvent

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")