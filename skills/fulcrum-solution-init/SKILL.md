---
name: fulcrum-solution-init
description: Turn raw source material (a BRD, product docs, a Figma or Stitch export, HTML mockups, screenshots, or any mix) into an ODC solution plan and a project repo that a cheaper orchestrator can build from across many unattended sessions. Decomposes the work into apps, agents and workflows, emits a task graph with parallel lanes per app, asks the rigor level, runs read-only tenant checks, and scaffolds the plan, specs and handoff. Use when the user says "start a new OutSystems project", "build this BRD in ODC", "I have a Figma and want an ODC solution", "plan an ODC build", "turn these designs into an OutSystems app", "scaffold an ODC engagement", or hands over source artifacts and asks what to build. Run ONCE per project, before any Mentor build turn.
version: "1.0.0"
requires: ODC MCP server authenticated; Mentor enabled on the tenant; filesystem write access for the project repo; an image-inspection capability and an image-dimension scanner for visual source material; a subagent mechanism for parallel triage
---

# ODC solution init

Phase zero of an ODC engagement. Everything downstream reads what this phase writes.
Run once per project, on the **deep-reasoning** tier (see `../../MODEL-TIERS.md`); every
session after runs **workhorse**: spend the expensive thinking once, so later sessions execute.

## When to use

A solution-sized ask - more than a handful of screens, or several apps, agents or
workflows - with source material that is not yet a spec, and no plan in the repo.

**Not** for one app from one clean source with no decomposition: one app from one
design source (`../fulcrum-design-loop/SKILL.md`), or with no BRD and about five or
fewer steps, the router's micro profile (`../fulcrum-project-state/references/micro-profile.md`), which asks the step-2
app-creation question itself. **Not** for a repo this skill scaffolded: edit the plan.

## Does not own

Owned here: source triage, the platform decision, the probe, decomposition, the task
graph, sizing, the scaffold, the handoff structure. Everything else belongs to a sibling:

| Need | Owner |
|---|---|
| Mentor turn shape, polling, run-id durability, publish sequencing | `../fulcrum-mentor-turns/SKILL.md` |
| Why a construct fails (aggregates, repeaters, icons, dates, overlays) | `../fulcrum-engine-traps/SKILL.md` |
| Proof obligations, the rigor table, visual capture | `../fulcrum-verification/SKILL.md` |
| TASKS schema v3 column values; selecting and batching the frontier | `../fulcrum-project-state/references/file-schemas.md`; `../fulcrum-loop-engine/SKILL.md` |
| Loader idempotence, natural keys, static entity identifiers | `../fulcrum-seed-data/SKILL.md` |
| Stop conditions, fix-turn caps, delegation depth, model tier policy | `../fulcrum-unattended-guardrails/SKILL.md` |
| No source material exists at all - nothing written, no designs, no mockups | `../fulcrum-discovery/SKILL.md` |

Cross-reference these; never restate their rules beyond a one-line pointer.

## Procedure

Run in order. Steps 2 and 3 gate step 4 - never plan before both are settled.

### 1. Source triage

Source material arrives near-useless more often than not. Do not read it as a spec.

- **Dimension-scan every file first**, before any visual inspection. Bucket by size and
  aspect: brand assets, full-screen frames, icon glyphs, fragment crops, blanks. In the
  reference corpus a first-pass visual triage and a later systematic dimension scan
  disagreed on the frame count (67 vs 87) - the scan is the reliable census, so run it
  first and let inspection sample within its buckets. `[VERIFIED]`
- **Inspect a representative sample per bucket, not every file.** Expect a very low
  signal ratio: 2 of 138 exports were genuinely upload-ready assets. `[VERIFIED]`
- **Deduplicate to screen/flow groups.** Filter states of one list template are one
  group, not six.
- **Derive a written brief when none was supplied**, into the repo, as the domain source
  of truth. Nothing downstream should ever re-triage raw exports.
- **Record every correction to the incoming brief explicitly.** An unrecorded correction
  gets re-litigated by a later session.
- **Resolve asset provenance and rights now.** If the source cannot be re-exported
  cleanly, every asset gap is a manual-crop task, not a re-export task, and is work.
  Bucket table, sampling rule, asset-upload handoff: `references/source-triage.md`.

