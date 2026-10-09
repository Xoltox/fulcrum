---
name: fulcrum-unattended-guardrails
description: >
  Safety rails for long, largely unattended ODC Mentor build sessions - stop conditions, fix-turn
  caps as a ceiling, halt-and-report rules, escalation rules, subagent depth and delegation
  boundaries, tool-call budgeting, checkpoint discipline, Mentor concurrency locks and model tier
  policy. It does not own the iteration mechanism - that is `fulcrum-loop-engine`. Use when the user
  says "run the build unattended", "let it run overnight", "keep going while I'm away", "work
  through the remaining steps on your own", "don't stop and ask me every time", "delegate this to
  subagents", "long-running Mentor session", "how do I stop it breaking the app while I'm not
  watching", or when starting any session expected to run many steps without a human reading each
  one.
version: "1.0.0"
requires: >
  ODC MCP server authenticated; Mentor enabled on the tenant; a subagent
  dispatch capability with per-dispatch model tier selection; a writable
  project repo for checkpoint and handoff files.
---

# Unattended build guardrails

Load this **before** the first dispatch of an unattended session, and keep its
rules in force for the whole session. It owns nothing about *what* to build.

- ODC construct behaviour → `../fulcrum-engine-traps/SKILL.md`
- Turn granularity, prompt shape, polling cadence → `../fulcrum-mentor-turns/SKILL.md`
- Proof obligations and instruments → `../fulcrum-verification/SKILL.md`
- Plan, phases, handoff document structure → `../fulcrum-solution-init/SKILL.md`
- **The iteration mechanism** (select, dispatch, poll, verify, record, advance;
  fix-loop; oscillation detection) -> `../fulcrum-loop-engine/SKILL.md`
- Where durable state lives and its schemas → `../fulcrum-project-state/SKILL.md`

**The seam with the loop: the loop detects, this file decides.** The loop
notices a repeat failure, an exhausted cap, a regression or a runtime
step-change and hands it here. Every stop condition, cap and halt rule is
stated here and only here — do not restate one inside a loop procedure, and do
not iterate from this file.

**Delegation is the default posture.** The orchestrator supervises and never
executes; subagents work and absorb poll traffic; tiers are set per dispatch.
Run undelegated only without a subagent capability (`references/delegation.md`).

## The premise

Unattended does not mean autonomous. It means: **the agent is trusted to stop
safely, not trusted to recover from anything.** The worst outcome of an unwatched
hour must be lost time, never lost work.

The failure mode this is built against [VERIFIED]: an agent resumed a **stale
Mentor session** and published from it, silently reverting the live app past six
completed steps while the revision number advanced normally. Every platform
success signal read green; a human noticed, and recovery was manual through the
vendor portal. The only defences are a staleness guard before every mutating
turn, a checkpoint that survives the agent, and a halt rule that fires early.
Full account: `references/halt-conditions.md`, heading "The revert failure mode
 -  why halting early is cheap".

## Session-start checklist

1. **Confirm the plan exists and is written down.** Unattended execution of an
   underived plan is the highest-risk thing in this skill set. If the plan is
   not on disk, stop — that is init work, not build work.
2. **Set the model tier explicitly** per `../../MODEL-TIERS.md`. Never rely on
   inheritance. Note the per-agent context ceiling in `MODEL-TIERS.local.md`.
3. **Verify the wait mechanism once.** Prefer a native wait primitive (any
   depth, no context cost), then a discardable delegated poller, then an
   in-process sleep. Confirm it actually suspends and reuse it all session - a
   silently-swallowed wait turns a poll loop into an unbounded spin.
   Harness findings: `../../HARNESS-NOTES.md`.
4. **Record the current app revision** - the baseline for every later "did this
   land / did this revert" question.
5. **Name the checkpoint path** and the handoff path. Agents do not invent them.
6. **State the step budget for the session** — how many steps, and the halt rule.

## Hard stops — halt and report to the user

Do not work around any of these. Write the checkpoint, then stop and report.

