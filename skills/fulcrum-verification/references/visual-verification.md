# Visual verification

Rung 5 of the proof ladder catches defect classes nothing cheaper can reach
(see `defect-instrument-matrix.md`). This file is how to run that rung
without fooling yourself.

## The capture trap, generalised

`[VERIFIED]` A capture tool's idea of "the full page" is frequently not the
app's real scroll container. In the source build, the app shell scrolled an
internal container element, not the document — so a "full page" capture
silently cropped every screenshot at the document's fold, and every earlier
image carried that blind spot with no error surfaced anywhere.

This is a class of trap, not a fact about one framework: any layout that
scrolls a nested container instead of the document body will silently defeat
a naive full-page capture, in any harness, on any platform.

Procedure:
1. On first contact with an app (or app section) using this skill, identify
   the actual scrolling element — not the assumed document root. Compare the
   document's reported height against the height of candidate container
   elements; the one that disagrees is usually the real scroll container.
2. Measure and capture against that container specifically, not the
   document, for every subsequent screenshot in that app or section.
3. Treat this as a one-time-per-app setup cost, not a per-screenshot check —
   but re-verify if the shell/layout changes.

## DOM identity over visible-text extraction

Verify element identity and structure from markup, not from a visible-text
dump. A closed or hidden overlay yields empty visible text while its full
markup — including correct content — remains present in the DOM. `[VERIFIED]`

Corollary: an overlay that is not yet wired to its opening trigger can still
be verified structurally (its markup exists, its content is correct) before
the interaction that reveals it is built.

## A text dump is not a visibility check

`[VERIFIED]` Content can be fully present and correct in the DOM while being
completely unreachable to the user. The source build hit a case where an
overlay was collapsed to an invisible strip by a style override, yet text
extraction returned its entire correct content — a text-only gate passed
outright on a UI nobody could see. Never accept a passing text extraction as
proof of visibility. Pair it with rung 5 (an actual rendered capture) for
anything involving an overlay, a modal, a sheet, or any container whose
visibility depends on a style class rather than DOM presence.

## Assert against actual DOM order, not spec prose

Widgets vary in whether they render a value before its label or after.
Verify the actual order empirically per widget type before writing an
assertion against it — do not trust a spec's description of the order.
`[VERIFIED]`

## Locate by element identifier, not by visible text

`[VERIFIED]` Container widgets that render multiple panes (e.g. a tabbed
container) commonly render every pane into the DOM regardless of which one is
currently active. A text match for a label can hit an inactive pane's
duplicate label before it hits the intended active one. Locate elements by a
specific, stable identifier (an id, a data attribute, a structural path) —
never by matching visible text alone.

## Screenshot comparison against a reference design

Comparing a live screen against a reference design (mockup, spec image,
prior signed-off screenshot) is high-value and catches classes nothing else
does — see the matrix. When the comparison surfaces a recurring component
pattern that is wrong across several screens (a card layout, a badge style, a
chip variant), fix the pattern once at its source and propagate the fix,
rather than re-deriving and re-fixing it per screen. Re-deriving per screen
both wastes turns and risks drifting the fix between screens.
