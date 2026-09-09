from fastapi import APIRouter
from pydantic import BaseModel
from typing import List


class VerificationResult(BaseModel):
    event_id: str
    original_plate: str
    corrected_plate: str
    supporting_cameras: List[str]
    reid_similarity: float
    verification_confidence: float
    reason: str


router = APIRouter(prefix="/verification", tags=["Verification"])


@router.post("/")
def receive_verification(data: VerificationResult):
    return {
        "message": "Verification data received",
        "data": data
    }
@router.get("/events")
def get_verification_events():
    return {
        "events": [
            {
                "event_id": "EVT_001",
                "original_plate": "DL01AB1284",
                "corrected_plate": "DL01AB1234",
                "supporting_cameras": [
                    "CAM_01",
                    "CAM_02",
                    "CAM_03"
                ],
                "reid_similarity": 0.94,
                "verification_confidence": 0.97,
                "reason": "Plate mismatch corrected using cross-camera vehicle appearance and trajectory."
            },
            {
                "event_id": "EVT_002",
                "original_plate": "DL02XY781",
                "corrected_plate": "DL02XY0781",
                "supporting_cameras": [
                    "CAM_02",
                    "CAM_03"
                ],
                "reid_similarity": 0.89,
                "verification_confidence": 0.91,
                "reason": "OCR ambiguity resolved using supporting camera observations."
            }
        ]
    }