# Pixcons

A personal 16 by 16 pixel art icon theme for KDE Plasma. It inherits from Breeze Dark,
so only the icons drawn here change and everything else keeps its default look.

Drawn in the Endesga 32 palette with selective outlines and free silhouettes.
See [STYLE.md](STYLE.md) for the rules. Inspired by
[pixora-icons](https://github.com/tsora1603/pixora-icons), drawn from scratch.

## Layout

```
Pixcons/                  the icon theme, link or pack this folder
  index.theme             theme metadata
  scalable/<context>/     generated SVGs, one per icon, plus alias symlinks
src/<context>/*.pix       the actual sources, 16 line text grids
src/aliases.txt           extra names that point at an existing icon
palette/*.hex             the only colors allowed, Endesga 32 plus gap fillers
scripts/pixbuild.py       .pix to SVG and PNG preview
scripts/build.sh          rebuild everything and create aliases
templates/icon.pix        blank canvas to copy
install.sh                symlink the theme into ~/.local/share/icons
```

Contexts are `apps`, `places`, `mimetypes`, `categories` and `devices`.

## Use it

```
./install.sh --restart
```

Then pick Pixcons under System Settings, Appearance, Icons. The theme folder is a symlink
into this repo, so after `scripts/build.sh` a cache clear is enough to see new icons.

## Draw an icon

A `.pix` file is a legend followed by the grid:

```
O 733e39
Y feae34
................
.OYYYYYYYYYYYYO.
...
```

Each legend line maps one character to a palette color, `.` is transparent.
Build with `scripts/build.sh --preview` and check the PNG in `preview/`.

## Pack for sharing

```
tar czhf pixcons.tar.gz Pixcons
```

The `h` flag turns the alias symlinks into real files. Install the archive on any Plasma
machine through Install from File in the Icons settings page.
