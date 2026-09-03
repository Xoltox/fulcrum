---
name: fulcrum-engine-traps
description: >
  Construct-indexed registry of known OutSystems ODC / Mentor engine traps —
  ways a screen, aggregate, widget or integration publishes with 0 validation
  errors and a clean deploy while being functionally broken. Use before and
  during any turn that builds or edits a screen, aggregate, repeater, link,
  icon, date expression, REST integration, static entity, chart, or overlay
  in ODC. Trigger phrases: "building a screen in ODC", "add an aggregate",
  "my aggregate returns one row", "the gallery only shows one card", "the
  icon isn't rendering", "the link is overflowing its box", "Mentor built it
  but it looks wrong", "why did this render empty", "REST is dropping a
  field", "wire up a wizard/chart/action sheet/dropdown".
version: "1.0.0"
requires: >
  A construct to check against this registry; tenant-profile.md present or
  in progress for tenant-varying facts (icon font, UI-block availability,
  meridiem tokens, db_query liveness).
---

# ODC engine traps

A lookup table, not a procedure. Every entry here is a construct that Mentor
can build, validate, and publish cleanly while it is **functionally wrong**.
That is the defining shape of every trap in this registry: **validation and
publish are not proof of correctness.** For the instrument that actually
proves correctness, see `../fulcrum-verification/SKILL.md`. For turn sizing and
prompt-length limits, see `../fulcrum-mentor-turns/SKILL.md`. For loading seed
rows, see `../fulcrum-seed-data/SKILL.md`. This skill owns none of those — it
owns "does this construct have a known failure mode, and what is it."

## How to use this file

1. Before a turn touching a construct below, read the matching reference
   file and restate the mechanism (not just the ban) in the Mentor prompt —
   see `../fulcrum-mentor-turns/SKILL.md` for prompt-shaping.
2. After a turn lands, verify against the trap's stated failure mode, not
   against `change_applied` or a clean publish — see the "Visible to
   validation?" column on every entry. If it says "no", validation and
   publish tell you nothing.
3. Tenant-varying facts (`[TENANT]`) are never asserted here. Check
   `tenant-profile.md` first; if the fact isn't there yet, probe for it.

## Front-loaded: the four traps that cost the most

Measured across the 47-step reference build. An agent that internalizes only
this table already avoids the majority of fix-turn overruns.

| Trap | Failure mode | Visible to validation/publish? |
|---|---|---|
| **Aggregate/repeater collapse** (16 steps hit this — the single most expensive trap class) | Deleting a `Gallery`'s default `List` child, or omitting it, collapses the repeat to one row: `.List.Current` resolves to the first record with no repeater around it. Screen renders exactly one card, every binding correct. | No — 0 validation errors, clean publish, `change_applied: true`. |
| **Link needs an explicit block display** (11 steps) | A link widget defaults to `display:inline`. Wrapping a card/tile in one makes it overflow its own padding box, and restyles the wrapped text to link color. | No — DOM text and bindings are all correct; only the render shows it. |
| **REST silently drops falsey values** (9 steps) | An Integer `0` or Boolean `False` output vanishes from the JSON response body entirely. "Zero" becomes indistinguishable from "field never set." | No — clean publish; only inspecting the actual response body shows it. |
| **No model-layer path to live row data** `[TENANT]` (9 steps) | On tenants where the raw-row-read path is dead, asking Mentor to inspect live data returns a plausible, fabricated-looking answer with no error. | No — Mentor reports success/an answer either way. |

Two more, just below that threshold, worth knowing before any build session:

| Trap | Failure mode | Visible? |
|---|---|---|
| **On-demand aggregate refresh wiring** (7 steps) | A dependent aggregate defaults to `Fetch = AtStart`: it runs once against a null filter at load and never re-fires inside an accordion/modal/sheet. Permanently empty panel. | No. |
| **Default placeholder children shipped on new widgets** (7 steps) | Every new widget/block ships default children Mentor never mentions unless asked. Some are decorative (delete them); some — a `Gallery`'s `List` — are the repeater itself (deleting is the collapse trap above). | No. |

And the meta-trap behind all of them:

