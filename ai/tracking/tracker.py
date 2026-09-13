"""Per-camera ByteTrack-style multi-object tracker for Member 1 detections.

Member 3 contract
-----------------
This module assigns ``local_track_id`` independently for every camera.
It implements the core ByteTrack association strategy:

1. Predict existing tracks with a constant-velocity motion model.
2. Split detections into high- and low-confidence groups.
3. Associate high-confidence detections first.
4. Associate remaining tracks with low-confidence detections.
5. Create new tracks from unmatched high-confidence detections.
6. Age unmatched tracks and remove them after ``max_age`` frames.

This keeps the existing VEYTRA JSON contract unchanged. Cross-camera
identity is intentionally handled later by ``matcher.py`` using plate,
Re-ID, temporal, spatial and route signals.

The implementation is dependency-free; it does not require a separate
tracking package. Re-ID remains a separate cross-camera component.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

BBox = list[float]


def bbox_iou(box_a: BBox, box_b: BBox) -> float:
    """Intersection-over-union for [x1, y1, x2, y2] boxes."""
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    inter_w = max(0.0, inter_x2 - inter_x1)
    inter_h = max(0.0, inter_y2 - inter_y1)
    inter = inter_w * inter_h
    if inter <= 0:
        return 0.0
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def is_valid_bbox(value: Any) -> bool:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        return False
    try:
        x1, y1, x2, y2 = (float(v) for v in value)
    except (TypeError, ValueError):
        return False
    return x2 > x1 and y2 > y1


def _center(box: BBox) -> tuple[float, float]:
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def _velocity(box_a: BBox, box_b: BBox) -> tuple[float, float]:
    ax, ay = _center(box_a)
    bx, by = _center(box_b)
    return bx - ax, by - ay


def _predict_box(box: BBox, velocity: tuple[float, float]) -> BBox:
    vx, vy = velocity
    return [box[0] + vx, box[1] + vy, box[2] + vx, box[3] + vy]


def _greedy_iou_matches(
    track_boxes: list[BBox],
    det_boxes: list[BBox],
    threshold: float,
) -> tuple[list[tuple[int, int]], list[int], list[int]]:
    if not track_boxes or not det_boxes:
        return [], list(range(len(track_boxes))), list(range(len(det_boxes)))

    pairs: list[tuple[float, int, int]] = []
    for ti, tbox in enumerate(track_boxes):
        for di, dbox in enumerate(det_boxes):
            score = bbox_iou(tbox, dbox)
            if score >= threshold:
                pairs.append((score, ti, di))
    pairs.sort(key=lambda x: x[0], reverse=True)

    used_t: set[int] = set()
    used_d: set[int] = set()
    matches: list[tuple[int, int]] = []
    for _, ti, di in pairs:
        if ti in used_t or di in used_d:
            continue
        used_t.add(ti)
        used_d.add(di)
        matches.append((ti, di))

    return (
        matches,
        [i for i in range(len(track_boxes)) if i not in used_t],
        [i for i in range(len(det_boxes)) if i not in used_d],
    )


@dataclass
class _Track:
    track_id: int
    bbox: BBox
    previous_bbox: BBox | None = None
    velocity: tuple[float, float] = (0.0, 0.0)
    time_since_update: int = 0
    hits: int = 1
    confidence: float = 0.0

    def predict(self) -> BBox:
        return _predict_box(self.bbox, self.velocity)

    def update(self, bbox: BBox, confidence: float) -> None:
        self.previous_bbox = self.bbox
        self.velocity = _velocity(self.bbox, bbox)
        self.bbox = list(bbox)
        self.confidence = confidence
        self.time_since_update = 0
        self.hits += 1


@dataclass
class _CameraState:
    next_id: int = 1
    tracks: list[_Track] = field(default_factory=list)

    def new_id(self) -> int:
        value = self.next_id
        self.next_id += 1
        return value


class PerCameraTracker:
    """ByteTrack-style local tracker with independent state per camera.

    Parameters
    ----------
    high_threshold:
        Confidence threshold for the first ByteTrack association stage.
    low_threshold:
        Minimum confidence accepted into the second association stage.
    match_threshold:
        IoU threshold for association against motion-predicted boxes.
    max_age:
        Number of consecutive unmatched frames before a track is removed.
    """

    def __init__(
        self,
        high_threshold: float = 0.5,
        low_threshold: float = 0.1,
        match_threshold: float = 0.3,
        max_age: int = 5,
    ) -> None:
        if not 0 <= low_threshold <= high_threshold <= 1:
            raise ValueError("require 0 <= low_threshold <= high_threshold <= 1")
        if not 0 <= match_threshold <= 1:
            raise ValueError("match_threshold must be between 0 and 1")
        if max_age < 0:
            raise ValueError("max_age must be >= 0")

        self.high_threshold = high_threshold
        self.low_threshold = low_threshold
        self.match_threshold = match_threshold
        self.max_age = max_age
        self._cameras: dict[str, _CameraState] = {}

    def _state_for(self, camera_id: str) -> _CameraState:
        return self._cameras.setdefault(camera_id, _CameraState())

    def _age_and_prune(self, state: _CameraState, unmatched: list[int]) -> None:
        for idx in unmatched:
            if 0 <= idx < len(state.tracks):
                state.tracks[idx].time_since_update += 1
        state.tracks = [
            t for t in state.tracks if t.time_since_update <= self.max_age
        ]

    @staticmethod
    def _confidence(det: dict[str, Any]) -> float:
        value = det.get("vehicle_confidence", det.get("confidence", 0.0))
        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.0

    def update(self, frame_result: Any) -> dict[str, Any]:
        """Track one frame while preserving all Member 1 detection fields."""
        if not isinstance(frame_result, dict):
            return {
                "camera_id": None,
                "timestamp": None,
                "source": None,
                "detections": [],
                "error": "invalid_frame_result",
            }

        camera_id = frame_result.get("camera_id")
        result = {
            "camera_id": camera_id,
            "timestamp": frame_result.get("timestamp"),
            "source": frame_result.get("source"),
            "detections": [],
        }
        if "error" in frame_result:
            result["error"] = frame_result["error"]

        detections = frame_result.get("detections")
        camera_key = str(camera_id) if camera_id is not None else "_unknown"
        state = self._state_for(camera_key)

        if detections is None:
            self._age_and_prune(state, list(range(len(state.tracks))))
            result["error"] = result.get("error", "missing_detections")
            return result

        if not isinstance(detections, list):
            result["error"] = "detections_not_a_list"
            return result

        output = [dict(det) if isinstance(det, dict) else {} for det in detections]
        valid: list[tuple[int, BBox, float]] = []
        for i, det in enumerate(detections):
            if not isinstance(det, dict):
                continue
            box = det.get("vehicle_bbox")
            if not is_valid_bbox(box):
                continue
            valid.append((i, [float(v) for v in box], self._confidence(det)))

        # Predict all active tracks one frame forward.
        predicted = [track.predict() for track in state.tracks]

        high = [(i, box, conf) for i, box, conf in valid if conf >= self.high_threshold]
        low = [(i, box, conf) for i, box, conf in valid
               if self.low_threshold <= conf < self.high_threshold]

        # Stage 1: high-confidence detections.
        high_boxes = [x[1] for x in high]
        matches1, unmatched_tracks, unmatched_high = _greedy_iou_matches(
            predicted, high_boxes, self.match_threshold
        )

        assigned: dict[int, int] = {}
        for track_idx, high_idx in matches1:
            det_idx, box, conf = high[high_idx]
            state.tracks[track_idx].update(box, conf)
            assigned[det_idx] = state.tracks[track_idx].track_id

        # Stage 2: remaining tracks vs low-confidence detections.
        remaining_track_indices = unmatched_tracks
        low_boxes = [x[1] for x in low]
        rem_predicted = [predicted[i] for i in remaining_track_indices]
        matches2, _, _ = _greedy_iou_matches(
            rem_predicted, low_boxes, self.match_threshold
        )

        matched_low_dets: set[int] = set()
        for local_track_idx, low_idx in matches2:
            track_idx = remaining_track_indices[local_track_idx]
            det_idx, box, conf = low[low_idx]
            state.tracks[track_idx].update(box, conf)
            assigned[det_idx] = state.tracks[track_idx].track_id
            matched_low_dets.add(det_idx)

        matched_track_indices = {t for t, _ in matches1}
        matched_track_indices.update(
            remaining_track_indices[t] for t, _ in matches2
        )

        # Tracks unmatched after both association stages are aged.
        for idx, track in enumerate(state.tracks):
            if idx not in matched_track_indices:
                track.time_since_update += 1

        # ByteTrack creates new tracks from unmatched HIGH-confidence detections.
        for high_idx in unmatched_high:
            det_idx, box, conf = high[high_idx]
            track_id = state.new_id()
            state.tracks.append(
                _Track(track_id=track_id, bbox=list(box), confidence=conf)
            )
            assigned[det_idx] = track_id

        # Low-confidence unmatched detections intentionally do not create IDs.
        state.tracks = [
            t for t in state.tracks if t.time_since_update <= self.max_age
        ]

        for i, det in enumerate(detections):
            if not isinstance(det, dict):
                output[i] = {"local_track_id": None}
                continue
            out = dict(det)
            out["local_track_id"] = assigned.get(i)
            output[i] = out

        result["detections"] = output
        return result


def track_sequence(
    frames: list[dict[str, Any]],
    **tracker_kwargs: Any,
) -> list[dict[str, Any]]:
    """Track a list of frames in order."""
    tracker = PerCameraTracker(**tracker_kwargs)
    return [tracker.update(frame) for frame in frames]
