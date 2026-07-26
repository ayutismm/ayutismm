import os
import argparse
from pathlib import Path
from xml.sax.saxutils import escape

RADIUS = 16
PADDING_X = 28
PADDING_Y = 24
LINE_HEIGHT = 22
LABEL_SPACING = 110
TEXT_FONT_SIZE = 12
SVG_WIDTH = 540
BACKGROUND = "#0f172a"
BORDER = "#334155"
TEXT_COLOR = "#e2e8f0"
ACCENT = "#38bdf8"
SECONDARY = "#94a3b8"

CONTENT = [
    ("", "ayush@github"),
    ("", "──────────────────────────────────────────────"),
    ("Now", "B.Tech ECE @ IIIT Kota"),
    ("Focus", "Software Development & DSA"),
    ("Seeking", "SDE Internship '27"),
    ("Location", "Rajasthan, India"),
    ("", ""),
    ("Edu", "B.Tech Electronics & Communication"),
    ("", "Indian Institute of Information Technology Kota"),
    ("", ""),
    ("— Stack", ""),
    ("Languages", "C++, C, Python, JavaScript"),
    ("Frontend", "HTML, CSS, React, Tailwind CSS, Vite"),
    ("Backend", "Node.js, Express.js"),
    ("Database", "Firebase, Supabase"),
    ("Tools", "Git, GitHub, Android Studio, VS Code, Figma"),
    ("Learning", "System Design, SQL, Next.js"),
    ("", ""),
    ("— Projects", ""),
    ("Featured", "Campus Companion"),
    ("", "DHWANI (BFSK Acoustic Communication)"),
    ("", "Bluetooth Mesh Emergency System"),
    ("", ""),
    ("— CP", ""),
    ("LeetCode", "DSA & Problem Solving"),
    ("CodeChef", "★ 1115 Rating"),
    ("", ""),
    ("Focus", "Arrays • Hashing • Sliding Window"),
    ("", "Bit Manipulation • STL"),
    ("", ""),
    ("— Interests", ""),
    ("", "AI Apps"),
    ("", "Backend Development"),
    ("", "Open Source"),
    ("", "Mobile Development"),
    ("", ""),
    ("— Highlights", ""),
    ("•", "Lead Designer @ Neon Cinematics"),
    ("•", "Content Lead @ GDG Genesys"),
    ("•", "2+ Years Freelance Graphic Designer"),
    ("•", "Building real-world software projects"),
]


def build_svg(static: bool = False) -> str:
    rows = CONTENT
    svg_height = PADDING_Y * 2 + len(rows) * LINE_HEIGHT
    lines = []
    stagger = 0.05

    for index, (label, value) in enumerate(rows):
        y = PADDING_Y + index * LINE_HEIGHT
        x_label = PADDING_X
        x_value = PADDING_X + LABEL_SPACING
        delay = round(index * stagger, 3)

        is_accent = label and not label.startswith('—') and label != '•'
        label_fill = ACCENT if is_accent else TEXT_COLOR
        if not value and not label:
            label_fill = SECONDARY

        safe_label = escape(label)
        safe_value = escape(value)

        if static:
            cls = ""
            style = ""
        else:
            cls = ' class="line"'
            style = f' style="animation-delay:{delay}s"'

        label_text = (
            f'  <text{cls}{style} x="{x_label}" y="{y}" fill="{label_fill}" '
            f'xml:space="preserve">{safe_label}</text>\n'
        )

        if value:
            value_text = (
                f'  <text{cls}{style} x="{x_value}" y="{y}" fill="{TEXT_COLOR}" '
                f'xml:space="preserve">{safe_value}</text>\n'
            )
        else:
            value_text = ""

        lines.append(label_text)
        lines.append(value_text)

    animation_css = ""
    if not static:
        animation_css = (
            '  .line { opacity: 0; animation: fadeIn 0.55s ease-out both; }\n'
            '  @keyframes fadeIn { '
            '0% { opacity: 0; transform: translateY(-6px); } '
            '60% { opacity: 1; transform: translateY(1px); } '
            '100% { opacity: 1; transform: translateY(0); } }\n'
            '  @media (prefers-reduced-motion: reduce) { '
            '.line { opacity: 1 !important; animation: none !important; } }\n'
        )

    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_WIDTH} {svg_height}" '
        f'width="{SVG_WIDTH}" height="{svg_height}" '
        f'font-family="\'JetBrains Mono\', \'Courier New\', monospace" font-size="{TEXT_FONT_SIZE}px">\n'
        f'<style>\n'
        f'  text {{ shape-rendering: crispEdges; }}\n'
        f'{animation_css}'
        f'</style>\n'
        f'<rect width="{SVG_WIDTH}" height="{svg_height}" fill="none" />\n'
        f'<rect x="1" y="1" width="{SVG_WIDTH - 2}" height="{svg_height - 2}" '
        f'fill="{BACKGROUND}" rx="{RADIUS}" ry="{RADIUS}" stroke="{BORDER}" stroke-width="1" />\n'
        f'<g>\n'
        + "".join(lines)
        + f'</g>\n'
        f'</svg>\n'
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a small neofetch-style info card SVG.")
    parser.add_argument(
        "--output",
        default="info-card.svg",
        help="Output SVG path (default: info-card.svg)",
    )
    args = parser.parse_args()

    static = os.environ.get("STATIC", "0") == "1"
    svg_content = build_svg(static=static)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg_content, encoding="utf-8")
    print(f"Wrote info card to: {output_path} {'(static)' if static else '(animated)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
