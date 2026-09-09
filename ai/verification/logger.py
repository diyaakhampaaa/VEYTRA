"""
logger.py
---------
Job: Record EVERY verification decision (corrected or not) permanently,
matching the `verification_logs` table from your team's shared schema.

Using a fake in-memory list for now (same pattern as fake_event_store.py).
Swap for a real PostgreSQL INSERT later -- function names/shapes stay
the same, so nothing else needs to change when that happens.
"""

from datetime import datetime, timezone
from typing import Optional

# Fake "verification_logs" table, in memory.
_VERIFICATION_LOGS: list[dict] = []


def log_verification_decision(
    correction_result: dict,
    original_confidence: Optional[float] = None,
) -> dict:
    """
    MAIN FUNCTION of this file.

    Input: the output dict from correction.apply_correction(), e.g.
        {
            "event_id": "EVT1023",
            "original_plate": "DL01AB1284",
            "corrected_plate": "DL01AB1234",
            "supporting_cameras": ["C13", "C15"],
            "reid_similarity": 0.93,
            "verification_confidence": 0.93,
            "reason": "..."
        }

    Writes one log entry matching the shared `verification_logs` schema
    from the Technical Team Guide:
        verification_id, event_id, original_plate, corrected_plate,
        supporting_cameras, original_confidence, verification_confidence,
        reason, timestamp

    Returns the log entry that was written (useful for tests / API responses).
    """
    entry = {
        "verification_id": f"VLOG{len(_VERIFICATION_LOGS) + 1:04d}",
        "event_id": correction_result.get("event_id"),
        "original_plate": correction_result.get("original_plate"),
        "corrected_plate": correction_result.get("corrected_plate"),
        "supporting_cameras": correction_result.get("supporting_cameras", []),
        "original_confidence": original_confidence,
        "verification_confidence": correction_result.get("verification_confidence"),
        "reason": correction_result.get("reason"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    _VERIFICATION_LOGS.append(entry)
    return entry


def get_all_logs() -> list[dict]:
    """
    Stand-in for: SELECT * FROM verification_logs;
    Used by the API's GET /verification-logs endpoint later.
    """
    return _VERIFICATION_LOGS
