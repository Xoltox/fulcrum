# Fulcrum - authoring contract

Read this before writing or editing any skill in `skills/`. It is binding.

## What Fulcrum is

A harness-agnostic skill set for driving **OutSystems ODC Mentor** through long,
largely unattended build sessions with real guardrails. Derived from several ODC
builds across different tenants and build styles - zero-shot, one-shot,
multi-shot and long-running - plus their incident and build logs.

The unit of work is a **solution**, not an app: possibly several apps, agents and
workflows under one plan.

## Hard rule 1 - harness agnostic

These skills must work in Claude Code, Antigravity, Cursor, Codex, or a bare
scripted agent loop. Therefore:

- **Never name a harness-specific tool as the required instrument.** Say what
  capability is needed and let the agent map it.
  - Wrong: "use the Agent tool with `subagent_type: general-purpose`"
  - Right: "dispatch a subagent using your harness's subagent mechanism"
  - Wrong: "screenshot with Playwright"
  - Right: "capture with a browser automation capability (browser MCP tool
    preferred when available; a headless driver such as Playwright otherwise)"
- **Never name a model.** Use the tier vocabulary in
  `skills/fulcrum-unattended-guardrails/references/model-tiers.md`
  (`deep-reasoning`, `workhorse`, `poller`). Only `MODEL-TIERS.md` maps tiers to
  concrete model names, and it does so for more than one vendor.
- **MCP tool names are allowed** when referring to ODC MCP operations
  (`mentor_start_session`, `mentor_request_upload`,
  `mentor_prompt`, `mentor_get_run`, `mentor_get_event`, `publish_status`,
  `env_app`, `app_revisions`, `env_list`, `context_*`). Publishing is a
  `mentor_prompt` "Publish" turn; creating and editing an asset is a
  `mentor_prompt` too. Do not name `mentor_create_asset` or `mentor_load_asset`
  (deprecated, "do not call" on the 2026-10-30 listing), `mentor_publish`
  (deprecated; absent on the 2026-10-16 listing), `app_create`, `publish_start`, `mentor_start` or `mentor_cancel` (absent from the
  live surface) as instruments. These are the ODC surface itself, not
  a harness feature. Write them bare - no `mcp__outsystems__` prefix, which is
  Claude-Code-specific wiring.
- **No harness-specific frontmatter or syntax in a skill.** `allowed-tools`,
  slash-command syntax and `$ARGUMENTS` are one harness's wiring. Leave them
  out entirely - an installing agent adds whatever its own harness needs.
- **Quirks of one harness go in `HARNESS-NOTES.md`**, never in a skill, and are
  written as one harness's observation that another may or may not share. A
  skill states the capability it needs and the property that must hold; the
  harness picks the implementation.

## Hard rule 2 - platform truth by default

Every rule in a skill must be **general ODC/Mentor truth**, not incident history
from one build and not one tenant's configuration.

- Strip all project nouns: no client or project names, no domain-entity names
  specific to a real engagement, no project-specific CSS class prefixes, no
  specific revision numbers. Where a concrete example genuinely aids
  comprehension, invent a neutral one (`Order`, `Shipment`, `Customer`).
- **Tenant-varying facts do not get asserted.** They get read, asked, or observed on the
  first real row. See below.
- Keep the *consequence*, drop the anecdote. "Deleting a Gallery's default `List`
  child collapses the repeater to one row while validation and publish stay
  clean" is platform truth. "This happened on step 18" is not.

### Tool facts live in one place

Tool-specific facts (names, parameters, error texts, completion signals, publish
mechanics) live in `skills/fulcrum-mentor-turns/references/mcp-surface.md`, each with
a date. Every other file links to it and restates at most one line. A tool fact written
anywhere else will drift when the surface changes. The baseline of tool and parameter
names is `skills/fulcrum-mentor-turns/references/mcp-snapshots/`.

### The tenant profile contract

Facts that vary by tenant, licence, or platform version live in `tenant-profile.md` in
the project repo. A read-only, free capability probe during `fulcrum-solution-init`
writes the file: the Mentor liveness gate, plus what a read can answer. A fact no free
read answers is asked at intake, or marked `first-row` and recorded when the first real
row that needs it lands. Never a spike: a row built only to learn a fact consumes hours
and publishes throwaway revisions to prove what that first real row proves anyway.

