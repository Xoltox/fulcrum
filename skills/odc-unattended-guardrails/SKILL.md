---
name: odc-unattended-guardrails
description: >
  Safety rails for long, largely unattended ODC Mentor build sessions — stop
  conditions, fix-turn caps, halt-and-report rules, subagent depth and
  delegation boundaries, tool-call budgeting, checkpoint discipline, Mentor
  concurrency locks and model tier policy. Use when the user says "run the
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

- ODC construct behaviour → `../odc-engine-traps/SKILL.md`
- Turn granularity, prompt shape, polling cadence → `../odc-mentor-turns/SKILL.md`
- Proof obligations and instruments → `../odc-verification/SKILL.md`
- Plan, phases, handoff document structure → `../odc-solution-init/SKILL.md`

## The premise

Unattended does not mean autonomous. It means: **the agent is trusted to stop
safely, not trusted to recover from anything.** Every rule below exists so that
the worst outcome of an unwatched hour is lost time, never lost work.

The failure mode this discipline is built against [VERIFIED]: an agent resumed
a **stale Mentor session** and published from it. The publish silently reverted
the live app past six completed steps of work, while the revision number
advanced normally — so every platform success signal was green. No automated
gate caught it; a human noticed the app looked wrong. Rollback tooling could not
reach the last clean state, and recovery was manual through the vendor portal.

Read the consequences: platform success signals cannot detect this class of
damage, an unattended run can therefore destroy verified work without emitting
a single error, and the only defences are a staleness guard before every
mutating turn, a checkpoint that survives the agent, and a halt rule that fires
early.

## Session-start checklist

Before the first dispatch:

1. **Confirm the plan exists and is written down.** Unattended execution of an
   underived plan is the highest-risk thing in this skill set. If the plan is
   not on disk, stop — that is init work, not build work.
2. **Set the model tier explicitly** per `../../MODEL-TIERS.md`. Do not rely on
   inheritance.
3. **Verify the wait mechanism once.** Establish a sleep primitive your harness
   will not swallow inside a subagent, and reuse it for the whole session. A
   silently-failing sleep turns a poll loop into an unbounded spin.
4. **Record the current app revision.** It is the baseline every later "did this
   land / did this revert" question is answered against.
5. **Name the checkpoint path** and the handoff path. Agents do not invent them.
6. **State the step budget for the session** — how many steps, and the halt rule.

## Hard stops — halt and report to the user

Do not work around any of these. Write the checkpoint, then stop and report.

| Trigger | Why it is a hard stop |
|---|---|
| **Stuck twice** on the same defect after a diagnostic step | Two failures at the same tier means the model of the problem is wrong, not the attempt count |
| **Fix-turn cap exceeded** — more than 1 build + 2 fix turns for one step | Beyond that, Mentor is being asked to guess; each turn mutates the model |
| A mutating turn is about to run against a session whose **staleness guard did not pass** | This is the revert failure mode above |
| The live app **regressed** — something previously verified now fails | Continuing builds on top of a corrupted state |
| A step needs **the user's own action** — re-auth, a portal-only operation, an asset upload with no MCP path | No amount of retrying creates a capability |
| A **permission or policy denial** | Confirm it is genuine with one direct retry, then stop. Never iterate looking for a way around it |
| The change required would **weaken validation, auth, or a business rule** to clear an error | Park it, disclose it, stop |
| Two candidate actions would both **touch Mentor concurrently** | See the concurrency lock below |

Explicitly **not** a reason to continue: "it is nearly working", "one more turn
should do it", "the user said unattended so they don't want to be asked".
An unattended session's correct output can be a halt report.

## Never escalate model tier to break a bug

Repeated same-tier attempts repeat the same wrong guess; a higher tier mostly
buys a more expensive version of the same guess. **Before any further fix
attempt after the first failure, run a diagnostic step** — read the actual model
state back, capture the running app, query live rows through the diagnostic
endpoint pattern in `../odc-verification/SKILL.md`. A fix turn with no new
evidence behind it does not count as a new attempt; it is the same attempt again.

