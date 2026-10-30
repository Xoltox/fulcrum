# Workflows

Mentor can build a Workflow. The traps are what it binds to unasked, and what a screen
may assume about timing. Tool facts:
`../../fulcrum-mentor-turns/references/mcp-surface.md`.

## 1. Mentor builds a Workflow end to end `[SINGLE-OBSERVATION]`

One 2026-10-30 run: app, public events and action, workflow, publish, then a live run
through a human step to `Done`, with Mentor's description of the flow matching behaviour.
This reverses an earlier "Mentor does not support Workflows" answer, so treat that answer
as stale if it comes back. The workflow editor is the Portal, not Studio.

## 2. Create it in the same session, with `assetRefs` on the app `[SINGLE-OBSERVATION]`

Publish the app first, then create the workflow in that session with `assetRefs` on the
app. It resolved the app's public events and action about 2 minutes after the app's
publish, with no index wait. Holds for a Workflow only; a library fails this way
(`mcp-surface.md`, heading "Published-state inspection").

## 3. Every workflow prompt says "Do not reference any other app in the tenant" `[SINGLE-OBSERVATION]`

**Failure mode.** Asked to resolve a workflow's validation errors, Mentor bound it to
existing events and actions of unrelated apps, unasked, with 0 errors. The workflow then
depends on those apps. It obeyed once told. Mentor also made an entity public unasked.

**Visible?** No: validation is clean, and the search that finds the foreign element looks
like success.

**Brief:** "Do not reference any other app in the tenant. Use only the elements of
`<App>`. List every dependency with its producer." Re-read the list before publishing;
`app_refs` on a workflow is not conclusive here (entities only). Ask for the entity's
`Public` flag by name.

## 4. Gate by the `env_app` code `[VERIFIED]`

`env_app` errors on a Workflow by design. `asset_type_not_listable_by_env_app` means
deployed, and says nothing of which revision. Details: `mcp-surface.md`, heading
"Publishing". Never read that error as a failed publish.

## 5. A screen must not assume a step finished `[SINGLE-OBSERVATION]`

| Moment | Observed |
|---|---|
| Event raised to first automatic activity's write | 7 s |
| Event to instance visible | about 30 s |
| Automatic activity calling an agent | 58 s cold, 6 s warm |
| Human step approved to `Done` | 9 to 68 s; one instance stayed `Active` about 17 minutes |

A screen that reads state straight after raising an event shows the old state, which
looks like a failure. Build the screen to re-read, and assert after a wait.

## 6. Event payload is capped at 2000 characters `[SINGLE-OBSERVATION]`

2001 characters is rejected at the trigger with `OS-BERT-61601` and no instance is
created. Pass a key in the event and read the rest by key.

## 7. Reading state through the System entities

- `ProcessInstance.Label` matches on exact equality; it held the process name plus the
  request id `[SINGLE-OBSERVATION]`.
- Status values were seen as `ProcessInstance` `Active`, `ActiveWithErrors`, `Done`,
  `Terminated`, and `ActivityInstance` `Open`, `Running`, `Waiting`, `Completed`,
  `Terminated`, `Error`. `HumanActivityInstance` extends `ActivityInstance`
  `[SINGLE-OBSERVATION]`.
- **These entities are tenant-wide** `[SINGLE-OBSERVATION]`: an unfiltered list shows
  other apps' instances. Filter by the process, or the screen leaks them and any count
  is wrong.
- **A multi-join aggregate returns one row per activity**, and statuses landed on the
  wrong rows after a fix `[SINGLE-OBSERVATION]`. Read with separate aggregates and check
  per row in the render.
- An empty value bound to a bigint filter failed at runtime with `OS-BERT-60407`
  `[SINGLE-OBSERVATION]`. Guard the id before the query runs.
- Mentor says an event is not matched to an instance and may close the waiting step of
  every instance `[UNVERIFIED]`. Not tested: do not plan concurrent instances on one
  event without proof.
