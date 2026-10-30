# Gates and rigor - the depth

The gate map and the rigor table live in `../SKILL.md`, heading "Gates and rigor",
and nowhere else. This file says who runs each gate, how far its evidence reaches and
what a failure does. Everything here is a Fulcrum rule; the depths are unmeasured
design choices, not findings.

## Why tiered

Proof costs minutes and tokens, like a Mentor turn, so running every rung on every
row spends a demo's budget on evidence nobody asked for. But a clean publish proves
nothing about rendering or logic, so no rigor may stop at G0 and call the work
verified. The dial changes when evidence is gathered and how much; `Gate` keeps the
record honest about how far it got.

## Vocabulary

- **Lane:** the rows of one app, run in order by one driver at a time. A declared
  producer and consumer pair runs as one lane.
- **Join:** a `Turn: verify`, `App: solution` row integrating lanes, one per consumer
  app; a single-app project has one.
- **`verify` row:** proof with no Mentor rung and no lease, run at every rigor. Exists
  only for joins, G2 and owed G3 (`../../fulcrum-solution-init/references/decomposition-and-sizing.md`,
  heading "Gate rows").
- **Mutating row:** a row with `Turn` of `build`, `fix`, `seed` or `publish`.
  `code`, `infra`, `external` and `manual` rows take no gate: `Gate` stays `-` and the
  session-file outcome line names the evidence.

## Who runs each gate

| Gate | Runs it | Lease | When it completes |
|---|---|---|---|
| G0 | `fulcrum-mentor-driver`, inside the dispatch | The dispatch's own | Before the driver reports |
| G1 | `fulcrum-renderer` for screens, then `fulcrum-verifier` to judge the evidence. No screens: `fulcrum-verifier` alone | None | After the driver returns, before that lane is selected again; where the rigor table says at the join, as the join row |
| G2 | `fulcrum-renderer` for evidence, then a fresh `fulcrum-verifier` | None | At the rigor table's moment; scope below |
| G3 | The instrument each rung names, per `../SKILL.md`. Rung 1 is a Mentor read-back: it runs inside the driver dispatch, before it closes | None, beyond the dispatch's own for rung 1 | Beside or after G1, before that lane is selected again |

**The driver cannot run G1.** It holds neither `http-probe` nor `browser-automation`,
so it cannot exercise the app, and a telemetry sweep over no exercise reads the
identical empty result for a broken app and a working one. The renderer judges
nothing, so a screen check needs a verifier behind it. The orchestrator rules on
the verifier's report (`../../fulcrum-loop-engine/references/iteration-contract.md`,
heading "Phase 5 - Verify").

