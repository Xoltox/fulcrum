# Icons, CSS, and theming

## 1. An icon widget's icon name is a static string, not an expression slot `[VERIFIED]`

**Failure mode.** The icon widget's `Icon`/`IconName` property looks
bindable but is a plain static string. Binding an `If(...)` expression to
it stores the **literal expression text** as the icon name — the render
shows an empty glyph with an empty `data-icon` attribute.

**Visible?** No — 0 validation errors, clean publish; only the render (and
inspecting the actual `data-icon` value) shows it empty.

**Fix:** use two icon instances with mutually-exclusive static `Visible`
gates (`If(cond, ...)` on `Visible`, one icon per branch, real static names
on each), never a conditional expression on the icon name itself. The same
shape applies to a per-row icon in a repeater — an icon cannot be
data-bound per row; switch on the row value and render one of N literal
icon widgets inside `If`s.

## 2. Icon glyph names are case- and form-sensitive, and a wrong name renders nothing `[TENANT]`

A wrong glyph name compiles clean, validates clean, and renders an empty
glyph with zero errors anywhere. The exact casing convention (e.g.
all-lowercase kebab-case vs PascalCase) and the available glyph set are
properties of the icon font this tenant/app references — check
`tenant-profile.md`. Do not assume a name works because it "looks right":
- Chevron-style expand/collapse glyphs are commonly named `caret-down` /
  `caret-up` rather than `chevron-down` / `chevron-up` — verify, don't
  assume either.
- A `-fill` suffixed variant can render 0×0 if the referenced font ships
  outline weight only for that glyph.

**Fix:** never ask Mentor whether an icon name is valid — it cannot
introspect the icon font at all; its answer is usage archaeology ("have I
seen this name used elsewhere"), not validation. Instead: set the name,
then confirm it against a sibling icon already known to render, or check
the render directly.

## 3. Only real theme CSS variables exist `[TENANT]`

Invented CSS variable names (a plausible-looking `--color-*`, `--space-*`,
etc. that isn't actually defined) silently no-op — the property falls
back to its default with no error. Verify any theme variable via a
computed-style read against the live render, not by pattern-matching the
naming convention. The actual variable namespace and set is tenant/theme
specific — check `tenant-profile.md`.

## 4. `Style` vs `CustomStyle` — the boundary is narrower than "always use CustomStyle" `[VERIFIED]`

Raw CSS put into a `Style` slot is silently dropped on link widgets and on
OutSystems UI **block** widgets generally. But on a plain expression
widget, a `Style` value **does** reach the DOM `style` attribute and
works. So the trap is real for link/block widgets, not universal.

**The deeper finding is about Mentor's behavior, not CSS**: it mirrors
whatever styling convention it can read in the surrounding app rather than
applying one stable rule — it will use `CustomStyle` on one pane because a
nearby pane does, and put raw CSS in a plain expression's `Style` on
another pane for the same reason. When there is no sibling to mirror, it
falls back to the correct slot (`CustomStyle`) on its own.

**Practical rule:** prefer `CustomStyle` regardless — it always works.
When consistency with an existing pattern matters, tell Mentor explicitly
which sibling to mirror; don't assume it will apply a rule uniformly on
its own. And note a **class name** placed in a container's `Style` slot
(as opposed to raw CSS) is a different, reliable mechanism — see below.

## 5. A CSS class name in a container's `Style` slot is reliable `[VERIFIED]`

A container's `Style` property accepting an `If(...)` expression that
returns class-name strings (conditional class selection) is the class slot
working as designed, and is solid — this is not the same thing as raw CSS
in `Style`, which is the trap above.

## 6. A CSS class declared later with equal specificity can silently defeat an earlier utility class `[SINGLE-OBSERVATION]`

If two classes of equal specificity both set a color and the more specific
(later-declared) one wins by source order, a utility "brand color" class
can be silently overridden. Fix by inheriting color rather than re-setting
it in the more specific class, or by not setting color there at all.

## 7. Utility classes can be layered — a variant class alone is not enough `[VERIFIED]`, class names themselves are project-local

Some CSS utility systems split a construct into a base class (geometry:
`display`, `border-radius`, `padding`) and one or more variant classes
(color only). Applying the variant class alone, without the base, renders
a full-bleed unstyled block instead of the intended pill/chip/badge shape.

**Fix, state the consequence not just the requirement:** "BOTH classes are
mandatory — the base class carries the geometry and the variant is
variant-only, so the variant alone renders as a full-width block." Audit
whether a project's utility classes are layered this way before styling
any chip/pill/badge-shaped element; the actual class names are project
local, not platform fact.

## 8. `AdvancedHtml` has no `Style` slot at all `[VERIFIED]`

An advanced-HTML widget exposes no style property to set a class on
directly. Ask for the layout requirement as an outcome ("right-align it
using a real existing class, report which class you used"), not as a
property to set — Mentor will correctly wrap it in a container and apply
the class there, and say so.

## 9. A progress-bar's color input can be a static-entity identifier, not a CSS value `[TENANT]`

Where a progress/status color input parameter exists, check whether it
expects a `Color`-style static-entity identifier (`Entities.Color.Red`,
etc.) rather than a CSS variable string — passing a CSS-variable-shaped
string into an identifier-typed input fails or no-ops. If the block has no
color input at all, put the color in `CustomStyle`, never in `Style` —
report which slot was used either way.

## 10. Passing a project class to an overlay block's `ExtendedClass` can break its positioning `[VERIFIED]`

An overlay/sheet-style block's own positioning CSS (its fixed/relative
positioning, margins) is load-bearing. Passing a project class through its
`ExtendedClass` input can silently collide with that positioning — e.g.
overriding `position:fixed` with `position:relative` and a negative margin
collapses the whole sheet to a thin strip.

**Visible?** No — model read-back clean, validator clean, publish clean,
even a full-text DOM check can pass; only the visual render shows the
collapse.

**Fix:** don't pass a project class into an overlay block's own
class/style-passthrough input. Put visual treatment on your own child
widgets' `CustomStyle` instead. And ask for the *outcome* ("give it an
opaque surface with rounded top corners; report what you used"), not a
specific class name — naming the class removes Mentor's chance to notice
the positioning conflict before applying it verbatim.

## 11. Chart per-point styling is a separate property from series styling `[SINGLE-OBSERVATION]`

Per-bar/per-slice color on a bar or similar chart is a data-point-level
property, distinct from the whole-series styling property — setting the
series property alone will not vary color per bar. Per-bar value labels
are commonly a built-in boolean on the chart block — no CSS/DOM hack is
needed for that specific requirement; check the block's own inputs before
building a workaround.

**Donut/pie center-label:** where no real "center label" property exists
on the chart block and its config struct has no raw CSS passthrough, do
not invent new CSS to fake it — reuse whatever overlay-container
convention the app already uses elsewhere for centering content over a
graphic, rather than adding a new one-off mechanism.