| Trigger | Why it is a hard stop |
|---|---|
| **Stuck twice** on the same defect after a diagnostic step | Two failures at the same tier means the model of the problem is wrong, not the attempt count. Detected mechanically: two `<task-id>:fail` entries in the `.fulcrum/JOURNAL.md` session index (`../fulcrum-loop-engine/SKILL.md`, heading "Oscillation detection — mechanical, not remembered") |
| **Fix-turn cap exceeded** — more than 1 build + 2 fix turns for one step | Beyond that, Mentor is being asked to guess; each turn mutates the model |
| A mutating turn is about to run against a session whose **staleness guard did not pass** | This is the revert failure mode above |
| The live app **regressed** — something previously verified now fails | Continuing builds on top of a corrupted state |
| A step needs **the user's own action** - re-auth, a portal-only operation, an asset upload with no MCP path, **the user setting a secret in the Portal**, a UI check behind a sign-in the harness will not let an agent perform | **User-action stop, not a halt.** No amount of retrying creates a capability. Ask for the action (a screenshot or confirmation for a UI check); never attempt a workaround. Detail: `references/halt-conditions.md`, heading "User-action stops" |
| **Mentor capacity stop** - the load of an asset still refused as "busy" after the bounded retry in `../fulcrum-mentor-turns/references/mcp-surface.md`, heading "Creating and loading an asset" | Report it as capacity, not as a model, auth or trap failure. Retrying past the bound only burns the window |
| A **permission or policy denial** | Confirm it is genuine with one direct retry, then stop. Never iterate looking for a way around it |
| The change required would **weaken validation, auth, or a business rule** to clear an error | Park it, disclose it, stop |
| Two candidate actions would both **touch Mentor concurrently** | See the concurrency lock below |
| A step depends on an op **confirmed unavailable** in `tenant-profile.md` with **no fallback** recorded | Improvising a path around a missing capability is unreviewed, unrecorded drift. `references/halt-conditions.md`, heading "Halt on an unavailable op with no fallback" |
| **Runtime errors stepped up across a build step** - `app_health` `errors` / `errorPercent` higher in the after window than the before window, or `lastErrorOccurred` inside the after window `[SCHEMA]` | The deployed app is now failing for real users in a way the build turn did not predict; the only stop that reads the running app. Take the reading per `../fulcrum-verification/references/runtime-telemetry.md`; rule in `references/halt-conditions.md` |

**Not** reasons to continue: "nearly working", "one more turn", "the user said
unattended". A halt report can be the correct output.

## Never report an untouched app as healthy

No unattended run may call an app **healthy** that has had no traffic:
`appScore` is a latency score that ignores errors, and no response times **score
100** `[SCHEMA]`, the state of every app just after a publish. Request `requests`
in `metrics`; if it reads `0`, the only verdict is **"no traffic in the
window"**. Exercise the app, then re-read. Detail: `references/halt-conditions.md`.

## Never escalate model tier to break a bug

A higher tier buys a more expensive version of the same wrong guess; the missing
input is evidence about the live system. **Before any fix attempt after the first
failure, run a diagnostic step** (`../fulcrum-verification/SKILL.md`). A fix turn
with no new evidence is the same attempt again.

## Orchestrator prohibitions — categorical

The orchestrator's job is exactly four things: **read state, write a
self-contained brief, dispatch, read the terse report back.**

It must **not itself** call `mentor_start_session`, `mentor_create_asset`,
`mentor_load_asset`, `mentor_prompt` (of any kind, including "Publish") or
`mentor_get_run`; poll `publish_status`; call a `context_*` inventory tool; curl
a REST endpoint; or run browser automation or a verification gate script.

Not to finish a small piece, not to "just quickly check", not when a prior
subagent left a run half-done - dispatch one to resume that same run. Re-verifying a wave means dispatching a fresh blind verifier, never running
the check inline. **Sole exception:** a live blocker needing the user's own
action, where one direct attempt confirms the block is genuine; confirm once,
then report and wait. Rationale, brief structure, mandatory prompt elements and
the blind-verifier rule: `references/delegation.md`.

