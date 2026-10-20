"""Neofetch-style info card whose lines fade and slide in on a stagger.

Edit the "card" list in docs/profile.json, then:  python scripts/build.py
Long values wrap onto a continuation line and the spacing tightens to fit more
rows, so the card keeps its size and look whatever you put in it.
STATIC=1 writes a frozen frame (no animation).
"""

import os

from theme import CYAN, GREEN, MUTED, NEON, PALETTE, ROOT, TEXT, esc, window

OUT = ROOT / "info-card.svg"
WIDTH, HEIGHT = 490, 460
STATIC = os.environ.get("STATIC") == "1"

X, Y0 = 24, 62
KEY_W = 70                       # label column
CHAR_W = 7.6                     # 13px monospace
WRAP = int((WIDTH - X - KEY_W - 12) / CHAR_W)   # characters that fit in the value column
STEP_MAX, BOTTOM = 22, HEIGHT - 20
START, GAP = 0.5, 0.16


def wrap(text, width=WRAP):
    """Split a value into lines, preferring the ' · ' separators, then spaces."""
    if len(text) <= width:
        return [text]
    out, line = [], ""
    for sep in (" · ", " "):
        if sep in text:
            words = text.split(sep)
            break
    else:
        return [text[i:i + width] for i in range(0, len(text), width)]
    for w in words:
        cand = f"{line}{sep}{w}" if line else w
        if len(cand) <= width:
            line = cand
        else:
            if line:
                out.append(line)
            while len(w) > width:          # a single very long word
                out.append(w[:width])
                w = w[width:]
            line = w
    if line:
        out.append(line)
    return out


def layout(card):
    """(row count, [(label, text)], step) for the given card rows after wrapping."""
    rows = []
    for key, val in card:
        for k, part in enumerate(wrap(val)):
            rows.append((key if k == 0 else "", part))
    # header + dashes take the top; colour blocks + prompt take the bottom (about 2 steps + 32px)
    step = min(STEP_MAX, (BOTTOM - (Y0 + 14) - 32) / (len(rows) + 1))
    return len(rows), rows, step


def anim(i):
    if STATIC:
        return "", ""
    b = START + i * GAP
    return ' opacity="0"', (
        f'<animate attributeName="opacity" from="0" to="1" begin="{b:.2f}s" dur="0.45s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" from="-12 0" to="0 0" begin="{b:.2f}s" dur="0.45s" fill="freeze"/>')


def render(p):
    handle = p["handle"]
    user = f"{handle}@github"
    _, rows, step = layout(p["card"])
    parts = []
    hidden, a = anim(0)
    parts.append(f'<g{hidden}><text x="{X}" y="{Y0}" font-size="15" font-weight="bold">'
                 f'<tspan fill="{NEON}">{esc(handle)}</tspan><tspan fill="{TEXT}">@</tspan><tspan fill="{NEON}">github</tspan></text>{a}</g>')
    hidden, a = anim(1)
    parts.append(f'<g{hidden}><text x="{X}" y="{Y0 + 14}" font-size="13" fill="{MUTED}">{"-" * len(user)}</text>{a}</g>')
    y = Y0 + 14 + step
    for i, (key, val) in enumerate(rows, start=2):
        hidden, a = anim(i)
        label = f"{key}:" if key else ""
        parts.append(
            f'<g{hidden}><text x="{X}" y="{y:.1f}" font-size="13" xml:space="preserve">'
            f'<tspan fill="{GREEN}" font-weight="bold">{esc(label)}</tspan>'
            f'<tspan x="{X + KEY_W}" fill="{TEXT}">{esc(val)}</tspan></text>{a}</g>')
        y += step
    # neofetch colour blocks
    hidden, a = anim(len(rows) + 2)
    blocks = "".join(f'<rect x="{X + k * 28}" y="{y - 4:.1f}" width="24" height="14" rx="2" fill="{c}"/>'
                     for k, c in enumerate(PALETTE + [CYAN, "#f778ba"]))
    parts.append(f"<g{hidden}>{blocks}{a}</g>")
    # prompt with a blinking cursor
    y += 32
    hidden, a = anim(len(rows) + 3)
    blink = "" if STATIC else '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/>'
    cx = X + len(f"{user} ~ $ ") * CHAR_W
    parts.append(f'<g{hidden}><text x="{X}" y="{y:.1f}" font-size="13" xml:space="preserve"><tspan fill="{NEON}">{esc(user)}</tspan>'
                 f'<tspan fill="{TEXT}"> ~ $ </tspan></text>'
                 f'<rect x="{cx:.1f}" y="{y - 11:.1f}" width="8" height="14" fill="{NEON}">{blink}</rect>'
                 f'<text x="{cx + 18:.1f}" y="{y:.1f}" font-size="12" fill="{MUTED}">← click to open the live terminal</text>{a}</g>')
    return window(WIDTH, HEIGHT, "~/neofetch", "\n".join(parts))


def main():
    from profile import load
    OUT.write_text(render(load()), encoding="utf-8")
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