| Trap | Failure mode | Visible? |
|---|---|---|
| **Zero validation errors catches no logic defects** (6 steps, and implicitly behind every row above) | "0 validation errors" and "publish succeeded" are syntax/type-checker signals only. None of the defects in this registry raise a validation error. | N/A — this is the reason the others aren't visible. |

## Two corrections to carry, not the blanket forms

**"Delete every default placeholder child" is wrong as a blanket rule.**
Before deleting any default child, ask: **does it REPEAT anything, or
POSITION anything?** If yes, it is structural, not a placeholder, and
deleting it produces the collapse trap above. If no (a stray text node, a
literal button, empty accordion items, chart add-on blocks), delete it.
"Default" and "placeholder" are not synonyms.

**"If Mentor says a UI block does not exist, believe it" is retracted.** An
absence answer was later found to be wrong — the block existed and was
public. Treat any "`<Block>` does not exist" answer as unproven; defer to
the tenant-profile probe or re-probe live, in the current step, before
committing a spec to that absence.

## Mentor's default instincts — steer these before they fire

These aren't construct traps but the root cause behind several of them.
Each is predictable, so each is preventable with the phrasing shown.

| Instinct | What it does | Phrasing that steers it |
|---|---|---|
| Silent substitution on error | Hits a type/validity error, quietly swaps in a different construct, reports success | "If any identifier/expression does not resolve, STOP and tell me which one — do NOT substitute silently. Report the exact validation error count." |
| Ships default placeholders unmentioned | Never volunteers a new widget's default children | "After creating this widget, inspect its children and report every default child by name before deciding what to delete." |
| Wrong join direction/type, unasked | Picks the join shape that matches the surface phrasing, not the data need; defaults join type to `Inner` | Name the driving/anchor entity explicitly, and name the join type explicitly — "LEFT JOIN from `<driving entity>`", "use an `Inner` join" or "`Left` join, because a row with a null FK must still appear." |
| Mirrors a nearby sibling instead of a stable rule | Copies whatever pattern is visually/structurally nearby, correct or not | Only ever say "mirror `<X>`" once `<X>` is verified in the render. Mirroring an unverified sibling propagates its defect. |
| False success on deletes | Reports "deleted ✓" from a thrown not-found exception that fired for an unrelated reason | Never trust a delete's self-report. Confirm via revision number advancing and the live artifact (`swagger.json`, endpoint status) actually being gone. |
| Hedged inference presented as observation | "confirmed via `<indirect signal>`", "as evidenced by", "this implies" — all mean inferred, not read | Ask for the property BY NAME and demand it be quoted back verbatim. Treat "confirmed via X" where X isn't the property itself as unverified. |

## Routing table — construct to reference file

| Construct / symptom | Open |
|---|---|
| Aggregate returns one row; Gallery/List collapse; on-demand refresh; join direction/type; OR-filters; `Div()`; list child-count assertions | `references/aggregates-and-repeaters.md` |
| Link wrapping a card overflows; link restyles wrapped text; container has no click event; wizard step wiring | `references/links-and-navigation.md` |
| Icon renders empty/wrong; icon bound per-row; glyph naming; CSS class order fights a utility class; `Style` vs `CustomStyle`; theme CSS vars | `references/icons-and-theming.md` |
| DateTime vs date comparisons; `CurrDate()`/`CurrDateTime()`; meridiem formatting; inline `If()` not short-circuiting | `references/dates-and-expressions.md` |
| REST output silently dropped; Boolean wired as a header; no live-row-data path; Server Action can't be Public; hand-wired JSON loaders | `references/rest-and-integration.md` |
| Static entity referenced by label vs identifier; sequential Ids; dual FKs to the same entity | `references/static-entities.md` |
| Action sheet / modal / bottom sheet / sidebar existence; wizard mechanics; dropdown shape; chart per-bar styling; donut center label | `references/overlays-wizards-charts.md` |

## Evidence tags

`[VERIFIED]` repeat-observed in the source build. `[SINGLE-OBSERVATION]` seen
once. `[UNVERIFIED]` inferred/reported, never confirmed. `[TENANT]` belongs in
`tenant-profile.md` — do not hardcode the answer, probe it.
