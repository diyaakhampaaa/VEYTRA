"""
worker.py
---------
Runs verification in the BACKGROUND, so if evidence-search is slow
(e.g. a real database query, or waiting on Member 3's Re-ID service),
the main traffic-analytics pipeline keeps processing other events
without waiting on us.
"""

import asyncio
from .suspicion import check_suspicion
from .evidence import find_supporting_evidence
from .scoring import find_best_candidate
from .correction import apply_correction
from .logger import log_verification_decision


async def verify_event_async(
    event: dict,
    reid_similarity: float | None = None,
    evidence_search_fn=find_supporting_evidence,
) -> dict:
    """
    `evidence_search_fn` is pluggable (defaults to the real evidence
    search) specifically so tests can substitute a deliberately SLOW
    version and prove other events still get processed concurrently.

    `asyncio.to_thread` runs the (possibly slow/blocking) evidence
    search in a background thread, so the main event loop stays free
    to work on other events while this one is waiting.
    """
    verdict = check_suspicion(event)
    if not verdict["is_suspicious"]:
        return {
            "event_id": event["event_id"],
            "original_plate": event.get("plate"),
            "corrected_plate": event.get("plate"),
            "supporting_cameras": [],
            "reid_similarity": reid_similarity,
            "verification_confidence": 1.0,
            "reason": "Not flagged as suspicious",
        }

    supporting = await asyncio.to_thread(evidence_search_fn, event)
    best = find_best_candidate(event.get("plate"), supporting, reid_similarity)
    result = apply_correction(event["event_id"], event.get("plate"), best, reid_similarity)
    log_verification_decision(result, original_confidence=event.get("ocr_confidence"))
    return result


async def verify_many_events_async(events: list[dict], evidence_search_fn=find_supporting_evidence) -> list[dict]:
    """
    Verifies multiple events CONCURRENTLY instead of one-by-one.
    """
    tasks = [verify_event_async(evt, evt.get("reid_similarity"), evidence_search_fn) for evt in events]
    return await asyncio.gather(*tasks)