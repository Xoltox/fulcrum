# Classifying a finding

Five classes. Every finding gets exactly one. Only **Gap** is a defect by default.

Four classes come from `../../../CONVENTIONS.md`, heading "Gap analysis never assumes how
the app got there". **Unfalsifiable requirement** is this skill's addition.

## Decision order — run it top to bottom, stop at the first yes

Running it in this order is what stops everything becoming a Gap. A pass that checks
"is it absent?" first will file drift, staleness and vagueness all as gaps.

1. **Is the requirement assessable as written?** If no testable behaviour can be derived
   from it — deferred specifics, "as appropriate", "to be detailed further with IT",
   quantities left unstated — it is an **Unfalsifiable requirement**. Stop. Do not look
   at the app for it at all; looking invites inventing a gap.
2. **Does the requirements document still describe intended behaviour here?** If the
   document is contradicted by a later decision record, a newer document revision, or
   an explicit stakeholder statement, it is a **Stale requirement**. Stop. The document
   is what needs changing.
3. **Does the app do something in this area at all?** If nothing exists — no entity, no
   attribute, no screen, no action, no role assignment — it is a **Gap**.
4. **It exists but differs.** It is **Drift**. Before calling any Drift a defect, sweep
   for a decision record (see `provenance.md`). Found one → Drift, deliberate, not a
   defect. None found → **Drift — undetermined**, and say that the absence of a record
   is not evidence of a mistake.
5. **Separately, sweep the inventory for artifacts no requirement claims.** Each is an
   **Undocumented addition**. Judge each as valuable, neutral, or scope creep, with a
   reason. Never silently a defect; never silently deleted from the plan either.

## What each class must carry

| Class | Required in the finding |
|---|---|
| Gap | The requirement identifier; the named artifacts checked and found absent; which inventory operation established the absence; whether the area's provenance makes the absence expected |
| Drift | What the document specifies; what the app actually does, by artifact name; the decision-record sweep result; a recommendation of which side should move |
| Stale requirement | The document location; the evidence it is superseded, quoted; the document edit needed |
| Undocumented addition | The artifacts, by name; a guess at its purpose; valuable / neutral / scope creep, with a reason; whether it should be documented or removed |
| Unfalsifiable requirement | The wording, quoted; **what would have to be decided** before the requirement can be assessed at all; who decides it |

## Unfalsifiable requirements in detail

A requirement is unfalsifiable when two competent reviewers with the same app could
reasonably disagree on whether it is satisfied, and no evidence in the project settles it.

Common shapes:

- Deferred specifics — wording equivalent to "to be detailed further with IT".
  `[SINGLE-OBSERVATION]` This exact deferral appeared in a real BRD.
- Unquantified qualities — "fast", "user-friendly", "scalable", with no threshold.
- A named actor with no named behaviour — "the manager will oversee approvals" without
  saying what the manager can see or do.
- Compound requirements whose clauses conflict, so satisfying one breaks the other.

Handling:

- Never score the app against one. It is a finding about the **document**.
- Exclude it from every coverage denominator and report the count separately. A report
  that silently drops them overstates coverage; one that counts them as gaps understates
  it. Both are wrong; naming them is the only correct move.
- The remediation for it is a **decision**, not a build step, and it usually blocks
  build steps. Say what it blocks — that is what makes it actionable.

## Anti-patterns

- **Everything is a Gap.** The default failure. If a report on a mature app has no
  Stale requirements and no Undocumented additions, the classification pass did not run
  — those classes are the normal output of time passing.
- **Drift laundered into Gap** because a decision record was not looked for. The sweep
  is mandatory, and its result is reported even when it found nothing.
- **Partial credit as a class.** "Partially met" is not a class. Split the requirement
  into named sub-requirements and classify each — that is exactly what makes the
  coverage figure recomputable (see `coverage-and-diagrams.md`).
- **Schema presence read as capability.** An attribute existing is not the requirement
  being met when the requirement is a behaviour. File the behaviour as its own
  sub-requirement so "schema present, logic absent" is visible rather than averaged.
- **Security findings folded into coverage.** Keep them separate and prominent.
- **Classifying from the document alone.** Every class except Stale requirement and
  Unfalsifiable requirement needs inventory evidence naming artifacts.
