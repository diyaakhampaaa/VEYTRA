from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import traci


BASE_DIR = Path(__file__).resolve().parent

CONFIG_FILE = BASE_DIR / "scenario.sumocfg"
OUTPUT_DIR = BASE_DIR / "outputs"

OBSERVATIONS_FILE = OUTPUT_DIR / "camera_observations.json"
GROUND_TRUTH_FILE = OUTPUT_DIR / "ground_truth.json"

SUMO_BINARY = r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe"


CAMERAS = {
    "C01": {"node": "C01", "latitude": 28.6100, "longitude": 77.2000},
    "C02": {"node": "C02", "latitude": 28.6200, "longitude": 77.2100},
    "C03": {"node": "C03", "latitude": 28.6150, "longitude": 77.2050},
    "C04": {"node": "C04", "latitude": 28.6100, "longitude": 77.2150},
    "C05": {"node": "C05", "latitude": 28.6050, "longitude": 77.2050},
}


CAMERA_EDGES = {
    "C01": {"C01_C03", "C03_C01"},
    "C02": {"C02_C03", "C03_C02"},
    "C03": {
        "C01_C03",
        "C03_C01",
        "C02_C03",
        "C03_C02",
        "C03_C04",
        "C04_C03",
        "C03_C05",
        "C05_C03",
    },
    "C04": {"C03_C04", "C04_C03"},
    "C05": {"C03_C05", "C05_C03"},
}


# A camera observes a vehicle only when it is physically
# close to the camera node.
CAMERA_ZONE_RADIUS = 50.0  # meters


RANDOM_SEED = 42
DROP_RATE = 0.10


def simulation_timestamp(step: float) -> str:
    base = datetime(2026, 9, 6, 15, 30, tzinfo=timezone.utc)
    return (base + timedelta(seconds=step)).isoformat()


def vehicle_type(vehicle_id: str) -> str:
    try:
        vtype = traci.vehicle.getTypeID(vehicle_id)
    except traci.TraCIException:
        return "unknown"

    return "Two-wheeler" if vtype == "bike" else "Car"


def direction_from_edge(edge_id: str) -> str:
    directions = {
        "C01_C03": "E",
        "C03_C01": "W",
        "C03_C04": "E",
        "C04_C03": "W",
        "C03_C02": "N",
        "C02_C03": "S",
        "C03_C05": "S",
        "C05_C03": "N",
    }

    return directions.get(edge_id, "UNKNOWN")


def plate_for_vehicle(vehicle_id: str) -> str:
    number = int(vehicle_id.replace("V", ""))
    return f"DL01AB{number:04d}"


def camera_for_edge(edge_id: str) -> str | None:
    for camera_id, edges in CAMERA_EDGES.items():
        if edge_id in edges:
            return camera_id

    return None


def camera_observation(vehicle_id: str) -> str | None:
    """
    Return the camera whose physical node is close to the vehicle.

    A camera observes a vehicle only when the vehicle is within
    CAMERA_ZONE_RADIUS meters of that camera node.
    """
    try:
        position = traci.vehicle.getPosition(vehicle_id)
    except traci.TraCIException:
        return None

    vehicle_x, vehicle_y = position

    closest_camera = None
    closest_distance = float("inf")

    for camera_id, camera in CAMERAS.items():
        try:
            node_x, node_y = traci.junction.getPosition(camera["node"])
        except traci.TraCIException:
            continue

        distance = (
            (vehicle_x - node_x) ** 2
            + (vehicle_y - node_y) ** 2
        ) ** 0.5

        if (
            distance <= CAMERA_ZONE_RADIUS
            and distance < closest_distance
        ):
            closest_distance = distance
            closest_camera = camera_id

    return closest_camera


