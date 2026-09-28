# Fulcrum — authoring contract

Read this before writing or editing any skill in `skills/`. It is binding.

## What Fulcrum is

A harness-agnostic skill set for driving **OutSystems ODC Mentor** through long,
largely unattended build sessions with real guardrails. Derived from several ODC
builds across different tenants and build styles — zero-shot, one-shot,
multi-shot and long-running — plus their incident and build logs.

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
  (`mentor_start_session`, `mentor_create_asset`, `mentor_load_asset`,
  `mentor_prompt`, `mentor_get_run`, `mentor_publish`, `publish_status`,
  `env_app`, `app_revisions`, `context_*`). These are the ODC surface itself, not
  a harness feature. Write them bare — no `mcp__outsystems__` prefix, which is
  Claude-Code-specific wiring.
- **No harness-specific frontmatter or syntax in a skill.** `allowed-tools`,
  slash-command syntax and `$ARGUMENTS` are one harness's wiring. Leave them
  out entirely — an installing agent adds whatever its own harness needs.
- **Quirks of one harness go in `HARNESS-NOTES.md`**, never in a skill, and are
  written as one harness's observation that another may or may not share. A
  skill states the capability it needs and the property that must hold; the
  harness picks the implementation.

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

- Wrong: "Icon names are PascalCase — write `ArrowRight`."
- Right: "Check `tenant-profile.md` for the icon-font family and its name
  casing. A wrongly cased icon name renders blank or falls back to a default
  glyph with no error, so quote names in the convention the probe confirmed."

Facts belonging in the profile include, at minimum: which UI blocks exist
(`Modal`, `BottomSheet`, `ActionSheet`, `Sidebar`, `Accordion`, `Wizard`);
icon-font family and name casing; available `ModelFeature_*` flags;
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
- `[SCHEMA]` — asserted by the vendor's own MCP tool documentation, not observed
  live. Stronger than inference: the vendor is describing its own system.
  Weaker than observation: documentation drifts from behaviour, and a schema
  states intent, not what a given tenant actually does. Keep it distinct —
  collapsing it into `[VERIFIED]` launders documentation as field evidence,
  which is exactly what this rule exists to prevent. Promote to `[VERIFIED]`
  only on a live observation.

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

**Reviewed exception:** `skills/fulcrum-unattended-guardrails/SKILL.md` runs
~238 lines. The repo owner reviewed and accepted this as a one-time exception
specific to that file — do not "fix" it by gutting content, and do not cite it
as licence to ignore the <200 target elsewhere.

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
Anything a specific harness requires is added at install time by the agent
doing the installing, never carried in the source.

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

**Waiting is a capability, not a shell command.** A wait must neither spin nor
accumulate context. Preference order: a native scheduling or wait primitive the
harness provides (works at any agent depth) > a delegated poller whose context
is discarded > an in-process sleep call. Verify once at session start that the
chosen mechanism actually suspends — a mechanism the harness silently swallows
turns a poll loop into an unbounded spin. Never mandate one implementation;
harness-specific findings belong in `HARNESS-NOTES.md`.

**Mentor polling cadence — the rate depends on who is paying for the poll.**
Each poll is a request *and* a response, and both persist in the context of
whoever issued them. That cost, not wall clock, is what the cadence optimises.

- **With a discardable poller** (a delegated agent whose context dies with it):
  **45 s** for turns where Mentor *answers* — read-only inventory, invariant
  checks, "report what you see"; **90 s** for turns where Mentor *changes the
  model* — any build or fix turn, and all publish polling.
- **With no delegation available** — the orchestrator polls in its own context:
  **90 s floor for everything**, answer-back turns included, and longer still
  for a turn known to run long. Polling fast here grows the orchestrator's
  context on every iteration, which is cumulative and unrecoverable.
- The 45 s rate is affordable *only* because a throwaway context absorbs it.
  Never carry that rate into an undelegated loop.
- Ignore the server's `pollAfterMs` field.

**`db_query` returns no rows — universal, not tenant-varying.** `[SCHEMA]` It is
not a model-layer SQL path. It runs only against a test harness stood up by
`test_setup_start`, requires that call's `test_app_url` + `shared_secret`, and
accepts only SQL templates declared upfront in its `query_templates`. Its own
schema states that no template, `SELECT` included, returns rows in v1 — every
template comes back with rowcount 0. So an empty result is a documented v1
platform limitation on every tenant, not tenant variance: there is no
model-layer path to live row data anywhere. Do not probe it, do not carry a
`db_query` row in `tenant-profile.md`, and do not re-derive this. The instrument
for live row data is `exec_in_app` against a harness fork; that procedure is
`skills/fulcrum-verification/`'s, not this file's.

**Model tiering — phase-based, not flat:**

- Project init (ingest sources, derive the solution plan, scaffold the repo):
  `deep-reasoning` tier, optionally `workhorse` if budget is tight.
