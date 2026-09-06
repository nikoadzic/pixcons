#!/usr/bin/env python3
"""Turn a hand drawn PNG back into a .pix grid.

Draw a square PNG at icon size (16x16) in GIMP or any pixel editor with
palette/pixcons.gpl loaded, then import it:

  python3 scripts/png2pix.py drawing.png -o src/apps/whatsapp.pix

Every drawn pixel is snapped to the nearest colour in palette/*.hex. A colour
too far from every ramp is an error rather than a silent snap, because it means
a colour picked outside the palette. Alpha works the same way, nearly solid and
nearly gone are decided for you and reported, anything in between is an error
naming the pixel, because that is what a soft brush leaves behind and only you
know what it was meant to be. If the target already exists its comment header
is kept, so re-importing a tweaked drawing does not throw away the notes.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image

import pixbuild

ROOT = Path(__file__).resolve().parent.parent
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
MAX_DIST = 60.0  # euclidean RGB, past this it is not a palette colour any more
# A .pix grid has no alpha channel, every pixel ends up either drawn or not, so alpha has
# to be decided here. Near the ends the intent is obvious and the pixel is snapped and
# reported. In the middle band it is genuinely ambiguous, which is what a soft brush or a
# rescale produces, so that is an error naming the pixel rather than a guess.
ALPHA_SOLID = 192  # above this the pixel was meant to be drawn
ALPHA_GONE = 64    # below this it was meant to be empty


def nearest(rgb, palette):
    """Closest palette colour to an (r, g, b) tuple and its distance."""
    best, bd = None, None
    for col in palette:
        pr, pg, pb = (int(col[i:i + 2], 16) for i in (0, 2, 4))
        d = ((rgb[0] - pr) ** 2 + (rgb[1] - pg) ** 2 + (rgb[2] - pb) ** 2) ** 0.5
        if bd is None or d < bd:
            best, bd = col, d
    return best, bd


def keep_comment(path):
    """The leading # block of an existing .pix, so notes survive a re-import."""
    if not Path(path).exists():
        return ""
    out = []
    for line in Path(path).read_text().splitlines():
        if line.startswith("#"):
            out.append(line)
        elif line.strip():
            break
    return "\n".join(out) + "\n" if out else ""


def convert(img, palette):
    """(rows, legend) for a square RGBA image, or exit with what went wrong."""
    w, h = img.size
    if w != h:
        sys.exit(f"image is {w}x{h}, a .pix grid has to be square")
    partial, offpalette, snapped, ghosts, faded = [], [], {}, 0, 0
    legend, chars, rows = {".": None}, {}, []
    for y in range(h):
        row = ""
        for x in range(w):
            r, g, b, a = img.getpixel((x, y))
            if a < ALPHA_GONE:
                ghosts += a > 0
                row += "."
                continue
            if a <= ALPHA_SOLID:
                partial.append((x, y, a))
                row += "."
                continue
            faded += a < 255
            col, dist = nearest((r, g, b), palette)
            if dist > MAX_DIST:
                offpalette.append((x, y, f"{r:02x}{g:02x}{b:02x}"))
                row += "."
                continue
            if dist > 0:
                snapped.setdefault((f"{r:02x}{g:02x}{b:02x}", col), 0)
                snapped[(f"{r:02x}{g:02x}{b:02x}", col)] += 1
            if col not in chars:
                if len(chars) >= len(LETTERS):
                    sys.exit(f"more than {len(LETTERS)} colours, that is not pixel art")
                chars[col] = LETTERS[len(chars)]
                legend[chars[col]] = col
            row += chars[col]
        rows.append(row)

    if partial:
        show = ", ".join(f"({x},{y}) alpha {a}" for x, y, a in partial[:8])
        sys.exit(f"{len(partial)} pixels are half drawn and could go either way, use the "
                 f"pencil rather than a soft brush: {show}")
    if offpalette:
        show = ", ".join(f"({x},{y}) #{c}" for x, y, c in offpalette[:8])
        sys.exit(f"{len(offpalette)} pixels outside the palette: {show}")
    if ghosts:
        print(f"dropped {ghosts} barely visible pixels (alpha under {ALPHA_GONE})", file=sys.stderr)
    if faded:
        print(f"filled in {faded} nearly solid pixels (alpha over {ALPHA_SOLID})", file=sys.stderr)
    for (was, now), n in sorted(snapped.items()):
        print(f"snapped #{was} -> #{now} ({n} px)", file=sys.stderr)
    return rows, legend


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("png")
    p.add_argument("-o", "--out", required=True, help="target .pix path")
    p.add_argument("--palette", default=str(ROOT / "palette"))
    args = p.parse_args()

    palette = pixbuild.load_palette(args.palette)
    img = Image.open(args.png).convert("RGBA")
    rows, legend = convert(img, palette)
    comment = keep_comment(args.out)  # read before the open below truncates the file

    with open(args.out, "w") as f:
        f.write(comment)
        for ch, col in legend.items():
            if col:
                f.write(f"{ch} {col}\n")
        f.write("\n".join(rows) + "\n")
    used = ", ".join(f"#{c}" for c in legend.values() if c)
    print(f"{args.out}: {len(rows)}x{len(rows)}, {used}")


if __name__ == "__main__":
    main()
