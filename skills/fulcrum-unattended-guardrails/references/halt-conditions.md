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

## The escalation ladder — in order, no skipping

1. **Build turn.** Fails.
2. **Diagnostic step.** Mandatory. Not a fix — an observation.
3. **Fix turn 1**, informed by what the diagnostic actually showed.
4. If it fails: **a second diagnostic**, then **fix turn 2**.
5. Still failing → **stuck twice → halt and report to the user.**

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
| Stuck twice after a diagnostic step | The escalation ladder is exhausted |
| Turn cap exceeded on one step | 1 build + 2 fix |
| A mutating turn about to run and the **staleness guard did not pass** | See "the revert failure mode" below |
| A previously verified behaviour now fails | Regression. Continuing builds on a corrupted state |
| A step needs the **user's own action** | Re-auth, a portal-only operation, an upload with no MCP path. Retrying does not create a capability |
| A permission or policy denial | Confirm with **one** direct retry, then stop. Never iterate looking for a way around it |
| The fix would weaken validation, auth, or a business rule | Park, disclose, stop. Phrase every "do not touch X" as *"do not touch X unless X is the root cause — if so, fix it and disclose prominently"* |
| Two candidate actions would both touch Mentor concurrently | Serialise, or stop and ask |
| The plan for the current step does not exist in writing | Deriving a plan mid-unattended-run is the highest-risk act available |

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
