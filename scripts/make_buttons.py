"""Link buttons in the terminal theme, one SVG per name in "buttons" (docs/profile.json).

Each is a small dark key with the site's own logo in its own colours (Instagram keeps
its gradient) and a label; the green underline draws in once. Known names: LinkedIn,
Instagram, Portfolio, GitHub, Email, YouTube, X/Twitter; anything else gets a >_ glyph.
"""

import json

from theme import BG, BORDER, FONT, GREEN, MUTED, NEON, ROOT, TEXT, esc

LOGOS = json.loads((ROOT / "scripts" / "tool_icons.json").read_text(encoding="utf-8"))["icons"]

OUT_DIR = ROOT / "buttons"
HEIGHT = 40
CHAR_W = 8.4  # 13px bold monospace

# 16x16 icons drawn with strokes in the theme green
ICONS = {
    "linkedin": '<rect x="1" y="1" width="14" height="14" rx="3" fill="none" stroke="{c}" stroke-width="1.6"/>'
                '<text x="8" y="12" font-size="9" font-weight="bold" fill="{c}" text-anchor="middle">in</text>',
    "instagram": '<rect x="1" y="1" width="14" height="14" rx="4" fill="none" stroke="{c}" stroke-width="1.6"/>'
                 '<circle cx="8" cy="8" r="3.2" fill="none" stroke="{c}" stroke-width="1.6"/><circle cx="12" cy="4" r="1" fill="{c}"/>',
    "portfolio": '<circle cx="8" cy="8" r="6.6" fill="none" stroke="{c}" stroke-width="1.5"/>'
                 '<ellipse cx="8" cy="8" rx="2.8" ry="6.6" fill="none" stroke="{c}" stroke-width="1.3"/>'
                 '<line x1="1.4" y1="8" x2="14.6" y2="8" stroke="{c}" stroke-width="1.3"/>',
    "github": '<circle cx="8" cy="8" r="6.6" fill="none" stroke="{c}" stroke-width="1.6"/>'
              '<path d="M6 14 v-2.4 q-2.4 .4 -2.8 -1.6 M10 14 v-2.6 q0 -1 -.6 -1.4 q2.6 -.3 2.6 -2.8 q0 -1 -.7 -1.7 q.3 -1 0 -1.8 q-1 0 -1.8 .7 a5 5 0 0 0 -3 0 q-.8 -.7 -1.8 -.7 q-.3 .8 0 1.8 q-.7 .7 -.7 1.7 q0 2.5 2.6 2.8" fill="none" stroke="{c}" stroke-width="1.2"/>',
    "email": '<rect x="1" y="3" width="14" height="10" rx="2" fill="none" stroke="{c}" stroke-width="1.6"/>'
             '<path d="M1.5 4 L8 9 L14.5 4" fill="none" stroke="{c}" stroke-width="1.4"/>',
    "youtube": '<rect x="1" y="3" width="14" height="10" rx="3" fill="none" stroke="{c}" stroke-width="1.6"/>'
               '<path d="M6.5 5.6 L10.6 8 L6.5 10.4 Z" fill="{c}"/>',
    "x": '<path d="M2 2 L14 14 M14 2 L2 14" stroke="{c}" stroke-width="1.8" stroke-linecap="round"/>',
}
ICONS["twitter"] = ICONS["x"]
# real logos (24x24 paths) scaled to 16px, in brand colours; X is white, as on dark backgrounds
IG_GRADIENT = ('<defs><linearGradient id="ig" x1="0" y1="1" x2="1" y2="0">'
               '<stop offset="0" stop-color="#FEDA75"/><stop offset="0.3" stop-color="#FA7E1E"/>'
               '<stop offset="0.6" stop-color="#D62976"/><stop offset="0.8" stop-color="#962FBF"/>'
               '<stop offset="1" stop-color="#4F5BD5"/></linearGradient></defs>')
BRAND_LOGOS = {
    "linkedin": ("linkedin", "#0A66C2"),
    "instagram": ("instagram", "url(#ig)"),
    "x": ("x", "#f0f6fc"),
    "twitter": ("x", "#f0f6fc"),
}
GLYPH_COLOURS = {"portfolio": NEON, "github": "#f0f6fc", "email": "#EA4335", "youtube": "#FF0000"}
FALLBACK = '<text x="0" y="12" font-size="12" font-weight="bold" fill="{c}">&gt;_</text>'


def slug(name):
    return "".join(ch for ch in name.lower() if ch.isalnum()) or "link"


def button(name, width):
    k = slug(name)
    if k in BRAND_LOGOS and BRAND_LOGOS[k][0] in LOGOS:
        logo, fill = BRAND_LOGOS[k]
        icon = (IG_GRADIENT if fill == "url(#ig)" else "") +             f'<g transform="scale({16 / 24:.4f})"><path d="{LOGOS[logo]["d"]}" fill="{fill}"/></g>'
    else:
        icon = ICONS.get(k, FALLBACK).format(c=GLYPH_COLOURS.get(k, NEON))
    label_x = 16 + 16 + 10
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{HEIGHT}" viewBox="0 0 {width} {HEIGHT}" font-family="{FONT}">
<rect x="0.5" y="0.5" width="{width - 1}" height="{HEIGHT - 1}" rx="8" fill="{BG}" stroke="{BORDER}"/>
<g transform="translate(16 {HEIGHT / 2 - 8})">{icon}</g>
<text x="{label_x}" y="{HEIGHT / 2 + 4.5}" font-size="13" font-weight="bold" fill="{TEXT}">{esc(name)}</text>
<text x="{width - 16}" y="{HEIGHT / 2 + 4.5}" font-size="13" fill="{MUTED}" text-anchor="end">↗</text>
<line x1="12" y1="{HEIGHT - 4}" x2="12" y2="{HEIGHT - 4}" stroke="{GREEN}" stroke-width="2" stroke-linecap="round">
<animate attributeName="x2" from="12" to="{width - 12}" begin="0.4s" dur="0.9s" calcMode="spline" keySplines="0.2 0.8 0.2 1" fill="freeze"/></line>
</svg>
"""


def render(p):
    """Write one SVG per button; return [(name, file, url)] in order."""
    names = p["buttons"]
    width = int(16 + 16 + 10 + max((len(n) for n in names), default=6) * CHAR_W + 34)
    OUT_DIR.mkdir(exist_ok=True)
    keep, out = set(), []
    for name in names:
        f = OUT_DIR / f"{slug(name)}.svg"
        f.write_text(button(name, width), encoding="utf-8")
        keep.add(f.name)
        out.append((name, f"buttons/{f.name}", p["socials"].get(name, "")))
    for old in OUT_DIR.glob("*.svg"):   # buttons removed from the list
        if old.name not in keep:
            old.unlink()
    return out


if __name__ == "__main__":
    from profile import load
    for name, path, url in render(load()):
        print(f"wrote {path}  ->  {url or '(no link yet)'}")
