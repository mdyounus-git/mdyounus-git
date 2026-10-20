"""Shared look for every SVG on the profile: a dark terminal window with neon green."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BG = "#0d1117"
BAR = "#161b22"
BORDER = "#30363d"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
GREEN = "#39d353"
NEON = "#69f0a0"
CYAN = "#58a6ff"

# contribution levels 0..4, plus a neon top end used for the busiest days
PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

FONT = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"


def window(width, height, title, body):
    """Wrap SVG body markup in a terminal window frame with a title bar."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="{FONT}">
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<path d="M0.5 28 V10.5 a10 10 0 0 1 10 -10 H{width - 10.5} a10 10 0 0 1 10 10 V28 Z" fill="{BAR}"/>
<line x1="0.5" y1="28" x2="{width - 0.5}" y2="28" stroke="{BORDER}"/>
<circle cx="18" cy="14.5" r="5" fill="#ff5f56"/><circle cx="35" cy="14.5" r="5" fill="#ffbd2e"/><circle cx="52" cy="14.5" r="5" fill="#27c93f"/>
<text x="{width / 2}" y="18.5" fill="{MUTED}" font-size="11" text-anchor="middle">{title}</text>
{body}
</svg>
"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
