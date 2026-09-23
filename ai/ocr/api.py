"""FastAPI wrapper for the READ stage.

Accepts a Member 1 detection event containing a base64-encoded plate crop,
runs the existing OCR engine, and returns the same event enriched with OCR
results.

Member 2 does not assign vehicle_id. That belongs to Member 3 tracking/Re-ID.
"""

from __future__ import annotations

import base64
import binascii
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Form, HTTPException

# Allow imports when running the API from the repository root.
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ai.ocr.ocr_engine import read_plate


app = FastAPI(
    title="VEYTRA OCR",
    description="Member 2 READ stage — enriches detection events with plate OCR.",
    version="2.0.0",
)


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "VEYTRA OCR", "stage": "READ"}


def _decode_plate_crop(plate_crop: str) -> bytes:
    """Decode M1's base64-encoded JPEG plate crop."""
    if not plate_crop:
        raise ValueError("plate_crop is empty")

    try:
        return base64.b64decode(plate_crop, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("plate_crop is not valid base64") from exc


@app.post("/ocr")
async def ocr_endpoint(
    event_id: str = Form(...),
    camera_id: str = Form(...),
    timestamp: str = Form(...),
    source: str = Form(...),
    plate_crop: str = Form(...),
    vehicle_type: str | None = Form(None),
    vehicle_confidence: float | None = Form(None),
) -> dict[str, Any]:
    """Run OCR on a Member 1 detection event.

    The event_id, camera_id, and timestamp are preserved so downstream
    tracking/verification can associate this OCR result with the original
    detection event.

    vehicle_id is intentionally not accepted or generated here.
    """

    try:
        crop_bytes = _decode_plate_crop(plate_crop)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    ocr_result = read_plate(crop_bytes)

    return {
        "event_id": event_id,
        "camera_id": camera_id,
        "timestamp": timestamp,
        "source": source,
        "vehicle_type": vehicle_type,
        "vehicle_confidence": vehicle_confidence,
        "plate_number": ocr_result["plate"],
        "ocr_confidence": ocr_result["confidence"],
        "alternatives": ocr_result["alternatives"],
    }