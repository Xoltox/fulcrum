# Halt conditions, fix-turn caps, escalation

## The turn cap

**Per step: 1 build turn + at most 2 fix turns.** [VERIFIED]

**What counts as the build turn.** A step's build is either one turn or a **build
pass of up to 4 short granular turns** (one region or object per turn, in the same
session, under the step's one objective); the pass counts as the one build turn.
More than 4 build turns means the step is too big: split it into two steps, each
ending in its Publish turn, rather than spending fix turns on build work. Consult,
guard and Publish turns are not build turns. (Fulcrum rule)

**A batch is one dispatch, and the cap still binds per row.** A batch's build pass stays inside
those 4 short turns; rows that do not fit go to the next dispatch. On batch failure, one fix turn on
the batch, then split per row. That fix turn counts against every row in the batch, so each row
keeps at most one more. A split that handed each row a fresh cap would turn 2 fix turns into 3
mutating guesses at the same defect. Procedure:
`../../fulcrum-loop-engine/references/oscillation-and-fix-loop.md`, heading "A failed batch".
(Fulcrum rule)

**A `fix` row gets 2 fix turns and no build turn;** two `:fail` parks it (same file,
heading "Late failures"). (Fulcrum rule)

Mentor is not a batch processor - one objective per turn (see
`../../fulcrum-mentor-turns/SKILL.md`). Past the build pass plus 2 fix turns on one
step, the pattern observed is not convergence: it is Mentor guessing, and each guess mutates the
model. The cap exists because the cost of an extra turn is not a wasted turn, it
is an unreviewed change to a live application.

On exceeding the cap: write the checkpoint, park the row with an honest status,
report. That is a lane stop ("Lane stops" below), not a halt. Do not carry the
overrun silently into the next dispatch.

## The escalation ceiling

This file owns the **ceiling and the terminal condition**. Running the attempts - issuing the turns, re-verifying, recording each one - is the loop's:
`../../fulcrum-loop-engine/references/oscillation-and-fix-loop.md`, heading
"The fix-loop". Do not iterate from this file.

Three rules bound every escalation, in force whoever is running it:

- **A diagnostic step is mandatory before every fix attempt after the first
  failure.** Not a fix - an observation.
- **At most two fix attempts** after the build turn. That is the turn cap above.
- **Still failing after the second -> stuck twice -> lane stop, report to the
  user** ("Lane stops" below). Detected mechanically, by scanning the session index rather than by an
  agent remembering: `../../fulcrum-loop-engine/SKILL.md`, heading "Oscillation
  detection - mechanical, not remembered". **The loop detects; this file
  decides.**

### The diagnostic step is not optional

**Before any fix attempt after the first failure, gather new evidence.** A fix
turn with no new evidence behind it is not a second attempt; it is the first
attempt again, and it will fail the same way.

Repeated same-tier attempts repeat the same wrong guess. Two failures mean the
*model of the problem* is wrong, not that the attempt count is too low.

What counts as a diagnostic: reading the actual model state back rather than
trusting a success signal; capturing the running app and looking at it; querying
live rows through the diagnostic REST endpoint pattern; reading the failing
assertion's actual value rather than its expectation. See
`../../fulcrum-verification/SKILL.md` for which instrument catches which defect class.

What does not count: re-reading the spec, re-reading your own prior turn,
rephrasing the same request, or asking Mentor whether it did the thing.

### Never escalate model tier to break a bug

Not for a stuck bug, not for a second failed fix turn. A higher tier mostly buys
a more expensive version of the same guess, because the missing input is
evidence about the live system, not reasoning capacity. Escalating also
converts a diagnosable failure into an expensive one, and the unattended session
still ends at the same stop.

Tier policy is phase-based and is set at dispatch time, not adjusted reactively:
`../../../MODEL-TIERS.md`.

## Hard stops

The orchestrator writes `.fulcrum/HALT.md` first (the file before the journal line,
per `../../fulcrum-project-state/references/resume-and-halt.md`), then stops and
reports; a driver only reports and stops. Do not work around any of these. If the halting dispatch returned
`session_state: open`, the orchestrator keeps the lease and `HALT.md` records the
open `sessionId` (`../../fulcrum-project-state/references/lease-and-concurrency.md`,
"Hold").

| Trigger | Detail |
|---|---|
| A previously verified behaviour now fails, beyond one app | Regression. Continuing builds on a corrupted state. Confined to one app: "Lane stops" below |
| A step needs the **user's own action** | A portal-only operation, an upload with no MCP path, the user setting a secret in the Portal, a role grant, a sign-in-gated UI check. A user-action stop, not a halt: see "User-action stops" below. Retrying does not create a capability |
| **Mentor capacity stop** | With no other driver in flight, the first turn of a session still refused as busy after the bounded retry in `../../fulcrum-mentor-turns/references/mcp-surface.md`, heading "Creating and loading an asset". See "Mentor capacity stop" below |
| A permission or policy denial | Confirm with **one** direct retry, then stop. Never iterate looking for a way around it |
| The fix would weaken validation, auth, or a business rule | Park, disclose, stop. Phrase every "do not touch X" as *"do not touch X unless X is the root cause - if so, fix it and disclose prominently"* |
| **All lanes flat** | Every lane with open rows is flat or parked, at least one flat. See "Stall and no-op decisions" below |
| **Auth lost** | An auth error on any call. There is no in-session recovery path and every lane shares the connection `[VERIFIED]`. Turns keep running server-side, so after the user reconnects, read the same runs: `../../fulcrum-mentor-turns/references/recovery.md`, heading "1. Transport-level auth expires mid-turn" |
| **Budget** | The orchestrator's budget reached the hand-back trigger. One budget funds every lane: stop selecting everywhere, let running lanes return, record them, hand back (`../../fulcrum-loop-engine/references/iteration-budget.md`, heading "The one rule the loop owns"). This stop is that hand-back: it writes no `HALT.md`, because resuming needs no human decision |
| **Secret exposed** | A secret value reached a prompt, a brief, a journal, a report or a committed file. A prompt is stored and replayed, so no later turn removes it; every lane keeps using what is exposed until the user rotates it. Never repeat the value in `HALT.md` |
| **Surface drift** | The live tools differ from the latest snapshot. Skill text naming a tool or parameter can no longer be trusted, on any lane. Full re-probe before any mutating work: `../../fulcrum-mentor-turns/references/mcp-surface.md`, heading "Re-probing the surface" |
| A step depends on an op **confirmed unavailable** with **no fallback** recorded in `tenant-profile.md` | See "Halt on an unavailable op with no fallback" below |
| The plan for the current step does not exist in writing | Deriving a plan mid-unattended-run is the highest-risk act available |
| **Runtime error step-change across a G1** | `app_health` `errors` / `errorPercent` higher in the after window than the before window, or `lastErrorOccurred` falling inside the after window. See below |

## Lane stops

**A stop whose cause lives in one app is scoped to its lane** (Fulcrum rule). It says the model of
one defect, or the state of one app, is wrong, which says nothing about another app. Stopping every
lane for it is the wave barrier the frontier removed. Permission denial, an unavailable op with no
fallback and a missing plan stay engagement-wide ("Hard stops" above).

| Trigger | Detail |
|---|---|
| Stuck twice after a diagnostic step | The escalation ceiling is exhausted. Two `:fail` entries for one task id in the session index is this firing mechanically |
| Turn cap exceeded on one row | 1 build (a pass of <= 4 short turns counts as one) + 2 fix |
| A mutating turn about to run and the **staleness guard did not pass** | See "the revert failure mode" below |
| Two actions would both touch Mentor concurrently on that app | Serialise, or stop and ask |
| A previously verified behaviour on that app now fails, confined to it | Regression. Continuing builds on a corrupted state |

1. Park the row: `Status: parked`, `Verdict: fail`, `Blocked on: the user`. No `HALT.md`.
2. Its dependents hold. A row of that lane that does not depend on it stays selectable, unless the
   dispatch returned `session_state: open`, or the stop is about the app itself (the last three
   above). Then the whole lane waits for the user: an open session keeps `open_session` on the lease
   (`../../fulcrum-project-state/references/lease-and-concurrency.md`, "Hold").
3. Report the lane, as "Honest reporting on halt" below lays out. Other lanes continue.
4. A parked row resumes only on a user decision, recorded in `DECISIONS.md`. A `:fail` count is never
   reset, so a twice-failed row comes back under a new id: the orchestrator rewrites its dependents'
   `DependsOn` to the new id and closes the old row (`Status: done`, `Verdict: fail`).

Nothing runnable left is not an exemption. The discriminator is `Verdict: fail`: a row parked with it
reads as flat in "Stall and no-op decisions" below, so the last lane to stop this way halts the
engagement. A row parked on a user action carries any other verdict and does not read flat.

## Halts with parallel lanes

**A halt stops the engagement, not one lane.** `HALT.md` is one file and its existence stops
every session (`../../fulcrum-project-state/references/resume-and-halt.md`). The trigger says the
live state, or something every lane rests on, cannot be trusted; other lanes may consume it, and
each further turn is one more unreviewed change while nobody has looked.

1. Write `HALT.md` first. From then on, no new dispatch of any kind on any lane.
2. Do not cancel a running dispatch. A run abandoned mid-turn has no verdict and may hold unpublished
   changes, which is worse than the turn finishing. Let it reach terminal and record its verdict.
3. Another trigger arriving from a finishing lane goes into the same `HALT.md`, under "What was
   tried", with its own app and task. There is never a second halt record.
4. Report after the last running dispatch returns. A dispatch returning `session_state: open` keeps
   its lease and `HALT.md` names its `sessionId`.

**Waiting is not a halt.** These hold only the row's dependents, never another lane. The row's own
lane continues with rows that do not depend on it:

- A `parked` row, including every lane stop above and every user-action stop below.
- A `blocked` row: a library consumer waiting on the index, for example.
- A lease held by someone else: that lane waits, or the orchestrator reports it.
- A parked lane (below): its rows wait as one.

The test: a halt means something is wrong; a wait means something is owed. Stopping every lane to
wait is the wave barrier the frontier removed, and it buys no safety.

**Rigor changes none of this.** Stops, caps and halts fire the same at `demo`, `pilot` and
`production`: gates are depth of evidence, not safety (`../../fulcrum-verification/SKILL.md`, heading
"Gates and rigor"). A `demo` run takes fewer readings, so a stop that depends on a reading can fire
later; it never fires differently.

## Stall and no-op decisions

**The loop detects; this file decides.** Detection:
`../../fulcrum-loop-engine/references/oscillation-and-fix-loop.md`, heading "Stall detection". Fulcrum
rule; the threshold is unmeasured. The two-fail rule stands and fires first where it applies. The
stall catches what it cannot see: a lane failing differently each time, returning `unproven`, or
splitting batches with nothing closing.

| Detected | Decision |
|---|---|
| A lane's done-count flat across 3 consecutive dispatches | **Park the lane.** Set its open rows `parked` with `Blocked on: the user`, the row it stalled on `Verdict: fail`, and report the rows, the dispatches and the last verified-good revision. Other lanes continue; rows depending on the parked lane wait with it |
| Every lane with open rows is flat or parked, at least one flat | **Halt.** A row parked with `Verdict: fail` reads as flat. A single-app project has one lane, so its stall is a halt. All lanes parked on user actions alone is a user-action stop, not a halt |
| Publish terminal, revision unchanged | **No-op.** The change did not land, whatever the outcome field says. The attempt failed: it enters the fix-loop under the turn cap, starting with a diagnostic step. Do not re-publish: a new revision needs a model change, and Mentor can silently ignore a prompt `[VERIFIED]` |

A parked lane resumes only on a user decision, recorded in `DECISIONS.md`, because the same inputs
would stall the same way. Never escalate tier to clear a stall: the missing input is evidence or a
decision, not reasoning capacity.

## User-action stops

A user-action stop differs from a halt: nothing has gone wrong, the next step is
simply not the agent's to take. Write the checkpoint, set the `TASKS.md` row to `parked` (Blocked on: the user;
`PARKED` is the report word), and report one concrete ask. Do not retry, and do not look for a way around it.

