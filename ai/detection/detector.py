"""
Member 1 - Detection module for VEYTRA.

Runs VehicleNet-Y26x and the fine-tuned YOLO plate detector
independently on the full CCTV frame.

Architecture:

    CCTV frame
        |
        +----> VehicleNet-Y26x
        |          |
        |          +----> vehicle detections
        |
        +----> Plate YOLO
                   |
                   +----> plate detections
                              |
                              +----> optional vehicle association
                                     |
                                     +----> OCR handoff

Plate detection does NOT depend on vehicle detection.
Every detected plate is preserved even when no matching
vehicle detection exists.
"""

import base64
import logging
import os
import time
import uuid

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
    "ai/detection/weights/plate_yolo_ft.pt",
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


def _is_plausible_vehicle_box(
    bbox: list[int],
    frame_shape: tuple,
) -> bool:
    """
    Filters out degenerate vehicle detections.
    """
    x1, y1, x2, y2 = bbox

    w = x2 - x1
    h = y2 - y1

    if w < 30 or h < 30:
        return False

    aspect_ratio = w / h if h > 0 else 0

    if aspect_ratio < 0.35:
        return False

    return True


def _run_vehicle_detection(frame: np.ndarray) -> list[dict]:
    """
    Runs VehicleNet-Y26x independently on the full frame.

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
            int(v)
            for v in box.xyxy[0].tolist()
        ]

        if not _is_plausible_vehicle_box(
            [x1, y1, x2, y2],
            frame.shape,
        ):
            logger.debug(
                "Skipping degenerate/edge vehicle box: %s",
                [x1, y1, x2, y2],
            )
            continue

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
    Crops the detected plate from the original frame, upscales it for OCR,
    encodes it as a high-quality JPEG, and returns a base64 string.
    """
    if plate_bbox is None:
        return None

    h, w = frame.shape[:2]

    x1, y1, x2, y2 = [
        int(v)
        for v in plate_bbox
    ]

    # Clamp coordinates to frame boundaries.
    x1 = max(0, min(x1, w))
    x2 = max(0, min(x2, w))
    y1 = max(0, min(y1, h))
    y2 = max(0, min(y2, h))

    if x2 <= x1 or y2 <= y1:
        return None

    crop = frame[y1:y2, x1:x2]

    if crop.size == 0:
        return None

    # ---------------------------------------------------------
    # UPSCALE FOR OCR
    # ---------------------------------------------------------

    crop_h, crop_w = crop.shape[:2]

    MIN_HEIGHT = 240
    MIN_WIDTH = 320

    scale_h = MIN_HEIGHT / crop_h
    scale_w = MIN_WIDTH / crop_w

    scale = max(
        1.0,
        scale_h,
        scale_w,
    )

    if scale > 1.0:
        new_w = int(crop_w * scale)
        new_h = int(crop_h * scale)

        crop = cv2.resize(
            crop,
            (new_w, new_h),
            interpolation=cv2.INTER_CUBIC,
        )

    # ---------------------------------------------------------
    # HIGH-QUALITY JPEG ENCODING
    # ---------------------------------------------------------

    success, encoded = cv2.imencode(
        ".jpg",
        crop,
        [
            cv2.IMWRITE_JPEG_QUALITY,
            95,
        ],
    )

    if not success:
        return None

    return base64.b64encode(
        encoded.tobytes()
    ).decode("utf-8")


def _box_center(
    bbox: list[int],
) -> tuple[float, float]:
    """Returns the center point of a bounding box."""
    x1, y1, x2, y2 = bbox

    return (
        (x1 + x2) / 2.0,
        (y1 + y2) / 2.0,
    )


def _plate_belongs_to_vehicle(
    plate_bbox: list[int],
    vehicle_bbox: list[int],
) -> bool:
    """
    Determines whether a detected plate belongs to a vehicle.

    The plate center must fall inside the vehicle bounding box.

    This is deliberately conservative. If the relationship is
    uncertain, the plate remains an independent unmatched plate
    rather than being assigned to the wrong vehicle.
    """
    px, py = _box_center(plate_bbox)

    vx1, vy1, vx2, vy2 = vehicle_bbox

    return (
        vx1 <= px <= vx2
        and vy1 <= py <= vy2
    )


