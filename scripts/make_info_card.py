"""Neofetch-style info card whose lines fade and slide in on a stagger.

Edit the "card" list in docs/profile.json, then:  python scripts/make_info_card.py
STATIC=1 writes a frozen frame (no animation).
"""

import json
import os

from theme import CYAN, GREEN, MUTED, NEON, PALETTE, ROOT, TEXT, esc, window

OUT = ROOT / "info-card.svg"
WIDTH, HEIGHT = 490, 460
STATIC = os.environ.get("STATIC") == "1"

USER = "younus@github"
# one source of truth, shared with the live terminal in docs/
LINES = [tuple(r) for r in json.loads((ROOT / "docs" / "profile.json").read_text(encoding="utf-8"))["card"]]

X, Y0, STEP = 24, 62, 22
START, GAP = 0.5, 0.16


def anim(i):
    if STATIC:
        return "", ""
    b = START + i * GAP
    return ' opacity="0"', (
        f'<animate attributeName="opacity" from="0" to="1" begin="{b:.2f}s" dur="0.45s" fill="freeze"/>'
        f'<animateTransform attributeName="transform" type="translate" from="-12 0" to="0 0" begin="{b:.2f}s" dur="0.45s" fill="freeze"/>')


def main():
    parts = []
    hidden, a = anim(0)
    parts.append(f'<g{hidden}><text x="{X}" y="{Y0}" font-size="15" font-weight="bold">'
                 f'<tspan fill="{NEON}">younus</tspan><tspan fill="{TEXT}">@</tspan><tspan fill="{NEON}">github</tspan></text>{a}</g>')
    hidden, a = anim(1)
    parts.append(f'<g{hidden}><text x="{X}" y="{Y0 + 14}" font-size="13" fill="{MUTED}">{"-" * len(USER)}</text>{a}</g>')
    y = Y0 + 14 + STEP
    for i, (key, val) in enumerate(LINES, start=2):
        hidden, a = anim(i)
        label = f"{key}:" if key else ""
        parts.append(
            f'<g{hidden}><text x="{X}" y="{y}" font-size="13" xml:space="preserve">'
            f'<tspan fill="{GREEN}" font-weight="bold">{esc(label)}</tspan>'
            f'<tspan x="{X + 70}" fill="{TEXT}">{esc(val)}</tspan></text>{a}</g>')
        y += STEP
    # neofetch colour blocks
    hidden, a = anim(len(LINES) + 2)
    blocks = "".join(f'<rect x="{X + k * 28}" y="{y - 4}" width="24" height="14" rx="2" fill="{c}"/>'
                     for k, c in enumerate(PALETTE + [CYAN, "#f778ba"]))
    parts.append(f"<g{hidden}>{blocks}{a}</g>")
    # prompt with a blinking cursor
    y += 32
    hidden, a = anim(len(LINES) + 3)
    blink = "" if STATIC else '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/>'
    parts.append(f'<g{hidden}><text x="{X}" y="{y}" font-size="13"><tspan fill="{NEON}">{USER}</tspan>'
                 f'<tspan fill="{TEXT}"> ~ $ </tspan></text>'
                 f'<rect x="{X + 8 * 18.6:.1f}" y="{y - 11}" width="8" height="14" fill="{NEON}">{blink}</rect>'
                 f'<text x="{X + 8 * 18.6 + 18:.1f}" y="{y}" font-size="12" fill="{MUTED}">← click to open the live terminal</text>{a}</g>')
    OUT.write_text(window(WIDTH, HEIGHT, "~/neofetch", "\n".join(parts)), encoding="utf-8")
    print(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
