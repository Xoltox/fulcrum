# Mentor prompt scaffolds

Verbatim-generalized templates from measured turns, plus the phrasings that
measurably failed. Fill in the bracketed placeholders; keep the rest as-is —
the exact wording is part of what made these work.

## What worked

**Scope fence** — put at the top of every build/fix turn:
> "Scope of this turn: create exactly ONE new `<thing>` named `<name>` and
> nothing else. Do not create any other action, endpoint, structure or
> resource. Do not modify any existing element — in particular do not touch
> `<pre-existing elements, by name>`."

**Question 0 — the staleness stop-gate.** [VERIFIED] The single
highest-value fragment in the source corpus: it has caught a stale session
before any write. Put it at the top of every step's *first* turn, with the
invariant drawn from the previous step's own verified output (an element
name plus a count), phrased so a wrong answer stops the run:
> "Question 0, answer this before anything else: how many `<X>` does
> `<screen/entity>` have, and does an element named `<Y>` exist? If the
> answers are not `<expected count>` / YES, say so plainly and STOP — do not
> answer anything else and do not make any change."

If it reports the stale state: discard the session, open a fresh one. A
revision-number check does not catch this — the revision still advances
under a stale publish.

**READ-then-MIRROR** — the highest-leverage *layout* phrasing measured.
[VERIFIED] Landed 3 for 3 first try on one step, and extended to 4 for 4
across two consecutive steps, including matching the visual result of
sibling panes with no extra correction turn:
> "FIRST: READ the existing `<sibling element / pane>` and report exactly
> how it is built. Then MIRROR that construction exactly. Do NOT modify
> `<the sibling>` — read only. Report the verbatim expression you copied."

For a *behavioral* pattern rather than a visual one, name the mechanism
Mentor already described back at it, from an earlier read-only turn:
> "MIRROR the mechanism `<element>` already uses, which you described to me
> earlier as: `<paste Mentor's own words from the read-back>`."

**Read the block first** — establishes real input contracts before binding
anything to them:
> "FIRST: read the UI block `<Block>`'s input parameters and report them
> verbatim (names + data types). Bind `<input>` as `<type A>` if that is its
> type; if it expects `<type B>`, adapt the formulas accordingly and say so."

**Pre-authorized scope cut** — removes the incentive to fake a result when
the preferred path turns out to be unavailable:
> "(b) If `<preferred route>` is possible, do that. (c) If it instead
> requires `<the thing being avoided>`, STOP and apply this PRE-AUTHORIZED
> SCOPE CUT instead: `<explicit fallback>`. Do NOT invent or hardcode any
> number in the fallback."

**Mandatory placeholder cleanup, with the repeater exemption** — a container
block's default children are not all placeholders:
> "After creating EVERY widget/block instance, inspect its children in the
> model tree and DELETE every default/placeholder child. EXEMPTION: a
> repeating container's default content child (e.g. a Gallery's `List`) is
> the REPEATER, not a placeholder — KEEP it. Before deleting any default
> child, ask whether it REPEATS or POSITIONS anything; if it does, keep it
> and tell me."

**State a repeater's required END STATE, not just its binding:**
> "The end state MUST be: `<container>` → a repeating widget in its content
> placeholder with `Source` set to `<Aggregate>.List` → item template → your
> content. The repeating widget the container ships with is the REPEATER,
> not a placeholder — do NOT delete it. Quote its `Source` property back to
> me by name."

**Lead a fix turn with the measured symptom, then the hypothesis, then an
escape hatch** — stops a confidently-worded wrong diagnosis from becoming a
second defect:
> "It renders exactly `<observed>`, not `<expected>`. The first item holds
> the correct data, so the source and bindings are correct but nothing is
> ITERATING. If your read shows the cause is something OTHER than
> `<hypothesis>`, say so plainly and fix the real cause instead. Do NOT
> apply a speculative fix on top of a wrong diagnosis."

**No silent substitution, with an exact-count demand:**
> "If any identifier / icon name / CSS class does not resolve, STOP and tell
> me which one — do NOT substitute silently. This turn must end with 0
> validation errors; report the exact validation error count for the whole
> application."

**Verbatim read-back:**
> "Then read all `<N>` back and quote every `<property>` VERBATIM. Confirm
> the substring `<known-wrong value>` appears in none of them. Report the
> exact validation error count."

**State the consequence, not just the requirement:**
> "BOTH `<A>` and `<B>` are mandatory — `<A>` carries the geometry and `<B>`
> is variant-only, so `<B>` alone renders as `<the broken visual result>`."