## Orchestrator prohibitions — categorical

The orchestrator's job is exactly four things: **read state, write a
self-contained brief, dispatch, read the terse report back.**

The orchestrator must **not itself**:

- call `mentor_start` or `mentor_get_run`
- call `publish_start` or `publish_status`
- call a `context_*` inventory tool
- curl a REST endpoint
- run browser automation or a verification gate script

Not to finish a small remaining piece of a step. Not to "just quickly check"
something. Not when a prior subagent left a run half-done — dispatch a subagent
to resume that same run instead. **Sole exception:** a live blocker needing the
user's own action, where a single direct attempt confirms the block is genuine;
confirm once, then report and wait.

This is stated categorically because the source corpus's own reusable guide
transcribed only half of it, and the half it dropped was the "not even to check"
clause — which is the clause that gets violated.

Full rationale, brief structure, and the mandatory prompt elements:
`references/delegation.md`.

## Subagent depth is ONE LEVEL

The orchestrator dispatches directly. **Subagents never spawn subagents.**
Parallel agents are siblings under the orchestrator, never nested.

`references/delegation.md` marks the "successor spawning" pattern found in the
source corpus **SUPERSEDED**, and states what to do instead. Read it before
granting any agent the ability to dispatch — it is the one thing in the corpus
that a future agent could cite to grant itself nesting.

## Concurrency lock — one Mentor session per app

The lock is **per app, not per tenant**: one Mentor session at a time against
any single app. [VERIFIED] Concurrent sessions across *different* apps in the
same tenant are supported.

- **Never dispatch two agents concurrently if both may touch Mentor on the same
  app.** Not "they probably won't collide" — the lock belongs to the app, not to
  the agent.
- Concurrency across apps is permitted, but the **ceiling is unpublished and can
  change server-side without notice.** [UNVERIFIED] Treat parallel-app fan-out
  as best-effort: never put N simultaneous sessions on a plan's critical path,
  and degrade to sequential on the first rejection rather than retrying into the
  limit.
- A `poller`-tier agent watching a run and a `workhorse` agent driving the next
  turn on the same app are *not* safely concurrent unless the second cannot
  start a turn.
- Parallel subagents must also **never write the same files**. Assign each a
  disjoint file scope in its brief. Shared project documents belong to the
  orchestrator; build agents report what should go in them.

## Budgets are tool-call counts, never token counts

**A subagent cannot measure its own token usage.** There is no self-inspection
tool, and the orchestrator learns the count only from the completion
notification — after the agent has already finished, far too late to act on.

Therefore:

- **Never** write "stop when you reach 150k tokens" into a prompt. The condition
  is unevaluable; the agent will ignore it or hallucinate compliance.
- **Never** ask an agent to report its own token usage. It will invent a number.
- Convert every budget into a **tool-call count**, which an agent can actually
  track, calibrated to the agent's work class.
- Reads dominate cost more than call count does — control what gets read first.

The arithmetic, the per-class budget table, the recalibration loop and the
prevention rules: `references/budgeting.md`.

## Always handoff-ready

The agent writes durable state to a checkpoint file **continuously** — after
every unit of work that produced a durable result or a resumable identifier —
not when it thinks it is near a limit.

This is the primary mechanism because it needs no number the agent cannot see,
and because it is the only one that is still correct **when the agent dies
unexpectedly**: context overflow, tool error, cancellation, crash. A
threshold-triggered handoff covers none of those, since nothing gets to run.

Write every run id, session id, job handle and revision number to the file **at
the moment it is issued**, before doing anything with it. A handle held only in
context dies with the agent, and an ODC run whose id is lost can become
permanently unpollable. [VERIFIED]

Checkpoint contents, discipline, and a worked example: `references/checkpoints.md`.

## Disclose, never absorb

Every subagent brief must require the agent to state, in its report:

- Turn-budget overruns, with the actual count.
- Any scope it cut, and why.
- Any deviation from the brief.
- **What it could not verify** — named explicitly, not omitted.

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
