# Polling cadence — derivation and precedence

Read when tempted to change the cadence in `../SKILL.md`, or when another
installed catalog prescribes a different one.

## Why the rate depends on who pays

Every poll is a request *and* a response, and both persist in the context of
whoever issued them. Wall clock is free; context is not. So the cadence is a
token-cost decision, and the right rate follows from one question: **whose
context absorbs this poll, and does that context survive the phase?**

- A delegated poller's context dies when it returns. Its poll traffic is
  quarantined, so a faster loop costs only that agent's throwaway window —
  hence **45 s** for answer-back turns, **90 s** for model-mutating turns and
  publish polling (long, and nothing useful arrives early).
- An orchestrator polling in its own context keeps every request and response
  for the rest of the session. Each iteration is a permanent debit against the
  window that supervises the whole run, so the floor is **90 s for everything**,
  longer for phases known to run long.

The seductive wrong inference is that no delegation means shorter loops, on the
grounds that the orchestrator is blocked and should find out sooner. That
optimises wall clock. Wall clock is not the scarce resource; the orchestrator's
window is, and it is the one resource no later economy restores.

## Precedence over other installed polling guidance

Another skill catalog may prescribe a different cadence — operation tiers keyed
to the *kind* of call, with a synchronous tier and a drain-then-pause tier.
When both are present, `../SKILL.md` governs. Do not average them, and do not
switch mid-session.

Two reasons, stated so a future reader can re-decide with the evidence rather
than guess at intent:

- Cost against wall clock is better at 45/90 across a long multi-turn build.
- Two rates split on one question an agent can always answer — *is Mentor
  answering me, or changing the model?* — are followed correctly more often
  than three tiers split on operation type, which requires classifying the call
  first. Robustness in an unattended loop beats theoretical precision.

That other catalog records per-poll telemetry, so it may hold data this rule
does not. If its cadence is ever shown to win on measured cost-to-wall-clock
for the mutating case, this rule is the one to change — update it in
`../SKILL.md`, in `../../../CONVENTIONS.md`, and in the sibling skills that
defer to it.
