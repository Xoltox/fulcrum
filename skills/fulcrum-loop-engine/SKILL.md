---
name: fulcrum-loop-engine
description: >
  The iteration mechanism for a Fulcrum build - how the runnable frontier of
  the task graph becomes parallel, recorded, proven dispatches, one lane per
  app. Owns frontier selection and batching, the precondition and staleness
  gate, dispatch, polling, verification, recording and advance; the bounded
  fix-loop; mechanical oscillation and stall detection; crash-idempotency of an
  iteration; and per-iteration budget accounting. Use when the user says
  "work through the task list", "run the next task", "keep building until the
  phase is done", "resume the loop", "what should I do next", "the same task
  keeps failing", "have we tried this before", "how many fix turns do I get", or
  "pick up the build where it stopped".
version: "1.0.0"
requires: >
  A `.fulcrum/` project-state directory already scaffolded and readable/writable;
  ODC MCP server authenticated with Mentor enabled on the tenant; a subagent
  dispatch capability with per-dispatch model tier selection; a wait capability
  that suspends without spinning or accumulating context.
---

# The build loop

Runnable rows in, proven and recorded outcomes out, one lane per app, no wave
barrier. This skill owns the **mechanism**. It owns no numbers of its own: every
ceiling, cap and stop condition it obeys is defined elsewhere and cited.

## Boundary

| Need | Owner |
|---|---|
| When to stop, halt, escalate, or cap a turn | `../fulcrum-unattended-guardrails/SKILL.md` |
| Where state lives and what shape it has | `../fulcrum-project-state/SKILL.md` |
| Turn shape, prompt length, polling cadence, publish sequencing | `../fulcrum-mentor-turns/SKILL.md` |
| What counts as proof of a verdict | `../fulcrum-verification/SKILL.md` |
| Why a construct breaks | `../fulcrum-engine-traps/SKILL.md` |
| What to build, and step sizing | `../fulcrum-solution-init/SKILL.md` |

**The seam with guardrails: the loop detects, guardrails decides.** The loop
notices a repeat failure, a cap reached, a stall, a regression, a runtime step-change - and hands it to guardrails. It never rules on whether to continue.

## The canonical iteration

Seven phases, in this order. `[UNVERIFIED]` - new design, not an observed
procedure. A phase whose omission has no named consequence gets skipped under
time pressure, so each carries what breaks without it.

| # | Phase | What it does | What breaks if skipped |
|---|---|---|---|
| 1 | **Select** | Compute the frontier of `.fulcrum/TASKS.md`: all `todo` rows whose `DependsOn` are done, grouped by `App`; form one dispatch per lane, one batch or one solo row; `Verdict: unproven` is a proof-only re-prove dispatch (`references/frontier-and-batching.md`) | Agent invents a task. Nothing joins it back to a plan step, so `Step` traceability is lost and gap analysis later reads the work as an undocumented addition |
| 2 | **Precondition** | Gate each dispatch: `HALT.md` absent; oscillation scan clean; budget covers a whole iteration; for Mentor turns only, lease acquired by the orchestrator for every app the dispatch holds, TTL sized to the dispatch budget, and the staleness guard run as the first turn of the dispatch (`verify`/`code`/`infra`/`external`/`manual` rows skip both); a row consuming an external system needs `.fulcrum/external/<system>.md` | Each gate has its own loss. No halt check resumes a run that was stopped as unsafe. No lease (Mentor turns) means two Mentor sessions on one app. No oscillation scan repeats a known-failing attempt. No staleness guard publishes from a stale model, which advances the revision while silently reverting completed work `[VERIFIED]` |
| 3 | **Dispatch** | Write state first, then brief and dispatch: one driver per lane, sibling depth 1 agents, up to the in-flight cap. One dispatch is one batch or one solo row, running guard, consult, build, fix and Publish in one Mentor session | The orchestrator executes instead of supervising and spends the window it needs to supervise with. Writing state after dispatch leaves a run mutating the app with no record of it |
| 4 | **Poll** | Poll the run to a terminal state at the cadence for who is paying | Polling in the orchestrator's own context at a delegated rate grows it cumulatively and unrecoverably. Not polling at all loses the run id, and an evicted run is permanently unreadable `[VERIFIED]` |
| 5 | **Verify** | Run the gates the project's `Rigor` owes this dispatch (`../fulcrum-verification/SKILL.md`, heading "Gates and rigor"). G0 always; G3, where owed, is exactly the rungs in the row's `Verify` column | A clean publish and zero validation errors prove nothing about rendering or logic `[VERIFIED]`. Skipping produces `done` rows that were never shown to work, and the next iteration builds on them |
| 6 | **Record** | The orchestrator writes each row's verdict (a driver only returns it) and the `Gate` it actually ran: `TASKS.md` row, session-file line, `JOURNAL.md` `Tasks` entry, `DECISIONS.md` if a decision was made | Oscillation detection reads the journal. An unrecorded failure is a failure the loop will repeat forever, because the mechanism that catches repeats has nothing to scan |
| 7 | **Advance** | Release the lease (the orchestrator, when the dispatch returns `session_state: closed`; on `session_state: open` keep it, record the open `sessionId`, and resume that dispatch or stop for the user), re-scan for oscillation, run the stall check, reconcile state at a wave close (`references/iteration-contract.md`), then select again for that lane once its G1 has reported - or hand to guardrails | A leaked lease blocks the app for its whole TTL; a lease released over a still-open session invites a second session on the app. Advancing without re-scanning defers a detected repeat by one whole iteration, which is one more mutating turn against a live app |

