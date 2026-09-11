"""
test_integration.py
--------------------
Proves our module works against Member 3's REAL verification_payloads()
output shape (confirmed from ai/tracking/tests/test_matcher.py's
test_plate_mismatch_veto), not just our own placeholder data.
"""

from ai.verification.integration import group_payloads_by_event, process_verification_payloads


def _sample_payload():
    """Mimics exactly what Member 3's verification_payloads() returns
    for one plate-mismatch candidate."""
    return {
        "event_id": "C02:2:2026-09-06T08:01:40+05:30",
        "camera_id": "C02",
        "plate": "MH02CD9999",       # the lower-confidence, likely-wrong reading
        "ocr_confidence": 0.58,
        "timestamp": "2026-09-06T08:01:40+05:30",
        "reid_similarity": 0.91,     # Member 3's appearance score
        "nearby_events": [{
            "event_id": "C01:1:2026-09-06T08:00:00+05:30",
            "camera_id": "C01",
            "plate": "DL01AB1234",   # the correct reading, seen elsewhere
            "ocr_confidence": 0.95,
            "timestamp": "2026-09-06T08:00:00+05:30",
        }],
        "match_score": {"overall": 0.88, "appearance": 0.91, "time": 0.9, "spatial": 0.85, "plate": 0.0},
        "verification_reason": "plate_mismatch",
    }


def test_group_payloads_merges_same_event():
    payload_1 = _sample_payload()
    payload_2 = _sample_payload()
    payload_2["nearby_events"] = [{
        "event_id": "C03:1:2026-09-06T08:03:00+05:30",
        "camera_id": "C03",
        "plate": "DL01AB1234",
        "ocr_confidence": 0.90,
        "timestamp": "2026-09-06T08:03:00+05:30",
    }]

    grouped = group_payloads_by_event([payload_1, payload_2])

    assert len(grouped) == 1  # same event_id -> merged into one
    assert len(grouped[0]["nearby_events"]) == 2  # both supporting events kept


def test_process_real_shaped_payload_corrects_a_realistic_ocr_error():
    """
    NOTE: Member 3's own test_plate_mismatch_veto example (MH02CD9999 vs
    DL01AB1234) uses two genuinely DIFFERENT plates -- that's intentional
    on their end, to prove their matcher correctly separates two
    different vehicles. It is NOT a realistic OCR-misread case, so our
    scoring correctly REFUSES to merge it (confirmed separately below).

    This test uses a realistic near-miss (one character off) -- the
    actual kind of error our USP is meant to catch and fix.
    """
    payload = _sample_payload()
    payload["plate"] = "DL01AB1284"  # realistic OCR misread: 8 instead of 3
    payload["nearby_events"][0]["plate"] = "DL01AB1234"  # the true plate

    results = process_verification_payloads([payload])

    assert len(results) == 1
    result = results[0]
    assert result["original_plate"] == "DL01AB1284"     # wrong reading preserved
    assert result["corrected_plate"] == "DL01AB1234"    # corrected using Member 3's evidence
    assert "C01" in result["supporting_cameras"]
    assert result["verification_confidence"] > 0.75


def test_process_real_shaped_payload_refuses_to_merge_genuinely_different_vehicles():
    """
    Confirms the earlier finding: two completely different plates
    (different state codes) must NOT be merged, even with strong
    appearance similarity -- this protects against merging two
    different cars that simply look alike.
    """
    payload = _sample_payload()  # MH02CD9999 vs DL01AB1234 -- genuinely different

    results = process_verification_payloads([payload])

    result = results[0]
    assert result["corrected_plate"] == result["original_plate"]  # left unchanged, correctly cautious
