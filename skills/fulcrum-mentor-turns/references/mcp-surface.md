# ODC MCP surface - the dated record

The single place Fulcrum records what the live OutSystems MCP server does.
Every other file points here instead of hardcoding a tool fact. When the
surface drifts, this file and a new snapshot under `mcp-snapshots/`
change; nothing else should need to.

Last full probe: **2026-10-09** (snapshot `mcp-snapshots/2026-10-09.md`).
Last drift check: **2026-10-16**, names plus five loaded schemas
(`publish_status`, `env_app`, `mentor_get_run`, `mentor_prompt`,
`mentor_create_asset`); names baseline now `mcp-snapshots/2026-10-16.md`.
Re-probe owed since: **2026-10-16** (drift found: five names gone; no
throwaway-app run done). While this line stands, mutating work must first run
the full re-probe below, or the user accepts the risk explicitly and that
acceptance is recorded in `DECISIONS.md`. Remove this line only in the change
that adds the re-probe's snapshot and moves "Last full probe".
(Fulcrum rule.)

How to read the rows. Every fact carries an evidence tag (vocabulary:
`../../../CONVENTIONS.md`, "Hard rule 4"), the date it was observed, and its
source:

- **probe** - a live throwaway-app run (create, answer-back, change, publish,
  published-state inspection) on 2026-10-09. One run: facts seen only there
  are `[SINGLE-OBSERVATION]`.
- **field** - observed during real engagements, 2026-10-07 to 2026-10-09,
  across more than one project. Combined with the probe, these reach
  `[VERIFIED]`.
