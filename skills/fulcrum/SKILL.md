---
name: fulcrum
description: The router and entry point for the whole Fulcrum skill family. Looks at the filesystem and the tenant, works out what state an engagement is in, and dispatches to the right skill — it never asks the user to self-classify. Use when the user says "build an OutSystems app", "start a new ODC project", "I have an idea for an app", "resume my Fulcrum work", "continue where I left off", "what should I build next", "pick up the build", "is this app done", or hands over a BRD, Figma export, mockup, screenshot, or a bare idea with no plan yet. Also the right skill whenever it is unclear which other Fulcrum skill applies.
version: "1.0.0"
requires: filesystem read access to the project repository to detect `.fulcrum/` and any existing app source; a capability to put structured questions to the user in small batches when the filesystem cannot answer them; no ODC MCP surface of its own — it dispatches into skills that need one.
---

# fulcrum — router and entry point

Read this first on any harness without skill auto-triggering. It performs no
Mentor turn, no verification, no planning, and defines no state-file schema of
its own — see `../../CONVENTIONS.md`, "Skill boundaries — stay in your lane",
row `fulcrum`. It detects, then dispatches.

**Its defining property: it detects, it does not interrogate.** Do not ask the
user "what is your situation?" — look at the filesystem and the tenant and work
it out. Asking the user to self-classify is the thing this skill replaces.

## Boundary

| Need | Owner |
|---|---|
| `.fulcrum/` file set, schemas, the lease, `HALT.md` mechanics | `../fulcrum-project-state/SKILL.md` |
| Interviewing a user with an idea but no written requirements | `../fulcrum-discovery/SKILL.md` |
| Decomposing source material into a plan and repo scaffold | `../fulcrum-solution-init/SKILL.md` |
| Assessing an existing app against its requirements | `../fulcrum-gap-analysis/SKILL.md` |
| Running the task list once resumed | `../fulcrum-loop-engine/SKILL.md` |
| What `mode` and `posture` mean, and the opt-in rule | `../../CONVENTIONS.md`, heading "Mode and posture" |

## The detection ladder

Run top to bottom; stop at the first row that matches. Full procedure,
including every conflicting-signal case: `references/detection-procedure.md`.

| Found | Route |
|---|---|
| No `.fulcrum/`, no app, no source material | `../fulcrum-discovery/SKILL.md` |
| No `.fulcrum/`, no app, source material present (BRD, Figma/Stitch export, mockups, screenshots) | `../fulcrum-solution-init/SKILL.md` |
| No `.fulcrum/`, an app already exists | `../fulcrum-gap-analysis/SKILL.md` |
| `.fulcrum/` present, `HALT.md` present | **STOP. Report. Ask a human.** Never auto-resume — see below. |
| `.fulcrum/` present, an open task per the `JOURNAL.md` index | resume → `../fulcrum-loop-engine/SKILL.md` |
| `.fulcrum/` present, all tasks closed | Report status. Offer the next phase in `plan.md`, or gap analysis if none remains. |

**Detection is cheap by construction.** Resume answers from the last row of
`.fulcrum/JOURNAL.md` alone — never open a session file to decide where to
route. That index exists precisely so a resume decision costs one file read.
See `../fulcrum-project-state/references/resume-and-halt.md`, heading "Read
order on every session start".

## HALT.md is absolute — state the mechanism

If `HALT.md` exists, the engagement is halted. **Never resume past it.** The
mechanism: a halt exists only because some agent already judged that
continuing was unsafe, with evidence in hand. A router that resumes without a
new human decision overrides that judgement with no new information, and the
next mutating turn fails the same way the halt was written to prevent —
against a live application, not a sandbox. Report the file's contents and stop.
Clearing it is a human act recorded in `DECISIONS.md`, per
`../fulcrum-project-state/references/resume-and-halt.md`, heading "Resuming
past a halt". This router does not perform that resolution; it only refuses to
skip it.

## A crashed session is not a halt, and neither is a clean stop

`HALT.md` absent does not mean the last session finished cleanly. The last
`JOURNAL.md` index row's `State` column plus the lease tell live from dead —
full signal table in `../fulcrum-project-state/references/resume-and-halt.md`,
heading "Crash recovery — the four signals of interrupted work". This router
does not diagnose a crash itself:

- `State: closed` in the last row → clean stop. Route by the ladder above as
  if starting fresh at that point.
- `State: open` in the last row → possible crash or a run still executing.
  Hand off to `../fulcrum-loop-engine/SKILL.md` to resume at its phase 4
  (poll the recorded run to a terminal state) — never restart the turn, and
  never re-run source triage or decomposition over a repo already scaffolded.

## Session-start tool preflight

Before dispatching into any skill below, confirm the ops the next phase needs
are actually callable — a schema that loads is not a tool that dispatches.
Consult `tenant-profile.md` where it already has the answer; probe only what
it does not. Keep it proportionate: a short preflight, not a full audit every
session. Full procedure: `references/tool-preflight.md`.

## Mode: read it, or establish it once

Mode (`guided` | `expert`) lives in `.fulcrum/project.md`. What each mode means
is owned by `../../CONVENTIONS.md`, heading "Mode and posture" — not restated
here.

- **Present:** read it, do not ask.
- **Absent** (first run, `.fulcrum/` not yet scaffolded): this router
  establishes it. Ask once, in the first question batch, with the two options
  named and a recommendation (`guided`, for a first engagement or an
  unfamiliar tenant). The skill that scaffolds `.fulcrum/` writes the answer
  to `project.md`; this router never writes that file itself.

## Question-asking discipline (guided mode only)

This is the only place in the family this discipline is defined. `expert` mode
skips it — the user invokes skills directly and decides for themselves.

- **Batch, never drip.** Small batches of related questions, not one
  question per turn. One-at-a-time multiplies round trips and reads as an
  interrogation.
- **Options plus a recommendation.** Every question the router asks carries
  concrete choices and, where one exists, a recommendation with its one-clause
  reason. A user forced to invent an answer from nothing gives a weaker answer
  than one choosing between named alternatives.
- **Never ask what the filesystem or the tenant can answer.** If `.fulcrum/`,
  an app, or source material already answers a question, do not ask it.

**The failure mechanism.** A router that asks what it could have detected
trains the user to distrust it — every future question reads as "did it even
look?" — and it spends the interaction budget genuine decisions need on
questions that had a mechanical answer. That budget does not refill mid-batch.

**Where this stops and discovery starts.** This router's questions are about
*routing and mode* — is there source material, does an app exist, guided or
expert — never about requirements content. The instant a question is about
what the app should do (roles, entities, screens, acceptance criteria), it
belongs to `../fulcrum-discovery/SKILL.md`'s interview, not here. Full
interaction contract, including the batch templates: `references/guided-mode-interaction.md`.

## Auto-trigger surface

This is the only skill in the family with a broad `description` — every other
skill's is narrow so a user who does not know the family lands here first
(`../../CONVENTIONS.md`, skill file layout). Do not narrow this one to match
the others.

## Routing to references

| Situation | Open |
|---|---|
| Any ladder row, or a conflicting-signal case (mismatched tenant, app with no state, `TASKS.md` rows but no plan) | `references/detection-procedure.md` |
| Composing a guided-mode question batch | `references/guided-mode-interaction.md` |
| Before dispatching, confirming the ops the next phase needs are callable | `references/tool-preflight.md` |
