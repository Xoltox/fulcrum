# The iteration contract

Phase by phase: what the phase does, which writes it makes, and what it must not
do. Everything here is `[UNVERIFIED]` unless tagged otherwise - this is a
specified mechanism, not an observed one.

The phase list and the failure mode of skipping each are in `../SKILL.md`,
heading "The canonical iteration". This file is the detail.

## Phase 1 - Select

Read `.fulcrum/TASKS.md`. Take the lowest `ID` with `Status: todo` whose
dependencies are satisfied.

- A row that cannot fill columns 4-6 (`App`, `Turn`, `Verify`) **is not a task**.
  It is a plan item. Send it back to `plan.md` and decompose it first
  (`../../fulcrum-project-state/references/file-schemas.md`, heading "TASKS.md").
- Never select a row whose `Step` names a plan step that does not exist. That
  row has lost its traceability join and the work will read later as an
  undocumented addition.
- **A Mentor step is selected whole.** When the selected row is a Mentor row,
  every `todo` row with the same `Step` and `App` (for example its `build`
  and `publish` rows) joins it in the one driver dispatch (phase 3). They go
  `active` together; each still closes on its own `Verify` evidence, and a row
  the dispatch did not reach goes back to `todo`.
- Never invent a task not in the file. If the right next action is not in
  `TASKS.md`, the loop is not the thing that should be running.

Writes: none.

## Phase 2 - Precondition

Six gates, in this order (gates 4 and 5 apply to Mentor turns only). Any gate that does not pass ends the iteration before
anything mutates.

| # | Gate | Check | On failure |
|---|---|---|---|
| 1 | Halt | `.fulcrum/HALT.md` exists? | Stop. A halt is never silently passed (`../../fulcrum-project-state/references/resume-and-halt.md`) |
| 2 | Oscillation | Scan `JOURNAL.md` column 5 for `<task-id>:fail` | Two or more -> hand to the halt path. `oscillation-and-fix-loop.md` |
| 3 | Budget | Does the remaining call budget cover a whole iteration? | Hand back now, at this phase boundary. `iteration-budget.md` |
| 4 | Lease | Mentor turns only: the orchestrator (sole lease writer) acquires `lease.<app>.json` for the row's `App` before the dispatch, `ttl_seconds` sized to the dispatch's wall-clock budget plus margin. `code`, `infra`, `external` and `manual` rows take no lease and skip this gate and gate 5 (`../../fulcrum-project-state/references/file-schemas.md`, heading "TASKS.md", "Turn types") | A live lease held by another holder: wait or halt, never take (`../../fulcrum-project-state/references/lease-and-concurrency.md`) |
| 5 | Staleness | Mentor turns only: cheap read-only invariant check against verified prior state, run as the first turn of the step's one driver dispatch | Mismatch, no unpublished changes -> close the Mentor session, open a fresh one. Unpublished changes held -> never close: Publish (if the step's own build verified) or halt `keep-open` (`../../fulcrum-mentor-turns/SKILL.md`, heading "The guard") |
| 6 | External system | A row consuming an external system: `.fulcrum/external/<system>.md` exists | Missing -> the row is not ready; the orchestrator records the system first (`file-schemas.md`, heading "external/<system>.md") |

Gate order is deliberate: the cheap, purely local gates run before the ones that
cost a lock or a Mentor turn.

Gate 5 is a Mentor turn and is therefore **dispatched**, not run by the
orchestrator - but not as a dispatch of its own. It is the first turn of the
step's single driver dispatch (phase 3), in the same session that then builds,
so the check tests the session that mutates. It is read-only, so it polls at
the answer-back cadence. A fresh `mentor_load_asset` loads the latest
published revision, so a passing guard proves the previous step landed
(published); it is not a session-staleness test. Gate 5 is also the per-step
Mentor liveness check (`../../fulcrum-solution-init/references/tenant-capability-probe.md`,
heading "0. Mentor liveness gate"): a guard answer that names the app's real
screens and widgets proves Mentor is live; a generic or no-app answer is a
liveness fail and halts.

The lease is not a substitute for gate 5, and gate 5 is not a substitute for
re-reading the live revision. They fail differently: the lease misses another
machine and a human in the portal; the invariant check misses nothing about
concurrency at all.

Writes (Mentor turns only, by the orchestrator): the lease file, and a session-file
`acquire lease` line. No one refreshes the lease mid-dispatch; pollers and drivers
never write it.

