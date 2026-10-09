#!/bin/sh
# install.sh - copy Fulcrum's skills/* into a target skills directory, and
# its Claude Code agent definitions (agents/claude-code/*.md) into an agents
# directory.
#
# POSIX sh only (no bashisms).
#
# Usage:
#   ./install.sh [target-dir] [--agents-dir <dir>] [--no-agents]
#                [--force-agents] [--dry-run]
#
#   target-dir          Where to install skills. Defaults to ~/.claude/skills.
#   --agents-dir <dir>  Where to install agent definitions.
#                       Defaults to ~/.claude/agents.
#   --no-agents         Skip installing agent definitions.
#   --force-agents      Also overwrite same-named agent files that were not
#                       generated from this repo (hand-made ones). Without
#                       this flag those are skipped with a warning.
#   --dry-run           Show what would happen, change nothing.
#
# Non-destructive: only adds and updates files. Never deletes anything
# already in target-dir or the agents directory. In the agents directory it
# touches only files whose names match the ones this repo ships, and
# overwrites such a file only if it carries the marker line
# "Generated from agents/roles/" (or --force-agents is given). A destination
# that is the very same file as the source (a link made by link-skills.ps1)
# is skipped. All agent conflicts are worked out and printed before anything
# is written.
#
# Agent definitions load at session start: restart your session after
# installing or updating them.

set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SRC="$SCRIPT_DIR/skills"
AGENTS_SRC="$SCRIPT_DIR/agents/claude-code"

DEST="$HOME/.claude/skills"
AGENTS_DEST="$HOME/.claude/agents"
DRY_RUN=0
DEST_SET=0
AGENTS=1
FORCE_AGENTS=0
MARKER='Generated from agents/roles/'

usage() {
  echo "Usage: $0 [target-dir] [--agents-dir <dir>] [--no-agents] [--force-agents] [--dry-run]" >&2
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      ;;
    --no-agents)
      AGENTS=0
      ;;
    --force-agents)
      FORCE_AGENTS=1
      ;;
    --agents-dir)
      if [ "$#" -lt 2 ] || [ -z "$2" ]; then
        echo "--agents-dir needs a directory" >&2
        usage
        exit 2
      fi
      case "$2" in
        -*)
          echo "--agents-dir needs a directory, got: $2" >&2
          usage
          exit 2
          ;;
      esac
      AGENTS_DEST="$2"
      shift
      ;;
    --agents-dir=*)
      AGENTS_DEST="${1#--agents-dir=}"
      case "$AGENTS_DEST" in
        ""|-*)
          echo "--agents-dir needs a directory, got: '$AGENTS_DEST'" >&2
          usage
          exit 2
          ;;
      esac
      ;;
    -*)
      echo "Unknown argument: $1" >&2
      usage
      exit 2
      ;;
    *)
      if [ "$DEST_SET" = "1" ]; then
        echo "Unknown argument: $1" >&2
        usage
        exit 2
      fi
      DEST="$1"
      DEST_SET=1
      ;;
  esac
  shift
done

if [ ! -d "$SRC" ]; then
  echo "error: $SRC does not exist. Aborting." >&2
  exit 1
fi

if [ "$AGENTS" = "1" ] && [ ! -d "$AGENTS_SRC" ]; then
  echo "warning: $AGENTS_SRC does not exist; skipping agent definitions." >&2
  AGENTS=0
fi

# classify <file-name>: print what would happen to the agent file of that name.
#   new | current | same-file | skip-not-ours | update | overwrite-forced
classify_agent() {
  _src="$AGENTS_SRC/$1"
  _dst="$AGENTS_DEST/$1"
  if [ ! -e "$_dst" ] && [ ! -L "$_dst" ]; then
    echo new
  elif [ -e "$_dst" ] && [ "$_src" -ef "$_dst" ]; then
    echo same-file
  elif [ -f "$_dst" ] && grep -q "$MARKER" "$_dst" 2>/dev/null; then
    if cmp -s "$_src" "$_dst"; then echo current; else echo update; fi
  elif [ "$FORCE_AGENTS" = "1" ]; then
    echo overwrite-forced
  else
    echo skip-not-ours
  fi
}

# Pre-check agents before writing anything (skills included).
if [ "$AGENTS" = "1" ]; then
  if [ -e "$AGENTS_DEST" ] && [ ! -d "$AGENTS_DEST" ]; then
    echo "error: $AGENTS_DEST exists and is not a directory. Aborting; nothing written." >&2
    exit 1
  fi
  echo "Agent definitions -> $AGENTS_DEST"
  for f in "$AGENTS_SRC"/*.md; do
    [ -f "$f" ] || continue
    name=$(basename "$f")
    case $(classify_agent "$name") in
      new) echo "  $name: new" ;;
      update) echo "  $name: update" ;;
      current) echo "  $name: up to date" ;;
      same-file) echo "  $name: skip (same file as source, already linked)" ;;
      overwrite-forced) echo "  $name: overwrite (--force-agents; not generated from this repo)" ;;
      skip-not-ours) echo "  $name: skip (not ours: exists without '$MARKER'; use --force-agents to overwrite)" ;;
    esac
  done
else
  echo "Agent definitions: skipped."
fi

if [ "$DRY_RUN" = "1" ]; then
  echo "[dry-run] would copy skills:"
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
ls "$DEST" | grep '^fulcrum\(-\|$\)' || true

if [ "$AGENTS" = "1" ]; then
  mkdir -p "$AGENTS_DEST"
  for f in "$AGENTS_SRC"/*.md; do
    [ -f "$f" ] || continue
    name=$(basename "$f")
    case $(classify_agent "$name") in
      new|update|overwrite-forced)
        # One file at a time, by name: never touches other files in the directory.
        cp "$f" "$AGENTS_DEST/$name"
        echo "  agent written: $name"
        ;;
      current) ;;
      same-file) echo "  agent skipped (same file): $name" ;;
      skip-not-ours) echo "  warning: agent skipped, not ours: $name" >&2 ;;
    esac
  done
  echo "Agent definitions load at session start: restart your session to use them."
fi
