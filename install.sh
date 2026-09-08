#!/bin/sh
# install.sh — copy Fulcrum's skills/* into a target skills directory.
#
# POSIX sh only (no bashisms).
#
# Usage:
#   ./install.sh [target-dir] [--dry-run]
#
#   target-dir   Where to install. Defaults to ~/.claude/skills.
#   --dry-run    Show what would happen, change nothing.
#
# Non-destructive: only adds and updates files. Never deletes anything
# already in target-dir, including skills not shipped by this repo.

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SRC="$SCRIPT_DIR/skills"

DEST="$HOME/.claude/skills"
DRY_RUN=0
DEST_SET=0

for arg in "$@"; do
  case "$arg" in
    --dry-run)
      DRY_RUN=1
      ;;
    -*)
      echo "Unknown argument: $arg" >&2
      echo "Usage: $0 [target-dir] [--dry-run]" >&2
      exit 2
      ;;
    *)
      if [ "$DEST_SET" = "1" ]; then
        echo "Unknown argument: $arg" >&2
        echo "Usage: $0 [target-dir] [--dry-run]" >&2
        exit 2
      fi
      DEST="$arg"
      DEST_SET=1
      ;;
  esac
done

if [ ! -d "$SRC" ]; then
  echo "error: $SRC does not exist. Aborting." >&2
  exit 1
fi

if [ "$DRY_RUN" = "1" ]; then
  echo "[dry-run] would copy:"
  for d in "$SRC"/*/; do
    name=$(basename "$d")
    echo "  $name -> $DEST/$name"
  done
  echo "[dry-run] no changes made."
  exit 0
fi

mkdir -p "$DEST"
echo "Installing skills -> $DEST"
if command -v rsync >/dev/null 2>&1; then
  # No --delete: only adds/updates files this repo ships. Does not remove
  # unrelated skills already installed in $DEST.
  rsync -a "$SRC/" "$DEST/"
else
  cp -R "$SRC/." "$DEST/"
fi

echo "Done. Installed skills:"
ls "$DEST" | grep '^fulcrum-' || true
