# Step spec template

Copy per step to `specs/step-<NN>-<slug>.md`. Replace every `<…>`. Delete no section — an
empty section is itself information, so write "None" rather than removing it.

A good spec reads as an **executable test plan**, not a design brief. Reference corpus:
specs that worked ran 168–226 lines. `[SINGLE-OBSERVATION]` Well below that usually means
judgment calls were left to the build agent.

The spec must be **self-sufficient**. The build agent reads this file and nothing else.

---

## Step \<NN\> — \<short title\>

**Phase:** \<phase number and name\>
**App:** \<exact target app identifier from tenant-profile.md\>
**Scope:** \<one sentence: what exists when this step is done\>

**NOT covered by this step:** \<enumerate. Every adjacent thing a reasonable agent might
think belongs here and does not. This section prevents scope creep more effectively than
any instruction to avoid it.\>

**Depends on:** \<step numbers whose output this step reads. State what it reads, not just
the number.\>

---

## Resolutions

Judgment calls, decided here so the build agent never has to guess. One line each:
the ambiguity, then the decision.

Anything genuinely ambiguous in the source that this step touches goes here. An ambiguity
left unresolved becomes an improvisation, and an improvisation becomes a fix turn.

- \<Ambiguity\> → **Decided:** \<decision\>. \<one-clause reason\>
- \<…\>

**Do not re-litigate these.** If a resolution turns out to be wrong, halt and report
rather than substituting a different decision mid-step.

---

## Invariant pre-check — halt if any fails

Read the current state and confirm each before making any change. **If any check fails,
stop and report. Do not attempt a fix and do not proceed.**

1. \<Precondition, stated as something observable\> — expected: \<observation\>
2. \<…\>

Rationale: a step that starts from an unexpected state produces damage that is more
expensive to unwind than the step was to run.

---

## Standing rules for this step

\<Restate inline, generated from the single rule source — never hand-edited. The build
agent must need no other file. Include at minimum:\>

- Tenant facts that apply here, quoted from `tenant-profile.md` with their values.
- The fix-turn cap and the halt condition.
- The proof obligation: what counts as evidence this step landed.
- Any construct-level prohibition relevant to what this step builds, **each with its
  failure mode stated** — a bare "do not" does not stop the failure recurring.

---

## Turn \<n\> — \<what this turn produces\>

One block per turn. Number them. Each element in the turn gets all four parts.

### \<Element name\>

**VISUAL LAYOUT**
\<Widget tree, nesting, and the style-class slot per node. Name real platform UI blocks,
never a generic container plus custom CSS. State widths, spacing and alignment where they
are load-bearing.\>

**DATA FLOW**
\<Entities and attributes only. State which entity, which attributes, and the filter or
sort in domain terms.

**Never name an aggregate, a screen action, or a local variable.** Naming implementation
constructs makes the build agent construct them to match the name rather than to match
the need, and the resulting model diverges from the platform's own conventions.\>

**FUNCTIONAL BEHAVIOR**
\<What responds to what. For a display-only element write "Display only — all values live
from entity data, loaded on entry", explicitly. A missing behaviour statement is read as
"static", and the agent hardcodes text.\>

**PRESENTATION ORDER**
\<The order elements appear in the rendered output, top to bottom. Disambiguates a widget
tree that reads ambiguously.\>

### \<Next element\>

\<…\>

---

## Turn \<n+1\> — \<…\>

\<…\>

---

## Non-goals

Explicit. Not aspirations deferred, but things this step must **not** do:

- \<Non-goal\>
- Cosmetic parity beyond what the acceptance checklist asserts. A cosmetic gap is never
  worth a capped turn.
- \<…\>

---

## Acceptance checklist

Numbered, individually verifiable assertions. Every item must be checkable by looking at
something — a rendered screen at a stated viewport, a specific string in the output, a
count, a response value.

**No item may say "should look right", "renders correctly", or "works as expected".**
Those are unfalsifiable, so they always pass.

1. \<Assertion\> — verified by: \<screenshot at \<viewport\> showing \<what\> / the value
   \<x\> in \<where\> / a count of \<n\> \<of what\>\>
2. \<…\>

Each item names its instrument. Which instrument catches which defect class:
`../../fulcrum-verification/SKILL.md`.

---

## Done when

Every acceptance item passes, and \<the state that makes this step demoable\>.
