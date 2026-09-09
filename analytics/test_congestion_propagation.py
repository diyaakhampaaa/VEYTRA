import pandas as pd

from analytics.congestion_propagation import propagate_congestion


def test_congestion_propagates_to_connected_camera():
    congestion = pd.DataFrame(
        [
            {
                "camera_id": "CAM_01",
                "timestamp": "2026-09-10 10:00:00",
                "congestion_score": 0.90,
            }
        ]
    )

    transitions = pd.DataFrame(
        [
            {
                "source_camera_id": "CAM_01",
                "target_camera_id": "CAM_02",
            }
        ]
    )

    result = propagate_congestion(congestion, transitions)

    assert len(result) == 1
    assert result.iloc[0]["source_camera_id"] == "CAM_01"
    assert result.iloc[0]["target_camera_id"] == "CAM_02"
    assert result.iloc[0]["propagated_score"] == 0.81


def test_congestion_does_not_propagate_from_low_congestion():
    congestion = pd.DataFrame(
        [
            {
                "camera_id": "CAM_01",
                "timestamp": "2026-09-10 10:00:00",
                "congestion_score": 0.30,
            }
        ]
    )

    transitions = pd.DataFrame(
        [
            {
                "source_camera_id": "CAM_01",
                "target_camera_id": "CAM_02",
            }
        ]
    )

    result = propagate_congestion(congestion, transitions)

    assert result.empty