"""
suspicion.py
------------
Job: Look at ONE vehicle event and decide -> is this worth double-checking?

We don't fix anything here. We just RAISE A FLAG (True/False) plus a reason.
Fixing happens later in correction.py, once evidence.py finds proof.

Think of this file as a security guard doing a quick glance-check,
not a detective doing a full investigation.
"""

from typing import Optional
from rapidfuzz import fuzz  # a library that compares how similar two text strings are


# ---- CONFIGURABLE THRESHOLDS ----
# These are "tunable knobs". If your team decides the OCR is often unreliable,
# you can raise this number so MORE events get flagged as suspicious.
OCR_CONFIDENCE_THRESHOLD = 0.75

# If two plates are less than this % similar, we treat them as "different plates"
# (RapidFuzz gives a score from 0 to 100, where 100 = identical strings)
# Set high (95) on purpose: Indian plates are short, so even a SINGLE
# misread character (e.g. "8" vs "3") should count as a disagreement worth
# checking -- that's exactly the kind of subtle error our USP needs to catch.
PLATE_SIMILARITY_THRESHOLD = 95


def is_ocr_confidence_low(ocr_confidence: float) -> bool:
    """
    Rule 1: Is the OCR reading itself unsure about what it read?

    Example: ocr_confidence = 0.61 -> True (this IS suspicious, 0.61 < 0.75)
             ocr_confidence = 0.94 -> False (this is NOT suspicious)
    """
    return ocr_confidence < OCR_CONFIDENCE_THRESHOLD


def has_neighbour_disagreement(plate: Optional[str], nearby_events: list[dict]) -> bool:
    """
    Rule 2: Do nearby cameras disagree on the plate number?

    'nearby_events' is a list of events from OTHER cameras that plausibly
    saw the same vehicle (Member 3 / evidence.py will hand us this list).

    We compare our plate against each nearby plate using fuzzy text matching
    (not exact match) because OCR often misreads 1-2 characters, so plates
    that are "almost the same" shouldn't be treated as a full disagreement --
    only plates that are meaningfully DIFFERENT count as disagreement.
    """
    if not plate or not nearby_events:
        # Nothing to compare against -> can't detect disagreement
        return False

    for event in nearby_events:
        neighbour_plate = event.get("plate")
        if not neighbour_plate:
            continue  # skip events with no plate at all

        similarity = fuzz.ratio(plate, neighbour_plate)  # 0-100 score
        if similarity < PLATE_SIMILARITY_THRESHOLD:
            return True  # found a meaningfully different plate nearby -> suspicious

    return False

MIN_FEASIBLE_TRAVEL_FRACTION = 0.3


def has_implausible_timing(camera_id, timestamp, nearby_events: list[dict]) -> bool:
    """Rule 3: is the time gap between this event and a nearby camera's
    sighting physically impossible (arrived impossibly fast)?"""
    if not camera_id or not timestamp or not nearby_events:
        return False

    from datetime import datetime
    from .camera_network import get_neighbour_cameras

    neighbours = get_neighbour_cameras(camera_id)
    if not neighbours:
        return False

    for event in nearby_events:
        neighbour_camera = event.get("camera_id")
        neighbour_timestamp = event.get("timestamp")
        if neighbour_camera not in neighbours or not neighbour_timestamp:
            continue

        expected_seconds = neighbours[neighbour_camera]
        try:
            gap_seconds = abs(
                (datetime.fromisoformat(neighbour_timestamp) - datetime.fromisoformat(timestamp)).total_seconds()
            )
        except (ValueError, TypeError):
            continue

        if gap_seconds < expected_seconds * MIN_FEASIBLE_TRAVEL_FRACTION:
            return True

    return False

def check_suspicion(event: dict) -> dict:
    """
    MAIN FUNCTION of this file.

    Input: one vehicle event dict, e.g.
        {
            "event_id": "EVT1023",
            "plate": "DL01AB1284",
            "ocr_confidence": 0.61,
            "nearby_events": [...]
        }

    Output: a small verdict dict, e.g.
        {
            "is_suspicious": True,
            "reasons": ["low_ocr_confidence", "neighbour_disagreement"]
        }

    We collect ALL matching reasons (not just the first one found) because
    it's useful evidence later -- "flagged for 2 reasons" is stronger
    justification than "flagged for 1 reason".
    """
    reasons = []

    if is_ocr_confidence_low(event.get("ocr_confidence", 1.0)):
        reasons.append("low_ocr_confidence")

    if has_neighbour_disagreement(event.get("plate"), event.get("nearby_events", [])):
        reasons.append("neighbour_disagreement")

    if has_implausible_timing(event.get("camera_id"), event.get("timestamp"), event.get("nearby_events", [])):
        reasons.append("implausible_timing")


    return {
        "is_suspicious": len(reasons) > 0,
        "reasons": reasons,
    }
