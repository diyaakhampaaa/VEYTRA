"""
output.py
---------
Shapes our internal correction result into the record Member 6's
dashboard (and Member 2's OCR pipeline) actually needs to consume.

Member 2's ask: expose event identity (event_id, vehicle_id), a clear
verification_status, the final plate number, and confidence/reasoning
-- and the dashboard should read THIS shape, not raw OCR output.

We keep the richer internal fields (original_plate, supporting_cameras,
reid_similarity, reason) alongside the requested minimal shape, rather
than replacing them -- more transparency for the audit trail, not less.
"""

from typing import Optional


def to_dashboard_record(
    correction_result: dict,
    vehicle_id: Optional[str] = None,
    ocr_confidence: Optional[float] = None,
) -> dict:
    """
    MAIN FUNCTION of this file.

    Input: the output of correction.apply_correction(), plus the
    vehicle_id and original ocr_confidence (both come from the source
    event -- our correction step doesn't generate them, just passes
    them through so identity is never lost).

    Output shape (matches Member 2's request):
        {
            "event_id": "E001",
            "vehicle_id": "V001",
            "plate_number": "DL01AB1234",
            "verification_status": "verified",
            "ocr_confidence": 0.94,
            ...plus our existing detail fields for the audit trail...
        }

    verification_status is one of:
        "verified"   -- reading confirmed correct (as-is or by evidence)
        "corrected"  -- reading was changed based on supporting evidence
        "unverified" -- suspicious, but not enough evidence to act on
    """
    original_plate = correction_result.get("original_plate")
    corrected_plate = correction_result.get("corrected_plate")
    reason = correction_result.get("reason", "") or ""

    if corrected_plate != original_plate:
        status = "corrected"
    elif "insufficient" in reason.lower() or "below threshold" in reason.lower():
        status = "unverified"
    else:
        status = "verified"

    return {
        # -- fields Member 2 asked for, dashboard reads these directly --
        "event_id": correction_result.get("event_id"),
        "vehicle_id": vehicle_id,
        "plate_number": corrected_plate,
        "verification_status": status,
        "ocr_confidence": ocr_confidence,
        # -- kept for backward compatibility: existing callers/tests already
        # rely on these exact field names, so we keep them rather than
        # breaking anything already wired to the old shape --
        "original_plate": original_plate,
        "corrected_plate": corrected_plate,
        "verification_confidence": correction_result.get("verification_confidence"),
        "supporting_cameras": correction_result.get("supporting_cameras", []),
        "reid_similarity": correction_result.get("reid_similarity"),
        "reason": reason,
    }
