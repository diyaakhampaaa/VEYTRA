from sqlalchemy import Column, String, Integer, Float
from geoalchemy2 import Geometry

from backend.database import Base


class Camera(Base):
    __tablename__ = "cameras"

    camera_id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    vehicles_detected = Column(Integer, default=0)
    source = Column(String, nullable=False)

    location = Column(
        Geometry("POINT", srid=4326),
        nullable=True
    )


class Vehicle(Base):
    __tablename__ = "vehicles"

    vehicle_id = Column(String, primary_key=True)
    plate = Column(String, unique=True, nullable=False)

    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)

    source = Column(String, nullable=False)

    reid_similarity = Column(Float, nullable=True)
    plate_similarity = Column(Float, nullable=True)
    temporal_score = Column(Float, nullable=True)
    route_score = Column(Float, nullable=True)

class VehicleCameraEvent(Base):
    __tablename__ = "vehicle_camera_events"

    id = Column(Integer, primary_key=True, autoincrement=True)

    vehicle_id = Column(String, nullable=False)
    camera_id = Column(String, nullable=False)

    timestamp = Column(String, nullable=False)
    direction = Column(String, nullable=True)