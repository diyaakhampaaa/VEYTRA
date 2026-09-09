"""
FastAPI wrapper for Member 1's detection module.
Exposes POST /detect, accepting a multipart image upload plus metadata.
"""

import logging

import cv2
import numpy as np
from fastapi import APIRouter, FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse

from detector import detect

logger = logging.getLogger(__name__)

app = FastAPI(title="VEYTRA Detection Service (Member 1)")
router = APIRouter()


@router.post("/detect")
async def detect_endpoint(
    image: UploadFile = File(..., description="Image file (jpg/png) to run detection on."),
    camera_id: str = Form(..., description="Identifier of the source camera."),
    timestamp: str = Form(..., description="ISO 8601 timestamp string for this frame."),
    source: str = Form(..., description='Either "real" or "simulated".'),
):
    """
    Runs vehicle + plate detection on an uploaded image.
    Returns the shared detection JSON contract. Never raises on bad input —
    returns a structured error JSON instead, so the caller's pipeline doesn't break.
    """
    try:
        contents = await image.read()
        np_arr = np.frombuffer(contents, dtype=np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except Exception:
        logger.exception("Failed to decode uploaded image for camera_id=%s", camera_id)
        return JSONResponse(
            status_code=400,
            content={
                "camera_id": camera_id,
                "timestamp": timestamp,
                "source": source,
                "detections": [],
                "error": "could_not_decode_image",
            },
        )

    if frame is None:
        return JSONResponse(
            status_code=400,
            content={
                "camera_id": camera_id,
                "timestamp": timestamp,
                "source": source,
                "detections": [],
                "error": "invalid_image_data",
            },
        )

    if source not in ("real", "simulated"):
        return JSONResponse(
            status_code=422,
            content={
                "camera_id": camera_id,
                "timestamp": timestamp,
                "source": source,
                "detections": [],
                "error": 'source must be "real" or "simulated"',
            },
        )

    result = detect(frame=frame, camera_id=camera_id, timestamp=timestamp, source=source)
    return JSONResponse(status_code=200, content=result)


app.include_router(router)