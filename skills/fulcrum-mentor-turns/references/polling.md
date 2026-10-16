# Polling - cadence, draining, and the driver brief

Read when briefing an agent that will drive Mentor, when tempted to change
the cadence in `../SKILL.md`, or when another installed catalog prescribes a
different one. Run-response fields cited here are recorded in
`mcp-surface.md`, heading "Reading a run".

## Why the rate depends on who pays

Every poll is a request *and* a response, and both persist in the context of
whoever issued them. Wall clock is free; context is not. So the cadence is a
token-cost decision, and the right rate follows from one question: **whose
context absorbs this poll, and does that context survive the phase?**

- A delegated poller's context dies when it returns. Its poll traffic is
  quarantined, so a faster loop costs only that agent's throwaway window -
  hence **45 s** for answer-back turns, **90 s** for model-mutating turns and
  for the Publish turn (long, and nothing useful arrives early).
- An orchestrator polling in its own context keeps every request and response
  for the rest of the session. Each iteration is a permanent debit against the
  window that supervises the whole run, so the floor is **90 s for everything**,
  longer for phases known to run long. This self-poll fallback is legitimate
  when no subagent is available; it is not a failure mode.

The seductive wrong inference is that no delegation means shorter loops, on the
grounds that the orchestrator is blocked and should find out sooner. That
optimises wall clock. Wall clock is not the scarce resource; the orchestrator's
window is, and it is the one resource no later economy restores.

## The server's pacing hint is overridden on purpose

The run response carries `pollIntervalMs` (about 1 s while working, 0 at the
end) `[SINGLE-OBSERVATION]`. That is the server saying how often it *can* be
asked, not how often it is worth asking. Fulcrum deliberately waits longer:
the cadence above governs, and `pollIntervalMs` never shortens a wait. There
is no `pollAfterMs` field; text naming one is stale.

## Draining - the cadence applies between drains, not within one

A run's events arrive in pages. `status: succeeded` can come back on a page
that still has `hasMore: true` `[VERIFIED]`. So:

- **While `hasMore` is true, page again immediately** - no wait. The cadence
  is the gap between "the run is still working" reads, never between pages of
  an already-finished run.
- A run is read only when a page returns `hasMore: false` and no
  `nextCursor`. **A poller reports only after that page.**
- **Never paraphrase or summarise unread pages.** A poller that stopped on the
  first terminal page and described the tail it never read has produced a
  fabricated report `[SINGLE-OBSERVATION]`. If a page could not be read,
  report exactly that, with the cursor, and stop.
- A page lost to a rejected response is re-read by passing the previous
  `nextCursor` (or `0` for the whole run) as `cursor`.
- Draining a long answer is expensive (~8k tokens for one), so the poller does
  not carry it back. The poller reports only terminal state, drained yes/no,
  run id, read count, and the publish key and revision if it saw them. The
  driver gets the answer text and the `result` object from its own direct read
  of the run from the start (`cursor: 0`, drained to `hasMore: false`). This pays
  for one long answer twice (once in the poller, once in the driver); accepted
  for a clean driver context.

## The wait must actually block

Waiting is a capability (canonical preference order:
`../../../CONVENTIONS.md`, the heading beginning "Canonical facts"). A wait mechanism that returns immediately turns a poll loop into a
back-to-back hammer on Mentor with no cadence at all (the observed wait history is in `../../../HARNESS-NOTES.md`, heading "Claude Code CLI - the wait at subagent depth"); this has been seen at
subagent depth more than once `[VERIFIED]`. Before the first poll in any
agent, verify the chosen wait suspends for the requested time (time one
short wait). If it does not, pick another mechanism; if none blocks, stop and
report. Which mechanisms block where is a harness observation and belongs in
`../../../HARNESS-NOTES.md`, never in a skill.

## Pointing at this skill is not a brief

An agent told only "read `fulcrum-mentor-turns`" has polled at its own
invented cadence and spawned no poller `[SINGLE-OBSERVATION]`. Every brief to
an agent that drives or polls Mentor must **restate** the rules below in its
own text. Paste this block, filled in:

```
Mentor driver rules (restated, binding):
- Before the first wait, write the runId (and later any publicationKey)
  to <durable log path>.
- Cadence: 45 s between reads for answer-back turns, 90 s for change turns
  and the Publish turn - if a discardable poller absorbs the polls.
  Polling in your own context with no poller: 90 s floor for everything.
- Ignore pollIntervalMs; it never shortens a wait.
- Verify once that your wait blocks before relying on it. If it returns
  immediately, stop and report.
- Drain: while hasMore is true, read the next page at once. The run is
  read only when hasMore is false and nextCursor is absent. Report only
  then. Never summarise a page you did not read.
- Report (poller): terminal state, drained yes/no, run id, read count, and
  the publicationKey and revision if a publish event appeared. Not the answer
  text, not the result object, not the event stream - the driver reads those
  itself (cursor 0, drained).
- Never answer a Mentor offer to publish. Publish only when briefed to.
- Never put a secret value in a prompt.
```

## After a poller reports terminal

The driver makes **one fresh direct read** of the run itself before the next
prompt or publish - the poller's report is second-hand, and the driver must
see the terminal page, the `result` and any publish events with its own
eyes. Record in the journal that the verdict rests on the direct read.

## Precedence over other installed polling guidance

Another skill catalog may prescribe a different cadence - operation tiers keyed
to the *kind* of call, with a synchronous tier and a drain-then-pause tier.
When both are present, `../SKILL.md` governs the waits. Its drain rule agrees
with the one above and is not in conflict. Do not average cadences, and do
not switch mid-session.

Two reasons, stated so a future reader can re-decide with the evidence rather
than guess at intent:

- Cost against wall clock is better at 45/90 across a long multi-turn build.
- Two rates split on one question an agent can always answer - *is Mentor
  answering me, or changing the model?* - are followed correctly more often
  than three tiers split on operation type, which requires classifying the call
  first. Robustness in an unattended loop beats theoretical precision.

That other catalog records per-poll telemetry, so it may hold data this rule
does not. If its cadence is ever shown to win on measured cost-to-wall-clock
for the mutating case, this rule is the one to change - update it in
`../SKILL.md`, in `../../../CONVENTIONS.md`, and in the sibling skills that
defer to it.
