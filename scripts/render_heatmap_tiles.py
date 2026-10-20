"""Draw the contribution heatmap as small tiles so every day shows its count on hover.

GitHub shows README images as plain <img> tags: the <title> tooltips inside an SVG never
appear, and image maps and styles are stripped. What it does keep is the title="" of
each <img>. So the heatmap is cut into one tiny image per day (plus a header and a
footer image) and README.md lays them out as a grid, each day with its own title.

How the grid holds together on GitHub (measured on the profile page):
- tiles sit inside an <h6>, whose line height (14.875px) is smaller than a tile, so
  rows touch with no gaps; align="top" removes the space under each line;
- every tile has the same percentage width, so the grid scales with the page and each
  row is exactly one line (the next tile does not fit and wraps);
- only ~30 distinct tile files exist (one per colour level, label and edge), so the
  browser downloads each once however many days use it.

Tiles are drawn on an opaque background so GitHub's light theme shows no seams.
"""

import html
from datetime import date

from render_heatmap_svg import level, load
from theme import BAR, BG, BORDER, FONT, GREEN, MUTED, NEON, PALETTE, ROOT, TEXT

OUT = ROOT / "hm"
U, TH = 15, 15.6          # tile width and height; a little taller than wide so rows never part
GUTTER = 2                 # tiles for the Mon/Wed/Fri labels
TOP_H, BOT_H = 64, 40
LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}