**Phases 1-2 and 6-7 are the orchestrator's. Phases 3-5 are dispatched** - the
orchestrator never calls Mentor, publish or a gate script itself
(`../fulcrum-unattended-guardrails/SKILL.md`, heading "Orchestrator
prohibitions - categorical"). Detail and a walkthrough: `references/iteration-contract.md`.

## Posture changes the shape of phase 3

Definitions and the opt-in rule: `../../CONVENTIONS.md`, heading "Mode and
posture". Read `posture` from `.fulcrum/project.md`.

**`collaborative` (the default)** - phase 3 is two turns, one consult per batch,
not one per row:

1. **Consult turn.** Ask Mentor for the idiomatic ODC approach to the task.
   Read-only; it changes nothing, so it polls at the answer-back cadence.
2. **Review** the proposal against `../fulcrum-engine-traps/SKILL.md`. Correct
   **only** the specific traps it trips. Do not rewrite an idiomatic proposal
   into your own design - that is `directive` posture wearing a consult turn.
3. **Build turn**, carrying the proposal plus the trap corrections.

**`directive`** - phase 3 is one build turn. The consult phase is skipped; the
rest of the iteration is unchanged.

**An accepted Mentor proposal is a decision.** Append a `DECISIONS.md` record
with `Decider: mentor`, naming the concrete model artifacts in `Affects`. Without
it `../fulcrum-gap-analysis/SKILL.md` reads the shape as drift it cannot account
for - which reads as a defect. `[UNVERIFIED]`

## The bounded fix-loop

A failed verify does not end the iteration. It enters a bounded inner loop
between phases 5 and 6.

**The ceiling is not this skill's to set.** It is **1 build turn (a build pass of up
to 4 short turns counts as one) + at most 2 fix
turns per step or batch** - `../fulcrum-mentor-turns/references/granularity.md`, heading "Turn economics",
and `../fulcrum-unattended-guardrails/references/halt-conditions.md`, heading
"The turn cap". Both state the same number. Obey it; never invent a second one.

Per attempt: **diagnostic step** (mandatory before any fix turn after the first
failure - a fix turn with no new evidence is the same attempt again, not a
second one; the rule is guardrails'; reading model state back uses published-state inspection when
published, Mentor read-back only as belief, and wire evidence for settings and
REST structures), then **fix turn**, then **read-back only** - the guard runs once
per dispatch and orchestrator gates run between dispatches - then
**record the attempt** before the next one.

A batch failing inside its dispatch gets one fix turn, then splits per row. Any gate failure after the
driver returned leaves closed rows `done` and opens one `fix` row. On exhausting the ceiling,
or on a second recorded `:fail`: stop the inner loop, write the honest verdict, hand to guardrails:
a lane stop. Never escalate model tier (`../../AGENTS.md`). Procedure: `references/oscillation-and-fix-loop.md`, including "Late failures".

## Oscillation detection - mechanical, not remembered

`../../AGENTS.md`: "Stuck twice on the same problem means stop and report."
That is now checkable by scanning one file.

