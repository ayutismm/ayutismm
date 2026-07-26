"""
Build a neofetch-style info card SVG to sit to the RIGHT of the ASCII portrait.
Terminal chrome (traffic-light dots) + gradient background + SMIL slide-in.
"""
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "info-card.svg")
STATIC = bool(os.environ.get("STATIC"))

W, H = 480, 520
PAD = 20
TITLEBAR_H = 30
KEY_X = PAD
VAL_X = PAD + 92
LINE_H = 20.5

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
INK = "#c9d1d9"
KEY = "#ffa657"
SECTION = "#58a6ff"
GREEN = "#3fb950"
ACCENT = "#22d3ee"

ROWS = [
    ("host",),
    ("kv", "Now", "B.Tech ECE @ IIIT Kota"),
    ("kv", "Focus", "Software Development & DSA"),
    ("kv", "Seeking", "SDE Internship '27"),
    ("kv", "Location", "Rajasthan, India"),
    ("gap",),
    ("sec", "Stack"),
    ("kv", "Languages", "C++, C, Python, JavaScript"),
    ("kv", "Frontend", "HTML, CSS, React, Tailwind, Vite"),
    ("kv", "Backend", "Node.js, Express.js"),
    ("kv", "Database", "Firebase, Supabase"),
    ("kv", "Tools", "Git, GitHub, Android Studio, Figma"),
    ("kv", "Learning", "System Design, SQL, Next.js"),
    ("gap",),
    ("sec", "Projects"),
    ("bul", "Campus Companion"),
    ("bul", "DHWANI (BFSK Acoustic Communication)"),
    ("bul", "Bluetooth Mesh Emergency System"),
    ("gap",),
    ("sec", "Highlights"),
    ("bul", "Lead Designer @ Neon Cinematics"),
    ("bul", "Content Lead @ GDG Genesys"),
    ("bul", "2+ Years Freelance Graphic Designer"),
    ("bul", "Building real-world software projects"),
]


def esc(s):
    return html.escape(s)


def rise(inner, i):
    if STATIC:
        return f"<g>{inner}</g>"
    delay = 0.15 + i * 0.06
    return (f'<g opacity="0" transform="translate(0,5)">{inner}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
            f'begin="{delay:.2f}s" dur="0.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>')


y_cursor = TITLEBAR_H + 30
parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    '<defs>'
    f'<linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#ibg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]
for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
             f'text-anchor="middle">ayutismm@github: ~$ neofetch</text>')

for i, row in enumerate(ROWS):
    kind = row[0]
    if kind == "gap":
        y_cursor += LINE_H * 0.5
        continue
    if kind == "host":
        inner = (f'<text x="{KEY_X}" y="{y_cursor:.1f}" font-size="14" font-weight="700">'
                 f'<tspan fill="{GREEN}">ayutismm</tspan><tspan fill="{MUTED}">@</tspan>'
                 f'<tspan fill="{ACCENT}">github</tspan></text>'
                 f'<line x1="{KEY_X+116}" y1="{y_cursor-4:.1f}" x2="{W-PAD}" y2="{y_cursor-4:.1f}" '
                 f'stroke="{FRAME}" stroke-opacity="0.8"/>')
    elif kind == "sec":
        title = esc(row[1])
        inner = (f'<text x="{KEY_X}" y="{y_cursor:.1f}" fill="{SECTION}" font-size="12.5" font-weight="700">'
                 f'&#8212; {title}</text>'
                 f'<line x1="{KEY_X + 12 + len(row[1])*8}" y1="{y_cursor-4:.1f}" x2="{W-PAD}" y2="{y_cursor-4:.1f}" '
                 f'stroke="{FRAME}" stroke-opacity="0.8"/>')
    elif kind == "kv":
        key, val = esc(row[1]), esc(row[2])
        inner = (f'<text x="{KEY_X}" y="{y_cursor:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">{key}</text>'
                 f'<text x="{VAL_X}" y="{y_cursor:.1f}" fill="{INK}" font-size="12.5">{val}</text>')
    elif kind == "bul":
        txt = esc(row[1])
        inner = (f'<circle cx="{KEY_X+3}" cy="{y_cursor-4:.1f}" r="2.5" fill="{GREEN}"/>'
                 f'<text x="{KEY_X+14}" y="{y_cursor:.1f}" fill="{INK}" font-size="12.5">{txt}</text>')
    else:
        continue
    parts.append(rise(inner, i))
    y_cursor += LINE_H

# Auto-size height
actual_h = int(y_cursor + 20)
parts[0] = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{actual_h}" viewBox="0 0 {W} {actual_h}" '
            f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">')
parts[2] = f'<rect width="{W}" height="{actual_h}" rx="12" fill="url(#ibg)"/>'
parts[3] = f'<rect x="0.5" y="0.5" width="{W-1}" height="{actual_h-1}" rx="12" fill="none" stroke="{FRAME}"/>'

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w") as f:
    f.write(svg)
print("wrote", OUT, len(svg), "bytes;", W, "x", actual_h, "content_bottom", round(y_cursor))
