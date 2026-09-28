# Template — `.fulcrum/DECISIONS.md`

Copy to `<project>/.fulcrum/DECISIONS.md`. **Append-only, ADR-lite.** Newest record
at the bottom. Never edit an accepted record — supersede it. The only edit ever
permitted to an existing record is setting its `Status` to `superseded by D-0NN` or
`reverted`.

This file closes a hole. `../../fulcrum-gap-analysis/SKILL.md` classifies a deviation
as **drift** rather than a **gap** only when it can find a decision record for the
artifact involved. It joins on the artifact identifier, so `Affects` must name
concrete entities, screens, actions or blocks — never a prose description of an area
of the app.

Schema: `../references/file-schemas.md`, heading "DECISIONS.md".

---

<!-- fulcrum-schema: DECISIONS v1 -->

# DECISIONS — \<solution name\>

Append-only. One record per decision.

## D-001 — \<short title\>

- **Date:** \<ISO-8601 UTC\>
- **Decider:** `user` | `agent` | `mentor`
- **Status:** `accepted`
- **Affects:** \<app identifier\> / \<Order, OrderList, GetOrders — concrete identifiers\>

**Context.** \<What was true that forced a choice. One paragraph.\>

**Decision.** \<What was decided, in the imperative.\>

**Alternatives rejected.** \<What else was on the table, and why not.\>

**Consequences.** \<What this makes harder or impossible later.\>

---

## D-002 — Shipment status is a static entity, not a free-text field

- **Date:** 2026-09-28T11:40:00Z
- **Decider:** `mentor`
- **Status:** `accepted`
- **Affects:** ordering_app / Shipment, ShipmentStatus, ShipmentDetail

**Context.** The requirements name five shipment states in prose and do not say how
they are stored. Under `posture: collaborative`, Mentor was asked for the idiomatic
ODC shape and proposed a static entity.

**Decision.** Model shipment status as a static entity with five records, referenced
from `Shipment`.

**Alternatives rejected.** A text attribute — unvalidated, and unfilterable in an
aggregate without string comparison.

**Consequences.** Adding a sixth state is a model change and a publish, not data
entry. The identifiers are fixed at creation; see
`../../fulcrum-engine-traps/references/static-entities.md` before renaming one.

---

`Decider: mentor` means Mentor chose the approach and the agent accepted it. Under
`posture: collaborative` that is the common case, and an unrecorded Mentor choice is
exactly the drift a later gap analysis cannot explain.
