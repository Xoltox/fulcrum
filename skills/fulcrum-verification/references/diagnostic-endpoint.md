# Diagnostic REST endpoint pattern

Rung 5 of the proof ladder (live data ground truth) has no model-layer path
in v1, on any tenant. This is the workaround, and the debt it creates.

## Why there is no model-layer path

`db_query`, `exec_in_app` and `test_setup_start` / `test_setup_status` were
absent on the 2026-10-16 listing (listed on 2026-10-09; absence may be per
tenant or per server version, re-check on the next probe; availability per
tenant goes in `tenant-profile.md`). Even when it listed, `db_query` was not a
model-layer SQL path: it needed a `test_setup_start` harness, accepted only
templates declared upfront, and its own schema said no template - `SELECT`
included - returns rows in v1 (`[SCHEMA]`, 2026-10-09). Current tool facts:
`../../fulcrum-mentor-turns/references/mcp-surface.md`.

So this endpoint, probed over HTTP, is the instrument for live row data.
Around it: `context_*` for published structure, `app_logs` / `app_traces` for
what the runtime did. Mentor answer-back is belief, never proof.

## The pattern that works

`[VERIFIED]`

1. **A temporary REST GET returning pipe-delimited plain text**, not JSON.
   Plain delimited text survives being read back through whatever channel
   the orchestrator/agent has, without a parsing layer that can itself hide
   a bug.
2. **Explicit boolean-to-text conversion** on every boolean field. The
   platform omits falsey values from response bodies entirely - a `false` or
   empty value is silently absent, not present-as-false. Its absence from
   the response is NOT evidence that the underlying assignment is missing;
   convert every boolean to an explicit text token (`"true"`/`"false"`)
   before it goes in the response.
3. **An explicit send-default-values property** on the response structure,
   for the same reason - a default/zero value can otherwise be silently
   dropped rather than sent.
4. **A header dump on every call.** Distinguishes a genuinely false/absent
   value from a value that was actually wired to a response header instead
   of a body field - a wiring mistake that a body-only read can't detect.
5. **Its own guard logic**, not bolted onto an existing orchestrator action.
   A diagnostic endpoint that shares logic with production code risks
   inheriting production's bugs (or introducing new ones into production) - 
   keep it structurally separate and disposable.

## The debt is real - track it from endpoint one

`[VERIFIED]` These endpoints accumulate as permanent artifacts if left
unmanaged. The source build finished with 7+ live diagnostic endpoints and no
removal plan. Do not let this recur:

- Log every diagnostic endpoint created, with its purpose and creation date,
  starting from the first one - not retroactively once there are several.
- Schedule teardown explicitly as part of the work that created the need for
  it, not as an afterthought once the feature ships.
- Treat an undocumented diagnostic endpoint discovered later as a finding to
  report, not as background noise to ignore.

## Outbound route probe (integrations)

A generic check that the app can reach a target and speaks the right scheme,
with no secret involved. `[SINGLE-OBSERVATION]`

1. From the app (a temporary action behind a diagnostic endpoint), make an
   **unauthenticated** call to a known protected path on the target. Take the
   path from the project's `.fulcrum/external/<system>.md`, section
   `## Endpoint and auth`.
2. Expect **401**. A 401 proves the route, host and scheme are right and the
   target is enforcing auth, without handling any credential.
3. A **transport error with no HTTP status** (refused, timeout, DNS, TLS) means
   the route is not reached at all: fix connectivity first (private
   connectivity, host name, scheme) before touching payload or auth.
4. Any other status (404, 5xx, redirect) is a finding about the path or the
   target; record it against the external contract file, not as a pass.

Treat the probe as a diagnostic endpoint: log it and schedule its teardown
like any other (see "The debt is real").
