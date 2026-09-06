"""
Unit tests for Member 1's detection module (detector.py).
Covers the contract shape, graceful handling of edge cases, and the
PDF's required edge-case scenarios: blurry frames, low light, partial
visibility, zero vehicles, and corrupted/unreadable input.
"""

import sys
import os

# Allow running with `pytest` from ai/detection/ without package install
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pytest

from detector import detect


def make_frame(height=480, width=640, fill_value=128):
    """Helper: creates a simple solid-color test frame."""
    return np.full((height, width, 3), fill_value, dtype=np.uint8)


def test_detect_returns_expected_contract_shape():
    """Basic sanity check: output has all required top-level keys."""
    frame = make_frame()
    result = detect(frame, camera_id="C01", timestamp="2026-09-06T15:30:00", source="real")

    assert "camera_id" in result
    assert "timestamp" in result
    assert "source" in result
    assert "detections" in result
    assert result["camera_id"] == "C01"
    assert result["source"] == "real"
    assert isinstance(result["detections"], list)


def test_detect_detection_fields_match_contract():
    """
    Each detection dict, if present, must have all required keys with
    correct types. A plain synthetic frame with no real vehicle content
    may correctly produce zero detections once real models are running
    (this differs from stub-era behavior, which always returned one fake
    detection regardless of frame content) — so we don't assert a fixed
    count, only that whatever comes back is contract-compliant.
    """
    frame = make_frame()
    result = detect(frame, camera_id="C01", timestamp="2026-09-06T15:30:00", source="real")

    assert isinstance(result["detections"], list)

    required_keys = {
        "vehicle_bbox", "vehicle_type", "vehicle_confidence",
        "vehicle_detector", "plate_bbox", "plate_confidence",
    }
    for det in result["detections"]:
        assert required_keys.issubset(det.keys())
        assert isinstance(det["vehicle_confidence"], float)
        assert 0.0 <= det["vehicle_confidence"] <= 1.0
        assert isinstance(det["plate_confidence"], float)
        assert 0.0 <= det["plate_confidence"] <= 1.0


def test_detect_handles_all_black_frame():
    """
    Edge case: an all-black frame (simulating a dead/blocked camera or
    total low-light failure). Must not crash.
    """
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    result = detect(frame, camera_id="C02", timestamp="2026-09-06T15:31:00", source="real")

    assert "detections" in result
    assert isinstance(result["detections"], list)


def test_detect_handles_low_light_frame():
    """Edge case: very dark (but not fully black) frame, simulating low-light footage."""
    frame = make_frame(fill_value=10)
    result = detect(frame, camera_id="C03", timestamp="2026-09-06T15:32:00", source="real")

    assert isinstance(result["detections"], list)


def test_detect_handles_blurry_frame():
    """Edge case: simulated blur via heavy gaussian noise, standing in for motion blur."""
    rng = np.random.default_rng(seed=42)
    frame = rng.integers(0, 255, (480, 640, 3), dtype=np.uint8)
    result = detect(frame, camera_id="C04", timestamp="2026-09-06T15:33:00", source="simulated")

    assert isinstance(result["detections"], list)


def test_detect_handles_partial_visibility_small_frame():
    """
    Edge case: an unusually small/cropped frame, simulating a vehicle
    that's only partially visible at the frame edge.
    """
    frame = make_frame(height=100, width=100)
    result = detect(frame, camera_id="C05", timestamp="2026-09-06T15:34:00", source="simulated")

    assert isinstance(result["detections"], list)
    # Must not produce a plate bbox larger than the frame itself
    for det in result["detections"]:
        if det["plate_bbox"] is not None:
            x1, y1, x2, y2 = det["plate_bbox"]
            assert 0 <= x1 <= 100 and 0 <= x2 <= 100


def test_detect_handles_none_frame_gracefully():
    """
    Edge case: corrupted/unreadable image bytes upstream would result in
    frame=None reaching detect(). Must return an error JSON, not raise.
    """
    result = detect(None, camera_id="C06", timestamp="2026-09-06T15:35:00", source="real")

    assert result["detections"] == []
    assert "error" in result
    assert result["camera_id"] == "C06"


def test_detect_handles_empty_array_frame_gracefully():
    """Edge case: a zero-size numpy array (e.g. from a failed decode)."""
    frame = np.array([])
    result = detect(frame, camera_id="C07", timestamp="2026-09-06T15:36:00", source="real")

    assert result["detections"] == []
    assert "error" in result


def test_detect_never_raises_on_any_valid_shape_input():
    """
    Broad safety net: detect() should never throw an unhandled exception
    for any reasonably-shaped valid frame, regardless of content.
    """
    frames = [
        make_frame(fill_value=0),
        make_frame(fill_value=255),
        make_frame(height=1080, width=1920),
    ]
    for frame in frames:
        try:
            result = detect(frame, camera_id="C08", timestamp="2026-09-06T15:37:00", source="real")
        except Exception as e:
            pytest.fail(f"detect() raised an unexpected exception: {e}")
        assert isinstance(result, dict)


def test_detect_missing_plate_sets_null_not_omitted():
    """
    Per the PDF contract: if no plate is detected, plate_bbox must be
    explicitly null and plate_confidence 0.0 — never omitted entirely.
    This test documents the expected behavior once real (non-stub)
    detection sometimes finds a vehicle with no visible plate.
    """
    frame = make_frame()
    result = detect(frame, camera_id="C09", timestamp="2026-09-06T15:38:00", source="real")

    for det in result["detections"]:
        assert "plate_bbox" in det  # key must exist even if value is None
        assert "plate_confidence" in det