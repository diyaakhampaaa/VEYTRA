"""CLI entrypoint: python run_ocr.py --image tests/sample_crops/crop1.jpg"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_OCR_DIR = Path(__file__).resolve().parent
_ROOT = _OCR_DIR.parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ai.ocr.ocr_engine import read_plate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="VEYTRA READ stage — OCR a plate crop.")
    parser.add_argument(
        "--image",
        required=True,
        help="Path to a plate crop (relative paths resolve from cwd, then ai/ocr/).",
    )
    args = parser.parse_args(argv)

    image_path = Path(args.image)
    if not image_path.is_file():
        fallback = _OCR_DIR / args.image
        if fallback.is_file():
            image_path = fallback
        else:
            print(json.dumps({"plate": None, "confidence": 0.0, "alternatives": []}))
            print(f"error: image not found: {args.image}", file=sys.stderr)
            return 1

    result = read_plate(str(image_path))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