Lookup rule: the agent looks for `tenant-profile.md` in the project's `.fulcrum/`
first, then walks up parent directories and uses the nearest one found; it writes a
new one in the project's `.fulcrum/` only if none is found. Users organise folders
differently, so no layout is imposed.

Skills must **reference the profile, never hardcode the answer**:

- Wrong: "Icon names are PascalCase - write `ArrowRight`."
- Right: "Check `tenant-profile.md` for the icon-font family and its name
  casing. A wrongly cased icon name renders blank or falls back to a default
  glyph with no error, so quote names in the convention the profile records."

Facts belonging in the profile include, at minimum: which UI blocks exist
(`Modal`, `BottomSheet`, `ActionSheet`, `Sidebar`, `Accordion`, `Wizard`);
the OutSystems UI version; icon-font family and name casing; available `ModelFeature_*` flags;
meridiem/format-token behaviour; whether server actions can be marked public;
Mentor backend identifier; and the Mentor prompt-length ceiling.

## Hard rule 3 - state the mechanism, not just the ban

Measured finding from the source build: prompts that named *why* a construct
fails stopped the failure recurring; prompts that only said "don't" did not.

- Weak: "Do not add an AggregatedAttribute here."
- Strong: "Do not add an AggregatedAttribute to this aggregate - an aggregate
  that carries one collapses `.List` to a single summary row, so the repeater
  renders exactly one item while validation and publish both stay clean."

Every rule carries its failure mode. If you cannot state what breaks, the rule
is not ready to write.

## Hard rule 4 - mark evidence strength

Tag any claim that is not directly observed. The tags and what each means live once
in `skills/fulcrum-verification/references/evidence-tags.md`, an installed file, because
agents read and write them at run time. Never restate them in a skill.

## Skill file layout

```
skills/<skill-name>/
  SKILL.md          # thin: when to use, the procedure, pointers. Target <200 lines.
  references/*.md   # depth, loaded on demand. One file per coherent topic.
```

`SKILL.md` is what an agent reads first and may be all it reads. It must be
self-sufficient for the common path and must say explicitly which reference file
to open for which situation. Do not write a 600-line SKILL.md.

**Reviewed exception:** `skills/fulcrum-unattended-guardrails/SKILL.md` ran
~238 lines before being trimmed to about 200; the exception stands for growth. The repo owner reviewed and accepted this as a one-time exception
specific to that file - do not "fix" it by gutting content, and do not cite it
as licence to ignore the <200 target elsewhere.

### Agent role layout

```
agents/
  roles/<name>.md           # harness-neutral role definition
  <harness>/<name>.md       # adapter for one harness
```

`agents/roles/` follows the same rules as skills: no harness names, no model
names, tool classes only (`run-read`, `mentor-drive`, `published-read`,
`attachment-upload`, `blocking-wait`, `file-read`, `file-write-scoped`, `spawn-poller`, `http-probe`,
`browser-automation`).
`agents/<harness>/` adapters may use that harness's names, tools and models.
Skills reference roles **by role name only** (`fulcrum-poller`,
`fulcrum-mentor-driver`, `fulcrum-verifier`, `fulcrum-renderer`, `fulcrum-capturer`), never
by adapter path.

### Frontmatter - portable subset only

```yaml
---
name: <directory name, exactly>
description: <"Use when ..." first, with concrete trigger phrases a user would
  actually type, then what it does. Under 1,536 characters. This is the
  auto-trigger surface - be specific.>
version: "1.0.0"
requires: <capabilities in prose, e.g. "ODC MCP server authenticated; Mentor
  enabled on the tenant; a browser automation capability for visual proof">
---
```

No `allowed-tools`, no `license`, no `compatibility`, no `metadata:` block.
Anything a specific harness requires is added at install time by the agent
doing the installing, never carried in the source.

`name` must match the directory name exactly, and must be globally unique - the
source corpus contains two skill directories declaring the same `name`, which
made one of them unresolvable.

## Cross-references

- Link by **relative path**: `see ../fulcrum-verification/SKILL.md`, or
  `references/aggregates.md`.
- **Never use `§`-numbered anchors.** Every such reference in the source corpus
  was dangling because the target files had no numbered headings.
- **Root documents are not installed.** `install.sh` and `INSTALL.md` copy `skills/`
  and agent adapters only, so a skill or role never links to a root document: the link
  is dead on every install. An authoring pointer is a plain mention with no path.
  Content an agent needs at run time lives in a skill reference and is linked there.
