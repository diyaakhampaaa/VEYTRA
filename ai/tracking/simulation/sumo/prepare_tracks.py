"""
Convert frame-level SUMO camera observations into completed local tracks.

IMPORTANT:
- This module reads ONLY camera_observations.json.
- It must never read ground_truth.json.
- It preserves camera-local identity.
- One output track represents one (camera_id, local_track_id).
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_INPUT = Path(__file__).resolve().parent / "outputs" / "camera_observations.json"


def _parse_timestamp(value: str) -> datetime:
    """Parse an ISO timestamp."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _dominant_value(values: list[Any]) -> Any:
    """Return the most common non-empty value."""
    valid = [value for value in values if value not in (None, "")]
    if not valid:
        return None

    return Counter(valid).most_common(1)[0][0]


def _highest_confidence_plate(observations: list[dict[str, Any]]) -> str | None:
    """
    Select the plate associated with the highest OCR confidence.

    If confidence is unavailable, fall back to the most common plate.
    """
    candidates = []

    for observation in observations:
        plate = observation.get("plate_number")

        if not plate:
            continue

        confidence = observation.get("ocr_confidence")

        if confidence is None:
            confidence = 0.0

        candidates.append((float(confidence), plate))

    if not candidates:
        return None

    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def prepare_tracks(
    observations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Aggregate frame-level observations into completed local tracks.

    Grouping key:
        (camera_id, local_track_id)

    No global vehicle identity is inferred here.
    """

    grouped: dict[tuple[str, int], list[dict[str, Any]]] = {}

    for observation in observations:
        camera_id = observation.get("camera_id")
        local_track_id = observation.get("local_track_id")

        if camera_id is None or local_track_id is None:
            continue

        try:
            local_track_id = int(local_track_id)
        except (TypeError, ValueError):
            continue

        timestamp = observation.get("timestamp")

        if not timestamp:
            continue

        try:
            _parse_timestamp(timestamp)
        except (TypeError, ValueError):
            continue

        key = (str(camera_id), local_track_id)
        grouped.setdefault(key, []).append(observation)

    tracks: list[dict[str, Any]] = []

    for (camera_id, local_track_id), group in grouped.items():

        ordered = sorted(
            group,
            key=lambda observation: _parse_timestamp(
                observation["timestamp"]
            ),
        )

        first = ordered[0]
        last = ordered[-1]

        timestamps = [observation["timestamp"] for observation in ordered]

        first_timestamp = min(
            timestamps,
            key=_parse_timestamp,
        )

        last_timestamp = max(
            timestamps,
            key=_parse_timestamp,
        )

        plate_text = _highest_confidence_plate(ordered)

        ocr_confidences = [
            float(observation["ocr_confidence"])
            for observation in ordered
            if observation.get("ocr_confidence") is not None
        ]

        vehicle_confidences = [
            float(observation["vehicle_confidence"])
            for observation in ordered
            if observation.get("vehicle_confidence") is not None
        ]

        latitudes = [
            observation["latitude"]
            for observation in ordered
            if observation.get("latitude") is not None
        ]

        longitudes = [
            observation["longitude"]
            for observation in ordered
            if observation.get("longitude") is not None
        ]

        directions = [
            observation.get("direction")
            for observation in ordered
            if observation.get("direction")
        ]

        vehicle_types = [
            observation.get("vehicle_type")
            for observation in ordered
            if observation.get("vehicle_type")
        ]

        sources = [
            observation.get("source")
            for observation in ordered
            if observation.get("source")
        ]

        track: dict[str, Any] = {
            "camera_id": camera_id,
            "local_track_id": local_track_id,

            "first_timestamp": first_timestamp,
            "last_timestamp": last_timestamp,

            "plate_text": plate_text,

            "vehicle_type": _dominant_value(vehicle_types),
            "direction": _dominant_value(directions),

            "latitude": (
                sum(latitudes) / len(latitudes)
                if latitudes
                else None
            ),
            "longitude": (
                sum(longitudes) / len(longitudes)
                if longitudes
                else None
            ),

            "ocr_confidence": (
                sum(ocr_confidences) / len(ocr_confidences)
                if ocr_confidences
                else None
            ),
            "vehicle_confidence": (
                sum(vehicle_confidences) / len(vehicle_confidences)
                if vehicle_confidences
                else None
            ),

            "source": _dominant_value(sources),

            "observation_count": len(ordered),

            # Preserve event IDs for evaluation/debugging.
            # Matcher/reconstruction do not depend on them.
            "event_ids": [
                observation.get("event_id")
                for observation in ordered
                if observation.get("event_id")
            ],

            # Keep the first/last raw observations available for
            # debugging without exposing hidden ground truth.
            "first_observation": first,
            "last_observation": last,
        }

        tracks.append(track)

    tracks.sort(
        key=lambda track: (
            track["camera_id"],
            track["local_track_id"],
        )
    )

    return tracks


def load_observations(input_path: Path = DEFAULT_INPUT) -> list[dict[str, Any]]:
    """Load public camera observations."""
    with input_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    observations = data.get("observations", [])

    if not isinstance(observations, list):
        raise ValueError("Expected 'observations' to be a list.")

    return observations


def save_tracks(
    tracks: list[dict[str, Any]],
    output_path: Path,
) -> None:
    """Save prepared tracks."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            {"tracks": tracks},
            file,
            indent=2,
        )


def main() -> None:
    input_path = DEFAULT_INPUT

    output_path = (
        Path(__file__).resolve().parent
        / "outputs"
        / "prepared_tracks.json"
    )

    observations = load_observations(input_path)
    tracks = prepare_tracks(observations)

    save_tracks(tracks, output_path)

    print("Track preparation completed.")
    print(f"Public observations: {len(observations)}")
    print(f"Completed local tracks: {len(tracks)}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()