---
name: fulcrum-gap-analysis
description: Assesses an ODC app that already exists against the requirements it was meant to satisfy, and plans what to do about the difference. Establishes build provenance first, extracts stable requirement identifiers, inventories the real model, builds a requirement-to-artifact traceability matrix with itemised evidence, classifies every finding as gap / drift / stale requirement / undocumented addition / unfalsifiable requirement, then sequences remediation as repair-or-rebuild. Use when asked to "compare what was built against the BRD", "what's missing from this app", "is this generated app complete", "gap analysis on my ODC app", "audit an app I inherited against its requirements", "does the app match the spec", "what should we build next on this app", or when handed a requirements document plus a live app and asked how far apart they are.
version: "1.0.0"
requires: ODC MCP surface for model inventory (context_entities, context_screens, context_roles, context_actions, context_agents, context_connections, context_structures, context_graph, context_search, app_info, app_refs, app_revisions); read access to the requirements source document; read access to whatever project history exists (build logs, decision records, handoffs, commit history); filesystem write access for the report; a mermaid-capable renderer for the required diagrams (source-level mermaid blocks are acceptable when none is available)
---

# ODC gap analysis

The app exists. Someone wants to know how it compares to the requirements it was
supposed to satisfy, and what to do about the difference. Run on the
**deep-reasoning** tier (see `../../MODEL-TIERS.md`) — classification is the whole
value, and a misclassification manufactures work.

## Boundary

Owned here: provenance, requirement identifiers, model inventory, the traceability
matrix, finding classification, repair-versus-rebuild, remediation sequencing.

| Need | Owner |
|---|---|
| Pre-build planning, decomposition, the tenant probe, brief derivation | `../fulcrum-solution-init/SKILL.md` |
| Spec form for each remediation step | `../fulcrum-solution-init/templates/spec-template.md` |
| Turn decomposition and prompt shape for building a fix | `../fulcrum-mentor-turns/SKILL.md` |
| Proving one fix actually landed | `../fulcrum-verification/SKILL.md` |
| Why a construct fails | `../fulcrum-engine-traps/SKILL.md` |
| Stop conditions, fix-turn caps, delegation depth | `../fulcrum-unattended-guardrails/SKILL.md` |

This skill produces an assessment and a plan; it does not build and does not prove. Do
not re-run `fulcrum-solution-init` on an app that already exists — it is pre-build and
refuses a scaffolded repo by design. Do not stretch `fulcrum-verification` over a whole
app: it scopes to proving one specific change landed.

## Provenance is step one and it changes the meaning of every finding

Do **not** assume the app came from a generator. Three shapes:

- **Fresh generator output.** ODC's web app-generation path optimises for speed of
  first result, not depth, so large gaps are its **expected product, not a failure**.
  `[SINGLE-OBSERVATION]` Say this in the report, plainly, before any number: a reader
  who does not know it reads "65% absent" as breakage when it is the normal starting
  position, and loses confidence in a tool that worked correctly. Here gap analysis is
  the standard bridge from generated scaffold to depth build.
- **A mature project** worked on over time by many people and agents. Most deviation
  here is **not** a defect: requirements moved, decisions were taken and never written
  down, features were added that nobody put in the document.
- **A mix**, which is the common case.

Establish provenance before judging anything. Look for what history exists — build or
change logs, per-step records, decision or judgement-call records, handoff documents,
app revision history (`app_revisions`), commit history, prior analysis reports. State
what you found **and what you could not establish**. An assessment that cannot say who
built what must say so, rather than defaulting to "the generator did it". Evidence
sources and the wording for an unknowable provenance: `references/provenance.md`.

## Five finding classes — classify every finding into exactly one

Four come from `../../CONVENTIONS.md`, heading "Gap analysis never assumes how the app
got there". The fifth is this skill's addition.

| Class | Means | Defect by default? |
|---|---|---|
| **Gap** | Required, and absent from the app. | **Yes** |
| **Drift** | Built, but not as specified. May be a deliberate decision nobody wrote down — look for a decision record before calling it a defect. | No |
| **Stale requirement** | The document no longer describes intended behaviour. The document is the thing that is wrong. | No |
| **Undocumented addition** | Present in the app, absent from the requirements. Could be valuable, could be scope creep. | No |
| **Unfalsifiable requirement** | The requirement cannot be assessed as written, so no app can be scored against it. A finding about the **document**. | No |

Only **Gap** is a defect by default. A mature codebase produces mostly the other four,
and treating deviation as failure there manufactures work and destroys trust in the
report.

**Unfalsifiable requirement** is the class agents most often skip, and skipping it
invents gaps. Documents routinely defer their own specifics — wording equivalent to
"to be detailed further with IT", "as appropriate", "per business need" — naming an
intention, not a testable behaviour. Do not score the app against it. File it against
the document with **what would have to be decided before it can be assessed at all**,
exclude it from every coverage denominator, and count it separately.

Classification is not a free choice: `references/finding-classes.md` has the decision
order, the evidence each class demands, and the anti-patterns that collapse everything
into Gap.

## Procedure

1. **Establish provenance.** Record what history exists and what is unknowable.
   `references/provenance.md`.
2. **Extract stable requirement identifiers** from the source document, one per
   assessable requirement, with named sub-requirements beneath. Where the document has
   no numbering, **assign identifiers and say in the report that you assigned them** —
   findings must be addressable and a later re-run must be comparable. Where the
   document is too thin to yield requirements at all, derive a brief first:
   `../fulcrum-solution-init/references/source-triage.md`, heading "Deriving the brief
   when none was supplied", owns that method. Do not restate it.
