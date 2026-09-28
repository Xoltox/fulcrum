---
name: fulcrum-loop-engine
description: >
  The iteration mechanism for a Fulcrum build — how one task becomes one
  completed, recorded, proven iteration, and how the loop advances to the next
  one. Owns task selection, the precondition and staleness gate, dispatch,
  polling, verification, recording and advance; the bounded fix-loop; mechanical
  oscillation detection against `.fulcrum/JOURNAL.md`; crash-idempotency of a
  single iteration; and per-iteration budget accounting. Use when the user says
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

One task in, one proven and recorded outcome out. This skill owns the
**mechanism**. It owns no numbers of its own: every ceiling, cap and stop
condition it obeys is defined elsewhere and cited.

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
notices a repeat failure, a cap reached, a regression, a runtime step-change —
and hands it to the halt path. It never rules on whether to continue.

## The canonical iteration

Seven phases, in this order. `[UNVERIFIED]` — new design, not an observed
procedure. A phase whose omission has no named consequence gets skipped under
time pressure, so each carries what breaks without it.

| # | Phase | What it does | What breaks if skipped |
|---|---|---|---|
| 1 | **Select** | Take the next actionable row from `.fulcrum/TASKS.md` — lowest `ID` with `Status: todo`, dependencies satisfied | Agent invents a task. Nothing joins it back to a plan step, so `Step` traceability is lost and gap analysis later reads the work as an undocumented addition |
| 2 | **Precondition** | Gate the dispatch: `HALT.md` absent; lease acquired for `App`; oscillation scan clean; budget covers a whole iteration; staleness guard passed against the live model | Each gate has its own loss. No halt check resumes a run that was stopped as unsafe. No lease means two Mentor sessions on one app. No oscillation scan repeats a known-failing attempt. No staleness guard publishes from a stale model, which advances the revision while silently reverting completed work `[VERIFIED]` |
| 3 | **Dispatch** | Write state first, then brief and dispatch the turn to a subagent | The orchestrator executes instead of supervising and spends the window it needs to supervise with. Writing state after dispatch leaves a run mutating the app with no record of it |
| 4 | **Poll** | Poll the run to a terminal state at the cadence for who is paying | Polling in the orchestrator's own context at a delegated rate grows it cumulatively and unrecoverably. Not polling at all loses the run id, and an evicted run is permanently unreadable `[VERIFIED]` |
| 5 | **Verify** | Run exactly the proof rungs named in the row's `Verify` column | A clean publish and zero validation errors prove nothing about rendering or logic `[VERIFIED]`. Skipping produces `done` rows that were never shown to work, and the next iteration builds on them |
| 6 | **Record** | Write the verdict: `TASKS.md` row, session-file line, `JOURNAL.md` `Tasks` entry, `DECISIONS.md` if a decision was made | Oscillation detection reads the journal. An unrecorded failure is a failure the loop will repeat forever, because the mechanism that catches repeats has nothing to scan |
| 7 | **Advance** | Release the lease, re-scan for oscillation, then select again — or hand to the halt path | A leaked lease blocks the app for its whole TTL. Advancing without re-scanning defers a detected repeat by one whole iteration, which is one more mutating turn against a live app |

