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