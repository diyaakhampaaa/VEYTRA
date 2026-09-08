"""
api.py
------
Thin FastAPI wrapper around the verification pipeline, so Member 6's
dashboard (or anyone else) can call this module over HTTP instead of
importing Python functions directly.
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from .suspicion import check_suspicion
from .evidence import find_supporting_evidence
from .scoring import find_best_candidate
from .correction import apply_correction
from .logger import log_verification_decision, get_all_logs

app = FastAPI(title="VEYTRA Verification Service")


class VehicleEvent(BaseModel):
    """Matches the shared vehicle_events contract (the fields we actually need)."""
    event_id: str
    camera_id: str
    plate: Optional[str] = None
    ocr_confidence: float = 1.0
    timestamp: str
    reid_similarity: Optional[float] = None


@app.post("/verify")
def verify_event(event: VehicleEvent) -> dict:
    """
    Runs one event through the full pipeline:
    suspicion check -> evidence search -> scoring -> correction -> logging.

    If the event isn't suspicious, we skip straight to a clean pass-through
    result (no need to search evidence for something that already looks fine).
    """
    event_dict = event.model_dump()
    verdict = check_suspicion(event_dict)

    if not verdict["is_suspicious"]:
        return {
            "event_id": event.event_id,
            "original_plate": event.plate,
            "corrected_plate": event.plate,
            "supporting_cameras": [],
            "reid_similarity": event.reid_similarity,
            "verification_confidence": 1.0,
            "reason": "Not flagged as suspicious",
        }

    supporting = find_supporting_evidence(event_dict)
    best = find_best_candidate(event.plate, supporting, event.reid_similarity)
    result = apply_correction(event.event_id, event.plate, best, event.reid_similarity)
    log_verification_decision(result, original_confidence=event.ocr_confidence)
    return result


@app.get("/verification-logs")
def verification_logs() -> list[dict]:
    """Returns every verification decision made so far (the audit trail)."""
    return get_all_logs()