- **schema** - the server's own tool schema or description text. Tagged
  `[SCHEMA]`. Server descriptions have been observed stale (see "Tool
  families"), so a description is never proof of behaviour.
- **server instructions** - the cross-tool invariants the server publishes
  with its tool list. Tagged `[SCHEMA]`.

## Tool families

| Fact | Tag | Observed | Source |
|---|---|---|---|
| Families: `mentor_*` (9), `context_*` (10), `app_*` (7), `env_*` (6), `deploy_*` (8), `extlib_*` (9), `publish_*` (2), `build_list`, `auth_status`, `submit_feedback`. 54 tools. | `[SCHEMA]` | 2026-10-16 | tool listing |
| **Absent on the 2026-10-16 listing** (listed on 2026-10-09): `db_query`, `exec_in_app`, `mentor_publish`, `test_setup_start`, `test_setup_status`. Absence may be per tenant or per server version: re-check on the owed re-probe and record per tenant in `tenant-profile.md`. Do not plan on them while absent. | `[SCHEMA]` | 2026-10-16 | tool listing |
| 2026-10-09 listing for comparison: `mentor_*` (10), `test_setup_*` (2), `exec_in_app`, `db_query`; 59 tools. | `[SCHEMA]` | 2026-10-09 | schema dump |
| Present and worth knowing: `mentor_get_event` (fetch one run event), `app_revisions` (revision list, cheap), `deploy_impact` + `deploy_impact_status` (blast-radius analysis before a promotion; read `impactKnown` before concluding), `deploy_messages` (per-deployment messages), `deploy_rollback` (needs two prior successful deploys), `extlib_contents` / `extlib_delete` / `extlib_download_source` / `extlib_download_status`. | `[SCHEMA]` | 2026-10-09 | schema dump |
| **Absent:** `app_create`, `publish_start`, `mentor_start`, `mentor_cancel` (only `mentor_cancel_prompt` exists). Any text naming these is stale. | `[VERIFIED]` | 2026-10-09 | probe tool listing; field |
| **Deprecated - `mentor_publish`:** the call returned a deprecation error (text under "Error texts") even though its schema description still described it as working. Not listed at all on 2026-10-16. Publish through a prompt instead ("Publishing"). | `[VERIFIED]` (error); absence `[SCHEMA]` 2026-10-16 | 2026-10-08, 2026-10-09 | probe plus two field reports |
| **Deprecated - `deploy_logs`:** alias of `env_deploy_history`, slated for removal. Use `env_deploy_history` or `deploy_messages`. | `[SCHEMA]` | 2026-10-09 | schema |
| **Server descriptions can be stale.** `mentor_publish` described itself as working; `build_list` still tells callers to wait on `publish_start`, which no longer exists; on 2026-10-16 the `publish_status` description still names `mentor_publish` as the source of the key although that tool no longer lists. Trust call behaviour over description text. | `[VERIFIED]` (2026-10-09); `publish_status` text `[SCHEMA]` | 2026-10-09, 2026-10-16 | probe vs schema |
| **`mentor_request_upload` is not an image path.** Params `sessionId`, `fileName`, `sizeBytes` (1 byte to 10 MB); it mints a presigned PUT URL whose `attachmentId` a `mentor_prompt` then references. Allowed extensions: `.txt .pdf .json .xml .docx .md` - no image format. Whether an uploaded attachment can become an image resource in the app is not stated and not tested. | `[SCHEMA]` | 2026-10-16 | schema |
| `deploy_start` and `deploy_rollback` state that shipping to Production needs explicit user confirmation first; `deploy_impact` may inform that confirmation. | `[SCHEMA]` | 2026-10-09 | schema |

## Creating and loading an asset

| Fact | Tag | Observed | Source |
|---|---|---|---|
| Sequence: `mentor_start_session` (no params, returns `sessionId`), then exactly one of `mentor_create_asset` or `mentor_load_asset`, then `mentor_prompt`. No asset mutation is possible before create or load. One asset per session. | `[SCHEMA]` | 2026-10-09 | schema |
| `mentor_create_asset` params: `sessionId`, `assetType` (`WebApplication`, `Agent`, `Library`, `Workflow`), `name`, optional `description`, `portfolioKey`, `templateAssetKey`. Returns `{sessionId, applicationKey}`. | `[SCHEMA]` | 2026-10-09 | schema; probe |
| **`portfolioKey` is required in practice** although the schema marks it optional: omitting it fails with "Portfolio ID is required." Source it from `env_list` (each environment row carries `portfolioKey`) and record it in `tenant-profile.md`. | `[VERIFIED]` | 2026-10-09 | probe; field |
| A created `WebApplication` is template-backed, not blank: a set of login and account screens in one UI flow and an app-named role, no default screen configured. Exact screen set is template-dependent - read it back, do not assume. | `[VERIFIED]` | 2026-10-08, 2026-10-09 | probe; field |
| **A created asset is unreachable outside its session until its first publish:** `app_info` 404, `app_revisions` "Asset not found", `env_app` `app_not_deployed_in_environment`, `mentor_load_asset` "not found", every `context_*` total 0. | `[SINGLE-OBSERVATION]` | 2026-10-09 | probe |
| Consequence: publish once early - right after the first change turn lands - before the session is closed or abandoned. Closing the session before that first publish loses the asset. | `[UNVERIFIED]` (inferred from the row above; not tested) | 2026-10-09 | inference |
| `mentor_load_asset` params: `sessionId`, `assetKey`, optional `revision` (defaults to latest). Loading an asset the session already holds returns the held copy, edits included. | `[SCHEMA]` | 2026-10-09 | schema |
| Asking Mentor (by prompt) to reload the asset replaces the held copy with the latest published revision and **permanently discards the session's unpublished changes**. Only on explicit user intent. | `[SCHEMA]` | 2026-10-09 | schema |
| **Capacity throttle on load:** the first `mentor_load_asset` of a session has failed with "A lot of people are currently using Mentor. Try again in a moment." (3 times in one project, 5 times over ~6 minutes in another). A new session later succeeded. `mentor_start_session` and `mentor_close_session` kept working throughout. | `[VERIFIED]` | 2026-10-07, 2026-10-08 | two projects' state records (3 failed loads; 5 failures over ~6 min); not encountered in the 2026-10-09 probe |
| **Fulcrum rule, not a platform fact:** on that capacity text, retry the load at most 3 times with growing backoff (about 30 s, 60 s, 120 s), each wait using a mechanism verified to block. Still failing: close the session, halt, report it as a capacity stop - not as a model or auth failure, and not as a trap. | Fulcrum rule | - | - |

## Sessions and context

| Fact | Tag | Observed | Source |
|---|---|---|---|
| **No session token.** No token field in any response, no token parameter on any call. The `sessionId` alone identifies the session. | `[SCHEMA]`; absence also seen in every response of the probe `[SINGLE-OBSERVATION]` | 2026-10-09 | schema; probe |
| **No fresh-context parameter.** `mentor_prompt` takes only `sessionId`, `message`, `attachmentRefs`. | `[SCHEMA]` | 2026-10-09 | schema |
| Every event of every run in one session carries the same `conversationId`; a later run knew what an earlier run built. **One session is one conversation.** | `[SINGLE-OBSERVATION]` | 2026-10-09 | probe, 3 runs |
| Therefore the only way to get fresh context is: close the session, start a new one, load the asset again. | `[SINGLE-OBSERVATION]` (follows from the two rows above) | 2026-10-09 | probe; schema |
| One prompt runs at a time per session; a `mentor_prompt` sent while one is running is **silently ignored**. | `[SCHEMA]` | 2026-10-09 | schema (carried from fulcrum-unattended-guardrails; no dated field observation here) |
| `mentor_cancel_prompt(sessionId, runId)` cancels only if `runId` is the current run, otherwise no-op; the session stays open. `mentor_close_session(sessionId)` cancels any in-flight run, releases the workspace context, and makes the `sessionId` unusable; returns `{sessionId, closed: true}`. | `[SCHEMA]`; close observed `[SINGLE-OBSERVATION]` | 2026-10-09 | schema; probe |
| Reading a run on a closed session fails with the closed-session text under "Error texts". | `[SINGLE-OBSERVATION]` | 2026-10-09 | probe |
| Sessions are garbage-collected after ~30 minutes idle, losing unpublished changes. | `[UNVERIFIED]` (another catalog's claim; not observed here) | - | upstream documentation |

## Reading a run

| Fact | Tag | Observed | Source |
|---|---|---|---|
| `mentor_prompt` returns at once: `{sessionId, runId, status: "working", pollIntervalMs}`. | `[SINGLE-OBSERVATION]` | 2026-10-09 | probe |
| `mentor_get_run` params: `sessionId`, `runId`, `cursor` (optional). There is no detail-level or event-limit parameter. | `[SCHEMA]` | 2026-10-09 | schema |
| Without `cursor`, a read returns only events not yet delivered. Pass the previous `nextCursor` to re-read from there, or `0` to re-read from the start. | `[SCHEMA]` | 2026-10-09 | schema |
| Response: `runId`, `status`, `events[]`, `pollIntervalMs`, `nextCursor` (absent on the last page), `hasMore`, `truncatedEventCount`, `result`. Status values: `working`, `succeeded`, `failed`, `cancelled`, `not_found`. | `[SCHEMA]`; shape seen `[SINGLE-OBSERVATION]` | 2026-10-09 | schema; probe |
| The pacing field is **`pollIntervalMs`** (1000 while working, 0 at the end). There is no `pollAfterMs`. Fulcrum overrides it upward - see `../SKILL.md`, heading "Polling". | `[SINGLE-OBSERVATION]` | 2026-10-09 | probe |
| **`status: succeeded` can arrive with `hasMore: true`.** A run is not read until a page returns `hasMore: false` with no `nextCursor`. A poller that stopped on the first terminal page reported an unread tail by paraphrase. | `[VERIFIED]` | 2026-10-09 | probe; field |
| The server's own terminal rule: keep polling until status is terminal **and** `nextCursor` is null. | `[SCHEMA]` | 2026-10-09 | schema |
| Events are JSON-encoded strings, each with `MsgType`. Seen: `reasoning`, `conversationInfoUpdated`, `text` (answer streamed as per-token chunks with `chunkSequenceNumber`), `status` (`statusType: Completed`), and the publish events under "Publishing". | `[SINGLE-OBSERVATION]` | 2026-10-09 | probe |
| Drain cost: a long answer streamed as ~160 events, about 8k tokens to read across two pages. Budget answer-back turns accordingly; skip `reasoning` events when only the answer matters. | `[SINGLE-OBSERVATION]` | 2026-10-09 | probe |
| Oversized events arrive as truncation markers (`_truncated` / `_eventId`); fetch the full body with `mentor_get_event(sessionId, runId, eventId)`, which returns `{runId, eventId, found, body}`. No marker has been seen live; the call itself worked with `eventId` acting as a 0-based index into the run's events. | `[SCHEMA]`; call `[SINGLE-OBSERVATION]` | 2026-10-09 | schema; probe |
| An event with `MsgType` `assetCompareRequested` is a request to the caller (open a Studio compare), not progress. Not seen live. | `[SCHEMA]` | 2026-10-09 | schema |

## Publishing

| Fact | Tag | Observed | Source |
|---|---|---|---|
| **Publish is a `mentor_prompt` with the message "Publish"**, polled like any other run. | `[VERIFIED]` | 2026-10-08, 2026-10-09 | probe; field |
| The Publish run emits `publishStarted`, `publishAccepted{revision, publicationKey}`, `pendingModelChanges`, `publishSucceeded{revision}`, then a text confirmation. | `[VERIFIED]` | 2026-10-08, 2026-10-09 | probe; field |
| **The `runId` is not the publication key.** The key is only in the `publishAccepted` event. Record both. | `[VERIFIED]` | 2026-10-08, 2026-10-09 | probe; field |
| Poll `publish_status` with the publication key; the `publication_id` parameter worked (aliases `publication_key`, `publish_key` exist). Seen: `status: Finished`, `outcome: success`, `applicationRevision`. Gate on `outcome` (`in_progress`, `success`, `build_engine_error`, `unknown`), not on `status`. | `[VERIFIED]` (call); outcome vocabulary `[SCHEMA]` | 2026-10-08, 2026-10-09 | probe; field; schema |
| `publish_status` schema: three optional string params `publication_id`, `publication_key`, `publish_key`, all resolving to the same lookup; exactly one is required. The server instructions name `publication_key` (the payload's `key`); any of the three is valid. | `[SCHEMA]` | 2026-10-16 | schema; server instructions |
| An `unknown` outcome is never success. `unknown` with `indeterminate: true` plus a `publish_advisory` means the outcome was never observed: poll again or verify with `env_app`; never re-publish on it. | `[SCHEMA]` | 2026-10-16 | schema |
| **Every publish lands in the tenant's Development environment** (the `env_list` row whose `purpose` is `Development`). Other environments are reached only by a separate `deploy_start` promotion, on user request. | `[SCHEMA]` | 2026-10-16 | server instructions; schema |
| **Confirmation gate: `env_app {env_key: <Development key>, key: <applicationKey>}` and its `revision` must equal the publication's `applicationRevision`.** A `success` outcome alone does not prove the change deployed; any other `revision` means it did NOT land. This is the gate Fulcrum uses. | `[SCHEMA]` | 2026-10-16 | server instructions; schema |
| A `Workflow` and a library are invisible to the deployed inventory. `env_app` on a `Workflow` errors: `asset_type_not_listable_by_env_app` (deployed in that env; confirms deployment, not revision) or `app_not_deployed_in_environment` (not deployed); branch on the `[code: <value>]` suffix of the error text. Confirm a library change through a consumer of it. | `[SCHEMA]` | 2026-10-16 | server instructions; schema |
| No publish is retried on the transport and nothing serializes publishes of one app. | `[SCHEMA]` | 2026-10-16 | server instructions |
| The publish completed inside its run (~50 s); `publish_status` was already terminal on its first read. The Publish run is the main wait; `publish_status` is confirmation. | `[SINGLE-OBSERVATION]` | 2026-10-09 | probe |
| After success, `env_app {key, env_key}` returns the runtime `url`, `revision`, `buildKey`, `deploymentKey`; `deploymentKey` equalled the publication key. Not contradicted on 2026-10-16, but supporting evidence only: the gate is the `revision == applicationRevision` row above. | `env_app` `[VERIFIED]`; key equality `[SINGLE-OBSERVATION]` | 2026-10-09 | probe; field |
| A change turn did not publish: no publish events, revision unchanged. | `[SINGLE-OBSERVATION]` | 2026-10-09 | probe |
| A change turn **did** appear to publish on its own once (revision moved, a later "Publish" answered "nothing new to publish"). | `[SINGLE-OBSERVATION]` | 2026-10-09 | field |
| Fulcrum rule from the two rows above: before sending "Publish", read the revision (`app_revisions` or `env_app`); publish only if it did not move since the last recorded publish. First-publish carve-out: on a created, never-published asset that read errors ("Creating and loading an asset"); no revision yet means first publish - send the Publish turn, the read error is not a blocker. | Fulcrum rule | - | - |
| Never publish again while the previous publish of that app is non-terminal - two revisions building at once can crash the build engine and wedge the app. | `[SCHEMA]` | 2026-10-09 | server instructions |
| A `failed` publish carrying an `OS-*` build-engine code is the build's own result: surface the code, do not re-publish blindly. | `[SCHEMA]` | 2026-10-09 | server instructions |
| A `failed` with `indeterminate: true` means the outcome was never observed and the build may still succeed: re-poll with the publication key or verify the deployed inventory; **never** re-publish on it. | `[SCHEMA]` | 2026-10-09 | server instructions |
| `publish_logs(pub_key)` returns the publication's `OS-DPL-*` messages. | `[SINGLE-OBSERVATION]` | 2026-10-09 | probe |
| Mentor volunteers unrequested offers to publish after a fix turn. | `[SINGLE-OBSERVATION]` | 2026-10-08 | field |

## Published-state inspection (context_*)

| Fact | Tag | Observed | Source |
|---|---|---|---|
| `context_*` reflect **published state only** - never the session's working model. An unpublished edit is invisible to them. | `[VERIFIED]` | 2026-10-08, 2026-10-09 | probe; field |
| **Index lag after publish:** 0 rows ~20 s after the publish, full rows at ~110 s (index timestamp ~67 s after deploy). Wait at least 2 minutes after a publish before asserting on `context_*`, and re-read once before calling an absence real. | `[VERIFIED]` (lag, probe) | 2026-10-08, 2026-10-09 | probe |
| A fresh-shell liveness gate once reported a false FAIL inside that lag window; it passed on re-read. | `[SINGLE-OBSERVATION]` | 2026-10-08 | project state record |
| Default page size is 20 for owned queries. | `[VERIFIED]` | 2026-10-09 | probe |
| Owned elements only (`owned_only`): inherited or referenced entities that Mentor lists do not appear in `context_entities`. | `[SINGLE-OBSERVATION]` | 2026-10-08 | project state record |
| **Access flags on template screens disagree with Mentor.** `context_screens` reported every template screen non-public with the app role, while Mentor reported four of them anonymous. Do not derive screen access from `context_screens` alone; prove access by behaviour (an anonymous request to the screen). | `[VERIFIED]` | 2026-10-08, 2026-10-09 | probe; field |
| Settings and consumed REST structures have no `context_*` view. | `[SINGLE-OBSERVATION]` | 2026-10-08 | field |

## Completion signals

| Fact | Tag | Observed | Source |
|---|---|---|---|
| `result` on a change or answer turn: `{attemptedChange, changeApplied, validation{errorCount, warningCount, firstMessages}}`. Field names are camelCase. | `[SINGLE-OBSERVATION]` | 2026-10-09 | probe |
| `attemptedChange` was `true` on a read-only question. It carries no signal - never read it. | `[SINGLE-OBSERVATION]` | 2026-10-09 | probe |
| `changeApplied` is weak. Carried from `../../fulcrum-verification/SKILL.md`: the flag can read `true` on a turn that changed nothing, and a no-change flag can appear on a turn that did land a change (`[VERIFIED]` there). The 2026-10-09 probe did not reproduce the false-positive: it saw `false` on read-only and Publish turns (Publish run: both flags `false`, no `validation` key). | `[VERIFIED]` (carried); probe `[SINGLE-OBSERVATION]` | 2026-10-09 | fulcrum-verification; probe |
| Neither flag, nor 0 validation errors, nor a clean publish proves a change landed. Proof is `../../fulcrum-verification/SKILL.md`'s. | `[VERIFIED]` | source builds | field |

## Error texts

Verbatim, for matching. Tag and source as noted.

| Text | Meaning | Tag |
|---|---|---|
| `Portfolio ID is required.` | `mentor_create_asset` without `portfolioKey` | `[VERIFIED]` |
| `The mentor_publish tool is deprecated and is no longer available. Use mentor_prompt with the message "Publish" instead.` | `mentor_publish` called | `[VERIFIED]` |
| `A lot of people are currently using Mentor. Try again in a moment.` | capacity throttle, seen on `mentor_load_asset` | `[VERIFIED]` |
| `The workspace session has been closed and can no longer be used. Start a new session before calling this tool.` | any session call after close | `[SINGLE-OBSERVATION]` |
| `Asset with key '<key>' not found.` | `mentor_load_asset` on an unpublished created asset (or a wrong key) | `[SINGLE-OBSERVATION]` |
| `OS-APPS-40401 Asset not found [code: revisions_rejected]` | `app_revisions` before first publish | `[SINGLE-OBSERVATION]` |
| `app_not_deployed_in_environment` | `env_app` on an asset never published to that environment | `[SINGLE-OBSERVATION]`; `[SCHEMA]` |
| `asset_type_not_listable_by_env_app` | `env_app` on a deployed `Workflow` | `[SCHEMA]` |
| `invalid_env_key` | `env_key` is not one of this tenant's environments; pick one from `env_list` and retry | `[SCHEMA]` (server instructions, 2026-10-16) |
| `data.category: "ThrottledError"`, `data.code: "repeated_failure_throttled"` | that exact call failed upstream the same way several times in a short window and was throttled; do not repeat it unchanged (rest of the instruction text was truncated when read on 2026-10-16) | `[SCHEMA]` (server instructions, 2026-10-16) |
| `tenant_not_allowed` | an allowlist gate, not a lapsed sign-in: re-auth and re-registering fail the same way. Confirm the configured host is the tenant meant (a wrong tenant host returns this too); if it is, stop and say the tenant needs enabling | `[UNVERIFIED]` (vendor skill text, 2026-10-16; not observed) |

## Re-probing the surface

The surface has changed under Fulcrum before, silently. Two checks, cheap
first.

**Drift check - every session start, read-only, seconds.** List the live
tool names and compare them against the latest file in `mcp-snapshots/`;
do not load schemas to do it. An added or removed name is drift. Also read the
"Re-probe owed since" line at the top of this file: while it stands, the check
does **not** pass for mutating work even when the names match the latest
snapshot, because that snapshot is itself the unreprobed drift. Compare
parameters only when a name changed or a call fails schema validation, and
delegate that diff to a read-only investigator so the orchestrator never
loads every schema (`../../fulcrum/references/tool-preflight.md`). No
difference: the rows above stand. Do not compare descriptions; they drift without behaviour
changing and are not evidence.

**On drift - full re-probe before any mutating work.** Drift was found on
2026-10-16 and this re-probe is still owed (the "Re-probe owed since" line at
the top). Run it on a throwaway app in a non-production environment, never on
a real one:

1. Dump the full schema of every tool and write it as a new dated snapshot in
   `mcp-snapshots/<YYYY-MM-DD>.md`, same format as the baseline.
2. Call any tool this file marks deprecated or absent that still lists, and
   record what the call actually returns.
3. Start a session and create a throwaway asset. Record what create requires
   and returns, and what is reachable outside the session before publish.
4. Run one answer-back turn. Record the run's response shape, pacing field,
   paging fields, event types, completion flags, and draining cost.
5. Run one small change turn (one static entity is enough). Record whether it
   publishes on its own.
6. Publish by whatever mechanism the surface now offers. Record the event or
   response that carries the publication key, and confirm with the publish
   status tool and the deployed-app read.
7. Read published state with `context_*` immediately and again after two
   minutes. Record the lag.
8. Close the session; leave the throwaway app identified as such.
9. Update every row above that changed, with the new date, tag and source.
   Update the "Last full probe" line and remove the "Re-probe owed since"
   line in the same change. Then tell the orchestrator which rows
   changed, so files citing them can be checked.

Do not drive Mentor against an unrecorded surface: a drift touching a tool
the current plan depends on means halt and report until this file is
updated (halt rules: `../../fulcrum-unattended-guardrails/SKILL.md`).
