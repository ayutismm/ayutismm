import argparse
from pathlib import Path
from xml.sax.saxutils import escape

import cv2
import numpy as np

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense)
DEFAULT_SOURCE = "source-prepped.png"
DEFAULT_OUTPUT = "avi-ascii.svg"

# Target card dimensions matching info-card.svg
CARD_WIDTH = 540
CARD_HEIGHT = 972
BACKGROUND = "#0f172a"
BORDER = "#334155"
TEXT_COLOR = "#38bdf8"
SECONDARY = "#94a3b8"
ACCENT = "#e2e8f0"


def build_ascii_grid(gray_image: np.ndarray, width: int = 68) -> list[str]:
    height, original_width = gray_image.shape
    aspect = height / original_width
    char_aspect = 0.52
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


def make_svg_content(rows: list[str]) -> str:
    cols = len(rows[0]) if rows else 0
    char_width = 7.1
    line_height = 13.0
    
    header_h = 60
    grid_width = cols * char_width
    grid_height = len(rows) * line_height
    
    offset_x = round((CARD_WIDTH - grid_width) / 2, 1)
    offset_y = round(header_h + (CARD_HEIGHT - header_h - grid_height) / 2, 1)

    total_duration = 0.75
    row_delay = 0.04
    cursor_width = 6

    def row_svg(row_index: int) -> str:
        y = offset_y + row_index * line_height
        begin = f"{round(row_index * row_delay, 2)}s"
        animate = (
            f"<animate attributeName=\"width\" from=\"0\" "
            f"to=\"{round(grid_width, 1)}\" dur=\"{total_duration}s\" begin=\"{begin}\" fill=\"freeze\" />"
        )
        return (
            f"  <clipPath id=\"clip-{row_index}\">\n"
            f"    <rect x=\"{offset_x}\" y=\"{y}\" width=\"0\" height=\"{line_height}\">\n"
            f"      {animate}\n"
            f"    </rect>\n"
            f"  </clipPath>\n"
        )

    rows_defs = [row_svg(i) for i in range(len(rows))]

    def row_group(row_index: int, row_text: str) -> str:
        y = offset_y + row_index * line_height
        begin = f"{round(row_index * row_delay, 2)}s"
        safe_text = escape(row_text)
        return (
            f"  <g clip-path=\"url(#clip-{row_index})\">\n"
            f"    <text x=\"{offset_x}\" y=\"{y}\" fill=\"{TEXT_COLOR}\" font-family=\"'JetBrains Mono', 'Courier New', monospace\" font-size=\"11px\" xml:space=\"preserve\" dominant-baseline=\"text-before-edge\">{safe_text}</text>\n"
            f"    <rect x=\"{offset_x}\" y=\"{y}\" width=\"{cursor_width}\" height=\"{line_height}\" fill=\"{ACCENT}\" opacity=\"0.8\">\n"
            f"      <animate attributeName=\"x\" from=\"{offset_x}\" to=\"{round(offset_x + grid_width, 1)}\" dur=\"{total_duration}s\" begin=\"{begin}\" fill=\"freeze\" />\n"
            f"    </rect>\n"
            f"  </g>\n"
        )

    rows_groups = [row_group(i, r) for i, r in enumerate(rows)]
    rows_defs_text = "".join(rows_defs)
    rows_groups_text = "".join(rows_groups)

    header_markup = (
        f"  <text x=\"28\" y=\"24\" fill=\"{ACCENT}\" font-family=\"'JetBrains Mono', 'Courier New', monospace\" font-size=\"12px\" xml:space=\"preserve\">ayush@ascii</text>\n"
        f"  <text x=\"138\" y=\"24\" fill=\"{TEXT_COLOR}\" font-family=\"'JetBrains Mono', 'Courier New', monospace\" font-size=\"12px\" xml:space=\"preserve\">./render_portrait.py</text>\n"
        f"  <text x=\"28\" y=\"46\" fill=\"{SECONDARY}\" font-family=\"'JetBrains Mono', 'Courier New', monospace\" font-size=\"12px\" xml:space=\"preserve\">──────────────────────────────────────────────</text>\n"
    )

    return (
        f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        f"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 {CARD_WIDTH} {CARD_HEIGHT}\" "
        f"width=\"{CARD_WIDTH}\" height=\"{CARD_HEIGHT}\" xml:space=\"preserve\">\n"
        f"  <style>\n"
        f"    text {{ shape-rendering: crispEdges; }}\n"
        f"  </style>\n"
        f"  <rect x=\"0\" y=\"0\" width=\"100%\" height=\"100%\" fill=\"{BACKGROUND}\" rx=\"16\" ry=\"16\" stroke=\"{BORDER}\" stroke-width=\"1\" />\n"
        f"{header_markup}"
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
        default=68,
        help="Character grid width in columns (default: 68)",
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

    svg_content = make_svg_content(rows)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg_content, encoding="utf-8")
    print(f"Wrote SVG to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
