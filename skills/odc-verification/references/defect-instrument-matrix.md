# Defect-to-instrument matrix

Generalised from a multi-week ODC build's logged defects. Every row is a real
defect, attributed to the cheapest instrument that actually caught it, and to
what cheaper checks were blind to it. Read this before designing a
verification pass — it tells you where to spend effort. `[VERIFIED]` unless
marked otherwise; several rows are `[SINGLE-OBSERVATION]` because the source
build hit them once.

| Defect class | Only caught by | What cheaper checks missed |
|---|---|---|
| Auto-numbered static-entity Ids that only fail at deploy time | The platform's own deploy-time error, surfaced via the revision/deploy history query | 0 validation errors — validation is not a deploy gate |
| Seed/loader actions writing blank rows or null foreign keys | Running the action, then reading the written rows back | A clean publish with 0 validation errors |
| A permanently empty nested list panel | Click-through / interaction test | Screen renders fine; the panel is simply empty and nothing static sees that |
| Whether a CRUD action actually persisted | click → reload → confirm (rung 6) | Any confirmation banner shown immediately after the click |
| A destructive action behind a native confirm dialog silently doing nothing | Registering a dialog handler before the click, then reload + re-verify | The click "succeeds" with no error, because an unhandled dialog is auto-dismissed by the driver — the harness itself lied |
| A monolithic turn that applied nothing | A read-only model inventory probe | The turn's own run-status lookup, once the run record is evicted or summarized away |
| A natural key wired to the wrong source field | Verbatim model read-back against the actual source resource, in a small isolated turn | Would publish clean while producing rows with a null foreign key |
| A value wired to a response header instead of the response body | The live response body plus an explicit header dump on the same call | The body simply omits the value — the platform drops falsey/absent values from response bodies with no signal |
| A delete that did not actually land | The live endpoint result plus the revision number NOT advancing | Mentor's own "deleted" summary; a change-applied-style flag reading green |
| Row-level data correctness at any point Mentor has no live-data path | A temporary diagnostic REST endpoint returning plain data (see `diagnostic-endpoint.md`) | Model read-back — structurally blind to runtime data |
| Whether seeded values propagate to a dependent screen | Cross-reading an already-verified screen that consumes the same data | Nothing cheaper — an already-verified screen is a row-level assertion you already own |
| Wrong function used for a "current moment" value (e.g. a live clock function instead of a fixed reference date) | Verbatim model read-back, demanded explicitly in the prompt | Would render plausible-looking numbers and pass any text-based check |
| An invalid type comparison in a filter expression | Validation error count | — one of the few cases where a model-level gate does the actual work |
| Unwanted extra default child nodes on a chart/list-type widget | Model read-back | No cheaper method exists |
| Corrupted formatted-text rendering (e.g. a meridiem/format-token bug) | Screenshot only | Model read-back showed the format string looking correct; validator 0 errors; publish succeeded — even a naive text match would have failed as a missing match, not pointed at a cause |
| A multi-character value breaking across two separate DOM nodes | Screenshot only | A text-based check sees the full string present in the DOM and is satisfied |
| Elements rendered full-bleed or clipped off-screen | Screenshot, repeatedly | — |
| Blank repeated rows inside an accordion/list container | Screenshot only | A text check cannot see an empty row — there is no text to be absent |
| Placeholder caption text shipped to a production screen | Screenshot, found many turns after it shipped | A text-gate reported a full, plausible character count throughout; the wrong keyword was being searched for |
| An unthemed native control left unstyled | Screenshot only | — |
| Multiple visual defects on a screen that scored perfectly on a text/structure gate | A full visual pass | The screen was signed off at a perfect text-gate score first |
| A broken chart (label count and bar count mismatched) | Screenshot | — |
| Mid-word text breaks; a floating element overlapping a card; content cut at a scroll boundary | Screenshot | — |
| A model behind the actually-deployed revision, so a build turn silently reverts already-completed work | The orchestrator's own independent revision/aggregate/widget-count query, asked as the FIRST question of a session, before any mutating turn | Nothing downstream — the subsequent publish reports success with an ADVANCING revision even while reverting prior steps; this is the one class no other rung catches in time `[SINGLE-OBSERVATION, but recurred twice in the same build]` |
| A change-applied-true turn that actually created a partial/orphaned object | Model read-back, demanded explicitly in the retry turn | A change-applied flag alone — true but not actionable on its own |
| An overlay collapsed to a near-zero-height strip by a style override | Screenshot, then inspecting the computed style directly | Model read-back correct; validator 0 errors; publish succeeded; AND full text extraction returned the overlay's entire correct content despite it being invisible — text extraction is blind to visibility, full stop |
| A label breaking mid-word inside a constrained container | Screenshot | Every character was present, in order, in the text extraction |
| A low-contrast icon/text variant on certain backgrounds | Reading the bound class's candidate variants directly in the stylesheet, before publishing | Nothing — this is the one genuinely cheap pre-publish win; do it routinely whenever a bound class expression selects between variants |
| A repeater whose default child was deleted, rendering exactly one item instead of the full set | A rendered row-count assertion, compared against an expected count derived from elsewhere in the live system | Model read-back clean; 0 validation errors; change-applied true; publish succeeded twice; AND a text check matching each expected string once would ALSO pass — a one-row list is textually indistinguishable from a correct list when the one visible row happens to be right. Believed to be the single defect class no non-visual signal can catch even in principle |
| Missing styling on an overlay's body, letting the page show through it | Screenshot | Text and structure both look perfect |
| Low-contrast link-styled text on a colored background | Screenshot | A text check reads the correct string out of the DOM successfully — correctness of content says nothing about legibility |
| A stale hardcoded expected count or value in a test fixture | Cross-reading against live data, not the platform | A text/screenshot gate flags it as a NEW app defect rather than a stale fixture |

## Conclusions

1. A green text-only check says nothing about whether the app looks right.
   Fully green structural/text scores have coexisted with broken charts,
   escaping-character leaks, values in the wrong slot, missing dates,
   overlapping elements, unthemed controls, and mid-word text breaks.
2. Anything that renders a **formatted** string needs a visual check.
   Counts, filters, identifiers and structure can be model-read-back correct
   on every turn while formatting is exactly where the render disagrees with
   the model.
3. Verify structure at the model layer, data over an API/endpoint, and
   appearance in an image. Each is blind to the other two — this is not
   redundancy, it is coverage.
4. The failing assertion is often the fixture, not the app. Audit a new
   assertion by negative-testing it (confirm it fails when you feed it a
   value you know is wrong) before trusting it to pass.
5. The only durable row-level data path costs extra turns and a publish —
   budget seed/data-correctness steps for that cost explicitly.
6. The shape to fear most is a repeater that does not repeat. Ship every
   list, gallery, or repeater with a row-count assertion whose expected value
   is derived from elsewhere in the live system — never hardcoded on both
   sides of the comparison.
7. A capture/verification harness needs its own verification. A "full page"
   capture can silently crop at a boundary that is not the app's real scroll
   container, corrupting every screenshot taken before the bug is found — see
   `visual-verification.md`. A verification tool can have a silent no-op bug
   exactly like the app under test can.
