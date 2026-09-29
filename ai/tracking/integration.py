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
from .reconstruct import TrajectoryReconstructor
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
    Member 3 tracking/Re-ID, e.g. each detection contains ``event_id``,
    ``local_track_id``, ``embedding`` and optionally Member 2's ``plate``,
    ``confidence`` and ``alternatives``.

    Original Member 1 event identity is preserved through aggregation using:

    - ``event_ids``: ordered list of source event IDs.
    - ``observations``: event-level observation records.

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

        # ---------------------------------------------------------
        # Re-ID embedding aggregation
        # ---------------------------------------------------------
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

        if embeddings and all(
            len(v) == len(embeddings[0]) for v in embeddings
        ):
            mean = [
                sum(vector[i] for vector in embeddings) / len(embeddings)
                for i in range(len(embeddings[0]))
            ]

            embedding = _normalise_embedding(mean)

        # ---------------------------------------------------------
        # Preserve original event identity
        # ---------------------------------------------------------
        event_ids: list[str] = []
        observations: list[dict[str, Any]] = []

        for row in rows:
            event_id = row.get("event_id")

            observation: dict[str, Any] = {
                "event_id": event_id,
                "camera_id": row.get("_camera_id"),
                "local_track_id": row.get("local_track_id"),
                "timestamp": row.get("_timestamp"),
                "source": row.get("_source"),
            }

            # Preserve OCR information at event level.
            plate, confidence, alternatives = _ocr_fields(row)

            observation["plate"] = plate
            observation["ocr_confidence"] = (
                confidence if confidence is not None else 0.0
            )
            observation["alternatives"] = alternatives

            # Preserve optional GIS / traffic fields.
            for field in (
                "road_segment_id",
                "direction",
                "latitude",
                "longitude",
            ):
                if row.get(field) is not None:
                    observation[field] = row.get(field)

            observations.append(observation)

            if event_id is not None:
                event_ids.append(str(event_id))

        # ---------------------------------------------------------
        # OCR history
        # ---------------------------------------------------------
        plate_reads: list[dict[str, Any]] = []

        for row in rows:
            plate, confidence, alternatives = _ocr_fields(row)

            if plate:
                plate_reads.append(
                    {
                        "event_id": row.get("event_id"),
                        "plate": plate,
                        "confidence": (
                            confidence if confidence is not None else 0.0
                        ),
                        "alternatives": alternatives,
                        "timestamp": row["_timestamp"],
                    }
                )

        best_read = max(
            plate_reads,
            key=lambda item: item["confidence"],
            default=None,
        )

        # ---------------------------------------------------------
        # Build matcher-ready local-track record
        # ---------------------------------------------------------
        record: dict[str, Any] = {
            "camera_id": camera_id,
            "local_track_id": first.get("local_track_id"),
            "first_timestamp": first["_timestamp"],
            "last_timestamp": last["_timestamp"],
            "source": first.get("_source"),

            "embedding": embedding,

            "plate_text": best_read["plate"] if best_read else None,
            "ocr_confidence": (
                best_read["confidence"] if best_read else None
            ),
            "plate_alternatives": (
                best_read["alternatives"] if best_read else []
            ),

            "plate_history": plate_reads,

            # NEW: preserve original Member 1 event identity.
            "event_ids": event_ids,
            "observations": observations,

            "observation_count": len(rows),
        }

        # Preserve optional road/direction/location fields from upstream.
        for field in (
            "road_segment_id",
            "direction",
            "latitude",
            "longitude",
        ):
            values = [
                row.get(field)
                for row in rows
                if row.get(field) is not None
            ]

            if values:
                record[field] = (
                    values[-1]
                    if field in ("latitude", "longitude")
                    else values[0]
                )

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