**Restate a known trap as a load-bearing constraint**, at the top of any
spec that touches it:
> "Non-negotiable constraint, restated because it is load-bearing: `<trap
> description>`. `<the concrete rule that avoids it>`."

**Explain WHY a constraint exists** — visibly stops Mentor substituting its
own approach:
> "WHY `<constraint>`: `<mechanism>` — `<the concrete failure this
> prevents>`."

**Confront a false success report** — the only phrasing that has landed a
delete Mentor previously claimed to have already done:
> "Your previous turn reported it deleted `<X>`, but the deletion did NOT
> land: `change_applied` was false / the live app still shows it. Do not
> tell me it is already gone — verify against the model and actually remove
> it. If it cannot be performed, say so plainly and name the obstacle rather
> than claiming success."

**Restate the invariant every single turn**, not just once at the start of a
multi-turn step:
> "Do NOT change `<invariant>` (must stay `<exact value>`)" — plus, in the
> read-back demand: "confirm `<invariant>` is still `<exact value>`."

**Self-audit turn:**
> "Verify — do not just assume — every item of the checklist below against
> the CURRENT app state by reading the model back item by item. If any item
> fails, fix it now, additive only: never rename/retype/delete a
> pre-existing element."

**The order IS the point** — for a turn where sequence, not content, is the
risk:
> "THE ORDER IS THE WHOLE POINT OF THIS TURN." + an explicit numbered step
> list + "do not reorder, do not merge steps, do not add a branch" + a
> read-back demand that names the exact ordering to prove.

**Character-by-character format read-back** — turns an invisible formatting
defect into a checkable claim:
> "Read the format string back CHARACTER BY CHARACTER and state exactly what
> it will render for input `<concrete example value>`."
Pair with the mechanism ("the `M` token is consumed as the month, not the
minute") — an example of desired output alone is not a specification (see
below).

**Overrule the attractive-but-wrong construct** pre-emptively:
> "If you think `<tempting construct>` would be cleaner, you are wrong for
> this platform; build `<the thing actually wanted>` instead."

**Bound a fix turn to an exact property count:**
> "Confirm you changed exactly `<N>` propert(y|ies) and list every property
> you touched." When clearing rather than setting: "CLEAR the property to
> empty. Do NOT substitute a different value."

**Clean up after a turn that claimed no change:**
> "Your previous turn reported `change_applied: true` while telling me it
> made no change. FIRST inspect for any partially-created element named
> `<X>`, `<Y>`, `<Z>`; if any exists, DELETE it and start clean."

**Pre-flight a UI block by name** — cheap, and would have saved a whole
turn when skipped:
> "Does the block `<Block>` exist in this application's referenced UI
> library? If not, list the blocks that DO exist with a similar purpose and
> their input parameters and events, and STOP."

## What failed — know these too

- **Specifying a date filter as an inequality pair** (e.g. "from today,
  before tomorrow") — reasonable in prose, platform-invalid, silently worked
  around into something else.
- **Giving an exact format string with no render-back demand.** Without the
  character-by-character read-back above, the defect stays invisible.
- **Giving only an example of the desired output** (e.g. "renders like
  `11.00 AM`") as the sole statement of intent — Mentor picked a token
  combination that satisfies the description in the model but not the
  actual render. An example is not a mechanism.
- **Gating a pre-flight question on "did you make a change."** A read-only
  prompt correctly reports no change — don't make the pre-flight's answer
  conditional on that.
- **Asking Mentor to report live row values from the database.** It cannot
  answer this reliably; verify through the render or a diagnostic endpoint
  instead.
- **Naming a UI block in a spec without pre-flighting it in the same step.**
  An absence answer from a previous step is a snapshot, not a fact — it can
  be wrong, and it can go stale. Re-run the one-line pre-flight every step
  that uses the block, even if a prior step already asked.
- **Specifying a visual treatment by class name rather than by outcome.**
  Telling Mentor to set a specific CSS class name got exact compliance and a
  broken overlay, because the class conflicted with positioning Mentor
  couldn't see from the name alone. Ask for the outcome ("give it an opaque
  surface with rounded top corners; report what you used") and let it
  notice the conflict.
- **Asking whether an icon name is valid.** Mentor cannot answer this
  reliably — verify by looking at the rendered icon, not by asking.
- **A blanket "delete every default/placeholder child" rule with no
  exemption.** Correct for most container blocks; actively destructive for
  a repeater's own default content child, which it deleted silently, twice,
  with every signal green. Never call a widget's default child a
  "placeholder" in a prompt unless you have checked that it neither repeats
  nor positions anything.
- **"Mirror the thing you just built" (rather than a signed-off sibling).**
  Cheap and exact, and it mirrors defects with the same fidelity — this is
  how one repeater bug propagated into a second instance for free. Only
  mirror something already verified in the render.
- **Carrying a block-absence answer forward across steps.** A block
  recorded absent in one step was found present and public a step later.
  Re-run the pre-flight; do not cache the answer.
