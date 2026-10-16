---
name: fulcrum-solution-init
description: Turn raw source material (a BRD, product docs, a Figma or Stitch export, HTML mockups, screenshots, or any mix) into an ODC solution plan and a project repo that a cheaper orchestrator can build from across many unattended sessions. Decomposes the work into apps, agents and workflows, sizes phases and steps, probes the tenant for everything that varies, and scaffolds the plan, specs and handoff. Use when the user says "start a new OutSystems project", "build this BRD in ODC", "I have a Figma and want an ODC solution", "plan an ODC build", "turn these designs into an OutSystems app", "scaffold an ODC engagement", or hands over source artifacts and asks what to build. Run ONCE per project, before any Mentor build turn.
version: "1.0.0"
requires: ODC MCP server authenticated; Mentor enabled on the tenant; filesystem write access for the project repo; an image-inspection capability and an image-dimension scanner for visual source material; a subagent mechanism for parallel triage
---

# ODC solution init

Phase zero of an ODC engagement. Everything downstream reads what this phase writes.
Run once per project, on the **deep-reasoning** tier (see `../../MODEL-TIERS.md`); every
session after runs **workhorse**. That asymmetry is the point - spend the expensive
thinking once, on decomposition and sizing, so later sessions only execute.

## When to use

A solution-sized ask - more than a handful of screens, or more than one app, or apps
plus agents plus workflows - with source material that is not yet a spec, and no repo
that already has a plan and a tenant profile.

**Not** for one app from one clean source with no decomposition: one app from one
design source (`../fulcrum-design-loop/SKILL.md`), or with no BRD and about five or
fewer steps, the router's micro profile (`../fulcrum-project-state/references/micro-profile.md`), which asks the step-2
app-creation question itself. **Not** for a repo this skill scaffolded: edit the plan.

## Does not own

Owned here: source triage, the platform decision, the probe, decomposition, sizing, the
scaffold, the handoff structure. Everything else belongs to a sibling:

| Need | Owner |
|---|---|
| Mentor turn shape, polling, run-id durability, publish sequencing | `../fulcrum-mentor-turns/SKILL.md` |
| Why a construct fails (aggregates, repeaters, icons, dates, overlays) | `../fulcrum-engine-traps/SKILL.md` |
| Proof obligations and visual capture | `../fulcrum-verification/SKILL.md` |
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
  signal ratio: 2 of 138 exports were genuinely upload-ready assets; the other 136 were
  frames, fused icon tiles, and sample-data tooltips. `[VERIFIED]`
- **Deduplicate to screen/flow groups.** Filter states of one list template are one
  group, not six. Reference corpus collapsed raw screen exports by roughly 2.4x.
- **Derive a written brief when none was supplied**, into the repo, as the domain source
  of truth. Nothing downstream should ever re-triage raw exports.
- **Record every correction to the incoming brief explicitly.** Triage overturned two
  stated assumptions in the reference corpus. An unrecorded correction gets
  re-litigated by a later session.
- **Resolve asset provenance and rights now.** If the source cannot be re-exported
  cleanly, every asset gap is a manual-crop task, not a re-export task, and is work.
  Bucket table, sampling rule, asset-upload handoff: `references/source-triage.md`.

### 2. Target-platform decision - before planning, not during

Reversing it means re-creating the app and re-building every screen. Make it a written,
checked decision with its consequence stated. Decide and record: web vs mobile
application type; mobile-first vs desktop layout; existing app or fresh shell; which shell.

- Mentor could not add screens to an app created with the **Mobile** application type,
  forcing a Reactive Web app with a phone-width mobile-first layout instead.
  `[SINGLE-OBSERVATION]` `[TENANT]` - confirm on the current tenant in step 3, don't assume.
- **App creation is a user choice; neither option is the default.** Ask the user: have
  Mentor create the app (`mentor_start_session` then `mentor_create_asset`), or will they
  create a shell app from the standard template in Studio/Portal for Fulcrum to load
  (`mentor_load_asset`). Record the answer. Either way, immediately after creation check
  screen access and the default screen:
  `../fulcrum-engine-traps/references/access-security-and-settings.md`. Mechanics:
  `../fulcrum-mentor-turns/references/mcp-surface.md#creating-and-loading-an-asset`.
- **Never use a System or template module as the shell.** `Template_*` and sample-data
  modules are refused by Mentor's Model API. Use a fresh app instead (either path above). `[VERIFIED]`
- **Disambiguate near-name-collision apps before the first build turn.** A stale scaffold
  with a similar name is how a session builds into the wrong app. Record the exact app
  identifier in `tenant-profile.md`, never the display name.

### 3. Tenant capability probe

One read-only pass that resolves everything tenant-varying and writes `tenant-profile.md`
into the repo. After this, **no downstream skill hardcodes a tenant fact** - they all read
the profile. Must resolve, at minimum: which UI blocks exist and
their real input properties; icon font family and name casing; available `ModelFeature_*`
flags; date and meridiem format-token behaviour; whether server actions can be marked
public; the Mentor backend identifier; the Mentor prompt-length ceiling. Two hard rules:

- **A Mentor answer of "that block does not exist" is not evidence.** A block reported
  absent was later found to exist and be public. `[VERIFIED]` Probe by attempting to
  reference the block and reading what actually lands. Record the observation, never the
  assertion.