3. **Inventory what actually exists** — entities and their attributes, screens, roles
   and per-screen role assignments, actions, integrations, timers — from the platform's
   own context/inventory operations, never from the requirements document and never
   from an agent's prose summary. Blind spots and the operations to use:
   `references/inventory.md`.
4. **Build the traceability matrix.** One row per requirement, itemising evidence of
   what **is** present and what is **not**, both naming concrete artifacts — entity and
   attribute names, screen names, action names, role names. The itemised evidence is
   the substance of the report; the coverage figure summarises it and never substitutes
   for it. `references/traceability-matrix.md`.
5. **Classify every finding** into exactly one of the five classes above.
6. **Assess remediation** — repair versus rebuild per area, then sequence the work.
   `references/repair-vs-rebuild.md`.
7. **Hand off.** Each remediation item becomes one or more step-sized specs on
   `../fulcrum-solution-init/templates/spec-template.md`; decompose each into turns with
   `../fulcrum-mentor-turns/SKILL.md`; prove each landed with
   `../fulcrum-verification/SKILL.md`.

Write the report from `templates/gap-report-template.md`.

## Every coverage figure states its denominator

From `../../CONVENTIONS.md`, heading "A coverage figure must state its denominator".

- Write "**3 of 5 named sub-requirements present** (60%)". Never a bare percentage.
- Two reviewers working from the same itemised evidence must land on the same number.
  If they cannot, the sub-requirements are not named concretely enough — fix the row,
  not the number.
- **The aggregate is derived from the per-requirement counts**, arithmetic shown in the
  report. Never estimated independently, never adjusted to "feel right".
- Unfalsifiable requirements leave the denominator, reported as their own count.
- Security findings are **never averaged into a coverage figure**. Own section, own
  prominence — a role inversion is not 4% of anything.

## Three required diagrams

Mermaid, in the report, deliverables not decoration — the parts of a real gap report a
team actually used to plan. `[SINGLE-OBSERVATION]`

1. **Requirement coverage** — done vs partial vs absent, counts labelled.
2. **Entity-relationship** — the **actual** schema drawn against the **required**
   schema, so missing entities and missing attributes are visible as absences rather
   than described in prose.
3. **Phased remediation flowchart** — the sequence from step 6, with dependencies.

Chart forms, mermaid shapes, and how to show an absence in an ER diagram:
`references/coverage-and-diagrams.md`.

## Citing a skill means applying a named rule from it

Fulcrum contains **no benchmarks, no rubrics and no scorecards**. The word "score"
appears in it only in warnings against trusting scores. So:

- If a report attributes a standard to a Fulcrum skill, it must **quote or name the
  rule it applied**, and name the skill and heading it came from.
- Never cite a skill because its title matches a section heading. `[SINGLE-OBSERVATION]`
  An observed report named three Fulcrum skills as its "evaluation standard" while
  quoting no rule from any of them.
- An unearned citation makes a report look authoritative while removing the reader's
  ability to check it. It is worse than no citation.
- The report's real standard is the requirements document plus the platform inventory.
  Say so.

## Finding shapes a percentage hides

Illustrations of **shape**, neutral names, not a checklist — do not hunt for these four.

- **Schema present, logic absent.** A required capability whose data model exists but
  whose enforcing logic does not — e.g. a `SequenceOrder` attribute on `Task` with zero
  gating logic anywhere. Very common, and a matrix that cannot express it collapses it
  into a high percentage.
- **Role inversion.** An edit screen for a results or completion record reachable by
  the very role whose result it records, letting a user write their own outcome.
  Security class, own section, out of the average.
- **The one attribute that carries the feature.** A core entity missing the single
  attribute the capability depends on while every surrounding attribute exists —
  coverage reads high, capability is zero.
- **Built and unreachable.** Screens that exist but are role-restricted such that the
  intended audience cannot reach them.

## Exit gate

Do not deliver until all hold:

1. Provenance stated, including what could not be established.
2. Every requirement has a stable identifier; assigned ones are declared as assigned.
3. Inventory came from platform operations, blind spots named as unresolved rather than
   reported as absences.
4. Every matrix row itemises present-evidence and absent-evidence by artifact name.
5. Every finding has exactly one of the five classes.
6. Every coverage figure carries its denominator; the aggregate's arithmetic is shown.
7. All three diagrams present.
8. Every Fulcrum citation names a rule and its heading, or is deleted.
9. Remediation sequenced, repair-or-rebuild decided per area, each item pointed at a spec.

## Reference files

| File | Open it when |
|---|---|
| `references/provenance.md` | Step 1 — evidence sources, what each proves, wording for unknowns |
| `references/finding-classes.md` | Step 5, or any time a finding looks like a Gap — decision order, evidence per class, anti-patterns |
| `references/inventory.md` | Step 3 — which operations to use, and the enumeration blind spots |
| `references/traceability-matrix.md` | Step 4 — row format, itemised evidence, partial rows |
| `references/coverage-and-diagrams.md` | Any number or chart in the report |
| `references/repair-vs-rebuild.md` | Steps 6 and 7 — the decision per area, sequencing rules |
| `templates/gap-report-template.md` | Writing the report |
