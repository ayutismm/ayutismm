import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup


HTML_URL = "https://github.com/users/{username}/contributions"


def infer_username() -> str | None:
    username = os.environ.get("GITHUB_USERNAME") or os.environ.get("GITHUB_USER")
    if username:
        return username.strip()

    try:
        url = subprocess.check_output(["git", "remote", "get-url", "origin"], text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

    match = re.search(r"github\.com[:/](?P<user>[^/]+)/", url)
    return match.group("user") if match else None


def fetch_contributions_html(username: str) -> str:
    url = HTML_URL.format(username=username)
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.text


def parse_tooltip_count(text: str) -> int:
    if not text:
        return 0
    if "no contributions" in text.lower():
        return 0
    match = re.search(r"(\d+)\s+contribution", text.lower())
    if match:
        return int(match.group(1))
    return 0


def parse_contributions(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    tooltips = {
        tooltip.get("for"): tooltip.get_text(" ", strip=True)
        for tooltip in soup.find_all(lambda tag: tag.name.lower() == "tool-tip" or tag.name.lower() == "tooltip")
        if tooltip.get("for")
    }

    days = []
    for cell in soup.find_all(attrs={"data-date": True, "data-level": True}):
        date_value = cell.get("data-date")
        if not date_value:
            continue
        level = cell.get("data-level", "0")
        count = 0
        cell_id = cell.get("id")
        if cell_id and cell_id in tooltips:
            count = parse_tooltip_count(tooltips[cell_id])
        days.append({"date": date_value, "count": count, "level": level})

    return sorted(days, key=lambda item: item["date"])


def compute_stats(days: list[dict]) -> dict:
    total = sum(day["count"] for day in days)
    monthly_totals: dict[str, int] = {}
    for day in days:
        month = day["date"][:7]
        monthly_totals[month] = monthly_totals.get(month, 0) + day["count"]

    best_day = max(days, key=lambda item: item["count"]) if days else {"date": None, "count": 0, "level": "0"}

    longest_streak = 0
    current_streak = 0
    streak = 0
    for day in days:
        if day["count"] > 0:
            streak += 1
            longest_streak = max(longest_streak, streak)
        else:
            streak = 0

    for day in reversed(days):
        if day["count"] > 0:
            current_streak += 1
        else:
            break

    return {
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "monthly_totals": monthly_totals,
        "day_count": len(days),
    }


def make_output(username: str, days: list[dict], stats: dict) -> dict:
    return {
        "username": username,
        "fetched_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source_url": HTML_URL.format(username=username),
        "days": days,
        "stats": stats,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch GitHub contribution heatmap data from the public contributions page.")
    parser.add_argument("--username", help="GitHub username to fetch contributions for")
    parser.add_argument(
        "--output",
        default="data/contributions.json",
        help="Output JSON path (default: data/contributions.json)",
    )
    args = parser.parse_args()

    username = args.username or infer_username()
    if not username:
        print("Error: GitHub username not provided. Set --username, GITHUB_USERNAME, or configure a git origin URL.")
        return 1

    html = fetch_contributions_html(username)
    days = parse_contributions(html)
    if not days:
        print("No contribution day cells found in the fetched page. Verify the username and page structure.")
        return 2

    stats = compute_stats(days)
    output = make_output(username, days, stats)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote {len(days)} contribution days to {output_path}")
    print(f"Stats: total={stats['total_contributions']}, current_streak={stats['current_streak']}, longest_streak={stats['longest_streak']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
