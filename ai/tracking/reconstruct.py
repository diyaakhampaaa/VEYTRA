"""
Deterministic trajectory reconstruction from matched local tracks.

Consumes ``CrossCameraMatcher.match()`` output (or a bare track list) and
builds one ordered journey per ``vehicle_id``. Does not import matcher,
tracker, or reid. Does not interpolate positions or invent cameras.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

DEFAULT_GAP_THRESHOLD = 120.0


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _empty_result(error: str = "invalid_match_result") -> dict[str, Any]:
    return {"trajectories": [], "skipped": [], "error": error}


def _extract_tracks(match_result: Any) -> list[Any] | None:
    if isinstance(match_result, list):
        return match_result
    if isinstance(match_result, dict) and "tracks" in match_result:
        tracks = match_result.get("tracks")
        if isinstance(tracks, list):
            return tracks
        return None
    return None


def _sort_key(track: dict[str, Any]) -> tuple:
    first = _parse_timestamp(track.get("first_timestamp"))
    last = _parse_timestamp(track.get("last_timestamp"))

    # Parsed datetimes are comparable once timezone-aware.
    return (
        first or datetime.min.replace(tzinfo=timezone.utc),
        last or datetime.min.replace(tzinfo=timezone.utc),
        str(track.get("camera_id", "")),
        str(track.get("local_track_id", "")),
    )


def _unique_adjacent(values: list[Any]) -> list[Any]:
    out: list[Any] = []

    for value in values:
        if value is None:
            continue

        if not out or out[-1] != value:
            out.append(value)

    return out


def _agreed_direction(values: list[Any]) -> Any:
    present = [v for v in values if v is not None]

    if not present:
        return None

    first = present[0]

    if all(v == first for v in present):
        return first

    return None


def _gap_seconds(earlier_last: datetime, later_first: datetime) -> float:
    return max(0.0, (later_first - earlier_last).total_seconds())


def _score_summary(
    observations: list[dict[str, Any]],
    matches: list[dict[str, Any]],
    vehicle_id: Any,
) -> dict[str, Any]:
    """Aggregate accepted matcher evidence for one reconstructed trajectory."""

    keys = {
        "reid_similarity": "appearance",
        "plate_similarity": "plate",
        "temporal_score": "time",
        "route_score": "spatial",
    }

    values: dict[str, list[float]] = {key: [] for key in keys}

    observation_keys = {
        (obs.get("camera_id"), obs.get("local_track_id"))
        for obs in observations
    }

    for match in matches:
        if not isinstance(match, dict) or match.get("vehicle_id") != vehicle_id:
            continue

        a = (
            match.get("camera_id_a"),
            match.get("local_track_id_a"),
        )

        b = (
            match.get("camera_id_b"),
            match.get("local_track_id_b"),
        )

        if a not in observation_keys and b not in observation_keys:
            continue

        score = match.get("match_score")

        if not isinstance(score, dict):
            continue

        for output_key, input_key in keys.items():
            value = score.get(input_key)

            if isinstance(value, (int, float)):
                values[output_key].append(
                    max(0.0, min(1.0, float(value)))
                )

    summary: dict[str, Any] = {}

    for output_key, items in values.items():
        summary[output_key] = (
            round(sum(items) / len(items), 4)
            if items
            else 1.0
        )

    return summary


def _build_event_observations(
    observations: list[dict[str, Any]],
    vehicle_id: Any,
    trajectory_id: str,
) -> list[dict[str, Any]]:
    """
    Extract original event-level observations from reconstructed
    local-track observations.

    The original event_id is preserved so downstream verification,
    correction, logging, and dashboard layers can trace a trajectory
    observation back to the exact detection/OCR event.

    No event IDs are invented.
    """

    event_observations: list[dict[str, Any]] = []
    seen_event_ids: set[Any] = set()

    for track in observations:

        # Preferred source:
        # ai.tracking.integration.prepare_track_records()
        #
        # This contains the original event-level records.
        nested_events = track.get("observations", [])

        if isinstance(nested_events, list):
            for event in nested_events:

                if not isinstance(event, dict):
                    continue

                event_id = event.get("event_id")

                if not event_id or event_id in seen_event_ids:
                    continue

                event_record = dict(event)

                # Preserve trajectory identity without changing
                # the original event identity.
                event_record["vehicle_id"] = vehicle_id
                event_record["trajectory_id"] = trajectory_id

                event_observations.append(event_record)
                seen_event_ids.add(event_id)

        # Fallback:
        # Some track records may contain event_ids without the
        # complete nested event records.
        event_ids = track.get("event_ids", [])

        if isinstance(event_ids, list):
            for event_id in event_ids:

                if not event_id or event_id in seen_event_ids:
                    continue

                event_observations.append(
                    {
                        "event_id": event_id,
                        "vehicle_id": vehicle_id,
                        "trajectory_id": trajectory_id,
                        "camera_id": track.get("camera_id"),
                        "local_track_id": track.get("local_track_id"),
                        "timestamp": track.get("first_timestamp"),
                    }
                )

                seen_event_ids.add(event_id)

    # Keep event order deterministic and chronological.
    event_observations.sort(
        key=lambda event: (
            _parse_timestamp(event.get("timestamp"))
            or datetime.min.replace(tzinfo=timezone.utc),
            str(event.get("camera_id", "")),
            str(event.get("event_id", "")),
        )
    )

    return event_observations


class TrajectoryReconstructor:
    """Build ordered journeys from matcher track records."""

    def __init__(
        self,
        gap_threshold: float = DEFAULT_GAP_THRESHOLD,
    ) -> None:
        if gap_threshold < 0:
            raise ValueError("gap_threshold must be >= 0")

        self.gap_threshold = gap_threshold

    def reconstruct(self, match_result: Any) -> dict[str, Any]:
        """Accept a ``match()`` dict or a list of tracks. Never raises."""

        tracks = _extract_tracks(match_result)

        if tracks is None:
            return _empty_result()

        matches = (
            match_result.get("matches", [])
            if (
                isinstance(match_result, dict)
                and isinstance(
                    match_result.get("matches", []),
                    list,
                )
            )
            else []
        )

        skipped: list[dict[str, Any]] = []
        valid: list[dict[str, Any]] = []

        for raw in tracks:

            if not isinstance(raw, dict):
                continue

            if raw.get("vehicle_id") is None:
                skipped.append(dict(raw))
                continue

            if (
                raw.get("camera_id") is None
                or raw.get("local_track_id") is None
            ):
                skipped.append(dict(raw))
                continue

            first = _parse_timestamp(
                raw.get("first_timestamp")
            )

            last = _parse_timestamp(
                raw.get("last_timestamp")
            )

            if first is None and last is None:
                skipped.append(dict(raw))
                continue

            row = dict(raw)

            if first is None:
                row["first_timestamp"] = row.get(
                    "last_timestamp"
                )

            if last is None:
                row["last_timestamp"] = row.get(
                    "first_timestamp"
                )

            valid.append(row)

        vehicle_order: list[Any] = []
        seen_vehicles: set[Any] = set()

        for track in valid:
            vid = track["vehicle_id"]

            if vid not in seen_vehicles:
                seen_vehicles.add(vid)
                vehicle_order.append(vid)

        grouped: dict[
            Any,
            list[dict[str, Any]],
        ] = {
            vid: []
            for vid in vehicle_order
        }

        for track in valid:
            grouped[track["vehicle_id"]].append(track)

        trajectories: list[dict[str, Any]] = []

        for index, vehicle_id in enumerate(
            vehicle_order,
            start=1,
        ):
            trajectory_id = f"T{index:03d}"

            ordered = sorted(
                grouped[vehicle_id],
                key=_sort_key,
            )

            unique: list[dict[str, Any]] = []

            seen_obs: set[
                tuple[Any, Any, Any]
            ] = set()

            for track in ordered:

                key = (
                    track.get("vehicle_id"),
                    track.get("camera_id"),
                    track.get("local_track_id"),
                )

                if key in seen_obs:
                    continue

                seen_obs.add(key)
                unique.append(track)

            observations: list[dict[str, Any]] = []

            for track in unique:
                obs = dict(track)

                obs["vehicle_id"] = vehicle_id
                obs["trajectory_id"] = trajectory_id
                obs["status"] = "observed"

                observations.append(obs)

            # ---------------------------------------------------------
            # NEW:
            # Preserve the original event-level identity.
            # ---------------------------------------------------------

            event_observations = _build_event_observations(
                observations=observations,
                vehicle_id=vehicle_id,
                trajectory_id=trajectory_id,
            )

            event_ids = [
                event["event_id"]
                for event in event_observations
                if event.get("event_id")
            ]

            # ---------------------------------------------------------
            # Existing leg reconstruction.
            # ---------------------------------------------------------

            legs: list[dict[str, Any]] = []
            gap_count = 0

            for i in range(len(observations) - 1):

                a = observations[i]
                b = observations[i + 1]

                a_last = _parse_timestamp(
                    a.get("last_timestamp")
                )

                b_first = _parse_timestamp(
                    b.get("first_timestamp")
                )

                gap = (
                    0.0
                    if a_last is None or b_first is None
                    else _gap_seconds(
                        a_last,
                        b_first,
                    )
                )

                status = (
                    "gap"
                    if gap > self.gap_threshold
                    else "consecutive"
                )

                if status == "gap":
                    gap_count += 1

                legs.append(
                    {
                        "from_camera_id": a.get(
                            "camera_id"
                        ),
                        "to_camera_id": b.get(
                            "camera_id"
                        ),
                        "from_local_track_id": a.get(
                            "local_track_id"
                        ),
                        "to_local_track_id": b.get(
                            "local_track_id"
                        ),
                        "from_timestamp": a.get(
                            "last_timestamp"
                        ),
                        "to_timestamp": b.get(
                            "first_timestamp"
                        ),
                        "gap_seconds": gap,
                        "status": status,
                        "road_from": a.get(
                            "road_segment_id"
                        ),
                        "road_to": b.get(
                            "road_segment_id"
                        ),
                    }
                )

            roads = _unique_adjacent(
                [
                    obs.get("road_segment_id")
                    for obs in observations
                ]
            )

            directions = [
                obs.get("direction")
                for obs in observations
            ]

            sources = [
                obs.get("source")
                for obs in observations
                if obs.get("source") is not None
            ]

            first_obs = observations[0]
            last_obs = observations[-1]

            plate_values = [
                obs.get(
                    "plate_text",
                    obs.get("plate"),
                )
                for obs in observations
                if obs.get(
                    "plate_text",
                    obs.get("plate"),
                )
            ]

            plate = (
                plate_values[0]
                if (
                    plate_values
                    and all(
                        v == plate_values[0]
                        for v in plate_values
                    )
                )
                else (
                    max(
                        plate_values,
                        key=lambda value: next(
                            (
                                float(
                                    obs.get(
                                        "ocr_confidence",
                                        obs.get(
                                            "confidence",
                                            0.0,
                                        ),
                                    )
                                    or 0.0
                                )
                                for obs in observations
                                if obs.get(
                                    "plate_text",
                                    obs.get("plate"),
                                )
                                == value
                            ),
                            0.0,
                        ),
                    )
                    if plate_values
                    else None
                )
            )

            trajectories.append(
                {
                    "vehicle_id": vehicle_id,
                    "trajectory_id": trajectory_id,
                    "plate": plate,

                    # Existing ordered camera journey.
                    "camera_sequence": [
                        obs.get("camera_id")
                        for obs in observations
                    ],

                    "start_time": min(
                        obs["first_timestamp"]
                        for obs in observations
                    ),

                    "end_time": max(
                        obs["last_timestamp"]
                        for obs in observations
                    ),

                    "match_score": _score_summary(
                        observations,
                        matches,
                        vehicle_id,
                    ),

                    "source": (
                        sources[0]
                        if sources
                        else None
                    ),

                    "first_timestamp": min(
                        obs["first_timestamp"]
                        for obs in observations
                    ),

                    "last_timestamp": max(
                        obs["last_timestamp"]
                        for obs in observations
                    ),

                    "observation_count": len(
                        observations
                    ),

                    # Existing road information.
                    "road_sequence": roads,

                    "direction_sequence": _unique_adjacent(
                        directions
                    ),

                    "direction": _agreed_direction(
                        directions
                    ),

                    "gap_count": gap_count,

                    # Existing local-track observations.
                    "observations": observations,

                    # NEW:
                    # Original M1/M2 event IDs.
                    "event_ids": event_ids,

                    # NEW:
                    # Full event-level provenance records.
                    "event_observations": event_observations,

                    # Existing camera-to-camera transitions.
                    "legs": legs,
                }
            )

        return {
            "trajectories": trajectories,
            "skipped": skipped,
        }


def reconstruct(
    match_result: Any,
    gap_threshold: float = DEFAULT_GAP_THRESHOLD,
) -> dict[str, Any]:
    """Module-level wrapper around ``TrajectoryReconstructor.reconstruct``."""

    return TrajectoryReconstructor(
        gap_threshold=gap_threshold
    ).reconstruct(match_result)