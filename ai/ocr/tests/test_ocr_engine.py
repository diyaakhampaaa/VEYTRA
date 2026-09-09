"""Unit tests for Member 2 READ-stage OCR (PaddleOCR is mocked)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai.ocr.ocr_engine import FAILED, preprocess_plate_crop, read_plate
from ai.ocr.plate_validator import (
    generate_alternatives,
    is_valid_indian_plate,
    normalize_plate_text,
)

SAMPLE_DIR = Path(__file__).resolve().parent / "sample_crops"


def _contract(result: dict) -> None:
    assert set(result) == {"plate", "confidence", "alternatives"}
    assert result["plate"] is None or isinstance(result["plate"], str)
    assert isinstance(result["confidence"], float)
    assert 0.0 <= result["confidence"] <= 1.0
    assert isinstance(result["alternatives"], list)
    assert all(isinstance(item, str) for item in result["alternatives"])


def test_normalize_strips_separators_without_rewriting_characters():
    assert normalize_plate_text("dl-01-ab-1234") == "DL01AB1234"
    assert normalize_plate_text("DLO1AB1234") == "DLO1AB1234"


def test_standard_and_bharat_formats_validate():
    assert is_valid_indian_plate("DL01AB1234")
    assert is_valid_indian_plate("MH12A1234")
    assert is_valid_indian_plate("KA03MGN1234")
    assert is_valid_indian_plate("22BH1234AA")
    assert not is_valid_indian_plate("HELLO")
    assert not is_valid_indian_plate("DL01AB123")
    assert not is_valid_indian_plate("DLO1AB1234")


def test_alternatives_do_not_mutate_primary_and_stay_valid():
    alts = generate_alternatives("DLO1AB1234")
    assert "DLO1AB1234" not in alts
    assert "DL01AB1234" in alts
    assert all(is_valid_indian_plate(item) for item in alts)


def test_read_plate_never_raises_on_garbage_inputs():
    for payload in (None, "not-a-file.jpg", np.zeros((0, 0), dtype=np.uint8), 123, []):
        result = read_plate(payload)
        _contract(result)
        assert result["plate"] is None
        assert result["confidence"] == 0.0
        assert result["alternatives"] == []


def test_unreadable_black_crop_returns_failed_contract(monkeypatch):
    """Edge case: blank/black crop must fail closed without calling OCR."""

    def boom(_img):
        raise AssertionError("OCR must not run on an unreadable crop")

    monkeypatch.setattr("ai.ocr.ocr_engine.recognize_text", boom)
    black = np.zeros((40, 120, 3), dtype=np.uint8)
    result = read_plate(black)
    _contract(result)
    assert result == FAILED or (
        result["plate"] is None and result["confidence"] == 0.0 and result["alternatives"] == []
    )


def test_unreadable_sample_file_if_present(monkeypatch):
    garbage = SAMPLE_DIR / "crop_unreadable.jpg"
    if not garbage.is_file():
        pytest.skip("sample unreadable crop not generated yet")

    monkeypatch.setattr(
        "ai.ocr.ocr_engine.recognize_text",
        lambda _img: (_ for _ in ()).throw(AssertionError("OCR skipped")),
    )
    result = read_plate(str(garbage))
    _contract(result)
    assert result["plate"] is None
    assert result["confidence"] == 0.0


def test_tiny_crop_is_upscaled_during_preprocess():
    tiny = np.full((8, 20, 3), 40, dtype=np.uint8)
    tiny[:, 4:8] = 200
    processed = preprocess_plate_crop(tiny)
    assert min(processed.shape[:2]) >= 48


def test_valid_ocr_read_matches_contract(monkeypatch):
    monkeypatch.setattr("ai.ocr.ocr_engine.recognize_text", lambda _img: ("DL 01 AB 1234", 0.94))
    crop = np.full((60, 200, 3), 180, dtype=np.uint8)
    crop[:, 20:30] = 20
    result = read_plate(crop)
    _contract(result)
    assert result["plate"] == "DL01AB1234"
    assert result["confidence"] == pytest.approx(0.94)
    assert "DL01AB1234" not in result["alternatives"]


def test_invalid_ocr_string_is_not_silently_corrected(monkeypatch):
    monkeypatch.setattr("ai.ocr.ocr_engine.recognize_text", lambda _img: ("XXXXNOTPLATE", 0.99))
    crop = np.full((60, 200, 3), 180, dtype=np.uint8)
    crop[:, 20:30] = 20
    result = read_plate(crop)
    _contract(result)
    assert result["plate"] == "XXXXNOTPLATE"
    assert result["confidence"] < 0.5
    assert result["confidence"] <= 0.45


def test_low_confidence_emits_confusion_alternatives(monkeypatch):
    monkeypatch.setattr("ai.ocr.ocr_engine.recognize_text", lambda _img: ("DL01AB1284", 0.51))
    crop = np.full((60, 200, 3), 180, dtype=np.uint8)
    crop[:, 20:30] = 20
    result = read_plate(crop)
    _contract(result)
    assert result["plate"] == "DL01AB1284"
    assert "DL01AB1234" in result["alternatives"]


def test_fastapi_post_ocr(monkeypatch):
    from ai.ocr.api import app

    monkeypatch.setattr(
        "ai.ocr.api.read_plate",
        lambda _payload: {"plate": "DL01AB1234", "confidence": 0.94, "alternatives": ["DL01AB1284"]},
    )
    client = TestClient(app)
    files = {"file": ("crop1.jpg", b"fake-bytes", "image/jpeg")}
    response = client.post("/ocr", files=files)
    assert response.status_code == 200
    body = response.json()
    assert body == {
        "plate": "DL01AB1234",
        "confidence": 0.94,
        "alternatives": ["DL01AB1284"],
    }
