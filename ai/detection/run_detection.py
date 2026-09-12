"""
CLI entrypoint for Member 1's detection module.
Usage:
    python run_detection.py --image path/to/frame.jpg [--camera-id C01] [--source real]
"""

import argparse
import json
import sys
from datetime import datetime, timezone

import cv2

from detector import detect


def main():
    parser = argparse.ArgumentParser(description="Run VEYTRA vehicle+plate detection on a single image.")
    parser.add_argument("--image", required=True, help="Path to the input image file.")
    parser.add_argument("--camera-id", default="C01", help="Camera identifier (default: C01).")
    parser.add_argument(
        "--source",
        default="real",
        choices=["real", "simulated"],
        help="Whether the frame is from real footage or a simulation (default: real).",
    )
    args = parser.parse_args()

    frame = cv2.imread(args.image)
    if frame is None:
        print(f"ERROR: could not read image at '{args.image}'", file=sys.stderr)
        sys.exit(1)

    timestamp = datetime.now(timezone.utc).isoformat()

    result = detect(
        frame=frame,
        camera_id=args.camera_id,
        timestamp=timestamp,
        source=args.source,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()