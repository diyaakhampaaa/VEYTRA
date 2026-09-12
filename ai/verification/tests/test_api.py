"""
test_api.py
-----------
Tests the actual HTTP /verify and /verification-logs endpoints,
not just the underlying Python functions.
"""

from fastapi.testclient import TestClient
from ai.verification.api import app

client = TestClient(app)


def test_verify_endpoint_corrects_suspicious_event():
    payload = {
        "event_id": "EVT_API1",
        "camera_id": "C13",
        "plate": "DL01AB1284",
        "ocr_confidence": 0.61,
        "timestamp": "2026-09-06T15:30:00",
        "reid_similarity": 0.93,
    }
    response = client.post("/verify", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["event_id"] == "EVT_API1"
    assert body["original_plate"] == "DL01AB1284"
    assert "corrected_plate" in body
    assert "verification_confidence" in body


def test_verify_endpoint_passes_through_clean_events():
    payload = {
        "event_id": "EVT_API2",
        "camera_id": "C13",
        "plate": "DL01AB1234",
        "ocr_confidence": 0.97,
        "timestamp": "2026-09-06T15:30:00",
    }
    response = client.post("/verify", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["corrected_plate"] == body["original_plate"]


def test_verification_logs_endpoint_returns_past_decisions():
    client.post("/verify", json={
        "event_id": "EVT_API3", "camera_id": "C13", "plate": "DL01AB1284",
        "ocr_confidence": 0.5, "timestamp": "2026-09-06T15:30:00",
    })

    response = client.get("/verification-logs")
    assert response.status_code == 200
    logs = response.json()
    assert isinstance(logs, list)
    assert any(log["event_id"] == "EVT_API3" for log in logs)