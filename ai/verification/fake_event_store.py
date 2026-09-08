"""
fake_event_store.py
--------------------
TEMPORARY STAND-IN for the real PostgreSQL `vehicle_events` table.

Why do this instead of connecting to a real database right away?
Because right now we want to focus on getting the SEARCH LOGIC correct
(evidence.py) without also debugging database connections at the same
time. Once the logic works and is tested, swapping this list for a
real SQL query is a small, mechanical change -- the function names
and what they return will stay the same.

This is a normal, professional way to build software: get the logic
right against fake data first, then plug in the real data source.
"""

# A small list of sample vehicle events, mimicking what would normally
# come from the shared `vehicle_events` database table.
SAMPLE_EVENTS = [
    {"event_id": "EVT_A1", "camera_id": "C13", "plate": "DL01AB1234",
     "timestamp": "2026-09-06T15:28:00", "ocr_confidence": 0.95},

    {"event_id": "EVT_A2", "camera_id": "C14", "plate": "DL01AB1284",  # <- the wrong one
     "timestamp": "2026-09-06T15:30:00", "ocr_confidence": 0.61},

    {"event_id": "EVT_A3", "camera_id": "C15", "plate": "DL01AB1234",
     "timestamp": "2026-09-06T15:32:00", "ocr_confidence": 0.93},

    # A totally unrelated vehicle, just to make sure our search
    # doesn't accidentally pull in events that have nothing to do
    # with the vehicle we're checking.
    {"event_id": "EVT_B1", "camera_id": "C14", "plate": "MH12XY5678",
     "timestamp": "2026-09-06T15:29:00", "ocr_confidence": 0.98},
]


def get_all_events() -> list[dict]:
    """
    Stand-in for: SELECT * FROM vehicle_events;

    Later, this becomes a real database query. Everything that calls
    this function doesn't need to know or care about that change.
    """
    return SAMPLE_EVENTS
