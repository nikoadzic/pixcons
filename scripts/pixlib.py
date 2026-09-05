"""Helpers for drawing icons in Python: cells are {(x, y): "hex"} dicts.

    from pixlib import *
    cells = rect(2, 2, 13, 13, "262b44")
    cells = outline(cells)               # selective 1px outline from the ramps
    save_pix(cells, "src/apps/foo.pix", "# foo\n")
    sheet([("a", cells)], "/tmp/a.png")   # zoomed on dark and light plus real sizes
"""
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pixbuild  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

# light to dark, from STYLE.md
RAMPS = [
    ["ffffff", "c0cbdc", "8b9bb4", "5a6988", "3a4466", "262b44", "181425"],
    ["fee761", "feae34", "f77622", "be4a2f", "733e39"],
    ["f6757a", "e43b44", "a22633", "3e2731"],
    ["ff0044", "b55088", "68386c", "3e2731"],
    ["63c74d", "3e8948", "265c42", "193c3e"],
    ["2ce8f5", "0099db", "124e89", "262b44"],
    ["ead4aa", "e8b796", "e4a672", "c28569", "d77643", "b86f50", "733e39", "3e2731"],
    ["8b94f7", "5865f2", "3c45a5"],
]
DARKEST = "181425"


def darker(col):
    """Next darker step of the first ramp containing col, or the darkest grey."""
    for ramp in RAMPS:
        if col in ramp:
            i = ramp.index(col)
            return ramp[i + 1] if i + 1 < len(ramp) else DARKEST
    return DARKEST


def lum(col):
    r, g, b = (int(col[i:i + 2], 16) for i in (0, 2, 4))
    return 0.299 * r + 0.587 * g + 0.114 * b


def outline(cells, size=16):
    """Add a 1px outline on transparent 4-neighbours of every fill, coloured by
    the darkest 'darker step' among the fills the outline pixel touches."""
    out = dict(cells)
    for (x, y), col in cells.items():
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n in cells or not (0 <= n[0] < size and 0 <= n[1] < size):
                continue
            cand = darker(col)
            if n not in out or lum(cand) < lum(out[n]):
                out[n] = cand
    return out


def rect(x0, y0, x1, y1, col, corners=0):
    """Filled rectangle, inclusive coordinates, optionally with corner pixels cut."""
    c = {(x, y): col for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}
    for i in range(corners):
        for j in range(corners - i):
            for p in ((x0 + j, y0 + i), (x1 - j, y0 + i), (x0 + j, y1 - i), (x1 - j, y1 - i)):
                c.pop(p, None)
    return c


def band(x0, y0, x1, y1, col, thick=2):
    """45 degree diagonal band from (x0, y0) to (x1, y1), thick pixels wide."""
    c = {}
    n = abs(x1 - x0)
    sx = 1 if x1 > x0 else -1
    sy = 1 if y1 > y0 else -1
    for i in range(n + 1):
        for t in range(thick):
            c[(x0 + i * sx + t, y0 + i * sy)] = col
    return c


def to_grid(cells, size=16):
    legend, chars = {".": None}, {}
    g = [["."] * size for _ in range(size)]
    for (x, y), col in cells.items():
        if col not in chars:
            chars[col] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[len(chars)]
            legend[chars[col]] = col
        g[y][x] = chars[col]
    return ["".join(r) for r in g], legend


def save_pix(cells, path, comment=""):
    g, legend = to_grid(cells)
    with open(path, "w") as f:
        f.write(comment)
        for ch, col in legend.items():
            if col:
                f.write(f"{ch} {col}\n")
        f.write("\n".join(g) + "\n")


def sheet(variants, out, scale=9, bgs=("#2a2e32", "#fcfcfc"), sizes=(16, 22, 32, 48)):
    """Comparison sheet: each variant zoomed on every background plus Plasma renders."""
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    cell, pad = 16 * scale + 6, 16
    W = pad + len(variants) * (cell + 10)
    H = pad + 30 + len(bgs) * (cell + 10) + max(sizes)
    im = Image.new("RGB", (W, H), bgs[0])
    d = ImageDraw.Draw(im)
    with tempfile.TemporaryDirectory() as tmp:
        for i, (label, cells) in enumerate(variants):
            g, legend = to_grid(cells)
            x = pad + i * (cell + 10)
            d.text((x, pad), label, fill="#eff0f1", font=font)
            for j, bg in enumerate(bgs):
                y = pad + 30 + j * (cell + 10)
                d.rectangle([x, y, x + cell - 1, y + cell - 1], fill=bg)
                pixbuild.to_png(g, legend, 16, scale, bg, f"{tmp}/z.png")
                im.paste(Image.open(f"{tmp}/z.png"), (x + 3, y + 3))
            svg = f"{tmp}/{i}.svg"
            Path(svg).write_text(pixbuild.to_svg(g, legend, 16))
            xx = x
            for s in sizes:
                subprocess.run(["ksvgtopng5", str(s), str(s), svg, f"{tmp}/r.png"], check=True)
                r = Image.open(f"{tmp}/r.png").convert("RGBA")
                im.paste(r, (xx, H - max(sizes) + (max(sizes) - s) // 2), r)
                xx += s + 12
    im.save(out)
    return out
