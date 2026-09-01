#!/usr/bin/env bash
# tome.sh — read the reference bookshelf (epubs) for agents, in place.
# Scans several roots so books in the vault, Apple Books, and iCloud Drive are all
# reachable WITHOUT copying. epub = zip; text is de-tagged on the way out.
#
#   tome.sh list                       # every epub across all roots
#   tome.sh find <name>                # locate a book by fuzzy name
#   tome.sh toc <book>                 # clean table of contents
#   tome.sh search <book> <regex>      # grep the book, with context (de-tagged)
#   tome.sh chapter <book> <toc-text>  # print the section whose TOC entry matches
#
# <book> is a fuzzy name fragment (first match wins). Quote multi-word names.
# Note: Apple Books *store purchases* are DRM'd and won't extract; sideloaded epubs are fine.

set -u

ROOTS=(
  "$HOME/Documents/Obsidian Vault/harness_engineering/Reference/books"
  "$HOME/Documents/books"
  "$HOME/Library/Mobile Documents/iCloud~com~apple~iBooks/Documents"
  "$HOME/Library/Mobile Documents/com~apple~CloudDocs/Downloads"
)

_all() { for r in "${ROOTS[@]}"; do [ -d "$r" ] && find "$r" -maxdepth 1 -iname '*.epub' 2>/dev/null; done; }

_resolve() {  # fuzzy name -> first matching epub path
  local q="$1" r hit
  for r in "${ROOTS[@]}"; do
    [ -d "$r" ] || continue
    hit="$(find "$r" -maxdepth 1 -iname "*$q*.epub" 2>/dev/null | head -1)"
    [ -n "$hit" ] && { printf '%s\n' "$hit"; return 0; }
  done
  return 1
}

_extract() {  # epub -> a dir of content. Zip file: unzip to tmp. Exploded dir: use as-is.
  local epub="$1" d
  if [ -d "$epub" ]; then printf '%s\n' "$epub"; return 0; fi
  d="$TMPDIR/tome-$(basename "$epub" .epub | tr -c 'A-Za-z0-9' _)"
  [ -d "$d" ] || { mkdir -p "$d"; unzip -o -q "$epub" -d "$d" 2>/dev/null; }
  printf '%s\n' "$d"
}

_strip() { sed 's/<[^>]*>/ /g' | tr -s ' \t' ' ' | grep -vE '^ *$'; }

# A book is readable whether it's a .epub zip file OR an exploded .epub directory
# (Apple Books stores them unpacked). iCloud stubs have 0 blocks and fail both.
_readable() {
  if [ -d "$1" ]; then
    [ -f "$1/mimetype" ] || find "$1" \( -iname '*.xhtml' -o -iname '*.html' \) 2>/dev/null | grep -q .
  else
    [ "$(stat -f '%b' "$1" 2>/dev/null || echo 0)" -gt 0 ] && unzip -l "$1" >/dev/null 2>&1
  fi
}
_guard() { _readable "$1" || { echo "NOT DOWNLOADED (iCloud stub?) — materialize it locally first: $1" >&2; exit 3; }; }

cmd="${1:-}"; shift || true
case "$cmd" in
  list)   _all | sort | while IFS= read -r f; do _readable "$f" && echo "$f" || echo "$f  [not downloaded]"; done ;;
  find)   q="${1:?usage: tome.sh find <name>}"; _all | grep -i "$q" || { echo "no match: $q" >&2; exit 1; } ;;
  toc)
    epub="$(_resolve "${1:?usage: tome.sh toc <book>}")" || { echo "not found: ${1:-}" >&2; exit 1; }
    _guard "$epub"; d="$(_extract "$epub")"; ncx="$(find "$d" \( -iname 'toc.ncx' -o -iname 'nav*.xhtml' \) 2>/dev/null | head -1)"
    [ -n "$ncx" ] && _strip < "$ncx" || { echo "no TOC found" >&2; exit 1; } ;;
  search)
    epub="$(_resolve "${1:?usage: tome.sh search <book> <regex>}")" || { echo "not found: ${1:-}" >&2; exit 1; }
    pat="${2:?usage: tome.sh search <book> <regex>}"; _guard "$epub"; d="$(_extract "$epub")"
    grep -rhiE ".{0,60}${pat}.{0,90}" "$d" --include='*.xhtml' --include='*.html' 2>/dev/null | _strip | head -25 ;;
  chapter)
    epub="$(_resolve "${1:?usage: tome.sh chapter <book> <toc-text>}")" || { echo "not found: ${1:-}" >&2; exit 1; }
    pat="${2:?usage: tome.sh chapter <book> <toc-text>}"; _guard "$epub"; d="$(_extract "$epub")"
    ncx="$(find "$d" -iname 'toc.ncx' 2>/dev/null | head -1)"
    src="$(grep -iB2 "$pat" "$ncx" 2>/dev/null | grep -oE 'src="[^"]+"' | head -1 | sed 's/src="//; s/".*//; s/#.*//')"
    [ -n "$src" ] || { echo "no TOC entry matches: $pat" >&2; exit 1; }
    f="$(find "$d" -name "$(basename "$src")" 2>/dev/null | head -1)"
    [ -n "$f" ] && _strip < "$f" || { echo "content file not found for: $src" >&2; exit 1; } ;;
  *) echo "usage: tome.sh {list | find <name> | toc <book> | search <book> <regex> | chapter <book> <toc-text>}" >&2; exit 2 ;;
esac
