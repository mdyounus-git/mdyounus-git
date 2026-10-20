# Editing the profile

Everything on the profile comes from **one file: [`docs/profile.json`](docs/profile.json)**.
Edit it on GitHub (open the file → pencil icon → *Commit changes*). About a minute later
the profile updates by itself in the same theme: info card, radars, toolbox, buttons,
README and the live terminal.

Don't edit `README.md` or the `.svg` files by hand. They are rebuilt on every change and
your edits would be overwritten.

## What you can change

| In `profile.json` | Shows up as |
|---|---|
| `card` | the rows of the info card, as `["Label", "value"]`. Labels up to 7 letters. Long values wrap by themselves. Use `""` as the label to continue the row above |
| `radar` → `axes` | radar chart points, as `["Skill", 0-100]`. Add `"off"` as a third value to draw it pink (offensive). 3 to 10 skills per chart |
| `toolbox` → `rows` | tool tiles, up to 10 per row and 4 rows. Known tools get their logo in brand colours; others get a two-letter tile |
| `socials` + `buttons` | the buttons at the bottom. Put a link in `socials` (e.g. `"Portfolio": "https://..."`) and the button becomes clickable. `""` shows the button without a link |
| `skills`, `tools`, `hobbies`, `interests`, `about` | what the live terminal prints for those commands |
| `portrait_caption` (optional) | the line under the ASCII portrait |
| `portrait_title` (optional) | the title bar of the portrait window, e.g. `"~/spider.txt"` (default `"~/avatar.txt"`) |

Your **profile picture** is picked up by itself: change it on GitHub and the ASCII portrait
is redrawn from the new picture on the next run (every 3 hours, or after any edit; to see it
at once, open **Actions → Update profile art → Run workflow**). Any picture works: a photo
or a logo, light or dark background, transparent PNG, GIF, square or not. If the new picture
is not a spider any more, change `portrait_title` and `portrait_caption` to match it.

The contribution heatmap is built from one small image per day, so hovering any day shows
its count, e.g. *"3 contributions on Mon, 05 Oct 2026"*. Its files live in `hm/`.

## If something is wrong

The build checks `profile.json` before drawing anything. A typo, such as a missing comma, a
score of 150, or a label that is too long, makes that run **fail without changing your
profile**: the live page keeps its last good version. GitHub emails you that the
*Update profile art* run failed; open it under the **Actions** tab, and the log says in plain
words what to fix and where. Fix it, commit again, and it goes through.

To go back to an earlier version entirely, the tag `profile-v1` marks the profile before
the radar charts were added, and `profile-v2-before-fixes` the profile before the heatmap
hover, the new section order and the any-picture portrait.

## Running it yourself (optional)

```bash
pip install -r scripts/requirements.txt
python scripts/profile.py          # only check profile.json
python scripts/build.py            # rebuild everything
python scripts/build.py --offline  # rebuild without downloading avatar/contributions
```
