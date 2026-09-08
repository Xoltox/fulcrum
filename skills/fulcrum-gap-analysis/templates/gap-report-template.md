# Gap analysis report template

Copy to `reports/gap-analysis-<app>-<YYYY-MM-DD>.md`. Replace every `<…>`. **Delete no
section** — an empty section is itself information, so write "None found" or "Could not
be established" rather than removing it.

Section order is deliberate: provenance before numbers, evidence before summary
judgement, and security out of the average.

---

## <App> — gap analysis, <date>

**Requirements source:** `<file or document, with its revision or date>`
**App:** `<exact app identifier>` · **Revisions observed:** `<n>` (`app_revisions`)
**Assessed by:** `<agent or person>` · **Prior report diffed against:** `<file, or None>`

### Read this first — provenance

`<One paragraph per area, or one for the app if uniform. Which of the three shapes:
fresh generator output, mature project, mix. The evidence.>`

**Could not be established:** `<Required. What is unknowable and the classification
consequence — which findings are therefore soft. See the wording in
references/provenance.md.>`

`<If any area is fresh generator output, state here, before any number: the generation
path optimises for speed of first result, not depth, so large gaps in that area are its
expected product and not a failure. Gap analysis is the standard bridge from generated
scaffold to depth build.>`

### What this report is measured against

The standard is `<the requirements document>` plus the platform inventory taken from
`<operations used>`. Fulcrum contains no benchmarks, rubrics or scorecards; where a rule
from a Fulcrum skill is applied below it is named and quoted at the point of use.

`<If you cite a Fulcrum skill anywhere, list here: skill, heading, and the rule as
quoted. If you cite none, write "No Fulcrum rules cited." Never name a skill without a
rule.>`

### Coverage

**Aggregate:** `<n>` of `<m>` assessable named sub-requirements present (`<pct>`%),
summed from the per-requirement counts in the matrix: `<show the arithmetic>`.

**Excluded from that denominator:** unfalsifiable requirements `<n>`; unresolved by
inventory `<n>`; withdrawn `<n>`. `<One line on why each was excluded.>`

`<Diagram 1 — requirement coverage, mermaid. See references/coverage-and-diagrams.md.>`

`<Per-area coverage chart or table. Usually more actionable than the aggregate.>`

### Findings by class

Counts: Gap `<n>` · Drift `<n>` (of which undetermined `<n>`) · Stale requirement `<n>`
· Undocumented addition `<n>` · Unfalsifiable requirement `<n>`.

Only **Gap** is a defect by default.

#### Gaps — required, absent

`<Per finding: requirement ID, what was searched for and with which operation, the named
artifacts found absent, and whether the area's provenance makes the absence expected.>`

#### Drift — built, not as specified

`<Per finding: what the document specifies, what the app does by artifact name, the
decision-record sweep result, and which side should move. Mark undetermined where no
record exists, and say that no record is not evidence of a mistake.>`

#### Stale requirements — the document is what is wrong

`<Per finding: document location, the evidence it is superseded quoted, the edit needed.>`

#### Undocumented additions — in the app, not in the requirements

`<Per finding: artifacts by name, apparent purpose, and valuable / neutral / scope creep
with a reason. Flag any that sits inside a rebuild area — it is lost unless documented
first.>`

#### Unfalsifiable requirements — cannot be assessed as written

`<Per finding: the wording quoted, what would have to be decided before the requirement
can be assessed at all, who decides, and what it blocks. These are findings about the
document. The app was not scored against them.>`

#### Unresolved by inventory

`<Rows whose implementation would plausibly be a Resource, Automation or Timer, which the
context enumeration operations do not list. Name the operation that would have been
needed, and the out-of-band check that would settle it. Absence from the inventory is
not evidence of absence.>`

### Security findings

`<Own section, deliberately outside every coverage figure. Per finding: the exposure in
one line, the artifacts and role assignments that create it, who can do what they should
not be able to do, and the smallest change that closes it. If none: "None found", and
say what was checked — role list, per-screen role assignment, write paths to
result/completion records.>`

### Traceability matrix

`<One row per requirement. Row format in references/traceability-matrix.md. Both evidence
columns itemised and naming artifacts; no row whose only content is a percentage.>`

| ID | Requirement | Sub-requirements | Present — evidence | Absent — evidence | Coverage | Class | Remediation |
|---|---|---|---|---|---|---|---|
| `<R-x (assigned)>` | | | | | `<n of m (pct%)>` | | |

**Identifier scheme:** `<"Document numbering used verbatim", or "Identifiers assigned by
this report as R-<area>-<n>; the source document carries no numbering.">`

### Data model — actual against required

`<Diagram 2 — ER diagram, mermaid, with every absent entity and attribute marked MISSING
and tagged with the requirement identifier that needs it, and every present-but-unused
element annotated. See references/coverage-and-diagrams.md.>`

### Remediation

#### Repair or rebuild, per area

| Area | Decision | Why | Consequence stated |
|---|---|---|---|
| | `<repair / rebuild>` | | |

#### Sequence

`<Diagram 3 — phased remediation flowchart, mermaid. Decisions first, security early and
as its own node, schema before logic before screens, every phase demoable, each node
naming the requirement identifiers it closes.>`

#### Work items

| # | Phase | Item | Closes | Repair/rebuild | Spec | Proof rungs |
|---|---|---|---|---|---|---|
| | | | `<R-ids>` | | `<specs/step-NN-…md>` | `<rungs from fulcrum-verification>` |

Specs use `../../fulcrum-solution-init/templates/spec-template.md`; turn decomposition uses
`../../fulcrum-mentor-turns/SKILL.md`; proof uses `../../fulcrum-verification/SKILL.md`. This
report is not proof that anything was fixed.

#### Document edits

`<Stale requirements and unfalsifiable requirements as their own track. An uncorrected
document reproduces the same false findings on the next re-run.>`

### Open questions

`<Anything the assessment could not settle, with what would settle it. An empty list here
on a real app is a warning sign, not a good result.>`
