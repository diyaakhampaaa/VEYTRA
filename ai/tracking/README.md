# Member 3 — Per-camera tracking (scaffold)

Tracking module for VEYTRA. This is the **TRACK** stage:

DETECT -> READ -> **TRACK** -> MATCH (Re-ID) -> VERIFY -> CORRECT -> RECONSTRUCT -> ANALYZE -> VISUALIZE -> ALERT

This package currently does per-camera identity (IoU `local_track_id`) and a
**baseline appearance embedding** (normalized RGB histogram). The original
image is never stored in tracking JSON; the caller must pass the same frame
that was sent to Member 1 `detect()`.

Not in this package yet: neural Re-ID, cross-camera matching, SUMO,
trajectory reconstruction, or evaluation.

## Input (Member 1 detection JSON)

```json
{
  "camera_id": "C01",
  "timestamp": "2026-09-06T15:30:00",
  "source": "real",
  "detections": [
    {
      "vehicle_bbox": [167, 519, 343, 727],
      "vehicle_type": "Two-wheeler",
      "vehicle_confidence": 0.95,
      "vehicle_detector": "VehicleNet-Y26x",
      "plate_bbox": [222, 590, 273, 616],
      "plate_confidence": 0.38
    }
  ]
}
```

## Output

Same payload, with `local_track_id` on each detection. Track IDs are **local
to a camera** — camera `C01` and `C02` may both use id `1`. Invalid or empty
input returns `detections: []` and never raises.

## Usage

```python
from ai.tracking import PerCameraTracker

tracker = PerCameraTracker()
tracked = tracker.update(detection_json)
```

Or over a sequence:

```python
from ai.tracking import track_sequence

tracked_frames = track_sequence([frame1, frame2, frame3])
```

## Re-ID baseline

```python
from ai.tracking import ReIDEmbedder, embed_tracked_frame

vector = ReIDEmbedder().embed(frame, [x1, y1, x2, y2])  # list[float] | None
with_embeddings = embed_tracked_frame(frame, tracked)
```

`embed_tracked_frame` copies tracker fields and adds `embedding` only on
detections that already have a non-null `local_track_id`. Swap the histogram
later by replacing `ReIDEmbedder.embed` (no torch / no weights in this baseline).

## Tests

From the repository root:

```bash
python -m pytest ai/tracking/tests -v
```

## Swapping the associator later

`PerCameraTracker` depends on an associator with `associate(track_bboxes, detection_bboxes)`.
`IoUAssociator` is the default. A ByteTrack/Kalman associator can be passed as
`associator=` without changing the JSON contract.
