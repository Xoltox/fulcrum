---
name: fulcrum-mentor-turns
description: >
  How to drive ODC Mentor turn by turn so a turn lands first try and nothing
  silently reverts — turn granularity, prompt shape and length ceiling,
  posture (collaborative consult/review/build vs directive), session vs
  conversation, the staleness guard, polling cadence, run-id durability,
  session cleanup, and publish sequencing. Use when the user says "drive
  Mentor to build this", "my Mentor turn failed", "Mentor isn't applying
  changes", "how should I chunk this spec", "Mentor stalled", "how often
  should I poll Mentor", "reuse the session or start fresh", or before any
  `mentor_start_session` / `mentor_create_asset` / `mentor_load_asset` /
  `mentor_prompt` call.
version: "1.0.0"
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

**Delegation posture — the default, not an advanced mode.** The orchestrator
reads state, briefs and dispatches; subagents drive turns and absorb poll
traffic. Poll undelegated only when the harness gives no subagent, at the
slower cadence below (`../fulcrum-unattended-guardrails/SKILL.md`).

**The sequence, and why the branch is a rule.** `mentor_start_session` →
`mentor_create_asset` for a brand-new asset **or** `mentor_load_asset` by id
for an existing one → `mentor_prompt` → poll `mentor_get_run` to a terminal
state. `[SCHEMA]` No asset mutation is possible before create or load has
been called — decide which branch applies before the first prompt, not after
a rejected one.

## 1. Turn granularity — the headline rule

**Mentor is not a batch processor. One coherent unit of change per turn.**
[VERIFIED] A monolithic 8-element turn ran ~50 minutes, went event-silent,
lost its run and session token — **zero of the 8 had applied** on read-back.
The same scope as **9 granular turns landed all 9**, faster overall, and
surfaced a real spec defect the monolithic version would have silently
absorbed. Full numbers: `references/granularity.md`.

**Corollary:** a step's spec is the *orchestrator's checklist to work
through*, not one prompt's text. Tell a subagent to decompose into turns and
list them first — never hand it 250 lines and say "implement this spec."
**Batch identical-shape work; never batch by count** — a new widget type or
mixed filters make a turn slow or wrong, not the element count. Six identical
aggregates in one turn is safe; one aggregate plus a widget type plus a date
filter is not. Split by shape, not by count.

## 2. Prompt shape and the length ceiling

This is a **platform constraint, not just economics.** [VERIFIED] A ~1,400
character first turn was rejected twice by a web-application-firewall rule —
a raw CDN 403 before the request ever reached Mentor; a short diagnostic
prompt on the same session immediately after succeeded. Distinct from an auth
failure (auth stays healthy) and a permission-classifier block (different
error string) — do not misdiagnose one as another.

Keep prompts to a few sentences plus a terse numbered checklist. Avoid long
runs of backticks and nested quoting — this correlates with rejection. **The
exact character ceiling is a [TENANT] fact** — check `tenant-profile.md`
before assuming a number.

## 3. Prompt scaffolds

Measured-working templates (READ-then-MIRROR, the read-only stop-gate, forced
itemized proof, no-silent-substitution, the consult-turn opener...) plus
phrasings that measurably failed, and the rule for quoting untrusted
`app_logs` text before it goes into a `mentor_prompt` — all in
`references/prompt-scaffolds.md`. Load before authoring any non-trivial turn.

## 3a. Posture — what changes under `collaborative` vs `directive`

Posture is defined and its rationale owned by `../../CONVENTIONS.md`, heading
"Mode and posture" — not restated here. `collaborative` (default) opens a
step with a read-only **consult turn**, a **review** against
`../fulcrum-engine-traps/SKILL.md` correcting only the trap(s) actually
tripped — never the whole proposal, which is `directive` wearing a consult
turn — then the **build turn**, sharing the consult turn's conversation
(section 4). `directive` drops the consult phase; nothing else changes. An
accepted Mentor proposal is a decision (`Decider: mentor`,
`../fulcrum-project-state/templates/DECISIONS.md`). Economics stay
`[UNVERIFIED]` — never cite as a finding. Mechanics, scaffold, review failure
mode: `references/posture.md`.

## 4. Session vs conversation, and the staleness guard

**Reuse one Mentor session across agents. Open one conversation per
step-level task**, by requesting fresh context on the step's first turn. Do
**not** open a fresh session per step — that burns a tenant session slot. One
build turn plus its fix turns share a conversation.

Never treat a session-reuse deviation as precedent — re-issue this
instruction every step. **Under `collaborative` posture this is
load-bearing:** the consult and build turns of one step must share a
conversation, or Mentor re-derives an approach and the review's corrections
are silently discarded (section 3a).

