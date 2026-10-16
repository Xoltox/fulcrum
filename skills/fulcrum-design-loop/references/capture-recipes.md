# Capture recipes - design source to design spec

Derived from outsystems-design-to-app v1.4.1 (MIT, Copyright (c) 2026 OutSystems),
modified; see THIRD-PARTY-NOTICE.md. Vendor-sourced rows are [UNVERIFIED].

Run by `fulcrum-capturer` in capture mode. Output schemas: `design-spec-format.md`.
Block lookup: `block-map.md`; archetype cues: `screen-archetypes.md`.

## Why an anatomy, not prose

Mentor never sees the image; it sees only prompt text. A prose description ("a
stack of three compact cards") leaves the structure to Mentor, and it drifts -
oversized cards, duplicated labels, empty values `[UNVERIFIED]` (vendor field
report). A widget tree pins nesting, block choice and classes per node. The anatomy
is still only the VISUAL LAYOUT part of a step's description; Fulcrum sends it one
region at a time, never whole.

## Order of work

Two kinds of capture dispatch, never mixed in one brief (Fulcrum rule):

- **Shared** - one dispatch, first, before any screen dispatch: enumerate the screens
  from the source (grouping rules under "Multi-image sources"), assign `SID`s S01..,
  and write the app-wide files `tokens.md`, `theme.css` and `data.md`. The screen list
  with `SID`, name and the source file (and, for a whole image, which part of it) goes
  in the report; the orchestrator records it in `manifest.md`. A later serial shared
  dispatch adds what screen dispatches reported missing.
- **Screen** - after the shared dispatch, one per <= 3 screens, parallel allowed:
  steps 1-6 below, writing only `screens/<SID>.md` for its own `SID`s. A class, token
  or entity the shared files lack is reported, never written.

1. Read `manifest.md` for the screens assigned to this dispatch (<= 3), the viewport,
   the reference images and the shared files.
2. Classify each screen by archetype (`screen-archetypes.md`); the archetype's common
   miss is the first thing to check in the capture.
3. Walk the screen into <= 6 top-level regions. More -> report it: the orchestrator
   splits into two screens or two steps.
4. Map each region to a block (`block-map.md`); write the anatomy.
5. Record tokens, classes, data, icons, interactions, acceptance items.
6. Report per the `fulcrum-capturer` role; questions for the user go in the report.

## Recipe A - reconstruct (screenshots, concept images, exported frames)

- Region by region, top-left to bottom-right. Each visible region becomes a node;
  a region seen but not mapped is reported, never dropped.
- Read classes from the pixels: grid and gaps, sizes, colours, type roles.
- **Uncertain hex is marked `~`** (`~#3B5BDB`). A `~` value is the bar's business:
  at a structural bar its drift is backlog, at a visual bar it is compared.
- Scrim or modal images: reconstruct the underlying screen from structure; only the
  crisp modal is exact.
- Low-fidelity concepts: capture structure and copy; mark every colour `~`, and say
  in the report that a visual bar on this source will be judged loosely.

## Recipe B - extract (HTML, TSX/React)

The source already is an anatomy.

| Source construct | Becomes |
|---|---|
| Component | Block (via `block-map.md`), keeping the component name as a comment |
| Tailwind classes, CSS constants, theme objects | Tokens in `tokens.md` and named classes in `theme.css` - never Tailwind names on nodes, since the theme does not define them and an undefined class is a silent no-op |
| Hooks, props, fetch results | `bind=` entity/attribute and `source=` in words |
| Literal arrays | Chart `series=` ids and seed rows in `data.md` |
| Routes and handlers | `onClick="navigate:<SID>"` or `action:<plain words>` |

## Figma

With a design-tool read capability: frames larger than 100 x 50 are candidates;
skip decorative layers under 50 px; read variables into `tokens.md`; layer names drive
source-name -> block (a layer named Tabs, Carousel, Wizard or Accordion is honoured
as that block). Without one: a `manual` stop asks the user to export each frame as
an image at the design width, then Recipe A.

## Reference images

`design/reference/<SID>.<ext>` is written by the **orchestrator only**, never by a
capturer or the renderer. (Fulcrum rule)

- **Image sources** (screenshots, concepts, exported Figma frames): the reference is
  the source file itself, copied unchanged. No cropping: a per-screen source file is
  copied as that screen's reference; a whole image holding several screens is copied
  whole for each, and the manifest `Reference` column names which part is the screen.
- **HTML source:** the reference is a render, not the code. Tier A briefs
  `fulcrum-renderer` to render the local file at the manifest viewport into its own
  evidence folder (`../../fulcrum-render-check/SKILL.md`, heading "Local-file
  reference render - no app"); the orchestrator then copies that capture into
  `design/reference/<SID>.png`. Without a browser: capture from code, and compare
  later against the user's screenshot (tier B) or structure only (tier C).

## Multi-image sources

One app may arrive as several images. Group them by screen with the rules in
`../../fulcrum-solution-init/references/source-triage.md`, heading "Deduplicating to
screen/flow groups"; states of one screen (empty, filtered, expanded) are one `SID`
with their acceptance items, not extra screens. If grouping needs more than that
heading - dimension scans, asset triage, more than about six groups - the source is
not a design-loop source: stop and report for a route to `fulcrum-solution-init`.

## Transcription

- Copy text and sample values verbatim, including casing and units.
- **Dates as day offset + time** (`-3d 09:30`), never literal dates - a literal date
  ages out of every relative filter (`../../fulcrum-seed-data/SKILL.md`, "Relative
  timestamps").
- Up to 12 seed rows per entity, with a natural key, unless a KPI decision needs more.
- Never invent rows the design does not show except where a KPI decision requires
  them; say which.

## KPI decision

A headline number (`135`, `15.6 days`) is almost never a live count over a dozen
seeded rows; `Count()` over 8 rows will not show 135 `[UNVERIFIED]` (vendor). Decide
per KPI, in `data.md`: stored metric entity | enough seeded rows | static text, and
name the acceptance item that proves it.

## Chart cues `[UNVERIFIED]`

| Design shows | Capture as |
|---|---|
| Segmented horizontal strip | Stacked-100 horizontal bar chart, one series per segment |
| Sparkline | Line chart, axes and legend hidden, fixed width class |
| Thin row chart | Same, with a minimum height recorded in `data.md` |

Every series resolves to a populated aggregate over a seeded entity; a chart on an
empty data-point list renders nothing while publish stays clean. A very short chart
can collapse because the chart library reserves spacing; record a minimum height and
mark it `[UNVERIFIED]` until rendered.

## Sizing completeness

Structure right, look wrong usually means size was under-specified `[UNVERIFIED]`:

- Every referenced custom class is defined in `theme.css`.
- The page background is defined **and** applied by a class on every screen root;
  defined-only falls through to the theme default.
- Metrics carry no-wrap and a minimum width; sparklines a fixed width; grids explicit
  column sizes; inline label pairs an explicit gap.
