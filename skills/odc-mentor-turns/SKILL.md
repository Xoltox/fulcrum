---
name: odc-mentor-turns
description: >
  How to drive ODC Mentor turn by turn so a turn lands first try and nothing
  silently reverts — turn granularity and decomposition, prompt shape and the
  length ceiling, session vs conversation, the staleness guard before any
  mutating turn, polling cadence, run-id durability, and publish sequencing.
  Use when the user says "drive Mentor to build this", "my Mentor turn
  failed", "Mentor isn't applying changes", "how should I chunk this spec for
  Mentor", "Mentor stalled", "the turn didn't land", "how often should I poll
  Mentor", "reuse the Mentor session or start fresh", or before issuing any
  `mentor_start` call.
version: "1.0.0"
requires: >
  ODC MCP server authenticated; Mentor enabled on the tenant; a durable log
  file for run identifiers; a sleep mechanism verified not to be swallowed by
  the harness.
---

# Driving Mentor, turn by turn

This skill owns turn mechanics only, not:
- what to build, or step sizing → `../odc-solution-init/SKILL.md`
- construct-specific traps (aggregates, repeaters, icons, dates...) → `../odc-engine-traps/SKILL.md`
- proving a change actually works → `../odc-verification/SKILL.md`
- stop conditions, fix-turn caps, halt rules → `../odc-unattended-guardrails/SKILL.md`

## 1. Turn granularity — the headline rule

**Mentor is not a batch processor. One coherent unit of change per turn.**

[VERIFIED] A single monolithic turn carrying 8 elements ran ~50 minutes, went
event-silent for the last ~28 minutes, was evicted from the run registry, and
lost its session token. Terminal result, validation state and refreshed token
were gone permanently — a liveness probe proved the run was still alive
shortly before eviction, so this was not a misread. Read back afterward: **zero
of the 8 elements had applied.** The same scope, rebuilt as **9 granular turns**
(786–5,057 chars each), landed all 9 — every one `change_applied: true`, 0
errors — in **25m44 total wall clock, faster than the single failed monolithic
attempt.** Decomposing the scope also surfaced a real spec defect (a foreign
key resolved from the wrong natural key) that the monolithic version would
have silently absorbed as a null foreign key on every affected row.

[VERIFIED] Separately, two other steps' full-spec single-turn attempts stalled
and were abandoned — one twice — before the same scope landed cleanly as
batched turns (8 turns in one case).

**Corollary — state this explicitly to any subagent:** a step's spec is the
*orchestrator's checklist to work through*, not the text of one prompt. Never
hand a subagent 250 lines and say "implement this spec." Tell it to decompose
into turns and list them before starting.

**Batch identical-shape work; never batch by count.** What makes a turn slow
or wrong is a new widget type or many filters mixed together, not the number
of elements. Six identical aggregates in one turn is cheap and safe; one
aggregate plus a new widget type plus a date filter is not, regardless of
"only 3 things." Split by shape, not by count.

## 2. Prompt shape and the length ceiling

This is a **platform constraint, not just economics.** [VERIFIED] A first turn
carrying full spec scaffolding at roughly 1,400 characters was rejected twice
by a web-application-firewall rule — a raw CDN 403 "Request blocked" response
before the request ever reached Mentor. A short diagnostic prompt sent on the
same session immediately after succeeded. Distinct from an auth failure (auth
stays healthy) and from a permission-classifier block (different error
string) — do not misdiagnose one as another.

Keep turn prompts to a few sentences plus a terse numbered checklist. Avoid
long runs of backticks and nested quoting in inline code — this correlates
with rejection.

**The exact character ceiling is a [TENANT] fact.** Check `tenant-profile.md`
for the Mentor prompt-length ceiling before assuming a number; do not hardcode
one here.

## 3. Prompt scaffolds

Measured-working templates (READ-then-MIRROR, the read-only stop-gate, forced
itemized proof, no-silent-substitution...) plus the phrasings that measurably
failed — in `references/prompt-scaffolds.md`. Load before authoring any
non-trivial turn prompt.

## 4. Session vs conversation, and the staleness guard

**Reuse one Mentor session across agents. Open one conversation per
step-level task**, by requesting fresh context on that step's first turn. Do
**not** open a fresh session per step — that burns a tenant session slot. One
build turn plus its fix turns within a step share a conversation.

Never treat a session-reuse deviation as precedent. Re-issue this instruction
explicitly every step — the incident below happened because a prior
one-off instruction was assumed to carry forward.

### The critical warning

Requesting fresh context does **not** guarantee a current model. [VERIFIED]
Staleness has been observed one step behind and two steps behind, with no
warning signal. Publishing from a stale model **silently reverts completed
work** while the revision number advances normally — revision-checking is
blind to this class of damage. [SINGLE-OBSERVATION, worst case] Resuming a
stale session and publishing from it reverted a live app past six completed
steps, wiping screens and entities while layering new work onto the stale
base. No automated gate caught it — a human noticed the app looked wrong.
Rollback tooling could not reach the clean state; recovery was manual through
the vendor portal.