def svg(w, h, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">\n{body}\n</svg>\n')


def tile(body=""):
    return svg(U, TH, f'<rect width="{U}" height="{TH}" fill="{BG}"/>{body}')


def cell(fill):
    return tile(f'<rect x="1.5" y="1.8" width="12" height="12" rx="2.5" fill="{fill}"/>')


def label(row, part):
    """The two gutter tiles of a row; the label text is drawn across both and clipped by each."""
    body = ""
    if part == 0:
        body += f'<line x1="0.5" y1="0" x2="0.5" y2="{TH}" stroke="{BORDER}"/>'
    if row in LABELS:
        x = GUTTER * U - 3 - part * U
        body += f'<text x="{x}" y="11" font-size="9" fill="{MUTED}" text-anchor="end">{LABELS[row]}</text>'
    return tile(body)


def top(width, data, weeks):
    parts = [
        f'<path d="M0.5 {TOP_H} V10.5 a10 10 0 0 1 10 -10 H{width - 10.5} a10 10 0 0 1 10 10 V{TOP_H} Z" '
        f'fill="{BG}" stroke="{BORDER}"/>',
        f'<path d="M1 28 V10.5 a9.5 9.5 0 0 1 9.5 -9.5 H{width - 10.5} a9.5 9.5 0 0 1 9.5 9.5 V28 Z" fill="{BAR}"/>',
        f'<line x1="0.5" y1="28" x2="{width - 0.5}" y2="28" stroke="{BORDER}"/>',
        '<circle cx="18" cy="14.5" r="5" fill="#ff5f56"/><circle cx="35" cy="14.5" r="5" fill="#ffbd2e"/>'
        '<circle cx="52" cy="14.5" r="5" fill="#27c93f"/>',
        f'<text x="{width / 2}" y="18.5" fill="{MUTED}" font-size="11" text-anchor="middle">~/contributions.sh</text>',
        f'<text x="16" y="46" font-size="12" fill="{NEON}">{data["total"]:,} contributions in the last year'
        f'<tspan fill="{MUTED}">  ·  updated {data["fetched"]}  ·  hover a day for its count</tspan></text>',
    ]
    last_month = None
    for w, week in enumerate(weeks):
        first = date.fromisoformat(week[0]["date"])
        if first.month != last_month and first.day <= 7 and w < len(weeks) - 1:
            parts.append(f'<text x="{GUTTER * U + w * U + 1.5}" y="{TOP_H - 5}" font-size="10" fill="{MUTED}">'
                         f'{first.strftime("%b")}</text>')
            last_month = first.month
    return svg(width, TOP_H, "\n".join(parts))


def bottom(width, data):
    parts = [f'<path d="M0.5 0 V{BOT_H - 10.5} a10 10 0 0 0 10 10 H{width - 10.5} a10 10 0 0 0 10 -10 V0" '
             f'fill="{BG}" stroke="{BORDER}"/>']
    ly = 10
    lx = width - 24 - 6 * U - 34
    parts.append(f'<text x="{lx - 6}" y="{ly + 10}" font-size="10" fill="{MUTED}" text-anchor="end">Less</text>')
    for i, c in enumerate(PALETTE):
        parts.append(f'<rect x="{lx + i * U}" y="{ly}" width="12" height="12" rx="2.5" fill="{c}"/>')
    parts.append(f'<text x="{lx + 6 * U + 4}" y="{ly + 10}" font-size="10" fill="{MUTED}">More</text>')
    best = data.get("best_day") or {"count": 0, "date": "-"}
    best_txt = f'{best["count"]} on {date.fromisoformat(best["date"]).strftime("%b %d")}' if best["count"] else "—"
    stats = [("total", f'{data["total"]:,}'), ("longest streak", f'{data["longest_streak"]}d'),
             ("current streak", f'{data["current_streak"]}d'), ("best day", best_txt)]
    tspans = "".join(f'<tspan fill="{GREEN}">{k}</tspan><tspan fill="{TEXT}"> {v}</tspan>'
                     f'<tspan fill="{MUTED}">{"   " if i < 3 else ""}</tspan>'
                     for i, (k, v) in enumerate(stats))
    parts.append(f'<text x="16" y="{ly + 10}" font-size="11" xml:space="preserve">{tspans}</text>')
    return svg(width, BOT_H, "\n".join(parts))


def tooltip(d):
    n = d["count"]
    when = date.fromisoformat(d["date"]).strftime("%a, %d %b %Y")
    what = "No contributions" if n == 0 else ("1 contribution" if n == 1 else f"{n:,} contributions")
    return f"{what} on {when}"


def main(wrap):
    """Write the tiles into hm/ and return the README markup for the whole heatmap.

    wrap is the opening tag put around each tile: an <a name> anchor, so a click does
    nothing while the hover title still shows."""
    data, weeks, top_n = load()
    cols = GUTTER + len(weeks) + 1
    width = cols * U
    OUT.mkdir(exist_ok=True)
    files = {"top.svg": top(width, data, weeks), "bottom.svg": bottom(width, data),
             "empty.svg": tile(), "edge.svg": tile(f'<line x1="{U - 0.5}" y1="0" x2="{U - 0.5}" y2="{TH}" stroke="{BORDER}"/>')}
    for i, c in enumerate(PALETTE):
        files[f"c{i}.svg"] = cell(c)
    for row in range(7):
        for part in range(GUTTER):
            files[f"l{part}-{row}.svg"] = label(row, part)
    for name, text in files.items():
        (OUT / name).write_text(text, encoding="utf-8")
    for old in OUT.glob("*.svg"):
        if old.name not in files:
            old.unlink()

    # floor to 3 decimals so a full row never adds up to more than 100% and spills over
    pct = int(100_000 / cols) / 1000
    total = f"{pct * cols:.3f}%"
    def img(name, width, title=""):
        t = html.escape(title, quote=True)
        return (f'{wrap}<img src="./hm/{name}" width="{width}" align="top" '
                f'alt="{t}" title="{t}" /></a>')

    grid = {}
    for w, week in enumerate(weeks):
        for d in week:
            grid[(w, (date.fromisoformat(d["date"]).weekday() + 1) % 7)] = d
    out = [img("top.svg", total, f'{data["total"]:,} contributions in the last year')]
    for row in range(7):
        out += [img(f"l{part}-{row}.svg", f"{pct}%") for part in range(GUTTER)]
        for w in range(len(weeks)):
            d = grid.get((w, row))
            out.append(img(f"c{level(d, top_n)}.svg", f"{pct}%", tooltip(d)) if d else img("empty.svg", f"{pct}%"))
        out.append(img("edge.svg", f"{pct}%"))
    out.append(img("bottom.svg", total, "Contribution totals and streaks"))
    print(f"wrote hm/: {len(files)} tiles for {len(weeks)} weeks")
    # one line, no spaces: whitespace between the tiles would open gaps in the grid
    return "<h6>" + "".join(out) + "</h6>"


if __name__ == "__main__":
    main('<a name="heatmap">')
