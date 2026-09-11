from fastapi import APIRouter

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/")
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