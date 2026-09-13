"""Schema helpers for SUMO hidden ground truth.

This module intentionally does not load the hidden file. ``evaluate.py`` is
 the sole runtime reader of ``ground_truth.json`` so inference cannot consume
truth labels by accident.
"""
from __future__ import annotations

from typing import Any


def validate_ground_truth(data: Any) -> bool:
    if not isinstance(data, dict) or not isinstance(data.get("vehicles"), dict):
        return False
    for vehicle_id, vehicle in data["vehicles"].items():
        if not isinstance(vehicle_id, str) or not isinstance(vehicle, dict):
            return False
        if not isinstance(vehicle.get("camera_sequence"), list):
            return False
        if not isinstance(vehicle.get("events"), list):
            return False
    return True
