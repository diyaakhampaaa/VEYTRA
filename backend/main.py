from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.tracking import router as tracking_router
from backend.routers.ocr import router as ocr_router
from backend.routers.detection import router as detection_router
from backend.routers.verification import router as verification_router
from backend.routers.analytics import router as analytics_router

app = FastAPI(title="VEYTRA API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(detection_router)
app.include_router(ocr_router)
app.include_router(tracking_router)
app.include_router(verification_router)
app.include_router(analytics_router)


@app.get("/")
def root():
    return {"message": "VEYTRA API is running"}


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "VEYTRA backend"
    }
@app.get("/cameras")
def get_cameras():
    return {
        "cameras": [
            {
                "camera_id": "CAM_01",
                "status": "Active",
                "vehicles_detected": 12,
                "source": "simulated"
            },
            {
                "camera_id": "CAM_02",
                "status": "Active",
                "vehicles_detected": 8,
                "source": "simulated"
            },
            {
                "camera_id": "CAM_03",
                "status": "Active",
                "vehicles_detected": 15,
                "source": "simulated"
            }
        ]
    }
@app.get("/vehicles/search")
def search_vehicle(plate: str):
    vehicles = {
        "DL01AB1234": {
            "plate": "DL01AB1234",
            "vehicle_id": "VEH_001",
            "camera_sequence": ["CAM_01", "CAM_02", "CAM_03"],
            "start_time": "18:42:10",
            "end_time": "18:49:32",
            "match_score": {
                "reid_similarity": 0.94,
                "plate_similarity": 0.98,
                "temporal_score": 0.91,
                "route_score": 0.89
            },
            "source": "simulated"
        }
    }

    vehicle = vehicles.get(plate.upper())

    if not vehicle:
        return {
            "found": False,
            "vehicle": None
        }

    return {
        "found": True,
        "vehicle": vehicle
    }
@app.get("/verification/events")
def get_verification_events():
    return {
        "events": [
            {
                "event_id": "EVT_001",
                "original_plate": "DL01AB1284",
                "corrected_plate": "DL01AB1234",
                "supporting_cameras": ["CAM_01", "CAM_02", "CAM_03"],
                "reid_similarity": 0.94,
                "verification_confidence": 0.97,
                "reason": "Plate mismatch corrected using cross-camera vehicle appearance and trajectory."
            },
            {
                "event_id": "EVT_002",
                "original_plate": "DL02XY781",
                "corrected_plate": "DL02XY0781",
                "supporting_cameras": ["CAM_02", "CAM_03"],
                "reid_similarity": 0.89,
                "verification_confidence": 0.91,
                "reason": "OCR ambiguity resolved using supporting camera observations."
            }
        ]
    }
@app.get("/analytics/overview")
def get_analytics():
    return {
        "segments": [
            {
                "segment_id": "SEG_01",
                "vehicle_count": 42,
                "average_speed": 38.5,
                "congestion_score": 0.32,
                "timestamp": "18:50:00"
            },
            {
                "segment_id": "SEG_02",
                "vehicle_count": 67,
                "average_speed": 21.4,
                "congestion_score": 0.71,
                "timestamp": "18:50:00"
            },
            {
                "segment_id": "SEG_03",
                "vehicle_count": 29,
                "average_speed": 46.2,
                "congestion_score": 0.18,
                "timestamp": "18:50:00"
            }
        ]
    }
@app.get("/alerts")
def get_alerts():
    return {
        "alerts": [
            {
                "alert_id": "ALT_001",
                "type": "Traffic Congestion",
                "severity": "High",
                "camera_id": "CAM_02",
                "message": "Heavy congestion detected on monitored road segment.",
                "vehicle_count": 67,
                "congestion_score": 0.71,
                "timestamp": "18:50:00",
                "source": "simulated",
                "status": "Active"
            },
            {
                "alert_id": "ALT_002",
                "type": "Vehicle Verification",
                "severity": "Medium",
                "camera_id": "CAM_01",
                "message": "Vehicle identity required cross-camera verification.",
                "vehicle_count": 1,
                "congestion_score": 0.12,
                "timestamp": "18:48:32",
                "source": "simulated",
                "status": "Active"
            },
            {
                "alert_id": "ALT_003",
                "type": "Traffic Flow",
                "severity": "Low",
                "camera_id": "CAM_03",
                "message": "Traffic flow is within normal operating conditions.",
                "vehicle_count": 29,
                "congestion_score": 0.18,
                "timestamp": "18:47:10",
                "source": "simulated",
                "status": "Monitoring"
            }
        ]
    }
@app.get("/simulation/comparison")
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