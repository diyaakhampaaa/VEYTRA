"""
Member 1 - Detection module for VEYTRA.
Wraps VehicleNet-Y26x (vehicle detection) and a fine-tuned YOLO model
(plate detection) behind a single detect() function.

NOTE: VehicleNet-Y26x access is currently pending approval on Hugging Face
(gated repo: Perception365/VehicleNet-Y26x). Until weights are available,
vehicle detection is stubbed with deterministic dummy output so the rest
of the pipeline (JSON contract, API, tests) can be built and tested now.
Search for "TODO(vehiclenet)" to find the swap-in point.
"""

import logging
import os
import time
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# Config: weight paths, overridable via environment variables
VEHICLE_WEIGHTS_PATH = os.environ.get(
    "VEHICLE_WEIGHTS_PATH", "ai/detection/weights/vehiclenet_y26x.pt"
)
PLATE_WEIGHTS_PATH = os.environ.get(
    "PLATE_WEIGHTS_PATH", "ai/detection/weights/plate_yolo.pt"
)

_vehicle_model = None
_plate_model = None


def _load_vehicle_model():
    """
    Loads VehicleNet-Y26x (Ultralytics YOLO26x fine-tuned on UVH-26-MV, 14 vehicle classes).

    TODO(vehiclenet): Replace this stub once Hugging Face access to
    Perception365/VehicleNet-Y26x is approved. Real implementation:

        from ultralytics import YOLO
        return YOLO(VEHICLE_WEIGHTS_PATH)
    """
    global _vehicle_model
    if _vehicle_model is None:
        logger.warning(
            "VehicleNet-Y26x weights not yet available — using stub vehicle detector."
        )
        _vehicle_model = "STUB_VEHICLE_MODEL"
    return _vehicle_model


def _load_plate_model():
    """
    Loads the fine-tuned YOLO plate detector.
    Will be trained in Colab in a later step; stubbed until weights exist.
    """
    global _plate_model
    if _plate_model is None:
        if os.path.exists(PLATE_WEIGHTS_PATH):
            from ultralytics import YOLO
            _plate_model = YOLO(PLATE_WEIGHTS_PATH)
        else:
            logger.warning(
                "Plate YOLO weights not found at %s — using stub plate detector.",
                PLATE_WEIGHTS_PATH,
            )
            _plate_model = "STUB_PLATE_MODEL"
    return _plate_model


def _run_vehicle_detection_stub(frame: np.ndarray) -> list[dict]:
    """
    Deterministic stub standing in for VehicleNet-Y26x inference.
    Returns one fixed dummy vehicle detection so downstream code
    (JSON contract, API, tests) can be built and verified now.
    """
    h, w = frame.shape[0], frame.shape[1]
    return [
        {
            "vehicle_bbox": [
                int(w * 0.2), int(h * 0.2), int(w * 0.6), int(h * 0.6)
            ],
            "vehicle_type": "car",
            "vehicle_confidence": 0.90,
            "vehicle_detector": "VehicleNet-Y26x",
        }
    ]


def _run_plate_detection_stub(frame: np.ndarray, vehicle_bbox: list[int]) -> dict:
    """
    Deterministic stub standing in for the fine-tuned YOLO plate detector,
    until real weights exist post fine-tuning.
    """
    x1, y1, x2, y2 = vehicle_bbox
    plate_w = int((x2 - x1) * 0.3)
    plate_h = int((y2 - y1) * 0.15)
    plate_x1 = x1 + int((x2 - x1) * 0.35)
    plate_y1 = y2 - plate_h - 5
    return {
        "plate_bbox": [plate_x1, plate_y1, plate_x1 + plate_w, plate_y1 + plate_h],
        "plate_confidence": 0.85,
    }


def detect(
    frame: np.ndarray,
    camera_id: str,
    timestamp: str,
    source: str,
) -> dict:
    """
    Runs vehicle + plate detection on a single frame and returns the
    shared JSON contract consumed by Member 3.

    Args:
        frame: image as a numpy array (H, W, 3), BGR (OpenCV convention).
        camera_id: identifier string for the source camera.
        timestamp: ISO 8601 timestamp string for this frame.
        source: "real" or "simulated".

    Returns:
        dict matching the exact contract:
        {
            "camera_id": str,
            "timestamp": str,
            "source": str,
            "detections": [
                {
                    "vehicle_bbox": [x1, y1, x2, y2],
                    "vehicle_type": str,
                    "vehicle_confidence": float,
                    "vehicle_detector": str,
                    "plate_bbox": [x1, y1, x2, y2] | None,
                    "plate_confidence": float,
                },
                ...
            ]
        }
        Never raises on empty/low-confidence/corrupted input — returns
        an empty detections list or an error dict instead.
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

    _load_vehicle_model()
    _load_plate_model()

    try:
        # TODO(vehiclenet): swap this stub call for real inference once
        # weights are available, e.g.:
        #   results = _vehicle_model.predict(frame, verbose=False)
        #   ... parse results into the same list-of-dict shape ...
        vehicle_detections = _run_vehicle_detection_stub(frame)
    except Exception:
        logger.exception("Vehicle detection failed for camera_id=%s", camera_id)
        vehicle_detections = []

    detections = []
    for veh in vehicle_detections:
        try:
            # TODO: once plate_model is a real YOLO model (post fine-tuning),
            # crop the frame to veh["vehicle_bbox"] and run real inference.
            plate_result = _run_plate_detection_stub(frame, veh["vehicle_bbox"])
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