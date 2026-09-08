"""
integration.py
---------------
Adapter that connects this module to Member 3's REAL cross-camera
matcher output, now that the plate_mismatch issue is fixed.

Member 3's `ai.tracking.integration.verification_payloads(match_result)`
already does the "find plausible supporting evidence" work for us --
it scans all track pairs and hands us only the ones where a plate
disagreement is plausible (appearance + time + spatial checks already
passed). So for this real-data path, we do NOT need our own
evidence.py/camera_network.py search -- we use the `nearby_events`
Member 3 already attached to each event.

IMPORTANT (kept independent on purpose): this file does NOT import
anything from ai.tracking. It only accepts plain dicts in the shape
Member 3's verification_payloads() produces. Whoever wires the two
modules together (Member 6's backend, or a test) calls Member 3's
function and passes the result in here -- this keeps our module
usable/testable on its own, per the spec's independence requirement.

Expected input shape, one dict per candidate (from Member 3's real code):
    {
        "event_id": "...", "camera_id": "...", "plate": "DL01AB1284",
        "ocr_confidence": 0.61, "timestamp": "...",
        "reid_similarity": 0.93,
        "nearby_events": [ {"event_id": ..., "camera_id": "C15", "plate": "DL01AB1234", ...} ],
        "match_score": {"overall": ..., "appearance": ..., "time": ..., "spatial": ..., "plate": ..., ...},
        "verification_reason": "..."
    }

Member 3 may return MULTIPLE candidate payloads for the same suspicious
event (if it's plausibly linked to more than one other camera sighting).
We merge those into one event with a combined nearby_events list before
running our pipeline once per unique event.
"""

from typing import Any

from .suspicion import check_suspicion
from .scoring import find_best_candidate
from .correction import apply_correction
from .logger import log_verification_decision


def group_payloads_by_event(payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Member 3 may hand us the SAME suspicious event more than once, each
    time paired with a different supporting camera. We merge those into
    one event with ALL its supporting evidence combined, so scoring.py
    sees the full picture (e.g. 2 cameras agreeing, not just 1 at a time).
    """
    grouped: dict[str, dict[str, Any]] = {}

    for payload in payloads:
        event_id = payload.get("event_id")
        if not event_id:
            continue

        if event_id not in grouped:
            # First time seeing this event -- copy it as our starting point
            merged = dict(payload)
            merged["nearby_events"] = list(payload.get("nearby_events", []))
            grouped[event_id] = merged
        else:
            # Already seen this event -- just add the new supporting evidence
            existing = grouped[event_id]
            existing["nearby_events"].extend(payload.get("nearby_events", []))
            # Keep the highest reid_similarity we've seen for this event
            new_reid = payload.get("reid_similarity")
            if new_reid is not None and (
                existing.get("reid_similarity") is None or new_reid > existing["reid_similarity"]
            ):
                existing["reid_similarity"] = new_reid

    return list(grouped.values())


def process_verification_payloads(payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    MAIN FUNCTION of this file.

    Takes Member 3's real verification_payloads() output (a list of
    candidate dicts) and runs each unique suspicious event through our
    full pipeline: suspicion check -> scoring -> correction -> logging.

    Returns a list of correction results (same shape as correction.py's
    apply_correction() output), ready for Member 5/6 to consume.
    """
    grouped_events = group_payloads_by_event(payloads)
    results = []

    for event in grouped_events:
        verdict = check_suspicion(event)

        if not verdict["is_suspicious"]:
            # Shouldn't normally happen -- Member 3 only sends us plausible
            # mismatches -- but we stay defensive rather than assume.
            results.append({
                "event_id": event["event_id"],
                "original_plate": event.get("plate"),
                "corrected_plate": event.get("plate"),
                "supporting_cameras": [],
                "reid_similarity": event.get("reid_similarity"),
                "verification_confidence": 1.0,
                "reason": "Not flagged as suspicious",
            })
            continue

        best = find_best_candidate(
            event.get("plate"),
            event.get("nearby_events", []),
            event.get("reid_similarity"),
        )
        result = apply_correction(
            event["event_id"],
            event.get("plate"),
            best,
            event.get("reid_similarity"),
        )
        log_verification_decision(result, original_confidence=event.get("ocr_confidence"))
        results.append(result)

    return results
