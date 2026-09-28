---
name: fulcrum-unattended-guardrails
description: >
  Safety rails for long, largely unattended ODC Mentor build sessions — stop
  conditions, fix-turn caps as a ceiling, halt-and-report rules, escalation
  rules, subagent depth and delegation boundaries, tool-call budgeting,
  checkpoint discipline, Mentor concurrency locks and model tier policy. It does
  not own the iteration mechanism — that is `fulcrum-loop-engine`. Use when the user says "run the
  build unattended", "let it run overnight", "keep going while I'm away", "work
  through the remaining steps on your own", "don't stop and ask me every time",
  "delegate this to subagents", "long-running Mentor session", "how do I stop
  it breaking the app while I'm not watching", or when starting any session
  expected to run many steps without a human reading each one.
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
- **The iteration mechanism** — selecting a task, dispatching, polling,
  verifying, recording and advancing it, the fix-loop and oscillation
  detection → `../fulcrum-loop-engine/SKILL.md`
- Where durable state lives and its schemas → `../fulcrum-project-state/SKILL.md`

**The seam with the loop: the loop detects, this file decides.** The loop
notices a repeat failure, an exhausted cap, a regression or a runtime
step-change and hands it here. Every stop condition, cap and halt rule is
stated here and only here — do not restate one inside a loop procedure, and do
not iterate from this file.

**Delegation posture — the default, not an advanced mode.** Fulcrum is meant to
run aggressively orchestrated: the orchestrator supervises and never executes,
subagents do the work and absorb poll traffic, and tiers are set per dispatch.
Run undelegated only when the harness offers no subagent capability. The rules
for all of it are in this file and `references/delegation.md`.

## The premise

Unattended does not mean autonomous. It means: **the agent is trusted to stop
safely, not trusted to recover from anything.** Every rule below exists so the
worst outcome of an unwatched hour is lost time, never lost work.

The failure mode this is built against [VERIFIED]: an agent resumed a **stale
Mentor session** and published from it, silently reverting the live app past six
completed steps while the revision number advanced normally. Every platform
success signal read green; a human noticed the app looked wrong, and recovery
was manual through the vendor portal. Platform success signals cannot detect
this class of damage, so an unattended run can destroy verified work without
emitting a single error. The only defences are a staleness guard before every
mutating turn, a checkpoint that survives the agent, and a halt rule that fires
early. Full account: `references/halt-conditions.md`, heading "The revert
failure mode — why halting early is cheap".

## Session-start checklist

Before the first dispatch:

1. **Confirm the plan exists and is written down.** Unattended execution of an
   underived plan is the highest-risk thing in this skill set. If the plan is
   not on disk, stop — that is init work, not build work.
2. **Set the model tier explicitly** per `../../MODEL-TIERS.md`. Never rely on
   inheritance.
3. **Verify the wait mechanism once.** Prefer a native wait primitive (any
   depth, no context cost), then a discardable delegated poller, then an
   in-process sleep. Confirm the chosen one actually suspends and reuse it all
   session — a silently-swallowed wait turns a poll loop into an unbounded spin.
   Harness-specific findings: `../../HARNESS-NOTES.md`.
4. **Record the current app revision.** It is the baseline every later "did this
   land / did this revert" question is answered against.
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
| A step needs **the user's own action** — re-auth, a portal-only operation, an asset upload with no MCP path | No amount of retrying creates a capability |
| A **permission or policy denial** | Confirm it is genuine with one direct retry, then stop. Never iterate looking for a way around it |
| The change required would **weaken validation, auth, or a business rule** to clear an error | Park it, disclose it, stop |
| Two candidate actions would both **touch Mentor concurrently** | See the concurrency lock below |
| A step depends on an op **confirmed unavailable** in `tenant-profile.md` with **no fallback** recorded | Improvising a path around a missing capability is unreviewed and unrecorded drift. Halt, do not work around it — `references/halt-conditions.md`, heading "Halt on an unavailable op with no fallback" |
| **Runtime errors stepped up across a build step** — `app_health` `errors` / `errorPercent` higher in the after window than the before window, or `lastErrorOccurred` inside the after window `[SCHEMA]` | The deployed app is now failing for real users in a way the build turn did not predict. This is the only stop here that reads the running app rather than the model. Take the before/after reading per `../fulcrum-verification/references/runtime-telemetry.md`; the stop rule is in `references/halt-conditions.md` |

Explicitly **not** a reason to continue: "it is nearly working", "one more turn
should do it", "the user said unattended so they don't want to be asked".
An unattended session's correct output can be a halt report.

## Never report an untouched app as healthy

**No unattended run may emit a "healthy" verdict for an app that has had no
traffic.** `appScore` is an Apdex-style **latency** score that ignores errors
entirely, and an app with no response times **scores 100** `[SCHEMA]` — a
freshly published app nobody has touched is indistinguishable from a fast,
correct one, and that is the state every unattended run is in right after a
publish. Request `requests` in `metrics` on every `app_health` call; if it reads
`0`, the only permitted verdict is **"no traffic in the window"**. Exercise the
app, then re-read. Detail: `references/halt-conditions.md`, heading "Never
report an untouched app as healthy".

## Never escalate model tier to break a bug

Repeated same-tier attempts repeat the same wrong guess; a higher tier buys a
more expensive version of it, because the missing input is evidence about the
live system, not reasoning capacity. **Before any fix attempt after the first
failure, run a diagnostic step** — read the model state back, capture the
running app, query live rows (`../fulcrum-verification/SKILL.md`). A fix turn
with no new evidence is not a new attempt; it is the same attempt again.

## Orchestrator prohibitions — categorical

