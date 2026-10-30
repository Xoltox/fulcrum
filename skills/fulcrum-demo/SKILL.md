---
name: fulcrum-demo
description: >
  Writes the demo script, a short happy path derived from the brief and plan
  that the demo-rigor final pass walks, checks demo readiness, and optionally
  plans a scripted in-app tour. Owns the format of `.fulcrum/demo-script.md`.
  Use when asked to prepare a demo, write the demo script, make the app
  demo-ready, rehearse the happy path, or add a guided tour or walkthrough to
  the app. Trigger phrases: "write the demo script", "is this demoable",
  "prepare the demo", "add a guided tour", "walk the audience through the app".
version: "1.0.0"
requires: >
  Brief and plan in the project repo; a finished or near-finished build to read
  step results against; a browser automation capability for the readiness walk.
---

# fulcrum-demo

## Boundary

Owns the demo script file and its format, the readiness checklist, and the
optional tour. Does not own gate definitions or what `demo` rigor runs (the
table lives once in `../fulcrum-verification/references/gates-and-rigor.md`),
sign-in mechanics (`../fulcrum-render-check/references/sign-in-modes.md`), seed
loaders (`../fulcrum-seed-data/SKILL.md`), or the sample sign-in build
(`../fulcrum-engine-traps/references/sample-signin.md`). Adds no gate, stop or
state file.

## The demo script row

Emitted by solution-init at `demo` rigor only: `Turn: code`, `App: solution`
(a literal: no lane, no lease), output `.fulcrum/demo-script.md`
(`../fulcrum-solution-init/references/decomposition-and-sizing.md`, heading
"Gate rows"). Final G2 at `demo` reads this file: each step is one claim
(`../fulcrum-verification/references/gates-and-rigor.md`, heading "G2 - blind
pass"). The writer needs only the brief, the plan and the published structure;
it does not drive Mentor.

## Format

Short: one persona block per role the path crosses, 5 to 10 steps total. A step
a verifier cannot judge from the screen is not a claim, so it does not belong.

```
# Demo script
Rigor: demo   Revision: <per app, filled at the final pass>

## Persona: <role name>
Sign-in: <mode from tenant-profile.md / sign-in-modes.md; sample persona name>
Seed needed: <rows that must exist before step 1>

| # | Persona | Action | Seed it reads | Expected visible result |
|---|---|---|---|---|
| 1 | Customer | Open the order list | 3 Orders, one per status | Three rows, status badges differ |
| 2 | Customer | Submit a new order | none | Success message; list now shows 4 rows |
| 3 | Manager | Open the approval queue | the order from step 2 | The new order is listed, Pending |
```

Rules:
- Derive from the brief and plan, never from the build: a path written from
  what got built hides what was dropped. Steps follow the user's story, not
  the screen inventory.
- Every step names the seeded data it reads and the exact text, count or state
  that proves it. "Looks right" is not a result. A step with no seed row behind
  it renders an empty state in front of the audience, passes validation and
  publish clean, and is found live.
- Expected results are visible on the screen. A claim that only a server log
  shows is out of scope; G2 at `demo` cannot judge it.
- A step that mutates data names the reset: an idempotent re-seed or a
  reload that restores the start state, so the path can run twice.

## Readiness checklist

Run once, when the plan claims "demoable" for the first time, not only at the
end: demo-readiness defects (cold-start timeouts, first load after a new
session needing a refresh, slow sign-in, display-only buttons, a reset that
leaves extra rows) were all found at the very end of a field build, after the
slot reserved for them was never reached. `[SINGLE-OBSERVATION]` Check:

1. Sign-in works through the recipe, per persona, from a cold browser session.
   The sample-persona block is hidden outside Dev by design, so confirm which
   stage the demo runs in; a demo outside Dev needs another sign-in mode.
2. Seed alignment: the rows each step reads exist, with the names and counts
   the script states, after the reset path. Run the loader twice; the counts
   must not change.
3. Both roles when the path crosses them: one pass per persona, signing in
   fresh each time. A reused browser session carries the prior identity.
4. Warm-up: the first call after idle to each backend module. A cold first
   call can time out and show a false error banner that a second call clears.
5. Every button on the path does something. A display-only control on the
   path is a defect; one off the path is a note.
6. First load on a clean profile: if a stale client bundle shows after publish,
   say so in the script and add the refresh as a step.

A finding is a row, in the owning lane, like any other defect. Do not edit the
app from the demo row.

## Scripted tour (optional)

A scripted tour is NOT an AI agent: no model call, no entitlement. It is a
client-side step-through that highlights real elements, one step at a time,
generated from the demo-script steps.

- Asked, never defaulted. Ask once when the demo script row is planned; the
  answer is a user decision recorded in `DECISIONS.md`.
- Runs as ordinary rows at the polish phase on the app lane, after the screens
  it points at are final. A tour built before the screens are stable highlights
  elements that later turns rename or remove, and it fails silently.
- Hidden outside Dev by the same gate as the sample sign-in block, checked in
  the client and not only in the layout. See `../fulcrum-engine-traps/references/sample-signin.md`.
- Tour rows are never `Risk: high` and never hold the demo: the demo script
  stands without them, and a failed tour row is reported and skipped.
- The mechanics (how a highlight attaches to a widget, how steps advance) are
  `[UNVERIFIED]`: no run has built one. The first tour row is the test; read
  its render, and fall back to dropping the tour rather than retrying.
