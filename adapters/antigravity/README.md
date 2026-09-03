# Antigravity adapter

## Install

```sh
mkdir -p ~/.agents/skills
cp -R /path/to/fulcrum/skills/* ~/.agents/skills/
```

`~/.agents/skills/` is the documented convention for non-Claude-Code
harnesses. Or run `../generic/install.sh ~/.agents/skills` (supports
`--dry-run`).

## Status: untested

Fulcrum is authored to be harness-agnostic, but it has only been exercised
in anger on one harness so far (Claude Code). It has **not** been run
end-to-end on Antigravity. Treat this adapter as an install path only, not
a verified integration.

There is no confirmed information here about how Antigravity discovers or
triggers skills, whether it reads `~/.agents/skills/` automatically, or how
it handles subagent dispatch, sleep/wait mechanisms, or browser automation
capabilities — none of that is asserted because none of it has been
verified on this harness. If you run Fulcrum on Antigravity and hit a
harness-specific problem (a skill not loading, a wait being swallowed, a
capability the skills assume that isn't present), report it so this adapter
can be corrected with real findings instead of guesses.

Until then, treat `AGENTS.md` at the repo root as your entry point and
follow `../generic/README.md` for how to load a skill manually if
auto-triggering does not work as expected.
