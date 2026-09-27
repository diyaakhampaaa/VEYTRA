
import cv2
from ai.detection.detector import detect
from ai.ocr.ocr_engine import read_plate
from ai.tracking.integration import track_and_enrich_frame, match_tracked_frames
from ai.tracking.tracker import PerCameraTracker
from ai.tracking.reid import ReIDEmbedder
from backend.database import SessionLocal
from backend.services.trajectory_persistence import persist_trajectories

VIDEOS = {
    "C01": r"data\tracking_videos\C01.MOV",
    "C02": r"data\tracking_videos\C02.mov",
    "C03": r"data\tracking_videos\C03.mov",
}

TEST_SECONDS = 10
FRAME_STRIDE = 10

all_tracked_frames = []

for camera_id, video_path in VIDEOS.items():
    print(f"\n=== Processing {camera_id} ===")

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_limit = int(fps * TEST_SECONDS)
    tracker = PerCameraTracker()
    embedder = ReIDEmbedder()

    processed = 0
    source_frame_index = 0

    while source_frame_index < frame_limit:
        ok, frame = cap.read()

        if not ok:
            break

        if source_frame_index % FRAME_STRIDE != 0:
            source_frame_index += 1
            continue

        timestamp = f"2026-09-27T00:00:{source_frame_index / fps:09.6f}"

        result = detect(
            frame=frame,
            camera_id=camera_id,
            timestamp=timestamp,
            source="real",
        )

        for detection in result.get("detections", []):
            plate_bbox = detection.get("plate_bbox")

            if not plate_bbox:
                detection["plate"] = None
                detection["ocr_confidence"] = 0.0
                detection["alternatives"] = []
                continue

            try:
                x1, y1, x2, y2 = map(int, plate_bbox)
                h, w = frame.shape[:2]

                x1 = max(0, min(x1, w))
                x2 = max(0, min(x2, w))
                y1 = max(0, min(y1, h))
                y2 = max(0, min(y2, h))

                plate_crop = frame[y1:y2, x1:x2]

                if plate_crop.size == 0:
                    raise ValueError("Plate crop is empty")

                ocr_result = read_plate(plate_crop)
                cv2.imwrite(f"data\\debug_plate_{camera_id}_{source_frame_index}.jpg", plate_crop)
                print(f"OCR {camera_id}: {ocr_result}")

                detection["plate"] = ocr_result.get("plate")
                detection["ocr_confidence"] = ocr_result.get("confidence", 0.0)
                detection["alternatives"] = ocr_result.get("alternatives", [])

            except Exception:
                detection["plate"] = None
                detection["ocr_confidence"] = 0.0
                detection["alternatives"] = []

        tracked = track_and_enrich_frame(
            detection_result=result,
            frame=frame,
            tracker=tracker,
            embedder=embedder,
        )

        all_tracked_frames.append(tracked)
        processed += 1
        source_frame_index += 1

    cap.release()

    camera_frames = [
        r for r in all_tracked_frames
        if r.get("camera_id") == camera_id
    ]

    camera_detections = sum(
        len(r.get("detections", []))
        for r in camera_frames
    )

    print(f"Frames processed: {processed}")
    print(f"Total detections: {camera_detections}")

print("\n=== CROSS-CAMERA MATCHING ===")

match_result = match_tracked_frames(all_tracked_frames)

trajectories = match_result.get("trajectories", [])
print(f"Total trajectories: {len(trajectories)}")
for trajectory in trajectories:
    print(
        trajectory.get("vehicle_id"),
        repr(trajectory.get("plate")),
        repr(trajectory.get("ocr_confidence")),
    )


db = SessionLocal()
try:
    persisted_events = persist_trajectories(
        db,
        match_result.get("trajectories", []),
    )
finally:
    db.close()

print(f"Persisted events: {persisted_events}")

print("Match result keys:", list(match_result.keys()))


for trajectory in trajectories[:16]:
    vehicle_id = trajectory.get("vehicle_id")
    events = trajectory.get("event_observations", [])
    cameras = []
    for event in events:
        camera = event.get("camera_id")
        if camera and camera not in cameras:
            cameras.append(camera)

    print(
        f"Vehicle {vehicle_id} | "
        f"cameras={cameras} | "
        f"events={len(events)}"
    )

print("\nC01 + C02 + C03 tracking and matching test complete.")




