# Fulcrum — authoring contract

Read this before writing or editing any skill in `skills/`. It is binding.

## What Fulcrum is

A harness-agnostic skill set for driving **OutSystems ODC Mentor** through long,
largely unattended build sessions with real guardrails. Derived from a 47-step,
multi-week agentic build that shipped a working ODC app, plus the incident log
from that build.

The unit of work is a **solution**, not an app: possibly several apps, agents and
workflows under one plan.

## Hard rule 1 — harness agnostic

These skills must work in Claude Code, Antigravity, Cursor, Codex, or a bare
scripted agent loop. Therefore:

- **Never name a harness-specific tool as the required instrument.** Say what
  capability is needed and let the agent map it.
  - Wrong: "use the Agent tool with `subagent_type: general-purpose`"
  - Right: "dispatch a subagent using your harness's subagent mechanism"
  - Wrong: "screenshot with Playwright"
  - Right: "capture with a browser automation capability (browser MCP tool
    preferred when available; a headless driver such as Playwright otherwise)"
- **Never name a model.** Use the tier vocabulary in `MODEL-TIERS.md`
  (`deep-reasoning`, `workhorse`, `poller`). Only `MODEL-TIERS.md` maps tiers to
  concrete model names, and it does so for more than one vendor.
- **MCP tool names are allowed** when referring to ODC MCP operations
  (`mentor_start`, `mentor_get_run`, `publish_start`, `publish_status`,
  `env_app`, `app_revisions`, `context_*`). These are the ODC surface itself, not
  a harness feature. Write them bare — no `mcp__outsystems__` prefix, which is
  Claude-Code-specific wiring.
- **No harness-specific frontmatter in the body of a skill.** `allowed-tools`,
  slash-command syntax, and `$ARGUMENTS` belong in `adapters/`, not here.
- **Quirks of one harness go in `adapters/<harness>/notes.md`**, not in a skill.
  Example: "sleep via `python3 -c 'import time; time.sleep(n)'`, never bash
  `sleep`" is a Claude Code subagent quirk. The portable rule is: "sleep via a
  mechanism your harness will not swallow — verify once at session start, then
  reuse it."

## Hard rule 2 — platform truth by default

Every rule in a skill must be **general ODC/Mentor truth**, not incident history
from one build and not one tenant's configuration.

- Strip all project nouns: no client or project names, no domain-entity names
  specific to a real engagement, no project-specific CSS class prefixes, no
  specific revision numbers. Where a concrete example genuinely aids
  comprehension, invent a neutral one (`Order`, `Shipment`, `Customer`).
- **Tenant-varying facts do not get asserted.** They get probed. See below.
- Keep the *consequence*, drop the anecdote. "Deleting a Gallery's default `List`
  child collapses the repeater to one row while validation and publish stay
  clean" is platform truth. "This happened on step 18" is not.

### The tenant profile contract

Facts that vary by tenant, licence, or platform version are resolved once per
project by a read-only capability probe during `fulcrum-solution-init`, which writes
`tenant-profile.md` into the project repo.

Skills must **reference the profile, never hardcode the answer**:

- Wrong: "`db_query` is dead — never use it."
- Right: "Check `tenant-profile.md` for `db_query`. On tenants where it returns
  empty results for even a trivial `SELECT 1`, there is no model-layer path to
  live row data; use a temporary diagnostic REST endpoint instead."

Facts belonging in the profile include, at minimum: `db_query` liveness; which
UI blocks exist (`Modal`, `BottomSheet`, `ActionSheet`, `Sidebar`, `Accordion`,
`Wizard`); icon-font family and name casing; available `ModelFeature_*` flags;
meridiem/format-token behaviour; whether server actions can be marked public;
Mentor backend identifier; and the Mentor prompt-length ceiling.

## Hard rule 3 — state the mechanism, not just the ban

Measured finding from the source build: prompts that named *why* a construct
fails stopped the failure recurring; prompts that only said "don't" did not.

- Weak: "Do not add an AggregatedAttribute here."
- Strong: "Do not add an AggregatedAttribute to this aggregate — an aggregate
  that carries one collapses `.List` to a single summary row, so the repeater
  renders exactly one item while validation and publish both stay clean."

Every rule carries its failure mode. If you cannot state what breaks, the rule
is not ready to write.

## Hard rule 4 — mark evidence strength

Tag any claim that is not directly observed:

- `[VERIFIED]` — observed live, more than once, in the source build.
- `[SINGLE-OBSERVATION]` — seen once; real but not generalised.
- `[UNVERIFIED]` — inferred or reported but never confirmed. Say so plainly.
- `[TENANT]` — belongs in `tenant-profile.md`; skill must defer to the probe.

Default to `[VERIFIED]` only when the source corpus shows repeat occurrence.
Do not launder a single observation into a general rule.

## Skill file layout

```
skills/<skill-name>/
  SKILL.md          # thin: when to use, the procedure, pointers. Target <200 lines.
  references/*.md   # depth, loaded on demand. One file per coherent topic.
```

`SKILL.md` is what an agent reads first and may be all it reads. It must be
self-sufficient for the common path and must say explicitly which reference file
to open for which situation. Do not write a 600-line SKILL.md.

### Frontmatter — portable subset only

```yaml
---
name: <directory name, exactly>
description: <what it does, then "Use when ..." with concrete trigger phrases a
  user would actually type. This is the auto-trigger surface — be specific.>
version: "1.0.0"
requires: <capabilities in prose, e.g. "ODC MCP server authenticated; Mentor
  enabled on the tenant; a browser automation capability for visual proof">
---
```

No `allowed-tools`, no `license`, no `compatibility`, no `metadata:` block.
Harness-specific frontmatter is injected by `adapters/`.

`name` must match the directory name exactly, and must be globally unique — the
source corpus contains two skill directories declaring the same `name`, which
made one of them unresolvable.

## Cross-references

- Link by **relative path**: `see ../fulcrum-verification/SKILL.md`, or
  `references/aggregates.md`.
- **Never use `§`-numbered anchors.** Every `§` reference in the source corpus
  was dangling because the target files had no numbered headings.
- Prefer naming a heading verbatim over citing a line number. Line numbers rot.

## Canonical facts — use these exact values

These were wrong or missing in the source corpus. They are correct here.

**Mentor polling cadence — two rates, by turn type:**

- **45 s** for turns where Mentor *answers* — read-only inventory, invariant
  checks, "report what you see" turns.
- **90 s** for turns where Mentor *changes the model* — any build or fix turn,
  and all publish polling.
- Ignore the server's `pollAfterMs` field.
- Never poll at a fixed short interval for a mutating turn; never poll a
  read-back turn at 90 s and waste half the wall clock.

**Model tiering — phase-based, not flat:**

- Project init (ingest sources, derive the solution plan, scaffold the repo):
  `deep-reasoning` tier, optionally `workhorse` if budget is tight.
- Every session after init: `workhorse` tier orchestrator.
- All poll loops and wait states: `poller` tier.
- Full rationale and the vendor mapping live in `MODEL-TIERS.md`. A flat
  single-tier policy appears in the source corpus as a budget-exhaustion
  artifact — record it as history, never as the rule.

## Skill boundaries — stay in your lane

Overlap causes mis-triggering. One topic, one owner:

| Skill | Owns | Explicitly does NOT own |
|---|---|---|
| `fulcrum-solution-init` | Ingesting source artifacts; decomposing a solution into apps/agents/workflows; phase and step sizing; repo scaffold; the tenant capability probe; the handoff document structure | Individual Mentor turn mechanics; trap lookup |
| `fulcrum-mentor-turns` | Turn granularity and decomposition; prompt shape and length ceiling; session vs conversation; staleness guard before mutating; polling cadence; run-id durability; publish sequencing | What to build; how to prove it landed |
| `fulcrum-engine-traps` | The construct-indexed trap registry: aggregates, repeaters, links, icons, dates, REST, static entities, charts, overlays, wizards, theming | Turn mechanics; verification procedure |
| `fulcrum-verification` | Proof obligations; which instrument catches which defect class; visual capture and comparison; diagnostic REST endpoint pattern; what platform success signals do not mean | Trap causes; orchestration |
| `fulcrum-seed-data` | Idempotent loaders; natural keys; relative timestamps; static entity identifiers; reset paths and their absence | Screen construction |
| `fulcrum-unattended-guardrails` | Stop conditions; fix-turn caps; escalation and halt rules; subagent depth and delegation boundaries; context and call budgeting; checkpoint and handoff discipline; concurrency locks; model tier policy | Anything ODC-construct-specific |

## Tone

Terse, imperative, evidence-first. No hedging, no filler, no praise. A rule per
line where possible. Tables for lookup content. The reader is an agent mid-task
with limited context — every line must earn its place.
