# Making a requirement observable

How to turn what a user says into something an app can fail. Read this the moment an
answer is vague, aspirational, or defers its specifics.

Design guidance, `[UNVERIFIED]`.

## Why this is the interview's highest-leverage act

`../../fulcrum-gap-analysis/references/finding-classes.md`, heading "Unfalsifiable
requirements in detail", defines a requirement as unfalsifiable when two competent
reviewers with the same app could reasonably disagree on whether it is satisfied. Such
a requirement is a finding **against the document**, is excluded from every coverage
denominator, and blocks the build steps that depend on it.

So every vague line emitted here becomes, months later, either a phantom gap or a
distorted coverage figure — and by then the person who could have answered the question
in five seconds has moved on. The cheapest possible moment to fix it is the moment it
is said.

The same shape appears in `../../fulcrum-solution-init/templates/spec-template.md`,
Acceptance checklist: **no item may say "should look right", "renders correctly", or
"works as expected"** — those always pass. An unfalsifiable requirement is the upstream
source of exactly that unfalsifiable acceptance item.

## The test

Ask, silently: **what would someone see, click, read or count if this were true — and
what would they see if it were false?** If both answers cannot be stated, the line is
not a requirement yet.

## The conversion question

Put to the user, in their words, one of:

- "What would you be looking at when you decided that was working?"
- "If it were broken, what would you notice first?"
- "How many, and over what period?"
- "Who specifically, and what exactly can they change?"

Ask once. If it does not produce an observable answer, mark `undecided` and move on —
a second attempt at the same vague point spends patience for the same non-answer.

## Conversion table

| Said | Unfalsifiable because | Convert to |
|---|---|---|
| "It should be fast" | No threshold, no operation | "The `Order` list shows its first rows without an intermediate loading state on a normal connection" — or `undecided`, naming who sets the threshold |
| "The manager oversees approvals" | A named actor with no named behaviour | "Role `Manager` can open `ShipmentApproval` for any `Shipment` and set its status; no other role can set that status" |
| "It should be user-friendly" | Nothing observable at all | Usually not convertible. Mark `undecided` unless the user names a specific frustration with the current process; then convert that |
| "Handle errors properly" | No error named, no behaviour named | "When the `Customer` lookup returns nothing, the screen shows a message naming the missing customer and the save does not proceed" |
| "To be detailed later with the team" | Deferred specifics — a literal shape seen in a real BRD `[SINGLE-OBSERVATION]` | Do not convert. `undecided`, naming the team and the step it blocks |
| "Reports as needed" | Unbounded scope | Ask for one report and its columns. One named report beats an open-ended promise |
| "Everyone can see everything" | Sounds like an answer, states no rule | Confirm literally: no role restriction on any screen. Record as a decision; it is one |
| "It should scale" | No load figure | "Expect around N `Order`s per month" — or `undecided` |

## The rule that matters most

**Never substitute a plausible specific for a vague answer and write it as a
requirement.**

The temptation is strong and the result is the worst line in the brief: it reads as
`held`, it is actually invented, and the build gets scored against it later. Two
permitted moves, and no third:

1. Convert it with the user, and mark it `elicited`.
2. Mark it `undecided`, naming who decides and what it blocks.

If the interviewer proposes a specific and the user does not object, that is `assumed`
— not `elicited`, and never `held`. The distinction is the whole point of the marker.

## Negative statements are requirements too

"No one but `Manager` can change a `Shipment` after dispatch" is observable, testable,
and is the kind of line whose absence produces a security finding later. Users volunteer
positive capability and almost never volunteer prohibitions. Ask for them directly.

## Where the converted line goes

Into the brief's requirement table with its `Confidence` value, and — when the
conversion involved choosing between alternatives — a `DECISIONS.md` record naming what
was rejected. The rejected alternative is what stops the question reopening.
