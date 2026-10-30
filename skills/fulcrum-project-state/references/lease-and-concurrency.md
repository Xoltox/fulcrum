# The lease, and what it can and cannot protect

## What it enforces

**One Mentor session at a time per app.** `[VERIFIED]` The rule and its operational
detail are in `../../fulcrum-unattended-guardrails/SKILL.md`, heading "Concurrency lock -
one Mentor session per app". What that does not provide is a mechanism that survives
the agent that holds the rule in its own head. `lease.<app>.json` is that mechanism.

**What breaks without it.** An orchestrator can only refuse to dispatch two agents it
knows about. A second session started by a different person, a different terminal, or
a resumed crashed run knows nothing about the first. Two concurrent Mentor sessions on
one app is a model-corruption path, not a queueing inconvenience: the loser's turns
land against a model the winner has already moved, and publishing from that stale
model advances the revision while silently reverting completed work. `[VERIFIED]`

## Why it is the one uncommitted file

Everything else in `.fulcrum/` is committed, because git is the team mechanism. The
lease is not, because a committed lock is **stale by definition** - it records that
someone held a lock at push time, which is not a question anyone needs answered.
`[UNVERIFIED]` Add `lease.*.json` to the project's `.gitignore`.

## Shape

```json
{
  "app": "<app identifier>",
  "holder": "<stable identity: user or host plus session label; the bare literal `user` only at a Studio hand-off>",
  "acquired": "<ISO-8601 UTC timestamp>",
  "ttl_seconds": 5400,
  "task": "T-014",
  "note": "<what is being done, one line>",
  "open_session": "<Mentor sessionId - only while a dispatch returned session_state: open>",
  "held_with": ["<other app identifiers in the same session - only on a multi-asset dispatch>"]
}
```

`ttl_seconds` above is an example (a 75-minute dispatch budget plus margin), not a
default - see the TTL rule below. On a batch, `task` lists every row of the dispatch,
comma-separated.

One lease file per app when the solution has several: `lease.<app identifier>.json`.
The lock is per app, so a single shared file would serialise apps that the platform
permits to run concurrently.

**App creation is a mutating call too.** Before the prompt that creates the app there is no app
identifier yet: key the lease by the intended app name from `plan.md` and
`project.md`, write the journal `started` line, then send the creating prompt. The
call returns a `runId`, not a key: record the `runId` in `RUN-IDS.md` before the wait.
The key arrives in the first run as `assetKey` (`../../fulcrum-mentor-turns/references/mcp-surface.md`,
heading "Creating and loading an asset"); once read, record it (`RUN-IDS.md` outcome
line, then `project.md` at wave close) and keep the same lease file until release. In
the field the first journal line and the lease came after creation, so a crash at that
moment would have left an app nobody knew existed. `[SINGLE-OBSERVATION]` The crash
window is now between the prompt and the `runId` record: after that, the run can be
re-read for the key; before it, the app may exist with no id on file.

- `holder` must be stable across a crash and unique across concurrent agents. A
  hostname plus a session label is enough. An agent-generated random id is acceptable
  only if it is written to the lease before anything else happens with it.
- **The orchestrator is the sole lease writer** (Fulcrum rule). It takes the lease
  before a Mentor dispatch and releases it when a dispatch returns
  `session_state: closed`. A dispatch that returns `session_state: open` keeps the
  lease (see "Release" below). Drivers and pollers never write it, so there is no
  per-poll refresh.
- `ttl_seconds` is a **liveness claim, not a permission window.** Set it to the
  dispatch's wall-clock budget plus margin - never a fixed figure. One driver dispatch
  covers a whole batch or solo row (guard, consult, build, fix, Publish), so the TTL
  must cover all of it. A TTL shorter than the work it covers manufactures the expiry case on a
  perfectly healthy run.

## Protocol

### Acquire

The orchestrator, before a Mentor dispatch:

1. Read `lease.<app>.json`. Absent -> write it, append a session-file `acquire lease` line,
   proceed.
2. Present, `holder` is you -> rewrite `acquired` and `ttl_seconds` for the new
   dispatch, proceed. This is the normal resume-your-own-work path.
3. Present, another holder, `acquired + ttl_seconds` **in the future** -> the lease is
   live. **Do not take it.** Either work on a different app, or stop and report. Never
   "check whether the other agent is really running" by starting a turn. A dead
   session's lease: "Resuming after a dead session" below.
4. Present, another holder, `acquired + ttl_seconds` **in the past** -> expired. It may
   be broken only if the holder's dispatch is also known dead (it never returned and
   its budget is exceeded), under the rules below. Never a `holder: user` lease: "Studio
   hand-off" below.

### Release

The orchestrator, when the dispatch returns `session_state: closed` -
including on a failed turn, a halt, and a deliberate handoff: delete the file and append a
session-file `release lease` line. A lease released only on the success path is a lease that
leaks on exactly the runs where recovery matters.

### Hold

