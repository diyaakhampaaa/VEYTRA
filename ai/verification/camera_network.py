"""
camera_network.py
------------------
PLACEHOLDER DATA -- this is a small, made-up camera network so we can
build and test evidence.py right now, without waiting for Member 3's
real camera-transition graph.

Once Member 3's real graph exists, we just swap out CAMERA_CONNECTIONS
below with real data pulled from their PostGIS database -- the rest of
evidence.py won't need to change at all. That's the whole point of
building it this way.

Think of this like a simple map: 5 cameras along a road, each one knows
which other cameras are its neighbours, and roughly how long it takes
a car to drive between them.
"""

# Each entry: "camera_id": { "neighbour_camera_id": expected_travel_time_seconds }
#
# Example: from C14, a car could reach C13 in about 90 seconds,
# or C15 in about 120 seconds, under NORMAL driving conditions.
CAMERA_CONNECTIONS = {
    "C13": {"C14": 90},
    "C14": {"C13": 90, "C15": 120},
    "C15": {"C14": 120, "C16": 100},
    "C16": {"C15": 100, "C18": 200},
    "C18": {"C16": 200},
}

# We allow some flexibility around the expected time, because real
# traffic isn't perfectly consistent (a car might go a bit faster or
# slower than "expected"). This is a tolerance window, in seconds.
TRAVEL_TIME_TOLERANCE_SECONDS = 60


def get_neighbour_cameras(camera_id: str) -> dict:
    """
    Given a camera, return its neighbours and expected travel times.

    Example: get_neighbour_cameras("C14") -> {"C13": 90, "C15": 120}

    Returns an empty dict if the camera isn't in our network at all
    (this should never crash -- just means "no known neighbours").
    """
    return CAMERA_CONNECTIONS.get(camera_id, {})