**The orchestrator runs none of them.** Its prohibitions hold at every rigor
(`../../fulcrum-unattended-guardrails/SKILL.md`, heading "Orchestrator prohibitions -
categorical"). Non-Mentor checkers need no lease, do not count toward the in-flight
cap and run alongside other lanes.

## G0 - publish gate

- Every publish, every publication key. One Publish can produce several keys when a
  session holds several assets; an ungated key is a publish nobody confirmed.
- Rung 2 then rung 3, per `../../fulcrum-mentor-turns/references/mcp-surface.md`,
  heading "Publishing", including how a `Workflow` or library is confirmed.
- A terminal publish with an unchanged revision is the no-op case: nothing landed.
  The loop detects it; the decision is in
  `../../fulcrum-unattended-guardrails/references/halt-conditions.md`, heading
  "Stall and no-op decisions".

## G1 - runtime check

Against the published revision, in this order:

1. **Exercise** the rows' observable outcomes: real requests or a real render. A
   check over zero traffic measures nothing (`runtime-telemetry.md`).
2. **Rung 4** over the exact window of that exercise, with the `app_health` bracket
   the runtime stop reads
   (`../../fulcrum-unattended-guardrails/references/halt-conditions.md`, heading
   "The runtime-shaped stop"). An `Error` entry is a hard fail. An empty sweep passes
   nothing by itself.
3. **Rung 6** where the render obligation applies (`../SKILL.md`, heading "Render
   obligation").

The revision is pinned: the brief names the live revision per app. The lane is not
selected again until G1 reports, so the check cannot race that lane's next publish.
Pinning is what stops a pass being recorded against a revision nobody exercised. The
hold: `../../fulcrum-loop-engine/references/frontier-and-batching.md`, heading "What
runs alongside what".

**What an exercise misses.** How much G1 covers is the rigor table's. Where it owes a
happy path, rows the path did not touch stay at `G0`, which is expected, not a defect.
Where it owes the batch, a row the exercise missed stays at `G0` with `Verdict:
unproven`.

Render hand-offs still apply: no browser capability, or no sign-in mode reaching the
screen, leaves rung 6 `untested` and the row below G1.

## G2 - blind pass

A `verify` row, so the build cannot close without it: the final row depends on all
leaves. Always a fresh `fulcrum-verifier`. It gets claims and evidence paths, never the
builder's report, `TASKS.md`, or the journal: a verifier shown the claim tends to
confirm it (`../../fulcrum-unattended-guardrails/references/delegation.md`, heading
"Re-verification means a fresh blind verifier").

When it runs: `../SKILL.md`, heading "Gates and rigor".

| Rigor | Claim source |
|---|---|
| `demo` | `.fulcrum/demo-script.md`: each step is one claim. Nothing else is in scope |
| `pilot` | The acceptance items of every plan step |
| `production` | Lane pass, before any join depending on it: that app's acceptance items. End pass: the join rows' cross-app claims and any lane claim not re-proven since a later publish touched it |

**Demo scope is a scope, not a discount on honesty.** The verifier reads the demo
script path in its brief and walks it. A defect off the script is out of scope: one
line as a note, never a FAIL, because a demo script is what the audience will see.
No demo script at the point G2 is due: G2 did not run. Report it and ask; never
substitute a free-form look around the app.

**Order.** Claims that need a render need evidence first. Dispatch `fulcrum-renderer`
with the same claims as assertions, then pass its evidence folder to the verifier.
The verifier cannot render; without a folder those claims come back `untested`.

**Same revision, or `untested`.** The brief names the expected revision per app. A
live revision that differs means the evidence belongs to another build: the verifier
reports `untested` for that app. A lane under G2 takes no mutating dispatch until the
verifier reports; other lanes keep moving.

## G3 - per-row proof

Exactly the rungs in the row's `Verify` column; fewer is a stated gap. `Verify` is
written at planning at every rigor. Where the rigor table runs no G3 on a row, the
list is unused, not deleted, so raising rigor later has something to run. Drivers
never edit `Verify`, `Risk` or `Gate`; the orchestrator owns `TASKS.md`.

Rung 8 belongs in `Verify` for a row touching a shared block or a prior verified
feature, and such a row is `Risk: high`. At `demo` no G3 runs, so the report states
that no regression sweep ran.

## Recording

- `Gate` is the highest gate actually run on that row, read by number. Never record
  above it, even when a later pass would probably have caught a defect.
- A gate reaches a row only through evidence about that row. A batch G1 that missed
  one row, or a G2 whose claims skipped it, leaves that row's `Gate` where it was.
- `Verdict: pass` means every gate the rigor requires of that row at this point ran
  and passed; `Gate` states how deep that is. A `demo` row at `G0` is `pass`.
- `Verdict: unproven` means a required gate did not run or came back `untested`. The
  row stays `todo` and is re-proven, not re-fixed
  (`../../fulcrum-loop-engine/references/frontier-and-batching.md`, heading "Unproven rows").
- A dependent reads a row as done only at `Status: done` with `Verdict: pass`.
- A `done`/`pass` row may be superseded by an open `fix` row carrying the same `Step`; the fix row, not the row, says whether the claim holds.
- Report figures state the denominator per gate: `G2: 14 of 16 claims OK, 2 untested`.

## Failure at each gate

| Gate | Failure | Goes to |
|---|---|---|
| G0, rung 1 | Build error, revision mismatch, no-op, failed read-back | The fix-loop inside the dispatch, under the turn cap |
| G1, G2, G3 | A failure on rows a driver already closed | The late failure rule: rows stay `done`, one new `fix` row (`../../fulcrum-loop-engine/references/oscillation-and-fix-loop.md`, heading "Late failures") |
| G1 | Runtime step-change | Hard stop |
| Any | A claim G1 or G3 had proven now fails | Regression: a lane stop if confined to that app, otherwise a hard stop |
| Any | `untested` | Never a failure and never a pass: `Verdict: unproven` and a stated gap |

Stops: `../../fulcrum-unattended-guardrails/references/halt-conditions.md`, headings
"Hard stops" and "Lane stops".

## Changing rigor

What rigor is and who changes it: `../../fulcrum/references/mode-and-posture.md`.

After a change, recorded `Gate` values stand: none is raised without evidence. On a
raise, list the rows now below the required gate and run what they owe. On a lower
setting, stop owing the difference and leave the record alone.

To `demo`: add the demo script row and make the final G2 depend on it. From `demo`: close it `done`/`-`.
