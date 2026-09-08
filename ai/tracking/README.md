# Member 3 — Per-camera tracking (scaffold)

Tracking module for VEYTRA. This is the **TRACK** stage:

DETECT -> READ -> **TRACK** -> MATCH (Re-ID) -> VERIFY -> CORRECT -> RECONSTRUCT -> ANALYZE -> VISUALIZE -> ALERT

This package currently does per-camera identity (IoU `local_track_id`) and a
**baseline appearance embedding** (normalized RGB histogram). The original
image is never stored in tracking JSON; the caller must pass the same frame
that was sent to Member 1 `detect()`.

Cross-camera matching is included as a deterministic baseline. Trajectory
reconstruction is also included. The integration adapter consumes Member 1's
detection JSON after tracking/Re-ID and accepts Member 2's exact OCR fields
(`plate`, `confidence`, `alternatives`).

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


## Member 1 + Member 2 integration

Member 3 does not replace upstream modules. It consumes their contracts.

```python
from ai.tracking import (
    PerCameraTracker,
    ReIDEmbedder,
    track_and_enrich_frame,
    match_tracked_frames,
    verification_payloads,
)

tracker = PerCameraTracker()
embedder = ReIDEmbedder()

# detection_result is the JSON returned by Member 1 `ai.detection.detect()`.
tracked = track_and_enrich_frame(detection_result, frame, tracker, embedder)

# Repeat for frames from all cameras, then:
match_result = match_tracked_frames(all_tracked_frames)
```

Each detection may carry Member 2's exact OCR output:

```json
{
  "plate": "DL01AB1234",
  "confidence": 0.94,
  "alternatives": ["DL01AB1284"]
}
```

`prepare_track_records()` converts those per-frame records into camera-local
completed tracks for the matcher. The selected `plate_text` is the
highest-confidence OCR read and `plate_history` retains all reads; Member 3
does not silently overwrite OCR history.

## Plate mismatch -> VERIFY integration

A different plate at two cameras is no longer discarded before verification.
If time, spatial feasibility, and appearance make the pair plausible,
`matcher.match()` keeps it out of the identity `matches` list **but** exposes
it in `verification_candidates`.

```python
payloads = verification_payloads(match_result)
```

Each payload contains a Member 4-compatible suspicious event plus a
`nearby_events` supporting read. The lower-confidence OCR observation is
selected as the suspicious event, while both original plate readings are
preserved.

This deliberately separates responsibilities:

`MATCH` = "these observations are plausibly the same vehicle"

`VERIFY/CORRECT` = "the plate disagreement is real OCR error and should be
corrected"

A plate mismatch is therefore **not** treated as proof of identity, and
ground truth is never used by Member 3.
