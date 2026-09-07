from fastapi import APIRouter
from pydantic import BaseModel
from typing import List


class TrackingResult(BaseModel):
    vehicle_id: str
    plate: str
    camera_sequence: List[str]
    start_time: str
    end_time: str
    match_score: dict
    source: str
    ground_truth_match: bool


router = APIRouter(prefix="/tracking", tags=["Tracking"])


@router.post("/")
def receive_tracking(data: TrackingResult):
    return {
        "message": "Tracking data received",
        "data": data
    }