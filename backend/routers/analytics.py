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