def run_simulation() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if OBSERVATIONS_FILE.exists():
        OBSERVATIONS_FILE.unlink()

    if GROUND_TRUTH_FILE.exists():
        GROUND_TRUTH_FILE.unlink()

    random.seed(RANDOM_SEED)

    observations = []
    hidden_ground_truth = {}

    # Camera-local tracking state.
    # The same vehicle gets a different local_track_id
    # at different cameras.
    local_track_counters = {
        camera_id: 0 for camera_id in CAMERAS
    }

    local_track_map = {}

    traci.start(
        [
            SUMO_BINARY,
            "-c",
            str(CONFIG_FILE),
            "--seed",
            str(RANDOM_SEED),
        ]
    )

    try:
        step = 0.0

        while step <= 300:
            traci.simulationStep()

            for vehicle_id in traci.vehicle.getIDList():
                try:
                    edge_id = traci.vehicle.getRoadID(vehicle_id)

                    # IMPORTANT:
                    # Do not treat the entire road edge as a camera.
                    # The camera observes the vehicle only near its
                    # physical SUMO node.
                    camera_id = camera_observation(vehicle_id)

                    if camera_id is None:
                        continue

                    # -----------------------------------------------------
                    # Assign a camera-local track ID.
                    #
                    # This intentionally does NOT use the plate number
                    # or expose the hidden global vehicle identity.
                    #
                    # Example:
                    #   C01 -> local_track_id 3
                    #   C03 -> local_track_id 7
                    #
                    # The cross-camera matcher must later determine that
                    # these two local tracks belong to the same vehicle.
                    # -----------------------------------------------------

                    track_key = (camera_id, vehicle_id)

                    if track_key not in local_track_map:
                        local_track_counters[camera_id] += 1

                        local_track_map[track_key] = (
                            local_track_counters[camera_id]
                        )

                    local_track_id = local_track_map[track_key]

                    timestamp = simulation_timestamp(step)

                    position = traci.vehicle.getPosition(vehicle_id)

                    camera = CAMERAS[camera_id]

                    event_id = f"EVT{len(observations) + 1:06d}"

                    observation = {
                        "event_id": event_id,
                        "camera_id": camera_id,
                        "local_track_id": local_track_id,
                        "plate_number": plate_for_vehicle(vehicle_id),
                        "timestamp": timestamp,
                        "latitude": camera["latitude"],
                        "longitude": camera["longitude"],
                        "direction": direction_from_edge(edge_id),
                        "vehicle_type": vehicle_type(vehicle_id),
                        "ocr_confidence": 0.98,
                        "vehicle_confidence": 0.99,
                        "verification_status": "PENDING",
                        "source": "simulated",
                        "position_x": position[0],
                        "position_y": position[1],
                    }

                    observations.append(observation)

                    # -----------------------------------------------------
                    # Hidden ground truth.
                    #
                    # This remains completely separate from the public
                    # observation data and is used only by evaluation.
                    # -----------------------------------------------------

                    if vehicle_id not in hidden_ground_truth:
                        hidden_ground_truth[vehicle_id] = {
                            "vehicle_id": vehicle_id,
                            "route": traci.vehicle.getRouteID(vehicle_id),
                            "camera_sequence": [],
                            "events": [],
                        }

                    gt = hidden_ground_truth[vehicle_id]

                    if camera_id not in gt["camera_sequence"]:
                        gt["camera_sequence"].append(camera_id)

                    gt["events"].append(
                        {
                            "event_id": event_id,
                            "camera_id": camera_id,
                            "timestamp": timestamp,
                            "edge_id": edge_id,
                            "x": position[0],
                            "y": position[1],
                        }
                    )

                except traci.TraCIException:
                    continue

            step += 1.0

    finally:
        traci.close()

    # -------------------------------------------------------------
    # Shuffle public observations to simulate disconnected,
    # unordered camera observations.
    # -------------------------------------------------------------

    shuffled_observations = observations.copy()
    random.shuffle(shuffled_observations)

    # -------------------------------------------------------------
    # Drop a percentage of observations to simulate missing /
    # discontinuous camera observations.
    # -------------------------------------------------------------

    kept_observations = [
        obs
        for obs in shuffled_observations
        if random.random() > DROP_RATE
    ]

    # -------------------------------------------------------------
    # Public observations.
    # -------------------------------------------------------------

    with OBSERVATIONS_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            {
                "simulation": {
                    "seed": RANDOM_SEED,
                    "drop_rate": DROP_RATE,
                    "camera_count": len(CAMERAS),
                    "vehicle_count": 20,
                },
                "observations": kept_observations,
            },
            file,
            indent=2,
        )

    # -------------------------------------------------------------
    # Hidden ground truth.
    # -------------------------------------------------------------

    with GROUND_TRUTH_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            {
                "simulation_seed": RANDOM_SEED,
                "vehicles": hidden_ground_truth,
            },
            file,
            indent=2,
        )

    print("SUMO simulation completed successfully.")
    print("Vehicles configured:", 20)
    print("Camera nodes:", len(CAMERAS))
    print("Raw observations:", len(observations))
    print("Public observations after drop/shuffle:", len(kept_observations))
    print("Ground truth vehicles:", len(hidden_ground_truth))
    print("Observations:", OBSERVATIONS_FILE)
    print("Hidden GT:", GROUND_TRUTH_FILE)


if __name__ == "__main__":
    run_simulation()