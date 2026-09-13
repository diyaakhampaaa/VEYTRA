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


def _as_float_vector(value: Any) -> list[float] | None:
    if not isinstance(value, (list, tuple)) or len(value) == 0:
        return None
    out: list[float] = []
    try:
        for item in value:
            out.append(float(item))
    except (TypeError, ValueError):
        return None
    return out


def _cosine(a: list[float], b: list[float]) -> float | None:
    if len(a) != len(b):
        return None
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for x, y in zip(a, b):
        dot += x * y
        norm_a += x * x
        norm_b += y * y
    if norm_a <= 0.0 or norm_b <= 0.0:
        return None
    cosine = dot / math.sqrt(norm_a * norm_b)
    return max(0.0, min(1.0, cosine))


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(a)))


def _coords(track: dict[str, Any]) -> tuple[float, float] | None:
    try:
        lat = float(track["latitude"])
        lon = float(track["longitude"])
    except (KeyError, TypeError, ValueError):
        return None
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        return None
    return lat, lon


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


def _weighted_mean(parts: list[tuple[float, float]]) -> float | None:
    """``parts`` is (weight, value); null components are already omitted."""
    if not parts:
        return None
    total_w = sum(weight for weight, _ in parts)
    if total_w <= 0.0:
        return None
    return sum(weight * value for weight, value in parts) / total_w


