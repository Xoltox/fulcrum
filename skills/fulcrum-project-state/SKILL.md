---
name: fulcrum-project-state
description: Defines the `.fulcrum/` project-state directory — the committed, on-disk memory a Fulcrum engagement resumes from. Owns the file set, each file's schema, which files are append-only and which are rewritten, the runtime lease that enforces one Mentor session per app, the crash-idempotent write ordering, the decision record that gap analysis consumes, and the halt record. Use when asked to "set up project state", "where do I record what's been done", "create the task list", "what should I write before running this unattended", "resume the build", "pick up where we left off", "record this decision", "why is the project halted", "is another agent working on this app", or when any Fulcrum skill needs to read or write durable state.
version: "1.0.0"
requires: filesystem read/write access to the project repository; a git working tree for the project (state is committed); the ability to read a clock for timestamps. No ODC MCP surface is needed to read or write project state itself.
---

# Fulcrum project state

## What this is

`.fulcrum/` is a directory **in the project repository** holding everything a cold
session needs to resume an engagement. It is a spec: this skill defines the file
contract, and every other Fulcrum skill obeys it.

Two hard properties:

- **It lives in the project, never in the installed skill directory.** Same principle
  as `../../MODEL-TIERS.md`, heading "The install interview must not edit installed
  files": installed content that carries project state makes every update fight the
  user's edits and lets the deployed copy drift from source. `[VERIFIED]`
- **It is committed to git.** Git *is* the multi-session and multi-person mechanism —
  history, merge, blame, review. Do not build a sync protocol, a database, or a
  distributed lock on top of it. The one exception is the lease, below.

## Boundary

| Need | Owner |
|---|---|
| How to iterate over the task list | `../fulcrum-loop-engine/SKILL.md` |
| When to stop, halt, or escalate | `../fulcrum-unattended-guardrails/SKILL.md` |
| What to build, and phase/step sizing | `../fulcrum-solution-init/SKILL.md` |
| Turn shape, polling, publish sequencing | `../fulcrum-mentor-turns/SKILL.md` |
| What counts as proof of a verdict | `../fulcrum-verification/SKILL.md` |

This skill owns **where state lives and what shape it has**. It never decides what
goes in it.

## `.fulcrum/` is terminal

Nothing here syncs outward to Jira, Linear, GitHub Issues, or any other tracker, and
nothing is mirrored inward. `[UNVERIFIED]` A mirror makes the tracker a second source
of the same fact at a different strength, which is documentation failure 1 in
`../fulcrum-solution-init/references/repo-scaffold.md`, heading "The four
documentation failures to design against": an agent obeys whichever copy it read
first and cannot tell it read the weaker one. Export a report if a human needs one;
never let anything write back.

## The layout

```
<project>/.fulcrum/
  project.md          solution identity, apps, mode, posture, tier overrides
  brief.md            derived requirements brief — written by fulcrum-discovery
  tenant-profile.md   the capability probe result — written by fulcrum-solution-init
  plan.md             phases and steps — stable, rarely rewritten
  TASKS.md            current truth: checkbox table of Mentor-turn-shaped tasks
  JOURNAL.md          session index: one ROW per session, completed in place
  journal/<session-id>.md  APPEND-ONLY: one file per session, one line per action
  DECISIONS.md        APPEND-ONLY: ADR-lite records
  RUN-IDS.md          APPEND-ONLY: durable run ids
  HANDOFF.md          two-part RULES/BRIEF snapshot, regenerated
  runs/<run-id>.md    optional per-run detail
  checkpoints/<agent-label>.md   per-agent, overwrite-in-place, ephemeral
  lease.json          runtime lock — NOT committed
  HALT.md             present only when halted — its existence is the signal
```

`tenant-profile.md`, `HANDOFF.md` and `RUN-IDS.md` are existing contracts. This skill
gives them a home and **does not restate their schemas**. See
`../fulcrum-solution-init/references/repo-scaffold.md` and
`../fulcrum-solution-init/templates/handoff-template.md`.

## Append-only versus rewritten — and why each file is where it is

