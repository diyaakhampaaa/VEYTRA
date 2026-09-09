"""Shared settings for traffic analytics.

PostgreSQL/PostGIS is not used in this first implementation.
The sample CSV is the input source.
"""

from __future__ import annotations

from datetime import timedelta

# Canonical window names used by density.py
WINDOW_5MIN = "5min"
WINDOW_15MIN = "15min"
WINDOW_1H = "1h"

ALLOWED_WINDOWS = (WINDOW_5MIN, WINDOW_15MIN, WINDOW_1H)

WINDOW_ALIASES = {
    "5": WINDOW_5MIN,
    "5m": WINDOW_5MIN,
    "5min": WINDOW_5MIN,
    "15": WINDOW_15MIN,
    "15m": WINDOW_15MIN,
    "15min": WINDOW_15MIN,
    "60": WINDOW_1H,
    "60m": WINDOW_1H,
    "60min": WINDOW_1H,
    "1h": WINDOW_1H,
    "1hr": WINDOW_1H,
    "1hour": WINDOW_1H,
}

PANDAS_FLOOR_FREQ = {
    WINDOW_5MIN: "5min",
    WINDOW_15MIN: "15min",
    WINDOW_1H: "1h",
}

WINDOW_DURATION = {
    WINDOW_5MIN: timedelta(minutes=5),
    WINDOW_15MIN: timedelta(minutes=15),
    WINDOW_1H: timedelta(hours=1),
}


def normalize_window(window: str | int) -> str:
    """Map user input to a canonical window name."""
    key = str(window).strip().lower()
    if key not in WINDOW_ALIASES:
        allowed = ", ".join(ALLOWED_WINDOWS)
        raise ValueError(f"Unsupported time window {window!r}. Use one of: {allowed}.")
    return WINDOW_ALIASES[key]