### 2. Target-platform decision - before planning, not during

Reversing it means re-creating the app and re-building every screen. Make it a written,
checked decision with its consequence stated. Decide and record: web vs mobile
application type; mobile-first vs desktop layout; existing app or fresh shell; which shell.

- Mentor could not add screens to an app created with the **Mobile** application type,
  forcing a Reactive Web app with a phone-width mobile-first layout instead.
  `[SINGLE-OBSERVATION]` `[TENANT]` - ask at intake; otherwise the first real screen row shows it.
- **App creation is a user choice; neither option is the default.** Ask the user: have
  Mentor create the app (`mentor_start_session` then a `mentor_prompt` describing it), or will they
  create a shell app from the standard template in Studio/Portal for Fulcrum to attach
  (`assetRefs`). Record the answer. Either way, immediately after creation check
  screen access and the default screen:
  `../fulcrum-engine-traps/references/access-security-and-settings.md`. Mechanics:
  `../fulcrum-mentor-turns/references/mcp-surface.md#creating-and-loading-an-asset`.
- **Never use a System or template module as the shell.** `Template_*` and sample-data
  modules are refused by Mentor's Model API. Use a fresh app instead (either path above). `[VERIFIED]`
- **Disambiguate near-name-collision apps before the first build turn.** A stale scaffold
  with a similar name is how a session builds into the wrong app. Record the exact app
  identifier in `tenant-profile.md`, never the display name.
- **Ask `Rigor` (`demo | pilot | production`) in every mode**, unless `project.md` or the
  router's batch already holds the answer. Never defaulted, never inferred: it fixes how
  much proof the plan pays for, and a guess overbuilds a demo or under-proves production.
  Record it in `project.md`. What it sets: `../fulcrum-verification/SKILL.md`, "Gates and rigor".

### 3. Tenant capability probe

One read-only, free pass that writes `tenant-profile.md` into the repo. After this, **no
downstream skill hardcodes a tenant fact** - they all read the profile. Free reads fill
what they can: tool listing, environment keys, target app identity. Any other fact is
asked at intake or marked `first-row`, for the first real row that needs it. Two hard rules:

- **A Mentor answer of "that block does not exist" is not evidence.** A block reported
  absent was later found to exist and be public. `[VERIFIED]` The first real row that
  needs a block references it and reads what lands. Record the observation, never the
  assertion.
- **Gate on Mentor liveness before any build begins.** In a tenant-wide outage every run
  returned `succeeded` with a summary saying no application was selected.
  `[SINGLE-OBSERVATION]` The gate: a cheap read-only prompt returns a summary **naming
  real content from the actual app**. `attempted_change` is false on a healthy read-only
  turn too, so that field is not the signal.

Checklist, probe prompts, evidence format: `references/tenant-capability-probe.md`; fill
`templates/tenant-profile.md`.

### 4. Solution decomposition

Decide and write into the plan:

- **Apps** - one per coherent persona-plus-lifecycle or module boundary, not per screen area, never for parallelism alone.
- **Agents and workflows** - which behaviour is an agent, which a workflow, which just a
  server action. Name each and its trigger.
- **Entity ownership** - exactly one owning app or library per entity. Consumers
  reference the owner and never redeclare it; shared reference data belongs at the lowest
  level everything above it can consume. `[UNVERIFIED]` on multi-app plans.
- **Deployable units** - what ships together, and so what must be demoable together.
- **Prefer fewer apps.** Each extra boundary buys isolation and costs a cross-app
  dependency every later step must respect.

### 5. Task graph and step sizing

- **Emit a graph, not a stage list.** Write `TASKS.md` rows (schema v3): `App`, `DependsOn`
  with true data dependencies only, `Batchable`, `Risk`. A phase is a derived label, a
  layer in the graph, never a gate.
- **Shape.** Foundation rows (shared entities, contracts) first and serial, lanes fan out
  per app, gate rows last. Lane order: base, UI, logic, polish.
  A cross-app contract is an explicit upstream row, so consumers depend on the contract,
  not the whole app. Parallelism only comes from different apps.