- Prefer naming a heading verbatim over citing a line number. Line numbers rot.

## Canonical facts - use these exact values

These were wrong or missing in the source corpus. They are correct here.

**Waiting is a capability, not a shell command.** A wait must neither spin nor
accumulate context. Preference order: a native scheduling or wait primitive the
harness provides (works at any agent depth) > a delegated poller whose context
is discarded > an in-process sleep call. Verify once at session start that the
chosen mechanism actually suspends - a mechanism the harness silently swallows
turns a poll loop into an unbounded spin. Never mandate one implementation;
harness-specific findings belong in `HARNESS-NOTES.md`.

**Mentor polling cadence - the rate depends on who is paying for the poll.**
Each poll is a request *and* a response, and both persist in the context of
whoever issued them. That cost, not wall clock, is what the cadence optimises.

- **With a discardable poller** (a delegated agent whose context dies with it):
  **45 s** for turns where Mentor *answers* - read-only inventory, invariant
  checks, "report what you see"; **90 s** for turns where Mentor *changes the
  model* - any build or fix turn, and all publish polling.
- **With no delegation available** - the orchestrator polls in its own context:
  **90 s floor for everything**, answer-back turns included, and longer still
  for a turn known to run long. Polling fast here grows the orchestrator's
  context on every iteration, which is cumulative and unrecoverable.
- The 45 s rate is affordable *only* because a throwaway context absorbs it.
  Never carry that rate into an undelegated loop.
- The server's pacing field is `pollIntervalMs`; it is a hint that Fulcrum overrides upward. Drain rule: a run is not read until a page returns `hasMore: false` with no `nextCursor` (`skills/fulcrum-mentor-turns/references/mcp-surface.md#reading-a-run`).

**No model-layer path to live row data.** `db_query`, `exec_in_app` and
`test_setup_start` / `test_setup_status` were absent on the 2026-10-16 listing
(listed on 2026-10-09; absence may be per tenant or per server version,
re-check on the next probe). While absent, do not plan on them. Even when
`db_query` listed, its own schema said no template returns rows in v1
(`[SCHEMA]`, 2026-10-09), so it was never a row-data instrument. Live row
data comes from a temporary diagnostic REST endpoint probed over HTTP, read
with `app_logs` / `app_traces` and published structure from `context_*`;
Mentor answer-back is belief only. The procedure is
`skills/fulcrum-verification/references/diagnostic-endpoint.md`; tool
availability is in `skills/fulcrum-mentor-turns/references/mcp-surface.md`.

**Model tiering - phase-based, not flat:**

- Project init (ingest sources, derive the solution plan, scaffold the repo):
  `deep-reasoning` tier, optionally `workhorse` if budget is tight.
- Every session after init: `workhorse` tier orchestrator.
- All poll loops and wait states: `poller` tier.
- Tiers are resolved per install, and may be overridden per project. See
  `skills/fulcrum-unattended-guardrails/references/model-tiers.md` for the resolution
  order and `MODEL-TIERS.md` for the local-override contract.

**Subagent depth - one level, with a single narrow exception:**

- Mutating work is **depth 1**, always: the orchestrator dispatches directly and
  no build agent spawns its own children.
- **Exception, polling only.** The Mentor-driver role may spawn exactly one
  nested poller when its own tier is expensive and the phase is long - otherwise
  the expensive parent accumulates poll traffic in its context for the whole run.
  The nested agent may do nothing but wait and report; every other role never
  spawns. [VERIFIED] on one harness (2026-10-08, repeated in a project journal);
  [UNVERIFIED] elsewhere, where a sibling poller is the fallback.
- This exception buys nothing when the poller tier is already cheap, or when the
  harness offers a native wait primitive that costs no context at any depth.
  Prefer the primitive; nest only to isolate cost.
- No other nesting. A depth dial is only as good as an agent's willingness to
  respect it, which is exactly what cannot be trusted unattended.

**Delegation posture is a default, not an advanced mode.** Aggressive
orchestration is how this skill set is meant to run, so it belongs on the
always-visible surface (`AGENTS.md`) and not only inside the guardrails skill, whose
`SKILL.md` is the installed statement.
- Full rationale and the vendor mapping live in `MODEL-TIERS.md`. A flat
  single-tier policy appears in the source corpus as a budget-exhaustion
  artifact - record it as history, never as the rule.

