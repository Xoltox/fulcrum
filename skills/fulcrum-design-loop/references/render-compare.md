# Render-compare - rung 6, design variant

Runs for a screen row when `project.md` has `design` set. It adds the reference
image, the judge, the diff vocabulary and the triage to
`../../fulcrum-render-check/SKILL.md` (executing a render) and
`../../fulcrum-verification/references/visual-verification.md` (reading a capture).

## When

After the step's Publish passes the publish gate (`env_app` revision equals the
publication's `applicationRevision`; `../../fulcrum-mentor-turns/references/mcp-surface.md`,
heading "Publishing") and the lag wait in render-check's "When to run". A compare
against the previous revision proves nothing about this one.

## 1. Capture

Brief `fulcrum-renderer` per render-check's "The procedure", step 1, plus:

- viewport(s) from `manifest.md` - one capture per form factor;
- access mode per screen from batch B Q2 and Q4 (anonymous, approved persona, or user
  hand-off);
- capture the full scroll container, not the window - an internal scroll container
  clips the screenshot (`visual-verification.md`, "The capture trap, generalised");
- screenshots allowed only per the batch B Q5 answer;
- evidence into `.fulcrum/evidence/render/<task-id>/<UTC-stamp>/`.

**Tier B:** the orchestrator adds a `manual` row, parked `Blocked on: the user`: "Send
a screenshot of `<screen>` at `<viewport>`, signed in as `<role or public>`". It files
the image as received at `design/user-shots/<SID>-r<n>.<ext>` (round `n`), never under
`evidence/render/`, which is the renderer's alone
(`../../fulcrum-project-state/references/file-schemas.md`, "Write ownership"), and
notes in the fidelity file that the user captured it.

## 2. Judge

Dispatch a **fresh, blind** `fulcrum-verifier` with an image-inspection capability.
Its brief contains only:

- the reference image (`design/reference/<SID>.<ext>`; for a whole image, the
  manifest's note naming which part is the screen);
- the capture(s) and the render `report.md` (tier B: the user's screenshot from
  `design/user-shots/`, no render report);
- the screen's F-items from `screens/<SID>.md`, Acceptance section;
- the fidelity bar from `manifest.md`;
- the diff vocabulary below.

Never the builder's report, the capture reasoning, the anatomy rationale, or an
earlier round's triage: a judge that knows what was intended sees it. (Fulcrum rule)

It returns, per F-item, `OK | FAIL | PARTIAL | untested`, then a diff list
(`class | location | expected | observed`), then what it could not judge.

## 3. Diff vocabulary and severity

| Class | Covers | At bar (a) structural | At bar (b) visual |
|---|---|---|---|
| `structure` | Missing or extra region, wrong block, wrong order | blocker | blocker |
| `data` | Empty list/chart/KPI, literal binding path shown, wrong value, duplicate rows | blocker | blocker |
| `icon` | Missing, fallback glyph, invisible on its surface | major | major |
| `size` | Wrapping, overflow, collapsed chart | major | major |
| `token` | Colour, type, radius | minor | major |
| `spacing` | Gaps, padding, margins | minor | major |
| `copy` | Text differs from the source | minor, unless an F-item names it (then major) | same |

A value marked `~` in `tokens.md` is compared loosely: drift within what the source
can show is not a diff. (Fulcrum rule)

## 4. Triage - the orchestrator

- blocker and major -> fix candidates; minor -> `design/backlog.md`.
- **Pattern:** a diff on 2+ screens, or caused by a theme class, token or chrome
  element. One `fix` row on the owning step (P1.02 theme or P1.03 chrome), then
  re-compare **every** affected screen, passed ones included. Fixing a shared cause per
  screen wastes turns and lets the copies drift
  (`visual-verification.md`, "Screenshot comparison against a reference design").
- A pattern fix that regresses a passed screen is a halt
  (`../../fulcrum-unattended-guardrails/SKILL.md`).

## 5. Fix rounds

Each round is a new driver dispatch on a `fix` row of the same `Step`; the build
session closed at Publish.

1. **Diagnostic first** - a published-state read or a verbatim read-back of the node
   (`../../fulcrum-unattended-guardrails/references/halt-conditions.md`, "The diagnostic
   step is not optional").
2. A fix turn led by the measured symptom ("the table renders one row; the capture
   shows ..."), not by a restated spec.
3. Publish, publish gate, lag, re-render, re-judge with a fresh verifier: round r2.

**At most 2 compare rounds per screen**, inside the step's 2 fix turns. A diff
surviving round 2, or the fix cap, -> the row's verdict is `fail` and the guardrails
halt path runs. The loop engine's oscillation scan covers repeats across sessions
(`../../fulcrum-loop-engine/references/oscillation-and-fix-loop.md`).

## 6. Record

Write `design/fidelity/<SID>-r<n>.md` from `../templates/fidelity.md`: the verifier
report fenced verbatim, then the triage table (`diff | class | severity | fix | pattern
| backlog | task id`), then the verdict:

- `pass` - every F-item OK at the bar;
- `fail` - a blocker or major diff after the last allowed round;
- `unproven` - a rung untested, with the reason.

The row's `TASKS.md` `Verdict` is the orchestrator's, from this file.

## Tier C - no render instrument

Per screen: `context_screens` after the index lag; a verbatim Mentor read-back per
region (rung 1 - belief, not proof); `context_themes` content if it exposes CSS
(`[UNVERIFIED]`, probe once and record the answer in `tenant-profile.md`); seed proof
per `../../fulcrum-seed-data/SKILL.md`, "Verifying a seed". Every screen is
`unproven`, reason "visual untested".

Render-only defect classes lead the report, because nothing in tier C can see them:
repeater collapse, collapsed overlay, dark-on-dark icon, empty chart, wrapped metric.

Curl or any HTTP fetch is never a render: it does not run a client-side ODC screen
(`../../fulcrum-verification/SKILL.md`, heading "Render obligation").
