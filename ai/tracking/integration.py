"""Integration adapters for the Member 1 -> Member 2 -> Member 3 contract.

Member 1 owns detection, Member 2 owns plate OCR, and Member 3 owns tracking
and cross-camera identity. This module keeps the boundary explicit: it accepts
Member 1-style frame JSON, preserves Member 2's ``plate/confidence/alternatives``
fields, and converts per-frame tracker/Re-ID output into completed local-track
records for ``CrossCameraMatcher``.

No ground truth is consumed here.
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any, Iterable

from .matcher import CrossCameraMatcher
from .reid import ReIDEmbedder, embed_tracked_frame
from .tracker import PerCameraTracker


def _ocr_fields(det: dict[str, Any]) -> tuple[str | None, float | None, list[str]]:
    """Read both Member 2 names and legacy Member 3 aliases."""
    ocr = det.get("ocr")
    if not isinstance(ocr, dict):
        ocr = {}

    plate = det.get("plate")
    if plate is None:
        plate = det.get("plate_text", ocr.get("plate"))
    plate = str(plate).strip().upper() if plate is not None and str(plate).strip() else None

    confidence = det.get("confidence")
    if confidence is None:
        confidence = det.get("ocr_confidence", ocr.get("confidence"))
    try:
        confidence = float(confidence) if confidence is not None else None
    except (TypeError, ValueError):
        confidence = None
    if confidence is not None:
        confidence = max(0.0, min(1.0, confidence))

    alternatives = det.get("alternatives")
    if alternatives is None:
        alternatives = ocr.get("alternatives", [])
    if not isinstance(alternatives, list):
        alternatives = []
    alternatives = [str(x).strip().upper() for x in alternatives if str(x).strip()]
    return plate, confidence, alternatives


def _normalise_embedding(values: list[float]) -> list[float] | None:
    norm = math.sqrt(sum(value * value for value in values))
    if norm <= 0.0:
        return None
    return [value / norm for value in values]


def prepare_track_records(tracked_frames: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aggregate Member 1/2/3 frame outputs into matcher-ready local tracks.

    Expected per-frame shape is the normal Member 1 detection contract after
    Member 3 tracking/Re-ID, e.g. each detection contains ``local_track_id``,
    ``embedding`` and optionally Member 2's ``plate``, ``confidence`` and
    ``alternatives``. The returned records are camera-local tracks with
    ``first_timestamp``/``last_timestamp`` and a representative OCR read.

    A track's plate history is retained rather than silently forcing one OCR
    value. The highest-confidence valid read becomes ``plate_text``.
    """
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)

    for frame in tracked_frames:
        if not isinstance(frame, dict):
            continue
        camera_id = frame.get("camera_id")
        timestamp = frame.get("timestamp")
        detections = frame.get("detections")
        if camera_id is None or timestamp is None or not isinstance(detections, list):
            continue

        for det in detections:
            if not isinstance(det, dict) or det.get("local_track_id") is None:
                continue
            key = (str(camera_id), str(det["local_track_id"]))
            row = dict(det)
            row["_camera_id"] = camera_id
            row["_timestamp"] = timestamp
            row["_source"] = frame.get("source")
            groups[key].append(row)

    records: list[dict[str, Any]] = []
    for (camera_id, local_track_id), rows in groups.items():
        rows.sort(key=lambda row: str(row["_timestamp"]))
        first = rows[0]
        last = rows[-1]

        embeddings: list[list[float]] = []
        for row in rows:
            value = row.get("embedding")
            if isinstance(value, (list, tuple)) and value:
                try:
                    vector = [float(x) for x in value]
                except (TypeError, ValueError):
                    continue
                embeddings.append(vector)

        embedding = None
        if embeddings and all(len(v) == len(embeddings[0]) for v in embeddings):
            mean = [
                sum(vector[i] for vector in embeddings) / len(embeddings)
                for i in range(len(embeddings[0]))
            ]
            embedding = _normalise_embedding(mean)

        plate_reads: list[dict[str, Any]] = []
        for row in rows:
            plate, confidence, alternatives = _ocr_fields(row)
            if plate:
                plate_reads.append(
                    {
                        "plate": plate,
                        "confidence": confidence if confidence is not None else 0.0,
                        "alternatives": alternatives,
                        "timestamp": row["_timestamp"],
                    }
                )

        best_read = max(plate_reads, key=lambda item: item["confidence"], default=None)

        record: dict[str, Any] = {
            "camera_id": camera_id,
            "local_track_id": first.get("local_track_id"),
            "first_timestamp": first["_timestamp"],
            "last_timestamp": last["_timestamp"],
            "source": first.get("_source"),
            "embedding": embedding,
            "plate_text": best_read["plate"] if best_read else None,
            "ocr_confidence": best_read["confidence"] if best_read else None,
            "plate_alternatives": best_read["alternatives"] if best_read else [],
            "plate_history": plate_reads,
            "observation_count": len(rows),
        }

        # Preserve optional road/direction/location fields from upstream.
        for field in ("road_segment_id", "direction", "latitude", "longitude"):
            values = [row.get(field) for row in rows if row.get(field) is not None]
            if values:
                record[field] = values[-1] if field in ("latitude", "longitude") else values[0]

        records.append(record)

    records.sort(
        key=lambda row: (
            str(row.get("first_timestamp", "")),
            str(row.get("camera_id", "")),
            str(row.get("local_track_id", "")),
        )
    )
    return records


def track_and_enrich_frame(
    detection_result: dict[str, Any],
    frame: Any,
    tracker: PerCameraTracker | None = None,
    embedder: ReIDEmbedder | None = None,
) -> dict[str, Any]:
    """Run Member 3 tracking + Re-ID on a Member 1 detection result.

    Member 2 OCR fields already attached to each detection are preserved.
    If Member 2 fields are absent, this function does not invent them.
    """
    tracker_obj = tracker if tracker is not None else PerCameraTracker()
    tracked = tracker_obj.update(detection_result)
    return embed_tracked_frame(frame, tracked, embedder=embedder)


def match_tracked_frames(
    tracked_frames: Iterable[dict[str, Any]],
    matcher: CrossCameraMatcher | None = None,
) -> dict[str, Any]:
    """Prepare completed tracks and run the cross-camera matcher."""
    records = prepare_track_records(tracked_frames)
    matcher_obj = matcher if matcher is not None else CrossCameraMatcher()
    result = matcher_obj.match(records)
    result["track_records"] = records
    return result


def verification_payloads(match_result: dict[str, Any]) -> list[dict[str, Any]]:
    """Return Member 4-ready suspicious/supporting event payloads.

    For each plausible plate-mismatch candidate, the lower-confidence OCR
    observation is presented as the suspicious event and the other observation
    is included as supporting evidence. The original OCR values are preserved.
    """
    candidates = match_result.get("verification_candidates", [])
    if not isinstance(candidates, list):
        return []

    payloads: list[dict[str, Any]] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        event = candidate.get("event")
        supporting = candidate.get("supporting_event")
        if not isinstance(event, dict) or not isinstance(supporting, dict):
            continue
        if float(supporting.get("ocr_confidence", 0.0)) < float(event.get("ocr_confidence", 0.0)):
            event, supporting = supporting, event
        suspicious = dict(event)
        suspicious["nearby_events"] = [dict(supporting)]
        suspicious["match_score"] = dict(candidate.get("match_score", {}))
        suspicious["verification_reason"] = candidate.get("reason")
        payloads.append(suspicious)
    return payloads
