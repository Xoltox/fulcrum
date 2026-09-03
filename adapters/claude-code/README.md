# Claude Code adapter

## Install

```sh
mkdir -p ~/.claude/skills
cp -R /path/to/fulcrum/skills/* ~/.claude/skills/
```

Or run `../generic/install.sh` (defaults to `~/.claude/skills`, supports
`--dry-run`).

## What auto-triggering does for you here

Claude Code reads each skill's `description` frontmatter and loads the
matching `SKILL.md` automatically when your prompt matches one of its
trigger phrases — you do not need to name the skill or read `AGENTS.md`
first. `AGENTS.md` still exists at the repo root because Fulcrum is
harness-agnostic and most other harnesses lack this feature, but on Claude
Code it is redundant with what the harness already does for you.

## Known quirks of this harness

- **Subagent sleeps need a mechanism the harness will not swallow.** On
  this harness, invoking sleep via a Python one-liner
  (`python3 -c "import time; time.sleep(n)"`) has proven reliable where the
  shell `sleep` builtin, invoked the same way inside a subagent, has not
  reliably held. This is a harness artifact of Claude Code's subagent
  execution, not a platform truth about ODC, Mentor, or any other harness —
  verify your own harness's sleep behavior once at session start and reuse
  whatever proves reliable, per `skills/fulcrum-mentor-turns/SKILL.md`.

## Updating from the upstream `outsystems-mcp-skills` repo

If you also track the third-party `denwx/outsystems-mcp-skills` skills,
`update-upstream-skills.sh` in this directory pulls that clone and syncs its
`skills/` into `~/.claude/skills/`. It takes the clone's path as an optional
argument (or `$OUTSYSTEMS_MCP_SKILLS_CLONE`) — it does not live inside that
clone, so it cannot create stray local commits there. See the script's own
header comment for usage and safety notes.
