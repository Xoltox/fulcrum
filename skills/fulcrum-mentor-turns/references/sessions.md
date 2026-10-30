# Sessions, context, and when to start fresh

Detail behind `../SKILL.md`, heading "4. Sessions, conversation and the
staleness guard". Tool facts cited here are recorded, dated and tagged in
`mcp-surface.md`, heading "Sessions and context".

## What a session is now

- A session is one conversation and holds every asset created or attached in
  it, several if needed (`mcp-surface.md`, "Sessions and context"). Every run
  in the session shares that conversation: Mentor remembers what earlier
  turns asked and built. `[VERIFIED]`
- There is no token to carry, echo or refresh, and no "fresh context" switch
  on a prompt. The `sessionId` is the whole handle. `[SCHEMA]`
- Fresh context therefore means: `mentor_close_session`, then
  `mentor_start_session`, then a `mentor_prompt` attaching the asset (`assetRefs`).
  Nothing short of that clears Mentor's memory of the conversation.
- Close discards whatever the session holds unpublished. On a session that
  created its asset and has not yet published, close loses the asset
  `[UNVERIFIED]` - publish once early (`../SKILL.md`, heading "7. Publish
  sequencing").

## One session per dispatch, or carry one across dispatches

The tradeoff, stated so the choice is made rather than defaulted:

| Keep the session | Start fresh |
|---|---|
| Mentor carries its own earlier proposals, names and corrections into the next turn - the consult and build turns of a dispatch depend on this | Mentor re-reads the model with no remembered beliefs; nothing it got wrong earlier steers the next turn |
| No new first turn, so no fresh exposure to the capacity throttle | Each new session has a first turn, and the first Mentor call of a session has been refused under capacity (`mcp-surface.md`, "Creating and loading an asset") |
| Risk: carried beliefs go stale - Mentor "remembers" a state the model no longer has, and the staleness guard is the only check | Risk: costs a first turn and loses useful context; a cross-dispatch dependency must be restated in the prompt |

Rules that follow:

- **Within a dispatch: always one session.** Consult, build and its fix turns
  share it. Splitting them makes Mentor re-derive an approach and silently
  drops the review's corrections (`posture.md`).
- **Across dispatches: a fresh session per dispatch** (Fulcrum rule). One
  dispatch is one batch or one solo row with one Publish, and a fresh session's
  `assetRefs` with no revision works on the latest `[SCHEMA]`, so the dispatch's
  staleness guard proves the previous one landed. Carrying a session into the
  next dispatch trades that proof for remembered context; restate any
  cross-dispatch dependency in the prompt instead.
- **Resume a session only within the same row or batch**: the orchestrator passes
  the `sessionId` a previous dispatch of that row or batch handed back with
  `session_state: open` (budget stop, halt with unpublished changes). Do not
  resume when the guard fails or a read-back contradicts published state and
  the session holds no unpublished changes, after a cancel or an interrupted
  run, or after idle long enough that its survival is in doubt (idle GC is
  `[UNVERIFIED]`).
- **Never close a session holding unpublished changes**: publish or halt with
  it kept open (`../SKILL.md`, staleness guard).
- **One session per app at a time**, held under the lease
  (`../../fulcrum-project-state/SKILL.md`). Two sessions never build one app at
  once: user-confirmed, not to be tested. Concurrent sessions on different apps
  are allowed.
- **One session may hold several assets**, but Publish covers the held
  assets with changes (inferred) and each publication is gated on its own key (`mcp-surface.md`, "Publishing").
- **`assetRefs` does not refresh a held asset**, and `revision` on a held asset
  breaks reads. A stale session is closed, not re-attached (`mcp-surface.md`,
  "Sessions and context").
- **Always close** a session you are done with and that holds no unpublished
  changes. Nothing states that idle release frees its workspace context or
  slot.

## Mentor's read-back is belief, not proof

An answer-back turn reports what Mentor believes about the model. It has
been confidently wrong: it claimed JSON names existed that it had only
inferred (F-020).
`[VERIFIED]`

- When a read-back contradicts published-state inspection (`context_*`,
  once indexed; the lag is variable) or wire evidence (a request log, a probe endpoint),
  **trust the instrument** and write the contradiction to the journal.
- Before the first publish, read-back is the only view of the working model.
  Treat it as a lead to check after publish, not as a verdict.
- Where no `context_*` view exists (settings, consumed REST structures and
  their JSON names), only behaviour on the wire proves the state. Plan that
  check; do not accept a read-back for it.
- Which instrument proves which defect class:
  `../../fulcrum-verification/SKILL.md`.