class _UnionFind:
    """Union-find that refuses to merge two tracks from the same camera."""

    def __init__(self, cameras: list[str]) -> None:
        n = len(cameras)
        self.parent = list(range(n))
        self.cameras: list[set[str]] = [{cam} for cam in cameras]

    def find(self, i: int) -> int:
        while self.parent[i] != i:
            self.parent[i] = self.parent[self.parent[i]]
            i = self.parent[i]
        return i

    def union(self, i: int, j: int) -> bool:
        ri, rj = self.find(i), self.find(j)
        if ri == rj:
            return True
        if self.cameras[ri] & self.cameras[rj]:
            return False
        self.parent[rj] = ri
        self.cameras[ri] = self.cameras[ri] | self.cameras[rj]
        return True


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

    def score_pair(self, track_a: Any, track_b: Any) -> dict[str, Any]:
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
        if None in (t_a0, t_a1, t_b0, t_b1) or t_a1 < t_a0 or t_b1 < t_b0:
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
            earlier_last, later_first = t_a1, t_b0
        else:
            earlier_last, later_first = t_b1, t_a0
        gap = max(0.0, (later_first - earlier_last).total_seconds())
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
        time_score = 1.0 if self.max_time_gap <= 0.0 else max(0.0, 1.0 - (gap / self.max_time_gap))

        spatial_score, spatial_reject = self._spatial_score(track_a, track_b, gap)
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

        vec_a = _as_float_vector(track_a.get("embedding"))
        vec_b = _as_float_vector(track_b.get("embedding"))
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
            plate = 0.0
        else:
            plate = 1.0

        plate_accept = plate == 1.0
        plate_mismatch = plate == 0.0
        if (appearance is None and not self.allow_missing_appearance and not plate_accept):
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
        if appearance is not None and appearance < self.min_appearance and not plate_accept:
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
            parts.append((self.weight_appearance, appearance))
        parts.append((self.weight_time, time_score))
        if spatial_score is not None:
            parts.append((self.weight_spatial, spatial_score))
        overall = _weighted_mean(parts)
        if plate_accept:
            if overall is None:
                overall = 1.0
            else:
                overall = min(1.0, (overall + 1.0) / 2.0)

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
        """Build a Member 4-ready candidate without changing identity labels."""
        def event(track: dict[str, Any]) -> dict[str, Any]:
            raw_plate = track.get("plate_text")
            if raw_plate is None:
                raw_plate = track.get("plate")
            plate = _normalize_plate(raw_plate)
            confidence = track.get("ocr_confidence", track.get("confidence"))
            try:
                confidence = float(confidence) if confidence is not None else 0.0
            except (TypeError, ValueError):
                confidence = 0.0
            return {
                "event_id": f"{track.get('camera_id')}:{track.get('local_track_id')}:{track.get('first_timestamp')}",
                "camera_id": track.get("camera_id"),
                "plate": plate,
                "ocr_confidence": max(0.0, min(1.0, confidence)),
                "timestamp": track.get("first_timestamp") or track.get("last_timestamp"),
                "reid_similarity": score.get("appearance"),
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
        for raw in tracks:
            if not isinstance(raw, dict):
                continue
            if raw.get("camera_id") is None or raw.get("local_track_id") is None:
                skipped.append(_copy_track(raw))
                continue
            valid.append((len(valid), _copy_track(raw)))

        if not valid:
            result: dict[str, Any] = {"tracks": skipped, "matches": []}
            if tracks != []:
                result["error"] = "no_valid_tracks"
            result["verification_candidates"] = []
            return result

        n = len(valid)
        uf = _UnionFind([str(track["camera_id"]) for _, track in valid])
        scored_pairs: list[tuple[float, int, int, dict[str, Any]]] = []
        verification_candidates: list[dict[str, Any]] = []

        for i in range(n):
            for j in range(i + 1, n):
                score = self.score_pair(valid[i][1], valid[j][1])
                if score.get("verification_eligible"):
                    verification_candidates.append(
                        self._verification_candidate(valid[i][1], valid[j][1], score)
                    )
                if not score["accepted"] or score["overall"] is None:
                    continue
                scored_pairs.append((float(score["overall"]), i, j, score))

        scored_pairs.sort(key=lambda item: item[0], reverse=True)
        unioned: dict[tuple[int, int], dict[str, Any]] = {}
        for overall, i, j, score in scored_pairs:
            if uf.union(i, j):
                unioned[(i, j)] = score

        roots: dict[int, str] = {}
        next_id = 1
        labeled: list[dict[str, Any]] = []
        best_for_index: dict[int, tuple[float, dict[str, Any], int]] = {}
        for (i, j), score in unioned.items():
            overall = float(score["overall"])
            for idx, other in ((i, j), (j, i)):
                prev = best_for_index.get(idx)
                if prev is None or overall > prev[0]:
                    best_for_index[idx] = (overall, score, other)

        for i, track in valid:
            root = uf.find(i)
            if root not in roots:
                roots[root] = f"V{next_id:03d}"
                next_id += 1
            out = _copy_track(track)
            out["vehicle_id"] = roots[root]
            best = best_for_index.get(i)
            out["match_score"] = best[1] if best is not None else None
            labeled.append(out)

        matches: list[dict[str, Any]] = []
        for (i, j), score in sorted(unioned.items(), key=lambda item: (item[0][0], item[0][1])):
            a = labeled[i]
            b = labeled[j]
            matches.append(
                {
                    "camera_id_a": a["camera_id"],
                    "local_track_id_a": a["local_track_id"],
                    "camera_id_b": b["camera_id"],
                    "local_track_id_b": b["local_track_id"],
                    "vehicle_id": a["vehicle_id"],
                    "match_score": score,
                }
            )

        return {
            "tracks": labeled + skipped,
            "matches": matches,
            "verification_candidates": verification_candidates,
        }

    def _lookup_link(self, cam_a: str, cam_b: str) -> dict[str, float] | None:
        if not self.camera_links:
            return None
        return self.camera_links.get((cam_a, cam_b)) or self.camera_links.get((cam_b, cam_a))

    def _spatial_score(
        self,
        track_a: dict[str, Any],
        track_b: dict[str, Any],
        gap: float,
    ) -> tuple[float | None, str | None]:
        """Return (spatial_score, reject_reason). Score may be null."""
        cam_a = str(track_a.get("camera_id"))
        cam_b = str(track_b.get("camera_id"))
        link = self._lookup_link(cam_a, cam_b)
        if link is not None:
            try:
                min_s = float(link.get("min_seconds", 0.0))
                max_s = float(link.get("max_seconds", self.max_time_gap))
            except (TypeError, ValueError):
                min_s, max_s = 0.0, self.max_time_gap
            if gap < min_s or gap > max_s:
                return None, "spatial_infeasible"
            span = max_s - min_s
            if span <= 0.0:
                spatial = 1.0
            else:
                mid = (min_s + max_s) / 2.0
                spatial = max(0.0, 1.0 - abs(gap - mid) / (span / 2.0))
            return spatial, None

        coords_a = _coords(track_a)
        coords_b = _coords(track_b)
        if coords_a is None or coords_b is None:
            return None, None

        distance = _haversine_km(coords_a[0], coords_a[1], coords_b[0], coords_b[1])
        if gap <= 0.0:
            if distance > 0.05:
                return None, "spatial_infeasible"
            return 1.0, None
        hours = gap / 3600.0
        speed = distance / hours
        if speed > self.max_speed_kmh:
            return None, "spatial_infeasible"
        if self.max_speed_kmh <= 0.0:
            return 1.0, None
        return max(0.0, 1.0 - (speed / self.max_speed_kmh)), None
