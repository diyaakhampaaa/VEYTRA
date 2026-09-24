"""
M3/M4 -> M5 adapter.

Converts reconstructed M3 trajectories plus M4 verification/correction
results into the normalized event schema consumed by M5 analytics.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


REQUIRED_COLUMNS = (
    "event_id",
    "vehicle_id",
    "camera_id",
    "timestamp",
    "road_segment_id",
)

ALLOWED_STATUSES = {
    "verified",
    "corrected",
    "accepted",
}


def _first(record: dict[str, Any], *keys: str) -> Any:
    """Return the first non-empty value among the supplied keys."""
    for key in keys:
        value = record.get(key)
        if value is not None and value != "":
            return value
    return None


def _normalise_status(value: Any) -> str:
    if value is None:
        return "verified"

    status = str(value).strip().lower()

    mapping = {
        "pending": "pending",
        "verified": "verified",
        "accepted": "accepted",
        "corrected": "corrected",
        "rejected": "rejected",
        "failed": "rejected",
    }

    return mapping.get(status, status)


def _apply_correction(
    event: dict[str, Any],
    correction: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Merge one M4 correction result onto an M3 event.

    M4 may only contain the correction-specific fields, so all
    trajectory/camera/timestamp/location information remains sourced
    from M3.
    """
    result = dict(event)

    original_plate = _first(
        event,
        "plate_number",
        "plate",
        "plate_text",
        "original_plate",
    )

    result["original_plate"] = original_plate

    if correction is None:
        result["corrected_plate"] = None
        result["verification_status"] = _normalise_status(
            event.get("verification_status", "verified")
        )
        result["verification_confidence"] = event.get(
            "verification_confidence"
        )
        return result

    corrected_plate = _first(
        correction,
        "corrected_plate",
        "corrected_plate_text",
        "corrected_plate_number",
    )

    correction_original = _first(
        correction,
        "original_plate",
        "plate_number",
        "plate",
    )

    result["original_plate"] = (
        correction_original
        if correction_original is not None
        else original_plate
    )

    result["corrected_plate"] = corrected_plate

    if corrected_plate:
        result["plate_number"] = corrected_plate
        result["verification_status"] = "corrected"
    else:
        result["plate_number"] = result["original_plate"]
        result["verification_status"] = _normalise_status(
            correction.get("verification_status", "verified")
        )

    result["verification_confidence"] = _first(
        correction,
        "verification_confidence",
        "confidence",
    )

    result["verification_reason"] = _first(
        correction,
        "reason",
        "verification_reason",
    )

    result["supporting_cameras"] = correction.get(
        "supporting_cameras"
    )

    result["reid_similarity"] = correction.get(
        "reid_similarity"
    )

    return result


