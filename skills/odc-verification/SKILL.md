---
name: odc-verification
description: Proves that a change to an ODC app actually landed and actually works, rather than trusting that the platform said so. Owns proof obligations, which instrument catches which defect class, visual capture and comparison, the diagnostic REST endpoint pattern for live data, and what the platform's own success signals do and do not mean. Use when asked to verify a change landed, "did the publish work", "check the screen renders correctly", "prove the data is right", "regression check my ODC app", or before marking any build step done.
version: "1.0.0"
requires: ODC MCP surface for model read-back and revision queries (context_*, app_revisions); a browser automation capability for visual and interaction proof (a browser MCP tool where the harness has one, a headless browser driver such as Playwright otherwise); a scripted HTTP client for API-level ground truth; ability to stand up a temporary diagnostic REST endpoint when tenant-profile.md shows no live model-layer path to row data.
---

# odc-verification

## Boundary

This skill owns **proof**, not cause. For why a construct breaks, see
`../odc-engine-traps/SKILL.md`. For turn/session mechanics, see
`../odc-mentor-turns/SKILL.md`. For seed loaders and idempotency, see
`../odc-seed-data/SKILL.md`. If you find yourself explaining *why* a widget
misbehaves, stop and cross-reference instead of writing it here.

## The central problem

The platform's own success signals are unreliable in **both directions**, and
model-layer checks are structurally blind to whole defect classes.

- A `change_applied`-style flag can read true on a turn that changed nothing,
  and a no-change flag can appear on a turn that did land a change. `[VERIFIED]`
- Zero validation errors and a clean publish are compatible with blank rows,
  an empty record source, a repeater rendering exactly one item, an icon
  rendering nothing, a collapsed overlay, corrupted formatted text, and
  overflowing content. `[VERIFIED]`
- Mentor's own read-back and arithmetic over live data are not trustworthy —
  it has misreported row counts, claimed an escaped character was correct
  when doubled, and claimed a rendering fix worked while the DOM still showed
  the defect. `[VERIFIED]` It cannot read live row counts or run arithmetic
  over live data at all; that is runtime state, not model state. `[VERIFIED]`
- Mentor cannot read a numbered publish revision — it sees only internal
  model-save digests. An independent revision query is the only source of
  truth for what is actually live. `[VERIFIED]`
- A publish revision number advancing is **not** proof the intended change
  landed — publishing from a stale model advances the revision while silently
  reverting completed work. `[VERIFIED]`
- The platform attributes every publish to the authenticated tenant user
  regardless of origin, so portal-made and agent-made publishes are
  indistinguishable after the fact. `[VERIFIED]`

## The proof ladder

Escalate through these rungs. State which rungs a change needs before
starting — most changes need more than rung 2. Never stop at a rung because
it came back clean; stop because the next rung is inapplicable.

| # | Rung | Establishes | Blind to |
|---|---|---|---|
| 1 | Model read-back, demanded **verbatim** (the literal property value, never a summary or paraphrase) | The model shape | Rendering, runtime data |
| 2 | Validation and publish status | Compilability | Logic, rendering |
| 3 | Independent revision confirmation via the platform's own revision query — never Mentor's prose | What revision is actually live | Whether that revision does the right thing |
| 4 | Live data ground truth (see `references/diagnostic-endpoint.md`) | Row-level correctness | Rendering |
| 5 | Rendered visual capture (see `references/visual-verification.md`) | What the user actually sees | State changes over time |
| 6 | Interaction proof: click, then reload or re-fetch, then confirm the state persisted. A confirmation banner alone is never accepted | Persistence of a state change | Nothing it claims — this is the strongest per-action rung |
| 7 | Regression sweep across the app after any shared-block change | No collateral damage elsewhere | A scoped-only run is acceptable ONLY when the change touches no shared block, and that must be justified explicitly in the report |

Demanding rung 1 verbatim matters on its own: Mentor has claimed a fix worked
while the DOM still showed the defect, and has self-corrected mid-answer on a
count. Treat any paraphrased read-back as unverified.

## Instrument selection — capability, not tool name

State the proof obligation first, then pick an instrument in this preference
order:

1. A browser automation capability native to the harness, where one exists —
   usually the most reliable, lowest-friction option for visual and
   interaction proof.
2. A headless browser driver (e.g. Playwright) otherwise, for the same
   obligations.
3. A scripted HTTP client for API-level ground truth — required for rung 4
   when there is no live model-layer query path (see
   `references/diagnostic-endpoint.md`).

Never write a rule as "use X" for a named tool. Write the obligation, then the
preference order above.

## Where the depth lives

- `references/defect-instrument-matrix.md` — the empirical map of which
  instrument actually caught which defect class, and what cheaper checks
  missed. Read this before designing any verification pass.
- `references/visual-verification.md` — the capture trap, DOM-identity vs.
  visible-text checks, tab/pane pitfalls, and comparison-against-reference
  workflow.
- `references/diagnostic-endpoint.md` — the temporary REST endpoint pattern
  for live data when there is no model-layer path, and the debt it creates.
- `references/verification-hygiene.md` — invariants over fixed values,
  independent hand-classification, full-row arithmetic checks, programmatic
  diffing, fixture-correction discipline, and subagent proof requirements.

## Non-negotiables (full detail in references/verification-hygiene.md)

- Assert invariants, never a hardcoded fixed value, for anything time- or
  data-size-dependent. Derive the expected count from elsewhere in the live
  system, never hardcode it on both sides of a comparison.
- Hand-classify expected results independently before comparing against
  rendered output — do not accept Mentor's or the agent's own classification
  as ground truth.
- Check arithmetic invariants across **every** row, not a sample.
- Compare digests and diffs programmatically, never by eye.
- When new correct data legitimately changes expected numbers, tighten the
  fixture and label it a fixture correction — never weaken or delete an
  assertion to make a gate pass.
- A subagent's report of success is not proof. Require every verification
  agent to state explicitly what it could **not** verify.
- Distinguish pre-existing known failures from newly introduced ones on every
  run; never silently absorb either into a passing report.
