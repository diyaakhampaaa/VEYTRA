import os
import cv2
from detector import detect

sample_dir = 'tests/sample_frames'
image_files = sorted(os.listdir(sample_dir))

for fname in image_files:
    path = os.path.join(sample_dir, fname)
    frame = cv2.imread(path)
    if frame is None:
        continue
    result = detect(frame, camera_id='C01', timestamp='2026-01-01T00:00:00', source='real')
    for i, det in enumerate(result['detections']):
        bbox = det.get('plate_bbox')
        if bbox is None:
            continue
        x1, y1, x2, y2 = bbox
        w, h = x2 - x1, y2 - y1
        conf = det['plate_confidence']
        vtype = det['vehicle_type']
        print(f"{fname}_{i}_{vtype}_conf{conf:.2f}: original size {w}x{h}px (area={w*h})")