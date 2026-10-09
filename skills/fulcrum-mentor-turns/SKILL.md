---
name: fulcrum-mentor-turns
description: >
  How to drive ODC Mentor turn by turn so a turn lands first try and nothing
  silently reverts - turn granularity, prompt shape and length ceiling,
  posture, sessions and when to start fresh, the staleness guard, polling
  cadence and draining, run-id durability, the Publish turn, and the dated
  record of the live MCP surface. Use when the user says "drive Mentor to
  build this", "my Mentor turn failed", "Mentor isn't applying changes", "how
  should I chunk this spec", "Mentor stalled", "how often should I poll
  Mentor", "reuse the session or start fresh", "how do I publish", "did the
  MCP tools change", or before any `mentor_start_session` /
  `mentor_create_asset` / `mentor_load_asset` / `mentor_prompt` call.
version: "1.1.0"
requires: >
  ODC MCP server authenticated; Mentor enabled on the tenant; a durable log
  file for run identifiers; a wait capability that suspends without spinning
  or accumulating context; a subagent dispatch capability where available.
---

# Driving Mentor, turn by turn

This skill owns turn mechanics only, not: what to build or step sizing
(`../fulcrum-solution-init/SKILL.md`); construct-specific traps
(`../fulcrum-engine-traps/SKILL.md`); proving a change works
(`../fulcrum-verification/SKILL.md`); stop/halt rules
(`../fulcrum-unattended-guardrails/SKILL.md`).

**Tool facts live in one file:** parameters, response fields, event names,
error texts and their evidence dates are in `references/mcp-surface.md`. This
file states rules; that file states what the server does. If the live
surface disagrees with it, re-probe (its heading "Re-probing the surface").

**Delegation is the default.** The orchestrator reads state, briefs and
dispatches; subagents drive turns and absorb poll traffic. Poll undelegated
only when the harness gives no subagent, at the slower cadence below.

**The sequence.** `mentor_start_session` -> `mentor_create_asset` for a new
asset **or** `mentor_load_asset` for an existing one -> `mentor_prompt` ->
read `mentor_get_run` until drained. No mutation is possible before create
or load `[SCHEMA]`; decide the branch before the first prompt. Create needs
a `portfolioKey` in practice (from `env_list`; record it in
`tenant-profile.md`). A created asset exists only inside its session until
its first publish - **publish once early**, before that session can close
(section 7). A load can be refused under capacity; the bounded retry rule is
in `references/mcp-surface.md`, heading "Creating and loading an asset".

## 1. Turn granularity - the headline rule

**Mentor is not a batch processor. One coherent unit of change per turn.**
[VERIFIED] A monolithic 8-element turn ran ~50 minutes, went event-silent and
lost its run - **zero of the 8 had applied** on read-back. The same scope as
**9 granular turns landed all 9**, faster overall, and surfaced a real spec
defect the monolithic version would have absorbed. Numbers:
`references/granularity.md`.

**Corollary:** a step's spec is the *orchestrator's checklist*, not one
prompt's text. Tell a subagent to decompose into turns and list them first.
**Batch identical-shape work; never batch by count** - six identical
aggregates in one turn is safe; one aggregate plus a new widget type plus a
date filter is not.

## 2. Prompt shape, the length ceiling, and secrets

[VERIFIED] A ~1,400-character first turn was rejected twice by a
web-application-firewall rule (a raw CDN 403 - not auth, not a permission
classifier); a short prompt on the same session then succeeded. Keep prompts
to a few sentences plus a terse numbered checklist; avoid long runs of
backticks and nested quoting. **The ceiling is a [TENANT] fact** -
check `tenant-profile.md`.

**Never put a secret value in a Mentor prompt** - a prompt is stored and
replayed, so the value can leak into the model, history and logs (leak path
`[UNVERIFIED]`; the rule costs nothing). Brief a secret Setting with an
**empty default**; the user sets the value in the ODC Portal - a user-action
stop, not a halt.
`../fulcrum-engine-traps/references/access-security-and-settings.md`, entry 2.

## 3. Prompt scaffolds

Measured-working templates, phrasings that measurably failed, and quoting
untrusted `app_logs` text: `references/prompt-scaffolds.md`. Load before
authoring any non-trivial turn.

## 3a. Posture - `collaborative` vs `directive`

Defined in `../../CONVENTIONS.md`, heading "Mode and posture". `collaborative`
(default): a read-only **consult turn**, a **review** against
`../fulcrum-engine-traps/SKILL.md` correcting only the trap(s) tripped -
never a rewrite of the whole proposal - then the **build turn** in the same
session (section 4). `directive` drops the consult. An accepted Mentor
proposal is a decision (`Decider: mentor`). Economics stay `[UNVERIFIED]`.
Mechanics: `references/posture.md`.

## 4. Sessions, conversation and the staleness guard

