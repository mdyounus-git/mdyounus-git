"""Scrape the public contribution calendar (no token needed) into data/contributions.json."""

import json
import re
from datetime import date

import requests
from bs4 import BeautifulSoup

from theme import ROOT

USER = "mdyounus-git"
OUT = ROOT / "data" / "contributions.json"


def main():
    html = requests.get(f"https://github.com/users/{USER}/contributions", timeout=30,
                        headers={"User-Agent": "profile-readme-bot"}).text
    soup = BeautifulSoup(html, "html.parser")
    tips = {t.get("for"): t.get_text(" ", strip=True) for t in soup.find_all("tool-tip")}
    days = []
    for td in soup.select("td[data-date]"):
        tip = tips.get(td.get("id"), "")
        m = re.match(r"([\d,]+) contribution", tip)
        days.append({"date": td["data-date"], "level": int(td.get("data-level", 0)),
                     "count": int(m.group(1).replace(",", "")) if m else 0})
    days.sort(key=lambda d: d["date"])

    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)
    current = 0
    today = date.today().isoformat()
    for d in reversed(days):
        if d["date"] == today and not d["count"]:
            continue  # today isn't over yet
        if not d["count"]:
            break
        current += 1
    best = max(days, key=lambda d: d["count"]) if days else None
    months = {}
    for d in days:
        months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["count"]

    data = {"user": USER, "fetched": today, "total": sum(d["count"] for d in days),
            "longest_streak": longest, "current_streak": current,
            "best_day": best, "months": months, "days": days}
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1), encoding="utf-8")
    print(f"{len(days)} days, {data['total']} contributions, longest streak {longest}, current {current}")


if __name__ == "__main__":
    main()
