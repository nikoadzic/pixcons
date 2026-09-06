#!/usr/bin/env python3
"""Turn .pix text grids into crisp SVG icons and zoomed PNG previews.

A .pix file has a legend (one "char hex" per line) followed by the grid,
one row per line. "." is transparent. Lines starting with # are comments.

  python3 scripts/pixbuild.py src/places/folder.pix --svg Pixcons/scalable/places
  python3 scripts/pixbuild.py src/**/*.pix --preview /tmp/previews --scale 8
"""
import argparse
import re
import sys
from pathlib import Path

LEGEND_RE = re.compile(r"^(\S)\s+#?([0-9a-fA-F]{6})\s*$")


def load_palette(path):
    """Load every .hex file in a directory, or a single .hex file."""
    files = sorted(Path(path).glob("*.hex")) if Path(path).is_dir() else [Path(path)]
    return {l.strip().lstrip("#").lower() for f in files for l in f.read_text().splitlines()
            if l.strip() and not l.startswith("#")}


def parse_pix(path):
    legend = {".": None}
    rows = []
    for raw in Path(path).read_text().splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        m = LEGEND_RE.match(line)
        if m and not rows:
            legend[m.group(1)] = m.group(2).lower()
            continue
        rows.append(line)
    size = len(rows)
    for y, row in enumerate(rows):
        if len(row) != size:
            sys.exit(f"{path}: row {y} has {len(row)} chars, expected {size}")
        for x, c in enumerate(row):
            if c not in legend:
                sys.exit(f"{path}: unknown char {c!r} at row {y} col {x}")
    return rows, legend, size


def check_palette(path, legend, palette):
    bad = [c for c in legend.values() if c and c not in palette]
    if bad:
        sys.exit(f"{path}: colors not in palette: {', '.join('#' + c for c in bad)}")


def to_svg(rows, legend, size):
    runs = {}
    for y, row in enumerate(rows):
        x = 0
        while x < size:
            c = row[x]
            col = legend[c]
            x0 = x
            while x < size and row[x] == c:
                x += 1
            if col:
                runs.setdefault(col, []).append(f"M{x0} {y}h{x - x0}v1h-{x - x0}z")
    body = "".join(f'<path fill="#{col}" d="{"".join(d)}"/>' for col, d in runs.items())
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
            f'viewBox="0 0 {size} {size}" shape-rendering="crispEdges">{body}</svg>\n')


def to_png(rows, legend, size, scale, bg, out):
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (size * scale, size * scale), bg)
    d = ImageDraw.Draw(img)
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            col = legend[c]
            if col:
                d.rectangle([x * scale, y * scale, (x + 1) * scale - 1, (y + 1) * scale - 1],
                            fill="#" + col)
    img.save(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pix", nargs="+", type=Path)
    ap.add_argument("--palette", type=Path, default=Path(__file__).resolve().parent.parent / "palette",
                    help="a .hex file or a directory of them, default palette/")
    ap.add_argument("--svg", type=Path, help="directory to write <name>.svg into")
    ap.add_argument("--preview", type=Path, help="directory to write <name>.png previews into")
    ap.add_argument("--edit", type=Path,
                    help="directory to write 1:1 transparent PNGs into, to draw on in a "
                         "pixel editor and read back with png2pix.py")
    ap.add_argument("--scale", type=int, default=8)
    ap.add_argument("--bg", default="#2a2e32", help="preview background, default Breeze Dark window")
    args = ap.parse_args()

    palette = load_palette(args.palette) if args.palette.exists() else None
    for src in args.pix:
        rows, legend, size = parse_pix(src)
        if palette:
            check_palette(src, legend, palette)
        if args.svg:
            args.svg.mkdir(parents=True, exist_ok=True)
            (args.svg / f"{src.stem}.svg").write_text(to_svg(rows, legend, size))
        if args.preview:
            args.preview.mkdir(parents=True, exist_ok=True)
            to_png(rows, legend, size, args.scale, args.bg, args.preview / f"{src.stem}.png")
        if args.edit:
            args.edit.mkdir(parents=True, exist_ok=True)
            to_png(rows, legend, size, 1, (0, 0, 0, 0), args.edit / f"{src.stem}.png")
        print(f"{src.name}: {size}x{size}, {len([c for c in legend.values() if c])} colors")


if __name__ == "__main__":
    main()
