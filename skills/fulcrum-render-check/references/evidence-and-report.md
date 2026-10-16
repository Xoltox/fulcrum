# Evidence and report

Detail for `../SKILL.md`, heading "Evidence".

## Folder

```
.fulcrum/evidence/render/<task-id>/<UTC-stamp>/
  report.md
  <nn>-<mode>-<viewport>.png        # one per assertion, nn = assertion number,
                                    # only once the screenshot decision is recorded
  <nn>-text.txt                     # page text, when longer than the excerpt
```

- `<task-id>` is the `TASKS.md` task id, in the full and micro profiles alike.
  `<UTC-stamp>` is compact UTC, e.g. `20261016T140311Z`, so re-runs never
  overwrite earlier evidence.
- The renderer writes only inside this folder. The orchestrator links the
  folder from the session journal line; the renderer never edits journal,
  TASKS or DECISIONS files. (Fulcrum rule)
- Never write a credential, a session token, a cookie or the sample
  password literal into any evidence file. A screenshot of a page that
  displays a secret is not captured; record the reason instead.

## Per-assertion record

One block per assertion in `report.md`, every field filled (`-` when not
applicable):

| Field | Content |
|---|---|
| `assertion` | The observable outcome from the brief, verbatim |
| `url` | Requested URL, and the final URL after redirects |
| `mode` | `anonymous`, `persona:<label>`, `user-session`, or `none` |
| `viewport` | Width x height |
| `revision` | Live revision from `env_app` at render time |
| `screenshot` | Relative path, or `not taken` plus the reason (screenshot decision not yet recorded; not available in this browser) |
| `text` | A short excerpt of the page text that bears on the assertion |
| `console` | Client-side errors seen, or `none seen` plus the capture limit (below) |
| `network` | Failed requests (URL path and status), or `none seen` plus the limit |
| `tries` | Load attempts, with the wait between them |
| `data changes` | Each record created, updated or deleted and each upload, with its identifying value, for clean-up; `none` otherwise |
| `observation` | What the page showed, in the renderer's own words. No verdict |

## Capture rules

- Capture the real scroll container, not only the document (the capture trap
  in `../../fulcrum-verification/references/visual-verification.md`). Identify
  it once per app section.
- Pair every text excerpt with a screenshot when screenshots are allowed:
  text present in the DOM is not proof it is visible. Until the user's
  screenshot decision is in `DECISIONS.md`, capture page text and the DOM
  snapshot only, write no image file, and say in `observation` that
  visibility was not captured (`../SKILL.md`, heading "Evidence").
- A capability the browser lacks (screenshot, console, network, page
  scripts) is recorded as "not available in this browser" in that field,
  never as `none seen`.
- Locate elements by stable identifier or DOM structure, not by visible
  text, where several panes render the same label.
- Read-only page scripts, where the harness grants a script tool, are allowed
  for measurement only: element sizes,
  computed style, image natural width, resource timing entries. Never set
  values, submit forms, read storage or cookies, or call app endpoints.

## Console and network limits

Browser tools differ in what they expose. Some return the browser process
output rather than the page console, and resource timing entries may not
carry an HTTP status in every browser `[UNVERIFIED]`. State in the record
which source was read; "none seen" from a source that may not carry the
signal is not "none". An error toast or error screen in the DOM is captured
regardless.

## Retries after a publish

- Initial wait: none from the `context_*` index. A render does not read it,
  so its lag (variable; `../../fulcrum-mentor-turns/references/mcp-surface.md`,
  heading "Published-state inspection (context_*)") does not apply. How long a
  runtime page takes to serve the new revision after the publish gate passes
  is separate and `[UNVERIFIED]`; a brief may set an initial wait, and the
  retries below cover it.
- Then up to 3 loads, 60 s apart, each wait one that actually blocks.
- Still a 404, old content or error page: record it with every try and stop
  that assertion. The orchestrator decides whether it is lag, a failed
  deploy, or a defect.

## The report the orchestrator reads

`report.md` starts with a summary of 15 lines or fewer:

```
render: <task-id> revision <n> at <UTC>
mode(s): <modes used>; pages opened <n>, closed <n>
<nn> <assertion short name>: <observed> | <screenshot path>
...
security: <sample-persona picker seen outside Dev | none seen>
not checked: <assertion and reason, one per line, or "none">
```

`observed` is a description, never OK or FAIL. The verdict (OK / FAIL /
PARTIAL / untested) is the orchestrator's or the verifier's, written to their
own records.
