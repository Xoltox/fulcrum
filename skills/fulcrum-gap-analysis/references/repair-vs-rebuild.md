# Repair versus rebuild, and sequencing

Decide **per area**, never per app, and write the decision with its consequence stated —
the same discipline the target-platform decision gets in
`../../fulcrum-solution-init/SKILL.md`, heading "2. Target-platform decision — before
planning, not during".

## The decision

An area is anything with a coherent boundary: one entity cluster, one screen flow, one
integration. For each area with findings, choose:

**Repair** — keep what exists, add and correct. The default. Choose it when:

- The data model is right in shape, even if attributes are missing. Adding an attribute
  is cheap; re-shaping relationships is not.
- The findings are Gaps in logic over a correct schema.
- Screens exist and are structurally close to what is required.
- Provenance shows deliberate hand-built work — rebuilding discards decisions nobody
  wrote down, and those decisions are the expensive part.

**Rebuild** — discard the area's artifacts and build again from a spec. Choose it when:

- Entity relationships are wrong, not merely incomplete. A wrong cardinality propagates
  into every screen and action built on it, so repair cost grows with each dependent.
- The area is fresh generator scaffold with little depth. There is nothing to preserve,
  and a rebuild from a real spec is usually shorter than a long chain of corrections.
- Coverage in the area is near zero while artifact count is high — a shell that looks
  built and does nothing.
- Repair would take more build turns than a rebuild. Estimate both in turns, using the
  right-sizing test in `../../fulcrum-solution-init/SKILL.md`, heading "5. Phase and step
  sizing", and write the estimate down. An unstated estimate is how a rebuild gets
  chosen for aesthetic reasons.

State the consequence either way. Repair's consequence is that existing defects and
undocumented decisions survive. Rebuild's consequence is that anything undocumented in
that area is lost, so an Undocumented addition inside a rebuild area must be
**documented before the rebuild or deliberately abandoned**, and the report must say
which. This is the most common way a gap analysis destroys working behaviour.

## Sequencing rules

1. **Decisions first.** Every unfalsifiable requirement that blocks build work becomes a
   decision item ahead of the phase it blocks. Name who decides.
2. **Security findings early and separately.** A role inversion or an unauthorised write
   path is live exposure, not a coverage item. It is usually small and it should not wait
   behind a schema phase unless it technically must.
3. **Schema before logic before screens.** Correcting an attribute after screens read it
   costs a re-touch of every consumer.
4. **Seed data before any screen that reads it** — `../../fulcrum-seed-data/SKILL.md`.
5. **Every phase ends demoable.** Same rule as the initial build. Never leave the app
   mid-transformation across a session boundary.
6. **Stale requirements are document edits**, not build work. Sequence them as their own
   track so they do not inflate the build estimate — but sequence them, because an
   uncorrected document reproduces the same false gaps on the next re-run.
7. **Rebuild areas go early** when anything else depends on them, since dependents built
   against the old shape would be rebuilt twice.

## Handing off

The plan is not the work. Each item becomes:

- One or more step-sized specs on
  `../../fulcrum-solution-init/templates/spec-template.md`, each naming the requirement
  identifiers it closes so the next re-run can diff against this report.
- Turn decomposition and prompt shape from `../../fulcrum-mentor-turns/SKILL.md`.
- Proof that it landed from `../../fulcrum-verification/SKILL.md` — and pick the proof
  rungs per item now, while the evidence is fresh. A schema addition needs a different
  ladder than a role change.
- Stop conditions, fix-turn caps and delegation limits from
  `../../fulcrum-unattended-guardrails/SKILL.md` for the sessions that execute it.

This skill stops here. It does not build, and its own report is not proof that anything
was fixed.