The orchestrator's job is exactly four things: **read state, write a
self-contained brief, dispatch, read the terse report back.**

The orchestrator must **not itself** call `mentor_start_session`,
`mentor_create_asset`, `mentor_load_asset`, `mentor_prompt` or `mentor_get_run`;
call `mentor_publish` or `publish_status`; call a `context_*` inventory tool;
curl a REST endpoint; or run browser automation or a verification gate script.

Not to finish a small remaining piece of a step. Not to "just quickly check"
something. Not when a prior subagent left a run half-done — dispatch a subagent
to resume that same run instead. **Sole exception:** a live blocker needing the
user's own action, where a single direct attempt confirms the block is genuine;
confirm once, then report and wait. Stated categorically because the source
corpus's own reusable guide dropped the "not even to check" clause — which is
the clause that gets violated. Full rationale, brief structure and the mandatory
prompt elements: `references/delegation.md`.

## Subagent depth is ONE LEVEL

The orchestrator dispatches directly. **Subagents never spawn subagents.**
Parallel agents are siblings, never nested. **Mutating work is depth 1, always.**

**One exception, polling only.** [SINGLE-OBSERVATION] A subagent may spawn a
single nested agent that **does nothing but wait and report**, and only when its
*own* tier is expensive and the phase is long — otherwise the expensive parent
carries the whole run's poll traffic. It buys nothing when the poller tier is
cheap or a native wait primitive exists. Prefer the primitive; nest only to
isolate cost.

No other nesting: a depth dial is only as good as an agent's willingness to
respect it, which is what cannot be trusted unattended. This exception survives
that objection only because it is mechanically checkable — one permitted role,
one permitted action. It is **not** the corpus's "successor spawning with a
depth dial", which `references/delegation.md` marks **SUPERSEDED**. Read that
file before granting any agent the ability to dispatch.

## Concurrency lock — one Mentor session per app

The lock is **per app, not per tenant**: one Mentor session at a time against
any single app, with concurrent sessions across *different* apps supported.
[VERIFIED] The mechanism: Mentor handles one prompt at a time per session, and a
`mentor_prompt` issued while a prior prompt is still running does not error — it
is **silently ignored**. [VERIFIED] A racing agent gets no signal its turn was
dropped; treat it as never sent.

- **Never dispatch two agents concurrently if both may touch Mentor on the same
  app.** The lock belongs to the app, not to the agent. A `poller` watching a
  run and a `workhorse` driving the next turn are not safely concurrent unless
  the second provably cannot start a turn.
- Concurrency across apps is permitted, but the **ceiling is unpublished and can
  change server-side without notice.** [UNVERIFIED] Fan out opportunistically,
  never on a plan's critical path, and degrade to sequential on the first
  rejection rather than retrying into the limit.
- Parallel subagents must **never write the same files.** Assign each a disjoint
  file scope in its brief; shared project documents belong to the orchestrator.
- The enforceable mechanism that survives the agent is the lease:
  `../fulcrum-project-state/references/lease-and-concurrency.md`.

## Budgets are tool-call counts, never token counts

**A subagent cannot measure its own token usage.** There is no self-inspection
tool, and the orchestrator learns the count only from the completion
notification, after the agent has finished — far too late to act on. Therefore:
never write a token threshold into a prompt (the condition is unevaluable, so
the agent ignores it or hallucinates compliance), never ask an agent to report
its own token usage (it will invent a number), and convert every budget into a
**tool-call count** calibrated to the agent's work class. Reads dominate cost
more than call count does — control what gets read first.

The arithmetic, the per-class budget table, the recalibration loop and the
prevention rules: `references/budgeting.md`. How a single iteration is accounted
against them: `../fulcrum-loop-engine/references/iteration-budget.md`.

## Always handoff-ready

The agent writes durable state to a checkpoint file **continuously** — after
every unit of work that produced a durable result or a resumable identifier —
not when it thinks it is near a limit. This is primary because it needs no
number the agent cannot see, and because it is the only mechanism still correct
**when the agent dies unexpectedly**: context overflow, tool error,
cancellation, crash. A threshold-triggered handoff covers none of those, since
nothing gets to run.

Write every run id, session id, job handle and revision number to the file **at
the moment it is issued**, before doing anything with it. A handle held only in
context dies with the agent, and an ODC run whose id is lost can become
permanently unpollable. [VERIFIED]

Checkpoint contents, discipline and a worked example: `references/checkpoints.md`.
Durable project state, as distinct from an agent checkpoint:
`../fulcrum-project-state/SKILL.md`.

## Disclose, never absorb

Every subagent brief must require the agent to state, in its report: turn-budget
overruns with the actual count; any scope it cut, and why; any deviation from
the brief; and **what it could not verify**, named explicitly.

An unverifiable claim reported as unverifiable is useful. The same claim
reported as done is the input to the next failure. Honest vocabulary only:
`OK` / `PARTIAL` / `PARKED` / `untested`. Never a bare "done" or "failed".

## Reference files

| Open when | File |
|---|---|
| Sizing an agent's budget, or an agent overran | `references/budgeting.md` |
| Writing a brief, or tempted to nest a subagent | `references/delegation.md` |
| Setting up checkpoints, or resuming after a death | `references/checkpoints.md` |
| A step is failing repeatedly and you must decide whether to continue | `references/halt-conditions.md` |
| A reading from the running app looks like a stop signal, or you are about to call an app healthy | `references/halt-conditions.md`, headings "The runtime-shaped stop" and "Never report an untouched app as healthy" |
| You need to run the tasks, not decide whether to stop | `../fulcrum-loop-engine/SKILL.md` |
