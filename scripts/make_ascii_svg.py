import argparse
from pathlib import Path
from xml.sax.saxutils import escape

import cv2
import numpy as np

RAMP = " .`:-=+*cs#%@"  # bright (sparse) -> dark (dense)
DEFAULT_SOURCE = "source-prepped.png"
DEFAULT_OUTPUT = "avi-ascii.svg"

CARD_WIDTH = 540
BACKGROUND = "#0f172a"
BORDER = "#334155"
TEXT_COLOR = "#38bdf8"
ACCENT = "#e2e8f0"
SECONDARY = "#94a3b8"


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
    card_height = int(header_h + grid_height + 40)

    offset_x = round((CARD_WIDTH - grid_width) / 2, 1)
    offset_y = round(header_h + 10, 1)

    stagger = 0.04

    # Build text rows markup using CSS animation classes
    text_rows = []
    for i, row_text in enumerate(rows):
        y = offset_y + i * line_height
        delay = round(i * stagger, 3)
        safe_text = escape(row_text)
        text_rows.append(
            f'  <text class="r" x="{offset_x}" y="{y}" '
            f'style="animation-delay:{delay}s" '
            f'xml:space="preserve" dominant-baseline="text-before-edge">{safe_text}</text>'
        )

    rows_markup = "\n".join(text_rows)

    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CARD_WIDTH} {card_height}" '
        f'width="{CARD_WIDTH}" height="{card_height}" '
        f'font-family="\'JetBrains Mono\', \'Courier New\', monospace">\n'
        f'<style>\n'
        f'  .r {{ fill: {TEXT_COLOR}; font-size: 11px; opacity: 0; '
        f'animation: fadeIn 0.5s ease-out both; }}\n'
        f'  .hdr {{ fill: {ACCENT}; font-size: 12px; opacity: 0; '
        f'animation: fadeIn 0.5s ease-out both; }}\n'
        f'  .hdr2 {{ fill: {TEXT_COLOR}; font-size: 12px; opacity: 0; '
        f'animation: fadeIn 0.5s ease-out both; animation-delay: 0.05s; }}\n'
        f'  .sep {{ fill: {SECONDARY}; font-size: 12px; opacity: 0; '
        f'animation: fadeIn 0.5s ease-out both; animation-delay: 0.1s; }}\n'
        f'  @keyframes fadeIn {{ '
        f'0% {{ opacity: 0; transform: translateY(-6px); }} '
        f'60% {{ opacity: 1; transform: translateY(1px); }} '
        f'100% {{ opacity: 1; transform: translateY(0); }} }}\n'
        f'  @media (prefers-reduced-motion: reduce) {{ '
        f'.r, .hdr, .hdr2, .sep {{ opacity: 1 !important; animation: none !important; }} }}\n'
        f'</style>\n'
        f'<rect width="{CARD_WIDTH}" height="{card_height}" fill="none" />\n'
        f'<rect x="1" y="1" width="{CARD_WIDTH - 2}" height="{card_height - 2}" '
        f'fill="{BACKGROUND}" rx="16" ry="16" stroke="{BORDER}" stroke-width="1" />\n'
        f'<text class="hdr" x="28" y="24" xml:space="preserve">ayush@ascii</text>\n'
        f'<text class="hdr2" x="138" y="24" xml:space="preserve">./render_portrait.py</text>\n'
        f'<text class="sep" x="28" y="46" xml:space="preserve">'
        f'──────────────────────────────────────────────</text>\n'
        f'{rows_markup}\n'
        f'</svg>\n'
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Render ASCII portrait SVG from a prepped grayscale image.")
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
