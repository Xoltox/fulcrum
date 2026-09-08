# Fulcrum — harness notes

A skill states the capability it needs and the property that must hold; the
harness picks the implementation. This file is where that split gets
concrete: what individual harnesses have actually been observed to do.

Everything below is an **observation**, never a rule. An entry here is one
harness's behaviour, once, and another harness may not share it. This file
used to be a hand-written per-harness adapter set; one of those adapters
was wrong for a harness nobody on this project actually runs. That is why
this file now records only what was directly observed, and says so at every
entry — no guessing ahead of a harness you haven't watched do the thing.

## Waiting

`CONVENTIONS.md` sets the property: a wait must neither spin nor accumulate
context. Preference order, restated here because it is where harnesses
differ most:

1. A native scheduling or wait primitive the harness provides, if it works
   at any agent depth.
2. A delegated poller whose context is discarded when it reports back.
3. An in-process sleep call, last resort.

Verify once at session start that whatever you pick actually suspends —
a mechanism the harness silently swallows turns a poll loop into an
unbounded spin, and that failure mode is easy to miss because the loop still
"runs."

Two observations. Each names the harness deliberately: an observation you
cannot match to your own setup is nearly useless.

- **[OBSERVED — Antigravity]** A native scheduling tool was seen to suspend
  correctly regardless of the depth of the agent invoking it — a top-level
  session and a nested subagent both got a clean suspend with no busy loop.
  Where a primitive like this exists, it is the best option available, and
  it removes the reason to nest a poller purely to keep polling cost off an
  expensive parent's context — the primitive already isolates that cost.
- **[OBSERVED — Claude Code]** A subagent was seen to silently swallow one
  sleep form (the shell `sleep` builtin) while a different form on the same
  subagent (invoking a sleep through a Python one-liner) worked
  correctly. The swallowed form returned immediately every time, turning
  what should have been a bounded poll loop into an unbounded spin that
  looked, from the transcript, like the wait had simply been skipped. Treat
  this as a symptom to check for, not a named cause: if a wait appears to
  return instantly, verify — with a timestamp check or similar — that the
  mechanism actually suspended before concluding the platform itself is
  slow or broken. Do not carry a specific shell builtin or language
  construct forward as "the fix" for another harness. This is one harness's
  artifact — recorded here so that a reader hitting the same symptom
  elsewhere has a known case to compare against, not so they copy the
  workaround blind.

## Install observations

- **[OBSERVED — Antigravity]** The harness resolved its own skills directory
  and completed a correct install with no per-harness instructions and no
  adapter file — it was simply told the goal (see
  `INSTALL.md`) and worked out the mechanism itself. This is the case that
  motivated dropping the hand-written adapter approach in favor of stating
  goals and letting the agent resolve them.

## Contributed observations

Empty. Nothing has been added here yet — that's intentional, not an
oversight; do not fill it with speculation to make the section look used.

A useful addition names: the harness, exactly what was observed, how it was
noticed (what tipped you off that something was different from the
documented property), and what you changed as a result. An entry missing
any of those four is not ready to add.
