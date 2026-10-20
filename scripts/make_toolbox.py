"""The toolbox panel: rows of tool tiles under a heading, from "toolbox" in docs/profile.json.

Brand logos come from scripts/tool_icons.json (Simple Icons, CC0) in their official
colours, drawn like app icons: the brand colour fills a rounded square and the logo sits
on it in white. Tools without a logo there get a hand-drawn icon from GLYPHS on their own
brand colour (BRAND); anything unknown gets a two-letter monogram on the theme green.
"""

import json

from theme import BAR, BORDER, GREEN, MUTED, NEON, ROOT, TEXT, esc, window

OUT = ROOT / "toolbox.svg"
WIDTH = 860
PAD = 24
TILE_H, ROW_LABEL, ROW_GAP = 80, 22, 14
LOGOS = json.loads((ROOT / "scripts" / "tool_icons.json").read_text(encoding="utf-8"))["icons"]

# names people write -> icon key
ALIASES = {
    "microsoftsentinel": "sentinel", "azuresentinel": "sentinel",
    "elk": "elastic", "elasticsearch": "elastic", "elasticsiem": "elastic", "kibana": "elastic",
    "mitreattck": "attack", "mitreattack": "attack", "attck": "attack",
    "volatility3": "volatility", "burp": "burpsuite", "kali": "kalilinux", "bash": "gnubash",
}

S = 'fill="none" stroke="{c}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"'
# 24x24 line icons for tools Simple Icons does not carry
GLYPHS = {
    "sentinel": f'<path d="M12 2 L20 5 V11 C20 16.5 16.5 20.5 12 22 C7.5 20.5 4 16.5 4 11 V5 Z" {S}/><path d="M8.5 12 L11 14.5 L15.5 9.5" {S}/>',
    "wazuh": f'<path d="M12 2 L20 5 V11 C20 16.5 16.5 20.5 12 22 C7.5 20.5 4 16.5 4 11 V5 Z" {S}/><path d="M7.5 8.5 L9.5 15.5 L12 10.5 L14.5 15.5 L16.5 8.5" {S}/>',
    "suricata": f'<circle cx="12" cy="12" r="9.5" {S}/><circle cx="12" cy="12" r="5.5" {S}/><path d="M12 12 L18.7 5.3" {S}/><circle cx="12" cy="12" r="1.4" fill="{{c}}"/>',
    "zeek": f'<path d="M2 12 H6 L8.5 6 L12 18 L15 9 L17 12 H22" {S}/>',
    "autopsy": f'<circle cx="10" cy="10" r="6.5" {S}/><circle cx="10" cy="10" r="1.8" {S}/><path d="M15 15 L21 21" fill="none" stroke="{{c}}" stroke-width="2.6" stroke-linecap="round"/>',
    "volatility": f'<rect x="2.5" y="7" width="19" height="9" rx="1.5" {S}/><path d="M6 10 V13 M9.5 10 V13 M13 10 V13 M16.5 10 V13 M5 16 V19 M9 16 V19 M15 16 V19 M19 16 V19" {S}/>',
    "velociraptor": f'<circle cx="12" cy="12" r="8" {S}/><circle cx="12" cy="12" r="3.5" {S}/><path d="M12 1.5 V5.5 M12 18.5 V22.5 M1.5 12 H5.5 M18.5 12 H22.5" {S}/>',
    "yara": f'<path d="M8 3 C5 3 5.5 6 5.5 8.5 C5.5 10.5 4.5 12 3 12 C4.5 12 5.5 13.5 5.5 15.5 C5.5 18 5 21 8 21" {S}/><path d="M16 3 C19 3 18.5 6 18.5 8.5 C18.5 10.5 19.5 12 21 12 C19.5 12 18.5 13.5 18.5 15.5 C18.5 18 19 21 16 21" {S}/><path d="M9.5 9 L14.5 15 M14.5 9 L9.5 15" {S}/>',
    "cyberchef": f'<path d="M7 13.5 C3.5 13.5 3 8.5 6.5 8 C7 4.5 11 3.5 12.5 6 C14 3.5 18 4.5 17.5 8 C21 8.5 20.5 13.5 17 13.5 Z" {S}/><path d="M7 13.5 V20 H17 V13.5 M7 17 H17" {S}/>',
    "nmap": f'<path d="M1.5 12 C4.5 6.5 8 4.5 12 4.5 C16 4.5 19.5 6.5 22.5 12 C19.5 17.5 16 19.5 12 19.5 C8 19.5 4.5 17.5 1.5 12 Z" {S}/><circle cx="12" cy="12" r="3.6" {S}/><circle cx="12" cy="12" r="1.2" fill="{{c}}"/>',
    "attack": f'<rect x="2.5" y="3" width="19" height="18" rx="1.5" {S}/><path d="M2.5 9 H21.5 M2.5 15 H21.5 M8.8 3 V21 M15.2 3 V21" {S}/><rect x="9.6" y="9.8" width="4.8" height="4.4" fill="{{c}}"/>',
}