**Gap analysis never assumes how the app got there.** An app under assessment may
be fresh generator output, or years of work by many people and agents, or both.
Establish provenance before judging anything, and classify findings into five
kinds rather than one:

- **Gap** - required, absent.
- **Drift** - built, but not as specified. May be a deliberate decision nobody
  wrote down. Look for a decision record before calling it a defect.
- **Stale requirement** - the document no longer describes intended behaviour.
  The document is the thing that is wrong.
- **Undocumented addition** - present in the app, absent from the requirements.
  Could be valuable, could be scope creep; never silently a defect.
- **Unfalsifiable requirement** - the requirement cannot be assessed as written
  (it defers the specifics, or states no observable outcome). Scoring an app
  against one invents a gap. Report it against the document, naming what would
  have to be decided before the requirement can be judged at all.

Only the first kind is a defect by default. A mature codebase produces mostly the
other three, and treating deviation as failure there manufactures work and
destroys trust in the report.

**A coverage figure must state its denominator.** "3 of 5 named sub-requirements
present" is reproducible; a bare percentage is a judgement wearing the costume of
a measurement. Charts and aggregate figures are wanted - they are what makes a
report usable - but every number must be recomputable from the itemised evidence
beside it.

**`JOURNAL.md` absorbs `BUILD-LOG.md`. One role, one file - split by session.** The
append-only history of what happened is `.fulcrum/journal/<session-id>.md`, one file
per working session, carrying a line schema rather than a prose narrative. Lines merge
as adjacent lines; prose paragraphs conflict and need a human to adjudicate them under
time pressure. A line schema is also the only form a resuming agent can slice
mechanically. `.fulcrum/JOURNAL.md` keeps the name and becomes the **session index**,
one row per session, rich enough that resume and oscillation detection both answer
from the index alone - a monolithic journal makes every reader pay for the whole
project history to ask about the last three steps. Do not re-introduce `BUILD-LOG.md`
under any name, and do not fork a second history file. Schema:
`skills/fulcrum-project-state/references/file-schemas.md`, headings "JOURNAL.md - the
session index" and `journal/<session-id>.md`.

## Skill boundaries - stay in your lane

Overlap causes mis-triggering. One topic, one owner:

