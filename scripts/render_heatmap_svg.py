#!/usr/bin/env python3
"""
Render data/contributions.json as a GitHub-style contribution heatmap SVG matching
the reference style: rounded colored cells in a 53-week x 7-day grid, diagonal
line-after-line slide-down reveal (CSS keyframes), Less->More legend, terminal title bar,
and stats footer.
"""
import datetime
import json
import os
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
IN_PATH = os.path.join(HERE, "..", "data", "contributions.json")
OUT_PATH = os.path.join(HERE, "..", "contrib-heatmap.svg")

# GitHub green ramp: empty -> brightest.
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

CELL = 12
GAP = 3
STEP = CELL + GAP
PAD = 22
LEFT_LABEL_W = 30
TOP_LABEL_H = 20
TITLEBAR_H = 30

BG = "#0a0e14"
BG2 = "#0d1420"
FRAME = "#30363d"
MUTED = "#7d8590"
TEXT = "#e6edf3"
ACCENT = "#22d3ee"
GREEN = "#39d353"
GOLD = "#f2cc60"

# reveal timing
COL_T = 0.065   # per-column delay contribution
ROW_T = 0.0358  # per-row delay contribution
CELL_DUR = 0.42


def level_for(count):
    if count == 0:
        return 0
    if count <= 2:
        return 1
    if count <= 6:
        return 2
    if count <= 15:
        return 3
    if count <= 30:
        return 4
    return 5


def build_grid(days):
    if not days:
        return []
    first = datetime.date.fromisoformat(days[0]["date"])
    lead_pad = (first.weekday() + 1) % 7  # sunday=0
    grid = []
    col = [None] * lead_pad
    for d in days:
        date = datetime.date.fromisoformat(d["date"])
        weekday = (date.weekday() + 1) % 7
        while len(col) < weekday:
            col.append(None)
        col.append((d["date"], d["count"], level_for(d["count"])))
        if len(col) == 7:
            grid.append(col)
            col = []
    if col:
        while len(col) < 7:
            col.append(None)
        grid.append(col)
    return grid


def compute_streaks(days):
    sorted_days = sorted(days, key=lambda d: d["date"])
    total = sum(d["count"] for d in days)
    
    current_streak = 0
    longest_streak = 0
    curr = 0
    best_day = {"date": "-", "count": 0}
    
    for d in sorted_days:
        cnt = d["count"]
        if cnt > best_day["count"]:
            best_day = {"date": d["date"], "count": cnt}
        if cnt > 0:
            curr += 1
            if curr > longest_streak:
                longest_streak = curr
        else:
            curr = 0
            
    # Check if current streak extends up to today/yesterday
    # (Walk backwards from end)
    current_streak = 0
    for d in reversed(sorted_days):
        if d["count"] > 0:
            current_streak += 1
        elif current_streak > 0:
            break

    start_date = sorted_days[0]["date"] if sorted_days else "-"
    end_date = sorted_days[-1]["date"] if sorted_days else "-"
    
    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "range": {"start": start_date, "end": end_date}
    }


