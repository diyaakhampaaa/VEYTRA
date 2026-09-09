from __future__ import annotations

import json
from pathlib import Path
from typing import Any


OUTPUT_DIR = Path(__file__).resolve().parent / "output"


LAYER_FILES = {
    "cameras": "cameras.geojson",
    "trajectories": "trajectories.geojson",
    "congestion": "congestion.geojson",
    "bottlenecks": "bottlenecks.geojson",
    "density": "density.geojson",
    "od_flows": "od_flows.geojson",
    "roads": "roads.geojson",
}


def list_layers() -> list[str]:
    """
    Return the names of available GIS layers.
    """
    return [
        layer_name
        for layer_name, filename in LAYER_FILES.items()
        if (OUTPUT_DIR / filename).exists()
    ]


def get_layer(layer_name: str) -> dict[str, Any]:
    """
    Load one GeoJSON layer by name.
    """
    if layer_name not in LAYER_FILES:
        raise ValueError(
            f"Unknown layer '{layer_name}'. "
            f"Available layers: {list(LAYER_FILES)}"
        )

    layer_path = OUTPUT_DIR / LAYER_FILES[layer_name]

    if not layer_path.exists():
        raise FileNotFoundError(
            f"Layer '{layer_name}' has not been generated yet: {layer_path}"
        )

    with layer_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_all_layers() -> dict[str, dict[str, Any]]:
    """
    Load all currently available GIS layers.
    """
    return {
        layer_name: get_layer(layer_name)
        for layer_name in list_layers()
    }


if __name__ == "__main__":
    print("Available layers:")
    print(list_layers())