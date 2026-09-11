"""Load sample vehicle-event data for analytics.

Until another member provides a live event store, density reads the
controlled CSV under analytics/data/.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PACKAGE_DIR = Path(__file__).resolve().parent
SAMPLE_EVENTS_PATH = PACKAGE_DIR / "data" / "sample_vehicle_events.csv"

REQUIRED_COLUMNS = (
    "vehicle_id",
    "camera_id",
    "timestamp",
    "road_segment_id",
)


def load_vehicle_events(path: str | Path | None = None) -> pd.DataFrame:
    """Read vehicle sightings and parse timestamps.

    Extra columns (plate, lat/lon, direction, trajectory) are kept for
    later modules but are not required for density.
    """
    csv_path = Path(path) if path is not None else SAMPLE_EVENTS_PATH
    if not csv_path.exists():
        raise FileNotFoundError(f"Vehicle events file not found: {csv_path}")

    df = pd.read_csv(csv_path)
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Vehicle events CSV is missing required columns: {missing}")

    # Keep the original offset so 1-hour bins follow local city time,
    # not UTC clock hours.
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df
