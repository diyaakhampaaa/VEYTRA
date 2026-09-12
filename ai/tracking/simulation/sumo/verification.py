from __future__ import annotations

from typing import Any


def normalize_plate(value: Any) -> str | None:
    if not isinstance(value, str):
        return None

    plate = "".join(
        ch for ch in value.upper()
        if ch.isalnum()
    )

    return plate or None


def verify_candidate(
    candidate: dict[str, Any],
    observations: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Verify a suspicious cross-camera candidate using
    observations belonging to the specific suspicious
    camera/local track.

    The verifier must not use global plate frequency,
    because observations from unrelated vehicles must
    never influence a correction.
    """

    event = candidate.get("event", {})
    supporting_event = candidate.get(
        "supporting_event",
        {},
    )

    candidate_camera = event.get("camera_id")
    candidate_track = event.get("local_track_id")

    supporting_camera = supporting_event.get(
        "camera_id"
    )
    supporting_track = supporting_event.get(
        "local_track_id"
    )

    candidate_plate = normalize_plate(
        event.get("plate")
    )

    supporting_plate = normalize_plate(
        supporting_event.get("plate")
    )

    # ------------------------------------------------------------
    # Determine which side is suspicious.
    #
    # In the controlled fault, the supporting event contains
    # the corrupted OCR result.
    # ------------------------------------------------------------

    if supporting_plate:
        suspicious_camera = supporting_camera
        suspicious_track = supporting_track
        suspicious_plate = supporting_plate

        reference_camera = candidate_camera
        reference_track = candidate_track
        reference_plate = candidate_plate

    else:
        suspicious_camera = candidate_camera
        suspicious_track = candidate_track
        suspicious_plate = candidate_plate

        reference_camera = supporting_camera
        reference_track = supporting_track
        reference_plate = supporting_plate

    # ------------------------------------------------------------
    # Retrieve evidence ONLY from the suspicious local track.
    # ------------------------------------------------------------

    evidence = []

    for observation in observations:

        camera_id = observation.get("camera_id")
        local_track_id = observation.get(
            "local_track_id"
        )

        if camera_id != suspicious_camera:
            continue

        if local_track_id != suspicious_track:
            continue

        plate = normalize_plate(
            observation.get("plate_text")
            or observation.get("plate")
            or observation.get("plate_number")
        )

        if plate is None:
            continue

        evidence.append(
            {
                "camera_id": camera_id,
                "local_track_id": local_track_id,
                "plate": plate,
                "timestamp": (
                    observation.get("first_timestamp")
                    or observation.get("timestamp")
                ),
                "ocr_confidence": observation.get(
                    "ocr_confidence",
                    observation.get(
                        "confidence",
                        0.0,
                    ),
                ),
            }
        )

    # ------------------------------------------------------------
    # No evidence
    # ------------------------------------------------------------

    if not evidence:
        return {
            "status": "UNRESOLVED",
            "reason": "no_track_specific_evidence",
            "correction": None,
            "evidence": [],
        }

    # ------------------------------------------------------------
    # Find the most common plate within THIS track only.
    # ------------------------------------------------------------

    plate_counts: dict[str, int] = {}

    for item in evidence:
        plate = item["plate"]
        plate_counts[plate] = (
            plate_counts.get(plate, 0) + 1
        )

    corrected_plate = max(
        plate_counts,
        key=plate_counts.get,
    )

    corrected_count = plate_counts[
        corrected_plate
    ]

    # ------------------------------------------------------------
    # Require actual agreement from the track evidence.
    # ------------------------------------------------------------

    if (
        corrected_plate != suspicious_plate
        and corrected_count >= 2
    ):

        return {
            "status": "RESOLVED",
            "reason": "track_specific_ocr_consensus",
            "correction": {
                "camera_id": suspicious_camera,
                "local_track_id": suspicious_track,
                "original_plate": suspicious_plate,
                "corrected_plate": corrected_plate,
            },
            "reference": {
                "camera_id": reference_camera,
                "local_track_id": reference_track,
                "plate": reference_plate,
            },
            "evidence": evidence,
        }

    # ------------------------------------------------------------
    # Evidence exists but is not strong enough.
    # ------------------------------------------------------------

    return {
        "status": "UNRESOLVED",
        "reason": "insufficient_track_specific_consensus",
        "correction": None,
        "reference": {
            "camera_id": reference_camera,
            "local_track_id": reference_track,
            "plate": reference_plate,
        },
        "evidence": evidence,
    }