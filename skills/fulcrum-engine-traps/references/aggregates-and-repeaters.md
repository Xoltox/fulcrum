# Aggregates and repeaters

Screen aggregates bound to `.List`/`.List.Length`/`.List.Current.<attr>` are
the most reliable data-read construct on the platform — lean on them over
Server Actions wherever the shape allows. The traps below are the exceptions.

## 1. Gallery/List collapse — the most expensive trap in this registry `[VERIFIED]`

**Failure mode.** A `Gallery` block does not iterate by itself. It ships a
`List` widget inside its `Content` placeholder — that `List` is the actual
repeater, with `Source` bound to `<Aggregate>.List`. If that `List` is
deleted (most commonly by an over-broad "delete default placeholder
children" instruction) or never given the right `Source`, the screen still
renders: `.List.Current` resolves to the first row of the aggregate when it
sits outside any repeater, so exactly **one card renders, with every
binding correct**.

**Visible to validation/publish?** No. 0 validation errors, `change_applied:
true`, clean publish. Only the render shows a 1-card screen where N were
expected.

**Required end state, state it explicitly in the build prompt:**
> "End state MUST be: `Gallery` → a `List` widget in its `Content`
> placeholder with `Source` = `<Aggregate>.List` → `ListItem` → your card
> content. The `List` the Gallery ships in `Content` is the REPEATER, not a
> placeholder — do NOT delete it. Quote its `Source` property back to me by
> name."

**Diagnosing after the fact:** if a repeater renders exactly one card and
that card's data is the correct first record, the aggregate and bindings
are right and nothing is iterating — look for the missing/misdirected
`List`, don't touch the aggregate. State the measured symptom before the
hypothesis, and give an escape hatch: "if your read shows the cause is
something other than the missing `List`, say so and fix the real cause —
do not apply a speculative fix on top of a wrong diagnosis."

**A list widget contributes non-row sibling DOM nodes** `[SINGLE-OBSERVATION]`
— asserting "parent child count == row count" fails even on a correctly
built list, because the list contributes its own wrapper nodes alongside
the rows. Scope any DOM-count assertion to the row container specifically,
not the parent.

## 2. On-demand aggregate refresh wiring `[VERIFIED]`

**Failure mode.** A dependent aggregate inside an accordion, expander,
modal, or action-sheet defaults to `Fetch = AtStart`. It executes once
against a null filter/identifier at screen load and never fires again — the
panel renders permanently empty behind a correctly-wired toggle.

**Visible to validation/publish?** No.

**Fix, and the phrasing that works:**
> "`Fetch = OnDemand` plus an explicit `RefreshData` node in the toggle
> action."

Stronger, if a proven sibling exists: name it and say mirror it verbatim —
"MIRROR the existing proven pattern: `<Sibling>` already has `<X>` with
`Fetch=OnDemand` refreshed by a `RefreshData` in `<action>`. READ that and
construct the new one the same way. Read-only on the sibling." Naming a
concrete sibling to copy is measurably more reliable than stating the rule
alone.

## 3. Join direction, unasked `[VERIFIED]`

**Failure mode.** Given "chart the waybills [child] against routes
[parent]", Mentor's natural join is child-LEFT-JOIN-parent — the direction
that silently drops the parent rows with zero matching children. A route
with zero orders/shipments never appears in the chart.

**Visible?** No — clean aggregate, clean chart, fewer categories than exist.

**Fix:** name the *driving* entity explicitly before describing the join —
state "chart `<parent>`, LEFT JOIN `<child>`", not "chart the `<child>`
records". A defect built this way is not reliably fixable by a patch turn
on the same aggregate; two fix attempts on one build failed and it took a
full aggregate rebuild to close. Ask what is actually bound before
prescribing any fix.

## 4. Join type, unasked `[VERIFIED]`

**Failure mode.** Told to "join `<related entity>`", Mentor picks `Inner`
by default. A row whose FK is null vanishes from the list entirely — no
error, clean publish.

**Fix:** always name the join type as well as the join condition: "use a
Left join, because a row with a null FK must still appear" or "an Inner
join is correct here because every `<parent>` row has a `<child>`."

## 5. A single OR-expression must be one filter `[VERIFIED]`

**Failure mode.** Splitting an OR-condition across two separate aggregate
filters silently changes the logic: separate filters are ANDed together,
not ORed, and the aggregate returns fewer/zero rows.

**Fix:** "Put the whole OR-expression in a SINGLE filter — do NOT split it
into two, because two separate filters are ANDed together and that breaks
the logic."

## 6. `Div()` is not a valid function `[VERIFIED]`

The validator rejects `Div()` outright as an unknown identifier — this one
at least IS visible, as a validation error. Use truncated integer division
instead (the platform's native division operator on integer operands).

## 7. Static-entity state through a joined attribute, not a second aggregate `[SINGLE-OBSERVATION]`

If you need to compare a row's state against a static-entity ordinal
(e.g. "has this row passed milestone N"), join the static entity into the
existing aggregate and compare the joined attribute (e.g. its sort-order
column) against a literal — this needs no separate aggregate over the
static entity at all, and is cheaper and simpler.

## 8. Max Records on a screen aggregate `[TENANT]`

Some tenants reject an empty "Max Records" value on a screen aggregate.
Check `tenant-profile.md`; if unset, probe once and record a safe explicit
value (e.g. a large integer) rather than leaving it blank.

## 9. Hand-wired JSON/record loaders can publish clean with an empty payload `[VERIFIED]`

**Failure mode.** A `JSONDeserialize` → `ForEach` → `CreateOrUpdate` loader
can publish with 0 validation errors while `CreateOrUpdate.Source` is bound
to an empty record literal (`{ }`) instead of the populated loop variable —
every field and FK on every row silently blank.

**Visible?** No — clean publish, 0 errors, rows exist in the entity with
every field null/default.

**Fix:** state as a load-bearing constraint at the top of the spec, and
demand the exact read-back: "`CreateOrUpdate<X>.Source` is the populated
local record variable, not a literal — read it back and confirm."

## 10. Idempotency anchor for a re-runnable loader/orchestrator `[VERIFIED]`

Guard pattern: aggregate on an anchor entity → `If .List.Empty = False` →
End (no writes) is reliable, but only if the anchor entity is actually
empty on first run. Anchors that already hold rows from an earlier step
short-circuit the loader permanently and silently on every call. Name the
anchor explicitly and say why any more "obvious" candidate is wrong for
this run.