- **No spike or probe rows.** Do not plan a row to test a platform capability. An unknown
  is asked at intake, or tried on the first real row, which fails fast; traps already
  live in skills. A spike consumes hours, publishes throwaway revisions, and proves what
  the first real row would prove anyway.
- **Gates are ordinary rows:** a join per consumer app, a final G2, at `demo` a demo script.
- **Every phase ends demoable. Data before screens.** Seed before any screen reads it.
- **A 12-screen plan is already not a one-shot.** Budget from the measured cost anchors
  in the reference: seed steps are the most expensive class. `[SINGLE-OBSERVATION]`
- **Right-sizing test.** A step is right-sized when a *fresh* agent with no history can
  execute it against one written spec within **one build turn (a build pass of up to 4
  short turns counts as one) plus two fix turns**. If it cannot, split it.

Gate rows, sizing tables, slice ordering: `references/decomposition-and-sizing.md`.

### 6. Author the specs

One spec file per step up to the first join, written now - not left to the build session. Specs
are the interface between this expensive phase and every cheap one after it. Anatomy
that worked: scope plus what is explicitly **not** covered; judgment calls resolved
outright; standing rules restated inline so the build agent needs no other file; numbered
turn blocks using **VISUAL LAYOUT / DATA FLOW / FUNCTIONAL BEHAVIOR / PRESENTATION
ORDER**, where DATA FLOW names entities and attributes only, never aggregates, screen
actions or local variables; an invariant pre-check that can halt the run; non-goals; and
a checklist of numbered, verifiable, screenshot-anchored assertions.

Never "should look right". Good specs read as executable test plans. `[SINGLE-OBSERVATION]`
Copy `templates/spec-template.md` per step.

### 7. Scaffold the repo and the handoff

The handoff document is **two parts**: stable **RULES** that accumulate, and a **BRIEF**
replaced wholesale every session. Never a growing narrative of past steps - that is what
the append-only build log is for. Scaffold: the derived brief, the plan, `TASKS.md`,
`specs/`, a per-step build-pattern log, a run-id log, `tenant-profile.md`, the handoff.

Layout, file roles, handoff shape and three observed failure modes: `references/repo-scaffold.md` (heading "Failures to design against"), `templates/handoff-template.md`.

## Routing per-app bootstrap

This skill decides the decomposition and the plan; it does not bootstrap an app itself.
Route each app's first build by the source type available **for that app**:

| Source for that app | Route to |
|---|---|
| Visual or code design - screenshots, concept images, Figma frames, HTML, TSX/React | `../fulcrum-design-loop/SKILL.md`, entered at its Intake with Q1 (app creation) and Q7 (form factor, if applicable) pre-answered here and step ids from this plan; the intake steps it still runs are listed in its "Intake" section, and every unanswered batch B question is asked before capture. Per app: `.fulcrum/design/<app>/`, one `project.md` `design` entry, at most 6 screens |
| Text only - derived brief, prose spec | `../fulcrum-mentor-turns/SKILL.md` per spec |
| Both | design loop for theme, chrome and screens; this skill's specs for entities and logic, so the design loop omits its P1.04 Data and P1.05 Seed steps when this plan already has the entity and seed steps |

Fulcrum never runs an external bootstrap skill's procedure. Where `outsystems-design-to-app`
is installed, the design loop may read its reference data as `[UNVERIFIED]` input; its
batching, prompt, session and publish procedure conflicts with Fulcrum rules
(`../fulcrum-design-loop/references/official-skill-interop.md`).

## Exit gate

Do not hand off until all of these hold:

1. A derived written brief exists in the repo.
2. The target-platform decision is recorded with its consequence, and `Rigor` is in `project.md`.
3. `tenant-profile.md` exists; every row has recorded evidence or is marked `first-row`.
4. The Mentor liveness gate passed against the actual target app, or is deferred because Mentor creates it.
5. The plan names apps, agents, workflows, entity owners and deployable units; `TASKS.md` holds the graph with its gate rows, no spike rows.
6. Every step up to the first join has a spec file passing the right-sizing test.
7. The handoff has a RULES part and a BRIEF part, and the BRIEF lists the current frontier.
