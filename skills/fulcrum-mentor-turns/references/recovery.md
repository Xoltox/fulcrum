# Recovery playbook for interrupted turns

Seven distinct interruption shapes. Diagnose which one before reacting - the
correct recovery differs for each, and applying the wrong one wastes a run or
starts a competing one. Error texts to match against:
`mcp-surface.md`, heading "Error texts".

## 1. Transport-level auth expires mid-turn

The connection's own authentication expires. It has **no in-session
recovery path.** [VERIFIED]

Recovery: reconnect out of band (re-authenticate the transport), then **read
the same orphaned run** with the same `sessionId` and `runId` - do not start
a competing turn on the same scope. The server-side turn kept running
through the transport gap; only your ability to observe it was interrupted.
This is why the run id is logged before the first wait (`../SKILL.md`,
section 6).

## 2. Orchestrator error interrupts a session after the work already completed

If an orchestrator-level error (agent killed, process crashed, dispatch
failed) interrupts a session *after* the underlying turn had already reached
a terminal state server-side, do not "resume" purely to run a check-only
turn - that spends a turn to learn something you can get for free.

Recovery: if the session is still open, one direct `mentor_get_run` read
(drained to the last page) shows the outcome. For published work, check the
app **revision** (`app_revisions` / `env_app`) and re-verify live per
`../../fulcrum-verification/SKILL.md`. If the evidence reflects the expected
work, it landed; if not, treat it as a normal incomplete turn and continue
per the granularity and staleness rules in `../SKILL.md`.

## 3. The session is closed or lost

A call on a closed session fails with the closed-session text. There is no
token or resume call to recover it; the `sessionId` is finished.
`[SINGLE-OBSERVATION]`

Recovery: start a new session and load the asset again. Anything the old
session held **unpublished is gone** - re-establish what the published
revision contains (`context_*` after the index lag, or a read-only turn)
before re-issuing the lost work. A session that created its asset and never
published leaves nothing to load `[UNVERIFIED]`; the create step starts
over. This is why a created asset is published once early (`../SKILL.md`,
section 7).

## 4. Mentor capacity throttle

The load (or another Mentor call) fails with the capacity text ("A lot of
people are currently using Mentor..."). `[VERIFIED]` This is load on the
service, not a defect in your request, your auth, or the model - do not
record it as a trap and do not rewrite the prompt.

Recovery: the bounded retry rule in `mcp-surface.md`, heading "Creating and
loading an asset" - at most 3 retries with growing backoff, each wait
verified to block. Still failing: close the session, halt, and report it as
a capacity stop. A later fresh session has succeeded where the first was
throttled.

## 5. A permission-classifier block on publish

A publish can be blocked outright by a permission classifier, independent of
anything OutSystems-side - no OutSystems error shape applies to it, and
Mentor's own reporting will not explain it. [VERIFIED] This kind of block
has resolved after re-authentication in the past - **do not assume every
occurrence is a permanent restriction.**

Recovery: confirm the underlying auth is healthy, and check the revision has
not moved (the publish may have gone through). Then retry once. If it recurs
after a clean retry with healthy auth, stop and report - do not iterate
trying to route around a policy denial; see the hard-stop list in
`../../fulcrum-unattended-guardrails/SKILL.md`.

## 6. A publish ends failed or indeterminate

- `failed` with an `OS-*` build-engine code: the build's own verdict.
  Surface the code (and `publish_logs` messages); fix with a Mentor turn.
  Do not re-publish unchanged. `[SCHEMA]`
- `failed` with `indeterminate: true`: the outcome was never observed and
  the build may still succeed. Re-poll `publish_status` with the same
  publication key, or check `env_app` (`revision` vs the publication's
  `applicationRevision`). **Never re-publish on it** - a second
  revision building alongside the first can wedge the app. `[SCHEMA]`

## 7. Abandoning an in-flight prompt or a whole stale session

Two distinct calls. `[SCHEMA]`

- **`mentor_cancel_prompt(sessionId, runId)`** cancels the in-flight prompt
  **only if `runId` is the session's current run** - otherwise it is a
  no-op. The session **stays open**. Use this to abandon one bad turn but
  keep the conversation (its consult-turn proposal, its accepted
  corrections) for the next attempt.
- **`mentor_close_session(sessionId)`** tears the session down: cancels any
  in-flight run, releases the workspace context, stops progress tracking.
  The `sessionId` is **not usable afterward**, and its unpublished changes
  are gone. This is the call behind the staleness guard in `../SKILL.md` -
  "close the stale session, then open a fresh one" means this call.

**Why this matters, not just hygiene:** a `mentor_prompt` issued while a
prior prompt is still running on that session is **silently ignored** - no
error. `[VERIFIED]` An abandoned in-flight prompt is therefore not inert: a
later prompt on the same session can be dropped with no signal, and the
agent cannot tell "ignored" from "landed" without re-reading state. Close or
cancel before reusing a session you suspect is still mid-run.

**Never assume abandoning a session without calling either op frees
anything.** An idle-timeout collection of sessions has been claimed by
another catalog but not observed here `[UNVERIFIED]`. Treat an unclosed
session as still holding its workspace context and its per-app lease until
`mentor_close_session` confirms otherwise.

### The staleness incident this guards against

[SINGLE-OBSERVATION, worst case] Resuming a stale session and publishing from
it once reverted a live app past six completed steps, wiping screens and
entities while layering new work onto the stale base. No automated gate
caught it - a human noticed the app looked wrong. Rollback tooling could not
reach the clean state; recovery was manual through the vendor portal. A
`mentor_close_session` call the moment staleness was suspected would have
made the stale session unusable before any publish could reach it.

## Cross-cutting rule for all seven

Never let an interruption become a reason to start a second turn or a second
publish covering the same scope while the first might still be alive or
might have already landed. Check state (run-in-flight signal, revision,
publish status, rendered app) before creating any new mutating call. This is
the run-id durability discipline of `../SKILL.md`, section 6, applied to the
recovery case.
