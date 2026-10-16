# ODC MCP surface - the dated record

The single place Fulcrum records what the live OutSystems MCP server does.
Every other file points here instead of hardcoding a tool fact. When the
surface drifts, this file and a new snapshot under `mcp-snapshots/`
change; nothing else should need to.

Last full probe: **2026-10-16** (snapshot `mcp-snapshots/2026-10-16.md`:
full schema load plus a throwaway-app run). Previous full probe: 2026-10-09
(`mcp-snapshots/2026-10-09.md`).

How to read the rows. Every fact carries an evidence tag (vocabulary:
`../../../CONVENTIONS.md`, "Hard rule 4"), the date it was observed, and its
source:

- **probe** - a live throwaway-app run (create, answer-back, change, publish,
  published-state inspection), done on 2026-10-09 and again on 2026-10-16. A
  fact seen in only one probe is `[SINGLE-OBSERVATION]` with that date; one
  seen in both is `[VERIFIED]` with both dates.
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
| **Absent since 2026-10-16** (listed on 2026-10-09): `db_query`, `exec_in_app`, `mentor_publish`, `test_setup_start`, `test_setup_status`. The full re-probe confirmed it: not in the full tool listing, not callable. Absence may be per tenant or per server version: record it per tenant in `tenant-profile.md`. Do not plan on them while absent. | `[SCHEMA]` | 2026-10-16 | tool listing; full re-probe |
| 2026-10-09 listing for comparison: `mentor_*` (10), `test_setup_*` (2), `exec_in_app`, `db_query`; 59 tools. | `[SCHEMA]` | 2026-10-09 | schema dump |
| Present and worth knowing: `mentor_get_event` (fetch one run event), `app_revisions` (revision list, cheap), `deploy_impact` + `deploy_impact_status` (blast-radius analysis before a promotion; read `impactKnown` before concluding), `deploy_messages` (per-deployment messages), `deploy_rollback` (needs two prior successful deploys), `extlib_contents` / `extlib_delete` / `extlib_download_source` / `extlib_download_status`. All still listed on 2026-10-16; `mentor_get_event` and `app_revisions` called on both probes. | `[SCHEMA]` | 2026-10-09, 2026-10-16 | schema dump; probe |
| **Absent:** `app_create`, `publish_start`, `mentor_start`, `mentor_cancel` (only `mentor_cancel_prompt` exists). Any text naming these is stale. | `[VERIFIED]` | 2026-10-09, 2026-10-16 | probe tool listing; field |
| **Deprecated - `mentor_publish`:** the call returned a deprecation error (text under "Error texts") even though its schema description still described it as working. Not listed and not callable on 2026-10-16, so the error can no longer be re-observed. Publish through a prompt instead ("Publishing"). | `[VERIFIED]` (error); absence `[SCHEMA]` 2026-10-16 | 2026-10-08, 2026-10-09, 2026-10-16 | probe plus two field reports |
| **Deprecated - `deploy_logs`:** alias of `env_deploy_history`, slated for removal. Still works: the call returned a normal page with no deprecation warning in the response. Use `env_deploy_history` or `deploy_messages`. | `[SCHEMA]`; call `[SINGLE-OBSERVATION]` | 2026-10-09, 2026-10-16 | schema; probe |
| **Mentor publishes do not appear in deployment history.** `deploy_logs` (`env_deploy_history`) listed only `Deploy` and `ApplyConfigs` operations; publishes into Development made by Mentor were absent. `page.totalResults` and `totalPages` came back null. Never confirm a publish from deployment history; use the `env_app` gate ("Publishing"). | `[SINGLE-OBSERVATION]` | 2026-10-16 | probe |
| **Server descriptions can be stale, and drift.** `mentor_publish` described itself as working (2026-10-09). `build_list` told callers to wait on `publish_start`, which no longer exists (2026-10-09); by 2026-10-16 that was fixed (it now says: after `publish_status` reports `success`, poll until a `Release` build is `Finished`, then pass its `buildKey` and `revision` to `deploy_start`). On 2026-10-16 the `publish_status` description still names `mentor_publish` as the source of the key although that tool no longer lists. Trust call behaviour over description text. | `[VERIFIED]` (2026-10-09); description texts `[SCHEMA]` | 2026-10-09, 2026-10-16 | probe vs schema |
| **`mentor_request_upload` is not an image path.** Params `sessionId`, `fileName`, `sizeBytes` (1 byte to 10 MB); it mints a presigned PUT URL whose `attachmentId` a `mentor_prompt` then references (`attachmentRefs`). Allowed extensions: `.txt .pdf .json .xml .docx .md` - no image format. The schema description also says: for refining an existing app, summarize the document's key requirements as text in the prompt instead. | `[SCHEMA]` | 2026-10-16 | schema |
| `mentor_request_upload` by call: returns `{attachmentId, uploadUrl, expiresAt}`. `attachmentId` is `conversations/<conversationId>/spec_<fileName>` (the server prefixes `spec_`; scoped to the session's conversation). `uploadUrl` is a presigned PUT that expires in about 30 minutes (`expiresAt` given). Limits are enforced server-side: a `.md` file was accepted; a `.png` and a size over 10 MB were rejected with the texts under "Error texts". Uploading to the slot and attaching it to a prompt was not done; whether an attachment can become an image resource in the app is not stated and not tested. | `[SINGLE-OBSERVATION]` | 2026-10-16 | probe |
| `deploy_start` and `deploy_rollback` state that shipping to Production needs explicit user confirmation first; `deploy_impact` may inform that confirmation. | `[SCHEMA]` | 2026-10-09 | schema |

## Creating and loading an asset

| Fact | Tag | Observed | Source |
|---|---|---|---|
| Sequence: `mentor_start_session` (no params, returns `sessionId`), then exactly one of `mentor_create_asset` or `mentor_load_asset`, then `mentor_prompt`. No asset mutation is possible before create or load. One asset per session. | `[SCHEMA]`; sequence `[VERIFIED]` | 2026-10-09, 2026-10-16 | schema; probe |
| `mentor_create_asset` params: `sessionId`, `assetType` (`WebApplication`, `Agent`, `Library`, `Workflow`), `name`, optional `description`, `portfolioKey`, `templateAssetKey`. Returns `{sessionId, applicationKey}`. | `[SCHEMA]`; return `[VERIFIED]` | 2026-10-09, 2026-10-16 | schema; probe |
| **`portfolioKey` is required in practice** although the schema marks it optional: omitting it fails with "Portfolio ID is required." Source it from `env_list` (each environment row carries `portfolioKey`) and record it in `tenant-profile.md`. | `[VERIFIED]` | 2026-10-09 | probe; field |
| A created `WebApplication` is template-backed, not blank: a set of login and account screens in one UI flow and an app-named role, no default screen configured. On 2026-10-16 Mentor placed all template screens in a UI flow `Common` and reported the main flow empty. Exact screen set is template-dependent - read it back, do not assume. | `[VERIFIED]` | 2026-10-08, 2026-10-09, 2026-10-16 | probe; field |
| **A created asset is unreachable outside its session until its first publish:** `app_info` 404, `app_revisions` "Asset not found", `env_app` `app_not_deployed_in_environment`, `mentor_load_asset` "not found" (from a second session), every `context_*` total 0. | `[VERIFIED]` | 2026-10-09, 2026-10-16 | probe |
| Consequence: publish once early - right after the first change turn lands - before the session is closed or abandoned. Closing the session before that first publish loses the asset. | `[UNVERIFIED]` (inferred from the row above; not tested) | 2026-10-09 | inference |
| `mentor_load_asset` params: `sessionId`, `assetKey`, optional `revision` (defaults to latest). Loading an asset the session already holds returns the held copy, edits included. | `[SCHEMA]` | 2026-10-09 | schema |
| Asking Mentor (by prompt) to reload the asset replaces the held copy with the latest published revision and **permanently discards the session's unpublished changes**. Only on explicit user intent. | `[SCHEMA]` | 2026-10-09 | schema |
| **Capacity throttle on load:** the first `mentor_load_asset` of a session has failed with "A lot of people are currently using Mentor. Try again in a moment." (3 times in one project, 5 times over ~6 minutes in another). A new session later succeeded. `mentor_start_session` and `mentor_close_session` kept working throughout. | `[VERIFIED]` | 2026-10-07, 2026-10-08 | two projects' state records (3 failed loads; 5 failures over ~6 min); not encountered in the 2026-10-09 or 2026-10-16 probes |
| **Fulcrum rule, not a platform fact:** on that capacity text, retry the load at most 3 times with growing backoff (about 30 s, 60 s, 120 s), each wait using a mechanism verified to block. Still failing: close the session, halt, report it as a capacity stop - not as a model or auth failure, and not as a trap. | Fulcrum rule | - | - |

## Sessions and context

| Fact | Tag | Observed | Source |
|---|---|---|---|
| **No session token.** No token field in any response, no token parameter on any call. The `sessionId` alone identifies the session. | `[SCHEMA]`; absence also seen in every response of both probes `[VERIFIED]` | 2026-10-09, 2026-10-16 | schema; probe |
| **No fresh-context parameter.** `mentor_prompt` takes only `sessionId`, `message`, `attachmentRefs`. | `[SCHEMA]` | 2026-10-09, 2026-10-16 | schema |
| Every event of every run in one session carries the same `conversationId`; a later run knew what an earlier run built. **One session is one conversation.** An upload slot's `attachmentId` is scoped to the same `conversationId`. | `[VERIFIED]` | 2026-10-09, 2026-10-16 | probe, 3 runs each |
| Therefore the only way to get fresh context is: close the session, start a new one, load the asset again. | `[VERIFIED]` (follows from the two rows above) | 2026-10-09, 2026-10-16 | probe; schema |
| One prompt runs at a time per session; a `mentor_prompt` sent while one is running is **silently ignored**. | `[SCHEMA]` | 2026-10-09 | schema (carried from fulcrum-unattended-guardrails; no dated field observation here) |
| `mentor_cancel_prompt(sessionId, runId)` cancels only if `runId` is the current run, otherwise no-op; the session stays open. `mentor_close_session(sessionId)` cancels any in-flight run, releases the workspace context, and makes the `sessionId` unusable; returns `{sessionId, closed: true}`. | `[SCHEMA]`; close observed `[VERIFIED]` (cancel not called) | 2026-10-09, 2026-10-16 | schema; probe |
| Reading a run on a closed session fails with the closed-session text under "Error texts". | `[VERIFIED]` | 2026-10-09, 2026-10-16 | probe |
| Sessions are garbage-collected after ~30 minutes idle, losing unpublished changes. | `[UNVERIFIED]` (another catalog's claim; not observed here) | - | upstream documentation |

## Reading a run

| Fact | Tag | Observed | Source |
|---|---|---|---|
| `mentor_prompt` returns at once: `{sessionId, runId, status: "working", pollIntervalMs}` (`pollIntervalMs: 1000`). | `[VERIFIED]` | 2026-10-09, 2026-10-16 | probe |
| `mentor_get_run` params: `sessionId`, `runId`, `cursor` (optional). There is no detail-level or event-limit parameter. | `[SCHEMA]` | 2026-10-09 | schema |
| Without `cursor`, a read returns only events not yet delivered. Pass the previous `nextCursor` to re-read from there, or `0` to re-read from the start. `cursor` acts as a 0-based event index: `cursor: 41` on a drained 44-event run returned events 41 to 43. | `[SCHEMA]`; index behaviour `[SINGLE-OBSERVATION]` | 2026-10-09, 2026-10-16 | schema; probe |
| Response: `runId`, `status`, `events[]`, `pollIntervalMs`, `nextCursor` (absent on the last page), `hasMore`, `truncatedEventCount`, `result`. Status values: `working`, `succeeded`, `failed`, `cancelled`, `not_found`. | `[SCHEMA]`; shape seen `[SINGLE-OBSERVATION]` | 2026-10-09 | schema; probe |
| **Terminal pages omit `pollIntervalMs` and `nextCursor` entirely** (keys absent, not 0 or null): every terminal page carried only `runId`, `status`, `events`, `result`, `hasMore`, `truncatedEventCount`. Every run was already terminal on its first read, so a working-state page was not seen that day. A missing key is not an error; the drain rule below is unchanged. | `[SINGLE-OBSERVATION]` | 2026-10-16 | probe, 3 runs |
| The pacing field is **`pollIntervalMs`** (1000 on the prompt response and while working; at the end it read 0 on 2026-10-09 and was absent on 2026-10-16). There is no `pollAfterMs`. Fulcrum overrides it upward - see `../SKILL.md`, heading "Polling". | `[VERIFIED]` (1000); end value `[SINGLE-OBSERVATION]` each | 2026-10-09, 2026-10-16 | probe |
| **`status: succeeded` can arrive with `hasMore: true`.** A run is not read until a page returns `hasMore: false` with no `nextCursor`. A poller that stopped on the first terminal page reported an unread tail by paraphrase. Not reproduced on 2026-10-16 (three runs of 44, 27 and 13 events each drained in one page with `hasMore: false`); no counter-evidence, the rule stands. | `[VERIFIED]` | 2026-10-09 | probe; field |
| The server's own terminal rule: keep polling until status is terminal **and** `nextCursor` is null. | `[SCHEMA]` | 2026-10-09 | schema |
| Events are JSON-encoded strings, each with `MsgType`. Seen: `reasoning`, `conversationInfoUpdated`, `text` (answer streamed as per-token chunks with `chunkSequenceNumber`), `status` (`statusType: Completed`), and the publish events under "Publishing". | `[VERIFIED]` | 2026-10-09, 2026-10-16 | probe |
| Every event carries both `MsgType` and `msgType` (the same value twice) plus `conversationId`. Match on either key; do not treat the duplicate as two events. | `[SINGLE-OBSERVATION]` | 2026-10-16 | probe |
| Drain cost: a long answer streamed as ~160 events, about 8k tokens to read across two pages (2026-10-09); a six-item list answer was 44 events, about 6k characters, one page (2026-10-16). Budget answer-back turns accordingly; skip `reasoning` events when only the answer matters. | `[SINGLE-OBSERVATION]` each | 2026-10-09, 2026-10-16 | probe |
| Oversized events arrive as truncation markers (`_truncated` / `_eventId`); fetch the full body with `mentor_get_event(sessionId, runId, eventId)`, which returns `{runId, eventId, found, body}`. No marker has been seen live (`truncatedEventCount: 0` throughout); the call itself worked with `eventId` acting as a 0-based index into the run's events. | `[SCHEMA]`; call `[VERIFIED]` | 2026-10-09, 2026-10-16 | schema; probe |
| An event with `MsgType` `assetCompareRequested` is a request to the caller (open a Studio compare), not progress. Not seen live (2026-10-09, 2026-10-16). | `[SCHEMA]` | 2026-10-09 | schema |

## Publishing

| Fact | Tag | Observed | Source |
|---|---|---|---|
| **Publish is a `mentor_prompt` with the message "Publish"**, polled like any other run. | `[VERIFIED]` | 2026-10-08, 2026-10-09, 2026-10-16 | probe; field |
| The Publish run emits `publishStarted`, `publishAccepted{revision, publicationKey}`, `pendingModelChanges`, `publishSucceeded{revision}`, then a text confirmation. | `[VERIFIED]` | 2026-10-08, 2026-10-09, 2026-10-16 | probe; field |
| Every publish event also carries `assetKey`. `pendingModelChanges` is `{assetsChanges: [{assetKey, changes}]}`; on a first publish `changes` was empty although an entity had been added - not a change list to rely on. | `[SINGLE-OBSERVATION]` | 2026-10-16 | probe |
| **The `runId` is not the publication key.** The key is only in the `publishAccepted` event. Record both. | `[VERIFIED]` | 2026-10-08, 2026-10-09, 2026-10-16 | probe; field |
| Poll `publish_status` with the publication key; the `publication_id` parameter worked (aliases `publication_key`, `publish_key` exist). Seen: `status: Finished`, `outcome: success`, `applicationRevision`. Gate on `outcome` (`in_progress`, `success`, `build_engine_error`, `unknown`), not on `status`. | `[VERIFIED]` (call); outcome vocabulary `[SCHEMA]` | 2026-10-08, 2026-10-09, 2026-10-16 | probe; field; schema |
| `publish_status` schema: three optional string params `publication_id`, `publication_key`, `publish_key`, all resolving to the same lookup; exactly one is required. The server instructions name `publication_key` (the payload's `key`); any of the three is valid. By call, all three returned the identical small response `{key, status, applicationKey, applicationRevision, outcome}` and nothing else. | `[SCHEMA]`; aliases by call `[SINGLE-OBSERVATION]` | 2026-10-16 | schema; server instructions; probe |
| An `unknown` outcome is never success. `unknown` with `indeterminate: true` plus a `publish_advisory` means the outcome was never observed: poll again or verify with `env_app`; never re-publish on it. | `[SCHEMA]` | 2026-10-16 | schema |
| **Every publish lands in the tenant's Development environment** (the `env_list` row whose `purpose` is `Development`). Other environments are reached only by a separate `deploy_start` promotion, on user request (build key: see the `env_app.buildKey` row below). The probe's publish was live in the `Development` environment. | `[SCHEMA]`; observed `[SINGLE-OBSERVATION]` | 2026-10-16 | server instructions; schema; probe |
| **Confirmation gate: `env_app {env_key: <Development key>, key: <applicationKey>}` and its `revision` must equal the publication's `applicationRevision`.** A `success` outcome alone does not prove the change deployed; any other `revision` means it did NOT land. This is the gate Fulcrum uses. It reads the deployment record, not the published-state index, so it does not wait on index lag: the deployment was stamped seconds after the Publish prompt and `env_app` carried the new revision on its first read. Confirm a publish with it before any `context_*` read ("Published-state inspection"). | `[SCHEMA]`; immediacy `[SINGLE-OBSERVATION]` | 2026-10-16 | server instructions; schema; probe |
| A `Workflow` and a library are invisible to the deployed inventory. `env_app` on a `Workflow` errors: `asset_type_not_listable_by_env_app` (deployed in that env; confirms deployment, not revision) or `app_not_deployed_in_environment` (not deployed); branch on the `[code: <value>]` suffix of the error text. Confirm a library change through a consumer of it. | `[SCHEMA]` | 2026-10-16 | server instructions; schema |
| No publish is retried on the transport and nothing serializes publishes of one app. | `[SCHEMA]` | 2026-10-16 | server instructions |
| The publish completed inside its run (~50 s on 2026-10-09; on 2026-10-16 the revision existed 3 s and the deployment 4 s after the Publish prompt, and the run was terminal before its first read); `publish_status` was already terminal on its first read both times. The Publish run is the main wait; `publish_status` is confirmation. | `[VERIFIED]`; durations `[SINGLE-OBSERVATION]` each | 2026-10-09, 2026-10-16 | probe |
| After success, `env_app {key, env_key}` returns `{applicationKey, name, assetType, revision, buildKey, deploymentKey, deploymentDateTime, url}` (the runtime `url`); `deploymentKey` equalled the publication key. Supporting evidence only: the gate is the `revision == applicationRevision` row above. | `[VERIFIED]` | 2026-10-09, 2026-10-16 | probe; field |
| **`env_app.buildKey` is the Debug build, not a promotable one.** `build_list {asset_key, revision}` showed a `Debug` build, finished about 12 s after the deployment, whose key equalled `env_app.buildKey`, and a separate `Release` build finished about 1 minute after the deployment. A `deploy_start` promotion needs the `Release` build's `buildKey` (with `revision`) from `build_list`, polled until a `Release` row is `Finished` - never `env_app`'s `buildKey`. `build_list` response: `{builds: [{buildKey, assetKey, assetRevision, buildType, startedDateTime, finishedDateTime, builtBy, status, securityAudit, portfolioKey}]}`. The `build_list` description says the same. | `[SINGLE-OBSERVATION]`; description `[SCHEMA]` | 2026-10-16 | probe; schema |
| A change turn did not publish: no publish events, revision unchanged. | `[VERIFIED]` | 2026-10-09, 2026-10-16 | probe |
| A change turn **did** appear to publish on its own once (revision moved, a later "Publish" answered "nothing new to publish"). Not reproduced on the 2026-10-16 probe. | `[SINGLE-OBSERVATION]` | 2026-10-09 | field |
| Fulcrum rule from the two rows above: before sending "Publish", read the revision (`app_revisions` or `env_app`); publish only if it did not move since the last recorded publish. First-publish carve-out: on a created, never-published asset that read errors ("Creating and loading an asset"); no revision yet means first publish - send the Publish turn, the read error is not a blocker. | Fulcrum rule | - | - |
| Never publish again while the previous publish of that app is non-terminal - two revisions building at once can crash the build engine and wedge the app. | `[SCHEMA]` | 2026-10-09 | server instructions |
| A `failed` publish carrying an `OS-*` build-engine code is the build's own result: surface the code, do not re-publish blindly. | `[SCHEMA]` | 2026-10-09 | server instructions |
| A `failed` with `indeterminate: true` means the outcome was never observed and the build may still succeed: re-poll with the publication key or verify the deployed inventory; **never** re-publish on it. | `[SCHEMA]` | 2026-10-09 | server instructions |
| `publish_logs(pub_key)` returns the publication's `OS-DPL-*` messages, shape `{result: [{message, messageType, detail, type, severity}]}`. A first publish with a new entity included `OS-DPL-20019` ("Applying database changes may take longer than usual, up to 4 minutes"). | `[VERIFIED]`; shape and 20019 `[SINGLE-OBSERVATION]` | 2026-10-09, 2026-10-16 | probe |
| Mentor volunteers unrequested offers to publish after a fix turn. Not observed on the 2026-10-16 answer or change turns. | `[SINGLE-OBSERVATION]` | 2026-10-08 | field |

## Published-state inspection (context_*)

| Fact | Tag | Observed | Source |
|---|---|---|---|
| `context_*` reflect **published state only** - never the session's working model. An unpublished edit is invisible to them. | `[VERIFIED]` | 2026-10-08, 2026-10-09, 2026-10-16 | probe; field |
| **Index lag after publish is variable and can be long.** 2026-10-09: 0 rows ~20 s after the publish, full rows at ~110 s. 2026-10-16, a new app's first publish: `context_entities` and `context_screens` (by key and by name, `owned_only` true and false) returned 0 rows at every read from about 1.5 to about 25 minutes after the deployment, and `context_search` found nothing for the app; it was still not indexed when probing stopped. Observed range: about 2 minutes to more than 25 minutes. No fixed wait is safe. | `[VERIFIED]` (lag exists); about 2 min `[SINGLE-OBSERVATION]` 2026-10-09; more than 25 min `[SINGLE-OBSERVATION]` 2026-10-16 | 2026-10-08, 2026-10-09, 2026-10-16 | probe |
| Index rows of other apps all carried the same one or two index timestamps, suggesting batch re-indexing rather than indexing per publish. | `[UNVERIFIED]` (inference) | 2026-10-16 | probe |
| **`context_graph` read published state sooner than the index.** It returned the published entity (attributes and static records, at the published revision) about 11 minutes after the deployment, its first try, while `context_entities` still showed 0 rows at 25 minutes. Its own lag was not measured. | `[SINGLE-OBSERVATION]` | 2026-10-16 | probe |
| `context_graph` params: `key` (required), `root` (an element name; returns a small subgraph around it), `graphviz`, and `cursor` (new on 2026-10-16). Output is paged: a JSON header `{app_key, source, revision, latest_revision, root, graphviz, page, has_more, blocks, xre_version}` then the graph text blocks; while `has_more` is true, pass the returned cursor as `cursor`. The description documents a stored-graph code family (`graph_pending`, `graph_store_warming`, `graph_store_unavailable`, `graph_not_available`, `graph_cursor_invalid`, `graph_root_not_found`, `graph_root_unsupported`, `graph_source_too_large`, `graph_build_timeout`) plus `server_busy`. Graph nodes carry provenance (`CreatedByTool`, `CreatedByAgent`, `CreatedBy`) and the edit's timestamp (the change turn's, not the publish's). | `[SCHEMA]`; header, `root` and provenance `[SINGLE-OBSERVATION]` | 2026-10-16 | schema; probe |
| **Gating on published state (Fulcrum rule).** (1) Confirm the publish first with the `env_app` gate (`revision == applicationRevision`, "Publishing"), which does not wait on the index. (2) After a confirmed publish, an empty `context_*` result means *not yet indexed*, never absence. (3) Re-read with a blocking wait up to a ceiling the brief sets. (4) For structure checks (does this entity, attribute or screen exist), prefer `context_graph` where it covers the element (`[SINGLE-OBSERVATION]` that it is faster). (5) At the ceiling, report the check `untested` / `unproven`, never `fail`. | Fulcrum rule | - | - |
| A fresh-shell liveness gate once reported a false FAIL inside that lag window; it passed on re-read. On 2026-10-16 a fixed 2-minute wait would have reported a false absence. | `[SINGLE-OBSERVATION]` each | 2026-10-08, 2026-10-16 | project state record; probe |
| Default page size is 20 for owned queries. With `owned_only: false` the page came back `limit: 0, nextPageOffset: null` for an app with no indexed rows. | `[VERIFIED]` (20); `owned_only: false` page `[SINGLE-OBSERVATION]` | 2026-10-09, 2026-10-16 | probe |
| Owned elements only (`owned_only`): inherited or referenced entities that Mentor lists do not appear in `context_entities`. | `[SINGLE-OBSERVATION]` | 2026-10-08 | project state record |
| **Access flags on template screens disagree with Mentor.** `context_screens` reported every template screen non-public with the app role, while Mentor reported four of them anonymous. Do not derive screen access from `context_screens` alone; prove access by behaviour (an anonymous request to the screen). | `[VERIFIED]` | 2026-10-08, 2026-10-09 | probe; field |
| Settings and consumed REST structures have no `context_*` view. | `[SINGLE-OBSERVATION]` | 2026-10-08 | field |
| Whether `context_themes` exposes a theme's CSS content (not only theme names) is unknown; probe once per tenant and record the answer in `tenant-profile.md`. | `[UNVERIFIED]` (not probed) | - | inference |

## Completion signals

| Fact | Tag | Observed | Source |
|---|---|---|---|
| `result` on a change turn: `{attemptedChange, changeApplied, validation{errorCount, warningCount, firstMessages}}`. Field names are camelCase. On 2026-10-16 the answer-back and Publish turns returned `{attemptedChange, changeApplied}` with **no `validation` key**: expect `validation` only on change turns (on 2026-10-09 an answer turn was recorded with it). | `[VERIFIED]` (change turn); answer-turn absence `[SINGLE-OBSERVATION]` | 2026-10-09, 2026-10-16 | probe |
| `attemptedChange` was `true` on a read-only question (2026-10-09) and `false` on one (2026-10-16). It carries no reliable signal - never read it. | `[SINGLE-OBSERVATION]` each | 2026-10-09, 2026-10-16 | probe |
| `changeApplied` is weak. Carried from `../../fulcrum-verification/SKILL.md`: the flag can read `true` on a turn that changed nothing, and a no-change flag can appear on a turn that did land a change (`[VERIFIED]` there). Neither probe reproduced the false-positive: both saw `false` on read-only and Publish turns (Publish run: both flags `false`, no `validation` key), and on 2026-10-16 `true` on the real change. | `[VERIFIED]` (carried); probes `[VERIFIED]` | 2026-10-09, 2026-10-16 | fulcrum-verification; probe |
| Neither flag, nor 0 validation errors, nor a clean publish proves a change landed. Proof is `../../fulcrum-verification/SKILL.md`'s. | `[VERIFIED]` | source builds | field |

## Error texts

Verbatim, for matching. Tag and source as noted.

| Text | Meaning | Tag |
|---|---|---|
| `Portfolio ID is required.` | `mentor_create_asset` without `portfolioKey` | `[VERIFIED]` |
| `The mentor_publish tool is deprecated and is no longer available. Use mentor_prompt with the message "Publish" instead.` | `mentor_publish` called (tool absent since 2026-10-16) | `[VERIFIED]` |
| `A lot of people are currently using Mentor. Try again in a moment.` | capacity throttle, seen on `mentor_load_asset` | `[VERIFIED]` |
| `The workspace session has been closed and can no longer be used. Start a new session before calling this tool.` | any session call after close | `[VERIFIED]` (2026-10-09, 2026-10-16) |
| `Asset with key '<key>' not found.` | `mentor_load_asset` on an unpublished created asset (or a wrong key); arrives wrapped as `UpstreamError: [{"type":"text","text":"..."}]` | `[VERIFIED]` (2026-10-09, 2026-10-16) |
| `OS-APPS-40401 Asset not found [code: revisions_rejected]` | `app_revisions` before first publish; full text `UpstreamError: list revisions rejected by AVS (404 Not Found) for <key>: OS-APPS-40401 Asset not found [code: revisions_rejected]` | `[VERIFIED]` (2026-10-09, 2026-10-16) |
| `Failed to get asset: HTTP status client error (404 Not Found) ...` | `app_info` before first publish | `[SINGLE-OBSERVATION]` (text, 2026-10-16) |
| `app_not_deployed_in_environment` | `env_app` on an asset never published to that environment; full text `ValidationError: application <key> has no deployment in environment <env>; list the deployed set with env_apps [code: app_not_deployed_in_environment]` | `[VERIFIED]` (2026-10-09, 2026-10-16); `[SCHEMA]` |
| `The file extension of the conversation attachment is not allowed. Please use a different file type.` | `mentor_request_upload` with a disallowed extension (seen for `.png`) | `[SINGLE-OBSERVATION]` (2026-10-16) |
| `The conversation attachment exceeds the maximum allowed size.` | `mentor_request_upload` with `sizeBytes` over 10 MB | `[SINGLE-OBSERVATION]` (2026-10-16) |
| `asset_type_not_listable_by_env_app` | `env_app` on a deployed `Workflow` | `[SCHEMA]` |
| `invalid_env_key` | `env_key` is not one of this tenant's environments; pick one from `env_list` and retry | `[SCHEMA]` (server instructions, 2026-10-16) |
| `data.category: "ThrottledError"`, `data.code: "repeated_failure_throttled"` | that exact call failed upstream the same way several times in a short window and was throttled; do not repeat it unchanged (rest of the instruction text was truncated when read on 2026-10-16) | `[SCHEMA]` (server instructions, 2026-10-16) |
| `tenant_not_allowed` | an allowlist gate, not a lapsed sign-in: re-auth and re-registering fail the same way. Confirm the configured host is the tenant meant (a wrong tenant host returns this too); if it is, stop and say the tenant needs enabling | `[UNVERIFIED]` (vendor skill text, 2026-10-16; not observed) |

## Re-probing the surface

The surface has changed under Fulcrum before, silently. Two checks, cheap
first.

**Drift check - every session start, read-only, seconds.** List the live
tool names and compare them against the latest file in `mcp-snapshots/`;
do not load schemas to do it. An added or removed name is drift. Compare
parameters only when a name changed or a call fails schema validation, and
delegate that diff to a read-only investigator so the orchestrator never
loads every schema (`../../fulcrum/references/tool-preflight.md`). No
difference: the rows above stand. Do not compare descriptions; they drift without behaviour
changing and are not evidence.

**On drift - full re-probe before any mutating work.** Run it on a throwaway
app in a non-production environment, never on a real one:

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
7. Confirm the publish with the `env_app` gate, then read published state with
   `context_*` immediately and again on a blocking-wait schedule (for example
   +2, +5, +10, +25 minutes) until rows appear or a ceiling is hit; try
   `context_graph` alongside. Record the lag of each, or that the ceiling was hit.
8. Close the session; leave the throwaway app identified as such.
9. Update every row above that changed, with the new date, tag and source.
   Update the "Last full probe" line in the same change. Then tell the
   orchestrator which rows
   changed, so files citing them can be checked.

Do not drive Mentor against an unrecorded surface: a drift touching a tool
the current plan depends on means halt and report until this file is
updated (halt rules: `../../fulcrum-unattended-guardrails/SKILL.md`).
