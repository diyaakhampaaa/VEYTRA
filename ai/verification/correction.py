"""
correction.py
--------------
Job: Take the scoring result and make the FINAL decision:
"do we actually correct this record, or leave it as-is?"

Rule from the spec (non-negotiable): the ORIGINAL plate reading must
NEVER be overwritten/deleted, even when we do correct it. We always
keep both, side by side.
"""

from typing import Optional


# Only correct the record if our confidence is above this line.
# Below this, we'd rather stay honest and say "not sure enough" than
# risk making a wrong correction.
CONFIDENCE_THRESHOLD = 0.75


def apply_correction(
    event_id: str,
    original_plate: str,
    best_candidate: dict,
    reid_similarity: Optional[float] = None,
) -> dict:
    """
    MAIN FUNCTION of this file.

    Input:
      - the suspicious event's id and original plate
      - best_candidate: the result from scoring.find_best_candidate()
      - reid_similarity: passed through just so it appears in the output

    Output: matches the EXACT contract from the spec:
        {
            "event_id": ...,
            "original_plate": ...,
            "corrected_plate": ...,
            "supporting_cameras": [...],
            "reid_similarity": ...,
            "verification_confidence": ...,
            "reason": "..."
        }
    """
    candidate_plate = best_candidate.get("candidate_plate")
    confidence = best_candidate.get("verification_confidence", 0.0)
    supporting_cameras = best_candidate.get("supporting_cameras", [])

    # Case 1: no supporting evidence was found at all
    if candidate_plate is None:
        return {
            "event_id": event_id,
            "original_plate": original_plate,
            "corrected_plate": original_plate,  # unchanged -- kept as-is
            "supporting_cameras": [],
            "reid_similarity": reid_similarity,
            "verification_confidence": confidence,
            "reason": "Insufficient supporting evidence",
        }

    # Case 2: we found a candidate, but the plate is already correct
    # (nearby cameras agree with what we already have -- nothing to fix)
    if candidate_plate == original_plate:
        return {
            "event_id": event_id,
            "original_plate": original_plate,
            "corrected_plate": original_plate,
            "supporting_cameras": supporting_cameras,
            "reid_similarity": reid_similarity,
            "verification_confidence": confidence,
            "reason": "Original reading confirmed by neighbouring cameras",
        }

    # Case 3: we have a DIFFERENT candidate, but confidence is too low to trust it
    if confidence < CONFIDENCE_THRESHOLD:
        return {
            "event_id": event_id,
            "original_plate": original_plate,
            "corrected_plate": original_plate,  # NOT corrected -- not confident enough
            "supporting_cameras": supporting_cameras,
            "reid_similarity": reid_similarity,
            "verification_confidence": confidence,
            "reason": f"Candidate found but confidence ({confidence}) below threshold ({CONFIDENCE_THRESHOLD})",
        }

    # Case 4: strong enough evidence -- actually correct the record
    return {
        "event_id": event_id,
        "original_plate": original_plate,  # <- kept, never deleted
        "corrected_plate": candidate_plate,
        "supporting_cameras": supporting_cameras,
        "reid_similarity": reid_similarity,
        "verification_confidence": confidence,
        "reason": f"Neighbouring camera agreement ({', '.join(supporting_cameras)})"
        + (" + high Re-ID similarity" if reid_similarity and reid_similarity > 0.8 else ""),
    }
