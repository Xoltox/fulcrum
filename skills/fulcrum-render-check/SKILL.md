---
name: fulcrum-render-check
description: Renders a published ODC screen in a real browser and captures what a user actually sees, signed out or signed in, so proof rungs 6-7 and the render obligation stop being reported untested. Owns the browser preflight, the sign-in mode choice (anonymous, generated sample personas, user hand-off), render timing after a publish, evidence capture, and the security observations a render surfaces. Use when asked to "render the screen", "check the page actually shows", "does the new screen load", "is this screen public", "prove access for this role", "take a screenshot of the app", "run the render obligation", "click it and check it persisted", or after any publish that added or changed a screen.
version: "1.0.0"
requires: A browser automation capability that can open a page, read page text and a DOM or accessibility snapshot, take a screenshot, click, and read console output where available (whatever browser MCP the harness has - e.g. firefox-devtools, Claude in Chrome, Claude's built-in browser, Playwright or Chrome DevTools MCP - or a headless driver otherwise); ODC MCP published-state reads (env_app, context_screens, context_search, context_roles); a wait that actually blocks; write access to the project's .fulcrum/ evidence folder.
---

# fulcrum-render-check

## Boundary

This skill owns **executing a render and recording what it showed**. It does
not own what counts as proof or which rungs a change needs
(`../fulcrum-verification/SKILL.md`), how to read a capture without fooling
yourself (`../fulcrum-verification/references/visual-verification.md`), why a
construct renders wrong (`../fulcrum-engine-traps/SKILL.md`), or seeding the
rows a list should show (`../fulcrum-seed-data/SKILL.md`).

The executing role is `fulcrum-renderer`. It reports **observations**; the
orchestrator (or the blind `fulcrum-verifier` reading the evidence) gives the
verdict. A renderer that grades its own capture is the builder marking its own
work. (Fulcrum rule)

## When to run

- **After the step's publish passes the publish gate**, never before. The
  Mentor driver ends every mutating step with its own Publish turn; the gate
  is `env_app` live `revision` equal to the publication's
  `applicationRevision` (`../fulcrum-mentor-turns/references/mcp-surface.md`,
  heading "Publishing"). Then allow about 2 minutes: that figure is the
  `context_*` index lag (same file, heading "Published-state inspection
  (context_*)"); that runtime page loads lag the same way is an inference
  `[UNVERIFIED]`, which is why the procedure also retries. A render of the
  previous revision proves nothing about this one.
- **Every step that adds or changes a screen**: rung 6 for that screen.
- **Every step that creates an app or adds screens**: the render obligation -
  the default screen signed out, plus one authenticated screen.
- **Every access claim**, anonymous and signed-in. `context_screens` access
  flags on template screens have disagreed with Mentor `[VERIFIED]`; only a
  render proves who can reach a screen.
- **Rung 7 and functional checks** (fill a form, search, trigger validation,
  walk a flow; click, reload, confirm persisted) when the brief permits the
  renderer to change data, with the record prefix it may create.

**Data-changing interactions** - submitting a form that creates, updates or
deletes a record, an upload - only when an assertion requires it, only in the
Development environment, never on a Test or Production URL, and each one
recorded in `report.md` (what was created or changed) so the test data can be
cleaned up. Typing into an ordinary field (a search box, a form under test) is
not itself a data change. (Fulcrum rule)

## Preflight - once per project

1. Does this harness give a delegable role a browser automation capability,
   and through which browser? The orchestrator does not probe it itself (it
   never runs browser automation): dispatch `fulcrum-renderer` with a
   probe-only brief (open a blank or public page, read a snapshot, close it,
   report the browser tool set and which capabilities it covers).
2. Record the result per project, not per tenant, because the harness and
   its browser can differ between projects: `project.md` field `browser` -
   the state (callable, unavailable, unknown), the browser tool set, the
   capabilities it covers, and the date. A capability the browser lacks makes
   that observation "not available in this browser" in every report, never
   clean.
3. **Unavailable:** rungs 6-7 and the render obligation stay `untested` with
   the reason "no browser capability". Ask the user to render (a screenshot or
   a confirmation). Never substitute an HTTP 200, a text fetch or a model
   read-back for a render, and never claim one happened.
4. Per app, record whether the generated sample sign-in pattern is present
   (below). It is an app fact, so re-check it when the Login screen changes.
5. **Screenshots: ask first.** Before the first render in the project, ask the
   user whether render screenshots are committed or kept out of the
   repository, and record the answer in `DECISIONS.md` (heading "Evidence"
   below).

## Sign-in modes - in order of preference

Pick the first mode that can prove the claim. Full detection steps and
caveats: `references/sign-in-modes.md`.

| Mode | Use for | Detect | Never |
|---|---|---|---|
| a. Anonymous | Screens meant public; proving a screen is NOT public (expect a redirect to Login or InvalidPermissions) | Always available | Treat a redirect as a pass when access was expected |
| b. Generated sample personas | Signed-in renders in **Dev only**, on apps that kept the generated Login screen | Published-state reads for the generated actions and the "Log in as ..." buttons | Enable without the user's recorded decision |
| c. User hand-off | Any signed-in render mode b cannot cover | The user signs in in the shared browser, or confirms an existing session | Type a credential, or script around a blocked one |
| d. None | - | Neither b nor c available | Report anything but `untested` with the reason |

**Mode b is a user-policy choice.** The first click on a persona registers a
real identity-provider user and grants it a role `[SINGLE-OBSERVATION]`
(read from the model, not exercised). Ask once per project; the orchestrator
records the answer in `DECISIONS.md`. Absent a recorded yes, mode b is off.
(Fulcrum rule)

**Choosing a persona.** Read the target screen's roles (`context_screens`),
then pick the least-privileged persona whose role is on that list, so a
pass is not an admin bypass. For a negative access check pick a persona
whose role is not on it and expect InvalidPermissions. Role flags on
template screens are unreliable, so the render, not the flag, is the proof.

**No credential is ever typed** - never a password, token, API key,
one-time code or other secret, into any field, by any mechanism, and never
read from anywhere in order to enter it. A screen that needs one is a stop
and a hand-off to the user (mode c). Sign-in is by an approved sample-persona
button (a click) or a session the user signed in. This is a rule, not a tool
restriction: the renderer's browser tools can type. Some harnesses
additionally block credential entry in auto mode, including a workaround
(`[VERIFIED]`, see `../fulcrum-unattended-guardrails/references/delegation.md`,
heading "A UI check behind a sign-in is a user-action hand-off"). (Fulcrum
rule)

## The procedure

1. **Brief** the renderer blind: runtime URL and screen paths, the app key
   and the Development `env_key`, the assertions as observable outcomes, the
   sign-in mode and persona per assertion, viewport(s), the evidence folder,
   the expected revision, whether it may change data, and whether screenshots
   are allowed. On the design loop the viewport(s) come from
   `.fulcrum/design/manifest.md`, and a brief may also ask for a reference
   render of a local design file (an HTML source) into the evidence folder it
   names (heading "Local-file reference render - no app"). Not the build's intent narrative. Plus everything in
   `../fulcrum-unattended-guardrails/references/delegation.md`, heading "What
   a brief must contain".
2. **Confirm live revision** with `env_app` before the first load.
3. **Lag and retry.** A 404, the previous revision's content, or a
   generic error page right after a publish is not a FAIL. Wait (a real
   blocking wait) 60 s and reload; at most 3 tries after the initial lag;
   then record the observation and stop that assertion.
4. **One page per run.** List pages first; never touch a page the renderer did
   not open (in mode c it belongs to the user). Close every page it opened.
5. **Order the modes**: all anonymous assertions first, then one persona at a
   time. Between personas sign out through the app's own logout, then confirm
   sign-out by loading a protected screen and seeing the Login redirect. If
   sign-out cannot be confirmed, stop: the next persona's results would be
   contaminated.
6. **Capture per assertion** (below), then check the render obligation list.
7. **Rung 7 and functional checks**: act, wait for the request to settle,
   reload or re-navigate, then capture again. A confirmation toast alone is
   never evidence. Data changes follow the rule under "When to run".
8. **Report** observations only; the orchestrator gives the verdict.

## Local-file reference render - no app

The design loop's HTML reference render runs in its capture phase, before any app
exists. Its brief names the local file, the viewport(s), the evidence folder
(`.fulcrum/evidence/render/design-ref/<UTC-stamp>/` while no `TASKS.md` row exists)
and whether screenshots are allowed. Steps 2 and 3 above do not apply - there is no
publish, no revision and no lag - and there is no sign-in; steps 4, 6 and 8 do. Whether
the harness's browser opens a `file://` URL is `[UNVERIFIED]`: on a refusal the
renderer reports it and the source falls to capture from code (the design loop's
tier B or C). The renderer writes only the evidence folder; copying the capture into
`design/reference/` is the orchestrator's
(`../fulcrum-design-loop/references/capture-recipes.md`, heading "Reference images").

## Render obligation - what to look for

Each is an observation to report, never to repair:

- Blank or missing layout; a shell with no content; content clipped by an
  internal scroll container (the capture trap in `visual-verification.md`).
- Placeholder or template text left on the screen.
- Broken images or icons (an image with zero natural width; an icon rendering
  nothing or a fallback glyph).
- An empty list where the brief says seed data exists.
- Error toasts or feedback messages; an error screen.
- Client-side exceptions in console output; failed network calls.
- Redirect to Login or InvalidPermissions when access was expected - and,
  just as important, the screen rendering when it was expected to be denied.

## Evidence

Folder: `.fulcrum/evidence/render/<task-id>/<UTC-stamp>/` (`<task-id>` is the
`TASKS.md` task id in both profiles). One `report.md` plus capture files. The
renderer writes only inside that folder. Per assertion: URL, mode and
persona label, viewport, screenshot path, page-text excerpt, console errors,
failed network calls, observation. Layout and report format:
`references/evidence-and-report.md`.

**Screenshots: ask first.** They can contain real data, and some projects
want them committed, so it is the user's choice. Ask before the first render
in a project; the orchestrator records the answer in `DECISIONS.md` and, if
the user wants them kept out of the repository, makes the change the user
asked for. Fulcrum never adds an ignore entry or leaves files untracked on its
own. Until the answer is recorded, a render captures page text and the DOM
snapshot only and writes no screenshot file; the report says visibility was
not captured. (Fulcrum rule)

## Security observations - surface, never fix silently

- **Sample-persona buttons visible outside Dev.** The generated picker gates
  on a hardcoded Dev domain `[SINGLE-OBSERVATION]`; a changed domain or a
  copied app can expose or hide it. Seeing it in any non-Dev stage is a
  security finding.
- **A shared sample password in client code.** The generated pattern passes
  one literal password from button handlers, so it likely ships in the client
  bundle `[UNVERIFIED]` (inferred from client-side actions; not inspected).
  Never read, quote or log the literal.
- Recommend the user decide (remove the picker, gate it differently, or
  accept for Dev). **Never promote a screen carrying these buttons without the
  user's recorded decision.** (Fulcrum rule)

## What this skill does not do

- Comparison against a design, pixel or otherwise. The design loop's
  render-compare consumes this skill's captures:
  `../fulcrum-design-loop/references/render-compare.md`.
- Load or performance testing.
- Credential entry, account creation outside mode b, or role grants.
- Diagnosis or repair of what it sees.

## Where the depth lives

- `references/sign-in-modes.md` - detecting the generated sample sign-in
  pattern from published state, persona choice, the registration side effect,
  sign-out, and the user hand-off script.
- `references/evidence-and-report.md` - evidence folder layout, the
  per-assertion record, retries, console and network capture limits, and the
  report the orchestrator reads.
