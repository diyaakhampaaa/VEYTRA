"""Per-camera multi-object tracker for Member 1 detection JSON.

Design
------
Member 1 emits one JSON object per camera frame. This module assigns a
``local_track_id`` to each detection by matching bounding boxes to tracks
seen on the *same camera* in previous frames.

Matching is IoU-only on purpose. Re-ID embeddings, Kalman motion models,
and ByteTrack can replace ``IoUAssociator`` later without changing the
JSON contract: any associator only needs ``associate(track_bboxes,
detection_bboxes)``.

IDs are local to a camera. The same integer may appear on two cameras;
cross-camera identity is a later stage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

BBox = list[float]


def bbox_iou(box_a: BBox, box_b: BBox) -> float:
    """Intersection-over-union of two [x1, y1, x2, y2] boxes.

    Returns 0.0 when boxes do not overlap or have non-positive area.
    """
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_w = max(0.0, inter_x2 - inter_x1)
    inter_h = max(0.0, inter_y2 - inter_y1)
    intersection = inter_w * inter_h
    if intersection <= 0.0:
        return 0.0

    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - intersection
    if union <= 0.0:
        return 0.0
    return intersection / union


def is_valid_bbox(value: Any) -> bool:
    """True when value is a 4-number box with positive width and height."""
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        return False
    try:
        x1, y1, x2, y2 = (float(v) for v in value)
    except (TypeError, ValueError):
        return False
    return x2 > x1 and y2 > y1


class Associator(Protocol):
    """Strategy for pairing existing tracks with new detections.

    Return value:
        matches: (track_index, detection_index) pairs
        unmatched_tracks: track indices with no partner
        unmatched_detections: detection indices with no partner
    """

    def associate(
        self,
        track_bboxes: list[BBox],
        detection_bboxes: list[BBox],
    ) -> tuple[list[tuple[int, int]], list[int], list[int]]:
        ...


class IoUAssociator:
    """Greedy highest-IoU matching with a minimum overlap threshold.

    Each track and each detection is used at most once. This is enough for
    a first tracker and has no third-party dependencies. A later Kalman or
    ByteTrack associator can implement the same ``associate`` method.
    """

    def __init__(self, iou_threshold: float = 0.3) -> None:
        if not 0.0 <= iou_threshold <= 1.0:
            raise ValueError("iou_threshold must be between 0 and 1 inclusive")
        self.iou_threshold = iou_threshold

    def associate(
        self,
        track_bboxes: list[BBox],
        detection_bboxes: list[BBox],
    ) -> tuple[list[tuple[int, int]], list[int], list[int]]:
        if not track_bboxes or not detection_bboxes:
            return (
                [],
                list(range(len(track_bboxes))),
                list(range(len(detection_bboxes))),
            )

        # All candidate pairs above threshold, highest IoU first.
        pairs: list[tuple[float, int, int]] = []
        for t_idx, t_box in enumerate(track_bboxes):
            for d_idx, d_box in enumerate(detection_bboxes):
                iou = bbox_iou(t_box, d_box)
                if iou >= self.iou_threshold:
                    pairs.append((iou, t_idx, d_idx))
        pairs.sort(key=lambda item: item[0], reverse=True)

        used_tracks: set[int] = set()
        used_dets: set[int] = set()
        matches: list[tuple[int, int]] = []
        for _, t_idx, d_idx in pairs:
            if t_idx in used_tracks or d_idx in used_dets:
                continue
            used_tracks.add(t_idx)
            used_dets.add(d_idx)
            matches.append((t_idx, d_idx))

        unmatched_tracks = [i for i in range(len(track_bboxes)) if i not in used_tracks]
        unmatched_dets = [i for i in range(len(detection_bboxes)) if i not in used_dets]
        return matches, unmatched_tracks, unmatched_dets


@dataclass
class _Track:
    """Internal active track for one camera."""

    track_id: int
    bbox: BBox
    time_since_update: int = 0
    hits: int = 1


@dataclass
class _CameraState:
    """Track list and ID counter for a single camera_id."""

    next_id: int = 1
    tracks: list[_Track] = field(default_factory=list)

    def new_id(self) -> int:
        track_id = self.next_id
        self.next_id += 1
        return track_id


def _empty_result(
    camera_id: Any = None,
    timestamp: Any = None,
    source: Any = None,
    error: str = "invalid_frame_result",
) -> dict[str, Any]:
    return {
        "camera_id": camera_id,
        "timestamp": timestamp,
        "source": source,
        "detections": [],
        "error": error,
    }


def _copy_passthrough_fields(frame_result: dict[str, Any]) -> dict[str, Any]:
    """Keep Member 1 metadata; do not invent fields they did not send."""
    out: dict[str, Any] = {
        "camera_id": frame_result.get("camera_id"),
        "timestamp": frame_result.get("timestamp"),
        "source": frame_result.get("source"),
        "detections": [],
    }
    if "error" in frame_result:
        out["error"] = frame_result["error"]
    return out


class PerCameraTracker:
    """Assign ``local_track_id`` independently for each ``camera_id``.

    Call ``update`` once per frame, in time order, with Member 1's detection
    dict. Frames from different cameras may be interleaved; state is keyed
    by ``camera_id``.

    Parameters
    ----------
    associator:
        Matching strategy. Defaults to greedy IoU. Pass a Kalman/ByteTrack
        associator later without changing callers.
    max_age:
        How many consecutive frames a track may go unmatched before it is
        dropped. A vehicle that reappears after that gets a new id (Re-ID
        will later recover that case).
    """

    def __init__(
        self,
        associator: Associator | None = None,
        max_age: int = 5,
    ) -> None:
        if max_age < 0:
            raise ValueError("max_age must be >= 0")
        self.associator: Associator = associator if associator is not None else IoUAssociator()
        self.max_age = max_age
        self._cameras: dict[str, _CameraState] = {}

    def update(self, frame_result: Any) -> dict[str, Any]:
        """Process one Member 1 frame payload and return tracked detections.

        Never raises on bad input. Invalid payloads yield an empty
        ``detections`` list plus an ``error`` key.
        """
        if not isinstance(frame_result, dict):
            return _empty_result()

        camera_id = frame_result.get("camera_id")
        detections = frame_result.get("detections")

        if detections is None:
            result = _copy_passthrough_fields(frame_result)
            # A missing list is a gap: age this camera's tracks, then return.
            if camera_id is not None:
                state = self._state_for(str(camera_id))
                self._age_unmatched(state, list(range(len(state.tracks))))
            result["detections"] = []
            if "error" not in result:
                result["error"] = "missing_detections"
            return result

        if not isinstance(detections, list):
            result = _copy_passthrough_fields(frame_result)
            result["detections"] = []
            result["error"] = "detections_not_a_list"
            return result

        camera_key = str(camera_id) if camera_id is not None else "_unknown"
        state = self._state_for(camera_key)

        indexed: list[tuple[int, BBox]] = []
        for i, det in enumerate(detections):
            if not isinstance(det, dict):
                continue
            bbox = det.get("vehicle_bbox")
            if is_valid_bbox(bbox):
                indexed.append((i, [float(v) for v in bbox]))

        track_bboxes = [t.bbox for t in state.tracks]
        det_bboxes = [box for _, box in indexed]
        matches, unmatched_tracks, unmatched_dets = self.associator.associate(
            track_bboxes, det_bboxes
        )

        assigned: dict[int, int] = {}

        for track_idx, det_idx in matches:
            track = state.tracks[track_idx]
            orig_i, box = indexed[det_idx]
            track.bbox = box
            track.time_since_update = 0
            track.hits += 1
            assigned[orig_i] = track.track_id

        for det_idx in unmatched_dets:
            orig_i, box = indexed[det_idx]
            new_id = state.new_id()
            state.tracks.append(_Track(track_id=new_id, bbox=box))
            assigned[orig_i] = new_id

        self._age_unmatched(state, unmatched_tracks)

        result = _copy_passthrough_fields(frame_result)
        tracked: list[dict[str, Any]] = []
        for i, det in enumerate(detections):
            if isinstance(det, dict):
                out_det = dict(det)
            else:
                out_det = {"invalid_detection": det}
            out_det["local_track_id"] = assigned.get(i)
            tracked.append(out_det)
        result["detections"] = tracked
        return result

    def _state_for(self, camera_key: str) -> _CameraState:
        if camera_key not in self._cameras:
            self._cameras[camera_key] = _CameraState()
        return self._cameras[camera_key]

    def _age_unmatched(self, state: _CameraState, unmatched_tracks: list[int]) -> None:
        """Increment miss count on unmatched tracks and drop stale ones."""
        unmatched = set(unmatched_tracks)
        surviving: list[_Track] = []
        for idx, track in enumerate(state.tracks):
            if idx in unmatched:
                track.time_since_update += 1
            if track.time_since_update <= self.max_age:
                surviving.append(track)
        state.tracks = surviving


def track_sequence(
    frames: list[Any],
    associator: Associator | None = None,
    max_age: int = 5,
) -> list[dict[str, Any]]:
    """Run ``PerCameraTracker.update`` over an ordered list of frames."""
    tracker = PerCameraTracker(associator=associator, max_age=max_age)
    return [tracker.update(frame) for frame in frames]
