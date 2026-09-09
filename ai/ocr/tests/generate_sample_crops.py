"""Create synthetic plate crops used by tests and the README sample."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

OUT = Path(__file__).resolve().parent / "sample_crops"


def _blank(w: int = 360, h: int = 90, color: tuple[int, int, int] = (40, 200, 230)) -> np.ndarray:
    canvas = np.zeros((h, w, 3), dtype=np.uint8)
    canvas[:, :] = color
    cv2.rectangle(canvas, (4, 4), (w - 5, h - 5), (30, 30, 30), 3)
    return canvas


def _paint(text: str, *, blur: int = 0, angle: float = 0.0, occlude: bool = False) -> np.ndarray:
    img = _blank()
    h, w = img.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 1.35
    thickness = 3
    (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
    x = max(8, (w - tw) // 2)
    y = (h + th) // 2
    cv2.putText(img, text, (x, y), font, scale, (20, 20, 20), thickness, cv2.LINE_AA)
    if angle:
        matrix = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), angle, 1.0)
        img = cv2.warpAffine(img, matrix, (w, h), flags=cv2.INTER_LINEAR, borderValue=(40, 200, 230))
    if blur:
        k = blur if blur % 2 == 1 else blur + 1
        img = cv2.GaussianBlur(img, (k, k), 0)
    if occlude:
        cv2.rectangle(img, (w // 2, 8), (w - 12, h - 8), (60, 60, 60), -1)
    return img


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(OUT / "crop1.jpg"), _paint("DL01AB1234"))
    cv2.imwrite(str(OUT / "crop2.jpg"), _paint("MH12DE1433", blur=11))
    cv2.imwrite(str(OUT / "crop3.jpg"), _paint("KA03MG1991", angle=18.0))
    cv2.imwrite(str(OUT / "crop4.jpg"), _paint("TN09AB2468", occlude=True))
    cv2.imwrite(str(OUT / "crop_unreadable.jpg"), np.zeros((48, 160, 3), dtype=np.uint8))
    print(f"wrote samples to {OUT}")


if __name__ == "__main__":
    main()
