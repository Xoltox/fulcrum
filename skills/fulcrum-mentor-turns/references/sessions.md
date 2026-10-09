# Sessions, context, and when to start fresh

Detail behind `../SKILL.md`, heading "Sessions, conversation and the
staleness guard". Tool facts cited here are recorded, dated and tagged in
`mcp-surface.md`, heading "Sessions and context".

## What a session is now

- A session holds one asset (created or loaded) and one conversation. Every
  run in the session shares that conversation: Mentor remembers what earlier
  turns asked and built. `[SINGLE-OBSERVATION]`
- There is no token to carry, echo or refresh, and no "fresh context" switch
  on a prompt. The `sessionId` is the whole handle. `[SCHEMA]`
- Fresh context therefore means: `mentor_close_session`, then
  `mentor_start_session`, then `mentor_load_asset`. Nothing short of that
  clears Mentor's memory of the conversation.
- Close discards whatever the session holds unpublished. On a session that
  created its asset and has not yet published, close loses the asset
  `[UNVERIFIED]` - publish once early (`../SKILL.md`, heading "Publish
  sequencing").

## Reuse across consecutive steps, or start fresh

The tradeoff, stated so the choice is made rather than defaulted:

| Keep the session | Start fresh |
|---|---|
| Mentor carries its own earlier proposals, names and corrections into the next turn - the consult and build turns of a step depend on this | Mentor re-reads the model with no remembered beliefs; nothing it got wrong earlier steers the next turn |
| No new `mentor_load_asset`, so no fresh exposure to the capacity throttle | Each new session is a load, and loads have been refused under capacity (`mcp-surface.md`, "Creating and loading an asset") |
| Risk: carried beliefs go stale - Mentor "remembers" a state the model no longer has, and the staleness guard is the only check | Risk: costs a load and loses useful context; a cross-step dependency must be restated in the prompt |

Rules that follow:

- **Within a step: always one session.** Consult, build and its fix turns
  share it. Splitting them makes Mentor re-derive an approach and silently
  drops the review's corrections (`posture.md`).
- **Across consecutive steps on the same app: reuse by default**, provided
  the step's first turn passes the staleness guard. Reuse is a decision made
  fresh at each step, not a precedent.
- **Start fresh when** the guard fails or a read-back contradicts published
  state; the previous step ended in a halt, a cancel, or an interrupted run;
  the session has sat idle long enough that its survival is in doubt
  (idle GC is `[UNVERIFIED]`); or several steps of accumulated conversation
  are now more liability than help.
- **One session per app at a time**, held under the lease
  (`../../fulcrum-project-state/SKILL.md`). Concurrent sessions on different
  apps are allowed.
- **Always close** a session you are done with. Nothing states that idle
  release frees its workspace context or slot.

## Mentor's read-back is belief, not proof

An answer-back turn reports what Mentor believes about the model. It has
been confidently wrong: it claimed JSON names existed that it had only
inferred (F-020).
`[VERIFIED]`

- When a read-back contradicts published-state inspection (`context_*`,
  after the index lag) or wire evidence (a request log, a probe endpoint),
  **trust the instrument** and write the contradiction to the journal.
- Before the first publish, read-back is the only view of the working model.
  Treat it as a lead to check after publish, not as a verdict.
- Where no `context_*` view exists (settings, consumed REST structures and
  their JSON names), only behaviour on the wire proves the state. Plan that
  check; do not accept a read-back for it.
- Which instrument proves which defect class:
  `../../fulcrum-verification/SKILL.md`.
