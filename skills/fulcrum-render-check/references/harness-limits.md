# Harness limits and false defects

Detail for `../SKILL.md`, heading "The procedure". Each row is something a
render does that looks like an app defect, or a browser limit that makes an
assertion undrivable. Report the observation and the limit; the orchestrator
judges. Tool and parameter names are one browser's; the capability is what
matters (`HARNESS-NOTES.md` in the Fulcrum repo for per-harness detail).

## Looks like a defect, is not

| Symptom | Mechanism | Do |
|---|---|---|
| Banner or timeout on the first sign-in or first server call after idle | The first call into a cold backend can exceed the client call timeout `[VERIFIED]` | Retry once after a short wait; record both tries as one cold-start observation. A second failure is an observation of the app |
| First click on a sample sign-in button does nothing, shows a required-field message | The button is a submit button, so the first click ran form validation instead of signing in `[VERIFIED]` | Report it; do not click around it. The fix is a build row (`../../fulcrum-engine-traps/references/sample-signin.md`) |
| Send fails, a stylesheet or script 404s, behaviour that the live revision should not have | The browser served a cached client bundle from an earlier revision `[VERIFIED]` | One hard refresh, then re-check. If it clears, record "stale bundle after publish", not a defect, and spend no fix turn. A new device or profile needs the same refresh on first load |
| Content present in the DOM but the layout area blank (low opacity) on the first load | First load in a hidden or backgrounded tab `[SINGLE-OBSERVATION]` | Reload once while the page is foregrounded before recording a blank layout |

## Session identity

- A browser profile keeps its last session. Before any anonymous or persona
  assertion, read the signed-in state first; if an identity from an earlier run
  or another person is present, sign out through the app and confirm, or the
  run's results belong to that identity `[VERIFIED]`.
- The header logout control sometimes does nothing where an in-page logout link
  works `[SINGLE-OBSERVATION]`. Try the other; an unconfirmed sign-out still ends
  the run.
- A role-gated app has no authenticated render until the user holds the role
  in Development. Ask for the grant when the plan is made, not when the render
  is due; it is a user action, never the renderer's `[SINGLE-OBSERVATION]`.

## Inputs the browser cannot drive reliably

- **File inputs.** An upload capability can report success while a hidden file
  input still holds no files `[VERIFIED]`. Do not retry it. An upload-bearing
  assertion is `untested` unless the brief grants an in-page file build (a small
  valid image generated in the page and attached to the input, which worked once
  `[SINGLE-OBSERVATION]`), or the submit path is proven another way (a gated
  diagnostic endpoint, or a user step). Never push base64 through a prompt or
  a page script (it corrupts), and never start a local server for the page to
  fetch from: a secure page is blocked from fetching a local plain-HTTP address.
- **Text entry.** A value set by a form-fill capability may not reach the
  OutSystems model, so the next action acts on the old value `[VERIFIED]`. Use
  real keystrokes for any field whose value an action will read, then confirm by
  an effect (dependent text, a saved value).
- **Dropdowns.** Click plus arrow key left the value unchanged where the
  select/fill capability set it `[SINGLE-OBSERVATION]`; confirm either way by an
  effect, and retype by keystroke when the model did not follow.
- **Snapshots omit controls.** Some buttons are missing from an accessibility
  snapshot `[VERIFIED]`. Find the control with a read-only DOM query and click
  it through the click capability by a stable selector. A page script that
  clicks is a change to interaction, not a measurement: report that the
  control was not reachable by the capability and stop that assertion unless the
  brief grants a script click by name.
- **Viewport floor.** One browser clamped width to about 500 px
  `[SINGLE-OBSERVATION]`. Record the width actually reached; never label a
  capture as a phone width the browser did not give.
- **Budget.** A run of 30 to 70 browser calls was typical; brief few assertions
  per dispatch `[SINGLE-OBSERVATION]`.

## Both roles after a shared edit

A step that edits a shared layout, header, role-aware link or the logic that
links a user to a record can regress the screens of the other role, and one
fix once created a duplicate user-linked row `[VERIFIED]`. Brief a render per
role the shared asset serves, not only the role of the changed screen.

## Hygiene

Kill nothing the renderer did not start, and start no process of its own. A
background server left running cannot be stopped under a permission classifier
`[SINGLE-OBSERVATION]`.
