from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from datetime import datetime
import cv2
import numpy as np

from ai.detection.detector import detect
from ai.ocr.ocr_engine import read_plate
from ai.tracking.integration import track_and_enrich_frame

from backend.database import SessionLocal
from backend.models import DetectionEvent

router = APIRouter(prefix="/detection", tags=["Detection"])


@router.post("/run")
async def run_detection(
    file: UploadFile = File(...),
    camera_id: str = Form("CAM_01"),
    source: str = Form("real"),
):
    try:
        # ============================================================
        # 1. READ UPLOADED IMAGE
        # ============================================================

        image_bytes = await file.read()

        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )

        frame = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if frame is None:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is not a valid image."
            )

        timestamp = datetime.now().isoformat()

        # ============================================================
        # 2. DETECT VEHICLES + NUMBER PLATES
        #    MEMBER 1 — DETECTION
        # ============================================================

        result = detect(
            frame=frame,
            camera_id=camera_id,
            timestamp=timestamp,
            source=source,
        )

        # ============================================================
        # 3. OCR EVERY DETECTED PLATE
        #    MEMBER 2 — OCR
        # ============================================================

        for detection in result.get("detections", []):

            plate_bbox = detection.get("plate_bbox")

            if not plate_bbox:
                detection["plate"] = None
                detection["ocr_confidence"] = 0.0
                detection["alternatives"] = []
                continue

            try:
                x1, y1, x2, y2 = map(
                    int,
                    plate_bbox
                )

                # Keep coordinates inside image
                h, w = frame.shape[:2]

                x1 = max(0, min(x1, w))
                x2 = max(0, min(x2, w))
                y1 = max(0, min(y1, h))
                y2 = max(0, min(y2, h))

                plate_crop = frame[y1:y2, x1:x2]

                if plate_crop.size == 0:
                    raise ValueError(
                        "Plate crop is empty"
                    )

                # READ stage
                ocr_result = read_plate(
                    plate_crop
                )

                detection["plate"] = ocr_result.get(
                    "plate"
                )

                detection["ocr_confidence"] = ocr_result.get(
                    "confidence",
                    0.0
                )

                detection["alternatives"] = ocr_result.get(
                    "alternatives",
                    []
                )

            except Exception as ocr_error:

                detection["plate"] = None
                detection["ocr_confidence"] = 0.0
                detection["alternatives"] = []
                detection["ocr_error"] = str(
                    ocr_error
                )

        # ============================================================
        # 4. TRACK + RE-ID
        #    MEMBER 3 — TRACKING
        #
        # Uses:
        #   - vehicle bounding boxes from Member 1
        #   - OCR information from Member 2
        #   - original frame for Re-ID embedding
        #
        # Adds:
        #   - local_track_id
        #   - embedding
        # ============================================================

        result = track_and_enrich_frame(
            detection_result=result,
            frame=frame,
        )

        # ============================================================
        # 5. SAVE DETECTION + OCR RESULTS TO DATABASE
        # ============================================================

        db = SessionLocal()

        try:

            for detection in result.get(
                "detections",
                []
            ):

                event = DetectionEvent(
                    camera_id=camera_id,
                    timestamp=timestamp,
                    source=source,

                    vehicle_type=detection.get(
                        "vehicle_type"
                    ),

                    vehicle_confidence=detection.get(
                        "vehicle_confidence"
                    ),

                    plate=detection.get(
                        "plate"
                    ),

                    plate_confidence=detection.get(
                        "ocr_confidence"
                    ),
                )

                print(
                    "🔥 SAVING TO DB:",
                    {
                        "camera_id": camera_id,
                        "track_id": detection.get(
                            "local_track_id"
                        ),
                        "plate": detection.get(
                            "plate"
                        ),
                        "ocr_confidence": detection.get(
                            "ocr_confidence"
                        ),
                    }
                )

                db.add(event)

            db.commit()

        finally:
            db.close()

        # ============================================================
        # 6. RETURN COMPLETE PIPELINE RESULT
        # ============================================================

        return result

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Detection + OCR + Tracking failed: "
                f"{str(error)}"
            )
        )