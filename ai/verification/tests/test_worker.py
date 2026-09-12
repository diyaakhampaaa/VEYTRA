"""
test_worker.py
---------------
Proves verification does NOT block the main pipeline, by timing
3 events with a deliberately SLOW evidence search.
"""

import time
import asyncio
from ai.verification.worker import verify_many_events_async
from ai.verification.evidence import find_supporting_evidence


def _slow_evidence_search(event):
    time.sleep(0.2)
    return find_supporting_evidence(event)


def test_verification_runs_concurrently_not_one_by_one():
    events = [
        {"event_id": "EVT_X1", "camera_id": "C13", "plate": "DL01AB1284",
         "ocr_confidence": 0.5, "timestamp": "2026-09-06T15:30:00"},
        {"event_id": "EVT_X2", "camera_id": "C14", "plate": "MH12ZZ0000",
         "ocr_confidence": 0.5, "timestamp": "2026-09-06T15:30:00"},
        {"event_id": "EVT_X3", "camera_id": "C15", "plate": "KA05AA1111",
         "ocr_confidence": 0.5, "timestamp": "2026-09-06T15:30:00"},
    ]

    start = time.perf_counter()
    results = asyncio.run(verify_many_events_async(events, evidence_search_fn=_slow_evidence_search))
    elapsed = time.perf_counter() - start

    assert len(results) == 3
    assert elapsed < 0.5, f"Expected concurrent execution (~0.2s), took {elapsed:.2f}s -- looks like it's blocking"