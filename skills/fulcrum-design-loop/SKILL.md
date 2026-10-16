---
name: fulcrum-design-loop
description: One-shot design-to-app for a single ODC app. Takes one design source - a
  screenshot, concept image, mockup, Figma frames, an HTML page or TSX/React code - for an
  app of about six or fewer screens, captures it into a per-screen widget-tree spec of real
  OutSystems UI blocks, builds it through Mentor one step at a time, and render-compares
  each published screen against the source with a bounded fix loop. Use when the user says
  "build this screenshot", "turn this mockup into an app", "make this design work in
  OutSystems", "one-shot this concept into ODC", "screenshot to app", "Figma to ODC app",
  "build this HTML/TSX as an OutSystems app", or hands over one design for one app. Not
  for multi-app solutions or piles of exports needing triage (fulcrum-solution-init), not
  for an app that already exists (fulcrum-gap-analysis), not for an app with no design
  (fulcrum micro profile or fulcrum-discovery).
version: "1.0.0"
requires: ODC MCP server authenticated; Mentor enabled on the tenant; an image-inspection
  capability for visual sources; a subagent mechanism with per-dispatch tier selection;
  a browser automation capability for a delegated role (optional - degrades to user
  screenshots, then structure-only); a design-tool read capability for Figma (optional -
  else the user exports frames as images).
---

# fulcrum-design-loop

## Boundary

One design source for one app -> a published, render-compared ODC app in Development.
This skill owns **design capture and the design spec format; the block-mapping gate;
step decomposition of a captured design; render-compare against the source and diff
triage.** It does not own turn mechanics, traps, proof rungs, render execution, seed
loaders, iteration or stop rules; those are reused by pointer, never restated:
state and the micro profile `../fulcrum-project-state/SKILL.md`; iteration
`../fulcrum-loop-engine/SKILL.md`; turns, sessions, publish gate
`../fulcrum-mentor-turns/SKILL.md`; traps `../fulcrum-engine-traps/SKILL.md`; proof
`../fulcrum-verification/SKILL.md`; renders `../fulcrum-render-check/SKILL.md`; seeds
`../fulcrum-seed-data/SKILL.md`; halts, caps, delegation
`../fulcrum-unattended-guardrails/SKILL.md`.

The design loop **is** the micro file set plus `.fulcrum/design/`, with a design step
allowance of 5 + N steps, N <= 6 screens, plus one step per split screen step; the
ceiling is N <= 6 screens and 5 + 2N steps with splits counted; promotion is proposed
only beyond that. Entered from `fulcrum-solution-init`
on the full profile, each app has its own `.fulcrum/design/<app>/` and the 6-screen cap
applies per app. (Fulcrum rule)

## When not to use

| Situation | Route instead |
|---|---|
| More than about 6 screens, a second app, agents/workflows, a BRD alongside, or exports needing dedupe/asset triage | `../fulcrum-solution-init/SKILL.md` |
| The app exists with content beyond the template screen set | `../fulcrum-gap-analysis/SKILL.md` |
| No design, small ask | micro profile via `../fulcrum/SKILL.md` |
| `.fulcrum/` already has a plan | `../fulcrum-loop-engine/SKILL.md` (resume); never re-capture |

The router proposes this skill; the user confirms. Never auto-picked, `expert`
included. (Fulcrum rule)

## The loop at a glance

| # | Phase | Exit | Who (tier) |
|---|---|---|---|
| 0 | Intake | Batch B recorded; preflight done | orchestrator (`workhorse`) |
| 1 | Capture | Screen list with SIDs, tokens, theme, data, then screen files drafted | `fulcrum-capturer` (`deep-reasoning`): one shared dispatch first, then one dispatch per <= 3 screens, parallel |
| 2 | Gate | `design/gate.md` all PASS, or one re-capture per failing screen done | fresh `fulcrum-capturer` in gate mode (`workhorse`), blind to capture reasoning |
| 3 | Plan, go/no-go | User says go (batch C) | orchestrator |
| 4 | Build | Step's Publish passes the `env_app` revision gate | `fulcrum-mentor-driver` + `fulcrum-poller` |
| 5 | Verify | Rungs in the row's `Verify` have evidence | `fulcrum-renderer`, `fulcrum-verifier` |
| 6 | Render-compare | Verdict per screen at the bar | verifier judges; orchestrator triages |
| 7 | Fix | Re-compare done, or cap -> halt path | driver, new dispatch on a `fix` row of the same `Step` |
| 8 | Report | All screen rows terminal; promotion offered, never done | orchestrator |