def _extract_trajectory_list(
    m3_result: dict[str, Any] | list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Extract trajectory records from the M3 result."""
    if isinstance(m3_result, list):
        return m3_result

    if not isinstance(m3_result, dict):
        raise ValueError("M3 result must be a dict or list.")

    trajectories = m3_result.get("trajectories")

    if isinstance(trajectories, list):
        return trajectories

    # Also support a single trajectory object.
    if "vehicle_id" in m3_result:
        return [m3_result]

    raise ValueError(
        "M3 result does not contain a 'trajectories' list."
    )


def _extract_m3_events(
    m3_result: dict[str, Any] | list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Flatten M3 trajectories into event-level records.

    Preferred source:
        trajectory["event_observations"]

    Fallback:
        trajectory["observations"]
    """
    trajectories = _extract_trajectory_list(m3_result)

    events: list[dict[str, Any]] = []

    for trajectory in trajectories:
        vehicle_id = trajectory.get("vehicle_id")
        trajectory_id = trajectory.get("trajectory_id")

        nested = trajectory.get("event_observations")

        if not isinstance(nested, list):
            nested = trajectory.get("observations", [])

        if not isinstance(nested, list):
            continue

        for observation in nested:
            if not isinstance(observation, dict):
                continue

            event = dict(observation)

            event["vehicle_id"] = _first(
                event,
                "vehicle_id",
            ) or vehicle_id

            event["trajectory_id"] = _first(
                event,
                "trajectory_id",
            ) or trajectory_id

            event["event_id"] = _first(
                event,
                "event_id",
            )

            event["camera_id"] = _first(
                event,
                "camera_id",
            )

            event["timestamp"] = _first(
                event,
                "timestamp",
                "time",
            )

            event["road_segment_id"] = _first(
                event,
                "road_segment_id",
            )

            event["latitude"] = _first(
                event,
                "latitude",
                "lat",
            )

            event["longitude"] = _first(
                event,
                "longitude",
                "lon",
            )

            event["plate_number"] = _first(
                event,
                "plate_number",
                "plate",
                "plate_text",
            )

            event["direction"] = _first(
                event,
                "direction",
            )

            event["road_name"] = _first(
                event,
                "road_name",
            )

            event["verification_status"] = _normalise_status(
                event.get("verification_status")
            )

            events.append(event)

    return events


def _index_corrections(
    corrections: Any,
) -> dict[str, dict[str, Any]]:
    """
    Index M4 correction records by event_id.

    Supports:
      - list of correction dictionaries
      - {"corrections": [...]}
      - {"results": [...]}
      - {"correction_results": [...]}
    """
    if corrections is None:
        return {}

    if isinstance(corrections, dict):
        for key in (
            "corrections",
            "results",
            "correction_results",
            "verification_results",
        ):
            candidate = corrections.get(key)
            if isinstance(candidate, list):
                corrections = candidate
                break

    if not isinstance(corrections, list):
        return {}

    indexed: dict[str, dict[str, Any]] = {}

    for correction in corrections:
        if not isinstance(correction, dict):
            continue

        event_id = _first(
            correction,
            "event_id",
        )

        if event_id is None:
            continue

        indexed[str(event_id)] = correction

    return indexed


def normalize_m3_m4_events(
    m3_result: dict[str, Any] | list[dict[str, Any]],
    m4_corrections: Any = None,
) -> pd.DataFrame:
    """
    Convert M3 trajectories + optional M4 corrections into M5 events.
    """
    events = _extract_m3_events(m3_result)

    corrections = _index_corrections(m4_corrections)

    normalized: list[dict[str, Any]] = []

    for event in events:
        event_id = event.get("event_id")

        # M5 must preserve upstream event identity.
        # Never invent an event ID here.
        if event_id is None:
            continue

        correction = corrections.get(str(event_id))

        record = _apply_correction(
            event,
            correction,
        )

        normalized.append(record)

    if not normalized:
        return pd.DataFrame(columns=REQUIRED_COLUMNS)

    df = pd.DataFrame(normalized)

    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            df[column] = None

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
        utc=True,
    )

    for column in (
        "event_id",
        "vehicle_id",
        "camera_id",
        "road_segment_id",
    ):
        df[column] = df[column].astype("string")

    df = df.dropna(
        subset=list(REQUIRED_COLUMNS)
    ).copy()

    status = df["verification_status"].astype(str).str.lower()

    df = df[
        status.isin(ALLOWED_STATUSES)
    ].copy()

    return df.reset_index(drop=True)


def load_m3_m4_events(
    m3_path: str | Path,
    m4_path: str | Path | None = None,
) -> pd.DataFrame:
    """Load M3 trajectory JSON and optional M4 correction JSON."""

    m3_path = Path(m3_path)

    with m3_path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        m3_result = json.load(handle)

    m4_result = None

    if m4_path is not None:
        m4_path = Path(m4_path)

        with m4_path.open(
            "r",
            encoding="utf-8",
        ) as handle:
            m4_result = json.load(handle)

    return normalize_m3_m4_events(
        m3_result,
        m4_result,
    )


def dataframe_to_records(
    df: pd.DataFrame,
) -> list[dict[str, Any]]:
    """Convert normalized M5 events to JSON-safe records."""
    if df.empty:
        return []

    result = df.copy()

    if "timestamp" in result.columns:
        result["timestamp"] = result["timestamp"].astype(str)

    return result.where(
        pd.notna(result),
        None,
    ).to_dict(
        orient="records"
    )

def load_verified_events(
    path: str | Path,
) -> pd.DataFrame:
    """
    Backward-compatible loader used by the existing M5 analytics modules.

    Supports CSV and JSON files containing already-normalized verified
    event records.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Verified events file not found: {path}")

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)

        for column in REQUIRED_COLUMNS:
            if column not in df.columns:
                raise ValueError(
                    f"Missing required column '{column}' in {path}"
                )

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce",
            utc=True,
        )

        if "verification_status" not in df.columns:
            df["verification_status"] = "verified"

        status = (
            df["verification_status"]
            .astype(str)
            .str.lower()
        )

        df = df[
            status.isin(ALLOWED_STATUSES)
        ].copy()

        return df.reset_index(drop=True)

    if path.suffix.lower() == ".json":
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        # If this is an M3 trajectory file, use the new M3/M4 adapter.
        if isinstance(data, dict) and "trajectories" in data:
            return normalize_m3_m4_events(data)

        if isinstance(data, list):
            return normalize_m3_m4_events(data)

        if isinstance(data, dict):
            records = (
                data.get("events")
                or data.get("observations")
                or data.get("records")
            )

            if isinstance(records, list):
                return normalize_m3_m4_events(records)

        raise ValueError(
            f"Unsupported verified-events JSON structure: {path}"
        )

    raise ValueError(
        f"Unsupported verified-events file type: {path.suffix}"
    )