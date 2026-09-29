import cv2
import os

VIDEOS = {
    "CAM_01": "data/raw_videos/camera1.mov",
    "CAM_02": "data/raw_videos/camera2.mp4",
    "CAM_03": "data/raw_videos/camera3.mp4",
}

OUTPUT_DIR = "data/sample_frames"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for camera_id, video_path in VIDEOS.items():

    print(f"\nProcessing {camera_id}: {video_path}")

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"ERROR: Could not open {video_path}")
        continue

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    duration = total_frames / fps if fps else 0

    print(f"FPS: {fps:.2f}")
    print(f"Duration: {duration:.2f} seconds")

    frame_interval = int(fps * 2)

    frame_number = 0
    saved = 0

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        if frame_number % frame_interval == 0:

            filename = os.path.join(
                OUTPUT_DIR,
                f"{camera_id}_{frame_number}.jpg"
            )

            cv2.imwrite(filename, frame)

            saved += 1

            print(f"Saved: {filename}")

        frame_number += 1

    cap.release()

    print(f"{camera_id}: saved {saved} sample frames")

print("\nDone!")