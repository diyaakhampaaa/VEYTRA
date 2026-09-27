import cv2
from ai.detection.detector import detect

p = r"data\tracking_videos\C01.MOV"
cap = cv2.VideoCapture(p)
fps = cap.get(cv2.CAP_PROP_FPS)

i = 0
saved = 0
limit = int(fps)

while i < limit:
    ok, frame = cap.read()
    if not ok:
        break

    if i % 10 == 0:
        result = detect(
            frame=frame,
            camera_id="C01",
            timestamp=str(i / fps),
            source="real",
        )

        for j, detection in enumerate(result.get("detections", [])):
            bbox = detection.get("plate_bbox")

            if not bbox:
                continue

            x1, y1, x2, y2 = map(int, bbox)
            h, w = frame.shape[:2]

            x1 = max(0, min(x1, w))
            x2 = max(0, min(x2, w))
            y1 = max(0, min(y1, h))
            y2 = max(0, min(y2, h))

            crop = frame[y1:y2, x1:x2]

            if crop.size:
                path = f"data\debug_plate_C01_{i}_{j}.jpg"
                cv2.imwrite(path, crop)
                saved += 1

    i += 1

cap.release()
print("Saved plate crops:", saved)
