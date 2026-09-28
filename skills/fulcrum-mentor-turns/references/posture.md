# Posture mechanics — the consult turn, review, and decision recording

Owns **how a turn is shaped** under each posture. Posture's definition, its
orthogonality with mode, and the rationale for `collaborative` being the
default are owned by `../../../CONVENTIONS.md`, heading "Mode and posture" —
read that first. This file does not restate policy, only mechanics.

## `collaborative` (default) — three moves inside one step

1. **Consult turn.** Ask Mentor for the idiomatic ODC approach before
   instructing anything — what entities, screens and actions it would create
   for the stated outcome. Read-only: it changes nothing, so it polls at the
   answer-back cadence (`../SKILL.md`, section 5). Scaffold:
   `prompt-scaffolds.md`, heading "Consult turn".
2. **Review.** Read Mentor's proposal against
   `../../fulcrum-engine-traps/SKILL.md`. Correct **only** the specific
   trap(s) it trips.
3. **Build turn.** Carries the reviewed proposal plus the trap corrections,
   in the **same conversation** as the consult turn (below).

### The failure mechanism in the review step

An agent that finds a trap in Mentor's proposal and rewrites the whole
approach — rather than patching the one trapped element — has silently
reverted to `directive` posture while still believing it is collaborating.
The rewrite discards exactly what the consult turn was bought for: Mentor's
platform idiom. The tell: if a correction touches more of the proposal than
the named trap's own construct, it is a rewrite, not a review.

## Consult and build must share one Mentor conversation

Not a new rule — it is the session-vs-conversation discipline in
`../SKILL.md`, section 4, applied to the consult step specifically. If the
build turn opens separate context from the consult turn, Mentor no longer has
its own proposal in front of it and the build turn re-derives an approach
from scratch. The review step's trap corrections were made against a
proposal Mentor is then not building from — they are silently discarded, not
applied. Same conversation, same step, both turns.

## An accepted proposal is a decision

Record it in `.fulcrum/DECISIONS.md` with `Decider: mentor` and concrete
artifact identifiers in `Affects`. Record shape:
`../../fulcrum-project-state/templates/DECISIONS.md`. Skipping this is
exactly the drift `../../fulcrum-gap-analysis/SKILL.md` cannot explain
later — it reads a model shape nothing in the repo accounts for.

## Turn economics

Consult turns are answer-back (cheaper cadence); build turns mutate (slower
cadence) — `../SKILL.md`, section 5. `[UNVERIFIED]` The claim that one cheap
consult turn buys fewer expensive fix turns overall is a design prediction,
not a measurement: `../../../CONVENTIONS.md` tags it `[UNVERIFIED]` and no run
has been instrumented to compare posture cost end to end. Keep the tag as
written. Do not upgrade it, and do not cite the trade as a finding.

## `directive`

The consult phase is dropped. Nothing else in the iteration changes — same
granularity, staleness guard, polling, run-id, and publish rules as under
`collaborative`.
