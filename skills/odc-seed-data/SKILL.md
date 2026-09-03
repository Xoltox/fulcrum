---
name: odc-seed-data
description: >
  Seeds sample or demo data into an ODC app so screens have real rows to
  read against. Owns idempotent loaders, natural keys, relative timestamps,
  static-entity identifiers, and reset paths (and their absence). Use when
  asked to seed sample data, load demo data into an app, set up test data
  for screens, or when seeded rows come back blank, duplicated, or stale.
  Trigger phrases: "seed sample data", "load demo data into my ODC app",
  "my seeded rows are blank", "set up test data for these screens", "add a
  reset/teardown for my seed data", "the seed ran twice and duplicated rows".
version: "1.0.0"
requires: >
  ODC MCP surface for model edits and publish; tenant-profile.md present or
  in progress for tenant-varying facts (server-action public exposure,
  static-entity auto-numbering, live-row-read path); a scripted HTTP client
  to call the exposed loader endpoint on demand.
---

# odc-seed-data

## Boundary

This skill owns **getting rows into the database safely and repeatably**. It
does not own screen construction (see `../odc-engine-traps/SKILL.md`), turn
sizing (see `../odc-mentor-turns/SKILL.md`), or the verification instruments
themselves (see `../odc-verification/SKILL.md` — this skill states the
four-step seed-proof obligation, that sibling owns the tools that discharge
it). Seed before building any screen that reads the data — an empty table
hides its own screen bugs.

Budget seed work at **three or more turns minimum**, as its own phase, not a
chore folded into a screen turn. On the reference build this was the single
most expensive step: ~18 revisions, 4+ hours, 14 turns, two abandoned
monolithic attempts, and one wedged session. `[VERIFIED]`

## The loader pattern

One idempotent load action per entity, called by an orchestrator action, run
from a published-time trigger:

1. Each `LoadSampleDataFor<Entity>` action carries **its own guard**,
   checking an entity or field specific to that loader. Never bolt a later
   loader's guard onto an earlier one's, and never let a later loader
   silently no-op just because an earlier one already ran — each loader must
   independently answer "have I already run" for its own data. `[VERIFIED]`
2. An orchestrator (`LoadSampleData`) chains every per-entity loader in
   FK-safe parent-before-child order.
3. Wire the orchestrator to a published-time trigger so seeding happens
   automatically on every publish; the per-loader guards make repeat firing
   harmless. See "What context tools don't show you" below — this trigger
   is invisible to model inspection, which is expected, not evidence it is
   missing.
4. Assign every output count (rows created, skipped flag) via an explicit
   `Assign` node from a real running total before the action ends — never a
   literal. A literal `RowsCreated = 0` in the output path is indistinguishable
   from a genuine zero once read back over REST (REST silently omits falsey
   values — see `../odc-engine-traps/SKILL.md`).

Worked structure and JSON-resource layout: `references/loader-pattern.md`.

## The most expensive defect: the empty record source

On the reference build, a create-or-update action's `Source` was left as an
empty inline record literal on **all seven loaders**. It published with
**zero validation errors** and silently blanked every field and every
foreign key across 34 rows. Nothing at the model layer caught it — not
validation, not publish, not a clean revision. `[VERIFIED]`

**Standing rule:** declare an explicit record variable, populate every
field — including every foreign key — with an `Assign` node, and only then
feed that variable into the create-or-update's `Source`. Never rely on an
inline or implied record source. Before trusting any loader, read `.Source`
back verbatim and confirm it names a populated local record variable, not a
literal.

Archetype of "clean publish, blank data": treat any data-writing action as
unproven until rows have been read back, regardless of validation status.

## Guard conditions and null semantics

A guard comparing a text attribute to an empty string (`Attribute = ""`)
never matches when the platform's stored default is `null`, not empty text
— and swapping in a null-identifier comparison is a different type and
silently never matches either. `[SINGLE-OBSERVATION]`

**Robust form:** test `Length(Attribute) = 0`, folding null and empty into
one true condition.

Generalize this: any guard that can silently never match produces a loader
that either **silently re-runs** (duplicating rows) or **silently never
runs** (screens stay empty) — and neither failure shows up in validation or
publish. Every guard in a loader chain deserves this scrutiny, not just the
orchestrator's top-level check.

## Natural keys

