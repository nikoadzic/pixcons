#!/usr/bin/env python3
"""Render a review sheet for one or more .pix files: big zoom on dark and light
backgrounds plus Plasma's own renderer at 16, 22, 32 and 48 px.

  python3 scripts/review.py src/apps/com.spotify.Client.pix
  -> preview/review-com.spotify.Client.png
"""
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pixbuild  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SCALE, PAD = 20, 24
BGS = [("Breeze Dark", "#2a2e32"), ("light", "#fcfcfc")]


def render_real(svg, size):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as t:
        subprocess.run(["ksvgtopng5", str(size), str(size), str(svg), t.name], check=True)
        return Image.open(t.name).convert("RGBA")


def main():
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    out_dir = ROOT / "preview"
    out_dir.mkdir(exist_ok=True)
    for src in map(Path, sys.argv[1:]):
        rows, legend, size = pixbuild.parse_pix(src)
        big = size * SCALE
        W = PAD * 3 + big * 2
        H = PAD * 3 + big + 80
        sheet = Image.new("RGB", (W, H), "#2a2e32")
        d = ImageDraw.Draw(sheet)
        d.text((PAD, PAD // 2), src.stem, fill="#eff0f1", font=font)
        with tempfile.TemporaryDirectory() as tmp:
            for i, (label, bg) in enumerate(BGS):
                x = PAD + i * (big + PAD)
                pixbuild.to_png(rows, legend, size, SCALE, bg, f"{tmp}/big.png")
                sheet.paste(Image.open(f"{tmp}/big.png"), (x, PAD))
            svg = Path(tmp) / "icon.svg"
            svg.write_text(pixbuild.to_svg(rows, legend, size))
            for i, (label, bg) in enumerate(BGS):
                x0 = PAD + i * (big + PAD)
                d.rectangle([x0, PAD + big + 12, x0 + big - 1, PAD + big + 76], fill=bg)
                xx = x0 + 16
                for s in (16, 22, 32, 48):
                    im = render_real(svg, s)
                    sheet.paste(im, (xx, PAD + big + 12 + (64 - s) // 2), im)
                    xx += s + 20
        out = out_dir / f"review-{src.stem}.png"
        sheet.save(out)
        print(out)


if __name__ == "__main__":
    main()