# brand colours for the hand-drawn icons (taken from each product's own logo)
BRAND = {
    "sentinel": "#0078D4",      # Microsoft Azure blue
    "wazuh": "#3595F9",
    "suricata": "#EF8B23",
    "zeek": "#2E86C1",
    "autopsy": "#4A90D9",
    "volatility": "#E8432E",
    "velociraptor": "#E85E26",  # Rapid7 orange
    "yara": "#394EFF",          # VirusTotal blue
    "cyberchef": "#4AC1DF",
    "nmap": "#0E83CD",
    "attack": "#D7262E",        # MITRE ATT&CK red
}


def key(name):
    k = "".join(ch for ch in name.lower() if ch.isalnum())
    return ALIASES.get(k, k)


def lum(hex_colour):
    """Relative luminance (WCAG) of a #rrggbb colour."""
    h = hex_colour.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def icon(name, cx, cy, box=42, size=24):
    """An app-style icon: the brand colour as the rounded background, the logo on top in
    white (or near-black when the brand colour is light), like the tool's own app icon."""
    k = key(name)
    if k in LOGOS:
        bg = LOGOS[k].get("hex", NEON)
    elif k in GLYPHS:
        bg = BRAND.get(k, NEON)
    else:
        bg = NEON
    fg = "#0d1117" if lum(bg) > 0.45 else "#ffffff"
    x, y = cx - box / 2, cy - box / 2
    # a hairline keeps very dark brand squares (e.g. Splunk's black) visible on the dark tile
    edge = f' stroke="{BORDER}"' if lum(bg) < 0.03 else ""
    tile = f'<rect x="{x:.1f}" y="{y:.1f}" width="{box}" height="{box}" rx="10" fill="{bg}"{edge}/>'
    s = size / 24
    at = f'translate({cx - size / 2:.1f} {cy - size / 2:.1f}) scale({s:.3f})'
    if k in LOGOS:
        return tile + f'<g transform="{at}"><path d="{LOGOS[k]["d"]}" fill="{fg}"/></g>'
    if k in GLYPHS:
        return tile + f'<g transform="{at}">{GLYPHS[k].format(c=fg)}</g>'
    mono = "".join(w[0] for w in name.split()[:2]).upper() if " " in name else name[:2].title()
    return tile + (f'<text x="{cx}" y="{cy + 6}" font-size="16" font-weight="bold" fill="{fg}" '
                   f'text-anchor="middle">{esc(mono)}</text>')


def height(spec):
    return 28 + 52 + len(spec["rows"]) * (ROW_LABEL + TILE_H + ROW_GAP) + 4


def render(p):
    spec = p["toolbox"]
    H = height(spec)
    parts = [f'<text x="{PAD}" y="58" font-size="15" font-weight="bold" fill="{NEON}">{esc(spec["heading"])}</text>',
             f'<text x="{WIDTH - PAD}" y="58" font-size="12" fill="{MUTED}" text-anchor="end">$ ls {esc(spec["title"])}</text>']
    y = 80
    n = 0
    for row in spec["rows"]:
        tools = row["tools"]
        parts.append(f'<text x="{PAD}" y="{y + 12}" font-size="11" fill="{GREEN}">── {esc(row["label"])}</text>'
                     f'<line x1="{PAD + 26 + len(row["label"]) * 6.6 + 8:.1f}" y1="{y + 8}" x2="{WIDTH - PAD}" y2="{y + 8}" stroke="{BORDER}"/>')
        y += ROW_LABEL
        cols = max(len(tools), 8)               # short rows keep the same tile size, left-aligned
        slot = (WIDTH - 2 * PAD) / cols
        tw = slot - 10
        for i, name in enumerate(tools):
            x = PAD + i * slot + 5
            cx = x + tw / 2
            b = 0.3 + n * 0.06
            n += 1
            parts.append(
                f'<g opacity="0"><rect x="{x:.1f}" y="{y}" width="{tw:.1f}" height="{TILE_H}" rx="8" fill="{BAR}" stroke="{BORDER}"/>'
                f'{icon(name, cx, y + 31)}'
                f'<text x="{cx:.1f}" y="{y + TILE_H - 12}" font-size="{min(10.5, (tw - 10) / (len(name) * 0.62)):.1f}" fill="{TEXT}" text-anchor="middle">{esc(name)}</text>'
                f'<animate attributeName="opacity" from="0" to="1" begin="{b:.2f}s" dur="0.4s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" from="0 8" to="0 0" begin="{b:.2f}s" dur="0.4s" fill="freeze"/></g>')
        y += TILE_H + ROW_GAP
    return window(WIDTH, H, f"~/{spec['title'].strip('~/')}", "\n".join(parts))


if __name__ == "__main__":
    from profile import load
    OUT.write_text(render(load()), encoding="utf-8")
    print(f"wrote {OUT.name}")
