"""Cross-camera identity matching for completed local tracks.

This module does not import ``tracker.py`` or ``reid.py``. It reads the
same field names those stages emit and assigns a global ``vehicle_id``.

Matching uses appearance (optional), time, optional spatial/travel
feasibility, and optional plate text. OCR is never required.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

from rapidfuzz.fuzz import ratio

EARTH_RADIUS_KM = 6371.0

WEIGHT_APPEARANCE = 0.60
WEIGHT_TIME = 0.25
WEIGHT_SPATIAL = 0.15

DEFAULT_MIN_APPEARANCE = 0.70
DEFAULT_MAX_TIME_GAP = 120.0
DEFAULT_MAX_SPEED_KMH = 120.0
DEFAULT_MIN_OVERALL = 0.55


def _empty_match_result(error: str = "invalid_tracks") -> dict[str, Any]:
    return {"tracks": [], "matches": [], "error": error}


def _copy_track(track: dict[str, Any]) -> dict[str, Any]:
    return dict(track)


def _normalize_plate(value: Any) -> str | None:
    if not isinstance(value, str):
        return None

    compact = "".join(ch for ch in value.upper() if ch.isalnum())
    return compact or None


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


def _parse_coordinates(value: Any) -> tuple[float, float] | None:
    if isinstance(value, dict):
        lat = value.get("latitude")
        lon = value.get("longitude")
    elif isinstance(value, (list, tuple)) and len(value) >= 2:
        lat, lon = value[0], value[1]
    else:
        return None

    try:
        lat = float(lat)
        lon = float(lon)
    except (TypeError, ValueError):
        return None

    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        return None

    return lat, lon


def _haversine_km(
    point_a: tuple[float, float],
    point_b: tuple[float, float],
) -> float:
    lat1, lon1 = map(math.radians, point_a)
    lat2, lon2 = map(math.radians, point_b)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    hav = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2.0) ** 2
    )

    return 2.0 * EARTH_RADIUS_KM * math.asin(
        min(1.0, math.sqrt(hav))
    )


def _as_float_vector(value: Any) -> list[float] | None:
    if not isinstance(value, (list, tuple)):
        return None

    result: list[float] = []

    for item in value:
        try:
            result.append(float(item))
        except (TypeError, ValueError):
            return None

    return result if result else None


def _cosine(
    vector_a: list[float],
    vector_b: list[float],
) -> float | None:
    if len(vector_a) != len(vector_b):
        return None

    dot = sum(a * b for a, b in zip(vector_a, vector_b))
    norm_a = math.sqrt(sum(a * a for a in vector_a))
    norm_b = math.sqrt(sum(b * b for b in vector_b))

    if norm_a <= 0.0 or norm_b <= 0.0:
        return None

    value = dot / (norm_a * norm_b)

    return max(-1.0, min(1.0, value))


def _score_payload(
    *,
    overall: float | None,
    accepted: bool,
    appearance: float | None,
    time: float | None,
    spatial: float | None,
    plate: float | None,
    missing: list[str],
    reject_reason: str | None,
    verification_eligible: bool = False,
) -> dict[str, Any]:
    return {
        "overall": overall,
        "accepted": accepted,
        "appearance": appearance,
        "time": time,
        "spatial": spatial,
        "plate": plate,
        "missing": missing,
        "reject_reason": reject_reason,
        "verification_eligible": verification_eligible,
    }


def _weighted_mean(
    parts: list[tuple[float, float]],
) -> float | None:
    """``parts`` is (weight, value); null components are already omitted."""
    if not parts:
        return None

    total_w = sum(weight for weight, _ in parts)

    if total_w <= 0.0:
        return None

    return sum(weight * value for weight, value in parts) / total_w


class CrossCameraMatcher:
    """Assign global ``vehicle_id`` values across cameras.

    Parameters
    ----------
    min_appearance, max_time_gap, max_speed_kmh, min_overall:
        Default gates from the matcher design.
    camera_links:
        Optional ``{(cam_a, cam_b): {"min_seconds", "max_seconds"}}``.
        Enforced only when a pair is present in the map (either order).
    weights:
        Optional override of appearance/time/spatial weights.
    """

    def __init__(
        self,
        min_appearance: float = DEFAULT_MIN_APPEARANCE,
        max_time_gap: float = DEFAULT_MAX_TIME_GAP,
        max_speed_kmh: float = DEFAULT_MAX_SPEED_KMH,
        min_overall: float = DEFAULT_MIN_OVERALL,
        camera_links: dict[tuple[str, str], dict[str, float]] | None = None,
        weight_appearance: float = WEIGHT_APPEARANCE,
        weight_time: float = WEIGHT_TIME,
        weight_spatial: float = WEIGHT_SPATIAL,
        allow_missing_appearance: bool = False,
    ) -> None:
        self.min_appearance = min_appearance
        self.max_time_gap = max_time_gap
        self.max_speed_kmh = max_speed_kmh
        self.min_overall = min_overall
        self.camera_links = camera_links or {}
        self.weight_appearance = weight_appearance
        self.weight_time = weight_time
        self.weight_spatial = weight_spatial
        self.allow_missing_appearance = allow_missing_appearance

    def _spatial_score(
        self,
        track_a: dict[str, Any],
        track_b: dict[str, Any],
        gap_seconds: float,
    ) -> tuple[float | None, str | None]:
        point_a = _parse_coordinates(
            track_a.get("location")
            or track_a.get("coordinates")
        )

        point_b = _parse_coordinates(
            track_b.get("location")
            or track_b.get("coordinates")
        )

        if point_a is None or point_b is None:
            return None, None

        distance_km = _haversine_km(point_a, point_b)

        if gap_seconds <= 0.0:
            if distance_km > 0.01:
                return 0.0, "impossible_travel"
            return 1.0, None

        max_distance_km = (
            self.max_speed_kmh * gap_seconds / 3600.0
        )

        if max_distance_km <= 0.0:
            return 0.0, "impossible_travel"

        if distance_km > max_distance_km:
            return 0.0, "impossible_travel"

        ratio_value = distance_km / max_distance_km

        return max(0.0, 1.0 - ratio_value), None

    def score_pair(
        self,
        track_a: Any,
        track_b: Any,
    ) -> dict[str, Any]:
        """Score one pair. Never raises. ``accepted`` is the hard decision."""

        if not isinstance(track_a, dict) or not isinstance(track_b, dict):
            return _score_payload(
                overall=None,
                accepted=False,
                appearance=None,
                time=None,
                spatial=None,
                plate=None,
                missing=["invalid_track"],
                reject_reason="invalid_track",
            )

        missing: list[str] = []

        cam_a = track_a.get("camera_id")
        cam_b = track_b.get("camera_id")

        if cam_a is None or cam_b is None:
            return _score_payload(
                overall=None,
                accepted=False,
                appearance=None,
                time=None,
                spatial=None,
                plate=None,
                missing=["missing_camera_id"],
                reject_reason="invalid_track",
            )

        if str(cam_a) == str(cam_b):
            return _score_payload(
                overall=None,
                accepted=False,
                appearance=None,
                time=None,
                spatial=None,
                plate=None,
                missing=[],
                reject_reason="same_camera",
            )

        t_a0 = _parse_timestamp(track_a.get("first_timestamp"))
        t_a1 = _parse_timestamp(track_a.get("last_timestamp"))
        t_b0 = _parse_timestamp(track_b.get("first_timestamp"))
        t_b1 = _parse_timestamp(track_b.get("last_timestamp"))

        if (
            None in (t_a0, t_a1, t_b0, t_b1)
            or t_a1 < t_a0
            or t_b1 < t_b0
        ):
            return _score_payload(
                overall=None,
                accepted=False,
                appearance=None,
                time=None,
                spatial=None,
                plate=None,
                missing=["invalid_time"],
                reject_reason="invalid_time",
            )

        if t_a0 <= t_b0:
            earlier_last = t_a1
            later_first = t_b0
        else:
            earlier_last = t_b1
            later_first = t_a0

        gap = max(
            0.0,
            (later_first - earlier_last).total_seconds(),
        )

        if gap > self.max_time_gap:
            return _score_payload(
                overall=None,
                accepted=False,
                appearance=None,
                time=None,
                spatial=None,
                plate=None,
                missing=[],
                reject_reason="time_gap",
            )

        time_score = (
            1.0
            if self.max_time_gap <= 0.0
            else max(
                0.0,
                1.0 - (gap / self.max_time_gap),
            )
        )

        spatial_score, spatial_reject = self._spatial_score(
            track_a,
            track_b,
            gap,
        )

        if spatial_reject is not None:
            return _score_payload(
                overall=None,
                accepted=False,
                appearance=None,
                time=time_score,
                spatial=spatial_score,
                plate=None,
                missing=[],
                reject_reason=spatial_reject,
            )

        if spatial_score is None:
            missing.append("missing_spatial")

        vec_a = _as_float_vector(
            track_a.get("embedding")
        )
        vec_b = _as_float_vector(
            track_b.get("embedding")
        )

        if vec_a is None or vec_b is None:
            appearance = None
            missing.append("missing_embedding")
        else:
            appearance = _cosine(vec_a, vec_b)

            if appearance is None:
                missing.append("missing_embedding")

        raw_plate_a = track_a.get("plate_text")

        if raw_plate_a is None:
            raw_plate_a = track_a.get("plate")

        raw_plate_b = track_b.get("plate_text")

        if raw_plate_b is None:
            raw_plate_b = track_b.get("plate")

        plate_a = _normalize_plate(raw_plate_a)
        plate_b = _normalize_plate(raw_plate_b)

        if plate_a is None or plate_b is None:
            plate = None
            missing.append("missing_plate")
        elif plate_a != plate_b:
            # Use character-level similarity instead of treating
            # every non-identical plate as a 0% match.
            plate = ratio(plate_a, plate_b) / 100.0
        else:
            plate = 1.0

        plate_accept = plate == 1.0
        plate_mismatch = (
            plate is not None
            and plate < 1.0
        )

        if (
            appearance is None
            and not self.allow_missing_appearance
            and not plate_accept
        ):
            return _score_payload(
                overall=None,
                accepted=False,
                appearance=appearance,
                time=time_score,
                spatial=spatial_score,
                plate=plate,
                missing=missing,
                reject_reason="insufficient_cues",
            )

        if (
            appearance is not None
            and appearance < self.min_appearance
            and not plate_accept
        ):
            return _score_payload(
                overall=None,
                accepted=False,
                appearance=appearance,
                time=time_score,
                spatial=spatial_score,
                plate=plate,
                missing=missing,
                reject_reason="appearance_below_threshold",
            )

        parts: list[tuple[float, float]] = []

        if appearance is not None:
            parts.append(
                (
                    self.weight_appearance,
                    appearance,
                )
            )

        parts.append(
            (
                self.weight_time,
                time_score,
            )
        )

        if spatial_score is not None:
            parts.append(
                (
                    self.weight_spatial,
                    spatial_score,
                )
            )

        overall = _weighted_mean(parts)

        if plate_accept:
            if overall is None:
                overall = 1.0
            else:
                overall = min(
                    1.0,
                    (overall + 1.0) / 2.0,
                )

        if overall is None or overall < self.min_overall:
            return _score_payload(
                overall=overall,
                accepted=False,
                appearance=appearance,
                time=time_score,
                spatial=spatial_score,
                plate=plate,
                missing=missing,
                reject_reason="overall_below_threshold",
            )

        # A plate disagreement is NOT a hard identity failure anymore.
        # It remains rejected as a MATCH, but if the non-plate cues are strong
        # enough, preserve it as a verification candidate for Member 4.
        if plate_mismatch:
            return _score_payload(
                overall=overall,
                accepted=False,
                appearance=appearance,
                time=time_score,
                spatial=spatial_score,
                plate=plate,
                missing=missing,
                reject_reason="plate_mismatch",
                verification_eligible=True,
            )

        return _score_payload(
            overall=overall,
            accepted=True,
            appearance=appearance,
            time=time_score,
            spatial=spatial_score,
            plate=plate,
            missing=missing,
            reject_reason=None,
        )

    @staticmethod
    def _verification_candidate(
        track_a: dict[str, Any],
        track_b: dict[str, Any],
        score: dict[str, Any],
    ) -> dict[str, Any]:
        """Build a Member 4-ready candidate using original event identity."""

        def event(track: dict[str, Any]) -> dict[str, Any]:
            raw_plate = track.get("plate_text")

            if raw_plate is None:
                raw_plate = track.get("plate")

            plate = _normalize_plate(raw_plate)

            confidence = track.get(
                "ocr_confidence",
                track.get("confidence"),
            )

            try:
                confidence = (
                    float(confidence)
                    if confidence is not None
                    else 0.0
                )
            except (TypeError, ValueError):
                confidence = 0.0

            observations = track.get("observations")

            selected_observation = None

            if isinstance(observations, list):
                for observation in observations:
                    if not isinstance(observation, dict):
                        continue

                    observation_plate = _normalize_plate(
                        observation.get("plate")
                    )

                    try:
                        observation_confidence = float(
                            observation.get(
                                "ocr_confidence",
                                0.0,
                            )
                        )
                    except (TypeError, ValueError):
                        observation_confidence = 0.0

                    if (
                        observation_plate == plate
                        and observation_confidence == confidence
                    ):
                        selected_observation = observation
                        break

            if (
                selected_observation is None
                and isinstance(observations, list)
            ):
                matching_observations = []

                for observation in observations:
                    if not isinstance(observation, dict):
                        continue

                    observation_plate = _normalize_plate(
                        observation.get("plate")
                    )

                    if observation_plate != plate:
                        continue

                    try:
                        observation_confidence = float(
                            observation.get(
                                "ocr_confidence",
                                0.0,
                            )
                        )
                    except (TypeError, ValueError):
                        observation_confidence = 0.0

                    matching_observations.append(
                        (
                            observation_confidence,
                            observation,
                        )
                    )

                if matching_observations:
                    matching_observations.sort(
                        key=lambda item: item[0],
                        reverse=True,
                    )

                    selected_observation = (
                        matching_observations[0][1]
                    )

            if selected_observation is not None:
                event_id = selected_observation.get(
                    "event_id"
                )

                timestamp = selected_observation.get(
                    "timestamp",
                    track.get("first_timestamp")
                    or track.get("last_timestamp"),
                )

                camera_id = selected_observation.get(
                    "camera_id",
                    track.get("camera_id"),
                )

            else:
                # If upstream did not provide an event_id, do not
                # invent one. Preserve the absence of identity.
                event_id = None

                timestamp = (
                    track.get("first_timestamp")
                    or track.get("last_timestamp")
                )

                camera_id = track.get("camera_id")

            return {
                "event_id": event_id,
                "camera_id": camera_id,
                "plate": plate,
                "ocr_confidence": confidence,
                "timestamp": timestamp,
                "reid_similarity": score.get(
                    "appearance"
                ),
            }

        return {
            "event": event(track_a),
            "supporting_event": event(track_b),
            "match_score": dict(score),
            "reason": "plausible_cross_camera_match_with_plate_mismatch",
        }

    def match(self, tracks: Any) -> dict[str, Any]:
        """Assign ``vehicle_id`` values. Invalid input never raises."""

        if tracks is None:
            return _empty_match_result("invalid_tracks")

        if not isinstance(tracks, list):
            return _empty_match_result("tracks_not_a_list")

        valid: list[tuple[int, dict[str, Any]]] = []
        skipped: list[dict[str, Any]] = []

        for index, raw in enumerate(tracks):
            if not isinstance(raw, dict):
                skipped.append(
                    {
                        "index": index,
                        "reason": "invalid_track",
                    }
                )
                continue

            track = _copy_track(raw)

            if not track.get("camera_id"):
                skipped.append(
                    {
                        "index": index,
                        "reason": "missing_camera_id",
                    }
                )
                continue

            valid.append((index, track))

        if not valid:
            return {
                "tracks": [],
                "matches": [],
                "skipped": skipped,
                "error": None,
            }

        assigned: dict[int, str] = {}
        matches: list[dict[str, Any]] = []

        next_vehicle_number = 1

        for index, track in valid:
            if index in assigned:
                continue

            vehicle_id = f"V{next_vehicle_number:03d}"
            next_vehicle_number += 1

            assigned[index] = vehicle_id

            track["vehicle_id"] = vehicle_id

        for i in range(len(valid)):
            index_a, track_a = valid[i]

            for j in range(i + 1, len(valid)):
                index_b, track_b = valid[j]

                score = self.score_pair(
                    track_a,
                    track_b,
                )

                if score.get("accepted"):
                    vehicle_id = assigned[index_a]

                    assigned[index_b] = vehicle_id
                    track_b["vehicle_id"] = vehicle_id

                    matches.append(
                        {
                            "track_a": index_a,
                            "track_b": index_b,
                            "vehicle_id": vehicle_id,
                            "match_score": score,
                        }
                    )

                elif score.get("verification_eligible"):
                    matches.append(
                        {
                            "track_a": index_a,
                            "track_b": index_b,
                            "vehicle_id": None,
                            "match_score": score,
                            "verification_candidate": self._verification_candidate(
                                track_a,
                                track_b,
                                score,
                            ),
                        }
                    )

        output_tracks = []

        for index, track in valid:
            output_tracks.append(
                {
                    "index": index,
                    **track,
                }
            )

        return {
            "tracks": output_tracks,
            "matches": matches,
            "skipped": skipped,
            "error": None,
        }