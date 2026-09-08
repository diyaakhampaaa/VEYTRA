from ai.verification.suspicion import check_suspicion


def test_clean_event_is_not_suspicious():
    event = {"plate": "DL01AB1234", "ocr_confidence": 0.94, "nearby_events": []}
    result = check_suspicion(event)
    assert result["is_suspicious"] is False


def test_low_confidence_is_flagged():
    event = {"plate": "DL01AB1284", "ocr_confidence": 0.61, "nearby_events": []}
    result = check_suspicion(event)
    assert result["is_suspicious"] is True
    assert "low_ocr_confidence" in result["reasons"]


def test_neighbour_disagreement_is_flagged_even_with_high_confidence():
    """Proves the disagreement rule works on its own, not just riding
    on the low-confidence rule."""
    event = {
        "plate": "DL01AB1284",
        "ocr_confidence": 0.92,
        "nearby_events": [{"plate": "DL01AB1234"}],
    }
    result = check_suspicion(event)
    assert result["is_suspicious"] is True
    assert "neighbour_disagreement" in result["reasons"]


def test_missing_plate_does_not_crash():
    event = {"plate": None, "ocr_confidence": 0.5, "nearby_events": []}
    result = check_suspicion(event)
    assert isinstance(result["is_suspicious"], bool)