- **The user sets a secret in the Portal.** A secret value never goes in a
  Mentor prompt, a brief, a journal or a report. The agent names the secret
  setting, where to set it, and what to confirm back (that it is set, never its
  value), then waits for that confirmation.
- **A check that needs signing in to a UI**, when the harness blocks credential
  entry (a permission layer may refuse typed credentials and any workaround that
  materialises them, such as an auto-submitting local form). [VERIFIED] Brief it
  as "ask the user for a screenshot or a confirmation". Never let an agent
  attempt a workaround; the refusal is the control working, not an obstacle.
  Before handing off, try an approved generated sample persona
  (`delegation.md`, heading "A UI check behind a sign-in is a user-action
  hand-off").
- **A role grant.** A role-gated app has no authenticated render until the user holds
  the role in Development, and neither an agent nor the renderer can grant it. Ask when
  the plan is made, not when the render is due: asked late, it parks the render with the
  build already done (`../../fulcrum-render-check/references/harness-limits.md`, heading
  "Session identity"). `[SINGLE-OBSERVATION]`
- A portal-only operation and an upload with no MCP path follow the same shape.
  Lost auth does not: every lane shares it, so it is a halt ("Hard stops" above).

## Mentor capacity stop

**The first capacity text anywhere stops the fan-out** (Fulcrum rule), even when the driver's retry
then succeeded. Add no driver; let running dispatches finish; continue sequentially for the rest of
the session. A refused row is not a failure: it goes back to `todo` and records no `:fail`. Pushing
on after that text competes for the capacity the running lanes hold.

When a first turn is refused after the bounded retry in `mcp-surface.md` (3 retries, growing backoff,
each wait verified to block) and no other driver is in flight: close the session, halt, and report
**"Mentor capacity stop"**. It is not a model failure, an auth failure or a trap. The session is
not stale and no work was lost; the ask to the user is to retry later. Retrying
past the bound consumes window for no new information.

## The runtime-shaped stop

Every other stop above is model- or turn-shaped: it fires on what the platform
said about a turn. This one fires on what the deployed app actually did, and it
is the only stop here that can catch a change that published cleanly, verified
against the model, and then broke the running app.

**The rule.** Take an `app_health` reading bracketing each G1 exercise, so how often
this stop can fire follows the rigor table. If, across that window, `errors` or `errorPercent` steps up, or `lastErrorOccurred` falls inside
the after window, **halt and report.** `[SCHEMA]` - those fields and their
meanings are asserted by the ODC MCP tool schema, not observed in a Fulcrum run.

- The before/after window comparison is **instrument selection and belongs to
  verification**: `../../fulcrum-verification/references/runtime-telemetry.md`,
  heading "Which op answers which question". Take the reading from there. This
  file adds only the stop.
- It is a **hard stop, not a fix trigger.** A new class of runtime error means
  the live app is now failing for real users in a way the build turn did not
  predict. Continuing builds the next step on top of it.
- **Bracket tightly.** `app_health` returns aggregates and a wide window
  averages the incident away. `[SCHEMA]`
- **Absence of a step-change is not a pass.** Telemetry fails a change on its
  own and can never pass one; a silent defect writes no log line. `[SCHEMA]`
- `app_health` requires an environment key explicitly and has no default.
  `[SCHEMA]` A figure read from the wrong stage is not evidence about this one.

## Halt on an unavailable op with no fallback

**The rule.** When a step depends on an op recorded **confirmed unavailable**
in `tenant-profile.md` (`../../fulcrum-solution-init/references/tenant-capability-probe.md`,
heading "Tool availability - three states, not two") and no fallback is
recorded for it (`../../fulcrum-solution-init/references/tool-availability-and-fallback.md`),
**halt and report. Do not improvise a workaround.**

**The mechanism.** An unattended agent that works around a missing capability
invents an unreviewed approach on the spot and records it nowhere durable. The
deviation does not surface at the moment it happens - it surfaces later as
unexplainable drift: a screen built a different way than the plan describes, a
data path that does not match the spec, with no decision record explaining
why. A halt costs one interruption. A silent improvisation costs a future
session trying to reconcile behaviour against a plan that never mentioned it.

This is distinct from the ordinary fix-loop: a fix turn retries the *same* op
after gathering evidence. This halt fires when the op itself has no working
path at all - there is nothing to retry.

Do not confuse **unavailable** with **unknown**. An op that is merely unknown
(never dispatched - the default and correct state for every mutating op) is
not a halt condition by itself; dispatch it as the plan calls for and record
the outcome. This rule fires only once dispatch has actually failed with a
resolution error and no fallback exists.

## Never report an untouched app as healthy

**An unattended run must never emit a "healthy" verdict for an app that has had
no traffic.** This is the most dangerous false green available to an unattended
session, because it is the app's default state immediately after every publish.

**The mechanism.** `appScore` is an Apdex-style **latency** score computed from
response times. It ignores errors entirely. An app with no traffic has no
response times, and no response times **scores 100** `[SCHEMA]` - identical to a
fast, correct, heavily-used app. So a freshly published app nobody has touched
reports perfect health from zero evidence, and an agent with nobody watching
reports it onward as a pass.

The guardrail:

- Request `requests` in `metrics` on every `app_health` call.
- If `requests` is present in the echo and reads `0`, the only permitted verdict
  is **"no traffic in the window"**. Never "healthy", never "no errors", never a
  pass on any rung.
- If the app has had no traffic, **exercise it first**, then re-read. A reading
  over traffic nobody generated measures nothing.
- A metric absent from the row is an **absent reading, not a zero** `[SCHEMA]`.
  Report it as unavailable. Reading a missing `errors` as `errors: 0` converts a
  blind spot into a clean bill of health.
- Never synthesise availability or uptime - the platform exposes neither
  `[SCHEMA]`, and every candidate proxy lets a zero-traffic app report as up.

Full trap detail, including the paging and sampling cases:
`../../fulcrum-verification/references/runtime-telemetry.md`.

## Not reasons to continue

- "It is nearly working."
- "One more turn should do it."
- "The user said unattended, so they do not want to be interrupted."
- "The remaining piece is small enough to just do inline."

An unattended session's correct output can be a halt report. The user chose
unattended to avoid supervising *progress*, not to authorise damage.

## The revert failure mode - why halting early is cheap

[VERIFIED] An agent resumed a **stale Mentor session** and published from it.
The publish silently reverted the live application past six completed steps of
verified work. The revision number advanced normally, so every platform success
signal read green.

- No automated gate caught it. A human noticed the app looked wrong.
- Rollback tooling could not reach the last clean state.
- Recovery was manual, through the vendor portal.

The generalisable facts:

1. **A publish from a stale session is a destructive write that reports
   success.** Revision advance is not evidence of forward progress; it is only
   evidence that *something* was written.
2. **Platform success signals cannot detect this defect class.** Neither can a
   validation-error count.
3. **An unattended run can therefore destroy verified work without emitting a
   single error.**
4. **Rollback is not a safety net.** Do not plan on the assumption that a bad
   publish is reversible.

The three defences, all of which this skill mandates:

- A **staleness guard before every mutating dispatch** - verify the session's view
  of current state against an independent read (published-state `context_*`
  once indexed - the lag is variable - and the live revision via `app_revisions`), never
  against the session's own read-back; before any "Publish" turn, re-read the
  revision
  (`../../fulcrum-mentor-turns/SKILL.md`).
- A **checkpoint that survives the agent**, recording the revision observed
  before changes (`checkpoints.md`).
- A **halt rule that fires early**, because an hour of lost time is
  recoverable and six steps of lost work is not.

## Honest reporting on halt

The halt report states, in order:

1. **Status** - `PARTIAL` or `PARKED`. Never a bare "failed".
2. **The last verified-good state** - the revision, with the evidence that
   verified it.
3. **What was attempted**, including each diagnostic and what it showed.
4. **What could not be verified**, named explicitly.
5. **The specific decision or action the user needs to make.** A halt report
   without an ask is an interruption, not an escalation.
6. **The checkpoint path.**
