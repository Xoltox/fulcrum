# Links, navigation, and click targets

## 1. A link defaults to inline display `[VERIFIED]`

**Failure mode.** The link widget defaults to `display:inline`. Wrapping a
card, tile, or any block-level content in one makes it overflow its own
padding box — the wrapped content no longer respects its container's
sizing.

**Visible to validation/publish?** No — every binding is correct, the DOM
text is all present and correct; only the render shows the overflow.

**Fix, and make it standing practice, not a one-off patch:** set an
explicit block display on every link-wrapped card. Doing this
pre-emptively (rather than patching it after the fact) eliminated
recurrences entirely from the point it was adopted — put it in every
layout prompt that wraps existing content in a link, not just the first
one.

## 2. Wrapping existing content in a link restyles its text `[SINGLE-OBSERVATION]`

Wrapping an already-built tile/label in a link recolors its text to the
anchor color, which can drop contrast to near-invisible against a colored
background. This is visible only in the render — DOM text and bindings are
untouched. Plan the color override on the wrapped content in the **same**
turn as the wrap, not as a follow-up.

## 3. A link ships a default text node `[VERIFIED]`

New link widgets ship a child text node with the literal text `"link"`.
This is a genuine placeholder (it neither repeats nor positions anything —
see the exemption test in `../SKILL.md`) — delete it. It is easy to miss
because a "no literal `Button` caption" placeholder check does not catch
it; the literal text is `"link"`, not `"Button"`.

## 4. A native container has no click event `[VERIFIED]`

A plain container widget cannot be given a click handler — there is no
click event on it. For a click-to-select card/tile, wrap the content in a
link widget instead (and apply traps #1 and #2 above in the same turn).

## 5. Wrapping an existing block instance in a link, without disturbing it `[SINGLE-OBSERVATION]`

Wrapping an already-built block instance in a new link and wiring
`OnClick` can land correctly even when the turn's own report shows Mentor
internally recreated/renamed widgets to get there (visible as leftover
`2`-suffixed widget names before a final cleanup). A high internal-retry
count on this kind of turn is not itself a failure signal, but demand a
full verbatim read-back of the moved subtree's bindings afterward — don't
accept "done" on its own.

## 6. Wizard mechanics are not built-in `[VERIFIED]`

**Failure mode.** The wizard widget has no built-in step index or
next/back mechanism. You must build your own current-step variable and
wire the transitions yourself.

**Structural trap inside it:** step-content containers are **sibling**
containers to the wizard, not children of the wizard's own item — the
wizard item itself only holds the header caption. A step container left at
its default `Visible = True` bleeds into the initial screen load
regardless of which step is "current."

**Fix:** build an explicit step-index variable; wire each step transition
to it; explicitly set every step container's initial visibility rather
than trusting the default; and check on load that only the first step's
container is visible.
