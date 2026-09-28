# Halt conditions, fix-turn caps, escalation

## The turn cap

**Per step: 1 build turn + at most 2 fix turns.** [VERIFIED]

Mentor is not a batch processor — one objective per turn (see
`../../fulcrum-mentor-turns/SKILL.md`). Past three turns on one step, the pattern
observed is not convergence: it is Mentor guessing, and each guess mutates the
model. The cap exists because the cost of an extra turn is not a wasted turn, it
is an unreviewed change to a live application.

On exceeding the cap: write the checkpoint, park the step with an honest status,
report. Do not carry the overrun silently into the next step.

## The escalation ceiling

This file owns the **ceiling and the terminal condition**. Running the attempts
— issuing the turns, re-verifying, recording each one — is the loop's:
`../../fulcrum-loop-engine/references/oscillation-and-fix-loop.md`, heading
"The fix-loop". Do not iterate from this file.

Three rules bound every escalation, in force whoever is running it:

- **A diagnostic step is mandatory before every fix attempt after the first
  failure.** Not a fix — an observation.
- **At most two fix attempts** after the build turn. That is the turn cap above.
- **Still failing after the second → stuck twice → halt and report to the
  user.** Detected mechanically, by scanning the session index rather than by an
  agent remembering: `../../fulcrum-loop-engine/SKILL.md`, heading "Oscillation
  detection — mechanical, not remembered". **The loop detects; this file
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
still ends at the same halt.

Tier policy is phase-based and is set at dispatch time, not adjusted reactively:
`../../../MODEL-TIERS.md`.

## Hard stops

Write the checkpoint, then stop and report. Do not work around any of these.

| Trigger | Detail |
|---|---|
| Stuck twice after a diagnostic step | The escalation ceiling is exhausted. Two `:fail` entries for one task id in the session index is this firing mechanically |
| Turn cap exceeded on one step | 1 build + 2 fix |
| A mutating turn about to run and the **staleness guard did not pass** | See "the revert failure mode" below |
| A previously verified behaviour now fails | Regression. Continuing builds on a corrupted state |
| A step needs the **user's own action** | Re-auth, a portal-only operation, an upload with no MCP path. Retrying does not create a capability |
| A permission or policy denial | Confirm with **one** direct retry, then stop. Never iterate looking for a way around it |
| The fix would weaken validation, auth, or a business rule | Park, disclose, stop. Phrase every "do not touch X" as *"do not touch X unless X is the root cause — if so, fix it and disclose prominently"* |
| Two candidate actions would both touch Mentor concurrently | Serialise, or stop and ask |
| A step depends on an op **confirmed unavailable** with **no fallback** recorded in `tenant-profile.md` | See "Halt on an unavailable op with no fallback" below |
| The plan for the current step does not exist in writing | Deriving a plan mid-unattended-run is the highest-risk act available |
| **Runtime error step-change across a build step** | `app_health` `errors` / `errorPercent` higher in the after window than the before window, or `lastErrorOccurred` falling inside the after window. See below |

## The runtime-shaped stop

Every other stop above is model- or turn-shaped: it fires on what the platform
said about a turn. This one fires on what the deployed app actually did, and it
is the only stop here that can catch a change that published cleanly, verified
against the model, and then broke the running app.

**The rule.** Take an `app_health` reading bracketing the step. If, across that
step, `errors` or `errorPercent` steps up, or `lastErrorOccurred` falls inside
the after window, **halt and report.** `[SCHEMA]` — those fields and their
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
heading "Tool availability — three states, not two") and no fallback is
recorded for it (`../../fulcrum-solution-init/references/tool-availability-and-fallback.md`),
**halt and report. Do not improvise a workaround.**

**The mechanism.** An unattended agent that works around a missing capability
invents an unreviewed approach on the spot and records it nowhere durable. The
deviation does not surface at the moment it happens — it surfaces later as
unexplainable drift: a screen built a different way than the plan describes, a
data path that does not match the spec, with no decision record explaining
why. A halt costs one interruption. A silent improvisation costs a future
session trying to reconcile behaviour against a plan that never mentioned it.

This is distinct from the ordinary fix-loop: a fix turn retries the *same* op
after gathering evidence. This halt fires when the op itself has no working
path at all — there is nothing to retry.

Do not confuse **unavailable** with **unknown**. An op that is merely unknown
(never dispatched — the default and correct state for every mutating op) is
not a halt condition by itself; dispatch it as the plan calls for and record
the outcome. This rule fires only once dispatch has actually failed with a
resolution error and no fallback exists.

## Never report an untouched app as healthy

**An unattended run must never emit a "healthy" verdict for an app that has had
no traffic.** This is the most dangerous false green available to an unattended
session, because it is the app's default state immediately after every publish.

**The mechanism.** `appScore` is an Apdex-style **latency** score computed from
response times. It ignores errors entirely. An app with no traffic has no
response times, and no response times **scores 100** `[SCHEMA]` — identical to a
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
- Never synthesise availability or uptime — the platform exposes neither
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

## The revert failure mode — why halting early is cheap

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

- A **staleness guard before every mutating turn** — verify the session's view
  of current state against an independent read of the live revision, never
  against the session's own read-back
  (`../../fulcrum-mentor-turns/SKILL.md`).
- A **checkpoint that survives the agent**, recording the revision observed
  before changes (`checkpoints.md`).
- A **halt rule that fires early**, because an hour of lost time is
  recoverable and six steps of lost work is not.

## Honest reporting on halt

The halt report states, in order:

1. **Status** — `PARTIAL` or `PARKED`. Never a bare "failed".
2. **The last verified-good state** — the revision, with the evidence that
   verified it.
3. **What was attempted**, including each diagnostic and what it showed.
4. **What could not be verified**, named explicitly.
5. **The specific decision or action the user needs to make.** A halt report
   without an ask is an interruption, not an escalation.
6. **The checkpoint path.**
