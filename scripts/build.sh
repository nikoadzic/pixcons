#!/usr/bin/env bash
# Rebuild every icon: src/<context>/<name>.pix -> Pixcons/scalable/<context>/<name>.svg
# then create the symlinks listed in src/aliases.txt.
# Usage: scripts/build.sh            build all
#        scripts/build.sh --preview  also write zoomed PNGs to preview/<context>/
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
for dir in src/*/; do
  ctx="$(basename "$dir")"
  files=(src/"$ctx"/*.pix)
  [ -e "${files[0]}" ] || continue
  extra=()
  [ "${1:-}" = "--preview" ] && extra=(--preview "preview/$ctx" --scale 8)
  python3 scripts/pixbuild.py "${files[@]}" --svg "Pixcons/scalable/$ctx" "${extra[@]}"
done
grep -v '^\s*#' src/aliases.txt | grep . | while read -r ctx alias target; do
  [ -e "Pixcons/scalable/$ctx/$target.svg" ] || { echo "alias $alias: missing $target.svg" >&2; exit 1; }
  ln -sfn "$target.svg" "Pixcons/scalable/$ctx/$alias.svg"
  echo "$alias.svg -> $target.svg"
done