def _run_full_frame_plate_detection(
    frame: np.ndarray,
) -> list[dict]:
    """
    Runs the plate detector once on the complete CCTV frame.

    These are the same settings that successfully produced the
    standalone plate detections during testing.
    """
    model = _load_plate_model()

    # ---------------------------------------------------------
    # STUB PLATE DETECTOR
    # ---------------------------------------------------------

    if model == "STUB_PLATE_MODEL":
        h, w = frame.shape[:2]

        return [
            {
                "plate_bbox": [
                    int(w * 0.35),
                    int(h * 0.40),
                    int(w * 0.45),
                    int(h * 0.45),
                ],
                "plate_confidence": 0.90,
            }
        ]

    # ---------------------------------------------------------
    # REAL PLATE DETECTOR
    # ---------------------------------------------------------

    results = model.predict(
        frame,
        conf=0.25,
        imgsz=1920,
        iou=0.45,
        max_det=20,
        verbose=False,
    )

    result = results[0]

    detections = []

    for box in result.boxes:
        px1, py1, px2, py2 = [
            int(v)
            for v in box.xyxy[0].tolist()
        ]

        conf = float(box.conf[0])

        detections.append(
            {
                "plate_bbox": [
                    px1,
                    py1,
                    px2,
                    py2,
                ],
                "plate_confidence": conf,
            }
        )

    return detections


def _match_plates_to_vehicles(
    plate_detections: list[dict],
    vehicle_detections: list[dict],
) -> dict[int, int]:
    """
    Creates plate-index -> vehicle-index associations.

    A plate is associated only when its center falls inside a
    vehicle bounding box.

    Each vehicle can receive at most one plate.

    Each plate can be associated with at most one vehicle.

    Returns:
        {
            plate_index: vehicle_index
        }
    """

    matches = {}

    # ---------------------------------------------------------
    # GENERATE POSSIBLE MATCHES
    # ---------------------------------------------------------

    candidates = []

    for plate_index, plate in enumerate(plate_detections):
        plate_bbox = plate["plate_bbox"]

        for vehicle_index, vehicle in enumerate(vehicle_detections):
            vehicle_bbox = vehicle["vehicle_bbox"]

            if _plate_belongs_to_vehicle(
                plate_bbox,
                vehicle_bbox,
            ):
                candidates.append(
                    (
                        plate_index,
                        vehicle_index,
                        plate["plate_confidence"],
                    )
                )

    # ---------------------------------------------------------
    # PRIORITIZE HIGH-CONFIDENCE PLATES
    # ---------------------------------------------------------

    candidates.sort(
        key=lambda x: x[2],
        reverse=True,
    )

    used_plates = set()
    used_vehicles = set()

    for plate_index, vehicle_index, _ in candidates:
        if plate_index in used_plates:
            continue

        if vehicle_index in used_vehicles:
            continue

        matches[plate_index] = vehicle_index

        used_plates.add(plate_index)
        used_vehicles.add(vehicle_index)

    return matches


def _build_vehicle_detection(
    vehicle: dict,
    plate_result: dict | None,
    camera_id: str,
    timestamp: str,
) -> dict:
    """
    Builds the standard vehicle detection output.
    """
    if plate_result is None:
        plate_bbox = None
        plate_confidence = 0.0
        plate_crop = None

    else:
        plate_bbox = plate_result["plate_bbox"]
        plate_confidence = float(
            plate_result["plate_confidence"]
        )
        plate_crop = plate_result["plate_crop"]

    return {
        "event_id": str(uuid.uuid4()),
        "camera_id": camera_id,
        "timestamp": timestamp,

        # vehicle_id is intentionally NOT set here.
        # A consistent vehicle_id requires cross-frame/
        # cross-camera matching, which is Member 3's
        # tracking output.

        "vehicle_bbox": vehicle["vehicle_bbox"],
        "vehicle_type": vehicle["vehicle_type"],
        "vehicle_confidence": float(
            vehicle["vehicle_confidence"]
        ),
        "vehicle_detector": vehicle["vehicle_detector"],
        "plate_bbox": plate_bbox,
        "plate_confidence": plate_confidence,
        "plate_crop": plate_crop,
    }


