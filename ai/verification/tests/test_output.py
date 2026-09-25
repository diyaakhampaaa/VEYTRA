"""
test_output.py
---------------
Tests the dashboard-facing output shape Member 2 asked for:
event identity preserved, verification_status exposed, plate_number
is the final trusted plate, ocr_confidence passed through.
"""

from ai.verification.output import to_dashboard_record


def test_verified_status_when_reading_confirmed_as_is():
    correction_result = {
        "event_id": "E001",
        "original_plate": "DL01AB1234",
        "corrected_plate": "DL01AB1234",
        "supporting_cameras": [],
        "verification_confidence": 1.0,
        "reason": "Not flagged as suspicious",
    }
    record = to_dashboard_record(correction_result, vehicle_id="V001", ocr_confidence=0.94)

    assert record["event_id"] == "E001"
    assert record["vehicle_id"] == "V001"
    assert record["plate_number"] == "DL01AB1234"
    assert record["verification_status"] == "verified"
    assert record["ocr_confidence"] == 0.94


def test_corrected_status_when_plate_actually_changed():
    correction_result = {
        "event_id": "E002",
        "original_plate": "DL01AB1284",
        "corrected_plate": "DL01AB1234",
        "supporting_cameras": ["C13", "C15"],
        "verification_confidence": 0.93,
        "reason": "Neighbouring camera agreement",
    }
    record = to_dashboard_record(correction_result, vehicle_id="V002", ocr_confidence=0.61)

    assert record["plate_number"] == "DL01AB1234"  # final, corrected value
    assert record["original_plate"] == "DL01AB1284"  # original still exposed
    assert record["verification_status"] == "corrected"


def test_unverified_status_when_insufficient_evidence():
    correction_result = {
        "event_id": "E003",
        "original_plate": "MH12ZZ0000",
        "corrected_plate": "MH12ZZ0000",
        "supporting_cameras": [],
        "verification_confidence": 0.0,
        "reason": "Insufficient supporting evidence",
    }
    record = to_dashboard_record(correction_result, vehicle_id=None, ocr_confidence=0.5)

    assert record["verification_status"] == "unverified"
    assert record["vehicle_id"] is None  # never invented, just passed through as-is


def test_backward_compatible_fields_still_present():
    """Existing consumers relying on original_plate/corrected_plate/
    verification_confidence must not break."""
    correction_result = {
        "event_id": "E004",
        "original_plate": "DL01AB1284",
        "corrected_plate": "DL01AB1234",
        "supporting_cameras": ["C01"],
        "reid_similarity": 0.9,
        "verification_confidence": 0.85,
        "reason": "Neighbouring camera agreement",
    }
    record = to_dashboard_record(correction_result, vehicle_id="V004", ocr_confidence=0.6)

    assert record["original_plate"] == "DL01AB1284"
    assert record["corrected_plate"] == "DL01AB1234"
    assert record["verification_confidence"] == 0.85
    assert record["supporting_cameras"] == ["C01"]
    assert record["reid_similarity"] == 0.9