Phases 4-7 are the loop engine's iteration unchanged; this skill supplies the rows,
the brief content and the phase-6 procedure. The orchestrator reads only
`manifest.md`, `gate.md` and fidelity summaries - images stay in capturer and
verifier contexts. The one exception: it reads a screen's `screens/<SID>.md` when
composing that screen step's driver brief - that file only, and only then. (Fulcrum
rule)

## Intake

Entered from the router (batch A: mode; "design loop or full path"), or from
`fulcrum-solution-init`. Entry from `fulcrum-solution-init` is at Intake, with Q1 (app
creation) and Q7 (form factor, if applicable) pre-answered there, not re-asked. Of the
intake steps below, these still run: step 1 (copy into `source/`), step 2 for every
batch B question still unanswered (bar, access, instrument, personas, evidence, assets,
re-probe), in one batch before capture - never defaulted; step 3 (`manifest.md` and
the per-app `design` entry); step 4's browser preflight and official-skill detection.
Step ids come from the solution plan; P1.04 Data and P1.05 Seed are omitted when that
plan already has the entity and seed steps. Paths below then sit under
`.fulcrum/design/<app>/`.

1. Copy the design verbatim into `.fulcrum/design/source/` (write-once).
2. Ask **batch B in one batch** (exact text, conditions, recording:
   `references/intake-questions.md`). Every answer is a user-policy choice: asked,
   never defaulted, recorded `Decider: user`; `expert` may answer in the invocation,
   and a missing answer is still asked. (Fulcrum rule)
3. Write `project.md` (`profile: micro`, field `design` = `.fulcrum/design/manifest.md`;
   on the full profile `design` lists one manifest per app,
   `.fulcrum/design/<app>/manifest.md`) and `design/manifest.md` from
   `templates/manifest.md`.
4. Preflight: session-start tool preflight (`../fulcrum/references/tool-preflight.md`);
   `env_list` keys into `tenant-profile.md` per the micro profile procedure; the
   browser preflight in `../fulcrum-render-check/SKILL.md`, heading "Preflight - once
   per project", when the instrument answer is (a); official-skill detection
   (`references/official-skill-interop.md`); for a Figma source, the design-tool read
   check, run before batch B is sent so a frame-export ask joins it
   (`references/capture-recipes.md`, heading "Figma").

## Capture and the design spec

First one **shared** `fulcrum-capturer` dispatch: it enumerates the screens and
assigns `SID`s (reported; the orchestrator records them in `manifest.md`) and writes
the app-wide files `tokens.md`, `theme.css` and `data.md`. Then one dispatch per <= 3
screens, in parallel, each writing only its `screens/<SID>.md`; a class, token or
entity a screen needs that the shared files lack is reported, and one serial shared
dispatch adds it before the gate. The orchestrator copies references into
`reference/` after the shared dispatch reports SIDs, before the screen dispatches and
the gate. Every brief names the exact `design/` paths it may
write; `reference/` is the orchestrator's (`references/capture-recipes.md`, heading
"Reference images"). Recipes (images, HTML/TSX, Figma, reference images):
`references/capture-recipes.md`. Region-to-block lookup: `references/block-map.md`;
archetype cues: `references/screen-archetypes.md`.

Outputs (schemas and limits: `references/design-spec-format.md`): `screens/<SID>.md`
(anatomy, regions, icons, interactions, F-items; <= 6 top-level regions, else two
screens or two steps), `tokens.md`, `theme.css` (every custom class defined once),
`data.md` (entities, seed rows with dates as day offset + time, KPI and chart
decisions).

