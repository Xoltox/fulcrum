# Generic adapter

For any harness without documented skill auto-triggering, or a bare
scripted agent loop.

## Entry point

Read `AGENTS.md` at the repo root first, every session. It has a routing
table mapping your situation to the one skill to load — there is no
auto-trigger here, so this replaces it.

## Loading a skill manually

Once `AGENTS.md` names a skill, read that skill's file directly by path:

```
skills/<skill-name>/SKILL.md
```

Follow any `references/*.md` pointers inside it only when the situation it
names applies — they are depth, not required reading.

## Capabilities this skill set assumes

Whatever drives Fulcrum needs, at minimum:

- **An authenticated ODC MCP surface** — Mentor turns (`mentor_start`,
  `mentor_get_run`), publish (`publish_start`, `publish_status`), and model
  read-back (`context_*`, `app_revisions`, `env_app`).
- **A subagent mechanism** — some way to dispatch bounded, isolated units
  of work at a chosen model tier, one depth level only.
- **A browser automation capability for visual proof** — a browser MCP
  tool where your harness has one, otherwise a headless browser driver.
  Needed for `odc-verification`'s screen-render checks.
- **A shell** — for the diagnostic REST calls, seed-data loader calls, and
  sleep/poll loops the skills describe. Verify once at session start which
  sleep mechanism your harness will not swallow mid-wait, then reuse it.

If any of these is missing, the skill that needs it will say so in its
`requires` frontmatter — check that before assuming a workaround.

## Installing

```sh
./install.sh                    # copies skills/* into ~/.claude/skills
./install.sh /some/other/dir     # or any target directory
./install.sh --dry-run           # show what would happen, change nothing
```

`install.sh` only adds and updates files — it never deletes anything from
the target directory.
