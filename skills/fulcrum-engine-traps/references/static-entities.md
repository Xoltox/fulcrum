# Static entities

## 1. Reference static-entity records by identifier, never by label `[VERIFIED]`

Label text and the record's stable identifier can differ in spacing or
wording (e.g. a label reading "Not Received" against an identifier
`NotReceived`) — referencing by label string risks a silent mismatch.
Reference by the entity's identifier (`Entities.<Entity>.<Identifier>`)
every time. This is one of the most reliable constructs on the platform
when done this way — zero substitutions, zero positional-guess defects
observed across many sightings.

## 2. Static-entity records need explicit sequential Ids `[TENANT]`

**Failure mode.** Where automatic Id numbering for static entities is
disabled on a tenant, creating records without explicit sequential `Id`
values (1..N) publishes with 0 validation errors and then fails at
**deploy** time with an internal error (observed as `OS-DPL-50205`) —
after publish already reported success.

**Fix:** check `tenant-profile.md`. Where auto-numbering is off, state as
a load-bearing constraint at the top of any spec creating static-entity
records: "assign explicit sequential Id values (1..N) to every
static-entity record at creation time." Stating this proactively in the
spec, rather than discovering it at a failed deploy, is one of the
cheapest reliability levers available — it converts a defect that costs a
fix turn into something that never happens.

## 3. Two FKs from one entity to the same target are supported, not aliased `[SINGLE-OBSERVATION]`

An entity can carry two independent foreign keys pointing at the same
target entity (e.g. two separate role references into the same `Person`
entity), and the platform keeps them genuinely independent — it does not
silently collapse or alias them together. Safe to use when the data model
actually needs two distinct relationships to the same entity; no special
phrasing needed to prevent aliasing, but confirm both FKs resolve to
different attributes in a read-back since this shape is easy to describe
ambiguously in a spec.

## 4. Prefer a joined attribute over a second aggregate for static-entity-driven state

See `aggregates-and-repeaters.md` #7 — joining a static entity into an
existing aggregate and comparing the joined attribute against a literal
is cheaper and simpler than building a dedicated aggregate over the
static entity, for e.g. "has this row passed milestone N"-shaped checks.
