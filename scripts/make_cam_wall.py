import cv2, sys, random, pathlib

sys.path.insert(0, "ai/detection")
from detector import detect

SRC = pathlib.Path(sys.argv[1])
OUT = pathlib.Path("frontend/public/cams")
OUT.mkdir(parents=True, exist_ok=True)
TARGET = 10

frames = sorted(p for p in SRC.rglob("*") if p.suffix.lower() in {".jpg", ".jpeg", ".png"})
random.seed(7)

# Blur plates once on each full frame (detection works best on the whole scene)
blurred = []
for p in frames:
    img = cv2.imread(str(p))
    if img is None:
        continue
    for d in detect(img, "cam", "now", "real")["detections"]:
        if d["plate_bbox"]:
            x1, y1, x2, y2 = d["plate_bbox"]
            roi = img[y1:y2, x1:x2]
            if roi.size:
                img[y1:y2, x1:x2] = cv2.GaussianBlur(roi, (51, 51), 0)
    blurred.append(img)

for i in range(1, TARGET + 1):
    img = blurred[(i - 1) % len(blurred)]
    h, w = img.shape[:2]
    if i > len(blurred):  # repeats get a random crop so they look different
        cw = int(w * random.uniform(0.55, 0.8))
        ch = int(h * random.uniform(0.55, 0.8))
        x0 = random.randint(0, w - cw)
        y0 = random.randint(0, h - ch)
        img = img[y0:y0 + ch, x0:x0 + cw]
        h, w = img.shape[:2]
    img = cv2.resize(img, (800, int(800 * h / w)))
    cv2.imwrite(str(OUT / f"cam{i}.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 80])
    print("saved", i)