### The guard

Every step's first turn is a **cheap, read-only invariant check** against
known prior state, phrased so a mismatch halts the run immediately — e.g. "how
many aggregates does screen `<X>` have, and does a widget named `<Y>` exist?
If the answers are not `<N>` / YES, say so and STOP."

- Use the step's **own verified ground truth** — what you actually confirmed
  the prior step produced — never a possibly-stale figure copied from a
  handoff document.
- **If it mismatches, discard the session and open a fresh one.** A
  revision-number check does not substitute for this; the revision still
  advances under a stale publish.
- In a multi-screen step, **each sibling screen gets its own independent
  check.** Never transfer a passing check from one mirrored screen to another.
- Confound to hold in mind: Mentor's own arithmetic is independently
  unreliable, so a wrong count on this check may be a read-back error rather
  than true staleness. **The safe response is the same either way: discard
  the session.**

## 5. Polling

Use the two canonical rates from `../../CONVENTIONS.md` — do not reinvent a
cadence here and ignore any different value another doc suggests:

- **45 s** for turns where Mentor *answers* (read-only inventory, invariant
  checks, "report what you see").
- **90 s** for turns where Mentor *changes the model* (every build and fix
  turn) and for **all** publish polling.
- Ignore the server's suggested-interval field.

Poll lean: request minimal detail by default, pull full detail only on a
stall or a failure. Verify your sleep mechanism once at session start, then
reuse it — a mechanism the harness silently swallows turns a poll loop into
an unbounded spin. (Harness-specific sleep quirks belong in `adapters/`, not
here.)

### Precedence over other installed polling guidance

Another skill catalog may also be installed that prescribes a different
cadence — operation tiers keyed to the *kind* of call, with a synchronous
tier and a drain-then-pause tier. **When both are present, the cadence above
governs.** Do not average them, and do not switch mid-session.

Two reasons, stated so a future reader can re-decide with the evidence rather
than guess at intent:

- Cost against wall clock is better at 45/90 across a long multi-turn build.
- Two rates split on one question an agent can always answer — *is Mentor
  answering me, or changing the model?* — are followed correctly more often
  than three tiers split on operation type, which requires classifying the
  call first. Robustness in an unattended loop beats theoretical precision.

That other catalog records per-poll telemetry, so it may hold data this rule
does not. If its cadence is ever shown to win on measured cost-to-wall-clock
for the mutating case, this rule is the one to change — update it here, in
`../../CONVENTIONS.md`, and in the sibling skills that defer to it.

## 6. Run-id durability and orphaned runs

Capture the run identifier the instant a turn starts, and **write it to a
durable log before the first sleep.** If the polling agent dies afterward, an
uncaptured identifier dies with it and the work becomes permanently
unreadable even though it may have completed.

- A "run not found" response can be spurious. Never conclude the run died,
  and never start a competing turn on that basis.
- Re-issuing a start call is safe **only if it does not report a run already
  in flight** — that absence is positive proof no competing run is alive. If
  it does report one in flight, that is positive proof the original is still
  alive; poll it, don't fight it.
- An internal-retry count above zero can appear with no visible defect —
  disclose it, do not treat it as failure.

**Token rotation footgun.** The session token attached to a run's terminal
result is **re-issued on every read of that run**, not frozen at completion.
[VERIFIED] A token relayed second-hand out of a polling agent's report was
rejected as having an invalid signature. After any poller reports a run
terminal, make one direct read of that run yourself before the next start or
publish call, and use only that freshly fetched token. Record the session
identifier and its token as one pair, refreshed together, and confirm the
token's embedded session claim matches the recorded identifier before handing
off — a mismatch is rejected outright.

## 7. Publish sequencing

Mentor has no in-turn publish capability. Publishing is a **separate call,
never a request inside a Mentor prompt.**

- Publish messages hard-cap around 500 characters. Compose to roughly 450
  from the start — don't draft long prose and trim; that has cost repeated
  wasted round-trips across multiple steps.
- Publishes serialize cluster-wide. Budget them as wall clock, not as
  something parallel agents can absorb.
- Never trust Mentor's own prose about whether a publish landed — confirm the
  revision number actually advanced.
- A mid-flight publish is a live outage. Freeze all publishing before any
  live demo.

## 8. Recovery playbook

Transport-auth expiry mid-turn, orchestrator interruptions after work already
landed, token-less resume attempts, and permission-classifier blocks on
publish, with the correct recovery for each, in `references/recovery.md`.
Read before treating any interrupted turn as a failure.

## 9. Turn economics

Nominal budget per step: **1 build turn + up to 2 fix turns.** Disclose
overages, never silently absorb them. Heavy steps have run 14 turns and
~46 minutes including publishes — a known ceiling for a legitimately large
step, not evidence something is wrong.

Granular turns that succeeded ran up to ~5–7 minutes; the only turn to exceed
that was the ~50-minute monolithic failure above. Flag any turn past **~7
minutes** as a split-further candidate — check whether it carries more than
one shape of change before letting it run longer.
