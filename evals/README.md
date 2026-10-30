# Evals

Trigger and routing evals for Fulcrum's skills. They live outside `skills/`, so an install never copies them.

`cases.json` holds one case per routing decision: a prompt, a small project fixture, the skills allowed to fire first, and optionally a pattern the reply must match. `run-triggers.cjs` runs each case with `claude -p` in a throwaway project holding a copy of `skills/`, with no MCP servers, so nothing can reach a tenant. It needs Node 18 or later and Claude Code, and it spends API usage.

```sh
node evals/run-triggers.cjs --models haiku,sonnet,opus
node evals/run-triggers.cjs --only halt-present
```

These test one thing: that a prompt lands in the right skill and the skill's first move is sane. They are not build evals. Nothing here shows that a skill drives Mentor well. Run them after a description or router change, and before a release tag.

With no MCP surface, the router cannot read the app inventory, so a run may stop and say so. That is expected; the check is on the skill fired and the reply text.
