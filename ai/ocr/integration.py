from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

from ai.ocr.ocr_engine import read_plate


def read_plate_crop(plate_crop: Any) -> dict:
    """Run OCR on the base64 JPEG plate crop from Member 1."""
    if not isinstance(plate_crop, str) or not plate_crop:
        return {
            "plate": None,
            "confidence": 0.0,
            "alternatives": [],
        }

    try:
        image_bytes = base64.b64decode(plate_crop)
    except Exception:
        return {
            "plate": None,
            "confidence": 0.0,
            "alternatives": [],
        }

    return read_plate(image_bytes)


def read_plate_from_file(image_path: str | Path) -> dict:
    """Run OCR directly on an image file."""
    return read_plate(image_path)