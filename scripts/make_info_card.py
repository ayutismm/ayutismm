import os
import argparse
from pathlib import Path
from xml.sax.saxutils import escape

SVG_WIDTH = 490
PADDING_X = 20
TITLE_BAR_H = 30
LINE_HEIGHT = 20.5
LABEL_X = 112
RADIUS = 12

# GitHub dark theme colors (matching reference)
BG_TOP = "#111722"
BG_BOTTOM = "#0d1117"
BORDER = "#30363d"
TITLE_COLOR = "#7d8590"
NAME_GREEN = "#3fb950"
NAME_CYAN = "#22d3ee"
LABEL_ORANGE = "#ffa657"
TEXT_LIGHT = "#c9d1d9"
SECTION_BLUE = "#58a6ff"
BULLET_GREEN = "#3fb950"
DIM = "#7d8590"

# Content rows: (type, label, value)
#   type: "header", "kv", "section", "bullet", "blank"
CONTENT = [
    ("header", "", ""),
    ("kv", "Now", "B.Tech ECE @ IIIT Kota"),
    ("kv", "Focus", "Software Development & DSA"),
    ("kv", "Seeking", "SDE Internship '27"),
    ("kv", "Location", "Rajasthan, India"),
    ("kv", "Edu", "B.Tech Electronics & Communication"),
    ("kv", "", "Indian Institute of Information Technology Kota"),
    ("blank", "", ""),
    ("section", "— Stack", ""),
    ("kv", "Languages", "C++, C, Python, JavaScript"),
    ("kv", "Frontend", "HTML, CSS, React, Tailwind, Vite"),
    ("kv", "Backend", "Node.js, Express.js"),
    ("kv", "Database", "Firebase, Supabase"),
    ("kv", "Tools", "Git, GitHub, Android Studio, VS Code"),
    ("kv", "Learning", "System Design, SQL, Next.js"),
    ("blank", "", ""),
    ("section", "— Projects", ""),
    ("kv", "Featured", "Campus Companion"),
    ("kv", "", "DHWANI (BFSK Acoustic Communication)"),
    ("kv", "", "Bluetooth Mesh Emergency System"),
    ("blank", "", ""),
    ("section", "— CP", ""),
    ("kv", "LeetCode", "DSA & Problem Solving"),
    ("kv", "CodeChef", "★ 1115 Rating"),
    ("kv", "Focus", "Arrays • Hashing • Sliding Window"),
    ("kv", "", "Bit Manipulation • STL"),
    ("blank", "", ""),
    ("section", "— Highlights", ""),
    ("bullet", "", "Lead Designer @ Neon Cinematics"),
    ("bullet", "", "Content Lead @ GDG Genesys"),
    ("bullet", "", "2+ Years Freelance Graphic Designer"),
    ("bullet", "", "Building real-world software projects"),
]

STAGGER = 0.06


