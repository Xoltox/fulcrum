# Dates and expressions

## 1. `CurrDate()` cannot be compared directly to a `DateTime` attribute `[VERIFIED]`

**Failure mode.** `SomeDateTimeAttr = CurrDate()` (or any direct
date-to-datetime comparison) raises an `Invalid Expression` type error.
`>= CurrDate() and < AddDays(CurrDate(), 1)` is equally invalid despite
looking reasonable.

**The narrower, valid case:** comparing a `DateTime` attribute to a
null-date value IS valid — the trap is specifically datetime-to-date
comparison for "is this today", not every datetime/date interaction.

**Fix:** convert the DateTime attribute to a date first, then compare:
```
DateTimeToDate(SomeDateTimeAttr) = CurrDate()                      -- today
DateTimeToDate(SomeDateTimeAttr) = AddDays(CurrDate(), -1)          -- yesterday
```

**The dangerous part is the recovery, not the error itself** — see
"silent substitution" below.

## 2. Silent substitution on the type error above `[VERIFIED]`

Hitting the type error in #1, the unprompted recovery instinct is to
substitute `CurrDateTime()` for `CurrDate()` and report success. This
changes the meaning from "today" to "from this exact instant onward" —
`RequestedOn >= CurrDateTime()` renders 0 rows, not "today's rows", and
the turn reports success anyway.

**Visible?** No — the substituted expression is itself valid, so
validation and publish are both clean. Only checking the actual expression
text, or noticing the row count is wrong, shows it.

**Fix:** forbid the substitution explicitly and demand an error count:
"Do NOT substitute `CurrDateTime()` for `CurrDate()` — that silently
changes the meaning. If any expression does not resolve, STOP and tell me
which one; do not substitute silently. This turn must end with 0
validation errors — report the exact count."

## 3. An inline `Expression If()` does not short-circuit `[SINGLE-OBSERVATION]`

**Failure mode.** An inline `If(cond, a, b)` bound directly to a widget
property evaluates **both** branches before selecting one. A guard meant
to prevent a division-by-zero or a null dereference in one branch does not
protect that branch — it still evaluates, and can still throw or corrupt
the render, even though the guard condition looks correct.

**Fix:** compute the guarded value in a calculated aggregate attribute or
in an action (where a conditional *node*, not an inline expression, does
genuinely short-circuit), then bind the widget to the resulting plain
attribute — never to the inline `If()` directly when either branch is
unsafe to evaluate unconditionally.

## 4. `FormatDateTime` has no meridiem token `[VERIFIED]`

**Failure mode.** A format string containing a literal `AM/PM` (e.g.
`"hh.mm AM/PM"`) publishes clean and validates clean, but at render time
the `M` in `AM`/`PM` is consumed as the **month** token — output is
corrupted (e.g. `02.15 A8/P8` instead of `02.15 PM`).

**Visible?** No — model-invisible, screenshot-only defect.

**Fix, the only form proven correct across repeated use:**
```
FormatDateTime(dt, "hh.mm") + If(Hour(dt) < 12, " AM", " PM")
```
`hh` (12-hour hour token) is reliable on its own; only the meridiem token
is broken. A bare `tt` token is unverified — treat as untested, not safe.

**The separator character actually used must be read back from what
landed, not assumed from a spec draft** — Mentor has been observed to
"normalize" a requested separator (e.g. writing `hh:mm` when `hh.mm` was
specified) and justify it with a fabricated platform claim. Read format
strings back **character by character** and state what they will render
for a concrete sample input; treat an example of desired output ("e.g.
`11.00 AM`") as insufficient on its own — an example is not a
specification of the mechanism, and is exactly how this defect gets past
a review.

## 5. An example of desired output is not a specification `[VERIFIED]`

General form of the trap above, worth stating on its own: giving Mentor
"e.g. `11.00 AM`" as the only statement of intent leaves room for a token
choice that satisfies the description in the abstract but not in the
actual render. State the mechanism (which tokens, why) and demand a
character-by-character read-back, not just an example of the target
string.
