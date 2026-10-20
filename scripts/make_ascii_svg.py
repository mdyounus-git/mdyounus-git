"""Turn the GitHub avatar into an ASCII-art SVG whose rows type themselves in once, then freeze.

build.py downloads the current avatar into scripts/source-avatar.jpg first, so a new
profile picture shows up here by itself. Works for any picture: dark or light
background, logo or photo, square or tall (needs pillow + numpy).
"""

import numpy as np
from PIL import Image, ImageOps

from theme import GREEN, NEON, ROOT, esc, window

SRC = ROOT / "scripts" / "source-avatar.jpg"
OUT = ROOT / "spider-ascii.svg"

RAMP = " .`:-=+*cs#%@"  # sparse -> dense; the subject is made bright, so bright maps to dense
COLS = 52
CHAR_W, LINE_H = 6.2, 10.6  # monospace cell; height/width ~1.7
WIDTH, HEIGHT = 370, 460
MAX_ROWS = int((HEIGHT - 28 - 30 - 8) / LINE_H)  # what fits above the caption
CAPTION = "with great power comes great responsibility"
ROW_DUR, ROW_GAP, START = 0.28, 0.07, 0.4


def ascii_rows():
    """Return (rows of text, column count)."""
    img = ImageOps.exif_transpose(Image.open(SRC)).convert("L")
    a = np.asarray(img, dtype=np.float32) / 255.0
    # the background is whatever the border mostly is; flip so the subject is bright on dark
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    bg = float(np.median(border))
    if bg > 0.5:
        a, bg = 1.0 - a, 1.0 - bg
    ys, xs = np.where(np.abs(a - bg) > 0.25)
    if len(xs) < a.size * 0.01:          # nothing stands out: use the whole picture
        x0, y0, x1, y1 = 0, 0, a.shape[1], a.shape[0]
    else:
        pad = int(0.03 * max(a.shape))
        x0, y0 = max(xs.min() - pad, 0), max(ys.min() - pad, 0)
        x1, y1 = min(xs.max() + pad + 1, a.shape[1]), min(ys.max() + pad + 1, a.shape[0])
    crop = a[y0:y1, x0:x1]
    lo, hi = np.percentile(crop, 2), np.percentile(crop, 98)
    crop = np.clip((crop - lo) / max(hi - lo, 1e-3), 0, 1)   # stretch contrast for dull photos
    h, w = crop.shape
    cols = COLS
    rows = max(1, round(cols * h / w * CHAR_W / LINE_H))
    if rows > MAX_ROWS:                  # tall picture: keep the height, narrow the width
        rows = MAX_ROWS
        cols = max(12, round(rows * w / h * LINE_H / CHAR_W))
    small = Image.fromarray((crop * 255).astype(np.uint8)).resize((cols, rows), Image.LANCZOS)
    v = np.asarray(small, dtype=np.float32) / 255.0
    idx = np.clip((v * (len(RAMP) - 1)).round().astype(int), 0, len(RAMP) - 1)
    return ["".join(RAMP[i] for i in row).rstrip() for row in idx], cols


def main():
    from profile import load
    caption = load().get("portrait_caption", CAPTION)
    rows, cols = ascii_rows()
    # the live terminal (docs/) prints the same art for `neofetch` and `banner`
    (ROOT / "docs" / "spider.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")
    block_w = cols * CHAR_W
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
        f'{esc(caption)}'
        f'<animate attributeName="opacity" from="0" to="1" begin="{done:.2f}s" dur="0.8s" fill="freeze"/></text>')
    OUT.write_text(window(WIDTH, HEIGHT, "~/spider.txt", "\n".join(parts)), encoding="utf-8")
    print(f"wrote {OUT.name}: {len(rows)} rows x {cols} cols")


if __name__ == "__main__":
    main()
