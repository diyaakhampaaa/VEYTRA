"""
test_end_to_end.py
-------------------
THE core USP test, as required by the spec:

    Actual plate: DL01AB1234
    C01 -> DL01AB1234  (correct)
    C02 -> DL01AB1284  (WRONG - injected error)
    C03 -> DL01AB1234  (correct)

VEYTRA must: flag C02 as suspicious, find C01 + C03 as supporting
evidence, correct C02's record to DL01AB1234, and log the decision --
all while keeping the original wrong reading intact in the output.

We reuse our existing camera_network.py (C13-C14-C15-C16-C18) and just
rename them to C01/C02/C03 in this test for clarity against the spec's
exact wording -- the underlying logic doesn't care about the names.
"""

from ai.verification.suspicion import check_suspicion
from ai.verification.evidence import find_supporting_evidence
from ai.verification.scoring import find_best_candidate
from ai.verification.correction import apply_correction
from ai.verification.logger import log_verification_decision, get_all_logs
import ai.verification.camera_network as camera_network
import ai.verification.fake_event_store as fake_event_store


def run_pipeline(event: dict, reid_similarity=None) -> dict:
    verdict = check_suspicion(event)
    if not verdict["is_suspicious"]:
        return {
            "event_id": event["event_id"],
            "original_plate": event["plate"],
            "corrected_plate": event["plate"],
            "reason": "Not flagged as suspicious",
        }
    supporting = find_supporting_evidence(event)
    best = find_best_candidate(event["plate"], supporting, reid_similarity)
    result = apply_correction(event["event_id"], event["plate"], best, reid_similarity)
    log_verification_decision(result, original_confidence=event.get("ocr_confidence"))
    return result


def test_usp_scenario_catches_and_corrects_wrong_plate(monkeypatch):
    # Set up the exact scenario from the spec, using our test camera network
    monkeypatch.setattr(camera_network, "CAMERA_CONNECTIONS", {
        "C01": {"C02": 90},
        "C02": {"C01": 90, "C03": 90},
        "C03": {"C02": 90},
    })
    monkeypatch.setattr(fake_event_store, "SAMPLE_EVENTS", [
        {"event_id": "EVT_C01", "camera_id": "C01", "plate": "DL01AB1234",
         "timestamp": "2026-09-06T15:28:00", "ocr_confidence": 0.95},
        {"event_id": "EVT_C02", "camera_id": "C02", "plate": "DL01AB1284",
         "timestamp": "2026-09-06T15:29:30", "ocr_confidence": 0.61},
        {"event_id": "EVT_C03", "camera_id": "C03", "plate": "DL01AB1234",
         "timestamp": "2026-09-06T15:31:00", "ocr_confidence": 0.93},
    ])

    suspicious_event = {
        "event_id": "EVT_C02",
        "camera_id": "C02",
        "plate": "DL01AB1284",  # the injected wrong reading
        "ocr_confidence": 0.61,
        "timestamp": "2026-09-06T15:29:30",
    }

    result = run_pipeline(suspicious_event, reid_similarity=0.93)

    # The core USP assertions:
    assert result["original_plate"] == "DL01AB1284"  # original NEVER lost
    assert result["corrected_plate"] == "DL01AB1234"  # corrected to the true plate
    assert set(result["supporting_cameras"]) == {"C01", "C03"}  # both neighbours found
    assert result["verification_confidence"] > 0.75  # confident enough to act

    # Confirm it was actually logged for audit purposes
    logs = get_all_logs()
    assert any(log["event_id"] == "EVT_C02" and log["corrected_plate"] == "DL01AB1234" for log in logs)


def test_usp_scenario_does_not_merge_two_genuinely_different_vehicles():
    """A vehicle seen alone, with no real supporting evidence, must
    NOT be force-corrected just because some other unrelated plate
    exists somewhere in the system."""
    lonely_event = {
        "event_id": "EVT_LONELY",
        "camera_id": "C99",  # not in our camera network at all
        "plate": "MH12ZZ0000",
        "ocr_confidence": 0.55,
        "timestamp": "2026-09-06T15:30:00",
    }
    result = run_pipeline(lonely_event, reid_similarity=None)
    assert result["corrected_plate"] == result["original_plate"]  # left unchanged
