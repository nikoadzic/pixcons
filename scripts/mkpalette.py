#!/usr/bin/env python3
"""Write palette/*.hex out as a GIMP palette so editors offer only legal colours.

  python3 scripts/mkpalette.py

Load the result in GIMP with Windows > Dockable Dialogs > Palettes, then import
palette/pixcons.gpl. Piskel and Lospec read the same format. build.sh runs this
so the .gpl never drifts from the .hex files.

Ramp comments in the .hex files become the swatch names, so a colour reads as
"green 2" rather than a bare hex string while drawing.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def swatches(palette_dir):
    """(hex, name) in file order, named after the ramp comment they sit under."""
    out, seen = [], set()
    for f in sorted(Path(palette_dir).glob("*.hex")):
        ramp, n = f.stem, 0
        for line in f.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                ramp, n = line.lstrip("# ").split(",")[0].strip(), 0
                continue
            col = line.lstrip("#").lower()
            n += 1
            if col not in seen:
                seen.add(col)
                out.append((col, f"{ramp} {n}"))
    return out


def main():
    palette_dir = sys.argv[1] if len(sys.argv) > 1 else ROOT / "palette"
    out = Path(palette_dir) / "pixcons.gpl"
    cols = swatches(palette_dir)
    lines = ["GIMP Palette", "Name: Pixcons", "Columns: 8", "#"]
    for col, name in cols:
        r, g, b = (int(col[i:i + 2], 16) for i in (0, 2, 4))
        lines.append(f"{r:3d} {g:3d} {b:3d}\t{name}")
    out.write_text("\n".join(lines) + "\n")
    print(f"{out}: {len(cols)} colours")


if __name__ == "__main__":
    main()
