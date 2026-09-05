# Pixcons style guide

Every icon follows these rules so the set reads as one family.

## Canvas

- 16 by 16 pixels, drawn as a `.pix` text grid in `src/<context>/<icon-name>.pix`.
- Draw edge to edge. The outline may touch the canvas border, there is no safety margin,
  otherwise icons look smaller than their Breeze neighbours in the panel.
- Icon names are the freedesktop names an app asks for, for example `folder`,
  `com.spotify.Client` or `firefox`. Extra names for the same drawing go into `src/aliases.txt`.

## Palette

Endesga 32 (`palette/endesga-32.hex`) plus a few gap-filler ramps in `palette/extra.hex`.
The build refuses anything else. A ramp is added to `extra.hex` only when a brand hue has no
usable match in Endesga, and always as three steps, light, base and dark.
Think in ramps, light to dark, and pick neighbours from the same ramp for highlight, fill, shade and outline.

| Ramp | Light to dark |
|---|---|
| Grey | `ffffff` `c0cbdc` `8b9bb4` `5a6988` `3a4466` `262b44` `181425` |
| Yellow, orange | `fee761` `feae34` `f77622` `be4a2f` `733e39` |
| Red | `f6757a` `e43b44` `a22633` `3e2731` |
| Pink, purple | `ff0044` `b55088` `68386c` `3e2731` |
| Green | `63c74d` `3e8948` `265c42` `193c3e` |
| Blue, cyan | `2ce8f5` `0099db` `124e89` `262b44` |
| Brown, skin | `ead4aa` `e8b796` `e4a672` `c28569` `d77643` `b86f50` `733e39` `3e2731` |
| Violet (extra) | `8b94f7` `5865f2` `3c45a5` |
| Blue (extra) | `4b9bea` `0e70d3` `0a4a8f` |
| Orange red (extra) | `ff8a4c` `fb4d0d` `a32f0a` |

Brand colors get translated to the nearest ramp. If no ramp is close, the brand color becomes
a new ramp in `extra.hex` rather than a one-off. Discord's blurple was the first.

## Outline

- 1 px, closed around the whole silhouette and around every hole.
- Selective, not uniform. The outline is the next darker step of the ramp the fill next to it
  comes from. A yellow folder gets a `733e39` line, a green disc gets `265c42`.
- If the fill is already the darkest step of its ramp, use `181425`.

## Shading

- Light comes from above. One row of the next lighter step along the top of a surface,
  optionally one row of the next darker step along the bottom.
- Keep it to single pixel lines. No gradients, no dithering across areas.
- Flat monochrome logos may skip shading if the original has none.

## Shape

- Free silhouettes. Redraw the logo from scratch at this size, do not shrink the original.
- Ask what each pixel stands for. With 256 pixels every one carries a part of the picture.
- Fill the canvas as far as the shape allows so icons have similar visual weight.

## Workflow

1. Copy `templates/icon.pix` to `src/<context>/<name>.pix` and draw.
2. Run `scripts/build.sh --preview` and look at `preview/<context>/<name>.png`.
3. Reload Plasma's icon cache to see it live:
   `rm ~/.cache/icon-cache.kcache && kquitapp5 plasmashell && kstart5 plasmashell`
4. Commit the `.pix` source together with the generated SVG.
