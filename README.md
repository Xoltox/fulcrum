# Fulcrum

A harness-agnostic skill set for driving OutSystems ODC Mentor through long, largely unattended build sessions with real guardrails. Derived from a 47-step production ODC build and its incident log — the traps are field-observed, not theoretical.

## Why this exists

- Platform success signals are unreliable in both directions: zero validation errors and a clean publish are compatible with blank rows, empty repeaters, unrendered icons, and corrupted content. Model-layer checks are structurally blind to whole defect classes.

- Tenant-varying facts get probed once per project during init, then referenced thereafter. Differences in `db_query` liveness, available UI blocks, icon fonts, and Mentor backend identifiers are not hardcoded.

- Every rule carries its failure mode explicitly. Measured finding: prompts that named why a construct fails stopped the failure recurring. Prompts that only said "don't" did not.

- Claims carry explicit evidence strength tags: `[VERIFIED]` (observed multiple times), `[SINGLE-OBSERVATION]` (real but not generalized), `[UNVERIFIED]` (inferred only), or `[TENANT]` (deferred to the profile).

- Hand-restated rules degrade over a long build. These rules are packaged as skills so the same logic runs unmodified across many sessions, on any harness.

## The skills

| Skill | Owns | When it fires |
|---|---|---|
| `odc-solution-init` | Ingesting source material; decomposing into apps, agents, workflows; sizing phases and steps; probing tenant capabilities; scaffolding repo and specs | Once per project, before any Mentor turn. Run on deep-reasoning tier. |
| `odc-mentor-turns` | Turn granularity and decomposition; prompt shape and ceiling; session vs conversation; staleness guard before mutations; polling cadence (45s for read turns, 90s for write); run-id durability; publish sequencing | Before issuing any `mentor_start` call and during turn-by-turn execution. |
| `odc-engine-traps` | Construct-indexed trap registry: aggregates, repeaters, links, icons, dates, REST integrations, static entities, charts, overlays, wizards, theming | When building or editing any screen component or model element. |
| `odc-verification` | Proof obligations; which instrument catches which defect class; visual capture and comparison; diagnostic REST endpoint pattern for live data; what platform signals do and do not mean | Before marking any build step done. After publish. When changes seem not to land. |
| `odc-seed-data` | Idempotent loaders; natural keys; relative timestamps; static-entity identifiers; reset and teardown paths | Before building any screen that reads from data. |
| `odc-unattended-guardrails` | Stop conditions; fix-turn caps; halt-and-report rules; subagent depth and delegation; context and call budgeting; checkpoints and handoff discipline; Mentor concurrency locks; model tier policy | Load before the first dispatch of any long unattended session. |

## Install

Copy the contents of `skills/` into your agent's skills directory:

- Claude Code: `~/.claude/skills/`
- Other harnesses: `~/.agents/skills/`

For per-harness setup (frontmatter, adapters, auto-triggering), see `adapters/`. A scripted install is available at `adapters/generic/install.sh`.

## How it is meant to be used

1. **Solution init (once per project).** Run `odc-solution-init` on the deep-reasoning tier with your source material (BRD, Figma, mockups, or raw requirements). It produces the plan, specs, `tenant-profile.md`, and project repo scaffold. This phase is expensive but happens once.

2. **Every session after init.** Run on the workhorse tier. Read the written spec and execute it step by step. Do not re-derive the plan; the plan is already written.

3. **Polling and wait loops.** Run on the poller tier. All `mentor_get_run` polling, `publish_status` checking, and long-running supervision happens on the cheapest available model.

Tiers are vendor-neutral. See `MODEL-TIERS.md` for the concrete model mapping and the rationale. For harnesses without skill auto-triggering, see `AGENTS.md` for the entry point.

## Repository layout

```
fulcrum/
  skills/
    odc-solution-init/
      SKILL.md                    # When to run, what it does
      references/                 # Depth docs: decomposition, repo scaffold, tenant probe
      templates/                  # Handoff and spec templates; tenant-profile skeleton
    odc-mentor-turns/
      SKILL.md
      references/                 # Prompt scaffolds, turn recovery
    odc-engine-traps/
      SKILL.md
      references/                 # Per-construct trap detail: aggregates, repeaters, dates, etc.
    odc-verification/
      SKILL.md
      references/                 # Proof instruments, visual verification, diagnostic patterns
    odc-seed-data/
      SKILL.md
      references/                 # Idempotent loader pattern
    odc-unattended-guardrails/
      SKILL.md
      references/                 # Halt conditions, budgeting, delegation rules
  adapters/
    claude-code/                  # Claude Code harness-specific wiring
    antigravity/                  # Antigravity harness-specific wiring
    generic/                      # Portable install script
  CONVENTIONS.md                  # Authoring contract (binding)
  MODEL-TIERS.md                  # Tier vocabulary and vendor mapping
  LICENSE                         # MIT
```

## Conventions

All skills are bound by the authoring contract in `CONVENTIONS.md`. Read it before writing or editing.

Two headline rules:

- **Harness agnostic.** No vendor model names (use tier vocabulary from `MODEL-TIERS.md`), no harness tool names, no harness-specific frontmatter in skill bodies.

- **Platform truth by default.** Every rule is general ODC/Mentor truth, not incident history from one build. Tenant-varying facts are probed via `tenant-profile.md`, never hardcoded. Rules state their failure mechanism.

## Status and provenance

Derived from a single production ODC build on one tenant. The traps are field-observed but the skill set has been exercised on one harness only; other harnesses are untested.

This skill set complements and does not replace the separate `outsystems-mcp-skills` catalog, which covers app bootstrap, architecture dependency analysis, and deploy workflows. Fulcrum layers long-run build discipline and construction correctness on top.

Licensed under MIT.