## Phase 3 - Dispatch

**Write state first, then dispatch.** The order is the whole point
(`../../fulcrum-project-state/SKILL.md`, heading "Write ordering - state before
the wait, never after the result"):

Same order as `../../fulcrum-project-state/SKILL.md`, heading "Before the first
mutating call":

1. At session start (once): the orchestrator mints the session id, creates
   `journal/<session-id>.md` and appends the `JOURNAL.md` index row,
   `State: open`. Drivers never mint ids or edit the index; the brief names
   the session file they append to.
2. Mentor turns: the lease from phase 2 is held (before app creation it is
   keyed by the intended app name).
3. Set the `TASKS.md` row to `Status: active`, then append the session-file
   `started` line and set the id in the index row's `InFlight`.
4. Dispatch - **one driver dispatch per plan step**, covering the gate 5
   guard, consult (if any), build, fix and the step's Publish turn in one
   Mentor session. Brief inputs include `sessionId` (only to resume an open
   session a previous dispatch of the *same* step handed back) and
   `on_exit: close | keep-open` (default `close`); the driver reports
   `sessionId`, `session_state` and `unpublished_changes`.
5. The driver appends the `RUN-IDS.md` line with the task id **the instant
   the run id is issued**, before the first wait.
6. When the dispatch returns `session_state: closed`, the orchestrator releases
   the lease; when it returns `session_state: open`, it keeps the lease (phase 7
   restates both for every exit path).

The brief must carry everything in
`../../fulcrum-unattended-guardrails/references/delegation.md`, heading "What a
brief must contain" - including the turn cap, the halt rule, the file scope, and
the verbatim line "Correct my briefing - a correction beats agreement."

Under `collaborative` posture this phase is consult -> review -> build, all
inside the one dispatch and session - consult and build never split across
dispatches. The consult turn's proposal is reviewed (by the driver, against the
trap entries the brief carries from `../../fulcrum-engine-traps/SKILL.md`)
and **only the specific traps it trips** are corrected. Rewriting an idiomatic
proposal into your own design is `directive` posture with extra steps, and it
loses the one thing the consult turn was bought for: Mentor's platform idiom.

## Phase 4 - Poll

Cadence is `../../fulcrum-mentor-turns/SKILL.md`, heading "Polling" - 45 s for
answer-back turns and 90 s for model-mutating turns **with a discardable
poller**; a 90 s floor for everything without one. Never carry the 45 s rate
into an undelegated loop.

- Poll the **same run id**. Never start a competing turn because a run looks
  stalled - a "run not found" can be spurious.
- No per-poll lease refresh. The lease's `ttl_seconds` was sized in gate 4 to
  the dispatch's whole wall-clock budget plus margin, because a TTL shorter
  than the work it covers manufactures the expiry case on a healthy run.
  Pollers and drivers never write the lease.
- After a poller reports a run terminal, make one direct read of that run
  yourself before the next start or publish call - the poller's report is
  second-hand (see `../../fulcrum-mentor-turns/references/polling.md`).

## Phase 5 - Verify

Run **exactly** the rungs named in the row's `Verify` column, from
`../../fulcrum-verification/SKILL.md`, heading "The proof ladder". Not fewer
because the publish was clean; not a different set because a cheaper one came
back green.

- A check that reads published state waits out the index lag, re-reads, then
  decides; a FAIL inside the lag window is not a FAIL. A build step that
  created an app or added screens is not done until the render obligation is
  met (`../../fulcrum-verification/SKILL.md`, heading "Render obligation");
  a sign-in the harness cannot perform is a user-action hand-off.
- Rung 4 fails a change on its own and can never pass one. An empty log is the
  absence of evidence. `[SCHEMA]`
- A subagent's report of success is not proof. Require it to state what it could
  **not** verify.
- The verdict is the orchestrator's, not the dispatched agent's. Agents report
  evidence; the loop rules on it.

Outcomes, and only these three: `pass`, `fail`, `unproven`. `unproven` is
honest and is what tells a resuming session the work needs re-proving. Never
write `[x]` with an empty verdict.

## Phase 6 - Record

Four writes, in this order. The orchestrator writes `TASKS.md` and the
`JOURNAL.md` index; a driver returns its verdict and evidence and only appends
rows to the session journal file the brief names and to `RUN-IDS.md` (`file-schemas.md`, heading "Write ownership"):

