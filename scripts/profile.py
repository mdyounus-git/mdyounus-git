"""Load docs/profile.json and check it before anything is drawn from it.

Every generator goes through load(). If the file is broken (a missing comma, a
score of 150, a line too long for the card), the build stops with a plain-English
list of what to fix, nothing gets committed, and the live profile keeps showing
the last good version.

python scripts/profile.py   ->  just check the file
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "docs" / "profile.json"

CARD_KEY_MAX = 7       # the label column on the info card is 7 characters wide
CARD_VALUE_MAX = 90    # longer values are wrapped onto a second line; this caps the total
CARD_ROWS_MAX = 16     # rows the card can hold after wrapping (see make_info_card.py)
RADAR_AXES = (3, 10)
RADAR_NAME_MAX = 22
SIDES = ("", "def", "off")
TOOL_ROWS_MAX, TOOLS_PER_ROW, TOOL_NAME_MAX = 4, 10, 13


class ProfileError(Exception):
    pass


def _str(errs, d, key, where, required=True, max_len=None):
    v = d.get(key)
    if v is None:
        if required:
            errs.append(f'{where}: "{key}" is missing')
        return
    if not isinstance(v, str) or not v.strip():
        errs.append(f'{where}: "{key}" must be some text in quotes')
    elif max_len and len(v) > max_len:
        errs.append(f'{where}: "{key}" is {len(v)} characters, keep it to {max_len}')


def _str_list(errs, v, where, required=True):
    if v is None:
        if required:
            errs.append(f"{where} is missing")
        return
    if not isinstance(v, list) or not all(isinstance(x, str) and x.strip() for x in v):
        errs.append(f'{where} must be a list of texts, like ["one", "two"]')


def check(d):
    errs = []
    if not isinstance(d, dict):
        return ["the file must be one { ... } object"]
    for key in ("name", "handle", "github", "role", "uni", "location"):
        _str(errs, d, key, "profile")
    _str(errs, d, "since", "profile", required=False)
    _str(errs, d, "portrait_caption", "profile", required=False, max_len=50)
    if isinstance(d.get("handle"), str) and not d["handle"].replace("-", "").replace("_", "").isalnum():
        errs.append('profile: "handle" should be one word (letters, numbers, - or _), it is shown as handle@github')
    _str_list(errs, d.get("about"), '"about"')
    _str_list(errs, d.get("interests"), '"interests"', required=False)
    _str_list(errs, d.get("tools"), '"tools"', required=False)
    _str_list(errs, d.get("hobbies"), '"hobbies"', required=False)

    skills = d.get("skills", {})
    if not isinstance(skills, dict):
        errs.append('"skills" must be groups like {"Security": ["..."], "Scripting": ["..."]}')
    else:
        for group, items in skills.items():
            _str_list(errs, items, f'"skills" -> "{group}"')

    socials = d.get("socials", {})
    if not isinstance(socials, dict):
        errs.append('"socials" must look like {"LinkedIn": "https://..."}')
    else:
        for name, url in socials.items():
            if not isinstance(url, str) or (url and not url.startswith("https://")):
                errs.append(f'"socials" -> "{name}" must be a full link starting with https:// (or "" until you have one)')
        buttons = d.get("buttons", [])
        if not isinstance(buttons, list) or not all(isinstance(b, str) for b in buttons):
            errs.append('"buttons" must be a list of names from "socials", like ["LinkedIn", "Portfolio"]')
        else:
            for b in buttons:
                if b not in socials:
                    errs.append(f'"buttons" lists "{b}" but "socials" has no "{b}" entry')
                elif len(b) > 14:
                    errs.append(f'"buttons": "{b}" is too long for a button, keep it to 14 characters')
            if len(buttons) > 5:
                errs.append('"buttons": at most 5 fit in one row')

    card = d.get("card")
    if not isinstance(card, list) or not card:
        errs.append('"card" is missing; it is the list of ["Label", "value"] rows on the info card')
    else:
        for n, row in enumerate(card, 1):
            where = f'"card" row {n}'
            if not (isinstance(row, list) and len(row) == 2 and all(isinstance(x, str) for x in row)):
                errs.append(f'{where} must be ["Label", "value"] (use "" as the label to continue the row above)')
                continue
            key, val = row
            if len(key) > CARD_KEY_MAX:
                errs.append(f'{where}: label "{key}" is longer than {CARD_KEY_MAX} characters')
            if not val.strip():
                errs.append(f"{where}: the value is empty")
            elif len(val) > CARD_VALUE_MAX:
                errs.append(f"{where}: the value is {len(val)} characters, keep it to {CARD_VALUE_MAX} (or split it into two rows)")
        if not errs:
            from make_info_card import layout  # late import: the card knows its own geometry
            rows = layout(card)[0]
            if rows > CARD_ROWS_MAX:
                errs.append(f'"card" needs {rows} lines after wrapping long values, but the card holds {CARD_ROWS_MAX}; remove or shorten some rows')

    tb = d.get("toolbox")
    if tb is not None:
        if not isinstance(tb, dict):
            errs.append('"toolbox" must be an object with title, heading and rows')
        else:
            _str(errs, tb, "title", '"toolbox"', max_len=30)
            _str(errs, tb, "heading", '"toolbox"', max_len=60)
            rows = tb.get("rows")
            if not isinstance(rows, list) or not 1 <= len(rows) <= TOOL_ROWS_MAX:
                errs.append(f'"toolbox": "rows" needs 1 to {TOOL_ROWS_MAX} rows')
            else:
                for n, row in enumerate(rows, 1):
                    where = f'"toolbox" row {n}'
                    if not isinstance(row, dict):
                        errs.append(f'{where} must look like {{"label": "...", "tools": ["..."]}}')
                        continue
                    _str(errs, row, "label", where, max_len=40)
                    tools = row.get("tools")
                    _str_list(errs, tools, f'{where} "tools"')
                    if isinstance(tools, list):
                        if not 1 <= len(tools) <= TOOLS_PER_ROW:
                            errs.append(f'{where} has {len(tools)} tools; a row fits 1 to {TOOLS_PER_ROW}')
                        for t in tools:
                            if isinstance(t, str) and len(t) > TOOL_NAME_MAX:
                                errs.append(f'{where}: "{t}" is longer than {TOOL_NAME_MAX} characters, use a short name')

    radar = d.get("radar", {})
    if not isinstance(radar, dict):
        errs.append('"radar" must look like {"tech": {...}, "security": {...}}')
    else:
        if len(radar) > 2:
            errs.append(f'"radar" has {len(radar)} charts; the profile shows two side by side')
        for name, spec in radar.items():
            where = f'"radar" -> "{name}"'
            if not isinstance(spec, dict):
                errs.append(f"{where} must be an object with title, caption and axes")
                continue
            _str(errs, spec, "title", where, max_len=40)
            _str(errs, spec, "caption", where, max_len=60)
            axes = spec.get("axes")
            if not isinstance(axes, list) or not RADAR_AXES[0] <= len(axes) <= RADAR_AXES[1]:
                errs.append(f"{where}: \"axes\" needs between {RADAR_AXES[0]} and {RADAR_AXES[1]} skills")
                continue
            for n, ax in enumerate(axes, 1):
                if not (isinstance(ax, list) and len(ax) in (2, 3)):
                    errs.append(f'{where} axis {n} must be ["Skill", 80] or ["Skill", 80, "def"/"off"]')
                    continue
                label, score = ax[0], ax[1]
                side = ax[2] if len(ax) == 3 else ""
                if not isinstance(label, str) or not label.strip() or len(label) > RADAR_NAME_MAX:
                    errs.append(f"{where} axis {n}: the name must be text of at most {RADAR_NAME_MAX} characters")
                if isinstance(score, bool) or not isinstance(score, (int, float)) or not 0 <= score <= 100:
                    errs.append(f'{where} axis {n} ("{label}"): the score must be a number from 0 to 100')
                if side not in SIDES:
                    errs.append(f'{where} axis {n} ("{label}"): the third value must be "def", "off" or left out')
    return errs


def load(path=SRC):
    """Return the checked profile, or raise ProfileError listing every problem."""
    try:
        text = Path(path).read_text(encoding="utf-8-sig")  # -sig: tolerate a BOM from Windows editors
    except OSError as e:
        raise ProfileError(f"cannot read {path}: {e}")
    try:
        d = json.loads(text)
    except json.JSONDecodeError as e:
        line = text.splitlines()[e.lineno - 1] if 0 < e.lineno <= len(text.splitlines()) else ""
        hint = " (often a missing or extra comma, or a missing quote)"
        raise ProfileError(f"docs/profile.json is not valid JSON at line {e.lineno}, column {e.colno}: {e.msg}{hint}\n    {line.strip()}")
    errs = check(d)
    if errs:
        raise ProfileError("docs/profile.json needs fixing:\n" + "\n".join(f"  - {e}" for e in errs))
    # normalise optional parts so every renderer can rely on them
    d.setdefault("since", "")
    for k in ("interests", "tools", "hobbies"):
        d.setdefault(k, [])
    d.setdefault("skills", {})
    d.setdefault("socials", {})
    d.setdefault("buttons", [])
    d.setdefault("radar", {})
    for spec in d["radar"].values():
        spec["axes"] = [[a[0], a[1], a[2] if len(a) == 3 else ""] for a in spec["axes"]]
    return d


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        p = load()
    except ProfileError as e:
        print(e)
        sys.exit(1)
    print(f"profile.json OK: {len(p['card'])} card rows, radars: {', '.join(p['radar']) or 'none'}")
