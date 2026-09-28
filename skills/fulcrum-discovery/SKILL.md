---
name: fulcrum-discovery
description: Interviews a user who has an idea but no written requirements, and produces the brief that fulcrum-solution-init ingests. Runs a bounded, batched interview targeted at exactly what ODC and Mentor need — roles and per-screen access, entity relationships, integrations, seed data, read-only versus transactional screens — marks every answer as held, elicited, assumed or undecided, and converts vague answers into observable ones. Use when the user says "I have an idea for an app", "help me write requirements", "I don't have a BRD", "I want to build something but nothing is written down", "can you spec this out for me", "turn this into requirements", "interview me about my app", or hands over a one-paragraph idea and asks what to build. Also use in expert mode to fill one named hole in an existing document. Stops at the brief; planning is fulcrum-solution-init's.
version: "1.0.0"
requires: a capability to put structured questions to the user and receive answers in-session (a native elicitation primitive where the harness has one, otherwise ordinary conversational turn-taking); filesystem write access for the brief and `.fulcrum/DECISIONS.md`. No ODC MCP surface and no Mentor session are needed — this skill runs before either exists.
---

# fulcrum-discovery

The front door for a user with an idea and nothing written. Output is **one brief**
that `../fulcrum-solution-init/SKILL.md` ingests as its source material at step 1.

## Boundary

Owned here: the interview, the sufficiency judgement, and the brief. Nothing else.

| Need | Owner |
|---|---|
| Decomposition into apps/agents/workflows, phase and step sizing, specs, repo scaffold | `../fulcrum-solution-init/SKILL.md` |
| Where the brief and decision records live on disk | `../fulcrum-project-state/SKILL.md` |
| Assessing an app that already exists against requirements | `../fulcrum-gap-analysis/SKILL.md` |
| Anything Mentor, publish, or verification | the respective sibling skill |

**Stop at the brief.** Do not name phases, do not size steps, do not propose an app
split. Deciding the shape of the build during the interview freezes a decomposition
before the tenant probe has run, and `fulcrum-solution-init` will then either re-do it
or inherit it unexamined. `[UNVERIFIED]` — design decision, not a field observation.

## Interaction requirement

This skill cannot run without a live user. If the harness cannot reach one — an
unattended run, a queued job — do not interview and do not invent answers. Write what
source material exists, mark every readiness item `undecided`, and halt with the list
of what a human must answer.

## Procedure

### 1. Read what already exists, first

Never open with a question whose answer is in a file the user already handed over. An
interview that asks what the user just wrote reads as inattention and spends the same
patience budget for nothing. Inventory whatever exists — a paragraph, an email thread,
a screenshot, a spreadsheet — and mark each readiness item below `covered` or `open`
before asking anything.

### 2. Interview in batches

- **Three batches, at most five questions each.** Never one question per turn: it
  multiplies round trips and reads as an interrogation.
- Every question carries **concrete options** and, where one exists, a **recommendation
  with its one-clause reason**. A user who must invent an answer from nothing gives a
  weaker answer than one choosing between two named alternatives.
- Batch 1 is the readiness set's blocking items. Batch 2 is what batch 1's answers
  opened up. Batch 3 is confirmation and cleanup only.
- Play back the accumulated brief between batches. Correcting a written line is
  cheaper than answering the same question twice.

### 3. Stop when sufficient, not when complete

Stop when every readiness item has **either an answer or an explicit `undecided`
marker naming the step it blocks**. Sufficiency, not exhaustiveness.

**The mechanism.** An unbounded interview exhausts the user's patience and the
session's context before a single build turn runs, and answer quality decays as it
goes — a user asked thirty questions answers the last ten carelessly, so the late
answers are the *least* reliable, not the most. A fourth batch therefore buys
low-confidence content at full cost. Past the ceiling, an item becomes `undecided`,
which is honest and cheap; an invented specific is neither. Full rule, the ceiling's
override condition, and what is deliberately never asked:
`references/sufficiency-and-stopping.md`.

### 4. Convert every vague answer into an observable one

"Fast", "user-friendly", "the manager oversees approvals", "to be detailed later" are
requirements that no app can fail. `../fulcrum-gap-analysis/references/finding-classes.md`,
heading "Unfalsifiable requirements in detail", must later classify each one as a
finding **against the document** and exclude it from coverage — so every vague line
this interview emits becomes a phantom gap or a distorted coverage figure downstream.

Two permitted moves, and no third:

1. Convert it — ask what someone would see, click, or count if it were true, and write
   that. "The manager oversees approvals" becomes a named role, a named screen, and
   which records it can read versus write.
2. Mark it `undecided`, naming who decides and which step it blocks.

Never substitute a plausible specific for a vague answer and write it as a
requirement. Conversion patterns: `references/observable-requirements.md`.

### 5. Mark what the user knew versus what they guessed

Downstream skills treat every line in a brief as equally load-bearing unless the brief
says otherwise. Every requirement line carries a `Confidence` value:

| Value | Means |
|---|---|
| `held` | The user arrived with it. Strongest. Challenge only if it contradicts another `held` line. |
| `elicited` | The user decided it on the spot in answer to a question. Real, but untested against their own domain. |
| `assumed` | The interviewer proposed it and the user did not object. Weakest thing still written as a requirement. |
| `undecided` | No answer. Names who decides and what it blocks. Never a requirement. |