## Subagent depth is ONE LEVEL

The orchestrator dispatches directly. **Subagents never spawn subagents.**
Parallel agents are siblings, never nested. **Mutating work is depth 1, always.**

**One exception, polling only.** The Mentor-driver role may spawn **exactly one**
nested agent that **does nothing but wait and report**, when its *own* tier is
expensive and the phase is long. Every other role never spawns. [VERIFIED] on
one harness (a depth-1 subagent spawned a nested poller, 2026-10-08, and again in
a project journal); [UNVERIFIED] elsewhere. Where a nested agent cannot spawn,
use a **sibling poller** dispatched by the orchestrator. It buys nothing when
the poller tier is cheap or a native wait primitive exists - prefer the
primitive. It is mechanically checkable (one role, one action), which is why it
does not reopen the depth dial; "successor spawning" is **SUPERSEDED**. Read
`references/delegation.md` before granting any agent the ability to dispatch.

## Concurrency lock — one Mentor session per app

The lock is **per app, not per tenant**; concurrent sessions across *different*
apps are supported. [VERIFIED] A `mentor_prompt` issued while a prior prompt is
running is **silently ignored** - a racing agent gets no signal; treat it as
never sent.

- **Never dispatch two agents concurrently if both may touch Mentor on the same
  app.** A poller watching a run and a driver starting the next turn are not
  safely concurrent unless the second provably cannot start a turn.
- The cross-app ceiling is unpublished and can change. [UNVERIFIED] Fan out
  opportunistically, never on a critical path, degrade to sequential on the
  first rejection.
- Parallel subagents must **never write the same files**: assign disjoint file
  scopes; shared project documents belong to the orchestrator.
- Enforcing lease: `../fulcrum-project-state/references/lease-and-concurrency.md`.

## Budgets are tool-call counts, never token counts

**A subagent cannot measure its own token usage**, and the orchestrator learns
the count only after the agent has finished. Never write a token threshold into a
prompt (unevaluable), never ask an agent for its token usage (it will invent
one); convert every budget into a **tool-call count** for the agent's work class
and name a per-agent context ceiling in the brief. A brief with no budget is
defective. Arithmetic, per-class table, recalibration: `references/budgeting.md`.
Per-iteration accounting: `../fulcrum-loop-engine/references/iteration-budget.md`.

## Always handoff-ready

Write durable state to a checkpoint file **continuously**, after every unit of
work that produced a durable result or resumable identifier, not when near a
limit: it needs no number the agent cannot see and survives sudden death.

Write every run id, session id, job handle and revision number to the file **at
the moment it is issued**. A handle held only in context dies with the agent, and
an ODC run whose id is lost can become permanently unpollable. [VERIFIED]
Contents, discipline, worked example: `references/checkpoints.md`. Durable
project state: `../fulcrum-project-state/SKILL.md`.

## Disclose, never absorb

Every subagent brief requires the report to state: turn-budget overruns with the
actual count; any scope cut, and why; any deviation from the brief; and **what it
could not verify**, named explicitly. An unverifiable claim reported as
unverifiable is useful; reported as done it is the input to the next failure.
Honest vocabulary only: `OK` / `PARTIAL` / `PARKED` / `untested`.

## Reference files

| Open when | File |
|---|---|
| Sizing an agent's budget, or an agent overran | `references/budgeting.md` |
| Writing a brief, choosing a role, or tempted to nest a subagent | `references/delegation.md` |
| Setting up checkpoints, or resuming after a death | `references/checkpoints.md` |
| A step is failing repeatedly, or needs a user action, and you must decide whether to continue | `references/halt-conditions.md` |
| A reading from the running app looks like a stop signal, or you are about to call an app healthy | `references/halt-conditions.md`, headings "The runtime-shaped stop" and "Never report an untouched app as healthy" |
| You need to run the tasks, not decide whether to stop | `../fulcrum-loop-engine/SKILL.md` |
