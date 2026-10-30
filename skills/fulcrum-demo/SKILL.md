---
name: fulcrum-demo
description: Use when the user says "write the demo script", "prepare the demo", "is this demoable", "make the app demo-ready", "rehearse the happy path", "add a guided tour", "add a walkthrough to the app" or "walk the audience through the app" for an OutSystems or ODC app, or when a `demo` rigor build reaches its demo script row, even when the user does not mention Fulcrum. Writes `.fulcrum/demo-script.md`, the short happy path derived from the brief and plan that the demo-rigor final blind pass walks; checks demo readiness; optionally plans a scripted in-app tour (no AI agent, no entitlement). Not for seed loaders (fulcrum-seed-data), gate definitions (fulcrum-verification) or building sample sign-in (fulcrum-engine-traps).
version: "1.0.0"
requires: >
  Brief and plan in the project repo; a finished or near-finished build to read
  step results against; a browser automation capability on the renderer.
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
it drives no Mentor and no browser.

## Format

Short: one persona block per role the path crosses, 5 to 10 steps total.

```
# Demo script
Rigor: demo   Revision: <per app, filled at the final pass>

## Persona: <role name>
Sign-in: <mode from tenant-profile.md / sign-in-modes.md; sample persona name>

| # | App | Screen | Persona | Action | Seed it reads | Changes data | Expected visible result |
|---|---|---|---|---|---|---|---|
| 1 | OrderDesk | OrderList | Customer | Open the order list | 3 Orders, one per status | no | Three rows, status badges differ |
| 2 | OrderDesk | NewOrder | Customer | Submit order `DEMO-1` | Customer Ann | yes, `DEMO-`; reset: delete them | Success message; list shows 4 rows |
| 3 | OrderDesk | ApprovalQueue | Manager | Open the approval queue | The 1 Pending seeded Order | no | Two rows, `DEMO-1` Pending |
```

Rules:
- Derive from the brief and plan, never from the build: a path written from
  what got built hides what was dropped.
- Every step names the seeded data it reads and the exact text, count or state
  that proves it. A step with no seed row behind
  it renders an empty state in front of the audience, passes validation and
  publish clean, and is found live.
- Expected results are visible on the screen: G2 at `demo` cannot judge a
  server log.
- `App` and `Screen` are what a renderer assertion needs, per app. `Changes
  data` is `no`, or `yes` with the record prefix and the reset that lets the
  path run twice. Renderers act only under the prefix, never on a seeded row,
  so a step without one comes back `untested`.

## Readiness checklist

The demo row has no browser, so the orchestrator adds these as assertions to
the renderer brief of the join's G1, with the script's data permission and
prefix. No new gate: demo-readiness defects (cold-start timeouts, a first load
needing a refresh, slow sign-in, display-only buttons, a reset that leaves
extra rows) were all found at the very end of a field build, after the slot
reserved for them was never reached. `[SINGLE-OBSERVATION]`

1. Sign-in works, per persona, through the `Risk: high` row built from the
   recipe, from a cold browser session.
   The sample-persona block is hidden outside Dev by design, so confirm which
   stage the demo runs in; a demo outside Dev needs another sign-in mode.
2. Seed alignment: the rows each step reads show the script's names and
   counts, after the reset path.
3. Both roles when the path crosses them, signing in fresh each time: a reused
   browser session carries the prior identity.
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

- Asked once when the demo script row is planned, never defaulted; recorded in
  `DECISIONS.md`.
- Runs as ordinary rows at the polish phase on the app lane, after the screens
  it points at are final. A tour built before the screens are stable highlights
  elements that later turns rename or remove, and it fails silently.
- Hidden outside Dev by the sample sign-in block's server-side gate, one If
  around all of it: `../fulcrum-engine-traps/references/sample-signin.md`.
- Tour rows are never `Risk: high` and never hold the demo: the demo script
  stands without them, and a failed tour row is reported and skipped.
- The mechanics (how a highlight attaches to a widget, how steps advance) are
  `[UNVERIFIED]`: no run has built one. The first tour row is the test; read
  its render, and fall back to dropping the tour rather than retrying.
