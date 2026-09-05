#!/usr/bin/env bash
# Links the Pixcons theme into ~/.local/share/icons so edits in this repo show up live.
# Usage: ./install.sh [--restart]
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
target="$HOME/.local/share/icons/Pixcons"

mkdir -p "$HOME/.local/share/icons"
if [ -e "$target" ] && [ ! -L "$target" ]; then
  echo "refusing to replace a real directory at $target" >&2
  exit 1
fi
ln -sfn "$repo/Pixcons" "$target"
rm -f "$HOME/.cache/icon-cache.kcache"
echo "linked $target -> $repo/Pixcons"

if [ "${1:-}" = "--restart" ]; then
  kquitapp5 plasmashell && kstart5 plasmashell
else
  echo "pick Pixcons under System Settings > Appearance > Icons, or rerun with --restart"
fi
