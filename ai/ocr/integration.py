from pathlib import Path
from typing import Any

from ai.ocr.ocr_engine import read_plate


def read_plate_crop(plate_crop: Any) -> dict:
    return read_plate(plate_crop)


def read_plate_from_file(image_path: str | Path) -> dict:
    path = Path(image_path)

    if not path.exists():
        return {
            "plate": None,
            "confidence": 0.0,
            "alternatives": [],
        }

    return read_plate(path)