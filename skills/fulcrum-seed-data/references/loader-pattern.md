# Loader pattern - worked structure

## Layout

- A resources folder holds **one JSON file per entity** (e.g. `Order.json`,
  `Customer.json`) - the raw seed source, with every FK expressed as a
  natural key (see SKILL.md) and every timestamp as a day-offset + time
  pair.
- A logic folder holds one `LoadSampleDataFor<Entity>` server action per
  entity, plus one orchestrator, `LoadSampleData`.

## Per-entity loader

For each `LoadSampleDataFor<Entity>`:

1. **Guard** - an aggregate or count against a field/entity specific to
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
   - Pass that populated variable - never an inline or default record
     literal - as the `Source` of the `CreateOrUpdate` node.
4. **Count** - increment a running total in a local variable as each row is
   written; assign the final total to the action's output via an `Assign`
   node before `End`. Never a literal.

## Foreign keys and counts

- Resolve a parent by lookup on its full natural key, never by slicing a code
  string with `Substr`: a wrong offset matched nothing, every row skipped, and the
  timer still ended "Ok, 0 errors". A first "fix" that moved the offset made it
  worse `[VERIFIED]`.
- Each loader logs `Created` and `Skipped` per entity and returns them; the
  verification path fails when `Skipped` exceeds what the guard predicts. A
  diagnosis from Mentor is belief: read the actual stored format (one read or
  trace) before patching.
- Derive expected counts by script from the seed source. A hand count in a
  seed spec produced wrong expectations in two steps `[SINGLE-OBSERVATION]`.

## Anchor and create-only

Loaders that read the current date on every publish re-date their rows each
time, and a background loader then silently undoes decisions made in the app
`[VERIFIED]`. So:

- Write one anchor date (a settings row) only when absent; compute every
  day-offset from it.
- Loaders are create-only. An update path is allowed only to fill a missing
  link, never to overwrite a field a user may have changed.
- Aged seed shows nonsense in time-based figures (negative durations, ratios
  over 100%) until re-seeded; schedule a documented reset and re-seed before any
  KPI check, and treat such a figure as aging before treating it as a formula
  bug. A create-only re-run cannot re-date a row and the anchor is write-once, so
  only a reset that deletes the anchor does (heading "Reset ordering").

## Seeding from a file

An uploaded attachment (CSV or JSON) is read by Mentor but is not a seed path:
in one probe Mentor typed the values into assignment steps of an action that
nothing called, with no runtime resource behind it `[SINGLE-OBSERVATION]`
(2026-10-30). Binary spreadsheet and image carriers were rejected earlier
`[SINGLE-OBSERVATION]`. What worked: give Mentor about ten inline example rows
and have it extrapolate them into a JSON resource copied into the app
directory, loaded by a guarded loader on a timer; each prompt stayed under 600
characters `[SINGLE-OBSERVATION]`. Whether the attachment path is reachable by
another route is `[UNVERIFIED]`.

## Orchestrator

`LoadSampleData`: calls every `LoadSampleDataFor<Entity>` in FK-safe
parent-before-child order (parents first, so a child's FK lookup always
finds its parent already seeded). Aggregates run inside these loaders that
are expected to return every matching row need an explicit high
maximum-records value (see SKILL.md, Aggregate limits) - the default limit
silently truncates a lookup or a count.

## Publish-time trigger

Wire the orchestrator to fire on publish (a schedule value meaning "when
published," where the platform exposes one - confirm the exact mechanism
name and availability against `tenant-profile.md` or by direct inspection,
since this surface is one of the areas context-inspection tools do not
enumerate; see SKILL.md, "What the platform's context tools do not show
you"). Because every per-entity guard makes a repeat run a no-op, firing on
every publish is safe.

Trigger the seed from a timer scheduled When-Published, not from a screen or
app OnInitialize action. `[UNVERIFIED]` Vendor skill
`outsystems-design-to-app` (`references/gotchas/tablerecords-seeding.md`,
`references/design-capture.md`) prescribes the When-Published timer and calls
the OnInitialize list path a distant fallback (in-memory, not persisted);
not tested here. Verify after publish that the timer ran (runtime logs).

Give it a generous timeout - a chain of several entity loaders each doing
lookups and row-by-row assigns can run long on a first, empty-database
load.

## Reset ordering (if buildable - see SKILL.md, "The reset path")

If a reset/teardown action is attempted:

- One `DeleteSampleDataFor<Entity>` action per entity.
- A single reset orchestrator deletes **children before parents** - the
  exact reverse of the load order - then calls the load orchestrator to
  re-seed.
- Delete the anchor row too, or the re-seed brings the rows back on the old
  dates and the aged figures stay wrong.
- Leave static entities untouched; they are not part of the delete/reload
  cycle (see SKILL.md, Static entities).
- Treat a reset action's own publish as unproven until it publishes clean
  *and* a subsequent live-data read-back shows the rows gone - Mentor's
  self-reported "deleted" is not sufficient (see
  `../../fulcrum-verification/SKILL.md`).

## Exposure

Expose both the load orchestrator and any reset orchestrator as methods on
one REST resource (e.g. `POST /LoadSampleData`, `POST /ResetSampleData`).
Check whether the two methods' response structures can be shared before
editing either - a shared structure means a field added for one method's
response is visible on the other's too.
