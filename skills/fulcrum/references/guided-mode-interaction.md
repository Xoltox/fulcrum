# Guided-mode interaction contract

This is the only place in the Fulcrum family that defines question-asking
discipline. `expert` mode does not use this file — the user invokes skills
directly and no routing questions are asked. Mode definitions themselves:
`../../../CONVENTIONS.md`, heading "Mode and posture" — not restated here.

## What this router asks about, and what it never asks about

The router's questions are scoped to **routing and mode** only:

- Is there source material, or should this start from an interview?
- Does an app already exist that the user means for this engagement?
- `guided` or `expert`, on first run only.
- Which of two equally-plausible ladder rows applies, when a
  conflicting-signal case in `detection-procedure.md` has no mechanical
  answer.

It never asks about requirements content — roles, entities, screens,
acceptance criteria, integrations, seed data. The instant a question would be
about what the app should *do*, it is out of scope here and belongs to
`../../fulcrum-discovery/SKILL.md`'s interview. Route to it rather than asking
the question yourself.

**The line, concretely:** "Do you have a BRD, Figma export, or similar
written down?" is this router's question — it decides which skill to open.
"What roles does this app need?" is discovery's question — it decides what
the app contains. If in doubt, ask: does the answer change which skill I
dispatch to, or does it change what gets built? The former is this router's.

## The batching rule

Never ask one question per turn. Batch related questions together — this
router's own question set is short (mode, source material, ambiguous ladder
row), so in practice one batch of at most three questions covers the whole
first-run case. Reserve a second batch only for a genuine conflicting-signal
case detection could not resolve on its own.

## Every question carries options and a recommendation

Never ask an open question the user must answer from nothing. State the
choices and, where one exists, a one-clause recommendation.

**Example — mode, first run:**

> This looks like a first run — no `.fulcrum/` found yet. Two ways to work:
> - **guided** — I ask before anything ambiguous, narrate what's about to
>   happen, and surface assumptions as I make them. *Recommended for a first
>   engagement or an unfamiliar tenant.*
> - **expert** — you invoke skills directly; I proceed under stated
>   assumptions and record them rather than asking.
>
> Which do you want?

**Example — no source material found, app inventory ambiguous:**

> I don't see a BRD, Figma export, mockup, or existing `.fulcrum/` in this
> repo, and the tenant has an app called `OrderTracker` that may or may not be
> what you mean.
> - If `OrderTracker` **is** this engagement's app, I'll run a gap analysis
>   against it. *Recommended if you're picking up existing work.*
> - If it is **unrelated**, tell me what you have — even a one-paragraph
>   idea — and I'll start an interview to build a spec from scratch.
>
> Which is it?

## The failure mechanism, stated once

A router that asks what it could have detected from the filesystem or the
tenant trains the user to distrust it: every subsequent question reads as "did
you even look?" rather than as a genuine decision point, and that erodes the
willingness to answer carefully exactly when a real ambiguity needs it. It
also spends a fixed interaction budget — the same one
`../../fulcrum-discovery/references/sufficiency-and-stopping.md` describes
decaying answer quality against — on questions that had a mechanical answer,
leaving less patience for the questions that do not.

Concretely: never ask "do you want guided or expert mode" if `project.md`
already states it. Never ask "is there an app" if the tenant inventory already
settles it. Never ask "where's your BRD" if a file matching
`../../fulcrum-solution-init/references/source-triage.md`'s patterns is
already sitting in the repo — open it and confirm what was found instead of
asking whether it exists.

## After the batch

Play back what was decided in one line before dispatching — "Guided mode,
scaffolding from `docs/brd.md` via `fulcrum-solution-init`" — so the user can
correct a misread before a subagent starts spending calls on it. Then dispatch
per the ladder in `../SKILL.md`; this file's job ends at the handoff.