Express every foreign key and every lookup in seed source data as a
**natural key** — a code, a name, a label — never a positional index or a
generated/numeric Id. Resolve it to a real Id by lookup at load time. A
generated or positional identifier breaks the moment the seed is re-run or
reset, because the platform does not guarantee the same identifier next
time: a re-run must **update** a row it recognizes, never duplicate it.
`[VERIFIED]`

## Relative timestamps

Never hardcode a calendar date in seed data — it drifts, and a gate built
against it breaks as the wall clock moves past the date. `[VERIFIED]`

**Working pattern:** store a day offset (integer, e.g. `-3`, `0`, `+7`) plus
a time of day (text, e.g. `"09:30"`) in the seed source, and build the
actual timestamp at load time relative to the current date/time. Downstream,
assert any time-dependent figure as an **invariant** (e.g. "the count of
rows dated in the last 7 days"), never as a fixed expected value, for the
same reason.

## Static entities

- Auto-numbering for static-entity records is unavailable on current
  platform versions; creating one without an explicit Id passes validation
  and then **fails at deploy**. Always assign explicit sequential
  identifiers at record-creation time. Whether the underlying flag is
  present, and its exact error code, is a `[TENANT]` fact — defer to
  `tenant-profile.md` rather than asserting one here.
- Reference a static record by its **identifier**, never by label text and
  never by positional index — label and identifier text can differ,
  including in whitespace, so matching on the label picks the wrong row
  without warning.
- Watch for duplicate static records on re-run; they are not covered by the
  natural-key resolution above unless the loader explicitly guards them too.

## Exposing the loader

A server action cannot be marked public directly on current platform
versions (`[TENANT]` — confirm in `tenant-profile.md`); expose the loader
(and any reset action) through a REST method instead — load-bearing, not
tidiness, since an on-demand HTTP call may be the only way to trigger the
loader outside the publish-time trigger. Response structures can be shared
across REST methods; check that before editing either method, so a
shared-structure edit doesn't silently change both.

## Aggregate limits

Any aggregate expected to return **all** rows — action aggregate or screen
aggregate alike — needs an explicit high maximum-records value. The
platform default silently truncates, and a truncated aggregate inside a
loader or a verification action produces a plausible-looking wrong count
with no error.

## Verifying a seed

Four-step proof; discharge each step with the instruments in
`../odc-verification/SKILL.md` (diagnostic REST endpoint pattern when there
is no direct query path — `[TENANT]`, check `tenant-profile.md`):

1. Load on an empty/reset database → confirm real, non-zero row counts.
2. Load again → confirm it was skipped (zero rows written this time).
3. Reset, then load → confirm the counts come back, proving the seed is
   re-loadable, not a one-shot.
4. Spot-check foreign keys on a handful of leaf rows resolve to the
   *intended* parent, not null and not row one (a wrong join or sort-order
   bug silently picks row one when a lookup is written wrong).

Verify arithmetic invariants across **all** rows, not a sample. Hand-derive
expected counts independently before comparing — never accept the agent's
own classification of "looks right." This pass alone can consume a whole
turn's budget; plan for it inside the three-turn minimum, not on top of it.

## The reset path, and its absence

A reset/teardown action is genuinely valuable, and may not be buildable. On
the reference build, bulk-delete reset actions built with zero validation
errors but publish failed twice with a non-transient internal build error
that was never diagnosed; the feature was abandoned. `[SINGLE-OBSERVATION]`

If a reset path cannot be shipped, plan for the consequences rather than
retrying indefinitely: every gate run that exercises a create flow leaves
permanent rows behind; finite seed pools (a fixed list of natural keys to
pick from) get exhausted by repeated runs; diagnostic endpoints stood up
for verification accumulate with no removal path. Design gates to detect
and report exhaustion (an empty candidate pool) rather than silently
passing on an empty result.

If a reset action does get built, do not trust Mentor's report that the
delete succeeded — verify against the live schema or a live-data read-back,
per `../odc-verification/SKILL.md`.

## What the platform's context tools do not show you

Context/model-inspection tools do not enumerate an app's Resources tree, and
do not enumerate its Automations tree (Agents, Events, **Timers**). A
loader wired to a published-time trigger is invisible to that kind of
inspection. Do not conclude the trigger is missing from an inspection result
alone — confirm via the design surface directly before reporting it absent.
`[SINGLE-OBSERVATION]`

## Where the depth lives

`references/loader-pattern.md` — worked loader/orchestrator structure,
JSON-resource-per-entity layout, and reset-action ordering.