| Skill | Owns | Explicitly does NOT own |
|---|---|---|
| `fulcrum-solution-init` | Ingesting source artifacts; decomposing a solution into apps/agents/workflows; emitting the task graph (foundation, lanes, gate rows, cross-app contracts) and the no-spike rule; step sizing; asking `Rigor` at init; repo scaffold; the read-only tenant capability probe; the handoff document structure | Individual Mentor turn mechanics; trap lookup; frontier selection and batching; what `Rigor` sets |
| `fulcrum-mentor-turns` | Turn granularity and decomposition; prompt shape and length ceiling; session reuse vs fresh session; staleness guard before mutating; polling cadence; run-id durability; publish sequencing | What to build; how to prove it landed |
| `fulcrum-engine-traps` | The construct-indexed trap registry: aggregates, repeaters, links, icons, dates, REST, static entities, charts, overlays, wizards, theming, agents, workflows, sample sign-in | Turn mechanics; verification procedure |
| `fulcrum-verification` | Proof obligations; the gates G0 to G3 and the rigor table (once, here; others point to it); which instrument catches which defect class; visual capture and comparison; diagnostic REST endpoint pattern; what platform success signals do not mean | Trap causes; orchestration |
| `fulcrum-render-check` | Executing renders: browser preflight, sign-in mode choice (anonymous, generated sample personas, user hand-off), render timing after publish, evidence capture, security observations a render surfaces | What counts as proof (verification); why a construct renders wrong (traps); the verdict |
| `fulcrum-seed-data` | Idempotent loaders; natural keys; relative timestamps; static entity identifiers; reset paths and their absence | Screen construction |
| `fulcrum-gap-analysis` | Assessing an app that already exists against the requirements it was meant to satisfy: establishing build provenance, requirement-to-artifact traceability, classifying gaps vs drift vs stale requirements vs undocumented additions vs unfalsifiable requirements, repair-versus-rebuild, sequencing remediation | How to build or prove any individual fix; trap causes |
| `fulcrum-unattended-guardrails` | Stop conditions, including the stall decision; fix-turn caps as a ceiling; escalation and halt rules; subagent depth and delegation boundaries, including the in-flight cap on parallel drivers; context and call budgeting; checkpoint and handoff discipline; concurrency locks; model tier policy | Anything ODC-construct-specific; the iteration mechanism itself - selecting, dispatching, polling, recording and advancing is `fulcrum-loop-engine`'s |
| `fulcrum` | The router and entry point: detecting project state from the filesystem, resuming an engagement, mode selection, asking `Rigor` on first run and on resume when it is missing, proposing the micro profile for the user to confirm, question-asking discipline in `guided` mode, dispatching to the right skill | Anything it routes to. It performs no Mentor turn, no verification, no planning and no state-file schema of its own |
| `fulcrum-project-state` | Where durable state lives and what shape it has: the `.fulcrum/` file set and each file's schema, TASKS schema v3 and its migration, the full and micro profiles and which files each requires, who writes which file, append-only versus rewritten discipline, crash-idempotent write ordering, the runtime lease enforcing one Mentor session per app, the decision record gap analysis consumes, the halt record | What goes in any of those files. It never decides what to build, when to stop, what counts as proof, or how to iterate |
| `fulcrum-loop-engine` | The iteration mechanism: select the runnable frontier grouped by app, batch, precondition and staleness check, dispatch parallel lanes, poll, verify, record, advance per lane; the bounded fix-loop; oscillation and stall detection (detect only); crash-idempotency of a single iteration; per-iteration budget accounting | Stop conditions and halt rules - those are `fulcrum-unattended-guardrails`'. Also not what to build |
| Out of family: external systems and integration targets (not a skill) | Building and deploying the system - another vendor's server, a workflow engine, a third-party API, a service another team builds, its infrastructure - happens outside Fulcrum, under the user's own process. It appears in `TASKS.md` only as `Turn: external` rows | Its contract, which is Fulcrum's: `.fulcrum/external/<system>.md` (template `skills/fulcrum-project-state/templates/external-system.md`: endpoint and auth, payload contract, error codes, verified log locations), owned by `fulcrum-project-state`. It **must exist before the ODC step that consumes the system starts** |
| `fulcrum-design-loop` | One design source for one app built into a published app: design capture and the design spec format; the block-mapping gate; the build lanes (image, Studio, text) and the Studio hand-off; step decomposition of a captured design; render-compare against the source and diff triage | Turn mechanics, traps, proof rungs, render execution, seed loaders, iteration, stop rules; the `holder: user` lease (`fulcrum-project-state`) |
| `fulcrum-demo` | The demo script `.fulcrum/demo-script.md` and its format; the demo readiness checklist; the optional scripted in-app tour | Gate definitions and what `demo` rigor runs; sign-in mechanics; seed loaders; the sample sign-in build |
| `fulcrum-discovery` | Interviewing a user who has an idea but no written requirements, and producing the source material - a BRD or equivalent spec - that `fulcrum-solution-init` then ingests | Decomposition, sizing and planning; the `Rigor` question. It stops at the spec; `fulcrum-solution-init` takes it from there |

## Mode and posture

Three settings, **three orthogonal axes**: mode, posture and rigor. Never collapse them
into one dial. Their definitions, the opt-in rule and the rigor rules live once, in
`skills/fulcrum/references/mode-and-posture.md`, an installed file, because agents need
them at run time. Never restate them.

**All three settings are recorded in `.fulcrum/project.md`** - see
`skills/fulcrum-project-state/SKILL.md`, heading "Mode and posture" - never in the
installed skill files. Precedent: `MODEL-TIERS.md`, heading "The install interview
must not edit installed files". Installed content carrying project state makes every
update fight the user's edits and lets the deployed copy drift from source.

**Mode is NOT a branch inside each skill.** Four of the seven original `SKILL.md`
files are already at or over the 200-line target and a fifth sits one line under it,
so a per-skill mode fork is unaffordable and would breach the skill file layout rule
above. Mode is an **interaction contract owned by the router** (`fulcrum`), not a
second code path in every skill. A skill states its procedure once; the router decides
what to ask before dispatching into it.

## Tone

Terse, imperative, evidence-first. No hedging, no filler, no praise. A rule per
line where possible. Tables for lookup content. The reader is an agent mid-task
with limited context - every line must earn its place.