This is a **different namespace** from the `[VERIFIED]`/`[UNVERIFIED]` evidence tags in
`../../CONVENTIONS.md`, heading "Hard rule 4 — mark evidence strength". Those grade
Fulcrum's claims about the platform; these grade a requirement's provenance. Do not mix
them in one line.

An `assumed` line that turns out wrong is **drift the app inherited from the brief**,
not a build defect, and only this marker lets a later reader tell the two apart.
`[UNVERIFIED]`

### 6. Record decisions as they are made

Every choice made during the interview — a resolved ambiguity, a rejected alternative,
a recommendation the user accepted — is appended to `.fulcrum/DECISIONS.md` with
`Decider: user` or `Decider: agent`. Shape and rules are owned by
`../fulcrum-project-state/SKILL.md`, heading "DECISIONS.md closes an existing hole";
do not restate them here.

Record it at the moment it is made, not at the end. An interview that batches its
records loses the ones made before a crash, and an unrecorded interview choice is
indistinguishable from drift when gap analysis runs months later.

`Affects` wants concrete identifiers. Early in an interview there are none — write the
entity or screen *name* the decision will attach to, and accept that
`fulcrum-solution-init` may rename it.

### 7. Write the brief and hand off

Copy `templates/brief-template.md`. It is deliberately the same shape
`fulcrum-solution-init` derives for itself when it has to — see
`../fulcrum-solution-init/references/source-triage.md`, heading "Deriving the brief
when none was supplied" — so ingestion needs no translation step.

Hand off by naming the brief's path and saying what is still `undecided`. Do not
summarise the interview back at length; the brief is the summary.

## Mode

`guided` runs this as a conversation, start to finish. `expert` invokes it to fill one
named hole in an existing document: interview only that hole, append only those lines
and their decision records, and never rewrite the surrounding document. Both settings
and their rules are owned by `../../CONVENTIONS.md`, heading "Mode and posture".

## What to elicit, and why each item

Each row exists because something in this repo needs it. Questions:
`references/question-bank.md`.

| Elicit | Needed because |
|---|---|
| Roles, and which roles reach which screen — read versus write, separately | Role list and per-screen assignment are distinct findings (`../fulcrum-gap-analysis/references/inventory.md`). Unstated per-screen access produces role inversion — a user writing their own outcome (`../fulcrum-gap-analysis/SKILL.md`) — and a new screen can ship an unasked-for default role requirement nobody can detect without the intent written down (`../fulcrum-engine-traps/references/overlays-wizards-charts.md`, heading 5) |
| Entities, their key attributes, and every relationship — including two distinct references from one entity to the same entity | Relationship shape is the thing a brief most often omits, and the two-FKs-to-one-entity case is legal and commonly mis-modelled (`../fulcrum-engine-traps/references/static-entities.md`) |
| Which value sets are fixed and enumerable | Fixed sets are static entities, not text; the distinction is a model change versus data entry later (`../fulcrum-project-state/templates/DECISIONS.md`, record D-002) |
| Integration points, each with direction and payload | Integrations are named at decomposition (`../fulcrum-solution-init/SKILL.md`, step 4) and carry their own trap class (`../fulcrum-engine-traps/references/rest-and-integration.md`) |
| What rows must exist before a screen can be demonstrated working | Seed precedes any screen that reads it, and seeding is its own multi-turn phase (`../fulcrum-seed-data/SKILL.md`; `../fulcrum-solution-init/SKILL.md`, step 5 "Data before screens") |
| Per screen: read-only or transactional | A spec must state "display only" explicitly or the build agent hardcodes text (`../fulcrum-solution-init/templates/spec-template.md`, FUNCTIONAL BEHAVIOR), and a transactional screen demands the interaction-persistence rung (`../fulcrum-verification/SKILL.md`, proof ladder rung 7) |
| Persona and scope, and whether single-role is an assumption | The brief's required first content; a wrong persona mis-shapes every entity (`../fulcrum-solution-init/references/source-triage.md`) |
| Web or mobile, phone-width or desktop | Reversing it means re-creating the app and rebuilding every screen (`../fulcrum-solution-init/SKILL.md`, step 2) |
| One observable acceptance statement per screen | Acceptance items must name an instrument and may never say "works as expected" (`../fulcrum-solution-init/templates/spec-template.md`, Acceptance checklist) |
| The smallest slice worth demonstrating | Every phase ends demoable (`../fulcrum-solution-init/SKILL.md`, step 5) |
| Which images, logos and brand files exist, and who can upload them | There is no asset-upload path over the ODC MCP surface — every asset is a human handoff and a gate (`../fulcrum-solution-init/references/source-triage.md`, heading "Assets are a human handoff — plan for it") |

## Exit gate

Do not hand off until all hold:

1. The brief exists at a stated path, in the template's shape.
2. Every readiness item is answered or explicitly `undecided` with what it blocks.
3. Every requirement line carries a `Confidence` value.
4. No requirement line is unfalsifiable — each states something observable.
5. Every interview decision is appended to `.fulcrum/DECISIONS.md`.
6. The brief names which source material, if any, it was derived from.

## Routing

| Situation | Open |
|---|---|
| Composing the batches; need the actual questions and their options | `references/question-bank.md` |
| Deciding whether to ask one more question, or the user is losing patience | `references/sufficiency-and-stopping.md` |
| An answer is vague, aspirational, or defers specifics | `references/observable-requirements.md` |
| Writing the output | `templates/brief-template.md` |
| The brief is done | `../fulcrum-solution-init/SKILL.md` |
