import argparse
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from xml.sax.saxutils import escape

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL_SIZE = 12
CELL_GAP = 4
WEEK_COUNT = 53
ROW_COUNT = 7
MARGIN_LEFT = 18
MARGIN_TOP = 28
MARGIN_RIGHT = 24
MARGIN_BOTTOM = 96
LABEL_FONT = "12px 'Inter', 'Segoe UI', sans-serif"
FOOTER_FONT = "11px 'Inter', 'Segoe UI', sans-serif"
LEGEND_FONT = "11px 'Inter', 'Segoe UI', sans-serif"


def iso_to_date(value: str) -> date:
    return datetime.fromisoformat(value).date()


def build_heatmap(days: list[dict]) -> tuple[list[list[dict | None]], dict]:
    day_map = {iso_to_date(item["date"]): item for item in days}
    min_date = min(day_map)
    max_date = max(day_map)
    start_date = min_date - timedelta(days=(min_date.weekday() + 1) % 7)
    total_days = (max_date - start_date).days + 1
    week_count = (total_days + 6) // 7
    week_count = max(week_count, WEEK_COUNT)

    grid: list[list[dict | None]] = [
        [None for _ in range(ROW_COUNT)]
        for _ in range(week_count)
    ]

    cur = start_date
    for day_index in range(week_count * ROW_COUNT):
        week = day_index // ROW_COUNT
        row = day_index % ROW_COUNT
        if cur > max_date:
            cur += timedelta(days=1)
            continue
        if cur in day_map:
            grid[week][row] = day_map[cur]
        cur += timedelta(days=1)

    stats = {
        "total": sum(item["count"] for item in days),
        "best_day": max(days, key=lambda entry: entry["count"]) if days else {"count": 0, "date": None},
        "username": days[0].get("username") if days and "username" in days[0] else None,
    }
    return grid, stats


def render_svg(grid: list[list[dict | None]], stats: dict, username: str | None) -> str:
    width = MARGIN_LEFT + MARGIN_RIGHT + len(grid) * (CELL_SIZE + CELL_GAP) - CELL_GAP
    height = MARGIN_TOP + MARGIN_BOTTOM + ROW_COUNT * (CELL_SIZE + CELL_GAP) - CELL_GAP
    footer_text = f"{stats['total']} contributions in the last year"
    title_text = f"GitHub contributions" if username is None else f"{username} contributions"

    rows = []
    for row_index in range(ROW_COUNT):
        y = MARGIN_TOP + row_index * (CELL_SIZE + CELL_GAP)
        delay = row_index * 0.05
        for col_index, week in enumerate(grid):
            x = MARGIN_LEFT + col_index * (CELL_SIZE + CELL_GAP)
            cell = week[row_index]
            if cell is None:
                color = PALETTE[0]
                count = 0
                tooltip = "No data"
            else:
                level = int(cell.get("level", "0"))
                level = min(max(level, 0), len(PALETTE) - 1)
                color = PALETTE[level]
                count = cell.get("count", 0)
                tooltip = f"{count} contribution{'s' if count != 1 else ''} on {escape(cell['date'])}"
            animation_delay = delay + col_index * 0.002
            rows.append(
                f"    <g class=\"cell\" style=\"animation-delay: {animation_delay:.3f}s\">\n"
                f"      <title>{escape(tooltip)}</title>\n"
                f"      <rect x=\"{x}\" y=\"{y}\" width=\"{CELL_SIZE}\" height=\"{CELL_SIZE}\" rx=\"3\" ry=\"3\" fill=\"{color}\" />\n"
                f"    </g>\n"
            )

    legend_blocks = []
    legend_x = MARGIN_LEFT
    legend_y = height - MARGIN_BOTTOM + 28
    for index, color in enumerate(PALETTE):
        legend_blocks.append(
            f"    <rect x=\"{legend_x + index * 26}\" y=\"{legend_y}\" width=\"12\" height=\"12\" rx=\"3\" fill=\"{color}\" />\n"
        )
    legend_text = (
        f"    <text x=\"{MARGIN_LEFT - 10}\" y=\"{legend_y + 10}\" fill=\"#768390\" font-family=\"{LEGEND_FONT}\" text-anchor=\"end\">Less</text>\n"
        f"    <text x=\"{MARGIN_LEFT + len(PALETTE) * 26}\" y=\"{legend_y + 10}\" fill=\"#768390\" font-family=\"{LEGEND_FONT}\">More</text>\n"
    )

    return (
        f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        f"<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 {width} {height}\" "
        f"width=\"{width}\" height=\"{height}\" xml:space=\"preserve\">\n"
        f"  <style>\n"
        f"    .background {{ fill: #0f172a; }}\n"
        f"    .title {{ fill: #cbd5e1; font-family: 'Inter', 'Segoe UI', sans-serif; font-size: 14px; font-weight: 600; }}\n"
        f"    .footer {{ fill: #94a3b8; font-family: 'Inter', 'Segoe UI', sans-serif; font-size: 11px; }}\n"
        f"    .cell {{ opacity: 0; transform: translateY(-10px); animation: slideIn 0.35s ease forwards; }}\n"
        f"    text {{ user-select: none; }}\n"
        f"    @keyframes slideIn {{ from {{ opacity: 0; transform: translateY(-10px); }} to {{ opacity: 1; transform: translateY(0); }} }}\n"
        f"  </style>\n"
        f"  <rect x=\"0\" y=\"0\" width=\"100%\" height=\"100%\" fill=\"#010409\" rx=\"16\" />\n"
        f"  <text x=\"{MARGIN_LEFT}\" y=\"18\" class=\"title\">{escape(title_text)}</text>\n"
        f"  <g>\n"
        + "".join(rows)
        + f"  </g>\n"
        f"  <g>\n"
        f"{''.join(legend_blocks)}"
        f"{legend_text}"
        f"  </g>\n"
        f"  <text x=\"{MARGIN_LEFT}\" y=\"{height - 20}\" class=\"footer\">{escape(footer_text)}</text>\n"
        f"</svg>\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a GitHub-style contribution heatmap SVG from JSON data.")
    parser.add_argument(
        "--input",
        default="data/contributions.json",
        help="Input JSON path (default: data/contributions.json)",
    )
    parser.add_argument(
        "--output",
        default="contrib-heatmap.svg",
        help="Output SVG path (default: contrib-heatmap.svg)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return 1

    data = json.loads(input_path.read_text(encoding="utf-8"))
    days = data.get("days", [])
    if not days:
        print("No contribution day data found in JSON.")
        return 2

    username = data.get("username")
    grid, stats = build_heatmap(days)
    svg = render_svg(grid, stats, username)

    output_path = Path(args.output)
    output_path.write_text(svg, encoding="utf-8")
    print(f"Wrote heatmap SVG to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
