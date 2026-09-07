import pandas as pd

from analytics.od_matrix import build_trajectories, compute_od_matrix


def sample_events():
    return pd.DataFrame(
        [
            {
                "event_id": "E1",
                "vehicle_id": "V1",
                "trajectory_id": "T1",
                "camera_id": "CAM_01",
                "road_segment_id": "SEG_A",
                "timestamp": "2026-09-06T08:00:00+05:30",
            },
            {
                "event_id": "E2",
                "vehicle_id": "V1",
                "trajectory_id": "T1",
                "camera_id": "CAM_02",
                "road_segment_id": "SEG_B",
                "timestamp": "2026-09-06T08:10:00+05:30",
            },
            {
                "event_id": "E3",
                "vehicle_id": "V2",
                "trajectory_id": "T2",
                "camera_id": "CAM_01",
                "road_segment_id": "SEG_A",
                "timestamp": "2026-09-06T08:05:00+05:30",
            },
            {
                "event_id": "E4",
                "vehicle_id": "V2",
                "trajectory_id": "T2",
                "camera_id": "CAM_03",
                "road_segment_id": "SEG_C",
                "timestamp": "2026-09-06T08:15:00+05:30",
            },
        ]
    )


def test_build_trajectories():
    result = build_trajectories(sample_events())

    assert len(result) == 2

    first = result.iloc[0]

    assert first["origin_camera_id"] == "CAM_01"
    assert first["destination_camera_id"] == "CAM_02"
    assert first["origin_segment_id"] == "SEG_A"
    assert first["destination_segment_id"] == "SEG_B"


def test_od_matrix_counts_vehicle_journeys():
    result = compute_od_matrix(sample_events())

    matrix = result["od_matrix"]

    assert len(matrix) == 2
    assert matrix["vehicle_count"].sum() == 2


def test_od_matrix_groups_same_origin_destination():
    events = pd.concat(
        [
            sample_events(),
            pd.DataFrame(
                [
                    {
                        "event_id": "E5",
                        "vehicle_id": "V3",
                        "trajectory_id": "T3",
                        "camera_id": "CAM_01",
                        "road_segment_id": "SEG_A",
                        "timestamp": "2026-09-06T08:20:00+05:30",
                    },
                    {
                        "event_id": "E6",
                        "vehicle_id": "V3",
                        "trajectory_id": "T3",
                        "camera_id": "CAM_02",
                        "road_segment_id": "SEG_B",
                        "timestamp": "2026-09-06T08:30:00+05:30",
                    },
                ]
            ),
        ],
        ignore_index=True,
    )

    result = compute_od_matrix(events)
    matrix = result["od_matrix"]

    row = matrix[
        (matrix["origin_camera_id"] == "CAM_01")
        & (matrix["destination_camera_id"] == "CAM_02")
    ].iloc[0]

    assert row["vehicle_count"] == 2


def test_same_location_can_be_excluded():
    events = pd.DataFrame(
        [
            {
                "vehicle_id": "V1",
                "trajectory_id": "T1",
                "camera_id": "CAM_01",
                "road_segment_id": "SEG_A",
                "timestamp": "2026-09-06T08:00:00+05:30",
            },
            {
                "vehicle_id": "V1",
                "trajectory_id": "T1",
                "camera_id": "CAM_01",
                "road_segment_id": "SEG_A",
                "timestamp": "2026-09-06T08:05:00+05:30",
            },
        ]
    )

    result = compute_od_matrix(events)

    assert result["od_matrix"].empty


def test_empty_events():
    result = compute_od_matrix(pd.DataFrame())

    assert result["by_trajectory"].empty
    assert result["od_matrix"].empty