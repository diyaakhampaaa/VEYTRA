"""
evidence.py
-----------
Job: Given ONE suspicious event, find other events from NEARBY,
CONNECTED cameras that plausibly saw the same vehicle around the
same time.

This is the "detective going and asking neighbours" step, right
after suspicion.py's "something feels off" step.
"""

from datetime import datetime
from .camera_network import get_neighbour_cameras, TRAVEL_TIME_TOLERANCE_SECONDS
from .fake_event_store import get_all_events


def _seconds_between(time_a: str, time_b: str) -> float:
    """
    Small helper: how many seconds apart are two timestamps?

    Timestamps come in as text (ISO format, e.g. "2026-09-06T15:30:00"),
    so we convert them into actual datetime objects Python can do
    math on, then subtract.
    """
    dt_a = datetime.fromisoformat(time_a)
    dt_b = datetime.fromisoformat(time_b)
    return abs((dt_b - dt_a).total_seconds())


def find_supporting_evidence(event: dict) -> list[dict]:
    """
    MAIN FUNCTION of this file.

    Input: the suspicious event, e.g.
        {
            "event_id": "EVT_A2",
            "camera_id": "C14",
            "timestamp": "2026-09-06T15:30:00",
            ...
        }

    Output: a list of OTHER events that:
      1. come from a camera that's a known neighbour of this one, AND
      2. happened within a physically plausible time window

    This is where the "spatial-temporal filtering" idea from the
    CVPR paper comes in -- we don't compare against EVERY event ever
    recorded, only the ones that could realistically be the same car.
    """
    camera_id = event.get("camera_id")
    timestamp = event.get("timestamp")

    if not camera_id or not timestamp:
        # Can't search without knowing where/when this event happened
        return []

    neighbours = get_neighbour_cameras(camera_id)
    if not neighbours:
        # This camera has no known neighbours in our network -- nothing to check
        return []

    supporting_events = []

    for candidate_event in get_all_events():
        candidate_camera = candidate_event.get("camera_id")

        # Skip events from the same camera (we want OTHER cameras, not itself)
        if candidate_camera == camera_id:
            continue

        # Is this candidate's camera actually a neighbour of ours?
        if candidate_camera not in neighbours:
            continue

        expected_travel_seconds = neighbours[candidate_camera]
        actual_gap_seconds = _seconds_between(timestamp, candidate_event["timestamp"])

        # Is the actual time gap close to what we'd expect for this route,
        # allowing some wiggle room for normal traffic variation?
        lower_bound = 0
        upper_bound = expected_travel_seconds + TRAVEL_TIME_TOLERANCE_SECONDS

        if lower_bound <= actual_gap_seconds <= upper_bound:
            supporting_events.append(candidate_event)

    return supporting_events