- Every session after init: `workhorse` tier orchestrator.
- All poll loops and wait states: `poller` tier.
- Tiers are resolved per install, and may be overridden per project. See
  `MODEL-TIERS.md` for the resolution order and the local-override contract.

**Subagent depth — one level, with a single narrow exception:**

- Mutating work is **depth 1**, always: the orchestrator dispatches directly and
  no build agent spawns its own children.
- **Exception, polling only.** A subagent may spawn one nested poller when its
  own tier is expensive and the phase is long — otherwise the expensive parent
  accumulates poll traffic in its context for the whole run. The nested agent
  may do nothing but wait and report. [SINGLE-OBSERVATION]
- This exception buys nothing when the poller tier is already cheap, or when the
  harness offers a native wait primitive that costs no context at any depth.
  Prefer the primitive; nest only to isolate cost.
- No other nesting. A depth dial is only as good as an agent's willingness to
  respect it, which is exactly what cannot be trusted unattended.

**Delegation posture is a default, not an advanced mode.** Aggressive
orchestration is how this skill set is meant to run, so it belongs on the
always-visible surface (`AGENTS.md`) and not only inside the guardrails skill.
- Full rationale and the vendor mapping live in `MODEL-TIERS.md`. A flat
  single-tier policy appears in the source corpus as a budget-exhaustion
  artifact — record it as history, never as the rule.

**Gap analysis never assumes how the app got there.** An app under assessment may
be fresh generator output, or years of work by many people and agents, or both.
Establish provenance before judging anything, and classify findings into five
kinds rather than one:

- **Gap** — required, absent.
- **Drift** — built, but not as specified. May be a deliberate decision nobody
  wrote down. Look for a decision record before calling it a defect.
- **Stale requirement** — the document no longer describes intended behaviour.
  The document is the thing that is wrong.
- **Undocumented addition** — present in the app, absent from the requirements.
  Could be valuable, could be scope creep; never silently a defect.
- **Unfalsifiable requirement** — the requirement cannot be assessed as written
  (it defers the specifics, or states no observable outcome). Scoring an app
  against one invents a gap. Report it against the document, naming what would
  have to be decided before the requirement can be judged at all.

Only the first kind is a defect by default. A mature codebase produces mostly the
other three, and treating deviation as failure there manufactures work and
destroys trust in the report.

**A coverage figure must state its denominator.** "3 of 5 named sub-requirements
present" is reproducible; a bare percentage is a judgement wearing the costume of
a measurement. Charts and aggregate figures are wanted — they are what makes a
report usable — but every number must be recomputable from the itemised evidence
beside it.

**`JOURNAL.md` absorbs `BUILD-LOG.md`. One role, one file — split by session.** The
append-only history of what happened is `.fulcrum/journal/<session-id>.md`, one file
per working session, carrying a line schema rather than a prose narrative. Lines merge
as adjacent lines; prose paragraphs conflict and need a human to adjudicate them under
time pressure. A line schema is also the only form a resuming agent can slice
mechanically. `.fulcrum/JOURNAL.md` keeps the name and becomes the **session index**,
one row per session, rich enough that resume and oscillation detection both answer
from the index alone — a monolithic journal makes every reader pay for the whole
project history to ask about the last three steps. Do not re-introduce `BUILD-LOG.md`
under any name, and do not fork a second history file. Schema:
`skills/fulcrum-project-state/references/file-schemas.md`, headings "JOURNAL.md — the
session index" and `journal/<session-id>.md`.
`skills/fulcrum-solution-init/references/repo-scaffold.md` and
`skills/fulcrum-solution-init/templates/handoff-template.md` still describe
`BUILD-LOG.md`; both are stale against this decision and are rewired separately.

## Skill boundaries — stay in your lane

Overlap causes mis-triggering. One topic, one owner:

