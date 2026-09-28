# The iteration contract

Phase by phase: what the phase does, which writes it makes, and what it must not
do. Everything here is `[UNVERIFIED]` unless tagged otherwise — this is a
specified mechanism, not an observed one.

The phase list and the failure mode of skipping each are in `../SKILL.md`,
heading "The canonical iteration". This file is the detail.

## Phase 1 — Select

Read `.fulcrum/TASKS.md`. Take the lowest `ID` with `Status: todo` whose
dependencies are satisfied.

- A row that cannot fill columns 4–6 (`App`, `Turn`, `Verify`) **is not a task**.
  It is a plan item. Send it back to `plan.md` and decompose it first
  (`../../fulcrum-project-state/references/file-schemas.md`, heading "TASKS.md").
- Never select a row whose `Step` names a plan step that does not exist. That
  row has lost its traceability join and the work will read later as an
  undocumented addition.
- Never invent a task not in the file. If the right next action is not in
  `TASKS.md`, the loop is not the thing that should be running.

Writes: none.

## Phase 2 — Precondition

Five gates, in this order. Any gate that does not pass ends the iteration before
anything mutates.

| # | Gate | Check | On failure |
|---|---|---|---|
| 1 | Halt | `.fulcrum/HALT.md` exists? | Stop. A halt is never silently passed (`../../fulcrum-project-state/references/resume-and-halt.md`) |
| 2 | Oscillation | Scan `JOURNAL.md` column 5 for `<task-id>:fail` | Two or more → hand to the halt path. `oscillation-and-fix-loop.md` |
| 3 | Budget | Does the remaining call budget cover a whole iteration? | Hand back now, at this phase boundary. `iteration-budget.md` |
| 4 | Lease | Acquire `lease.<app>.json` for the row's `App` | A live lease held by another holder: wait or halt, never take (`../../fulcrum-project-state/references/lease-and-concurrency.md`) |
| 5 | Staleness | Cheap read-only invariant check against verified prior state | Mismatch → discard the Mentor session, open a fresh one (`../../fulcrum-mentor-turns/SKILL.md`, heading "The guard") |

Gate order is deliberate: the cheap, purely local gates run before the ones that
cost a lock or a Mentor turn.

Gate 5 is a Mentor turn and is therefore **dispatched**, not run by the
orchestrator. It is read-only, so it polls at the answer-back cadence.

The lease is not a substitute for gate 5, and gate 5 is not a substitute for
re-reading the live revision. They fail differently: the lease misses another
machine and a human in the portal; the invariant check misses nothing about
concurrency at all.

Writes: the lease file, and a session-file `acquire lease` line.

## Phase 3 — Dispatch

