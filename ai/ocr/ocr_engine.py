"""PaddleOCR wrapper, plate-crop preprocessing, and the READ-stage contract.

``read_plate`` never raises. Complete OCR failure returns
``{"plate": None, "confidence": 0.0, "alternatives": []}``.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import cv2
import numpy as np

from ai.ocr.plate_validator import (
    generate_alternatives,
    is_valid_indian_plate,
    normalize_plate_text,
)

FAILED: dict[str, Any] = {"plate": None, "confidence": 0.0, "alternatives": []}

_OCR_SINGLETON: Any = None


def _env_flag(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def _clamp_conf(value: float) -> float:
    if value != value:  # NaN
        return 0.0
    return float(min(1.0, max(0.0, value)))


def _to_bgr(plate_crop_image: Any) -> np.ndarray | None:
    if plate_crop_image is None:
        return None
    if isinstance(plate_crop_image, (str, Path)):
        img = cv2.imread(str(plate_crop_image), cv2.IMREAD_COLOR)
        return img if img is not None and img.size else None
    if isinstance(plate_crop_image, (bytes, bytearray, memoryview)):
        buf = np.frombuffer(plate_crop_image, dtype=np.uint8)
        if buf.size == 0:
            return None
        img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
        return img if img is not None and img.size else None
    if not isinstance(plate_crop_image, np.ndarray):
        return None
    img = plate_crop_image
    if img.size == 0 or img.ndim not in (2, 3):
        return None
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if img.shape[2] == 4:
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    if img.shape[2] == 3:
        return img
    return None


def _is_unreadable(bgr: np.ndarray) -> bool:
    h, w = bgr.shape[:2]
    if h < 4 or w < 4:
        return True
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    mean, std = float(gray.mean()), float(gray.std())
    if std < 2.5:
        return True
    if mean < 6.0 and std < 8.0:
        return True
    return False


def _deskew(gray: np.ndarray) -> np.ndarray:
    if not _env_flag("VEYTRA_OCR_DESKEW", True):
        return gray
    try:
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        coords = np.column_stack(np.where(binary < 128))
        if coords.size < 40:
            coords = np.column_stack(np.where(binary >= 128))
        if coords.size < 40:
            return gray
        rect = cv2.minAreaRect(coords.astype(np.float32))
        angle = rect[-1]
        if angle < -45:
            angle = 90 + angle
        elif angle > 45:
            angle = angle - 90
        if abs(angle) < 1.5 or abs(angle) > 35:
            return gray
        h, w = gray.shape[:2]
        matrix = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), -angle, 1.0)
        return cv2.warpAffine(
            gray,
            matrix,
            (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )
    except cv2.error:
        return gray


def preprocess_plate_crop(bgr: np.ndarray) -> np.ndarray:
    """Grayscale, upscale tiny crops, CLAHE contrast, optional deskew."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    min_side = max(16, _env_int("VEYTRA_OCR_MIN_SIDE", 48))
    h, w = gray.shape[:2]
    short = min(h, w)
    if 0 < short < min_side:
        scale = min(8.0, min_side / float(short))
        gray = cv2.resize(
            gray,
            (max(1, int(w * scale)), max(1, int(h * scale))),
            interpolation=cv2.INTER_CUBIC,
        )

    tiles = 8 if min(gray.shape[:2]) >= 32 else 2
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(tiles, tiles))
    gray = clahe.apply(gray)
    gray = _deskew(gray)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def _build_paddle() -> Any:
    from paddleocr import PaddleOCR

    lang = os.getenv("VEYTRA_OCR_LANG", "en")
    use_gpu = _env_flag("VEYTRA_OCR_USE_GPU", False)
    det = _env_flag("VEYTRA_OCR_USE_DET", False)
    rec_model_dir = os.getenv("VEYTRA_OCR_REC_MODEL_DIR", "").strip() or None
    det_model_dir = os.getenv("VEYTRA_OCR_DET_MODEL_DIR", "").strip() or None

    kwargs: dict[str, Any] = {"lang": lang}
    if rec_model_dir:
        kwargs["rec_model_dir"] = rec_model_dir
    if det_model_dir:
        kwargs["det_model_dir"] = det_model_dir

    attempts = [
        {**kwargs, "use_angle_cls": True, "use_gpu": use_gpu, "show_log": False, "det": det},
        {**kwargs, "use_angle_cls": True, "device": "gpu" if use_gpu else "cpu"},
        {**kwargs, "lang": lang},
    ]
    last_error: Exception | None = None
    for attempt in attempts:
        try:
            return PaddleOCR(**attempt)
        except TypeError as exc:
            last_error = exc
            continue
    if last_error:
        raise last_error
    return PaddleOCR(lang=lang)


