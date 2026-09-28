# Per-iteration budget accounting

**This file forks no arithmetic.** The formulas, the per-class rates, the
`0.65` checkpoint and `0.85` hand-back triggers, the recalibration loop and the
anti-patterns all live in
`../../fulcrum-unattended-guardrails/references/budgeting.md`. Read them there.
This file says only how an iteration is accounted against them.

Everything here is `[UNVERIFIED]`: it is an accounting scheme over measured
rates, not a measurement of its own.

## Two budgets, two owners

| Budget | Held by | Spent on |
|---|---|---|
| The dispatched agent's call budget | The subagent, per its class label | Its own turn: prompt, polls, read-backs |
| The orchestrator's call budget | The orchestrator | Selecting, gating, briefing, reading reports, writing `.fulcrum/` |

They are separate windows and must never be netted against each other. An
iteration that is cheap for the orchestrator can still exhaust its builder, and
an orchestrator can run out of window while every agent it dispatched came in
under budget. The source measurement makes this concrete: in one session the
orchestrator alone burned 141k on file reads while its agents each stayed well
inside their own windows.

## The orchestrator's per-iteration cost

Count calls, never tokens — a subagent cannot measure its own token usage and
the orchestrator learns the number only after the fact
(`../../fulcrum-unattended-guardrails/SKILL.md`, heading "Budgets are tool-call
counts, never token counts").

A `collaborative` iteration costs the orchestrator roughly:

| Phase | Orchestrator calls |
|---|---|
| 1 Select | 1 read (`TASKS.md`) |
| 2 Precondition | 1 halt check, 1 journal scan, 1 lease write, 1 dispatch for the invariant turn, 1 report read |
| 3 Dispatch | 2–3 state writes, 1–2 dispatches (consult, build), 1–2 report reads |
| 4 Poll | 0 — delegated. It is 0 **only** if delegated |
| 5 Verify | 1 dispatch per rung group, 1 report read each |
| 6 Record | 3–4 writes |
| 7 Advance | 1 lease delete, 0–1 re-scan |

Call it **15–20 orchestrator calls for a clean `collaborative` iteration**, plus
about 4 per fix-loop attempt. A `directive` iteration saves the consult dispatch
and its report read — 2 calls, not a different order of magnitude.

Do not treat those figures as measured. Derive your own from the recalibration
loop in `budgeting.md` after three iterations and replace them.

**Phase 4 is the line item that decides everything.** Polling in the
orchestrator's own context turns the cheapest phase into the most expensive one,
and the growth is cumulative and unrecoverable — nothing later gives the window
back. If the harness offers no delegation, the iteration cost is dominated by
polls and the 90 s floor applies to every one of them
(`../../fulcrum-mentor-turns/SKILL.md`, heading "Polling").

## The one rule the loop owns

**Check at phase 1 that the remaining budget covers a whole iteration. Hand back
at a phase boundary, never mid-iteration.**

Mechanism: an iteration abandoned between phase 3 and phase 6 leaves a run
mutating the app with a `started` line and no outcome. Recovering that costs a
poll of an unknown run, a re-read of the live revision, and a re-proof of
whatever the run may have changed — strictly more than the iteration would have
cost to finish. Stopping one iteration early is cheap; stopping halfway through
one is the most expensive stop available.

So, at phase 1:

```
remaining = budget - used
if remaining < cost_of_one_iteration:   hand back now
if used >= 0.85 x budget:               hand back now   (budgeting.md)
if used >= 0.65 x budget:               write the checkpoint, continue
```

`cost_of_one_iteration` is the class-calibrated figure above, plus the fix-loop
allowance if the task's history suggests it will need one. **Budget for the
ceiling, not the happy path**: a task allowed 1 build + 2 fix turns can consume
all three, and an iteration budgeted for one turn hands back in the middle of
the second.

## Sizing rules

- **Scope an iteration to about half the class budget**, not 95% of it. Agents
  overrun; leave slack (`budgeting.md`, "Prevention beats handoff").
- **Prefer many small dispatches over one large one.** Two 80k agents beat one
  160k agent: clean context each, and a failure loses half as much.
- **Never inline a summary and also point at the source.** The agent pays twice
  and cannot tell which version is authoritative.
- **Poll lean.** Request the summary form with a cursor; pull full detail once,
  on a stall or a failure. A poll loop that re-fetches the full payload each
  iteration turns the cheapest class into the most expensive.
- **An iteration that overran by 3x is usually a mis-sized task, not an
  under-budgeted one.** Check whether the row was really Mentor-turn-shaped
  before raising the rate — a row carrying more than one shape of change is a
  decomposition failure, and the fix is in `plan.md`, not in the budget.

## What to record

The per-iteration count is not durable state and does not belong in
`.fulcrum/`. It lives in the agent checkpoint
(`../../fulcrum-unattended-guardrails/references/checkpoints.md`), whose header
already carries `Class | Budget | Used | Tier`. Update `Used` at every phase
boundary, so a resuming orchestrator reads a real number rather than
reconstructing one from a transcript it should not be reading.
