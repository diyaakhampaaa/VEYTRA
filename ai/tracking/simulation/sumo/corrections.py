from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any


def create_correction_record(
    candidate: dict[str, Any],
    verification: dict[str, Any],
) -> dict[str, Any]:
    """Create an immutable-style provenance record for a correction.

    The record identifies the exact camera-local track that changed and keeps
    the other side of the match as a reference. The original OCR observation
    is never discarded by the correction application step.
    """
    event = candidate.get("event", {})
    supporting = candidate.get("supporting_event", {})
    correction = verification.get("correction") or {}
    reference = verification.get("reference") or {}

    return {
        "correction_id": "CORR001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "camera_id": correction.get("camera_id", event.get("camera_id")),
        "local_track_id": correction.get("local_track_id", event.get("local_track_id")),
        "original_plate": correction.get("original_plate"),
        "corrected_plate": correction.get("corrected_plate"),
        "reference": {
            "camera_id": reference.get("camera_id", supporting.get("camera_id")),
            "local_track_id": reference.get("local_track_id", supporting.get("local_track_id")),
            "plate": reference.get("plate", supporting.get("plate")),
        },
        "reason": verification.get("reason"),
        "status": verification.get("status"),
        "source": "parallel_verification",
        "evidence": deepcopy(verification.get("evidence", [])),
        "original_event": deepcopy(event),
        "supporting_event": deepcopy(supporting),
    }


def apply_correction(
    tracks: list[dict[str, Any]],
    correction_record: dict[str, Any],
) -> list[dict[str, Any]]:
    """Apply one resolved correction to the exact camera-local track.

    Returns a deep copy; the input list is never mutated. Original OCR is
    retained in ``original_plate`` and ``plate_history`` when present.
    Unresolved/invalid corrections are a no-op.
    """
    if not isinstance(tracks, list) or not isinstance(correction_record, dict):
        return deepcopy(tracks) if isinstance(tracks, list) else []
    if correction_record.get("status") != "RESOLVED":
        return deepcopy(tracks)

    camera_id = correction_record.get("camera_id")
    local_track_id = correction_record.get("local_track_id")
    corrected_plate = correction_record.get("corrected_plate")
    original_plate = correction_record.get("original_plate")
    correction_id = correction_record.get("correction_id")
    if camera_id is None or local_track_id is None or not corrected_plate:
        return deepcopy(tracks)

    out = deepcopy(tracks)
    for track in out:
        if not isinstance(track, dict):
            continue
        if str(track.get("camera_id")) != str(camera_id):
            continue
        if str(track.get("local_track_id")) != str(local_track_id):
            continue

        current = track.get("plate_text")
        if current is None:
            current = track.get("plate")
        if original_plate is None:
            original_plate = current

        track["original_plate"] = original_plate
        history = track.get("plate_history")
        if not isinstance(history, list):
            history = []
        history.append({
            "plate": original_plate,
            "status": "ORIGINAL",
            "correction_id": correction_id,
        })
        history.append({
            "plate": corrected_plate,
            "status": "CORRECTED",
            "correction_id": correction_id,
        })
        track["plate_history"] = history
        if "plate_text" in track or "plate" not in track:
            track["plate_text"] = corrected_plate
        if "plate" in track:
            track["plate"] = corrected_plate
        track["verification_status"] = "CORRECTED"
        track["verification_reason"] = correction_record.get("reason")
        track["correction_id"] = correction_id
        track["corrected_from"] = original_plate

    return out
