#!/bin/sh
# update-upstream-skills.sh — pull the outsystems-mcp-skills clone and sync
# its skills/ into the local agent's skills directory.
#
# POSIX sh only (no bashisms) — must run under dash/ash/sh, not just bash.
#
# Originally lived inside the outsystems-mcp-skills clone itself (as
# update-skills.sh) and located the clone via its own script directory.
# Moved here because a script that syncs a third-party upstream clone does
# not belong committed inside that clone's own working tree — it created
# local commits on `main` that collide with pull requests sent from the same
# clone. This copy takes the clone's location explicitly instead.
#
# Usage:
#   ./update-upstream-skills.sh [--dry-run] [clone-dir]
#
#   clone-dir   Path to the outsystems-mcp-skills clone. Defaults to the
#               $OUTSYSTEMS_MCP_SKILLS_CLONE env var if set, else
#               $HOME/Projects/Outsystems/outsystems-mcp-skills.
#   --dry-run   Show what would happen, change nothing.
#
# Install target:
#   This script installs into ~/.claude/skills/ (Claude Code's skills dir),
#   per upstream README "Path B — manual":
#     git clone https://github.com/denwx/outsystems-mcp-skills.git
#     cd outsystems-mcp-skills
#     mkdir -p ~/.claude/skills
#     cp -R skills/* ~/.claude/skills/
#
#   Non-Claude-Code harnesses (e.g. Codex CLI) use a different, separate
#   install location instead: ~/.agents/skills/. If you are on such a
#   harness, do NOT run this script as-is — either edit DEST below or run
#   the equivalent manual `cp -R skills/* ~/.agents/skills/` yourself.
#
# Symlink alternative (NOT used here, untested):
#   Instead of copying, DEST could in principle be a symlink into the
#   clone's skills/ directory (or each skill symlinked individually), so a
#   `git pull` alone would update the live skills with no copy step. This
#   script deliberately does NOT do that: whether Claude Code's harness
#   reliably resolves symlinked skill directories is untested, and skills
#   are only loaded at session start, so it can't be verified from inside
#   a running session. Copying is the documented, known-good method.
#
# Safety:
#   - Refuses to run (in either mode) if the clone's working tree has
#     uncommitted local changes — it will not pull or copy over changes
#     you might want to keep. Commit, stash, or discard them first.
#   - --dry-run performs the fetch/pull check but makes no changes: it
#     shows the commit range that WOULD be pulled and does not copy.

set -eu

DEST="$HOME/.claude/skills"
DRY_RUN=0
CLONE_DIR="${OUTSYSTEMS_MCP_SKILLS_CLONE:-$HOME/Projects/Outsystems/outsystems-mcp-skills}"
CLONE_DIR_SET=0

for arg in "$@"; do
  case "$arg" in
    --dry-run)
      DRY_RUN=1
      ;;
    -*)
      echo "Unknown argument: $arg" >&2
      echo "Usage: $0 [--dry-run] [clone-dir]" >&2
      exit 2
      ;;
    *)
      if [ "$CLONE_DIR_SET" = "1" ]; then
        echo "Unknown argument: $arg" >&2
        echo "Usage: $0 [--dry-run] [clone-dir]" >&2
        exit 2
      fi
      CLONE_DIR="$arg"
      CLONE_DIR_SET=1
      ;;
  esac
done

if [ ! -d "$CLONE_DIR" ]; then
  echo "error: $CLONE_DIR does not exist. Aborting." >&2
  exit 1
fi

cd "$CLONE_DIR"

if [ ! -d .git ]; then
  echo "error: $CLONE_DIR is not a git repository. Aborting." >&2
  exit 1
fi

# Refuse to run destructively over local edits (tracked changes, staged
# changes, or untracked files in the working tree).
if [ -n "$(git status --porcelain)" ]; then
  echo "error: working tree has uncommitted local changes. Refusing to pull/sync." >&2
  echo "       Commit, stash, or discard them first, then re-run." >&2
  git status --short
  exit 1
fi

BEFORE_SHA=$(git rev-parse HEAD)

if [ "$DRY_RUN" = "1" ]; then
  echo "[dry-run] fetching from origin (no local changes will be made)..."
  git fetch origin
  REMOTE_SHA=$(git rev-parse '@{u}' 2>/dev/null || git rev-parse origin/HEAD)
  if [ "$BEFORE_SHA" = "$REMOTE_SHA" ]; then
    echo "[dry-run] already up to date at $BEFORE_SHA"
  else
    echo "[dry-run] would pull commit range: $BEFORE_SHA..$REMOTE_SHA"
    git --no-pager log --oneline "$BEFORE_SHA..$REMOTE_SHA"
  fi
  echo "[dry-run] would sync skills/ -> $DEST"
  echo "[dry-run] no changes made."
  exit 0
fi

echo "Pulling latest changes..."
git pull --ff-only origin

AFTER_SHA=$(git rev-parse HEAD)

if [ "$BEFORE_SHA" = "$AFTER_SHA" ]; then
  echo "Already up to date at $BEFORE_SHA"
else
  echo "Pulled commit range: $BEFORE_SHA..$AFTER_SHA"
  git --no-pager log --oneline "$BEFORE_SHA..$AFTER_SHA"
fi

mkdir -p "$DEST"
echo "Syncing skills/ -> $DEST"
if command -v rsync >/dev/null 2>&1; then
  # No --delete: only adds/updates files this repo ships. Does not remove
  # unrelated skills you may have installed alongside these in $DEST.
  rsync -a skills/ "$DEST/"
else
  # Fallback matching upstream's documented manual install method exactly.
  cp -R skills/. "$DEST/"
fi

echo "Done. Installed skills:"
ls "$DEST" | grep '^outsystems-' || true
