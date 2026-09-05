# Pixcons

A personal KDE Plasma icon theme. It inherits from Breeze Dark and only contains
the icons that were drawn by hand, so everything else keeps its default look.

## Layout

```
Pixcons/            the icon theme itself (this folder gets linked or packed)
  index.theme       theme metadata, directory list and sizes
  apps/48/          application icons, 48x48 SVG, colorful
  places/48/        folder and location icons, 48x48 SVG
  actions/22/       monochrome toolbar and menu icons, 22x22 SVG
templates/          starting points for new icons
install.sh          links the theme into ~/.local/share/icons
```

## Use it locally

```
./install.sh --restart
```

Then pick Pixcons under System Settings, Appearance, Icons. Because the theme is
a symlink into this repo, saving an SVG in Inkscape is enough to see the change
after a cache clear.

## Add an icon

1. Find the name of the icon you want to replace, for example with
   `ls /usr/share/icons/breeze-dark/apps/48/` or the Cuttlefish app.
2. Copy the matching template from `templates/` into the right folder and rename
   it to that icon name, for example `Pixcons/apps/48/firefox.svg`.
3. Draw it in Inkscape and save as Plain SVG.
4. Clear the cache with `rm ~/.cache/icon-cache.kcache` and restart Plasma.

## Pack for sharing

```
tar czf pixcons.tar.gz Pixcons
```

The archive can be installed on any Plasma machine through Install from File in
the Icons settings page.
