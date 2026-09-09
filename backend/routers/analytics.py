from fastapi import APIRouter
from pydantic import BaseModel


class AnalyticsResult(BaseModel):
    segment_id: str
    vehicle_count: int
    average_speed: float
    congestion_score: float
    timestamp: str


router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.post("/")
def receive_analytics(data: AnalyticsResult):
    return {
        "message": "Analytics data received",
        "data": data
    }
@router.get("/overview")
def get_analytics():
    return {
        "segments": [
            {
                "segment_id": "SEG_01",
                "vehicle_count": 42,
                "average_speed": 38.5,
                "congestion_score": 0.32,
                "timestamp": "18:50:00"
            },
            {
                "segment_id": "SEG_02",
                "vehicle_count": 67,
                "average_speed": 21.4,
                "congestion_score": 0.71,
                "timestamp": "18:50:00"
            },
            {
                "segment_id": "SEG_03",
                "vehicle_count": 29,
                "average_speed": 46.2,
                "congestion_score": 0.18,
                "timestamp": "18:50:00"
            }
        ]
    }