**The scan.** Read `.fulcrum/JOURNAL.md`, the session index. Column 5, `Tasks`,
carries inline per-task outcomes (`T-003:pass,T-004:fail`), written as each task
reaches a terminal state, not at session close. Match the task id across column 5
of **every** row.

**What counts as a repeat: two or more `<task-id>:fail` entries across the whole
index.** Task ids are never reused, so the count is unambiguous. A `:fail` in the
current session's own row counts the same as one from six weeks ago.

**What does not count:** `:unproven` (work that happened but was not proven - re-prove it, do not re-fix it); a different task id however similar its prose;
and repeated attempts inside one fix-loop, which the turn cap governs, not this.

**Run it twice per iteration:** in phase 2 before dispatching, and in phase 7
immediately after recording a `:fail`. The second run is what stops a second
failure costing a third mutating turn.

**On detection the loop does not decide.** It stops the iteration, records what
it found, and hands to `../fulcrum-unattended-guardrails/references/halt-conditions.md`.

Grep recipes, the archive-rotation case and the false-negative modes:
`references/oscillation-and-fix-loop.md`.

## Stall detection and no spikes

A lane's done-count flat across 3 consecutive dispatches, or a terminal publish
with an unchanged revision, is detected here and decided in guardrails (Fulcrum
rule): `references/oscillation-and-fix-loop.md`, heading "Stall detection". Never
plan a spike or probe row to test a platform capability: it costs hours and
throwaway revisions to prove what the first real row proves anyway
(`references/frontier-and-batching.md`, heading "No spikes").

## Crash-idempotency - every iteration is re-runnable

An iteration must survive being killed at any point and re-run without
duplicating a mutation or losing a record. State is written **before** the wait,
never after the result: `../fulcrum-project-state/SKILL.md`, heading "Write
ordering - state before the wait, never after the result", and
`../fulcrum-project-state/references/resume-and-halt.md`. Apply them.

What the loop adds on re-entry, before anything else:

- A row with `Status: active` or an index row with `State: open` means an
  iteration was interrupted, once per lane in flight. **Resume each at phase 4** -
  poll the recorded run id to a terminal state. Never restart at phase 3: a
  competing turn is how a mutating turn races. An `active` row with no run and the live revision unchanged returns to `todo`.
- Treat every `InFlight` id as possibly-mutated: the app may have changed with
  no recorded outcome. Re-read the live app revision independently before
  re-entering phase 3 - a revision recorded in `.fulcrum/` is a baseline, not a
  current value. `[VERIFIED]`

## Per-iteration budget accounting

Budgets are **tool-call counts, never token counts**. The arithmetic, the
per-class rates, the 0.65 checkpoint and 0.85 hand-back triggers and the
recalibration loop are in
`../fulcrum-unattended-guardrails/references/budgeting.md`. Consume them; do
not fork them.

One rule is the loop's own: **check at phase 1 that the remaining budget covers
a whole iteration, and hand back at a phase boundary, never mid-iteration.** With
lanes in flight: stop selecting, let them return, record, then hand back. An
iteration abandoned between dispatch and record leaves a run mutating the app
with no verdict. Procedure: `references/iteration-budget.md`.

## Mode changes what the loop asks between iterations

The router (`fulcrum`) owns interaction; mode is not a branch inside this skill
(`../../CONVENTIONS.md`, heading "Mode and posture"). The loop marks only **where**
the decision points are. All four sit at phase 7, never mid-iteration.

| Decision point | `guided` | `expert` |
|---|---|---|
| Verdict was `fail` or `unproven` | Ask before the next iteration | Proceed; the record is the disclosure |
| Next task would deviate from `plan.md` | Block and ask | Proceed under a stated assumption, recorded in `DECISIONS.md` |
| Phase boundary reached (a derived label, not a gate) | Report; stop only if a decision is needed | Continue |
| Budget hand-back trigger reached | Report and ask | Hand back and report |

## Reference files

| Open when | File |
|---|---|
| Selecting, batching, multi-asset or library rows, the in-flight cap | `references/frontier-and-batching.md` |
| Running an iteration, or unsure which write belongs to which phase | `references/iteration-contract.md` |
| A task failed, a batch failed, a fix turn is next, or you need the oscillation or stall check | `references/oscillation-and-fix-loop.md` |
| Sizing an iteration against a budget, or deciding whether to start one more | `references/iteration-budget.md` |