def render(data):
    days = data.get("days", [])
    grid = build_grid(days)
    n_cols = len(grid)
    art_w = n_cols * STEP
    art_h = 7 * STEP

    month_labels = []
    seen_months = set()
    for ci, column in enumerate(grid):
        for cell in column:
            if cell is None:
                continue
            date = datetime.date.fromisoformat(cell[0])
            key = (date.year, date.month)
            if key not in seen_months and date.day <= 7:
                seen_months.add(key)
                month_labels.append((ci, date.strftime("%b")))
            break

    canvas_w = PAD + LEFT_LABEL_W + art_w + PAD
    stats_h = 88
    canvas_h = TITLEBAR_H + TOP_LABEL_H + art_h + stats_h + PAD

    css = f"""
.c {{ transform-box: fill-box; transform-origin: center; opacity: 0; animation: pop 0.55s ease-out both; }}
.g {{ animation: pop 0.55s ease-out both, flash 0.7s ease-out both; }}
@keyframes pop {{ 0% {{ opacity: 0; transform: scale(.2); }} 60% {{ opacity: 1; transform: scale(1.1); }} 100% {{ opacity: 1; transform: scale(1); }} }}
@keyframes flash {{ 0% {{ filter: brightness(2.4); }} 45% {{ filter: brightness(2.4); }} 100% {{ filter: brightness(1); }} }}
@media (prefers-reduced-motion: reduce) {{ .c {{ opacity: 1 !important; animation: none !important; }} }}
""".strip()

    username = data.get("username", "ayutismm")

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" '
        f'viewBox="0 0 {canvas_w} {canvas_h}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        f'<style>{css}</style>',
        '<defs>',
        f'<linearGradient id="hbg" x1="0" y1="0" x2="0" y2="1">',
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/>',
        '</linearGradient>',
        '</defs>',
        f'<rect width="{canvas_w}" height="{canvas_h}" rx="12" fill="url(#hbg)"/>',
        f'<rect x="0.5" y="0.5" width="{canvas_w-1}" height="{canvas_h-1}" rx="12" '
        f'fill="none" stroke="{FRAME}" stroke-width="1" stroke-opacity="0.55"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{canvas_w}" y2="{TITLEBAR_H}" stroke="{FRAME}" stroke-opacity="0.35"/>',
    ]
    for i, dotcol in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
        parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
    parts.append(f'<text x="{canvas_w/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
                 f'text-anchor="middle">ayutismm@github: ~/contributions --graph</text>')

    grid_top = TITLEBAR_H + TOP_LABEL_H
    grid_left = PAD + LEFT_LABEL_W

    for ci, label in month_labels:
        x = grid_left + ci * STEP
        parts.append(f'<text x="{x}" y="{TITLEBAR_H + 14}" fill="{MUTED}" font-size="10">{label}</text>')

    for wi, wname in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        y = grid_top + wi * STEP + CELL * 0.78
        parts.append(f'<text x="{PAD}" y="{y:.1f}" fill="{MUTED}" font-size="9">{wname}</text>')

    # the boxes -- rounded rects with pop and flash cascade animation
    for ci, column in enumerate(grid):
        gx = grid_left + ci * STEP
        for ri, cell in enumerate(column):
            if cell is None:
                continue
            date_s, count, lvl = cell
            gy = grid_top + ri * STEP
            delay = ci * COL_T + ri * ROW_T
            plural = "s" if count != 1 else ""
            cls = "c g" if count > 0 else "c e"
            parts.append(
                f'<rect class="{cls}" x="{gx}" y="{gy}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{PALETTE[lvl]}" style="animation-delay:{delay:.3f}s">'
                f'<title>{date_s}: {count} contribution{plural}</title></rect>'
            )

    # legend: Less [][][][][] More
    leg_y = grid_top + art_h + 6
    leg_x = canvas_w - PAD - (len(PALETTE) * (CELL - 1) + 70)
    parts.append(f'<text x="{leg_x}" y="{leg_y + CELL*0.8:.1f}" fill="{MUTED}" font-size="10" text-anchor="end">Less</text>')
    lx = leg_x + 8
    for lvl, color in enumerate(PALETTE):
        parts.append(f'<rect x="{lx}" y="{leg_y}" width="{CELL-1}" height="{CELL-1}" rx="2.2" fill="{color}"/>')
        lx += CELL
    parts.append(f'<text x="{lx + 4}" y="{leg_y + CELL*0.8:.1f}" fill="{MUTED}" font-size="10">More</text>')

    sep_y = leg_y + CELL + 14
    parts.append(f'<line x1="0" y1="{sep_y}" x2="{canvas_w}" y2="{sep_y}" stroke="{FRAME}" stroke-opacity="0.25"/>')

    # Get stats
    stats_data = data.get("stats", {})
    if "total_contributions" in stats_data:
        total = stats_data["total_contributions"]
        cs = stats_data.get("current_streak", 0)
        ls = stats_data.get("longest_streak", 0)
        best = stats_data.get("best_day", {"count": 0, "date": "-"})
        start_date = days[0]["date"] if days else "-"
        end_date = days[-1]["date"] if days else "-"
        rng = {"start": start_date, "end": end_date}
    else:
        st = compute_streaks(days)
        total = st["total"]
        cs = st["current_streak"]
        ls = st["longest_streak"]
        best = st["best_day"]
        rng = st["range"]

    ly = sep_y + 24
    parts.append(f'<text x="{PAD}" y="{ly}" font-size="13" fill="{GREEN}">'
                 f'<tspan font-weight="700">{total:,}</tspan>'
                 f'<tspan fill="{MUTED}"> contributions in the last year</tspan></text>')
    parts.append(f'<text x="{canvas_w - PAD}" y="{ly}" font-size="12" fill="{MUTED}" text-anchor="end">'
                 f'{rng["start"]} &#8594; {rng["end"]}</text>')
    ly += 24
    parts.append(f'<text x="{PAD}" y="{ly}" font-size="13" fill="{MUTED}">current streak '
                 f'<tspan fill="{ACCENT}" font-weight="700">{cs} days</tspan>'
                 f'<tspan fill="{MUTED}">   &#183;   longest </tspan>'
                 f'<tspan fill="{ACCENT}" font-weight="700">{ls} days</tspan></text>')
    parts.append(f'<text x="{canvas_w - PAD}" y="{ly}" font-size="12" fill="{MUTED}" text-anchor="end">'
                 f'best day <tspan fill="{GOLD}" font-weight="700">{best["count"]}</tspan> on {best["date"]}</text>')

    parts.append("</svg>")
    return "".join(parts)


def main() -> int:
    in_path = Path(IN_PATH)
    if not in_path.exists():
        print(f"Input file not found: {in_path}")
        return 1

    data = json.loads(in_path.read_text(encoding="utf-8"))
    svg = render(data)

    out_path = Path(OUT_PATH)
    out_path.write_text(svg, encoding="utf-8")
    print(f"Wrote heatmap SVG to: {out_path} ({len(svg)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