The orchestrator, when the dispatch returns `session_state: open` (a budget stop,
or a halt or lane stop with `on_exit: keep-open`, typically with `unpublished_changes: yes`): do **not**
release. The app still has a live Mentor session, and a second session on it is the
corruption path this file exists to prevent. Rewrite the lease with `open_session` set to the
returned `sessionId` and a new `acquired` / `ttl_seconds` sized to the expected resume dispatch
(or, when the next move is the user's, to a hold until the user decides), and append a
session-file `hold lease` line naming the sessionId. The next action is either a resume
dispatch of the **same** row or batch with that `sessionId`, or a stop for the user
(`HALT.md` records the open sessionId on a halt, the `hold lease` line on a lane stop).
Release only when a later dispatch returns
`session_state: closed`. (Fulcrum rule.)

## Several apps in one session

A driver may hold one declared producer and consumer pair
(`../../fulcrum-loop-engine/references/frontier-and-batching.md`, heading "Multi-asset
dispatch"). Each held app is still locked: a session holding a producer read-only is
still a session on that app, and a second session there is the same corruption path.
(Fulcrum rule.)

- **One lease file per app**, same `holder`, `acquired`, `ttl_seconds`, `task`, and
  `held_with` naming the others. The lock stays per app, so a reader of one file needs
  nothing else to see it is taken.
- **Acquire all or none.** Write them in sorted identifier order. If any is live under
  another holder, delete those just written and treat the dispatch as not ready. A
  partial set blocks one lane to no purpose and, with the opposite order elsewhere, two
  agents can each hold half forever.
- **Release all together**, on `session_state: closed`. **Hold all together**, on
  `session_state: open`: `open_session` goes in every file. The Mentor session is one
  thing, so its lock must not end app by app.
- **A break covers the set.** Check `held_with`, and confirm no run is in flight on any
  held app before overwriting any of the files.

## Studio hand-off - `holder: user`

Fulcrum rule. Any `manual` row that hands an app to the user in Studio holds the app
too, whichever skill emitted it: the design loop's Studio lane
(`../../fulcrum-design-loop/references/build-lanes.md`, heading "Studio lane"), an agent
replay (`../../fulcrum-engine-traps/references/agents.md`, entry 4), or any other Studio
step on an app that exists. A Studio session and a Mentor session on one app are two sessions building it,
and neither sees the other. A Studio session is invisible to this file, so the lease
records the hand-off, not the session.

- **Write.** At the hand-off, with every agent change published and no Mentor session
  open on that app, the orchestrator writes `lease.<app>.json` with `holder: user`, `task`
  that row and `ttl_seconds` sized to the expected pass, and appends a `hold lease` line.
  The row stays `manual`, `parked`, `Blocked on: the user`; there is no new status.
- **It counts as live at any age.** Never broken on expiry and never adopted: there is
  no dispatch to know dead, so expiry says only that it is time to ask the user. Ask.
  Steps 3 and 4 of "Acquire", "Breaking an expired lease" and "Resuming after a dead
  session" give no route past it.
- **No Mentor session opens on that app**, a read-only one included, until it is released.
  Other apps keep running. Non-Mentor checks of a published revision still may.
- **Release** on the user's "published": the orchestrator reads the live revision with
  `env_app`, records it in the session file, deletes the file and appends a `release
  lease` line. Only the user's answer ends it.

## Breaking an expired lease

An expired lease means the holder died or the TTL was set too short. Both are real, so
expiry alone is not proof the app is idle. A lease is breakable only after its own TTL
has expired **and** the holder's dispatch is known dead: no return, and its budget
exceeded. A holder whose dispatch may still be running is waited on or halted for.

1. Confirm independently that no Mentor run is still in flight on that app: read the
   tail of `RUN-IDS.md` and the previous holder's `journal/<session-id>.md` for a
   `started` line with no recorded outcome,
   and poll any such run to a terminal state through the MCP surface before doing
   anything else. A run in flight outranks an expired lease.
2. Only then overwrite the lease with your own.
3. Append a session-file line recording the break, naming the previous holder and its
   `acquired` timestamp. An unrecorded break makes a later corruption undiagnosable -
   there is no other trace that two agents both believed they held the app.

## Resuming after a dead session

Polling a known run needs no lease: a read cannot race a turn, and a run left unread is
how a run id goes unpollable.

To dispatch on the lane again, a new session adopts the dead session's lease rather than
breaking it. A TTL is no test here: a hold until the user decides can outlast the session.

1. Confirm the session is dead (no return, budget exceeded, or the user says so) and
   no run is live for that app, as in step 1 above, across any `held_with`.
2. Rewrite the lease with your own `holder`. Keep `open_session`: the next dispatch
   resumes that session.
3. Append a session-file `adopt lease` line naming the previous holder and `acquired`.

## What the lease does not protect against

State this plainly rather than trusting it further than it goes. `[UNVERIFIED]`

- **Another machine, or another checkout.** The lease is uncommitted, so it is visible
  only to agents sharing the filesystem. Cross-machine concurrency on one app is a
  human coordination problem; `.fulcrum/` does not solve it, and nothing in git can,
  because a push is not a lock.
- **A human working in the portal.** The platform attributes every publish to the
  authenticated tenant user regardless of origin, so a portal-made change is
  indistinguishable from an agent-made one after the fact. `[VERIFIED]` The lease
  cannot see it at all. A `holder: user` lease records a declared hand-off and nothing
  more.
- **A race between two agents reading the file at the same instant.** The read-then-write
  is not atomic. Acquiring is a convention, not a guarantee. It closes the common case
  - a second session started minutes later - and nothing more.

Because of all three, the lease never replaces the staleness guard: re-read the live
app revision immediately before any mutating turn, per
`../../fulcrum-mentor-turns/SKILL.md`.
