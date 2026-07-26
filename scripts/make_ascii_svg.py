import argparse
from pathlib import Path

import cv2
import numpy as np

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense)
DEFAULT_SOURCE = "source-prepped.png"
DEFAULT_OUTPUT = "avi-ascii.svg"


def build_ascii_grid(gray_image: np.ndarray, width: int = 100) -> list[str]:
    height, original_width = gray_image.shape
    aspect = height / original_width
    char_aspect = 0.55
    target_height = max(1, int(width * aspect * char_aspect))
    resized = cv2.resize(gray_image, (width, target_height), interpolation=cv2.INTER_AREA)

    rows: list[str] = []
    ramp_length = len(RAMP)
    for y in range(resized.shape[0]):
        row_chars = []
        for x in range(resized.shape[1]):
            value = int(resized[y, x])
            index = int((255 - value) * (ramp_length - 1) / 255)
            row_chars.append(RAMP[index])
        rows.append("".join(row_chars))
    return rows


def make_svg_content(rows: list[str], char_width: int = 10, line_height: int = 14) -> str:
    cols = len(rows[0]) if rows else 0
    svg_width = cols * char_width
    svg_height = len(rows) * line_height
    total_duration = 0.75
    row_delay = 0.06
    cursor_width = 6

    def row_svg(row_index: int, row_text: str) -> str:
        y = row_index * line_height
        begin = f"{row_index * row_delay}s"
        animate = (
            f"<animate attributeName=\"width\" from=\"0\" "
            f"to=\"{svg_width}\" dur=\"{total_duration}s\" begin=\"{begin}\" fill=\"freeze\" />"
        )

        return (
            f"  <clipPath id=\"clip-{row_index}\">\n"
            f"    <rect x=\"0\" y=\"{y}\" width=\"0\" height=\"{line_height}\">\n"
            f"      {animate}\n"
            f"    </rect>\n"
            f"  </clipPath>\n"
        )

    rows_defs = [row_svg(i, r) for i, r in enumerate(rows)]

    def row_group(row_index: int, row_text: str) -> str:
        y = row_index * line_height
        begin = f"{row_index * row_delay}s"
        return (
            f"  <g clip-path=\"url(#clip-{row_index})\">\n"
            f"    <text x=\"0\" y=\"{y}\" xml:space=\"preserve\" dominant-baseline=\"text-before-edge\">{row_text}</text>\n"
            f"    <rect x=\"0\" y=\"{y}\" width=\"{cursor_width}\" height=\"{line_height}\" fill=\"#777\" opacity=\"0.9\">\n"
            f"      <animate attributeName=\"x\" from=\"0\" to=\"{svg_width}\" dur=\"{total_duration}s\" begin=\"{begin}\" fill=\"freeze\" />\n"
            f"    </rect>\n"
            f"  </g>\n"
        )

    rows_groups = [row_group(i, r) for i, r in enumerate(rows)]
    rows_defs_text = "".join(rows_defs)
    rows_groups_text = "".join(rows_groups)

    return (
        f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        f"<svg xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" "
        f"viewBox=\"0 0 {svg_width} {svg_height}\" width=\"{svg_width}\" height=\"{svg_height}\" xml:space=\"preserve\">\n"
        f"  <style>\n"
        f"    text {{ fill: #38bdf8; font-family: 'DejaVu Sans Mono', 'Courier New', monospace; font-size: 12px; white-space: pre; }}\n"
        f"  </style>\n"
        f"  <rect width=\"100%\" height=\"100%\" fill=\"#0f172a\" rx=\"16\" ry=\"16\" stroke=\"#334155\" stroke-width=\"1\" />\n"
        f"  <defs>\n"
        f"{rows_defs_text}"
        f"  </defs>\n"
        f"{rows_groups_text}"
        f"</svg>\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a self-typing ASCII SVG from a prepped grayscale image.")
    parser.add_argument(
        "--source",
        default=DEFAULT_SOURCE,
        help=f"Path to the prepped grayscale source image (default: {DEFAULT_SOURCE})",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Path to output SVG file (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=100,
        help="Character grid width in columns (default: 100)",
    )
    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.exists():
        print(f"Source image not found: {source_path}")
        return 2

    image = cv2.imread(str(source_path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        print(f"Unable to read source image: {source_path}")
        return 3

    rows = build_ascii_grid(image, width=args.width)
    if not rows:
        print("Built no ASCII rows from image.")
        return 4

    svg_bytes = make_svg_content(rows).encode("utf-8")
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(svg_bytes)
    print(f"Wrote SVG to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