**Write state first, then dispatch.** The order is the whole point
(`../../fulcrum-project-state/SKILL.md`, heading "Write ordering — state before
the wait, never after the result"):

1. Set the `TASKS.md` row to `Status: active`.
2. Append the session-file `started` line and set the id in the index row's
   `InFlight`.
3. Dispatch.
4. Append the `RUN-IDS.md` line with the task id **the instant the run id is
   issued**, before the first wait.

The brief must carry everything in
`../../fulcrum-unattended-guardrails/references/delegation.md`, heading "What a
brief must contain" — including the turn cap, the halt rule, the file scope, and
the verbatim line "Correct my briefing — a correction beats agreement."

Under `collaborative` posture this phase is consult → review → build. The
consult turn's proposal is reviewed against `../../fulcrum-engine-traps/SKILL.md`
and **only the specific traps it trips** are corrected. Rewriting an idiomatic
proposal into your own design is `directive` posture with extra steps, and it
loses the one thing the consult turn was bought for: Mentor's platform idiom.

## Phase 4 — Poll

Cadence is `../../fulcrum-mentor-turns/SKILL.md`, heading "Polling" — 45 s for
answer-back turns and 90 s for model-mutating turns **with a discardable
poller**; a 90 s floor for everything without one. Never carry the 45 s rate
into an undelegated loop.

- Poll the **same run id**. Never start a competing turn because a run looks
  stalled — a "run not found" can be spurious.
- Refresh the lease's `acquired` on every non-terminal poll. A TTL shorter than
  the work it covers manufactures the expiry case on a healthy run.
- After a poller reports a run terminal, make one direct read of that run
  yourself before the next start or publish call — the session token is
  re-issued on every read `[VERIFIED]`.

## Phase 5 — Verify

Run **exactly** the rungs named in the row's `Verify` column, from
`../../fulcrum-verification/SKILL.md`, heading "The proof ladder". Not fewer
because the publish was clean; not a different set because a cheaper one came
back green.

- Rung 4 fails a change on its own and can never pass one. An empty log is the
  absence of evidence. `[SCHEMA]`
- A subagent's report of success is not proof. Require it to state what it could
  **not** verify.
- The verdict is the orchestrator's, not the dispatched agent's. Agents report
  evidence; the loop rules on it.

Outcomes, and only these three: `pass`, `fail`, `unproven`. `unproven` is
honest and is what tells a resuming session the work needs re-proving. Never
write `[x]` with an empty verdict.

## Phase 6 — Record

Four writes, in this order:

1. `TASKS.md` row: `Status`, `Verdict`, and `Done` only on a terminal state.
2. Session-file outcome line for the run.
3. `JOURNAL.md` index row: append `<task-id>:<verdict>` to column 5 and clear
   the id from `InFlight`. **Now, not at session close** — a session that
   crashes mid-task must still leave its attempt visible, and the crashed
   attempt is precisely the one oscillation detection needs.
4. `DECISIONS.md`, if the iteration made a decision. Under `collaborative`
   posture an accepted Mentor proposal is one: `Decider: mentor`, with concrete
   artifact identifiers in `Affects`.

A verdict recorded only in the orchestrator's context is not recorded.

## Phase 7 — Advance

1. Release the lease — **including on a failed turn, a halt, and a deliberate
   handoff.** A lease released only on the success path leaks on exactly the
   runs where recovery matters.
2. Re-run the oscillation scan if this iteration recorded a `:fail`.
3. Apply the mode decision point (`../SKILL.md`, heading "Mode changes what the
   loop asks between iterations").
4. Select again, or hand to the halt path.

At a `plan.md` phase boundary, additionally: remove `Status: done` rows from
`TASKS.md` (their history is already in `JOURNAL.md` and `RUN-IDS.md`) and
regenerate `HANDOFF.md`'s BRIEF.

## Worked walkthrough — one `collaborative` iteration

```
T-014 | Bind OrderList to GetOrders | app: orders-web | Turn: build | Verify: 1,3,6 | Step: P2.04

1 select      T-014 is lowest todo; P2.04 exists in plan.md
2 precondition HALT.md absent; JOURNAL scan: T-014 appears 0 times; budget 61 of 120 used;
               lease.orders-web.json written; invariant turn: "how many aggregates on
               OrderList, does widget OrderRepeater exist?" -> 1 / YES, matches ground truth
3 dispatch    TASKS row -> active; session-file started line; InFlight=T-014
              consult turn -> Mentor proposes an aggregate + Gallery
              review vs engine-traps -> correct the AggregatedAttribute trap only
              build turn dispatched; run id appended to RUN-IDS.md with "T-014"
4 poll        90 s cadence, same run id, lease refreshed each poll -> terminal
5 verify      rung 1 verbatim read-back; rung 3 revision query; rung 6 screenshot
              -> repeater shows 6 rows -> pass
6 record      TASKS: Status done, Verdict pass, [x]; session-file outcome line;
              JOURNAL Tasks += T-014:pass, InFlight -> —;
              DECISIONS D-009, Decider: mentor, Affects: orders-web / OrderList, GetOrders
7 advance     lease released; no :fail so no re-scan; expert mode -> select T-015
```

Read the last gap: the DECISIONS record exists because Mentor, not the agent,
chose the Gallery. Without it that choice is unexplainable drift six months on.
