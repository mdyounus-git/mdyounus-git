"""Turn the spider avatar into an ASCII-art SVG whose rows type themselves in once, then freeze.

Run once (needs pillow + numpy):  python scripts/make_ascii_svg.py
"""

import numpy as np
from PIL import Image

from theme import GREEN, NEON, ROOT, esc, window

SRC = ROOT / "scripts" / "source-avatar.jpg"
OUT = ROOT / "spider-ascii.svg"

RAMP = " .`:-=+*cs#%@"  # sparse -> dense; the spider is bright, so bright maps to dense
COLS = 52
CHAR_W, LINE_H = 6.2, 10.6  # monospace cell; height/width ~1.7
WIDTH, HEIGHT = 370, 460
ROW_DUR, ROW_GAP, START = 0.28, 0.07, 0.4


def ascii_rows():
    img = Image.open(SRC).convert("L")
    a = np.asarray(img, dtype=np.float32) / 255.0
    ys, xs = np.where(a > 0.35)
    pad = 10
    box = (max(xs.min() - pad, 0), max(ys.min() - pad, 0),
           min(xs.max() + pad, a.shape[1]), min(ys.max() + pad, a.shape[0]))
    crop = img.crop(box)
    rows = round(COLS * crop.height / crop.width * CHAR_W / LINE_H)
    small = np.asarray(crop.resize((COLS, rows), Image.LANCZOS), dtype=np.float32) / 255.0
    idx = np.clip((small * (len(RAMP) - 1)).round().astype(int), 0, len(RAMP) - 1)
    return ["".join(RAMP[i] for i in row).rstrip() for row in idx]


def main():
    rows = ascii_rows()
    block_w = COLS * CHAR_W
    x0 = (WIDTH - block_w) / 2
    y0 = 28 + (HEIGHT - 28 - 30 - len(rows) * LINE_H) / 2
    parts = ["<defs>"]
    for i in range(len(rows)):
        begin = START + i * ROW_GAP
        y = y0 + i * LINE_H
        parts.append(
            f'<clipPath id="r{i}"><rect x="{x0:.1f}" y="{y:.1f}" width="0" height="{LINE_H}">'
            f'<animate attributeName="width" from="0" to="{block_w:.1f}" begin="{begin:.2f}s" dur="{ROW_DUR}s" fill="freeze"/>'
            f"</rect></clipPath>")
    parts.append("</defs>")
    for i, row in enumerate(rows):
        if not row.strip():
            continue
        begin = START + i * ROW_GAP
        y = y0 + i * LINE_H
        parts.append(
            f'<text x="{x0:.1f}" y="{y + LINE_H * 0.8:.1f}" font-size="10" fill="{GREEN}" xml:space="preserve" '
            f'textLength="{len(row) * CHAR_W:.1f}" lengthAdjust="spacingAndGlyphs" clip-path="url(#r{i})">{esc(row)}</text>')
        # block cursor that runs along the row while it is being typed
        parts.append(
            f'<rect x="{x0:.1f}" y="{y:.1f}" width="{CHAR_W:.1f}" height="{LINE_H}" fill="{NEON}" opacity="0">'
            f'<set attributeName="opacity" to="0.9" begin="{begin:.2f}s" dur="{ROW_DUR}s"/>'
            f'<animate attributeName="x" from="{x0:.1f}" to="{x0 + block_w:.1f}" begin="{begin:.2f}s" dur="{ROW_DUR}s" fill="freeze"/>'
            f"</rect>")
    done = START + len(rows) * ROW_GAP + ROW_DUR
    parts.append(
        f'<text x="{WIDTH / 2}" y="{HEIGHT - 16}" font-size="11" fill="#8b949e" text-anchor="middle" opacity="0">'
        f'with great power comes great responsibility'
        f'<animate attributeName="opacity" from="0" to="1" begin="{done:.2f}s" dur="0.8s" fill="freeze"/></text>')
    OUT.write_text(window(WIDTH, HEIGHT, "~/spider.txt", "\n".join(parts)), encoding="utf-8")
    print(f"wrote {OUT.name}: {len(rows)} rows x {COLS} cols")


if __name__ == "__main__":
    main()