def _get_ocr() -> Any:
    global _OCR_SINGLETON
    if _OCR_SINGLETON is None:
        _OCR_SINGLETON = _build_paddle()
    return _OCR_SINGLETON


def _collect_ocr_pairs(result: Any) -> list[tuple[str, float]]:
    pairs: list[tuple[str, float]] = []

    def walk(node: Any) -> None:
        if node is None:
            return
        if isinstance(node, dict):
            text = node.get("rec_text") or node.get("text") or node.get("transcription")
            score = node.get("rec_score", node.get("score", node.get("confidence")))
            if text:
                try:
                    pairs.append((str(text), _clamp_conf(float(score if score is not None else 0.0))))
                except (TypeError, ValueError):
                    pairs.append((str(text), 0.0))
            for value in node.values():
                if isinstance(value, (list, tuple, dict)):
                    walk(value)
            return
        if isinstance(node, (list, tuple)):
            if (
                len(node) == 2
                and isinstance(node[0], str)
                and isinstance(node[1], (int, float))
            ):
                pairs.append((node[0], _clamp_conf(float(node[1]))))
                return
            if (
                len(node) == 2
                and isinstance(node[1], (list, tuple))
                and len(node[1]) == 2
                and isinstance(node[1][0], str)
            ):
                rec = node[1]
                pairs.append((str(rec[0]), _clamp_conf(float(rec[1]))))
                return
            for item in node:
                walk(item)

    walk(result)
    return pairs


def recognize_text(processed_bgr: np.ndarray) -> tuple[str, float]:
    """Run PaddleOCR on a preprocessed BGR crop. Returns (raw_text, confidence)."""
    ocr = _get_ocr()
    img = processed_bgr
    result = None
    try:
        result = ocr.ocr(img, det=_env_flag("VEYTRA_OCR_USE_DET", False), rec=True, cls=True)
    except TypeError:
        try:
            result = ocr.ocr(img)
        except Exception:
            predict = getattr(ocr, "predict", None)
            if predict is None:
                raise
            result = predict(img)
    except Exception:
        predict = getattr(ocr, "predict", None)
        if predict is None:
            raise
        result = predict(img)

    pairs = _collect_ocr_pairs(result)
    if not pairs:
        return "", 0.0

    scored: list[tuple[str, float, bool]] = []
    for text, conf in pairs:
        normalized = normalize_plate_text(text)
        if not normalized:
            continue
        scored.append((normalized, conf, is_valid_indian_plate(normalized)))

    if not scored:
        return "", 0.0

    valid = [item for item in scored if item[2]]
    pool = valid if valid else scored
    pool.sort(key=lambda item: item[1], reverse=True)
    best_text, best_conf, _ = pool[0]
    return best_text, best_conf


def _finalize_confidence(ocr_conf: float, valid: bool) -> float:
    conf = _clamp_conf(ocr_conf)
    if not valid:
        # Flag invalid format without inventing a different plate string.
        cap = _env_float("VEYTRA_OCR_INVALID_CONF_CAP", 0.45)
        return _clamp_conf(min(conf * 0.35, cap))
    return conf


def read_plate(plate_crop_image: Any) -> dict[str, Any]:
    """Recognize one plate crop. Independent of DETECT / TRACK / MATCH.

    Parameters
    ----------
    plate_crop_image:
        BGR/gray ``ndarray``, encoded image bytes, or filesystem path.
    """
    try:
        bgr = _to_bgr(plate_crop_image)
        if bgr is None or _is_unreadable(bgr):
            return dict(FAILED)

        processed = preprocess_plate_crop(bgr)
        raw_text, raw_conf = recognize_text(processed)
        normalized = normalize_plate_text(raw_text)
        if not normalized:
            return dict(FAILED)

        valid = is_valid_indian_plate(normalized)
        confidence = _finalize_confidence(raw_conf, valid)
        low_cut = _env_float("VEYTRA_OCR_LOW_CONFIDENCE", 0.75)
        alternatives: list[str] = []
        if (not valid) or confidence < low_cut:
            alternatives = generate_alternatives(normalized)

        return {
            "plate": normalized,
            "confidence": confidence,
            "alternatives": alternatives,
        }
    except Exception:
        return dict(FAILED)