| File | Discipline | Why |
|---|---|---|
| `JOURNAL.md` | append a row, then complete that row in place | Session index, one row per session. A session edits only its own row, so two sessions' edits land on different lines and merge cleanly. |
| `journal/*` | append-only | History. One file per session, written by one session, so it never conflicts; the append discipline is what keeps a crashed file readable and ordered. |
| `DECISIONS.md` | append-only | A decision is dated evidence. Editing one destroys the date that makes drift explicable. |
| `RUN-IDS.md` | append-only | A lost run id makes an in-flight run permanently unpollable. `[VERIFIED]` |
| `TASKS.md` | rewritten | Must show current truth in one read. An append log of status changes makes "what is open" a reconstruction. |
| `HANDOFF.md` | rewritten (BRIEF part) | Existing contract. |
| `project.md` | rewritten | Identity and settings, not history. |
| `brief.md` | written once by `fulcrum-discovery`, rarely rewritten | Derived requirements brief; a dated artifact, not a log. |
| `plan.md` | rewritten, rarely | Scope changes are deliberate and reviewed as a diff. |
| `checkpoints/*` | overwrite in place | Existing contract — `../fulcrum-unattended-guardrails/references/checkpoints.md`. Ephemeral working state for one agent; its durable residue is the session-file line and the TASKS row. Not an append log, and nothing may depend on it after that agent ends. |

Rewriting is safe **only** because the append-only files hold the history. That is
what lets `TASKS.md` drop closed rows at a phase boundary without losing anything.

## Write ordering — state before the wait, never after the result

`../../AGENTS.md` requires capturing a run identifier durably before the first wait.
That generalises to all state here. `[UNVERIFIED]`

Before dispatching or waiting on anything:

1. Allocate the task ID and write its `TASKS.md` row with status `active`.
2. Create `journal/<session-id>.md`, append its `started` line, and append the
   session's `JOURNAL.md` index row with `State: open`.
3. Append the `RUN-IDS.md` line the instant the run id is issued.

Only afterwards write the outcome, then the verdict.

**What breaks without this order.** A crash between dispatch and result leaves a run
mutating the app with no record of it. The next session sees no active work, opens a
second Mentor session on the same app — breaking the one-session-per-app
non-negotiable `[VERIFIED]` — and can publish from a stale model, which advances the
revision while silently reverting completed work. `[VERIFIED]`

Corollary: never write `[x]` with an empty verdict. `unproven` is the honest value
and it is what tells a resuming session the work needs re-proving.

## The lease, in one paragraph

`lease.json` is the only file here that is **not committed** — a committed lock is
stale the moment it is pushed. It carries a holder identity, an acquisition
timestamp, and a TTL. Acquire before opening a Mentor session; a live lease held by
someone else means wait or halt, never take; an expired lease may be broken, but only
with a session-file line recording the break. Without it, one-Mentor-session-per-app is
enforceable only inside a single agent's memory, and two sessions on one app is a
model-corruption path, not a queueing inconvenience. Full rules, including what the
lease cannot protect against: `references/lease-and-concurrency.md`.

## HALT.md is never silently passed

If `HALT.md` exists, the engagement is halted. Stop. Do not open a Mentor session, do
not publish, do not start the next task. Clearing it requires a human resolution
recorded in `DECISIONS.md` and the file deleted in that same change. Resuming past a
halt without that record defeats the guardrail that produced it and re-runs the
failure it stopped. `[UNVERIFIED]` Procedure: `references/resume-and-halt.md`.

## DECISIONS.md closes an existing hole

`../fulcrum-gap-analysis/SKILL.md` requires looking for a decision record before
calling a deviation a defect — its **drift** finding class. Nothing else in Fulcrum
produces such a record, so that check currently always finds nothing and every drift
reads as a gap. `[UNVERIFIED]` `DECISIONS.md` is that record. Its `Affects` field
must name concrete model artifacts (entity, screen, action identifiers), because gap
analysis joins from an artifact to a decision, not from prose. Shape:
`references/file-schemas.md`, heading "DECISIONS.md".

## Mode and posture

`project.md` records two orthogonal settings. This skill owns only that they live
there and what values are legal. **Their definitions, the orthogonality rule, the
failure mechanism and the opt-in rule are owned by `../../CONVENTIONS.md`, heading
"Mode and posture".** Read it there; it is not restated here.

- `mode`: `guided` | `expert`
- `posture`: `collaborative` | `directive`

`collaborative` is the default. Turn mechanics for each posture belong to
`../fulcrum-mentor-turns/SKILL.md`; do not write them here either.

## Routing

| Situation | Open |
|---|---|
| Creating `.fulcrum/`, or writing/parsing any file in it | `references/file-schemas.md` |
| Resuming, or checking whether a task has been attempted before | `JOURNAL.md` index alone — never open a session file for either query |
| About to open a Mentor session, or a second agent may be active | `references/lease-and-concurrency.md` |
| Starting cold, resuming after a crash, or `HALT.md` exists | `references/resume-and-halt.md` |
| Need a file skeleton to write | `templates/` |
