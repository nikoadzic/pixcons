#!/usr/bin/env python3
"""Write preview/gallery.html showing every built icon big, with a zoom slider
and a dark/light background toggle. Open it in a browser and refresh after
scripts/build.sh."""
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEME = ROOT / "Pixcons" / "scalable"

cards = []
for ctx in sorted(p for p in THEME.iterdir() if p.is_dir()):
    icons = sorted(p for p in ctx.glob("*.svg") if not p.is_symlink())
    if not icons:
        continue
    cards.append(f"<h2>{ctx.name} <small>{len(icons)}</small></h2><div class=grid>")
    for svg in icons:
        body = svg.read_text()
        cards.append(f"<figure>{body}<figcaption>{html.escape(svg.stem)}</figcaption>"
                     f"<div class=small>{body}{body}{body}{body}</div></figure>")
    cards.append("</div>")

page = f"""<!doctype html><meta charset=utf-8><title>Pixcons gallery</title>
<style>
:root {{ --z: 128px; --bg: #2a2e32; --fg: #eff0f1; }}
body {{ margin: 0; padding: 24px; background: var(--bg); color: var(--fg); font: 14px system-ui, sans-serif; }}
body.light {{ --bg: #fcfcfc; --fg: #232629; }}
header {{ display: flex; gap: 24px; align-items: center; margin-bottom: 16px; }}
h2 {{ margin: 24px 0 8px; font-size: 16px; }} h2 small {{ opacity: .5; font-weight: normal; }}
.grid {{ display: flex; flex-wrap: wrap; gap: 24px; }}
figure {{ margin: 0; text-align: center; }}
figure > svg {{ width: var(--z); height: var(--z); display: block; margin: 0 auto 6px; }}
figcaption {{ font-size: 12px; opacity: .8; word-break: break-all; max-width: var(--z); }}
.small {{ display: flex; gap: 10px; justify-content: center; align-items: end; margin-top: 6px; }}
.small svg:nth-child(1) {{ width: 16px; height: 16px; }} .small svg:nth-child(2) {{ width: 22px; height: 22px; }}
.small svg:nth-child(3) {{ width: 32px; height: 32px; }} .small svg:nth-child(4) {{ width: 48px; height: 48px; }}
</style>
<header><strong>Pixcons</strong>
<label>zoom <input type=range min=64 max=512 step=16 value=128 oninput="document.documentElement.style.setProperty('--z', this.value+'px')"></label>
<label><input type=checkbox onchange="document.body.classList.toggle('light', this.checked)"> light background</label>
</header>
{''.join(cards)}
"""
out = ROOT / "preview" / "gallery.html"
out.parent.mkdir(exist_ok=True)
out.write_text(page)
print(out)
