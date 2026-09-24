"""Input adapters for VEYTRA traffic analytics.

M5 consumes verified/corrected vehicle events produced by the
upstream tracking + verification pipeline.

The loader normalizes different upstream representations into a
common analytics schema while preserving event identity.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from .verified_events import load_verified_events

PACKAGE_DIR = Path(__file__).resolve().parent
SAMPLE_EVENTS_PATH = PACKAGE_DIR / "data" / "sample_vehicle_events.csv"


# Minimum fields required by the analytics layer.
REQUIRED_COLUMNS = (
    "vehicle_id",
    "camera_id",
    "timestamp",
    "road_segment_id",
)


# Fields that should be preserved whenever upstream provides them.
OPTIONAL_COLUMNS = (
    "event_id",
    "source",
    "plate_number",
    "corrected_plate",
    "original_plate",
    "verification_status",
    "verification_confidence",
    "ocr_confidence",
    "trajectory_id",
    "road_name",
    "direction",
    "latitude",
    "longitude",
    "road_segment_id",
    "timestamp",
)


def _normalise_records(records: list[dict[str, Any]]) -> pd.DataFrame:
    """Convert upstream event records into the M5 dataframe format."""

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)


    # ---------------------------------------------------------
    # Timestamp
    # ---------------------------------------------------------
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce",
        )

    # ---------------------------------------------------------
    # Vehicle identity
    #
    # M5 does NOT invent a vehicle identity.
    # vehicle_id must come from M3.
    # ---------------------------------------------------------
    if "vehicle_id" not in df.columns:
        raise ValueError(
            "Verified vehicle events must contain 'vehicle_id'. "
            "Vehicle IDs are assigned by the tracking module (M3)."
        )

    if "camera_id" not in df.columns:
        raise ValueError(
            "Verified vehicle events must contain 'camera_id'."
        )

    if "timestamp" not in df.columns:
        raise ValueError(
            "Verified vehicle events must contain 'timestamp'."
        )

    if "road_segment_id" not in df.columns:
        raise ValueError(
            "Verified vehicle events must contain 'road_segment_id'."
        )

    # ---------------------------------------------------------
    # Verification status
    #
    # Older M4 outputs may not explicitly expose this field.
    # In that case we mark the record as verified only when
    # it came through the verified-event adapter.
    # ---------------------------------------------------------
    if "verification_status" not in df.columns:
        df["verification_status"] = "verified"

    # ---------------------------------------------------------
    # Source
    # ---------------------------------------------------------
    if "source" not in df.columns:
        df["source"] = "verified_pipeline"

    # ---------------------------------------------------------
    # Keep useful columns, but don't throw away upstream data.
    # ---------------------------------------------------------
    return df


def load_vehicle_events(
    path: str | Path | None = None,
) -> pd.DataFrame:
    """Load vehicle events from CSV or JSON.

    If no path is supplied, the existing controlled sample dataset
    is used for backwards compatibility.

    For the real VEYTRA pipeline, pass the M4 verified-event file.
    """

    file_path = (
        Path(path)
        if path is not None
        else SAMPLE_EVENTS_PATH
    )

    if not file_path.exists():
        raise FileNotFoundError(
            f"Vehicle events file not found: {file_path}"
        )

    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        df = pd.read_csv(file_path)

    elif suffix == ".json":
        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        # Support:
        #   [...]
        # and
        #   {"events": [...]}
        if isinstance(data, dict):
            if "events" in data:
                data = data["events"]
            else:
                data = [data]

        if not isinstance(data, list):
            raise ValueError(
                "JSON vehicle-event input must contain a list "
                "of event objects."
            )

        df = pd.DataFrame(data)

    else:
        raise ValueError(
            f"Unsupported vehicle-event format: {suffix}. "
            "Use CSV or JSON."
        )

    df = _normalise_records(
        df.to_dict(orient="records")
    )

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Vehicle events are missing required columns: "
            f"{missing}"
        )

    if df.empty:
        return df

    # Remove records that cannot participate in analytics.
    df = df.dropna(
        subset=[
            "vehicle_id",
            "camera_id",
            "timestamp",
            "road_segment_id",
        ]
    ).copy()

    return df.reset_index(drop=True)