**Phases 1–2 and 6–7 are the orchestrator's. Phases 3–5 are dispatched** — the
orchestrator never calls Mentor, publish or a gate script itself
(`../fulcrum-unattended-guardrails/SKILL.md`, heading "Orchestrator
prohibitions — categorical"). Phase detail, the exact writes each phase makes,
and a worked walkthrough: `references/iteration-contract.md`.

## Posture changes the shape of phase 3

Definitions, the orthogonality rule and the opt-in rule are owned by
`../../CONVENTIONS.md`, heading "Mode and posture". Not restated here. Read
`posture` from `.fulcrum/project.md`.

**`collaborative` (the default)** — phase 3 is two turns:

1. **Consult turn.** Ask Mentor for the idiomatic ODC approach to the task.
   Read-only; it changes nothing, so it polls at the answer-back cadence.
2. **Review** the proposal against `../fulcrum-engine-traps/SKILL.md`. Correct
   **only** the specific traps it trips. Do not rewrite an idiomatic proposal
   into your own design — that is `directive` posture wearing a consult turn.
3. **Build turn**, carrying the proposal plus the trap corrections.

**`directive`** — phase 3 is one build turn. The consult phase is skipped; the
rest of the iteration is unchanged.

**An accepted Mentor proposal is a decision.** Append a `DECISIONS.md` record
with `Decider: mentor`, naming the concrete model artifacts in `Affects`
(`../fulcrum-project-state/references/file-schemas.md`, heading "DECISIONS.md").
Without it the app carries a shape nothing in the repo explains, and
`../fulcrum-gap-analysis/SKILL.md` reads it as drift it cannot account for —
which reads as a defect. `[UNVERIFIED]`

## The bounded fix-loop

A failed verify does not end the iteration. It enters a bounded inner loop
between phases 5 and 6.

**The ceiling is not this skill's to set.** It is **1 build turn + at most 2 fix
turns per step** — `../fulcrum-mentor-turns/SKILL.md`, heading "Turn economics",
and `../fulcrum-unattended-guardrails/references/halt-conditions.md`, heading
"The turn cap". Both state the same number. Obey it; never invent a second one.

Per attempt: **diagnostic step** (mandatory before any fix turn after the first
failure — a fix turn with no new evidence is the same attempt again, not a
second one; the rule is guardrails'), then **fix turn**, then **re-verify the
same rungs** — a fix is not proven by the fix turn reporting success — then
**record the attempt** before the next one.

On exhausting the ceiling, or on a second recorded `:fail` for this task: stop
the inner loop, write the honest verdict, hand to the halt path. Never escalate
model tier to break it (`../../AGENTS.md`). Full procedure:
`references/oscillation-and-fix-loop.md`.

## Oscillation detection — mechanical, not remembered

`../../AGENTS.md`: "Stuck twice on the same problem means stop and report."
That is now checkable by scanning one file.

**The scan.** Read `.fulcrum/JOURNAL.md` — the session index, one row per
session. Column 5, `Tasks`, carries inline per-task outcomes (`T-003:pass,T-004:fail`),
written as each task reaches a terminal state, not at session close. Match the
task id across column 5 of **every** row in the index.

**What counts as a repeat: two or more `<task-id>:fail` entries across the whole
index.** Task ids are never reused
(`../fulcrum-project-state/references/file-schemas.md`, heading "TASKS.md"), so
the count is unambiguous. A `:fail` in the current session's own row counts the
same as one from six weeks ago.

**What does not count:** `:unproven` (work that happened but was not proven —
re-prove it, do not re-fix it); a different task id however similar its prose;
and repeated attempts inside one fix-loop, which the turn cap governs, not this.

**Run it twice per iteration:** in phase 2 before dispatching, and in phase 7
immediately after recording a `:fail`. The second run is what stops a second
failure costing a third mutating turn.

**On detection the loop does not decide.** It stops the iteration, records what
it found, and hands to
`../fulcrum-unattended-guardrails/references/halt-conditions.md`. Guardrails
owns the verdict and the halt record.

Grep recipes, the archive-rotation case and the false-negative modes:
`references/oscillation-and-fix-loop.md`.

## Crash-idempotency — every iteration is re-runnable

An iteration must survive being killed at any point and re-run without
duplicating a mutation or losing a record.

**The write ordering that makes this true already exists.** State is written
**before** the wait, never after the result — `../fulcrum-project-state/SKILL.md`,
heading "Write ordering — state before the wait, never after the result", plus
the idempotency rules in `../fulcrum-project-state/references/resume-and-halt.md`.
Apply them; do not re-specify them here.

What the loop adds on re-entry, before anything else:

- A row with `Status: active` or an index row with `State: open` means an
  iteration was interrupted. **Resume it at phase 4** — poll the recorded run id
  to a terminal state. Never restart at phase 3: a competing turn on the same
  session is how a mutating turn ends up racing.
- Treat every `InFlight` id as possibly-mutated: the app may have changed with
  no recorded outcome. Re-read the live app revision independently before
  re-entering phase 3 — a revision recorded in `.fulcrum/` is a baseline, not a
  current value. `[VERIFIED]`

## Per-iteration budget accounting

Budgets are **tool-call counts, never token counts**. The arithmetic, the
per-class rates, the 0.65 checkpoint and 0.85 hand-back triggers and the
recalibration loop are in
`../fulcrum-unattended-guardrails/references/budgeting.md`. Consume them; do
not fork them.

One rule is the loop's own: **check at phase 1 that the remaining budget covers
a whole iteration, and hand back at a phase boundary, never mid-iteration.** An
iteration abandoned between dispatch and record leaves a run mutating the app
with no verdict — the state crash recovery is most expensive in. Procedure:
`references/iteration-budget.md`.

## Mode changes what the loop asks between iterations

Thin on purpose: the router (`fulcrum`) owns interaction and mode is not a
branch inside this skill (`../../CONVENTIONS.md`, heading "Mode and posture").
The loop marks only **where** the decision points are. All four sit at phase 7,
never mid-iteration.

| Decision point | `guided` | `expert` |
|---|---|---|
| Verdict was `fail` or `unproven` | Ask before the next iteration | Proceed; the record is the disclosure |
| Next task would deviate from `plan.md` | Block and ask | Proceed under a stated assumption, recorded in `DECISIONS.md` |
| Phase boundary in `plan.md` reached | Report and ask whether to continue | Continue |
| Budget hand-back trigger reached | Report and ask | Hand back and report |

## Reference files

| Open when | File |
|---|---|
| Running an iteration, or unsure which write belongs to which phase | `references/iteration-contract.md` |
| A task failed, you are about to issue a fix turn, or you need the oscillation scan | `references/oscillation-and-fix-loop.md` |
| Sizing an iteration against a budget, or deciding whether to start one more | `references/iteration-budget.md` |
