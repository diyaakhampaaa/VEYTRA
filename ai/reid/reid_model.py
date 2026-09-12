"""FastReID + VeRi-776 adapter with a dependency-safe interface.

The wrapper does not bundle proprietary/model-weight files. Point it at a
FastReID config and checkpoint when those are available. Core VEYTRA tests
remain runnable without torch/FastReID installed.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any


def cosine_similarity(a: list[float], b: list[float]) -> float | None:
    if not isinstance(a, (list, tuple)) or not isinstance(b, (list, tuple)) or len(a) != len(b) or not a:
        return None
    try:
        aa = [float(x) for x in a]
        bb = [float(x) for x in b]
    except (TypeError, ValueError):
        return None
    na = math.sqrt(sum(x * x for x in aa))
    nb = math.sqrt(sum(x * x for x in bb))
    if na <= 0 or nb <= 0:
        return None
    return max(0.0, min(1.0, sum(x * y for x, y in zip(aa, bb)) / (na * nb)))


class FastReIDModel:
    """Lazy FastReID inference wrapper.

    Parameters are explicit so the same interface can be used with a
    VeRi-776-trained checkpoint in the real pipeline.
    """

    def __init__(self, config_path: str | Path | None = None, weights_path: str | Path | None = None, device: str = "cpu") -> None:
        self.config_path = Path(config_path) if config_path else None
        self.weights_path = Path(weights_path) if weights_path else None
        self.device = device
        self._predictor: Any = None
        self._loaded = False

    @property
    def available(self) -> bool:
        return self.config_path is not None and self.weights_path is not None and self.config_path.exists() and self.weights_path.exists()

    def load(self) -> None:
        if not self.available:
            raise FileNotFoundError("FastReID config/VeRi-776 weights were not provided or do not exist")
        try:
            from fastreid.config import get_cfg
            from fastreid.engine import DefaultPredictor
        except ImportError as exc:
            raise RuntimeError("FastReID is not installed. Install the optional Re-ID dependencies.") from exc

        cfg = get_cfg()
        cfg.merge_from_file(str(self.config_path))
        cfg.MODEL.WEIGHTS = str(self.weights_path)
        cfg.MODEL.DEVICE = self.device
        self._predictor = DefaultPredictor(cfg)
        self._loaded = True

    def embed(self, vehicle_crop: Any) -> list[float] | None:
        """Return a FastReID embedding for one BGR/RGB crop.

        The exact predictor output varies by FastReID configuration, so this
        adapter accepts tensor/array-like outputs and converts them to a list.
        """
        if not self._loaded:
            self.load()
        if self._predictor is None:
            return None
        output = self._predictor(vehicle_crop)
        if hasattr(output, "detach"):
            output = output.detach().cpu().numpy()
        if hasattr(output, "reshape"):
            output = output.reshape(-1)
        try:
            values = [float(x) for x in output]
        except (TypeError, ValueError):
            return None
        norm = math.sqrt(sum(x * x for x in values))
        return [x / norm for x in values] if norm > 0 else None