1. `TASKS.md` row: `Status`, `Verdict`, and `Done` only on a terminal state.
2. Session-file outcome line for the run.
3. `JOURNAL.md` index row: append `<task-id>:<verdict>` to column 5 and clear
   the id from `InFlight`. **Now, not at session close** - a session that
   crashes mid-task must still leave its attempt visible, and the crashed
   attempt is precisely the one oscillation detection needs.
4. `DECISIONS.md`, if the iteration made a decision. Under `collaborative`
   posture an accepted Mentor proposal is one: `Decider: mentor`, with concrete
   artifact identifiers in `Affects`.

If the dispatch returned `session_state: open`, the session-file outcome line (write 2)
names the open Mentor `sessionId` and `unpublished_changes`, and `InFlight` keeps the
task id: the step is not finished, so write 1 leaves the row `active` with no terminal
verdict.

A verdict recorded only in the orchestrator's context is not recorded.

## Phase 7 - Advance

1. The orchestrator releases the lease when the dispatch returns
   `session_state: closed` - **including on a failed turn, a halt, and a
   deliberate handoff.** A lease released only on the success path leaks on
   exactly the runs where recovery matters. When the dispatch returns
   `session_state: open` (budget stop, or a halt with `on_exit: keep-open`), the
   orchestrator **keeps** the lease: it rewrites it with `open_session` set to the
   returned `sessionId` and a new `ttl_seconds` sized to the expected resume
   dispatch, or to a hold until the user decides. The next action is then a
   resume dispatch of the same step with that `sessionId`, or a halt for the
   user (`HALT.md` records the open sessionId) - never a new step on that app.
   Release comes only with a dispatch that returns `session_state: closed`
   (`../../fulcrum-project-state/references/lease-and-concurrency.md`, "Hold").
2. Re-run the oscillation scan if this iteration recorded a `:fail`.
3. Apply the mode decision point (`../SKILL.md`, heading "Mode changes what the
   loop asks between iterations").
4. Select again, or hand to the halt path.

**At a wave close**, before the next wave or the end of the session: reconcile.
Read the wave's index rows, session files and new `RUN-IDS.md` lines, then
rewrite `TASKS.md`, `project.md` and `HANDOFF.md` PART 2 to match, using the
checklist in `../../fulcrum-project-state/references/file-schemas.md`, heading
"Write ownership" ("Reconcile at every wave close").

At a `plan.md` phase boundary, additionally: remove `Status: done` rows from
`TASKS.md` (their history is already in `JOURNAL.md` and `RUN-IDS.md`) and
regenerate `HANDOFF.md`'s BRIEF.

## Worked walkthrough - one `collaborative` iteration

```
T-014 | Bind OrderList to GetOrders | app: orders-web | Turn: build | Verify: 1,3,6 | Step: P2.04

1 select      T-014 is lowest todo; P2.04 exists in plan.md
2 precondition HALT.md absent; JOURNAL scan: T-014 appears 0 times; budget 61 of 120 used;
               lease.orders-web.json written by the orchestrator, ttl = dispatch budget + margin
3 dispatch    TASKS row -> active; session-file started line; InFlight=T-014
              ONE driver dispatch, one session, on_exit: close:
              invariant turn (gate 5): "how many aggregates on OrderList, does
              widget OrderRepeater exist?" -> 1 / YES, matches ground truth
              consult turn -> Mentor proposes an aggregate + Gallery
              review vs engine-traps -> correct the AggregatedAttribute trap only
              build turn; run id appended to RUN-IDS.md with "T-014"; Publish turn
4 poll        90 s cadence, same run id, no lease writes -> terminal
5 verify      rung 1 verbatim read-back -> pass; rung 3 revision query -> pass;
              rung 6 untested (no browser capability recorded for this project, so
              fulcrum-renderer cannot run; render hand-off to the user) -> unproven
              until the user's render returns
6 record      TASKS: Verdict unproven (rung 6 hand-off), no [x]; session-file outcome line;
              JOURNAL Tasks += T-014:unproven, InFlight -> -;
              DECISIONS D-009, Decider: mentor, Affects: orders-web / OrderList, GetOrders
7 advance     driver returned session_state: closed -> lease released; no :fail so no re-scan; expert mode -> select T-015
```

Read the last gap: the DECISIONS record exists because Mentor, not the agent,
chose the Gallery. Without it that choice is unexplainable drift six months on.
