markdown
# Member 1 — Vehicle + Plate Detection

Detection module for VEYTRA (SIH 2026, PS 26127). This is the **DETECT** stage:

DETECT -> READ -> TRACK -> MATCH (Re-ID) -> VERIFY -> CORRECT -> RECONSTRUCT -> ANALYZE -> VISUALIZE -> ALERT


Turns a camera frame (real UVH-26 footage or a SUMO-simulated frame) into vehicle
and license-plate bounding boxes, consumed downstream by Member 2 (OCR) and
Member 3 (tracking).

## Current status

| Component | Status |
|---|---|
| Module structure, contract, API, CLI, tests | Complete |
| Vehicle detection — VehicleNet-Y26x | **Real, integrated** (`ai/detection/weights/vehiclenet_y26x.pt`) |
| Plate detection — fine-tuned YOLOv8n | **Real, integrated** (`ai/detection/weights/plate_yolo.pt`, mAP50=0.457) |

Both models are live. `detector.py` still contains a stub fallback path for
each (`STUB_VEHICLE_MODEL` / `STUB_PLATE_MODEL`) that activates automatically
if the weight files are missing — this keeps tests/CI functional without the
large binary weight files present, since those are gitignored and not
committed.

## Install

```bash
cd ai/detection
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

## Weights

Place model weight files here (gitignored, never committed):

ai/detection/weights/vehiclenet_y26x.pt
ai/detection/weights/plate_yolo.pt


Paths are configured via a `.env` file (gitignored, auto-loaded via
`python-dotenv`):

VEHICLE_WEIGHTS_PATH=weights/vehiclenet_y26x.pt
PLATE_WEIGHTS_PATH=weights/plate_yolo.pt


No manual export needed — `detector.py` calls `load_dotenv()` on import.

## Usage

### As a Python function
```python
from detector import detect
import cv2

frame = cv2.imread("path/to/frame.jpg")
result = detect(frame, camera_id="C01", timestamp="2026-09-06T15:30:00", source="real")
```

### CLI
```bash
python run_detection.py --image tests/sample_frames/real_sample1.png --camera-id C01 --source real
```

### HTTP API
```bash
uvicorn api:app --reload
```
```bash
curl -X POST "http://127.0.0.1:8000/detect" \
  -F "image=@tests/sample_frames/real_sample1.png" \
  -F "camera_id=C01" \
  -F "timestamp=2026-09-06T15:30:00" \
  -F "source=real"
```
Or use the interactive docs at http://127.0.0.1:8000/docs

## Data contract

Input: image frame + camera_id (string), timestamp (ISO 8601 string),
source ("real" or "simulated").

Output:
```json
{
  "camera_id": "C01",
  "timestamp": "2026-09-06T15:30:00",
  "source": "real",
  "detections": [
    {
      "vehicle_bbox": [167, 519, 343, 727],
      "vehicle_type": "Two-wheeler",
      "vehicle_confidence": 0.9507519602775574,
      "vehicle_detector": "VehicleNet-Y26x",
      "plate_bbox": [222, 590, 273, 616],
      "plate_confidence": 0.3819118142127991
    }
  ]
}
```
If no plate is detected, plate_bbox is null and plate_confidence is 0.0 —
keys always present, never omitted. vehicle_type is one of VehicleNet-Y26x's
14 real classes (Hatchback, Sedan, SUV, MUV, Two-wheeler, Three-wheeler,
Bus, Truck, LCV, Van, Bicycle, Tempo-traveller, and others), not a placeholder.

## Model details

**VehicleNet-Y26x** — YOLO26x fine-tuned on UVH-26-MV (IISc Bangalore,
Indian traffic), 14 vehicle classes, mAP@50:95=0.666. Gated on Hugging Face
(Perception365/VehicleNet-Y26x) — access was requested and approved during
this project.

**Plate detector** — Ultralytics YOLOv8n fine-tuned from scratch on ~45
manually + auto-annotated plate crops, cropped from UVH-26 vehicle
detections. Training: 50 epochs configured, stopped early via patience=15,
best result at epoch 21, mAP50=0.457, mAP50-95=0.285. Known limitation:
small training set (~45 labeled plates) — accuracy can likely be improved by
annotating more UVH-26 image folders and retraining.

## Testing

```bash
pytest tests/ -v
```
10/10 passing. Covers contract shape, all-black frame, low-light frame,
blurry frame, partial-visibility/small frame, None input, zero-size array
input, and a no-crash sweep across frame sizes. Tests pass identically
whether real weights are present or the module is running on stub fallback.

## Known operational gotchas

- Colab sessions reset frequently, wiping all in-memory variables and
  downloaded files. Rebuild via the reference pipeline rather than
  assuming prior state persists.
- Environment variables set via `export` only apply to the terminal tab
  they were run in, and only to processes started afterward — a
  long-running `uvicorn` process locks in whatever env state existed at
  launch. This is why the module uses a `.env` file + python-dotenv
  instead of relying on manual exports.
- Always confirm which git branch and working directory a terminal tab is
  in before running commands.