# Provenance

The first step, and the one that changes the meaning of every finding after it. The same
absent screen is an expected generator omission, a deliberate descope, or a regression,
depending only on how the app got here.

## What to look for, and what each source actually proves

Sweep all of these. Absence of a source is itself a finding to report.

| Source | Proves | Does not prove |
|---|---|---|
| A build or change log with per-step records | That an agentic or human build ran, and roughly what each step covered | That the step's work is still present — a later publish from a stale model silently reverts completed work (see `../../fulcrum-verification/SKILL.md`, heading "The central problem") |
| Decision or judgement-call records | That a deviation was chosen deliberately — the single strongest signal separating Drift from Gap | That the decision was implemented |
| Handoff documents | Where the last session believed it was, and what it believed was next | Anything about sessions that never wrote one |
| App revision history (`app_revisions`) | How many revisions exist, and the shape of the timeline — one revision cluster in one short window reads generator-ish; a long tail reads mature | Who or what authored anything: the platform attributes every publish to the authenticated tenant user regardless of origin, so portal-made and agent-made publishes are indistinguishable after the fact `[VERIFIED]` |
| Repo commit history | Authorship and chronology of the *specs and plans*, and often the only real named-author evidence available | Authorship of model changes, which do not pass through the repo |
| Prior gap or audit reports | What was already known, and lets this run be a delta rather than a restart | Their own accuracy — re-derive their numbers, do not inherit them |
| The requirements document's own revision history | Whether requirements moved after the build — the direct evidence for a Stale requirement | Which build sessions saw which version |

## The three shapes

**Fresh generator output.** Signals: a tight revision cluster, no per-step log, screens
that are uniform in structure, entities with default-shaped attributes, roles present but
unassigned per screen. Large gaps are the expected product. `[SINGLE-OBSERVATION]`
Report the expectation before the numbers.

**Mature project.** Signals: a long revision tail, multiple named authors in the repo,
prior handoffs, decision records, features present that no requirement mentions. Here the
prior for any deviation is Drift, Stale requirement, or Undocumented addition — **not**
Gap. Requiring evidence before filing a Gap is what keeps the report trustworthy.

**Mix.** The common case, and it is per-area, not per-app: a generated shell with two
hand-built deep areas is normal. Assign provenance **per area** and say so; a single
whole-app provenance verdict over a mixed app is a guess dressed as a finding.

## Saying what you could not establish

Required. Write it as its own subsection of the report, not as a caveat in a footnote.
An assessment that cannot say who built what must say so rather than defaulting to "the
generator did it" — that default converts every gap into an implied tool failure.

Usable wording:

> Provenance is partially established. The repo carries specs and commits from <n>
> authors through <date>; the app carries <n> revisions, of which none can be attributed
> to a specific author or session because the platform attributes all publishes to the
> authenticated tenant user. No decision records were found, so a deviation cannot be
> distinguished from an undocumented deliberate choice by evidence in the project.
> Findings below that depend on that distinction are marked **Drift — undetermined**
> rather than Gap.

That last sentence is the operative one: name the classification consequence of the
unknown, so the reader knows which findings are soft.

## Provenance changes the report, not just its preamble

- Generator-shaped area → the summary leads with "this is the expected starting position
  of the generation path", and remediation is framed as the depth build.
- Mature area → each candidate Gap needs a decision-record sweep first, and its absence
  is stated per finding.
- Undetermined area → no finding in it is filed as a defect without evidence beyond
  "the document says so and the app does not do it".
