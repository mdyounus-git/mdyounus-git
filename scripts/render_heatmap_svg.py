"""Draw data/contributions.json as an animated heatmap: weeks slide in diagonally once, then stay."""

import json
from datetime import date

from theme import GREEN, MUTED, NEON, PALETTE, ROOT, TEXT, window

SRC = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"
WIDTH, HEIGHT = 860, 230
CELL, GAP = 12, 3
X0, Y0 = 46, 66


def level(d, top):
    # GitHub's levels 0-4, with the year's busiest days lifted to the neon top end
    return 5 if top and d["count"] >= top else d["level"]


def main():
    data = json.loads(SRC.read_text(encoding="utf-8"))
    days = data["days"]
    counts = sorted((d["count"] for d in days if d["count"]), reverse=True)
    top = counts[max(len(counts) // 20, 0)] if len(counts) >= 10 else 0

    weeks, col = [], []
    for d in days:
        if col and date.fromisoformat(d["date"]).weekday() == 6:  # weeks start on Sunday
            weeks.append(col)
            col = []
        col.append(d)
    if col:
        weeks.append(col)

    parts = []
    for i, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(f'<text x="{X0 - 8}" y="{Y0 + i * (CELL + GAP) + 10}" font-size="10" fill="{MUTED}" text-anchor="end">{name}</text>')
    last_month = None
    for w, week in enumerate(weeks):
        first = date.fromisoformat(week[0]["date"])
        if first.month != last_month and first.day <= 7 and w < len(weeks) - 1:
            parts.append(f'<text x="{X0 + w * (CELL + GAP)}" y="{Y0 - 8}" font-size="10" fill="{MUTED}">{first.strftime("%b")}</text>')
            last_month = first.month
        x = X0 + w * (CELL + GAP)
        cells = []
        for d in week:
            row = (date.fromisoformat(d["date"]).weekday() + 1) % 7
            delay = 0.3 + (w + row) * 0.018
            cells.append(
                f'<rect x="{x}" y="{Y0 + row * (CELL + GAP)}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{PALETTE[level(d, top)]}" opacity="0"><title>{d["count"]} on {d["date"]}</title>'
                f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.35s" fill="freeze"/></rect>')
        parts.append("".join(cells))

    ly = Y0 + 7 * (CELL + GAP) + 14
    lx = WIDTH - 24 - 6 * (CELL + GAP) - 34
    parts.append(f'<text x="{lx - 6}" y="{ly + 10}" font-size="10" fill="{MUTED}" text-anchor="end">Less</text>')
    for i, c in enumerate(PALETTE):
        parts.append(f'<rect x="{lx + i * (CELL + GAP)}" y="{ly}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>')
    parts.append(f'<text x="{lx + 6 * (CELL + GAP) + 4}" y="{ly + 10}" font-size="10" fill="{MUTED}">More</text>')

    best = data.get("best_day") or {"count": 0, "date": "-"}
    best_txt = f'{best["count"]} on {date.fromisoformat(best["date"]).strftime("%b %d")}' if best["count"] else "—"
    stats = [("total", f'{data["total"]:,}'), ("longest streak", f'{data["longest_streak"]}d'),
             ("current streak", f'{data["current_streak"]}d'), ("best day", best_txt)]
    tspans = "".join(f'<tspan fill="{GREEN}">{k}</tspan><tspan fill="{TEXT}"> {v}</tspan><tspan fill="{MUTED}">{"   " if i < 3 else ""}</tspan>'
                     for i, (k, v) in enumerate(stats))
    parts.append(f'<text x="{X0 - 30}" y="{ly + 10}" font-size="11" xml:space="preserve">{tspans}</text>')
    parts.append(f'<text x="{X0 - 30}" y="46" font-size="12" fill="{NEON}">{data["total"]:,} contributions in the last year'
                 f'<tspan fill="{MUTED}">  ·  updated {data["fetched"]}</tspan></text>')
    OUT.write_text(window(WIDTH, HEIGHT, "~/contributions.sh", "\n".join(parts)), encoding="utf-8")
    print(f"wrote {OUT.name}: {len(weeks)} weeks")


if __name__ == "__main__":
    main()
