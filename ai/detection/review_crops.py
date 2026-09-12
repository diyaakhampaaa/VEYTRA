import os
import cv2
import base64
from detector import detect

output_dir = 'crop_review'
os.makedirs(output_dir, exist_ok=True)

sample_dir = 'tests/sample_frames'
image_files = sorted(os.listdir(sample_dir))

count = 0
for fname in image_files:
    path = os.path.join(sample_dir, fname)
    frame = cv2.imread(path)
    if frame is None:
        continue
    result = detect(frame, camera_id='C01', timestamp='2026-01-01T00:00:00', source='real')
    for i, det in enumerate(result['detections']):
        crop_b64 = det.get('plate_crop')
        if crop_b64 is None:
            continue
        conf = det['plate_confidence']
        vtype = det['vehicle_type']
        out_name = f'{output_dir}/{fname}_{i}_{vtype}_conf{conf:.2f}.jpg'
        crop_bytes = base64.b64decode(crop_b64)
        with open(out_name, 'wb') as f:
            f.write(crop_bytes)
        count += 1

print(f'Saved {count} plate crops to {output_dir}/')