| Skill | Owns | Explicitly does NOT own |
|---|---|---|
| `fulcrum-solution-init` | Ingesting source artifacts; decomposing a solution into apps/agents/workflows; phase and step sizing; repo scaffold; the tenant capability probe; the handoff document structure | Individual Mentor turn mechanics; trap lookup |
| `fulcrum-mentor-turns` | Turn granularity and decomposition; prompt shape and length ceiling; session vs conversation; staleness guard before mutating; polling cadence; run-id durability; publish sequencing | What to build; how to prove it landed |
| `fulcrum-engine-traps` | The construct-indexed trap registry: aggregates, repeaters, links, icons, dates, REST, static entities, charts, overlays, wizards, theming | Turn mechanics; verification procedure |
| `fulcrum-verification` | Proof obligations; which instrument catches which defect class; visual capture and comparison; diagnostic REST endpoint pattern; what platform success signals do not mean | Trap causes; orchestration |
| `fulcrum-seed-data` | Idempotent loaders; natural keys; relative timestamps; static entity identifiers; reset paths and their absence | Screen construction |
| `fulcrum-gap-analysis` | Assessing an app that already exists against the requirements it was meant to satisfy: establishing build provenance, requirement-to-artifact traceability, classifying gaps vs drift vs stale requirements vs undocumented additions vs unfalsifiable requirements, repair-versus-rebuild, sequencing remediation | How to build or prove any individual fix; trap causes |
| `fulcrum-unattended-guardrails` | Stop conditions; fix-turn caps as a ceiling; escalation and halt rules; subagent depth and delegation boundaries; context and call budgeting; checkpoint and handoff discipline; concurrency locks; model tier policy | Anything ODC-construct-specific; the iteration mechanism itself — selecting, dispatching, polling, recording and advancing a task is `fulcrum-loop-engine`'s |
| `fulcrum` | The router and entry point: detecting project state from the filesystem, resuming an engagement, mode selection, question-asking discipline in `guided` mode, dispatching to the right skill | Anything it routes to. It performs no Mentor turn, no verification, no planning and no state-file schema of its own |
| `fulcrum-project-state` | Where durable state lives and what shape it has: the `.fulcrum/` file set and each file's schema, append-only versus rewritten discipline, crash-idempotent write ordering, the runtime lease enforcing one Mentor session per app, the decision record gap analysis consumes, the halt record | What goes in any of those files. It never decides what to build, when to stop, what counts as proof, or how to iterate |
| `fulcrum-loop-engine` | The iteration mechanism: select task, precondition and staleness check, dispatch, poll, verify, record, advance; the bounded fix-loop; oscillation detection against `JOURNAL.md`; crash-idempotency of a single iteration; per-iteration budget accounting | Stop conditions and halt rules — those are `fulcrum-unattended-guardrails`'. Also not what to build |
| `fulcrum-discovery` | Interviewing a user who has an idea but no written requirements, and producing the source material — a BRD or equivalent spec — that `fulcrum-solution-init` then ingests | Decomposition, sizing and planning. It stops at the spec; `fulcrum-solution-init` takes it from there |

## Mode and posture

Two settings, **two orthogonal axes**. Never collapse them into one dial. An expert
user may want `collaborative`; a `guided` user may want `directive`. Every
combination of the four is legal and must be honoured as written.

**Mode — `guided` | `expert`.** Governs who decides and how much is asked of the user.

| | `guided` | `expert` |
|---|---|---|
| Entry | The router runs automatically and interviews the user | The user invokes skills directly |
| On ambiguity | Block and ask. Offer a small number of options with a recommendation | Proceed under a stated assumption and record it in `DECISIONS.md` |
| Assumptions | Surfaced to the user as they are made | Recorded, not narrated |
| Narration | Says what is about to happen and why, in plain language | Terse |
| Parameters and tiers | Defaults | Overridable per project |

**Posture — `collaborative` | `directive`.** Governs how the harness model talks to
Mentor.

| | `collaborative` (default) | `directive` |
|---|---|---|
| Turn shape | Consult Mentor for the idiomatic ODC approach first, review its proposal against the trap registry in `skills/fulcrum-engine-traps/`, correct only the specific traps, then build | Instruct Mentor exactly what to build |

**`collaborative` is the default at every tier.**

**The failure mechanism.** `directive` posture is a bet that the harness model's ODC
platform knowledge exceeds Mentor's. That bet loses more often as the harness model
gets cheaper. A model issuing strict build instructions on weak platform knowledge
invents non-idiomatic structures Mentor would never have chosen; those pass validation
and publish clean, then surface later as traps. Mentor is the better source of
platform idiom. Fulcrum is the better source of trap avoidance and verification.
`collaborative` posture is what makes that division of labour operational.

**`directive` is an explicit user opt-in and is NEVER auto-selected by tier**, model,
or budget. Same principle as the non-negotiable "never escalate model tier to break a
stuck bug" in `AGENTS.md`: posture is a user decision, never a machine one. A cheaper
tier is a reason to lean harder on `collaborative`, not a licence to switch.

**Both settings are recorded in `.fulcrum/project.md`** — see
`skills/fulcrum-project-state/SKILL.md`, heading "Mode and posture" — never in the
installed skill files. Precedent: `MODEL-TIERS.md`, heading "The install interview
must not edit installed files". Installed content carrying project state makes every
update fight the user's edits and lets the deployed copy drift from source.

**Mode is NOT a branch inside each skill.** Four of the seven original `SKILL.md`
files are already at or over the 200-line target and a fifth sits one line under it,
so a per-skill mode fork is unaffordable and would breach the skill file layout rule
above. Mode is an **interaction contract owned by the router** (`fulcrum`), not a
second code path in every skill. A skill states its procedure once; the router decides
what to ask before dispatching into it.

**Economics.** `collaborative` trades one cheap consult turn for fewer expensive fix
turns. `[UNVERIFIED]` This is a design prediction, not a measurement — no run has been
instrumented to compare the two postures' total turn cost. Do not cite it as a
finding.

## Tone

Terse, imperative, evidence-first. No hedging, no filler, no praise. A rule per
line where possible. Tables for lookup content. The reader is an agent mid-task
with limited context — every line must earn its place.
