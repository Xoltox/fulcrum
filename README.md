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
| `fulcrum-solution-init` | Ingesting source material; decomposing into apps, agents, workflows; sizing phases and steps; probing tenant capabilities; scaffolding repo and specs | Once per project, before any Mentor turn. Run on deep-reasoning tier. |
| `fulcrum-gap-analysis` | Assessing an app that already exists against the requirements it was meant to satisfy: build provenance, requirement-to-artifact traceability, classifying gaps vs drift vs stale requirements vs undocumented additions vs unfalsifiable requirements, remediation sequencing | When an app already exists (generated or inherited) and you need to know where it stands against its requirements before planning further work. |
| `fulcrum-mentor-turns` | Turn granularity and decomposition; prompt shape and ceiling; session vs conversation; staleness guard before mutations; polling cadence (rate depends on whether a discardable poller absorbs the cost); run-id durability; publish sequencing | Before issuing any `mentor_start` call and during turn-by-turn execution. |
| `fulcrum-engine-traps` | Construct-indexed trap registry: aggregates, repeaters, links, icons, dates, REST integrations, static entities, charts, overlays, wizards, theming | When building or editing any screen component or model element. |
| `fulcrum-verification` | Proof obligations; which instrument catches which defect class; visual capture and comparison; diagnostic REST endpoint pattern for live data; what platform signals do and do not mean | Before marking any build step done. After publish. When changes seem not to land. |
| `fulcrum-seed-data` | Idempotent loaders; natural keys; relative timestamps; static-entity identifiers; reset and teardown paths | Before building any screen that reads from data. |
| `fulcrum-unattended-guardrails` | Stop conditions; fix-turn caps; halt-and-report rules; subagent depth and delegation; context and call budgeting; checkpoints and handoff discipline; Mentor concurrency locks; model tier policy | Load before the first dispatch of any long unattended session. |

## Install

### Preferred: ask your agent

Point your coding agent at this repository and say:

> Install Fulcrum from this repo (use the latest released tag, not the
> default branch) following `INSTALL.md`.

Your agent knows where its own skills directory lives, better than any
instruction here could guess, and following `INSTALL.md` runs the install
interview that records which models serve which tier — a manual copy skips
that interview entirely. Install from a released tag rather than the tip of
the default branch: a tag is a revision someone reviewed and froze, and what
your agent reads to drive itself should be one of those, not whatever is
mid-edit on the default branch.

### Fallback: manual install, for a person

Use this if you are installing without an agent's help.

1. **Find your skills directory.** Claude Code reads from `~/.claude/skills/`.
   Other harnesses commonly use `~/.agents/skills/` by convention — check your
   harness's own docs if unsure.
2. **Copy the six skill directories in whole**, not just their `SKILL.md`
   files: `fulcrum-solution-init`, `fulcrum-mentor-turns`,
   `fulcrum-engine-traps`, `fulcrum-verification`, `fulcrum-seed-data`,
   `fulcrum-unattended-guardrails`. Each carries a `SKILL.md` plus a
   `references/` directory, and some carry a `templates/` directory — a skill
   missing its `references/` is broken even though it looks installed.
3. **Or run the installer.** `install.sh [target-dir] [--dry-run]` at the repo
   root copies `skills/` into `target-dir` (defaults to `~/.claude/skills`).
   `--dry-run` prints what it would do without changing anything. It is
   additive only — it never deletes anything already in the target directory.
4. **Verify the install.** Confirm each of the six directories exists at the
   target path with its `SKILL.md` and `references/` intact, and that your
   agent's skill listing (or equivalent discovery mechanism) picks them up.
5. **Update later** by re-running step 2 or 3 against a newer tag — both are
   safe to re-run and only add or overwrite files this repo ships.

**A manual install gets no install interview.** The interview is what decides
which model serves which tier (`deep-reasoning`, `workhorse`, `poller`) and
whether your harness supports per-subagent model assignment — installing by
hand means you must make those calls yourself. Read `MODEL-TIERS.md` for what
to decide and the resolution order, then record your answers in a
`MODEL-TIERS.local.md` file beside the installed skills — never edit the
answers into the skill files themselves or into `MODEL-TIERS.md`.

## How it is meant to be used

1. **Solution init (once per project, no app yet).** Run `fulcrum-solution-init` on the deep-reasoning tier with your source material (BRD, Figma, mockups, or raw requirements). It produces the plan, specs, `tenant-profile.md`, and project repo scaffold. This phase is expensive but happens once.

   **If an app already exists instead**, start with `fulcrum-gap-analysis`
   rather than solution-init — this is a first-class entry point, not a
   repair path for something that went wrong. It applies equally to fresh
   generator output (the platform's web app-generation route optimises for
   speed over depth, so large gaps there are expected and normal) and to an
   inherited mature app assessed at any time. It establishes where the app
   stands against its requirements; remediation then proceeds through the
   normal spec-and-turn path below.

2. **Every session after init.** Run on the workhorse tier. Read the written spec and execute it step by step. Do not re-derive the plan; the plan is already written.

3. **Polling and wait loops.** Run on the poller tier. All `mentor_get_run` polling, `publish_status` checking, and long-running supervision happens on the cheapest available model.

Tiers are vendor-neutral. See `MODEL-TIERS.md` for the concrete model mapping and the rationale. For harnesses without skill auto-triggering, see `AGENTS.md` for the entry point.

## Repository layout

```
fulcrum/
  skills/
    fulcrum-solution-init/
      SKILL.md                    # When to run, what it does
      references/                 # Depth docs: decomposition, repo scaffold, tenant probe
      templates/                  # Handoff and spec templates; tenant-profile skeleton
    fulcrum-gap-analysis/
      SKILL.md
      references/                 # Traceability matrix, finding classification, coverage reporting
    fulcrum-mentor-turns/
      SKILL.md
      references/                 # Prompt scaffolds, turn recovery
    fulcrum-engine-traps/
      SKILL.md
      references/                 # Per-construct trap detail: aggregates, repeaters, dates, etc.
    fulcrum-verification/
      SKILL.md
      references/                 # Proof instruments, visual verification, diagnostic patterns
    fulcrum-seed-data/
      SKILL.md
      references/                 # Idempotent loader pattern
    fulcrum-unattended-guardrails/
      SKILL.md
      references/                 # Halt conditions, budgeting, delegation rules
  install.sh                      # Portable installer: skills/ -> target dir
  CONVENTIONS.md                  # Authoring contract (binding)
  MODEL-TIERS.md                  # Tier vocabulary and vendor mapping
  INSTALL.md                      # Agent-driven install contract
  HARNESS-NOTES.md                # Observed per-harness behaviour (not requirements)
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
