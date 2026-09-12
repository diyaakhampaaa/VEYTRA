"""Run the complete Member 3 SUMO -> MATCH -> RECONSTRUCT demo."""
from __future__ import annotations

from ai.tracking.simulation.sumo.evaluate import run_evaluation
from ai.tracking.simulation.sumo.prepare_tracks import main as prepare_main
from ai.tracking.simulation.sumo.run_simulation import run_simulation


def main() -> None:
    run_simulation()
    prepare_main()
    result, meta = run_evaluation()
    print("\n=== COMPLETE MEMBER 3 DEMO ===")
    print("Public observations:", meta["public_observation_count"])
    print("Metrics:")
    for key, value in result["metrics"].items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
