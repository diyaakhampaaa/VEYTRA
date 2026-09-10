"""
Member 1 - Detection module for VEYTRA.

Wraps VehicleNet-Y26x (vehicle detection) and a fine-tuned YOLO model
(plate detection) behind a single detect() function.
"""

import base64
import logging
import os
import time

import cv2
import numpy as np
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

VEHICLE_WEIGHTS_PATH = os.environ.get(
    "VEHICLE_WEIGHTS_PATH",
    "ai/detection/weights/vehiclenet_y26x.pt",
)

PLATE_WEIGHTS_PATH = os.environ.get(
    "PLATE_WEIGHTS_PATH",
    "ai/detection/weights/plate_yolo.pt",
)

_vehicle_model = None
_plate_model = None


def _load_vehicle_model():
    """Loads VehicleNet-Y26x."""
    global _vehicle_model

    if _vehicle_model is None:
        if os.path.exists(VEHICLE_WEIGHTS_PATH):
            from ultralytics import YOLO

            _vehicle_model = YOLO(VEHICLE_WEIGHTS_PATH)

            logger.info(
                "Loaded VehicleNet-Y26x from %s",
                VEHICLE_WEIGHTS_PATH,
            )
        else:
            logger.warning(
                "VehicleNet-Y26x weights not found at %s — "
                "using stub vehicle detector.",
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

            logger.info(
                "Loaded plate detector from %s",
                PLATE_WEIGHTS_PATH,
            )
        else:
            logger.warning(
                "Plate YOLO weights not found at %s — "
                "using stub plate detector.",
                PLATE_WEIGHTS_PATH,
            )

            _plate_model = "STUB_PLATE_MODEL"

    return _plate_model


def _run_vehicle_detection(frame: np.ndarray) -> list[dict]:
    """
    Runs VehicleNet-Y26x on a frame.

    Falls back to a deterministic dummy detection if real weights
    aren't available.
    """
    model = _load_vehicle_model()

    if model == "STUB_VEHICLE_MODEL":
        h, w = frame.shape[:2]

        return [
            {
                "vehicle_bbox": [
                    int(w * 0.2),
                    int(h * 0.2),
                    int(w * 0.6),
                    int(h * 0.6),
                ],
                "vehicle_type": "car",
                "vehicle_confidence": 0.90,
                "vehicle_detector": "VehicleNet-Y26x",
            }
        ]

    results = model.predict(
        frame,
        conf=0.4,
        verbose=False,
    )

    result = results[0]

    detections = []

    for box in result.boxes:
        cls_id = int(box.cls[0])
        cls_name = model.names[cls_id]
        conf = float(box.conf[0])

        x1, y1, x2, y2 = [
            int(v) for v in box.xyxy[0].tolist()
        ]

        detections.append(
            {
                "vehicle_bbox": [x1, y1, x2, y2],
                "vehicle_type": cls_name,
                "vehicle_confidence": conf,
                "vehicle_detector": "VehicleNet-Y26x",
            }
        )

    return detections


def _encode_plate_crop(
    frame: np.ndarray,
    plate_bbox: list[int] | None,
) -> str | None:
    """
    Crop a detected plate from the full frame and encode it
    as a base64 JPEG string.

    The base64 string can safely be returned through the JSON API
    and decoded by Member 2 before OCR.
    """
    if plate_bbox is None:
        return None

    h, w = frame.shape[:2]

    x1, y1, x2, y2 = [
        int(v) for v in plate_bbox
    ]

    # Clamp coordinates to frame boundaries.
    x1 = max(0, min(x1, w))
    x2 = max(0, min(x2, w))
    y1 = max(0, min(y1, h))
    y2 = max(0, min(y2, h))

    # Invalid bounding box.
    if x2 <= x1 or y2 <= y1:
        return None

    crop = frame[y1:y2, x1:x2]

    if crop.size == 0:
        return None

    success, encoded = cv2.imencode(".jpg", crop)

    if not success:
        return None

    return base64.b64encode(
        encoded.tobytes()
    ).decode("utf-8")


def _run_plate_detection(
    frame: np.ndarray,
    vehicle_bbox: list[int],
) -> dict:
    """
    Crops the frame to the vehicle bounding box and runs the
    fine-tuned YOLO plate detector.

    Returns:
        plate_bbox
        plate_confidence
        plate_crop

    plate_crop is a base64-encoded JPEG string for OCR handoff.
    """
    model = _load_plate_model()

    x1, y1, x2, y2 = vehicle_bbox

    h, w = frame.shape[:2]

    # Clamp vehicle coordinates to frame boundaries.
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(w, x2)
    y2 = min(h, y2)

    # Invalid vehicle bounding box.
    if x2 <= x1 or y2 <= y1:
        return {
            "plate_bbox": None,
            "plate_confidence": 0.0,
            "plate_crop": None,
        }

    # ---------------------------------------------------------
    # STUB PLATE DETECTOR
    # ---------------------------------------------------------
    if model == "STUB_PLATE_MODEL":
        vehicle_w = x2 - x1
        vehicle_h = y2 - y1

        plate_w = int(vehicle_w * 0.3)
        plate_h = int(vehicle_h * 0.15)

        plate_x1 = x1 + int(vehicle_w * 0.35)
        plate_y1 = y2 - plate_h - 5

        plate_bbox = [
            plate_x1,
            plate_y1,
            plate_x1 + plate_w,
            plate_y1 + plate_h,
        ]

        plate_crop = _encode_plate_crop(
            frame,
            plate_bbox,
        )

        return {
            "plate_bbox": plate_bbox,
            "plate_confidence": 0.85,
            "plate_crop": plate_crop,
        }

    # ---------------------------------------------------------
    # REAL PLATE DETECTOR
    # ---------------------------------------------------------

    crop = frame[y1:y2, x1:x2]

    if crop.size == 0:
        return {
            "plate_bbox": None,
            "plate_confidence": 0.0,
            "plate_crop": None,
        }

    results = model.predict(
        crop,
        conf=0.25,
        verbose=False,
    )

    result = results[0]

    if len(result.boxes) == 0:
        return {
            "plate_bbox": None,
            "plate_confidence": 0.0,
            "plate_crop": None,
        }

    # Take the highest-confidence plate box.
    best_box = max(
        result.boxes,
        key=lambda b: float(b.conf[0]),
    )

    px1, py1, px2, py2 = [
        int(v)
        for v in best_box.xyxy[0].tolist()
    ]

    conf = float(best_box.conf[0])

    # Translate crop-local coordinates back to
    # full-frame coordinates.
    plate_bbox = [
        px1 + x1,
        py1 + y1,
        px2 + x1,
        py2 + y1,
    ]

    # Create the actual plate image crop.
    plate_crop = _encode_plate_crop(
        frame,
        plate_bbox,
    )

    return {
        "plate_bbox": plate_bbox,
        "plate_confidence": conf,
        "plate_crop": plate_crop,
    }


def detect(
    frame: np.ndarray,
    camera_id: str,
    timestamp: str,
    source: str,
) -> dict:
    """
    Runs vehicle + plate detection on a single frame.

    Returns:
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
                    "plate_crop": str | None
                }
            ]
        }

    plate_crop is a base64-encoded JPEG image that can be decoded
    by Member 2 and passed to the OCR module.

    Never raises — returns an error dict on invalid input instead.
    """
    start_time = time.time()

    # ---------------------------------------------------------
    # INPUT VALIDATION
    # ---------------------------------------------------------

    if (
        frame is None
        or not isinstance(frame, np.ndarray)
        or frame.size == 0
    ):
        logger.error(
            "detect() received invalid/empty frame for camera_id=%s",
            camera_id,
        )

        return {
            "camera_id": camera_id,
            "timestamp": timestamp,
            "source": source,
            "detections": [],
            "error": "invalid_or_empty_frame",
        }

    # ---------------------------------------------------------
    # VEHICLE DETECTION
    # ---------------------------------------------------------

    try:
        vehicle_detections = _run_vehicle_detection(frame)

    except Exception:
        logger.exception(
            "Vehicle detection failed for camera_id=%s",
            camera_id,
        )

        vehicle_detections = []

    # ---------------------------------------------------------
    # PLATE DETECTION + OCR HANDOFF
    # ---------------------------------------------------------

    detections = []

    for veh in vehicle_detections:
        try:
            plate_result = _run_plate_detection(
                frame,
                veh["vehicle_bbox"],
            )

            plate_bbox = plate_result["plate_bbox"]

            plate_confidence = float(
                plate_result["plate_confidence"]
            )

            plate_crop = plate_result["plate_crop"]

        except Exception:
            logger.exception(
                "Plate detection failed for a vehicle "
                "in camera_id=%s",
                camera_id,
            )

            plate_bbox = None
            plate_confidence = 0.0
            plate_crop = None

        detections.append(
            {
                "vehicle_bbox": veh["vehicle_bbox"],
                "vehicle_type": veh["vehicle_type"],
                "vehicle_confidence": float(
                    veh["vehicle_confidence"]
                ),
                "vehicle_detector": veh["vehicle_detector"],
                "plate_bbox": plate_bbox,
                "plate_confidence": plate_confidence,
                "plate_crop": plate_crop,
            }
        )

    # ---------------------------------------------------------
    # RETURN RESULT
    # ---------------------------------------------------------

    elapsed = time.time() - start_time

    logger.debug(
        "detect() for camera_id=%s took %.4f seconds",
        camera_id,
        elapsed,
    )

    return {
        "camera_id": camera_id,
        "timestamp": timestamp,
        "source": source,
        "detections": detections,
    }