**No Mentor prompt carries a whole file.** A region turn carries one region's subtree
(<= ~25 anatomy lines), the class names, bindings and one-line trap mechanisms, within
the prompt ceiling in `tenant-profile.md` section 8. An unresolved ceiling means a few
sentences plus a terse checklist (`../fulcrum-mentor-turns/SKILL.md`, heading "2.
Prompt shape, the length ceiling, and secrets");
record the longest prompt that landed. A truncated prompt builds part of the region
and reports success. (Fulcrum rule)

## The block gate

A fresh gate-mode capturer, given only the capture files and the reference images,
writes `design/gate.md`: one row per check per screen, PASS/FAIL with a line ref. The
twelve checks are in `references/design-spec-format.md`, heading "gate.md". FAIL ->
one re-capture of that screen, one re-gate; a second FAIL goes to batch C as an open
risk. A distinct block stays `unresolved` until its first step pre-flights it
(`../fulcrum-mentor-turns/references/prompt-scaffolds.md`, "Pre-flight a UI block by
name"). A gate graded by the spec's own author is self-marking. (Fulcrum rule)

## Steps

Write `plan.md` from `../fulcrum-project-state/templates/plan-micro.md` (design
variant line), `TASKS.md`, `JOURNAL.md`, `RUN-IDS.md`, then ask batch C.

| Step | Produces | Verify | Notes |
|---|---|---|---|
| P1.01 Shell | Create or load the user's shell (per batch B); access on template screens; default screen; first Publish | 1,3,6 | A created asset exists only in its session until the first publish |
| P1.02 Theme | `:root` overrides; `theme.css` groups, one turn each | 1,3,6 | Identical-shape groups may batch |
| P1.03 Chrome | N empty screens with Layout and access; Menu links; title; user info; logo per batch B; icon probe if flagged | 1,3,6 | Navigation before content |
| P1.04 Data | Entities, static entities (explicit Ids), KPI metric entity | 1,3 | Verify after the index lag |
| P1.05 Seed | Loaders from `data.md` per `../fulcrum-seed-data/SKILL.md` | its "Verifying a seed" | Own step; expect 3+ turns |
| P1.06+ Screen | One screen per step: skeleton, then regions | 1,3,4,6 (+7 for create/edit) | Below |

**Screen step**, one dispatch and one session: guard -> consult (Mentor's approach for
skeleton and blocks; doubles as block pre-flight) -> skeleton turn -> region turns ->
Publish. One region per turn; identical-shape regions may batch; a chart, a
table/repeater, a form and an overlay never share a turn. **Build pass <= 4 short
turns, counted as the one build turn** of `../fulcrum-unattended-guardrails/references/halt-conditions.md`,
"The turn cap"; more -> split into two steps, each ending in Publish; a split step
counts in the step allowance and the batch C estimate. Render-compare runs once, after
the last step of a split screen; earlier split steps verify rungs 1 and 3 only. Fix turns <= 2 per step. READ-then-MIRROR only against a region already render-verified. Briefs
carry region subtrees inline, never a path to the whole spec; row shapes and brief
contents: `references/design-spec-format.md`, "Step decomposition". (Fulcrum rule)

## Render-compare and fix

When `project.md` has `design`, rung 6 on a screen row runs
`references/render-compare.md` after the publish gate and the lag wait:

1. **Capture** - `fulcrum-renderer` at the manifest viewport(s) (tier A); the user's
   screenshot via a parked `manual` row (tier B); tier C has no capture and every
   screen is `unproven`. Curl is never a render.
2. **Judge** - a fresh blind `fulcrum-verifier` with image inspection, given only the
   reference, capture(s), render `report.md`, F-items, bar and diff vocabulary.
3. **Triage** - blocker/major -> fix, minor -> `backlog.md`; a diff on 2+ screens or
   from a theme class, token or chrome element is a **pattern**: one `fix` row on the
   owning step, then re-compare every affected screen.
4. **Fix** - diagnostic first, a fix turn led by the measured symptom, Publish,
   re-judge. At most 3 compare rounds per screen (the initial judge plus one re-judge
   per fix turn; fix turns stay <= 2); then `fail`, guardrails halt path.
5. **Record** `design/fidelity/<SID>-r<n>.md` from `templates/fidelity.md`.

## Stop and report

- **Done:** every screen row terminal (`pass`, `fail` parked, `unproven` with reason)
  and `design/report.md` written from `templates/report.md`.
- **Halt:** owned by `../fulcrum-unattended-guardrails/SKILL.md`; the design-specific
  trigger is a pattern fix regressing a passed screen.
- **Caps:** build pass <= 4, fix <= 2, compare rounds <= 3 (initial judge plus one
  re-judge per fix turn), renders <= 1 per form
  factor per round, one re-capture and re-gate per screen.
- **Promotion beyond Development is never done**; the report offers it. (Fulcrum rule)

## Official skill present

Where `outsystems-design-to-app` is installed, its reference data may be read as
`[UNVERIFIED]` input; its procedure is never run or quoted - its batching, prompt,
session and publish rules conflict with Fulcrum's. `references/official-skill-interop.md`.

## Reference files

| File | Open when |
|---|---|
| `references/intake-questions.md` | Asking batch B or C; recording answers |
| `references/capture-recipes.md` | Briefing or running capture |
| `references/design-spec-format.md` | Writing or checking any `design/` file; the gate; step rows |
| `references/block-map.md` | Mapping a region to an OS UI block |
| `references/screen-archetypes.md` | Classifying a screen; common misses per archetype |
| `references/render-compare.md` | Rung 6 on a screen row; triage; fix rounds |
| `references/official-skill-interop.md` | The official skill is installed |
| `references/THIRD-PARTY-NOTICE.md` | Licence of the derived files |
| `templates/` | `manifest.md`, `screen.md`, `fidelity.md`, `report.md` |
