# Design spec format - every file under `.fulcrum/design/`

Derived from outsystems-design-to-app v1.4.1 (MIT, Copyright (c) 2026 OutSystems),
modified; see THIRD-PARTY-NOTICE.md. Vendor-sourced rows are [UNVERIFIED].

Fulcrum's change: one Markdown file per screen instead of one JSON spec, size-limited
so a region fits one Mentor turn. Write ownership: `fulcrum-capturer` in phases 1-2
(only the paths its brief names - a shared dispatch the app-wide files, a screen
dispatch only its `screens/<SID>.md`), the orchestrator after; `reference/` and
`user-shots/` are always the orchestrator's; drivers, renderer and verifier never.
(Fulcrum rule) On the full profile every path below sits under `.fulcrum/design/<app>/`.

## Layout and limits

| Path | Schema marker | Limit | Template |
|---|---|---|---|
| `manifest.md` | `design-manifest v1` | one screen of text | `../templates/manifest.md` |
| `source/` | - | write-once verbatim copies; committed per batch B Q5 | - |
| `reference/<SID>.<ext>` | - | the image source file copied unchanged (no crop; a whole image names the screen in the manifest), or the renderer's HTML render copied by the orchestrator | - |
| `screens/<SID>.md` | `design-screen v1` | <= 150 lines; anatomy <= 80; <= 6 top-level regions | `../templates/screen.md` |
| `tokens.md` | - | about 60 lines, advisory | below |
| `theme.css` | - | about 150 lines, advisory; groups <= 25 lines | below |
| `data.md` | - | <= 120 lines | below |
| `gate.md` | `design-gate v1` | one row per check per screen | below |
| `fidelity/<SID>-r<n>.md` | `design-fidelity v1` | one per compare round | `../templates/fidelity.md` |
| `user-shots/<SID>-r<n>.<ext>` | - | tier B: the user's screenshot as received, one per screen per round | - |
| `backlog.md` | - | one line per minor diff or carried gate risk | below |
| `STUDIO-PASS.md` | `design-studio-pass v1` | one pass, `studio` lane only | `../templates/studio-pass.md` |
| `report.md` | `design-report v1` | - | `../templates/report.md` |

Every marker is written `<!-- fulcrum-schema: <marker> -->`; the full set is
`design-manifest v1`, `design-screen v1`, `design-gate v1`, `design-fidelity v1`,
`design-report v1` and `design-studio-pass v1`. A `-` means the file carries none.

A screen file over its limit is split, never trimmed of content: a screen over 6
regions becomes two screens or two steps, because a region must fit one turn. A theme
group stays <= 25 lines for the same reason. The whole-file figures for `tokens.md` and
`theme.css` bound no turn, so going over is noted in `gate.md`, not failed and not
waived: as hard caps they cost a decision record per overrun and caught nothing
`[SINGLE-OBSERVATION]`. (Fulcrum rule)

## screens/<SID>.md

Header: `# <SID> <name> - archetype: <archetype> - reference: reference/<SID>.<ext>`,
then `Layout: <LayoutBlock>   Access: <policy> (<D-id>)`. Sections, in order:
`Anatomy`, `Regions`, `Icons`, `Interactions`, `Acceptance`.

Anatomy attributes, and only these:

| Attribute | Holds |
|---|---|
| block name | A real OS UI block or stock widget (`block-map.md`) |
| `class=` | Classes confirmed stock in the app's theme, or defined in `theme.css` |
| `bind=` | Entity/attribute only - never an aggregate, action or variable name (those are Mentor's to name) |
| `source=` | The list's data in words: entities, join, sort, max |
| `series=` | A chart id from `data.md` |
| `onClick=` | `navigate:<SID>` or `action:<plain words>` |
| `icon=` | A semantic name, resolved to a tenant glyph at the gate |
| `static` | The node shows fixed text |

Mapping to the four-part description (`../../fulcrum-solution-init/SKILL.md`, step 6):
anatomy = VISUAL LAYOUT; `bind`/`source` = DATA FLOW; Interactions = FUNCTIONAL
BEHAVIOR; node order = PRESENTATION ORDER.

Regions: `R1..Rn`, one line each - blocks and constructs (chart, repeater, form,
overlay); a region's subtree must fit one turn (<= ~25 anatomy lines). Icons: location
-> semantic name -> tenant glyph, and `count = N`. Interactions: every interactive
node; static nodes say `static`. Acceptance: `F-<SID>-01..10`, each observable, each
naming its instrument (render, read-back, seed proof).

### Short form

`image` and `studio` lanes only (`build-lanes.md`): header, `Regions`, `Interactions`,
`Acceptance`. No `Anatomy`, no `Icons`: the picture carries them, and Mentor picks the
blocks. `Layout` in the header may read `from image`. A move to the `text` lane
completes the file first.

### Worked neutral screen

```
<!-- fulcrum-schema: design-screen v1 -->
# S02 Shipments - archetype: list-table - reference: reference/S02.png
Layout: LayoutSideMenu   Access: role ShipmentViewer (D-004)
## Anatomy
<LayoutSideMenu>
  {/* R1 header */} <Container class="page-head page-canvas">
     <Text class="h1" static>Shipments</Text>
     <Button class="btn btn-primary" onClick="navigate:S03">New shipment</Button></Container>
  {/* R2 filters */} <Container class="filter-row">
     <Search bind="Shipment.Reference"/> <Dropdown source="ShipmentStatus, all"/></Container>
  {/* R3 table */} <Table source="Shipment join Customer, sort CreatedOn desc, max 50">
     <Column head="REFERENCE"><Text bind="Shipment.Reference"/></Column>
     <Column head="CUSTOMER"><Text bind="Customer.Name"/></Column>
     <Column head="STATUS"><Tag bind="ShipmentStatus.Label"/></Column>
     <Column head=""><Icon icon="chevron-right" static/></Column></Table>
</LayoutSideMenu>
## Regions
R1 page header: Container, Text, Button (primary)
R2 filters: Search, Dropdown over a static entity
R3 table: Table over a joined aggregate (repeater construct)
## Icons
R3 row end -> chevron-right -> <glyph set at gate>; count = 1 per row
## Interactions
R1 Button -> navigate:S03 | R3 row -> navigate:S03 with the row's Id | R1 Text static
## Acceptance
F-S02-01 render: table shows 12 seeded rows, newest first
F-S02-02 render: Status filter narrows rows to the chosen status
F-S02-03 render: New shipment opens S03
```

## tokens.md

One row per token: `name | value (~ if uncertain) | maps to`, where "maps to" is an
existing OS UI `:root` variable override or a `theme.css` class. A token mapped to an
invented CSS variable is a no-op (`../../fulcrum-engine-traps/references/icons-and-theming.md`,
"Only real theme CSS variables exist"); the vocabulary at one library version is
`osui-v3.0.0-theme.md`. Groups: colour, type roles, spacing, radius, shadow. The page
background is defined **and** applied by a class on every screen root.

Where sources disagree, code wins over prose: a config value is what was built. Mark an
interpolated value `~`. A token mapping stays `[UNVERIFIED]` until the first render
reads it back by computed style; the named `theme.css` class is the fallback when a
variable does not take. `[UNVERIFIED]`, not yet render-proven: a web-font `@import` goes
in the first theme group, since CSS ignores an `@import` after any other rule, and a
content security policy may still block it.

## theme.css

Every custom class the anatomies use, defined once, grouped (<= 25 lines per group;
one group per theme turn). No reserved class names (list in `block-map.md`). A class
is stock only once confirmed in the app's theme; otherwise it is defined here. A
utility class in `osui-v3.0.0-theme.md` counts as stock only when the tenant's version
matches that tag (`block-map.md`, heading "OutSystems UI library reference").

## data.md

Sections: `Entities` (attributes, types, FKs; static entities with explicit Ids),
`Seed` (rows verbatim, dates as day offset + time, natural key per entity, <= 12 rows
unless a KPI needs more), `KPIs` (`value | decision | acceptance item`, decision =
stored metric entity / enough seeded rows / static), `Charts` (`id | screen | type |
series -> populated aggregate over a seeded entity | minimum height [UNVERIFIED]`).

## gate.md

Header `<!-- fulcrum-schema: design-gate v1 -->`. Table:
`SID | check | PASS/FAIL | line ref | note`. Written by a fresh gate-mode capturer.

| # | Check |
|---|---|
| 1 | Every visible region of the reference is a node |
| 2 | Every node is a real OS UI block or stock widget; each distinct block `unresolved` until its first step pre-flights it by reference |
| 3 | No section-level flex/grid; Adaptive blocks side by side; exceptions only as named `theme.css` classes; a wrapping grid is `Gallery` with its `List` (flex/wrap only if Gallery is unavailable) |
| 4 | One explicit Layout per screen root |
| 5 | Always-block primitives used (`block-map.md`, heading "Always-block primitives"); source layer names honoured (Carousel, Tabs, Wizard, Accordion) |
| 6 | Only default children that neither repeat nor position are deleted |
| 7 | No project ExtendedClass on overlay blocks |
| 8 | Every class stock-confirmed or defined; no Tailwind names; page background applied; no reserved names |
| 9 | Every data node bound; every chart series resolves to populated data; every KPI has a source decision; no literal dates |
| 10 | Icon count source == anatomy; names resolved via `tenant-profile.md` section 3 or flagged for the chrome step's icon probe; per-row icons as N literal icons under Ifs |
| 11 | One primary action; no interactive widget inside a Link |
| 12 | Acceptance items observable with an instrument; the screen and region limits above hold |

Mechanisms for checks 3, 6, 7, 10 and 11: `block-map.md` (vendor rows `[UNVERIFIED]`)
and `../../fulcrum-engine-traps/` (Gallery/List collapse, overlay ExtendedClass, icon
names). `image` and `studio` lanes run checks 1, 9 and 12 only; the others grade an
anatomy that does not exist (`build-lanes.md`).

FAIL -> one re-capture, one re-gate; a second FAIL is an open risk at batch C. The count
is per check per screen: a new reason on the same check is still a second FAIL, or a
re-gate that keeps finding something never ends. A carried risk gets a `backlog.md` line,
because a risk named only at batch C is lost once the build moves on
`[SINGLE-OBSERVATION]`. A block or widget the tenant lacks is never waived: it fails
at build whatever the gate says.

## backlog.md

`SID | diff | class | severity | round` - minor diffs not fixed at the bar and gate risks
carried from batch C (`class: gate`, `round: -`), listed in the report. Never silently
dropped.

## Step decomposition

Design variant of the micro profile: same files, 5 + N steps, N <= 6, plus one per
split screen step; ceiling N <= 6 and 5 + 2N steps with splits counted. Steps and
`Verify` rungs: `../SKILL.md`, heading "Steps".

`TASKS.md` rows, schema TASKS v3 (`../../fulcrum-project-state/references/file-schemas.md`,
heading "TASKS.md"): per step a `build` and a `publish` row (P1.05 a `seed` row instead
of `build`); `App` the app identifier; `DependsOn` true data edges only (Theme on Shell,
Chrome on Theme, Seed on Data, a screen on Chrome and on the entities it binds; a
screen does not depend on an unrelated screen); `Batchable: yes` for identical-shape
theme or screen rows, `no` otherwise; `Risk: high` for a sign-in screen, a role change
and any row touching shared chrome or theme after a screen passed, else `std`; `Gate: -`
until a gate runs; `Traps` from the step's constructs (e.g. a table ->
`aggregates-and-repeaters`, an overlay -> `overlays-wizards-charts`, icons ->
`icons-and-theming`); `manual` rows for asset upload, tier-B screenshots and a Studio
pass, parked `Blocked on: the user`. A screen step whose build pass needs more than 4 turns
(skeleton plus regions) is split into two steps before batch C, each ending in
Publish; the split steps count in the allowance and in batch C's estimate.

Driver brief for a screen step, inline, composed by the orchestrator from that
screen's file (the one `screens/<SID>.md` it reads, only while composing that step's
brief): the guard invariant; the consult question;
the skeleton (Layout content, Columns/Card skeleton, containers R1..Rn); each region's
subtree, classes, bindings and one-line trap mechanisms; the standard brief block
(`../../fulcrum-unattended-guardrails/references/delegation.md`, "What a brief must
contain"). Never a path to the whole spec - the driver would send it whole.
(Fulcrum rule)
