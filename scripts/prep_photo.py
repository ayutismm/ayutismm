import argparse
from pathlib import Path

import cv2
import numpy as np


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a photo for ASCII conversion using CLAHE and a white background.")
    parser.add_argument("source", help="Path to the source photo")
    parser.add_argument(
        "--output",
        default="source-prepped.png",
        help="Output path for the grayscale prep image (default: source-prepped.png)",
    )
    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.exists():
        print(f"Source file not found: {source_path}")
        return 2

    image = cv2.imread(str(source_path), cv2.IMREAD_UNCHANGED)
    if image is None:
        print(f"Unable to read image: {source_path}")
        return 3

    if image.ndim == 2:
        gray = image
        alpha = None
    elif image.shape[2] == 4:
        bgr = image[:, :, :3]
        alpha = image[:, :, 3]
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    else:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        alpha = None

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    prepped = clahe.apply(gray)

    if alpha is not None:
        alpha_f = alpha.astype(np.float32) / 255.0
        prepped_f = prepped.astype(np.float32)
        white_bg = np.full_like(prepped_f, 255.0)
        prepped = (prepped_f * alpha_f + white_bg * (1.0 - alpha_f)).astype(np.uint8)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    success = cv2.imwrite(str(output_path), prepped)
    if not success:
        print(f"Failed to write output image: {output_path}")
        return 4

    print(f"Wrote grayscale prep image to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
