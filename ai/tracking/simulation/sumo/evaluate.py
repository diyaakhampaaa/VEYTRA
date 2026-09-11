"""Evaluate Member 3 reconstruction against SUMO hidden ground truth.

Only this module reads ground_truth.json. The matching/reconstruction stages
consume public observations only.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ai.tracking.matcher import CrossCameraMatcher
from ai.tracking.reconstruct import reconstruct

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
OBSERVATIONS_FILE = OUTPUT_DIR / "camera_observations.json"
TRACKS_FILE = OUTPUT_DIR / "prepared_tracks.json"
GROUND_TRUTH_FILE = OUTPUT_DIR / "ground_truth.json"


def _load(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _event_gt_map(gt: dict[str, Any]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for vehicle_id, vehicle in gt.get("vehicles", {}).items():
        for event in vehicle.get("events", []):
            event_id = event.get("event_id")
            if event_id is not None:
                mapping[str(event_id)] = str(vehicle_id)
    return mapping


def _track_gt_ids(track: dict[str, Any], event_to_vehicle: dict[str, str]) -> set[str]:
    ids = set()
    for event_id in track.get("event_ids", []):
        vehicle = event_to_vehicle.get(str(event_id))
        if vehicle is not None:
            ids.add(vehicle)
    return ids


def _track_key(track: dict[str, Any]) -> tuple[str, str]:
    return str(track.get("camera_id")), str(track.get("local_track_id"))


def calculate_metrics(
    reconstruction: dict[str, Any],
    ground_truth: dict[str, Any],
) -> dict[str, float | int]:
    """Calculate real metrics from reconstructed tracks and hidden GT."""
    event_to_vehicle = _event_gt_map(ground_truth)
    gt_vehicles = ground_truth.get("vehicles", {})
    trajectories = reconstruction.get("trajectories", [])

    # Ground-truth identity of every predicted local track is derived only
    # from public event IDs matched against hidden GT here in evaluation.
    predicted_tracks: list[dict[str, Any]] = []
    for trajectory in trajectories:
        for obs in trajectory.get("observations", []):
            predicted_tracks.append(obs)

    # Vehicle matching accuracy: among GT vehicles visible at >=2 cameras,
    # how many have all their observed local tracks assigned to one predicted
    # vehicle identity? This rewards true cross-camera grouping.
    eligible_gt = {
        str(vid): tuple(vehicle.get("camera_sequence", []))
        for vid, vehicle in gt_vehicles.items()
        if len(vehicle.get("camera_sequence", [])) >= 2
    }
    gt_to_pred: dict[str, set[str]] = {vid: set() for vid in eligible_gt}
    for obs in predicted_tracks:
        ids = _track_gt_ids(obs, event_to_vehicle)
        pred = str(obs.get("vehicle_id"))
        for gt_id in ids:
            if gt_id in gt_to_pred:
                gt_to_pred[gt_id].add(pred)
    correct_vehicle_groups = sum(len(preds) == 1 for preds in gt_to_pred.values())
    vehicle_matching_accuracy = (
        correct_vehicle_groups / len(eligible_gt) if eligible_gt else 0.0
    )

    # Cross-camera association accuracy: accepted edges that connect two
    # tracks belonging to the same hidden vehicle.
    accepted_pairs = 0
    correct_pairs = 0
    for trajectory in trajectories:
        obs = trajectory.get("observations", [])
        for a, b in zip(obs, obs[1:]):
            a_ids = _track_gt_ids(a, event_to_vehicle)
            b_ids = _track_gt_ids(b, event_to_vehicle)
            if not a_ids or not b_ids:
                continue
            accepted_pairs += 1
            if a_ids & b_ids:
                correct_pairs += 1
    association_accuracy = correct_pairs / accepted_pairs if accepted_pairs else 0.0

    # Camera transition accuracy: compare each predicted adjacent camera pair
    # with the ordered GT camera transitions for the underlying vehicle.
    transition_total = 0
    transition_correct = 0
    for trajectory in trajectories:
        cameras = trajectory.get("camera_sequence", [])
        if len(cameras) < 2:
            continue
        underlying = set()
        for obs in trajectory.get("observations", []):
            underlying.update(_track_gt_ids(obs, event_to_vehicle))
        if len(underlying) != 1:
            continue
        gt_id = next(iter(underlying))
        gt_seq = gt_vehicles.get(gt_id, {}).get("camera_sequence", [])
        gt_pairs = set(zip(gt_seq, gt_seq[1:]))
        for pair in zip(cameras, cameras[1:]):
            transition_total += 1
            if tuple(pair) in gt_pairs:
                transition_correct += 1
    camera_transition_accuracy = (
        transition_correct / transition_total if transition_total else 0.0
    )

    # Exact trajectory accuracy for eligible GT vehicles: a reconstructed
    # trajectory must contain exactly the GT camera sequence.
    exact = 0
    gt_seen: set[str] = set()
    for trajectory in trajectories:
        underlying = set()
        for obs in trajectory.get("observations", []):
            underlying.update(_track_gt_ids(obs, event_to_vehicle))
        if len(underlying) != 1:
            continue
        gt_id = next(iter(underlying))
        if gt_id not in eligible_gt or gt_id in gt_seen:
            continue
        gt_seen.add(gt_id)
        if list(trajectory.get("camera_sequence", [])) == list(eligible_gt[gt_id]):
            exact += 1
    trajectory_accuracy = exact / len(eligible_gt) if eligible_gt else 0.0

    return {
        "vehicle_matching_accuracy": round(vehicle_matching_accuracy, 4),
        "correct_cross_camera_association_percent": round(association_accuracy * 100.0, 2),
        "camera_transition_accuracy": round(camera_transition_accuracy, 4),
        "trajectory_reconstruction_accuracy": round(trajectory_accuracy, 4),
        "gt_vehicles_with_multiple_cameras": len(eligible_gt),
        "accepted_cross_camera_associations_evaluated": accepted_pairs,
        "predicted_trajectories": len(trajectories),
    }


def run_evaluation() -> tuple[dict[str, Any], dict[str, Any]]:
    public = _load(OBSERVATIONS_FILE)
    prepared = _load(TRACKS_FILE)
    hidden = _load(GROUND_TRUTH_FILE)

    # Hidden GT is intentionally loaded only in this evaluator, after public
    # matching data has been prepared.
    matcher = CrossCameraMatcher()
    match_result = matcher.match(prepared.get("tracks", []))
    reconstruction = reconstruct(match_result)
    metrics = calculate_metrics(reconstruction, hidden)

    result = {"metrics": metrics, "reconstruction": reconstruction}
    return result, {"public_observation_count": len(public.get("observations", []))}


def main() -> None:
    result, meta = run_evaluation()
    print("=== VEYTRA MEMBER 3 EVALUATION ===")
    print("Public observations:", meta["public_observation_count"])
    for key, value in result["metrics"].items():
        print(f"{key}: {value}")
    out = OUTPUT_DIR / "evaluation.json"
    with out.open("w", encoding="utf-8") as file:
        json.dump(result, file, indent=2)
    print("Evaluation output:", out)


if __name__ == "__main__":
    main()
