# Loader pattern — worked structure

## Layout

- A resources folder holds **one JSON file per entity** (e.g. `Order.json`,
  `Customer.json`) — the raw seed source, with every FK expressed as a
  natural key (see SKILL.md) and every timestamp as a day-offset + time
  pair.
- A logic folder holds one `LoadSampleDataFor<Entity>` server action per
  entity, plus one orchestrator, `LoadSampleData`.

## Per-entity loader

For each `LoadSampleDataFor<Entity>`:

1. **Guard** — an aggregate or count against a field/entity specific to
   *this* entity's own seed rows (e.g. "does a `Customer` with this seed's
   natural key already exist"), not a shared anchor borrowed from another
   loader. If the guard's condition is a text comparison, use
   `Length(Attribute) = 0` rather than `Attribute = ""` (see SKILL.md, Guard
   conditions).
2. **Deserialize** the entity's JSON resource into a list of local
   structures.
3. **ForEach** row:
   - Resolve every natural-key FK to a real Id via a lookup aggregate.
   - Resolve any day-offset + time-of-day pair into an actual timestamp
     relative to the current date/time.
   - Declare an explicit record variable of the entity's Create/Update
     structure. Populate **every** field, including every resolved FK, with
     an `Assign` node.
   - Pass that populated variable — never an inline or default record
     literal — as the `Source` of the `CreateOrUpdate` node.
4. **Count** — increment a running total in a local variable as each row is
   written; assign the final total to the action's output via an `Assign`
   node before `End`. Never a literal.

## Orchestrator

`LoadSampleData`: calls every `LoadSampleDataFor<Entity>` in FK-safe
parent-before-child order (parents first, so a child's FK lookup always
finds its parent already seeded). Aggregates run inside these loaders that
are expected to return every matching row need an explicit high
maximum-records value (see SKILL.md, Aggregate limits) — the default limit
silently truncates a lookup or a count.

## Publish-time trigger

Wire the orchestrator to fire on publish (a schedule value meaning "when
published," where the platform exposes one — confirm the exact mechanism
name and availability against `tenant-profile.md` or by direct inspection,
since this surface is one of the areas context-inspection tools do not
enumerate; see SKILL.md, "What the platform's context tools do not show
you"). Because every per-entity guard makes a repeat run a no-op, firing on
every publish is safe.

Give it a generous timeout — a chain of several entity loaders each doing
lookups and row-by-row assigns can run long on a first, empty-database
load.

## Reset ordering (if buildable — see SKILL.md, "The reset path")

If a reset/teardown action is attempted:

- One `DeleteSampleDataFor<Entity>` action per entity.
- A single reset orchestrator deletes **children before parents** — the
  exact reverse of the load order — then calls the load orchestrator to
  re-seed.
- Leave static entities untouched; they are not part of the delete/reload
  cycle (see SKILL.md, Static entities).
- Treat a reset action's own publish as unproven until it publishes clean
  *and* a subsequent live-data read-back shows the rows gone — Mentor's
  self-reported "deleted" is not sufficient (see
  `../../fulcrum-verification/SKILL.md`).

## Exposure

Expose both the load orchestrator and any reset orchestrator as methods on
one REST resource (e.g. `POST /LoadSampleData`, `POST /ResetSampleData`).
Check whether the two methods' response structures can be shared before
editing either — a shared structure means a field added for one method's
response is visible on the other's too.
