# The lease, and what it can and cannot protect

## What it enforces

`../../../AGENTS.md`: **one Mentor session at a time per app.** `[VERIFIED]` The
rule is stated there and the operational detail is in
`../../fulcrum-unattended-guardrails/SKILL.md`, heading "Concurrency lock - one Mentor
session per app". What neither provides is a mechanism that survives the agent that
holds the rule in its own head. `lease.<app>.json` is that mechanism.

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
  "holder": "<stable identity: user or host plus session label>",
  "acquired": "<ISO-8601 UTC timestamp>",
  "ttl_seconds": 5400,
  "task": "T-014",
  "note": "<what is being done, one line>",
  "open_session": "<Mentor sessionId - only while a dispatch returned session_state: open>"
}
```

`ttl_seconds` above is an example (a 75-minute dispatch budget plus margin), not a
default - see the TTL rule below.

One lease file per app when the solution has several: `lease.<app identifier>.json`.
The lock is per app, so a single shared file would serialise apps that the platform
permits to run concurrently.

**App creation is a mutating call too.** Before `mentor_create_asset` there is no app
identifier yet: key the lease by the intended app name from `plan.md` and
`project.md`, write the journal `started` line, then create. Once the call returns the
application key, record it (`RUN-IDS.md` outcome line, then `project.md` at wave
close) and keep the same lease file until release. In the field the first journal
line and the lease came after creation, so a crash at that moment would have left an
app nobody knew existed. `[SINGLE-OBSERVATION]`

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
  covers a whole plan step (guard, consult, build, fix, Publish), so the TTL must cover
  all of it. A TTL shorter than the work it covers manufactures the expiry case on a
  perfectly healthy run.

## Protocol

**Acquire** (the orchestrator), before a Mentor dispatch:

1. Read `lease.<app>.json`. Absent -> write it, append a session-file `acquire lease` line,
   proceed.
2. Present, `holder` is you -> rewrite `acquired` and `ttl_seconds` for the new
   dispatch, proceed. This is the normal resume-your-own-work path.
3. Present, another holder, `acquired + ttl_seconds` **in the future** -> the lease is
   live. **Do not take it.** Either work on a different app, or stop and report. Never
   "check whether the other agent is really running" by starting a turn.
4. Present, another holder, `acquired + ttl_seconds` **in the past** -> expired. It may
   be broken only if the holder's dispatch is also known dead (it never returned and
   its budget is exceeded), under the rules below.

**Release** (the orchestrator), when the dispatch returns `session_state: closed` -
including on a failed turn, a halt, and a deliberate handoff: delete the file and append a
session-file `release lease` line. A lease released only on the success path is a lease that
leaks on exactly the runs where recovery matters.

**Hold** (the orchestrator), when the dispatch returns `session_state: open` (a budget stop,
or a halt with `on_exit: keep-open`, typically with `unpublished_changes: yes`): do **not**
release. The app still has a live Mentor session, and a second session on it is the
corruption path this file exists to prevent. Rewrite the lease with `open_session` set to the
returned `sessionId` and a new `acquired` / `ttl_seconds` sized to the expected resume dispatch
(or, when the next move is the user's, to a hold until the user decides), and append a
session-file `hold lease` line naming the sessionId. The next action is either a resume
dispatch of the **same** step with that `sessionId`, or a halt for the user (`HALT.md`
records the open sessionId). Release only when a later dispatch returns
`session_state: closed`. (Fulcrum rule.)

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

## What the lease does not protect against

State this plainly rather than trusting it further than it goes. `[UNVERIFIED]`

- **Another machine, or another checkout.** The lease is uncommitted, so it is visible
  only to agents sharing the filesystem. Cross-machine concurrency on one app is a
  human coordination problem; `.fulcrum/` does not solve it, and nothing in git can,
  because a push is not a lock.
- **A human working in the portal.** The platform attributes every publish to the
  authenticated tenant user regardless of origin, so a portal-made change is
  indistinguishable from an agent-made one after the fact. `[VERIFIED]` The lease
  cannot see it at all.
- **A race between two agents reading the file at the same instant.** The read-then-write
  is not atomic. Acquiring is a convention, not a guarantee. It closes the common case
  - a second session started minutes later - and nothing more.

Because of all three, the lease never replaces the staleness guard: re-read the live
app revision immediately before any mutating turn, per
`../../fulcrum-mentor-turns/SKILL.md`.
