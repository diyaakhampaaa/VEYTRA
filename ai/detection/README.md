Member 1 — Vehicle + Plate Detection

Detection module for VEYTRA (SIH 2026, PS 26127). This is the DETECT stage
of the pipeline:

DETECT -> READ -> TRACK -> MATCH (Re-ID) -> VERIFY -> CORRECT -> RECONSTRUCT -> ANALYZE -> VISUALIZE -> ALERT

Turns a camera frame (real UVH-26 footage or a SUMO-simulated frame) into vehicle
and license-plate bounding boxes, consumed downstream by Member 2 (OCR) and
Member 3 (tracking).

Current status
Component	Status
Module structure, contract, API, CLI, tests	Complete
Vehicle detection (VehicleNet-Y26x)	Stubbed — see below
Plate detection (fine-tuned YOLO)	Stubbed — see below

Why stubbed: Perception365/VehicleNet-Y26x (https://huggingface.co/Perception365/VehicleNet-Y26x)
is a gated Hugging Face model; access request is pending approval. The plate
detector requires a YOLO model fine-tuned on an annotated plate-crop dataset,
which has not been built yet. Both integration points are implemented behind
the same function signatures they'll use once real weights are available —
search detector.py for TODO(vehiclenet) and the plate-model equivalent to
find the exact swap-in points. All other behavior (JSON contract, error
handling, API, CLI, tests) is final and will not change when real models are
plugged in.

Install
bash
cd ai/detection
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
Weights

Once available, place model weight files here (both gitignored, never committed):

ai/detection/weights/vehiclenet_y26x.pt
ai/detection/weights/plate_yolo.pt

Paths are configurable via environment variables VEHICLE_WEIGHTS_PATH and
PLATE_WEIGHTS_PATH if you need to point elsewhere.

Usage
As a Python function
python
from detector import detect
import cv2

frame = cv2.imread("path/to/frame.jpg")
result = detect(frame, camera_id="C01", timestamp="2026-09-06T15:30:00", source="real")
CLI
bash
python run_detection.py --image tests/sample_frames/sample1.jpg --camera-id C01 --source real
HTTP API
bash
uvicorn api:app --reload

Then in a separate terminal:

bash
curl -X POST "http://127.0.0.1:8000/detect" \
  -F "image=@tests/sample_frames/sample1.jpg" \
  -F "camera_id=C01" \
  -F "timestamp=2026-09-06T15:30:00" \
  -F "source=simulated"

Or use the interactive docs at http://127.0.0.1:8000/docs

Data contract

Input: an image frame plus camera_id (string), timestamp (ISO 8601
string), source ("real" or "simulated").

Output:

json
{
  "camera_id": "C01",
  "timestamp": "2026-09-06T15:30:00",
  "source": "real",
  "detections": [
    {
      "vehicle_bbox": [128, 96, 384, 288],
      "vehicle_type": "car",
      "vehicle_confidence": 0.9,
      "vehicle_detector": "VehicleNet-Y26x",
      "plate_bbox": [217, 255, 293, 283],
      "plate_confidence": 0.85
    }
  ]
}

If no plate is detected for a vehicle, plate_bbox is null and
plate_confidence is 0.0 — the keys are always present, never omitted.

Sample I/O

Input: tests/sample_frames/sample1.jpg (640x480 test frame), called via CLI:

bash
python run_detection.py --image tests/sample_frames/sample1.jpg --camera-id C01 --source simulated

Output:

json
{
  "camera_id": "C01",
  "timestamp": "2026-09-06T15:41:12.345678+00:00",
  "source": "simulated",
  "detections": [
    {
      "vehicle_bbox": [128, 96, 384, 288],
      "vehicle_type": "car",
      "vehicle_confidence": 0.9,
      "vehicle_detector": "VehicleNet-Y26x",
      "plate_bbox": [217, 255, 293, 283],
      "plate_confidence": 0.85
    }
  ]
}
Testing
bash
pytest tests/ -v

Covers: contract shape validation, all-black frame, low-light frame, blurry
frame, partial-visibility/small frame, None input (corrupted image),
zero-size array input, and a broad no-crash sweep across frame sizes/content.
10/10 tests passing as of the last run.

Next steps
Get Hugging Face access approved for Perception365/VehicleNet-Y26x,
swap into detector.py at the TODO(vehiclenet) markers.
Build the plate-crop dataset from UVH-26 + simulated frames, annotate in
CVAT, fine-tune YOLO in Colab, export plate_yolo.pt into weights/.
Re-run pytest tests/ and the CLI/API smoke tests against real weights to
confirm output shape is unchanged, then update this README's Sample I/O
section with real (non-stub) output.