# Repo scaffold and handoff structure

Read this for step 7 of `../SKILL.md`. It defines the files the project repo must
contain, what each one is for, and the four documentation failures that made the
reference corpus hard for a fresh agent to obey.

The repo is the only durable memory across sessions. A fresh workhorse-tier orchestrator
reads it cold, every time, with no conversational history. Design it for that reader.

## Layout

```
<project>/
  DOMAIN.md             derived domain source of truth (step 1)
  PLAN.md               phases, steps, apps/agents/workflows, entity owners
  tenant-profile.md     the capability probe result (step 3)
  HANDOFF.md            two parts: RULES (stable) + BRIEF (replaced each session)
  BUILD-LOG.md          append-only: what happened, per step
  RUN-IDS.md            durable run-id log
  specs/
    step-<NN>-<slug>.md one spec per step (step 6)
  buildpatterns/
    step-<NN>-<slug>.md per-step reliability log
  assets/               source artifacts + the asset list from step 1
```

## File roles — one owner per fact

| File | Owns | Never contains |
|---|---|---|
| `DOMAIN.md` | Domain truth: personas, entities, screen inventory, resolved questions | Build mechanics, phase order |
| `PLAN.md` | Scope and ordering: phases, steps, decomposition, entity owners | Mentor mechanics, per-step detail |
| `tenant-profile.md` | Every tenant-varying fact, with evidence | Anything not probed |
| `HANDOFF.md` | Standing rules + the current session's brief | Narrative of past steps |
| `BUILD-LOG.md` | Append-only history, including withdrawn claims | Rules, plans |
| `RUN-IDS.md` | Run ids and their outcomes | Anything else |
| `specs/*` | Everything one step's build agent needs | Cross-step context |
| `buildpatterns/*` | What was reliable or unreliable for one step | Rules for other steps |

The right-hand column is the load-bearing one. Every documentation failure below is a
fact living in more than one file.

## The handoff document — two parts, one replaced

`HANDOFF.md` has exactly two parts:

**PART 1 — RULES.** Stable. Accumulates slowly. Standing decisions, the file map,
the target app identity, error handling, what is not to be re-litigated. Changes only
when a rule changes.

**PART 2 — BRIEF.** Replaced **wholesale** every session. Where the build is now, the
one next step, and what that step needs. Never appended to.

**Why the split.** A handoff that accumulates step narrative grows without bound and
buries the rules under history. The fresh agent then reads mostly-irrelevant past-step
detail and mis-weights it as current instruction. The append-only history belongs in
`BUILD-LOG.md`, which nobody is required to read to act.

Hard rules:

- The BRIEF names **exactly one** next step. Two next steps means the orchestrator picks.
- The BRIEF never narrates completed steps beyond what the next step depends on.
- The RULES section is where a new standing decision lands — once, in one place.
- Neither part restates a spec. Specs are self-sufficient by design.

Shape to copy: `../templates/handoff-template.md`.

## The four documentation failures to design against

All observed in the reference corpus. `[VERIFIED]`

### 1. One policy stated in three files at three different strengths

Model policy appeared in three files, each stating it differently. A fresh agent obeys
whichever it reads first and cannot tell it has read the weakest version.

**Rule.** Each policy is stated in exactly one file. Everywhere else links to it by
relative path. If two files must both mention it, one of them says "see X" and nothing
more.

### 2. Standing rules duplicated across three places, one copy missing a prohibition

The same rule set appeared three times; one copy had silently dropped a prohibition. An
agent obeying that copy breaks a rule it was never shown, and the breach looks like
disobedience rather than a documentation defect.

**Rule.** Never duplicate a rule list. If a spec must restate standing rules inline — and
it must, so the build agent needs no second file — then generate that block from one
source, and treat any hand-edit of a spec's rules block as a defect.

### 3. Every section-anchored cross-reference dangling

Every `§`-numbered reference in the corpus pointed at nothing, because the target files
had no numbered headings.

**Rule.** Link by relative path, and quote the target heading verbatim. Never `§`. Never
a line number — line numbers rot on the first edit.

### 4. A plausible inference recorded as verified fact

One claim in the corpus had to be formally withdrawn after being written down as verified
when it was an inference.

**Rule.** Tag evidence strength on every non-obvious claim, per the evidence tags in the
authoring contract. When a claim is withdrawn, **withdraw it in place in `BUILD-LOG.md`**
rather than deleting it — a silently deleted claim gets re-derived.

## Durable run-id log

Every Mentor run and every publish gets a line in `RUN-IDS.md` at the moment it is
started, before it is polled. A run id held only in an agent's context is lost when the
context is lost, and an unpolled run's outcome is then unknowable while its effects are
already in the model.

Minimum per line: timestamp, step number, run id, the operation, and the outcome once
known. Durability mechanics: `../../fulcrum-mentor-turns/SKILL.md`.

## Per-step build-pattern log

One file per step in `buildpatterns/`, written by the session that executed the step, not
by this skill. Scaffold the directory and the naming convention now, plus a one-line
stub explaining what belongs there:

- What the step actually did, versus what its spec said.
- Which turn shapes worked and which needed a fix turn.
- Anything that should become a standing rule — flagged, not promoted; promotion is a
  deliberate edit to `HANDOFF.md` PART 1.

## Scaffold checklist

- [ ] Every file in the layout exists, even if a stub.
- [ ] Every stub states what belongs in it and who writes it.
- [ ] No fact appears in two files at two strengths.
- [ ] No rule list is duplicated by hand.
- [ ] No `§` anchor and no line-number reference anywhere.
- [ ] `HANDOFF.md` has both parts, and the BRIEF names one next step.
- [ ] `RUN-IDS.md` exists and is empty rather than absent.
- [ ] Phase-one specs are written and each passes the right-sizing test.
