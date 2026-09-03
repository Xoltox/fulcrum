# Overlays, wizards, dropdowns, and charts

## 1. Named overlay blocks (Modal / Popup / Popover / BottomSheet / Sidebar / ActionSheet) — existence is a version fact, not a platform fact `[TENANT]`

**Failure mode.** Naming a specific overlay block in a spec without
checking it exists on this app's referenced UI library first can burn a
whole turn: the block may not exist at all in that version, or the
question can come back with a wrong absence answer that is only caught by
a later re-probe.

**Both directions are unproven until checked in the current step**:
- "This block does not exist" is a snapshot of one session's read, not a
  platform fact — an absence answer has been found wrong on re-probe,
  with the block present and public all along. See the correction in
  `../SKILL.md` — never carry a previous step's absence claim forward.
- Conversely, do not assume a block from another app's tenant exists here.

**Fix — pre-flight, every step that needs one, not once per app:**
> "Does the block `<Block>` exist in this application's referenced UI
> library? If not, list the overlay/container blocks that DO exist with
> their input parameters and events, and STOP."

Record the live answer in `tenant-profile.md` for this session; re-probe
at the start of any later step rather than trusting a carried-forward
answer, since the referenced library version can move between steps.

## 2. An overlay block's own input surface may be narrower than expected `[TENANT]`, mechanism is `[PLATFORM]`

**General mechanism:** an overlay/sheet block's inputs are frequently just
an open/closed boolean plus a close event and an extended-class
passthrough — no height, width, or built-in overlay-dimming input. Read
the block's actual input parameters before specifying a requirement like
"three-quarters height" that its input surface may not support at all;
some overlay blocks size purely to their content and cannot be told a
fixed size.

**Some overlay blocks have no `CustomStyle` property at all** — where that
is true, the *only* safe way to style the block's surface is a wrapper
container inside its own content placeholder carrying its own
`CustomStyle`, since the usual "always use `CustomStyle`, never `Style`"
escape hatch (see `icons-and-theming.md`) does not exist on that block,
and passing a class through its extended-class input risks the
positioning collision covered there too.

## 3. An overlay's built-in cancel/close button must be RETAINED `[SINGLE-OBSERVATION]`

Unlike most default children (see the exemption test in `../SKILL.md`),
an action-sheet-style block's own built-in cancel/close footer button is
correctly wired on creation — clicking it fires the close event, keeping
the open-state variable in sync — and is not a placeholder to delete. Ask
whether a default child REPEATS or POSITIONS anything before deleting it;
this one does neither, but it is still load-bearing wiring, not
decoration. Verify wiring with a real click, not just a model read-back.

## 4. Dropdown's real properties are List/Values/Labels/Variable `[SINGLE-OBSERVATION]`

Don't assume a dropdown-style widget exposes a `Source`/`Value`/`Caption`
shape by analogy with other list-bound widgets. Read its actual input
parameters first (see the "read the block first" pattern) — its real
inputs are commonly named `List` (the option set), `Values` (or similar,
the underlying values), `Labels` (display text), and `Variable` (the
two-way bound selection) instead.

## 5. A newly created screen can ship an unwanted default role requirement `[VERIFIED]`

The placeholder-cleanup instinct ("delete every default/placeholder
child") extends beyond widgets to screen-level *properties* — a new
screen can be created with a default role/permission requirement attached
that was never asked for. Check the screen's own properties, not just its
widget tree, after creating it.

## 6. `Columns2`/`Columns3`/`Columns4` fill column-major, not row-major `[VERIFIED]`

For a fixed grid, these are reliable — but the fill order for N children
across K columns is column-major: with 3 columns and 6 children, column 1
gets children 1 and 4, column 2 gets 2 and 5, column 3 gets 3 and 6. It
renders correctly, but the DOM text order does not match reading order —
any assertion checking content "by position" (e.g. "the 4th DOM node
should read X") will fail on a correctly built grid. Assert by label
content, never by position, for anything built with these.

`Columns6` works the same way as `Columns2`-`4` for a fixed grid of six
explicit children — this is not limited to 2/3/4. For a *wrapping* grid
(unknown/variable child count that should wrap to new rows), these
constructs are the wrong tool — use a flex/wrap layout instead and treat
that substitution as sanctioned, not a workaround to avoid.

## 7. Chart styling: per-point vs series, and don't invent CSS for a missing property

See `icons-and-theming.md` #11 for per-bar color, per-bar value labels,
and the donut/pie center-label case — the general rule that applies to
every chart block: read its actual optional-config inputs before
concluding a visual requirement needs a CSS/DOM workaround; when no real
property exists for it, reuse an existing convention already used
elsewhere in the app rather than inventing new one-off CSS.

## 8. A chart bound to a joined aggregate can silently drop zero-value categories

See `aggregates-and-repeaters.md` #3 (join direction) — this is the most
common way a chart under-reports categories, and it is a join-direction
trap, not a chart-specific one.
