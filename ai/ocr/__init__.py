"""VEYTRA Member 2 — READ stage (license-plate OCR).

Public contract consumed by Member 3 / Member 4:

    read_plate(plate_crop_image) -> {
        "plate": str | None,
        "confidence": float,  # always in [0, 1]
        "alternatives": list[str],
    }
"""

from ai.ocr.ocr_engine import read_plate

__all__ = ["read_plate"]
