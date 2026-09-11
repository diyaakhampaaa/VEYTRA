from ai.ocr.integration import read_plate_from_file

result = read_plate_from_file(
    "ai/ocr/tests/sample_crops/crop1.jpg"
)

detection = {
    "vehicle_bbox": [100, 100, 500, 400],
    "plate_text": result["plate"],
    "ocr_confidence": result["confidence"],
    "ocr_alternatives": result["alternatives"],
}

print(detection)