import os
import argparse
from pathlib import Path
from xml.sax.saxutils import escape

RADIUS = 16
PADDING_X = 28
PADDING_Y = 24
LINE_HEIGHT = 22
LABEL_SPACING = 110
TITLE_FONT_SIZE = 14
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
    defs = []
    duration = 0.45
    stagger = 0.05

    for index, (label, value) in enumerate(rows):
        y = PADDING_Y + index * LINE_HEIGHT
        is_title = index == 0
        text_color = TEXT_COLOR if value or label else SECONDARY
        x_label = PADDING_X
        x_value = PADDING_X + LABEL_SPACING
        begin = f"{index * stagger}s"
        if static:
            label_anim = ""
            value_anim = ""
            opacity = "1"
            transform = ""
        else:
            label_anim = (
                f"<animate attributeName=\"opacity\" from=\"0\" to=\"1\" dur=\"0.25s\" begin=\"{begin}\" fill=\"freeze\" />"
            )
            value_anim = (
                f"<animate attributeName=\"opacity\" from=\"0\" to=\"1\" dur=\"0.25s\" begin=\"{begin}\" fill=\"freeze\" />"
            )
            opacity = "0"
            transform = f"transform=\"translate(-12,0)\""

        safe_label = escape(label)
        safe_value = escape(value)
        label_text = (
            f"  <text x=\"{x_label}\" y=\"{y}\" fill=\"{ACCENT if label and not label.startswith('—') and label != '•' else text_color}\" "
            f"font-family=\"'JetBrains Mono', 'Courier New', monospace\" font-size=\"{TEXT_FONT_SIZE}px\" "
            f"opacity=\"{opacity}\" {transform} xml:space=\"preserve\">{safe_label}</text>\n"
        )

        if value:
            value_text = (
                f"  <text x=\"{x_value}\" y=\"{y}\" fill=\"{text_color}\" "
                f"font-family=\"'JetBrains Mono', 'Courier New', monospace\" font-size=\"{TEXT_FONT_SIZE}px\" "
                f"opacity=\"{opacity}\" {transform} xml:space=\"preserve\">{safe_value}</text>\n"
            )
        else:
            value_text = ""

        if not static:
            label_text = label_text.replace("</text>", f"{label_anim}</text>")
            if value_text:
                value_text = value_text.replace("</text>", f"{value_anim}</text>")

        lines.append(label_text)
        lines.append(value_text)

    return (
        f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        f"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 {SVG_WIDTH} {svg_height}\" "
        f"width=\"{SVG_WIDTH}\" height=\"{svg_height}\" xml:space=\"preserve\">\n"
        f"  <style>\n"
        f"    text {{ shape-rendering: crispEdges; }}\n"
        f"  </style>\n"
        f"  <rect x=\"0\" y=\"0\" width=\"100%\" height=\"100%\" fill=\"{BACKGROUND}\" rx=\"{RADIUS}\" ry=\"{RADIUS}\" stroke=\"{BORDER}\" stroke-width=\"1\" />\n"
        f"  <g>\n"
        + "".join(lines)
        + f"  </g>\n"
        f"</svg>\n"
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