def _build_unmatched_plate_detection(
    plate: dict,
    plate_crop: str | None,
    camera_id: str,
    timestamp: str,
) -> dict:
    """
    Builds an output entry for a plate that was detected but
    could not be reliably associated with any vehicle.

    The plate is preserved rather than discarded.
    """
    return {
        "event_id": str(uuid.uuid4()),
        "camera_id": camera_id,
        "timestamp": timestamp,

        # No reliable vehicle association exists.
        "vehicle_bbox": None,
        "vehicle_type": None,
        "vehicle_confidence": 0.0,
        "vehicle_detector": None,

        "plate_bbox": plate["plate_bbox"],
        "plate_confidence": float(
            plate["plate_confidence"]
        ),
        "plate_crop": plate_crop,
    }


def detect(
    frame: np.ndarray,
    camera_id: str,
    timestamp: str,
    source: str,
) -> dict:
    """
    Runs vehicle detection and plate detection independently
    on the complete CCTV frame.

    Vehicle detection:
        VehicleNet-Y26x

    Plate detection:
        Fine-tuned YOLO plate detector

    Plate detections are preserved even when they cannot be
    associated with a vehicle.

    Returns:
        {
            "camera_id": str,
            "timestamp": str,
            "source": str,
            "detections": [
                {
                    "event_id": str,
                    "camera_id": str,
                    "timestamp": str,
                    "vehicle_bbox": [x1, y1, x2, y2] | None,
                    "vehicle_type": str | None,
                    "vehicle_confidence": float,
                    "vehicle_detector": str | None,
                    "plate_bbox": [x1, y1, x2, y2] | None,
                    "plate_confidence": float,
                    "plate_crop": str | None
                }
            ]
        }

    For matched detections:
        vehicle + plate information appear together.

    For unmatched plates:
        vehicle fields are None/0, while plate information
        is still preserved for OCR.

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
    # INDEPENDENT FULL-FRAME PLATE DETECTION
    # ---------------------------------------------------------

    try:
        plate_detections = _run_full_frame_plate_detection(
            frame
        )

        logger.debug(
            "Detected %d plates on full frame for camera_id=%s",
            len(plate_detections),
            camera_id,
        )

    except Exception:
        logger.exception(
            "Full-frame plate detection failed for camera_id=%s",
            camera_id,
        )

        plate_detections = []

    # ---------------------------------------------------------
    # MATCH PLATES TO VEHICLES
    # ---------------------------------------------------------

    plate_to_vehicle = _match_plates_to_vehicles(
        plate_detections,
        vehicle_detections,
    )

    # Reverse mapping for easy lookup:
    # vehicle_index -> plate_index
    vehicle_to_plate = {
        vehicle_index: plate_index
        for plate_index, vehicle_index
        in plate_to_vehicle.items()
    }

    # ---------------------------------------------------------
    # BUILD VEHICLE OUTPUTS
    # ---------------------------------------------------------

    detections = []

    for vehicle_index, vehicle in enumerate(
        vehicle_detections
    ):
        plate_result = None

        if vehicle_index in vehicle_to_plate:
            plate_index = vehicle_to_plate[
                vehicle_index
            ]

            plate = plate_detections[plate_index]

            plate_crop = _encode_plate_crop(
                frame,
                plate["plate_bbox"],
            )

            plate_result = {
                "plate_bbox": plate["plate_bbox"],
                "plate_confidence": plate[
                    "plate_confidence"
                ],
                "plate_crop": plate_crop,
            }

        detections.append(
            _build_vehicle_detection(
                vehicle=vehicle,
                plate_result=plate_result,
                camera_id=camera_id,
                timestamp=timestamp,
            )
        )

    # ---------------------------------------------------------
    # PRESERVE UNMATCHED PLATES
    # ---------------------------------------------------------

    matched_plate_indices = set(
        plate_to_vehicle.keys()
    )

    for plate_index, plate in enumerate(
        plate_detections
    ):
        if plate_index in matched_plate_indices:
            continue

        plate_crop = _encode_plate_crop(
            frame,
            plate["plate_bbox"],
        )

        detections.append(
            _build_unmatched_plate_detection(
                plate=plate,
                plate_crop=plate_crop,
                camera_id=camera_id,
                timestamp=timestamp,
            )
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

    logger.debug(
        "Vehicle detections: %d | Plate detections: %d | "
        "Matched plates: %d | Unmatched plates: %d",
        len(vehicle_detections),
        len(plate_detections),
        len(plate_to_vehicle),
        len(plate_detections) - len(plate_to_vehicle),
    )

    return {
        "camera_id": camera_id,
        "timestamp": timestamp,
        "source": source,
        "detections": detections,
    }