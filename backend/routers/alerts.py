from fastapi import APIRouter
from backend.database import SessionLocal
from backend.models import Vehicle, Camera, VehicleCameraEvent

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/")
def get_alerts():

    db = SessionLocal()
    alerts = []

    try:
        # =========================================================
        # 1. VEHICLE VERIFICATION ALERTS
        # =========================================================

        vehicles = db.query(Vehicle).all()

        for vehicle in vehicles:

            # Ignore vehicles where verification data is not available
            if (
                vehicle.reid_similarity is None
                and vehicle.plate_similarity is None
            ):
                continue

            # Use whichever similarity values are available
            scores = []

            if vehicle.reid_similarity is not None:
                scores.append(vehicle.reid_similarity)

            if vehicle.plate_similarity is not None:
                scores.append(vehicle.plate_similarity)

            verification_score = min(scores)

            # Low similarity = possible verification issue
            if verification_score < 0.80:

                # -------------------------------------------------
                # Get real camera evidence for this vehicle
                # -------------------------------------------------

                events = (
                    db.query(VehicleCameraEvent)
                    .filter(
                        VehicleCameraEvent.vehicle_id == vehicle.vehicle_id,
                        VehicleCameraEvent.frame_path.isnot(None)
                    )
                    .order_by(VehicleCameraEvent.id)
                    .all()
                )

                evidence = [
                    {
                        "camera_id": event.camera_id,
                        "frame_path": event.frame_path,
                        "timestamp": event.timestamp
                    }
                    for event in events
                ]

                alerts.append({
                    "alert_id": f"VERIFY_{vehicle.vehicle_id}",
                    "type": "Vehicle Verification",
                    "severity": (
                        "High"
                        if verification_score < 0.65
                        else "Medium"
                    ),
                    "camera_id": "NETWORK",
                    "vehicle_id": vehicle.vehicle_id,
                    "plate": vehicle.plate,
                    "message": (
                        f"Vehicle {vehicle.plate} requires "
                        f"cross-camera verification."
                    ),
                    "verification_score": round(
                        verification_score,
                        2
                    ),
                    "source": vehicle.source,
                    "status": "Active",
                    "evidence": evidence
                })


        # =========================================================
        # 2. TRAFFIC CONGESTION ALERTS
        # =========================================================

        cameras = db.query(Camera).all()

        if cameras:

            vehicle_counts = [
                camera.vehicles_detected
                for camera in cameras
                if camera.vehicles_detected is not None
            ]

            if vehicle_counts:

                average_count = (
                    sum(vehicle_counts) /
                    len(vehicle_counts)
                )

                # Congestion threshold:
                # 1.25 × current network average
                congestion_threshold = (
                    average_count * 1.25
                )

                for camera in cameras:

                    count = camera.vehicles_detected or 0

                    if count >= congestion_threshold:

                        congestion_score = min(
                            count / (average_count * 2),
                            1.0
                        )

                        alerts.append({
                            "alert_id": (
                                f"TRAFFIC_{camera.camera_id}"
                            ),
                            "type": "Traffic Congestion",
                            "severity": (
                                "High"
                                if count >= average_count * 1.5
                                else "Medium"
                            ),
                            "camera_id": camera.camera_id,
                            "message": (
                                f"Elevated traffic detected at "
                                f"{camera.camera_id}."
                            ),
                            "vehicle_count": count,
                            "congestion_score": round(
                                congestion_score,
                                2
                            ),
                            "location": camera.location,
                            "source": camera.source,
                            "status": "Active"
                        })


        # =========================================================
        # 3. NORMAL TRAFFIC MONITORING
        # =========================================================

        if not alerts and cameras:

            # If there are no abnormal events,
            # show one real monitoring status.
            busiest_camera = max(
                cameras,
                key=lambda camera:
                camera.vehicles_detected or 0
            )

            alerts.append({
                "alert_id": (
                    f"FLOW_{busiest_camera.camera_id}"
                ),
                "type": "Traffic Flow",
                "severity": "Low",
                "camera_id": busiest_camera.camera_id,
                "message": (
                    "Traffic flow is currently within "
                    "normal monitored levels."
                ),
                "vehicle_count": (
                    busiest_camera.vehicles_detected
                ),
                "location": busiest_camera.location,
                "source": busiest_camera.source,
                "status": "Monitoring"
            })


        # =========================================================
        # RETURN ALERTS
        # =========================================================

        return {
            "alerts": alerts,
            "total": len(alerts),
            "source": "database"
        }

    finally:
        db.close()