def apply_verification_corrections_to_trajectories(
    trajectories: list[dict[str, Any]],
    verification_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Merge trajectories when verification proves that two camera-local
    identities belong to the same vehicle.

    Example:
        V001 -> DL01AB1234 from CAM_01
        V002 -> DL01AB1284 from CAM_02

    Verification:
        DL01AB1284 -> DL01AB1234

    Result:
        V001 -> DL01AB1234
        CAM_01 -> CAM_02
    """

    if not trajectories or not verification_results:
        return trajectories

    for correction in verification_results:

        if correction.get("verification_status") != "corrected":
            continue

        original_plate = correction.get("original_plate")
        corrected_plate = correction.get("corrected_plate")
        corrected_event_id = correction.get("event_id")

        if not original_plate or not corrected_plate:
            continue

        if original_plate == corrected_plate:
            continue

        # Find the trajectory containing the suspicious/corrected event.
        source_trajectory = None

        for trajectory in trajectories:
            event_ids = trajectory.get("event_ids", [])

            if corrected_event_id in event_ids:
                source_trajectory = trajectory
                break

            for observation in trajectory.get("event_observations", []):
                if observation.get("event_id") == corrected_event_id:
                    source_trajectory = trajectory
                    break

            if source_trajectory:
                break

        if source_trajectory is None:
            continue

        # Find the existing trajectory that already has the corrected plate.
        target_trajectory = None

        for trajectory in trajectories:
            if trajectory is source_trajectory:
                continue

            if trajectory.get("plate") == corrected_plate:
                target_trajectory = trajectory
                break

        if target_trajectory is None:
            continue

        source_vehicle_id = source_trajectory.get("vehicle_id")
        target_vehicle_id = target_trajectory.get("vehicle_id")
        target_trajectory_id = target_trajectory.get("trajectory_id")

                # Move all source observations into the target trajectory.
        source_observations = source_trajectory.get("observations", [])
        target_observations = target_trajectory.get("observations", [])

        merged_observations = (
            target_observations + source_observations
        )

        # Correct the identity of observations moved during verification.
        for observation in merged_observations:
            observation["vehicle_id"] = target_vehicle_id
            observation["trajectory_id"] = target_trajectory_id
            observation["status"] = "verified"

        target_trajectory["observations"] = merged_observations

        # Sort observations chronologically.
        target_trajectory["observations"].sort(
            key=lambda item: item.get("first_timestamp", "")
        )

        # Merge event IDs.
        target_event_ids = target_trajectory.get("event_ids", [])
        source_event_ids = source_trajectory.get("event_ids", [])

        target_trajectory["event_ids"] = list(
            dict.fromkeys(
                target_event_ids + source_event_ids
            )
        )

        # Merge event observations.
        target_event_observations = target_trajectory.get(
            "event_observations", []
        )

        source_event_observations = source_trajectory.get(
            "event_observations", []
        )

        merged_event_observations = (
            target_event_observations
            + source_event_observations
        )

        # Correct the identity of every moved event.
        for event in merged_event_observations:
            event["vehicle_id"] = target_vehicle_id
            event["trajectory_id"] = target_trajectory_id

        merged_event_observations.sort(
            key=lambda item: item.get("timestamp", "")
        )

        target_trajectory["event_observations"] = (
            merged_event_observations
        )

        # Update the trajectory metadata.
        target_trajectory["plate"] = corrected_plate

        timestamps = [
            event.get("timestamp")
            for event in merged_event_observations
            if event.get("timestamp")
        ]

        if timestamps:
            timestamps.sort()
            target_trajectory["start_time"] = timestamps[0]
            target_trajectory["end_time"] = timestamps[-1]
            target_trajectory["first_timestamp"] = timestamps[0]
            target_trajectory["last_timestamp"] = timestamps[-1]

        target_trajectory["observation_count"] = len(
            target_trajectory["observations"]
        )

                # Merge camera sequence without duplicates.
        camera_sequence = []

        for event in merged_event_observations:
            camera_id = event.get("camera_id")

            if camera_id is not None and camera_id not in camera_sequence:
                camera_sequence.append(camera_id)

        target_trajectory["camera_sequence"] = camera_sequence
        # Merge road and direction information.
        target_trajectory["road_sequence"] = list(
            dict.fromkeys(
                target_trajectory.get("road_sequence", [])
                + source_trajectory.get("road_sequence", [])
            )
        )

        target_trajectory["direction_sequence"] = list(
            dict.fromkeys(
                target_trajectory.get("direction_sequence", [])
                + source_trajectory.get("direction_sequence", [])
            )
        )

        # Keep the target/global vehicle identity.
        target_trajectory["vehicle_id"] = target_vehicle_id
        target_trajectory["trajectory_id"] = target_trajectory_id

        # Remove the duplicate trajectory.
        trajectories.remove(source_trajectory)

        print(
            f"[VERIFICATION] Merged {source_vehicle_id} "
            f"into {target_vehicle_id}: "
            f"{original_plate} -> {corrected_plate}"
        )

    return trajectories

def match_tracked_frames(
    tracked_frames: Iterable[dict[str, Any]],
    matcher: CrossCameraMatcher | None = None,
    reconstructor: TrajectoryReconstructor | None = None,
) -> dict[str, Any]:
    """
    Prepare completed tracks, run cross-camera matching, and reconstruct
    ordered vehicle trajectories.

    Pipeline:
        Member 1/2/3 frame outputs
            -> completed local tracks
            -> cross-camera vehicle identity
            -> ordered trajectories

    The original matcher result is preserved. Trajectory reconstruction
    is added as a downstream M3 stage.
    """

    records = prepare_track_records(tracked_frames)

    matcher_obj = (
        matcher
        if matcher is not None
        else CrossCameraMatcher()
    )

    result = matcher_obj.match(records)

    # ---------------------------------------------------------
    # Trajectory reconstruction
    # ---------------------------------------------------------
    reconstructor_obj = (
        reconstructor
        if reconstructor is not None
        else TrajectoryReconstructor()
    )

    trajectory_result = reconstructor_obj.reconstruct(
        result
    )

    # ---------------------------------------------------------
    # Preserve all existing matcher outputs and add the
    # reconstructed trajectory layer.
    # ---------------------------------------------------------
    result["track_records"] = records
    result["trajectories"] = trajectory_result.get(
        "trajectories",
        [],
    )
    result["trajectory_skipped"] = trajectory_result.get(
        "skipped",
        [],
    )

    return result




def verification_payloads(match_result: dict[str, Any]) -> list[dict[str, Any]]:
    """Return Member 4-ready suspicious/supporting event payloads.

    For each plausible plate-mismatch candidate, the lower-confidence OCR
    observation is presented as the suspicious event and the other observation
    is included as supporting evidence. The original OCR values are preserved.
    """
    payloads: list[dict[str, Any]] = []

    matches = match_result.get("matches", [])
    if not isinstance(matches, list):
        return []

    for match in matches:
        if not isinstance(match, dict):
            continue

        candidate = match.get("verification_candidate")
        if not isinstance(candidate, dict):
            continue

        event = candidate.get("event")
        supporting = candidate.get("supporting_event")

        if not isinstance(event, dict) or not isinstance(supporting, dict):
            continue

        # Lower-confidence OCR reading becomes the suspicious event.
        if float(supporting.get("ocr_confidence", 0.0)) < float(
            event.get("ocr_confidence", 0.0)
        ):
            event, supporting = supporting, event

        suspicious = dict(event)

        # Preserve supporting evidence.
        suspicious["nearby_events"] = [dict(supporting)]

        # Preserve matcher evidence for the verification layer.
        suspicious["match_score"] = dict(
            candidate.get("match_score", match.get("match_score", {}))
        )
        suspicious["verification_reason"] = candidate.get("reason")

        payloads.append(suspicious)

    return payloads
