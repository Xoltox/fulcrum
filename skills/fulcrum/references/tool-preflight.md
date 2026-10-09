# Session-start tool preflight

A short check, not a full audit. Run once per session, before dispatching any
work, so a step does not discover mid-build that an op it needs does not
dispatch. Full rules on the three states and the fallback table:
`../../fulcrum-solution-init/references/tenant-capability-probe.md`, heading
"Tool availability - three states, not two", and
`../../fulcrum-solution-init/references/tool-availability-and-fallback.md`.

## Why this sits in the router

**A schema that loads is not a tool that dispatches.** Fetching an op's schema
proves only that it is described somewhere, not that a call reaches a working
implementation. The router is the one place every session passes through
before dispatch, so it is the cheapest place to catch this before a plan
commits to an op that cannot be called.

## Step zero: server presence, then auth, then surface drift

Run these before the procedure below. Tool facts live in
`../../fulcrum-mentor-turns/references/mcp-surface.md`; this file only orders the checks.

1. **Server presence BEFORE auth.** Confirm the OutSystems MCP server is listed,
   enabled and connected before checking auth (`auth_status`). If it is not, follow
   the harness-specific steps in `../../../HARNESS-NOTES.md`. An unlisted server and
   an expired login look alike from the agent's side, so settle presence first.
2. **Auth can expire mid-engagement.** `[VERIFIED]` Treat an auth error on any call as
   an auth event, not a tool fault: see
   `../../fulcrum-mentor-turns/references/recovery.md`, heading "1. Transport-level
   auth expires mid-turn".
3. **Surface drift check.** At session start compare the live tool names and parameter
   names against the latest `../../fulcrum-mentor-turns/references/mcp-snapshots/*.md`. On any difference, stop and
   run the re-probe in
   `../../fulcrum-mentor-turns/references/mcp-surface.md#re-probing-the-surface` before
   trusting skill text that names a tool or parameter.

## The procedure

1. **List the ops this engagement's next phase actually needs.** Read
   `plan.md` / the next `TASKS.md` row, not the whole tool surface.
2. **Consult `tenant-profile.md` first.** If a needed op already has a row in
   its tool-availability section, use that answer - do not re-probe it.
3. **Probe only what the profile does not already answer**, and only read-only
   ops (`../../fulcrum-solution-init/references/tenant-capability-probe.md`
   still owns the probe mechanics - this step reuses it, not a separate
   procedure).
4. **For a mutating op the phase needs that is still `unknown`:** that is
   expected - do not probe it here. Let the real step that needs it dispatch
   it for its own reason, per the ordinary halt/fallback rules if it fails.
5. **For any op confirmed unavailable with no fallback recorded:** do not
   dispatch into the phase that needs it. Report the gap and route to
   `../../fulcrum-unattended-guardrails/references/halt-conditions.md`, heading
   "Halt on an unavailable op with no fallback", instead of starting work that
   is already known to hit a dead end.

## Proportionality

This is a lookup against an existing profile plus, at most, a handful of new
read-only probes for ops the profile has not yet answered - not a re-run of
the full tenant capability probe every session. If the profile is stale per
`tenant-capability-probe.md` rule 5, re-probe the affected rows only, not the
whole file.
