# Fulcrum - harness notes

A skill states the capability it needs and the property that must hold; the
harness picks the implementation. This file is where that split gets
concrete: what individual harnesses have actually been observed to do.

Everything below is an **observation**, never a rule. An entry here is one
harness's behaviour, once, and another harness may not share it. This file
used to be a hand-written per-harness adapter set; one of those adapters
was wrong for a harness nobody on this project actually runs. That is why
this file now records only what was directly observed, and says so at every
entry - no guessing ahead of a harness you haven't watched do the thing.

## Waiting

`CONVENTIONS.md` sets the property: a wait must neither spin nor accumulate
context. Preference order, restated here because it is where harnesses
differ most:

1. A native scheduling or wait primitive the harness provides, if it works
   at any agent depth.
2. A delegated poller whose context is discarded when it reports back.
3. An in-process sleep call, last resort.

Verify once at session start that whatever you pick actually suspends -
a mechanism the harness silently swallows turns a poll loop into an
unbounded spin, and that failure mode is easy to miss because the loop still
"runs."

Two observations. Each names the harness deliberately: an observation you
cannot match to your own setup is nearly useless.

- **[OBSERVED - Antigravity]** A native scheduling tool was seen to suspend
  correctly regardless of the depth of the agent invoking it - a top-level
  session and a nested subagent both got a clean suspend with no busy loop.
  Where a primitive like this exists, it is the best option available, and
  it removes the reason to nest a poller purely to keep polling cost off an
  expensive parent's context - the primitive already isolates that cost.
- **[OBSERVED - Claude Code]** A subagent was seen to silently swallow one
  sleep form (the shell `sleep` builtin) while a different form on the same
  subagent (invoking a sleep through a Python one-liner) worked
  correctly. The swallowed form returned immediately every time, turning
  what should have been a bounded poll loop into an unbounded spin that
  looked, from the transcript, like the wait had simply been skipped. Treat
  this as a symptom to check for, not a named cause: if a wait appears to
  return instantly, verify - with a timestamp check or similar - that the
  mechanism actually suspended before concluding the platform itself is
  slow or broken. Do not carry a specific shell builtin or language
  construct forward as "the fix" for another harness. This is one harness's
  artifact - recorded here so that a reader hitting the same symptom
  elsewhere has a known case to compare against, not so they copy the
  workaround blind.

### Claude Code CLI - the wait at subagent depth, observed 2026-10

Observations from one harness across several sessions. Each is a symptom to
compare against, not a fix to copy.

- **[VERIFIED]** (Claude Code CLI, 2026-10, several sessions) At subagent depth the shell
  `sleep` form was blocked or swallowed. Two further forms, a background shell
  sleep and a monitor-style until-loop, returned immediately, so a poller looped
  back-to-back with no cadence; one burned 40 turns in 75 seconds. A single
  foreground shell call running a one-line Python `time.sleep(N)` with a
  150000 ms call timeout did block. A poller that ran this way and a driver
  told to self-poll this way both kept cadence.
- How it was noticed: poll timestamps a second or two apart, and turn counts far
  above the poll count the cadence implies. What changed: Fulcrum's rule is to
  time one short wait before the first poll. **Verify your wait blocks**; do not
  take this list as the answer for another harness or another harness version.

## Install observations

- **[OBSERVED - Antigravity]** The harness resolved its own skills directory
  and completed a correct install with no per-harness instructions and no
  adapter file - it was simply told the goal (see
  `INSTALL.md`) and worked out the mechanism itself. This is the case that
  motivated dropping the hand-written adapter approach in favor of stating
  goals and letting the agent resolve them.

## Contributed observations

- **Claude Code CLI - server missing from the tool list** (observed 2026-10-08).
  The harness keeps per-project enable and disable lists for MCP servers; a
  disable entry wins over an enable entry; approval of a project-scoped server is
  granted per project directory; an expired transport login also hides the server
  until re-authentication. How it was noticed: the OutSystems tools were absent
  while `auth_status` could not be called. What changed: Fulcrum's pre-flight
  settles server presence (listed, enabled, connected) before checking auth.

- **Claude Code CLI - depth-1 subagents can spawn a nested poller** (observed
  2026-10-08). A depth-1 subagent spawned a cheaper-tier poller subagent
  successfully, and the pattern recurred in a project journal. Evidence:
  `[VERIFIED]` on this harness only. How noticed: the open question whether the
  nested-poller exception was usable here. What changed: the exception is
  documented as usable on this harness, with a sibling-poller fallback kept for
  harnesses where a nested agent cannot spawn.
- **Claude Code CLI - agent definitions load at session start** (observed
  2026-10). Editing or adding an agent definition mid-session has no effect until
  the session restarts; agents already running keep the old definition. A
  definition in a parent folder's agents directory is discovered from a session
  started in a child folder. How noticed: a corrected poller definition did not
  change a running driver's behaviour. What changed: drivers already running
  were told the corrected wait in their brief, and the fix is applied at the next
  restart.
- **Claude Code CLI - lean agent definitions are much cheaper** (measured
  2026-10, `[SINGLE-OBSERVATION]`). A lean, tool-scoped poller definition cost
  about 5.8k tokens for a 3-call run; a general-purpose agent doing similar work
  started above 50k tokens, inheriting the full tool set and instruction
  context. How noticed: the user read the transcript. What changed: roles ship as
  scoped definitions (see Agent definitions below).
- **Claude Code CLI - auto mode permission classifier** (observed 2026-10).
  The classifier blocked typing a credential into a browser, and blocked an
  auto-submitting local form written to get around that. A browser snapshot tool
  also failed repeatedly in one session (tool version unknown, so treat as
  observed once, not as a known bug). `[VERIFIED]` for the classifier blocks.
  How noticed: the UI check could not complete unattended. What changed: a
  sign-in-gated UI check is a user-action hand-off, briefed as "ask the user for
  a screenshot or a confirmation".

## Agent definitions

Harness-neutral role definitions live in `agents/roles/`. Adapters for a
harness live in `agents/<harness>/`; the Claude Code adapters ship in
`agents/claude-code/` and are installed by `install.sh`. Overview:
`agents/README.md`.

- **Claude Code CLI - `Agent(fulcrum-poller)` in a subagent's `tools:`**
  (recorded 2026-10-16, not yet observed). The driver adapter lists `Agent(fulcrum-poller)` to
  restrict which agent types it may spawn; whether the restriction is honoured
  at subagent level has not been tested. `[UNVERIFIED]` The driver body states
  the same rule in prose, so behaviour is bounded either way.

A useful addition names: the harness, exactly what was observed, how it was
noticed (what tipped you off that something was different from the
documented property), and what you changed as a result. An entry missing
any of those four is not ready to add.