**A session is one conversation.** There is no session token and no
fresh-context switch; runs in a session share Mentor's memory. Fresh context
means close the session, start a new one, load again (`references/mcp-surface.md`,
heading "Sessions and context").

- **Within a step, one session** - consult, build and fix turns share it, or
  the review's corrections are silently discarded.
- **Across consecutive steps, reuse by default** if the step's first turn
  passes the guard below. Reuse carries Mentor's context but also its stale
  beliefs; each fresh session is another load exposed to capacity
  throttling. When to start fresh: `references/sessions.md`.
- **One session per app at a time**; always close a finished session.

**Mentor's read-back is evidence of Mentor's belief, not of the model.** When
it contradicts published-state inspection or wire evidence, trust the
instrument and journal the contradiction (`references/sessions.md`).

### The critical warning

A session's model is **not guaranteed current.** [VERIFIED] Staleness has
been seen one and two steps behind, unsignalled. Publishing from it
**silently reverts completed work** while the revision still advances
[SINGLE-OBSERVATION, worst case: six steps lost]. `references/recovery.md`.

### The guard

Every step's first turn is a **cheap, read-only invariant check** against
the step's **own verified ground truth** (never a figure copied from a
handoff), phrased so a mismatch halts - e.g. "how many aggregates does
screen `<X>` have, and does a widget named `<Y>` exist? If not `<N>` / YES,
say so and STOP."

- **On mismatch, `mentor_close_session`, then start fresh.** A
  revision-number check does not substitute.
- Each sibling screen gets its **own** check. A wrong count may be a
  read-back error rather than staleness - **the response is the same.**

## 5. Polling

**Every poll is a request *and* a response, and both persist in the context
of whoever issued them.** Token cost, not wall clock, is what the cadence
optimises. **With a discardable poller:** **45 s** for turns where Mentor
*answers*; **90 s** for turns that *change the model*, including the Publish
turn. **With no delegation:** the orchestrator polls in its own context at a
**90 s floor for everything** - never carry 45 s into an undelegated loop.

- The server's `pollIntervalMs` is a hint Fulcrum deliberately overrides
  upward; it never shortens a wait.
- **Drain:** while `hasMore` is true, page again immediately. A run is read
  only when `hasMore` is false and `nextCursor` absent - `succeeded` can
  arrive before that. A poller reports only after the last page and **never
  paraphrases a page it did not read.**
- **Verify the wait blocks** before the first poll - a wait that returns
  immediately hammers Mentor with no cadence (`../../HARNESS-NOTES.md`).
- **A brief must restate these rules.** Pointing an agent at this skill is
  not enough. Paste the block in `references/polling.md`, heading "Pointing
  at this skill is not a brief".
- **Precedence:** if another catalog prescribes different cadences, this one
  governs; do not average or switch mid-session (`references/polling.md`).

## 6. Run-id durability and orphaned runs

Capture the `runId` the instant a turn starts and **write it to a durable
log before the first wait** - an uncaptured id dies with a crashed poller
though the work may have completed. Log a publication key the moment it
appears. A "run not found" can be spurious: never start a competing turn on
it. Disclose a nonzero internal-retry count; it is not a failure.

**After a poller reports terminal, the driver makes one fresh direct read
of `mentor_get_run` itself** before the next prompt or publish, and bases
its verdict on that read.

## 7. Publish sequencing

**Publish is its own planned turn:** a `mentor_prompt` whose message is
"Publish", polled at the mutating cadence, sent only at the step the plan
names. `mentor_publish` is deprecated. Events, keys and status fields:
`references/mcp-surface.md`, heading "Publishing".

- **Mentor's offers to publish are never accepted inline.** An unattended
  "yes" publishes outside the plan.
- **Before sending "Publish", read the revision** (`app_revisions` or
  `env_app`). If it moved since the last recorded publish, a change turn
  published on its own - record it, do not publish again.
- The `runId` is not the publication key: take the key from the
  `publishAccepted` event, confirm with `publish_status` (gate on
  `outcome`), then `env_app` for revision and URL.
- **Never publish while the previous publish is non-terminal.** A failure
  with an `OS-*` build code is the build's result: surface it.
  `indeterminate: true` means re-poll or check the deployed inventory.
  Neither is a reason to re-publish.
- Never trust Mentor's prose about a publish - confirm the revision, then
  prove the change per `../fulcrum-verification/SKILL.md`; `context_*`
  lags a publish by about 2 minutes.
- Publishes serialize; freeze them before a demo; Production needs explicit
  user confirmation (`references/granularity.md`, "Publish budgeting").

## 8. Recovery and turn economics

Auth expiry, lost sessions, the capacity throttle, failed publishes, abandoned
prompts: `references/recovery.md` - read before treating an interrupted turn as
failed. Budget per step: 1 build turn + up to 2 fix turns, plus the Publish turn;
disclose overages (`references/granularity.md`, "Turn economics").
