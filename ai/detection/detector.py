"""
Member 1 - Detection module for VEYTRA.
Wraps VehicleNet-Y26x (vehicle detection) and a fine-tuned YOLO model
(plate detection) behind a single detect() function.
"""

import logging
import os
import time
from typing import Optional

import numpy as np
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

VEHICLE_WEIGHTS_PATH = os.environ.get(
    "VEHICLE_WEIGHTS_PATH", "ai/detection/weights/vehiclenet_y26x.pt"
)
PLATE_WEIGHTS_PATH = os.environ.get(
    "PLATE_WEIGHTS_PATH", "ai/detection/weights/plate_yolo.pt"
)

_vehicle_model = None
_plate_model = None


def _load_vehicle_model():
    """Loads VehicleNet-Y26x (YOLO26x fine-tuned on UVH-26-MV, 14 vehicle classes)."""
    global _vehicle_model
    if _vehicle_model is None:
        if os.path.exists(VEHICLE_WEIGHTS_PATH):
            from ultralytics import YOLO
            _vehicle_model = YOLO(VEHICLE_WEIGHTS_PATH)
            logger.info("Loaded VehicleNet-Y26x from %s", VEHICLE_WEIGHTS_PATH)
        else:
            logger.warning(
                "VehicleNet-Y26x weights not found at %s — using stub vehicle detector.",
                VEHICLE_WEIGHTS_PATH,
            )
            _vehicle_model = "STUB_VEHICLE_MODEL"
    return _vehicle_model


def _load_plate_model():
    """Loads the fine-tuned YOLO plate detector."""
    global _plate_model
    if _plate_model is None:
        if os.path.exists(PLATE_WEIGHTS_PATH):
            from ultralytics import YOLO
            _plate_model = YOLO(PLATE_WEIGHTS_PATH)
            logger.info("Loaded plate detector from %s", PLATE_WEIGHTS_PATH)
        else:
            logger.warning(
                "Plate YOLO weights not found at %s — using stub plate detector.",
                PLATE_WEIGHTS_PATH,
            )
            _plate_model = "STUB_PLATE_MODEL"
    return _plate_model


def _run_vehicle_detection(frame: np.ndarray) -> list[dict]:
    """
    Runs VehicleNet-Y26x on a frame. Falls back to a single deterministic
    dummy detection if real weights aren't available (keeps the module
    functional in environments without the weight files, e.g. CI).
    """
    model = _load_vehicle_model()

    if model == "STUB_VEHICLE_MODEL":
        h, w = frame.shape[0], frame.shape[1]
        return [
            {
                "vehicle_bbox": [int(w * 0.2), int(h * 0.2), int(w * 0.6), int(h * 0.6)],
                "vehicle_type": "car",
                "vehicle_confidence": 0.90,
                "vehicle_detector": "VehicleNet-Y26x",
            }
        ]

    results = model.predict(frame, conf=0.4, verbose=False)
    result = results[0]

    detections = []
    for box in result.boxes:
        cls_id = int(box.cls[0])
        cls_name = model.names[cls_id]
        conf = float(box.conf[0])
        x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
        detections.append(
            {
                "vehicle_bbox": [x1, y1, x2, y2],
                "vehicle_type": cls_name,
                "vehicle_confidence": conf,
                "vehicle_detector": "VehicleNet-Y26x",
            }
        )
    return detections


def _run_plate_detection(frame: np.ndarray, vehicle_bbox: list[int]) -> dict:
    """
    Crops the frame to the vehicle bounding box and runs the fine-tuned
    plate detector on that crop. Falls back to a deterministic dummy box
    if real weights aren't available.
    """
    model = _load_plate_model()

    x1, y1, x2, y2 = vehicle_bbox
    h, w = frame.shape[0], frame.shape[1]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)

    if model == "STUB_PLATE_MODEL":
        plate_w = int((x2 - x1) * 0.3)
        plate_h = int((y2 - y1) * 0.15)
        plate_x1 = x1 + int((x2 - x1) * 0.35)
        plate_y1 = y2 - plate_h - 5
        return {
            "plate_bbox": [plate_x1, plate_y1, plate_x1 + plate_w, plate_y1 + plate_h],
            "plate_confidence": 0.85,
        }

    crop = frame[y1:y2, x1:x2]
    if crop.size == 0:
        return {"plate_bbox": None, "plate_confidence": 0.0}

    results = model.predict(crop, conf=0.25, verbose=False)
    result = results[0]

    if len(result.boxes) == 0:
        return {"plate_bbox": None, "plate_confidence": 0.0}

    # Take the highest-confidence plate box found in the crop
    best_box = max(result.boxes, key=lambda b: float(b.conf[0]))
    px1, py1, px2, py2 = [int(v) for v in best_box.xyxy[0].tolist()]
    conf = float(best_box.conf[0])

    # Translate crop-local coordinates back to full-frame coordinates
    plate_bbox = [px1 + x1, py1 + y1, px2 + x1, py2 + y1]

    return {"plate_bbox": plate_bbox, "plate_confidence": conf}


def detect(
    frame: np.ndarray,
    camera_id: str,
    timestamp: str,
    source: str,
) -> dict:
    """
    Runs vehicle + plate detection on a single frame and returns the
    shared JSON contract consumed by Member 3.

    Returns dict:
        {
            "camera_id": str, "timestamp": str, "source": str,
            "detections": [
                {
                    "vehicle_bbox": [x1,y1,x2,y2], "vehicle_type": str,
                    "vehicle_confidence": float, "vehicle_detector": str,
                    "plate_bbox": [x1,y1,x2,y2] | None, "plate_confidence": float,
                }, ...
            ]
        }
    Never raises — returns an error dict on invalid input instead.
    """
    start_time = time.time()

    if frame is None or not isinstance(frame, np.ndarray) or frame.size == 0:
        logger.error("detect() received invalid/empty frame for camera_id=%s", camera_id)
        return {
            "camera_id": camera_id,
            "timestamp": timestamp,
            "source": source,
            "detections": [],
            "error": "invalid_or_empty_frame",
        }

    try:
        vehicle_detections = _run_vehicle_detection(frame)
    except Exception:
        logger.exception("Vehicle detection failed for camera_id=%s", camera_id)
        vehicle_detections = []

    detections = []
    for veh in vehicle_detections:
        try:
            plate_result = _run_plate_detection(frame, veh["vehicle_bbox"])
            plate_bbox = plate_result["plate_bbox"]
            plate_confidence = float(plate_result["plate_confidence"])
        except Exception:
            logger.exception("Plate detection failed for a vehicle in camera_id=%s", camera_id)
            plate_bbox = None
            plate_confidence = 0.0

        detections.append(
            {
                "vehicle_bbox": veh["vehicle_bbox"],
                "vehicle_type": veh["vehicle_type"],
                "vehicle_confidence": float(veh["vehicle_confidence"]),
                "vehicle_detector": veh["vehicle_detector"],
                "plate_bbox": plate_bbox,
                "plate_confidence": plate_confidence,
            }
        )

    elapsed = time.time() - start_time
    logger.debug("detect() for camera_id=%s took %.4f seconds", camera_id, elapsed)

    return {
        "camera_id": camera_id,
        "timestamp": timestamp,
        "source": source,
        "detections": detections,
    }