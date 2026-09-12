"""
scoring.py
----------
Job: Take the suspicious event + the supporting evidence we found,
and produce ONE final number: "how confident am I this correction
is right?" (a float between 0 and 1).

We also decide WHICH plate to correct to, in case different nearby
cameras suggest different candidates (conflicting evidence).
"""

from typing import Optional
from rapidfuzz import fuzz


# ---- WEIGHTS ----
# These control how much each type of evidence "counts" toward the
# final score. They must add up to 1.0 so the final score stays
# between 0 and 1.
WEIGHT_PLATE_SIMILARITY = 0.5   # does the candidate plate text look similar?
WEIGHT_REID_SIMILARITY = 0.3    # does the car LOOK the same? (from Member 3)
WEIGHT_EVIDENCE_COUNT = 0.2     # how many independent cameras agree?

# If reid_similarity is missing, we can't use that 30% weight at all --
# so we cap the maximum possible confidence lower, since we have less
# total evidence to work with. This matches the spec requirement:
# "fall back to plate-only evidence with a lower confidence ceiling".
MAX_CONFIDENCE_WITHOUT_REID = 0.85

# How many supporting cameras counts as "fully convincing" for the
# evidence-count part of the score? 2 cameras agreeing = full marks.
FULL_EVIDENCE_CAMERA_COUNT = 2


def group_candidates_by_plate(supporting_events: list[dict]) -> dict:
    """
    Different nearby cameras might suggest DIFFERENT plates (conflicting
    evidence). This groups supporting events by which plate they saw,
    e.g.:
        {
            "DL01AB1234": ["C13", "C15"],   # 2 cameras agree on this one
            "DL01AB1239": ["C16"],          # only 1 camera suggests this
        }
    """
    grouped: dict[str, list[str]] = {}
    for evt in supporting_events:
        plate = evt.get("plate")
        camera = evt.get("camera_id")
        if not plate or not camera:
            continue
        grouped.setdefault(plate, []).append(camera)
    return grouped


def _evidence_count_score(num_supporting_cameras: int) -> float:
    """
    Turns "how many cameras agree" into a 0-1 score.
    1 camera -> 0.5, 2+ cameras -> 1.0 (capped, more than 2 doesn't add more)
    """
    return min(num_supporting_cameras / FULL_EVIDENCE_CAMERA_COUNT, 1.0)


def score_candidate(
    original_plate: str,
    candidate_plate: str,
    supporting_cameras: list[str],
    reid_similarity: Optional[float] = None,
) -> float:
    """
    Compute the verification_confidence for ONE candidate plate.

    Combines three signals using the weights above:
      - text similarity between original and candidate plate
      - reid_similarity (car appearance match), if we have it
      - how many cameras support this candidate
    """
    plate_sim = fuzz.ratio(original_plate, candidate_plate) / 100  # convert 0-100 -> 0-1
    evidence_score = _evidence_count_score(len(supporting_cameras))

    if reid_similarity is None:
        # No appearance evidence available -- redistribute its weight
        # onto the two signals we DO have, but cap the result so we
        # never claim high confidence off incomplete evidence.
        combined = (
            (WEIGHT_PLATE_SIMILARITY / (WEIGHT_PLATE_SIMILARITY + WEIGHT_EVIDENCE_COUNT)) * plate_sim
            + (WEIGHT_EVIDENCE_COUNT / (WEIGHT_PLATE_SIMILARITY + WEIGHT_EVIDENCE_COUNT)) * evidence_score
        )
        return round(min(combined, MAX_CONFIDENCE_WITHOUT_REID), 2)

    combined = (
        WEIGHT_PLATE_SIMILARITY * plate_sim
        + WEIGHT_REID_SIMILARITY * reid_similarity
        + WEIGHT_EVIDENCE_COUNT * evidence_score
    )
    return round(combined, 2)


def find_best_candidate(
    original_plate: str,
    supporting_events: list[dict],
    reid_similarity: Optional[float] = None,
) -> dict:
    """
    MAIN FUNCTION of this file.

    Looks at all supporting evidence, scores every candidate plate,
    and returns the BEST-SUPPORTED one -- this is how we handle
    conflicting evidence (spec requirement): if two different plates
    are suggested, we pick the one with the higher confidence score
    and can explain why.

    Returns:
        {
            "candidate_plate": "DL01AB1234",
            "verification_confidence": 0.93,
            "supporting_cameras": ["C13", "C15"]
        }
    If there's no supporting evidence at all, candidate_plate is None.
    """
    grouped = group_candidates_by_plate(supporting_events)

    if not grouped:
        return {
            "candidate_plate": None,
            "verification_confidence": 0.0,
            "supporting_cameras": [],
        }

    best_result = None
    for candidate_plate, cameras in grouped.items():
        confidence = score_candidate(original_plate, candidate_plate, cameras, reid_similarity)
        if best_result is None or confidence > best_result["verification_confidence"]:
            best_result = {
                "candidate_plate": candidate_plate,
                "verification_confidence": confidence,
                "supporting_cameras": cameras,
            }

    return best_result
