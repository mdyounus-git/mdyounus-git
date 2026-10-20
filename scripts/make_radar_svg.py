"""Two animated radar (spider) charts from the "radar" block in docs/profile.json:
programming on the left, security on the right. The shape grows out of the centre once,
then the glowing points keep a slow pulse.

python scripts/make_radar_svg.py   ->  radar-programming.svg, radar-security.svg
"""

import json
import math

from theme import BORDER, GREEN, MUTED, NEON, ROOT, TEXT, esc, window

PINK = "#f778ba"  # offensive axes; same pink as the neofetch colour blocks
WIDTH, HEIGHT = 430, 360
CX, CY, R = WIDTH / 2, 28 + 160, 92
RINGS = (0.25, 0.5, 0.75, 1.0)


def point(i, n, frac):
    a = -math.pi / 2 + 2 * math.pi * i / n
    return frac * R * math.cos(a), frac * R * math.sin(a), a


def poly(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def radar(spec):
    axes = spec["axes"]
    n = len(axes)
    parts = [f"""<defs>
<filter id="glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<radialGradient id="fill"><stop offset="0%" stop-color="{NEON}" stop-opacity="0.35"/><stop offset="100%" stop-color="{GREEN}" stop-opacity="0.12"/></radialGradient>
</defs>""", f'<g transform="translate({CX},{CY})">']

    # grid: rings and spokes
    for f in RINGS:
        ring = [point(i, n, f)[:2] for i in range(n)]
        dash = ' stroke-dasharray="3 3"' if f < 1 else ""
        parts.append(f'<polygon points="{poly(ring)}" fill="none" stroke="{BORDER}" stroke-width="1"{dash}/>')
    for i in range(n):
        x, y, _ = point(i, n, 1)
        parts.append(f'<line x1="0" y1="0" x2="{x:.1f}" y2="{y:.1f}" stroke="{BORDER}"/>')

    # the data shape, grown from the centre
    pts = [point(i, n, v / 100)[:2] for i, (_, v, _) in enumerate(axes)]
    grow = ('<animateTransform attributeName="transform" type="scale" from="0" to="1" begin="0.3s" dur="1.1s" '
            'calcMode="spline" keySplines="0.2 0.8 0.2 1" fill="freeze"/>')
    parts.append(f'<g transform="scale(0)">{grow}'
                 f'<polygon points="{poly(pts)}" fill="url(#fill)" stroke="{NEON}" stroke-width="2" stroke-linejoin="round"/>')
    for i, ((x, y), (_, _, side)) in enumerate(zip(pts, axes)):
        c = PINK if side == "off" else NEON
        delay = 1.4 + i * 0.15
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{c}" opacity="0">'
                     f'<animate attributeName="opacity" values="0;0.35;0.1;0.35" keyTimes="0;0.2;0.6;1" begin="{delay:.2f}s" dur="2.4s" repeatCount="indefinite"/></circle>'
                     f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{c}" filter="url(#glow)"/>')
    parts.append("</g>")

    # labels: long names wrap onto two lines, the value sits after the last word
    for i, (name, v, side) in enumerate(axes):
        x, y, a = point(i, n, 1)
        lx, ly = x + 14 * math.cos(a), y + 14 * math.sin(a)
        c, sn = math.cos(a), math.sin(a)
        anchor = "start" if c > 0.3 else "end" if c < -0.3 else "middle"
        words = name.upper().split(" ")
        lines = [name.upper()] if len(name) <= 12 or len(words) == 1 or anchor == "middle" else [" ".join(words[:-1]), words[-1]]
        top = ly - 6 - 13 * (len(lines) - 1) if sn < -0.5 else ly + 12 if sn > 0.5 else ly + 4 - 6.5 * (len(lines) - 1)
        col = PINK if side == "off" else GREEN
        spans = "".join(
            f'<tspan x="{lx:.1f}" y="{top + k * 13:.1f}" fill="{col}" font-weight="bold">{esc(t)}</tspan>'
            for k, t in enumerate(lines))
        parts.append(f'<text font-size="11" text-anchor="{anchor}" opacity="0">{spans}'
                     f'<tspan fill="{MUTED}"> {v}</tspan>'
                     f'<animate attributeName="opacity" from="0" to="1" begin="{0.9 + i * 0.12:.2f}s" dur="0.5s" fill="freeze"/></text>')
    parts.append("</g>")

    # caption, with a legend when the chart mixes defensive and offensive axes
    y = HEIGHT - 18
    if any(side == "off" for _, _, side in axes):
        lx = WIDTH - 104
        parts.append(f'<g font-size="10"><rect x="{lx}" y="40" width="8" height="8" rx="2" fill="{NEON}"/>'
                     f'<text x="{lx + 13}" y="47.5" fill="{TEXT}">defensive</text>'
                     f'<rect x="{lx}" y="55" width="8" height="8" rx="2" fill="{PINK}"/>'
                     f'<text x="{lx + 13}" y="62.5" fill="{TEXT}">offensive</text></g>')
    parts.append(f'<text x="24" y="{y}" font-size="11" fill="{MUTED}">{esc(spec["caption"])}</text>')
    return window(WIDTH, HEIGHT, spec["title"], "\n".join(parts))


def main():
    data = json.loads((ROOT / "docs" / "profile.json").read_text(encoding="utf-8"))["radar"]
    for key in ("programming", "security"):
        out = ROOT / f"radar-{key}.svg"
        out.write_text(radar(data[key]), encoding="utf-8")
        print(f"wrote {out.name}")


if __name__ == "__main__":
    main()