- **Gate on Mentor liveness before any build begins.** In a tenant-wide outage every run
  returned terminal status `succeeded` with `attempted_change` false and a summary saying
  no application was selected - including against an unrelated app. `[SINGLE-OBSERVATION]`
  The gate is therefore: a cheap read-only probe returns a summary **naming real content
  from the actual app**. A read-only prompt correctly returns `attempted_change` false,
  so that field is not the signal - the named content is.

Checklist, probe prompts, evidence format: `references/tenant-capability-probe.md`; fill
`templates/tenant-profile.md`.

### 4. Solution decomposition

Decide and write into the plan:

- **Apps** - one per coherent persona-plus-lifecycle boundary, not one per screen area.
- **Agents and workflows** - which behaviour is an agent, which a workflow, which just a
  server action. Name each and its trigger.
- **Entity ownership** - exactly one owning app or library per entity. Consumers
  reference the owner and never redeclare it; shared reference data belongs at the lowest
  level everything above it can consume. Confirm the consumption mechanism against the
  tenant before planning around it. `[UNVERIFIED]`
- **Deployable units** - what ships together, and so what must be demoable together.
- **Prefer fewer apps.** Each extra boundary buys isolation and costs a cross-app
  dependency every later step must respect.

### 5. Phase and step sizing

- **Order global-then-local.** Theme, navigation and data model once, up front. Then
  vertical slices, cheapest and most central first.
- **Every phase ends demoable.** Never leave the solution mid-transformation across a
  session boundary.
- **Data before screens.** Seed before building any screen that reads it.
- **A ~28-screen scope is emphatically not a one-shot.** A 12-screen plan already is not.
  The reference engagement ran 47 numbered steps across 5 phases. `[SINGLE-OBSERVATION]`
- **Cost anchors.** One seed/data step consumed 4+ hours across 14 turns and ~18
  revisions; heavy screen steps ran ~14 Mentor turns and ~46 minutes each.
  `[SINGLE-OBSERVATION]` Budget from these, not from optimism.
- **Right-sizing test.** A step is right-sized when a *fresh* agent with no history can
  execute it against one written spec within a cap of **one build turn (a build pass
  of up to 4 short turns counts as one) plus two fix
  turns**. If it cannot, split it.

Worked sizing tables and slice ordering: `references/decomposition-and-sizing.md`.

### 6. Author the specs

One spec file per step, written now - not deferred to the session that builds it. Specs
are the interface between this expensive phase and every cheap one after it. Anatomy
that worked: a header stating phase and scope plus what is explicitly **not**
covered; a resolution section stating judgment calls outright instead of leaving
ambiguity to the build agent; standing rules restated inline so the build agent needs no
other file; numbered turn blocks each using the four-part element description **VISUAL
LAYOUT / DATA FLOW / FUNCTIONAL BEHAVIOR / PRESENTATION ORDER**, where DATA FLOW names
entities and attributes only and never aggregates, screen actions or local variables; an
invariant pre-check that can halt the run; an explicit non-goals list; and an acceptance
checklist of numbered, verifiable, screenshot-anchored assertions.

Never "should look right". Good specs read as executable test plans and ran 168-226
lines. `[SINGLE-OBSERVATION]` Copy `templates/spec-template.md` per step.

### 7. Scaffold the repo and the handoff

The handoff document is **two parts**: stable **RULES** that accumulate, and a **BRIEF**
replaced wholesale every session. Never a growing narrative of past steps - that is what
the append-only build log is for. Scaffold: the derived brief, the plan, `specs/`, a
per-step build-pattern log, a durable run-id log, `tenant-profile.md`, and that handoff.

Layout, file roles, handoff shape and three observed failure modes: `references/repo-scaffold.md` (heading "Failures to design against"), `templates/handoff-template.md`.

## Routing per-app bootstrap

This skill decides the decomposition and the plan; it does not bootstrap an app itself.
Route each app's first build by the source type available **for that app**:

| Source for that app | Route to |
|---|---|
| Visual or code design - screenshots, concept images, Figma frames, HTML, TSX/React | `../fulcrum-design-loop/SKILL.md`, entered at its phase 1 (Capture) with this plan's app, shell decision and step ids; intake questions already answered here are not re-asked, and every unanswered batch B question is asked before capture. Per app: `.fulcrum/design/<app>/`, one `project.md` `design` entry, at most 6 screens |
| Text only - derived brief, prose spec | `../fulcrum-mentor-turns/SKILL.md` per spec |
| Both | design loop for theme, chrome and screens; this skill's specs for entities and logic |

Fulcrum never runs an external bootstrap skill's procedure. Where `outsystems-design-to-app`
is installed, the design loop may read its reference data as `[UNVERIFIED]` input; its
batching, prompt, session and publish procedure conflicts with Fulcrum rules
(`../fulcrum-design-loop/references/official-skill-interop.md`).

## Exit gate

Do not hand off until all of these hold:

1. A derived written brief exists in the repo.
2. The target-platform decision is recorded with its consequence.
3. `tenant-profile.md` exists, every listed fact resolved, each with recorded evidence.
4. The Mentor liveness gate passed against the actual target app.
5. The plan names apps, agents, workflows, entity owners and deployable units.
6. Every phase-one step has a spec file passing the right-sizing test.
7. The handoff has a RULES part and a BRIEF part, and the BRIEF names exactly one next step.
