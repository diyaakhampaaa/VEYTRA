"""
Rule-based congestion propagation across connected cameras.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


def propagate_congestion(
    congestion: pd.DataFrame,
    camera_transitions: pd.DataFrame,
    propagation_minutes: int = 5,
    score_decay: float = 0.90,
    congestion_threshold: float = 0.60,
) -> pd.DataFrame:
    """
    Propagate congestion from one camera to connected cameras.

    congestion columns:
        camera_id
        timestamp
        congestion_score
        congestion_level

    camera_transitions columns:
        source_camera_id
        target_camera_id

    Returns:
        source_camera_id
        target_camera_id
        timestamp
        propagated_score
        propagated_level
        propagation_reason
    """

    required_congestion = {
        "camera_id",
        "timestamp",
        "congestion_score",
    }

    required_transitions = {
        "source_camera_id",
        "target_camera_id",
    }

    missing_congestion = required_congestion - set(congestion.columns)
    missing_transitions = required_transitions - set(camera_transitions.columns)

    if missing_congestion:
        raise ValueError(
            f"Missing congestion columns: {sorted(missing_congestion)}"
        )

    if missing_transitions:
        raise ValueError(
            f"Missing transition columns: {sorted(missing_transitions)}"
        )

    if not 0 < score_decay <= 1:
        raise ValueError("score_decay must be between 0 and 1.")

    if propagation_minutes <= 0:
        raise ValueError("propagation_minutes must be positive.")

    congestion = congestion.copy()
    camera_transitions = camera_transitions.copy()

    congestion["timestamp"] = pd.to_datetime(
        congestion["timestamp"],
        errors="coerce",
    )

    congestion["congestion_score"] = pd.to_numeric(
        congestion["congestion_score"],
        errors="coerce",
    )

    congestion = congestion.dropna(
        subset=["camera_id", "timestamp", "congestion_score"]
    )

    congested = congestion[
        congestion["congestion_score"] >= congestion_threshold
    ]

    results: list[dict[str, Any]] = []

    for _, event in congested.iterrows():
        source_camera = event["camera_id"]
        source_score = float(event["congestion_score"])
        source_time = event["timestamp"]

        connected = camera_transitions[
            camera_transitions["source_camera_id"] == source_camera
        ]

        for _, transition in connected.iterrows():
            target_camera = transition["target_camera_id"]

            propagated_score = round(
                min(1.0, source_score * score_decay),
                4,
            )

            if propagated_score >= 0.80:
                level = "severe"
            elif propagated_score >= 0.60:
                level = "high"
            elif propagated_score >= 0.35:
                level = "moderate"
            else:
                level = "low"

            results.append(
                {
                    "source_camera_id": source_camera,
                    "target_camera_id": target_camera,
                    "timestamp": source_time
                    + pd.Timedelta(minutes=propagation_minutes),
                    "propagated_score": propagated_score,
                    "propagated_level": level,
                    "propagation_reason": (
                        "Congestion propagated from connected upstream camera"
                    ),
                }
            )

    return pd.DataFrame(
        results,
        columns=[
            "source_camera_id",
            "target_camera_id",
            "timestamp",
            "propagated_score",
            "propagated_level",
            "propagation_reason",
        ],
    )


if __name__ == "__main__":
    congestion_data = pd.DataFrame(
        [
            {
                "camera_id": "CAM_01",
                "timestamp": "2026-09-10 10:00:00",
                "congestion_score": 0.90,
                "congestion_level": "severe",
            },
            {
                "camera_id": "CAM_02",
                "timestamp": "2026-09-10 10:00:00",
                "congestion_score": 0.20,
                "congestion_level": "low",
            },
        ]
    )

    transition_data = pd.DataFrame(
        [
            {
                "source_camera_id": "CAM_01",
                "target_camera_id": "CAM_02",
            },
            {
                "source_camera_id": "CAM_02",
                "target_camera_id": "CAM_03",
            },
        ]
    )

    output = propagate_congestion(
        congestion_data,
        transition_data,
    )

    print(output.to_string(index=False))