def build_svg(static: bool = False) -> str:
    y_cursor = TITLE_BAR_H + 15
    elements = []
    row_index = 0

    for row_type, label, value in CONTENT:
        delay = round(row_index * STAGGER + 0.15, 2)
        anim_cls = "" if static else ' class="row"'
        anim_style = "" if static else f' style="animation-delay:{delay}s"'

        if row_type == "header":
            # avi@github header with colored segments + divider line
            elements.append(
                f'<g{anim_cls}{anim_style}>'
                f'<text x="{PADDING_X}" y="{y_cursor}" font-size="14" font-weight="700">'
                f'<tspan fill="{NAME_GREEN}">avi</tspan>'
                f'<tspan fill="{DIM}">@</tspan>'
                f'<tspan fill="{NAME_CYAN}">github</tspan></text>'
                f'<line x1="{LABEL_X}" y1="{y_cursor - 4}" x2="{SVG_WIDTH - PADDING_X}" '
                f'y2="{y_cursor - 4}" stroke="{BORDER}" stroke-opacity="0.8"/>'
                f'</g>'
            )
            y_cursor += LINE_HEIGHT
            row_index += 1

        elif row_type == "kv":
            safe_label = escape(label)
            safe_value = escape(value)
            parts = []
            if label:
                parts.append(
                    f'<text x="{PADDING_X}" y="{y_cursor}" fill="{LABEL_ORANGE}" '
                    f'font-size="12.5" font-weight="700">{safe_label}</text>'
                )
            if value:
                vx = LABEL_X if label else LABEL_X
                parts.append(
                    f'<text x="{vx}" y="{y_cursor}" fill="{TEXT_LIGHT}" '
                    f'font-size="12.5">{safe_value}</text>'
                )
            elements.append(f'<g{anim_cls}{anim_style}>{"".join(parts)}</g>')
            y_cursor += LINE_HEIGHT
            row_index += 1

        elif row_type == "section":
            y_cursor += 5  # extra spacing before section
            safe_label = escape(label)
            elements.append(
                f'<g{anim_cls}{anim_style}>'
                f'<text x="{PADDING_X}" y="{y_cursor}" fill="{SECTION_BLUE}" '
                f'font-size="12.5" font-weight="700">{safe_label}</text>'
                f'<line x1="{PADDING_X + 75}" y1="{y_cursor - 4}" '
                f'x2="{SVG_WIDTH - PADDING_X}" y2="{y_cursor - 4}" '
                f'stroke="{BORDER}" stroke-opacity="0.8"/>'
                f'</g>'
            )
            y_cursor += LINE_HEIGHT
            row_index += 1

        elif row_type == "bullet":
            safe_value = escape(value)
            elements.append(
                f'<g{anim_cls}{anim_style}>'
                f'<circle cx="{PADDING_X + 3}" cy="{y_cursor - 4}" r="2.5" fill="{BULLET_GREEN}"/>'
                f'<text x="{PADDING_X + 14}" y="{y_cursor}" fill="{TEXT_LIGHT}" '
                f'font-size="12.5">{safe_value}</text>'
                f'</g>'
            )
            y_cursor += LINE_HEIGHT
            row_index += 1

        elif row_type == "blank":
            y_cursor += 10

    svg_height = int(y_cursor + 20)

    # Animation CSS
    anim_css = ""
    if not static:
        anim_css = (
            '  .row { opacity: 0; transform: translateY(5px); '
            'animation: slideUp 0.4s ease-out both; }\n'
            '  @keyframes slideUp { '
            '0% { opacity: 0; transform: translateY(5px); } '
            '100% { opacity: 1; transform: translateY(0); } }\n'
            '  @media (prefers-reduced-motion: reduce) { '
            '.row { opacity: 1 !important; animation: none !important; } }\n'
        )

    body = "\n".join(elements)

    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{svg_height}" '
        f'viewBox="0 0 {SVG_WIDTH} {svg_height}" '
        f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">\n'
        f'<defs>\n'
        f'  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">\n'
        f'    <stop offset="0" stop-color="{BG_TOP}"/>\n'
        f'    <stop offset="1" stop-color="{BG_BOTTOM}"/>\n'
        f'  </linearGradient>\n'
        f'</defs>\n'
        f'<style>\n'
        f'{anim_css}'
        f'</style>\n'
        f'<rect width="{SVG_WIDTH}" height="{svg_height}" rx="{RADIUS}" fill="url(#bg)"/>\n'
        f'<rect x="0.5" y="0.5" width="{SVG_WIDTH - 1}" height="{svg_height - 1}" '
        f'rx="{RADIUS}" fill="none" stroke="{BORDER}"/>\n'
        f'<line x1="0" y1="{TITLE_BAR_H}" x2="{SVG_WIDTH}" y2="{TITLE_BAR_H}" stroke="{BORDER}"/>\n'
        f'<circle cx="20" cy="15" r="5" fill="#ff5f56"/>\n'
        f'<circle cx="36" cy="15" r="5" fill="#ffbd2e"/>\n'
        f'<circle cx="52" cy="15" r="5" fill="#27c93f"/>\n'
        f'<text x="{SVG_WIDTH / 2}" y="19" fill="{TITLE_COLOR}" font-size="12" '
        f'text-anchor="middle">avi@github: ~$ neofetch</text>\n'
        f'{body}\n'
        f'</svg>\n'
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a neofetch-style info card SVG.")
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
