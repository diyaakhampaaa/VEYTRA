from fastapi import APIRouter

router = APIRouter(
    prefix="/simulation",
    tags=["Simulation"]
)


@router.get("/comparison")
def get_simulation_comparison():

    return {
        "simulation": {
            "scenario_id": "SUMO_DELHI_001",
            "source": "simulated",
            "vehicles": 138,
            "average_speed": 35.4,
            "congestion_score": 0.40
        },
        "ground_truth": {
            "vehicles": 142,
            "average_speed": 34.8,
            "congestion_score": 0.43
        },
        "comparison": {
            "vehicle_count_difference": -4,
            "vehicle_count_accuracy": 0.97,
            "speed_difference": 0.6,
            "speed_accuracy": 0.98,
            "congestion_difference": -0.03,
            "overall_accuracy": 0.97
        }
    }