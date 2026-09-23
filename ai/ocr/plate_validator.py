from __future__ import annotations

import os
import re
from typing import Iterable

# Standard private/commercial:
# state(2) + RTO(2) + series(1-3) + number(4)
# Examples:
# DL01AB1234
# AP10AR0658
# TS09EG6531
_STANDARD = re.compile(r"^[A-Z]{2}[0-9]{2}[A-Z]{1,3}[0-9]{4}$")

# Bharat series:
# YY BH #### XX
# Example: 22BH1234AA
_BHARAT = re.compile(r"^[0-9]{2}BH[0-9]{4}[A-Z]{1,2}$")

# Optional extra patterns via VEYTRA_OCR_EXTRA_PLATE_REGEX
_SEPARATORS = re.compile(r"[\s.\-_/|\\]+")
_NON_ALNUM = re.compile(r"[^A-Z0-9]")

# Character pairs that PaddleOCR commonly confuses on plates.
_CONFUSION_PAIRS: tuple[tuple[str, str], ...] = (
    ("0", "O"),
    ("1", "I"),
    ("8", "B"),
    ("5", "S"),
    ("2", "Z"),
    ("8", "3"),
)

_DEFAULT_ALT_LIMIT = 5


def _extra_patterns() -> list[re.Pattern[str]]:
    raw = os.getenv("VEYTRA_OCR_EXTRA_PLATE_REGEX", "").strip()

    if not raw:
        return []

    compiled: list[re.Pattern[str]] = []

    for chunk in raw.split(","):
        chunk = chunk.strip()

        if not chunk:
            continue

        try:
            compiled.append(re.compile(chunk))
        except re.error:
            continue

    return compiled


def normalize_plate_text(raw: str | None) -> str:
    """
    Uppercase and remove separators/non-alphanumeric characters.

    Does NOT replace characters such as O -> 0 or I -> 1.
    """
    if not raw:
        return ""

    text = str(raw).upper().replace("IND", "")
    text = _SEPARATORS.sub("", text)
    return _NON_ALNUM.sub("", text)


def is_valid_indian_plate(text: str) -> bool:
    """
    Return True only when the already-normalized string
    matches a supported Indian plate format.
    """
    if not text:
        return False

    if _STANDARD.fullmatch(text) or _BHARAT.fullmatch(text):
        return True

    return any(pattern.fullmatch(text) for pattern in _extra_patterns())


def _slot_kind(text: str, index: int) -> str | None:
    """
    Guess whether a character position should contain
    a letter or digit for near-standard plate lengths.
    """
    n = len(text)

    if 9 <= n <= 11 and text[:2].isalpha():
        # LL DD (L{1,3}) NNNN
        if index < 2:
            return "L"

        if index < 4:
            return "D"

        if index >= n - 4:
            return "D"

        return "L"

    if (
        8 <= n <= 10
        and text[:2].isdigit()
        and n >= 4
        and text[2:4] == "BH"
    ):
        # NN BH NNNN L{1,2}
        if index < 2:
            return "D"

        if index < 4:
            return "L"

        if index < 8:
            return "D"

        return "L"

    return None


def _confusion_subs(char: str) -> Iterable[str]:
    for a, b in _CONFUSION_PAIRS:
        if char == a:
            yield b
        elif char == b:
            yield a


def _iter_confusion_candidates(text: str) -> Iterable[str]:
    singles = list(_iter_single_swaps(text, kind_aware=True))

    yield from singles

    # Two independent single-position swaps cover
    # typical multi-character OCR noise.
    for i, a in enumerate(singles):
        for b in singles[i + 1 :]:
            merged = _merge_if_two_sites(text, a, b)

            if merged:
                yield merged


def _iter_single_swaps(text: str, kind_aware: bool) -> Iterable[str]:
    chars = list(text)

    for i, ch in enumerate(chars):
        kind = _slot_kind(text, i) if kind_aware else None

        for alt in _confusion_subs(ch):
            if kind == "L" and not alt.isalpha():
                continue

            if kind == "D" and not alt.isdigit():
                continue

            trial = chars.copy()
            trial[i] = alt

            yield "".join(trial)


def _merge_if_two_sites(
    original: str,
    a: str,
    b: str,
) -> str | None:
    if len(a) != len(original) or len(b) != len(original):
        return None

    diffs_a = [
        i
        for i, (x, y) in enumerate(zip(original, a))
        if x != y
    ]

    diffs_b = [
        i
        for i, (x, y) in enumerate(zip(original, b))
        if x != y
    ]

    if (
        len(diffs_a) != 1
        or len(diffs_b) != 1
        or diffs_a[0] == diffs_b[0]
    ):
        return None

    chars = list(original)

    chars[diffs_a[0]] = a[diffs_a[0]]
    chars[diffs_b[0]] = b[diffs_b[0]]

    return "".join(chars)


def generate_alternatives(
    text: str,
    limit: int | None = None,
) -> list[str]:
    """
    Generate plausible plates from common OCR confusions.

    The primary OCR string is never modified.
    """
    if limit is None:
        try:
            limit = int(
                os.getenv(
                    "VEYTRA_OCR_ALT_LIMIT",
                    str(_DEFAULT_ALT_LIMIT),
                )
            )
        except ValueError:
            limit = _DEFAULT_ALT_LIMIT

    limit = max(0, limit)

    if not text or limit == 0:
        return []

    seen = {text}
    out: list[str] = []

    for candidate in _iter_confusion_candidates(text):
        if candidate in seen:
            continue

        seen.add(candidate)

        if is_valid_indian_plate(candidate):
            out.append(candidate)

        if len(out) >= limit:
            break

    return out


def validate_plate(
    text: str | None,
    confidence: float = 0.0,
) -> dict:
    """
    Validate an OCR result using both plate format and OCR confidence.

    A result is accepted only when:
    1. It matches a supported Indian plate format.
    2. OCR confidence is at least 0.50.

    Invalid/low-confidence reads return plate=None.
    """
    plate = normalize_plate_text(text)

    valid_format = is_valid_indian_plate(plate)

    accepted = valid_format and float(confidence) >= 0.50

    return {
        "plate": plate if accepted else None,
        "valid": accepted,
        "confidence": float(confidence),
    }