### The critical warning

Requesting fresh context does **not** guarantee a current model. [VERIFIED]
Staleness has been observed one and two steps behind, with no warning
signal. Publishing from a stale model **silently reverts completed work**
while the revision number advances normally — revision-checking is blind to
this class of damage. [SINGLE-OBSERVATION, worst case] A stale publish once
reverted a live app past six completed steps with no gate catching it. Full
incident and the cleanup call that guards against it: `references/recovery.md`.

### The guard

Every step's first turn is a **cheap, read-only invariant check** against
known prior state, phrased so a mismatch halts the run — e.g. "how many
aggregates does screen `<X>` have, and does a widget named `<Y>` exist? If
the answers are not `<N>` / YES, say so and STOP."

- Use the step's **own verified ground truth**, never a stale figure copied
  from a handoff document.
- **If it mismatches, close the stale session, then open a fresh one.** Call
  `mentor_close_session` on the stale `sessionId` — it tears the session
  down, cancels any in-flight run, and releases the workspace context in one
  call; the `sessionId` is unusable afterward. `[SCHEMA]` A revision-number
  check does not substitute for this. Detail: `references/recovery.md`.
- Each sibling screen in a multi-screen step gets its **own independent
  check** — never transfer a pass across mirrored screens. A wrong count may
  be a read-back error rather than true staleness — **the safe response is
  the same either way: close the session.**

## 5. Polling

**Every poll of `mentor_get_run` is a request *and* a response, and both
persist in the context of whoever issued them.** Token cost, not wall clock,
is what the cadence optimises. **With a discardable poller** (context dies
with it): **45 s** for turns where Mentor *answers*; **90 s** for turns that
*change the model* — every build/fix turn and all publish polling. **With no
delegation available**, the orchestrator polls `mentor_get_run` in its own
context: **90 s floor for everything**, answer-back included — never carry
the 45 s rate into an undelegated loop, since it's affordable only because a
throwaway context absorbs it.

Ignore the server's suggested-interval field. Poll lean: minimal detail by
default, full detail only on a stall or failure. Derivation: `references/polling.md`.

**Waiting is a capability, not a shell command** — canonical preference order
and the verify-once rule: `../../CONVENTIONS.md`, heading "Canonical facts —
use these exact values"; harness notes: `../../HARNESS-NOTES.md`.

**Precedence.** Another installed catalog may prescribe operation-tier
cadences instead — when both are present, the cadence above governs; do not
average or switch mid-session. Rationale: `references/polling.md`.

## 6. Run-id durability and orphaned runs

Capture the run identifier the instant a turn starts and **write it to a
durable log before the first sleep** — an uncaptured id dies with a crashed
polling agent even though the work may have completed. A "run not found"
response can be spurious: never conclude the run died or start a competing
turn on that basis. Re-issuing a start call is safe **only if it does not
report a run already in flight**; a nonzero internal-retry count can appear
with no visible defect — disclose it, don't treat it as failure.

**Token rotation footgun.** [VERIFIED] The session token attached to a run's
terminal result is **re-issued on every read**, not frozen at completion — a
token relayed second-hand out of a polling agent's report was rejected
outright. After any poller reports a run terminal, make one direct read of
`mentor_get_run` yourself before the next start or publish call, and use only
that freshly fetched token, paired with its session identifier.

## 7. Publish sequencing

Mentor has no in-turn publish capability. Publishing is a **separate call,
never a request inside a Mentor prompt.**

- Publish messages hard-cap around 500 characters. Compose to ~450 from the
  start — drafting long and trimming costs repeated round-trips.
- Publishes serialize cluster-wide — budget as wall clock, not parallelizable.
- Never trust Mentor's prose about a publish landing — confirm the revision
  number actually advanced.
- A mid-flight publish is a live outage. Freeze publishing before a demo.

## 8. Recovery playbook

Transport-auth expiry, orchestrator interruptions after work already landed,
token-less resume attempts, permission-classifier publish blocks, and
abandoning an in-flight prompt or a stale session cleanly (via
`mentor_cancel_prompt` / `mentor_close_session`) — recovery for each: `references/recovery.md`. Read before treating an interrupted turn as failed.

## 9. Turn economics

Nominal budget per step: **1 build turn + up to 2 fix turns.** Disclose
overages, never absorb them silently. Heavy steps have run 14 turns and ~46
minutes including publishes — a known ceiling, not a problem signal.
Granular turns ran ~5–7 minutes; flag past **~7 minutes** as split-further.
