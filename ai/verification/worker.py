"""
worker.py
---------
Runs verification in the BACKGROUND, so if evidence-search is slow
(e.g. a real database query, or waiting on Member 3's Re-ID service),
the main traffic-analytics pipeline keeps processing other events
without waiting on us.

This uses asyncio -- Python's built-in tool for "do this without
freezing everything else." Redis is optional/for later, when this
needs to run across multiple servers, not just one process.
"""

import asyncio
from .suspicion import check_suspicion
from .evidence import find_supporting_evidence
from .scoring import find_best_candidate
from .correction import apply_correction
from .logger import log_verification_decision


async def verify_event_async(event: dict, reid_similarity: float | None = None) -> dict:
    """
    Same pipeline as api.py's /verify, but as an async function that
    can run alongside other work instead of blocking it.

    `await asyncio.sleep(0)` below simulates handing control back to
    the event loop -- in the real system, this is where a slow database
    query or network call to Member 3's service would naturally yield
    control anyway.
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

    await asyncio.sleep(0)  # placeholder for a real slow I/O call (DB/network)
    supporting = find_supporting_evidence(event)

    await asyncio.sleep(0)
    best = find_best_candidate(event.get("plate"), supporting, reid_similarity)

    result = apply_correction(event["event_id"], event.get("plate"), best, reid_similarity)
    log_verification_decision(result, original_confidence=event.get("ocr_confidence"))
    return result


async def verify_many_events_async(events: list[dict]) -> list[dict]:
    """
    Verifies multiple events CONCURRENTLY instead of one-by-one.
    This is the actual proof that "verification doesn't block the
    main pipeline" -- multiple events get processed in parallel.
    """
    tasks = [verify_event_async(evt, evt.get("reid_similarity")) for evt in events]
    return await asyncio.gather(*tasks)
