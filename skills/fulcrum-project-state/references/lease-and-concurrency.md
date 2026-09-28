# The lease, and what it can and cannot protect

## What it enforces

`../../../AGENTS.md`: **one Mentor session at a time per app.** `[VERIFIED]` The
rule is stated there and the operational detail is in
`../../fulcrum-unattended-guardrails/SKILL.md`, heading "Concurrency lock — one Mentor
session per app". What neither provides is a mechanism that survives the agent that
holds the rule in its own head. `lease.json` is that mechanism.

**What breaks without it.** An orchestrator can only refuse to dispatch two agents it
knows about. A second session started by a different person, a different terminal, or
a resumed crashed run knows nothing about the first. Two concurrent Mentor sessions on
one app is a model-corruption path, not a queueing inconvenience: the loser's turns
land against a model the winner has already moved, and publishing from that stale
model advances the revision while silently reverting completed work. `[VERIFIED]`

## Why it is the one uncommitted file

Everything else in `.fulcrum/` is committed, because git is the team mechanism. The
lease is not, because a committed lock is **stale by definition** — it records that
someone held a lock at push time, which is not a question anyone needs answered.
`[UNVERIFIED]` Add `lease.json` to the project's `.gitignore`.

## Shape

```json
{
  "app": "<app identifier>",
  "holder": "<stable identity: user or host plus session label>",
  "acquired": "<ISO-8601 UTC timestamp>",
  "ttl_seconds": 1800,
  "task": "T-014",
  "note": "<what is being done, one line>"
}
```

One lease file per app when the solution has several: `lease.<app identifier>.json`.
The lock is per app, so a single shared file would serialise apps that the platform
permits to run concurrently.

- `holder` must be stable across a crash and unique across concurrent agents. A
  hostname plus a session label is enough. An agent-generated random id is acceptable
  only if it is written to the lease before anything else happens with it.
- `ttl_seconds` is a **liveness claim, not a permission window.** Set it to comfortably
  exceed the longest turn the task will run, and refresh it — rewrite `acquired` — on
  every poll that comes back non-terminal. A TTL shorter than the work it covers
  manufactures the expiry case on a perfectly healthy run.

## Protocol

**Acquire**, before opening a Mentor session or starting a mutating turn:

1. Read `lease.<app>.json`. Absent → write it, append a session-file `acquire lease` line,
   proceed.
2. Present, `holder` is you → refresh `acquired`, proceed. This is the normal
   resume-your-own-work path.
3. Present, another holder, `acquired + ttl_seconds` **in the future** → the lease is
   live. **Do not take it.** Either work on a different app, or stop and report. Never
   "check whether the other agent is really running" by starting a turn.
4. Present, another holder, `acquired + ttl_seconds` **in the past** → expired. It may
   be broken, under the rules below.

**Release**, on finishing the turn — including on a failed turn, a halt, and a
deliberate handoff: delete the file and append a session-file `release lease` line. A lease
released only on the success path is a lease that leaks on exactly the runs where
recovery matters.

## Breaking an expired lease

An expired lease means the holder died or the TTL was set too short. Both are real, so
expiry alone is not proof the app is idle.

1. Confirm independently that no Mentor run is still in flight on that app: read the
   tail of `RUN-IDS.md` and the previous holder's `journal/<session-id>.md` for a
   `started` line with no recorded outcome,
   and poll any such run to a terminal state through the MCP surface before doing
   anything else. A run in flight outranks an expired lease.
2. Only then overwrite the lease with your own.
3. Append a session-file line recording the break, naming the previous holder and its
   `acquired` timestamp. An unrecorded break makes a later corruption undiagnosable —
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
  — a second session started minutes later — and nothing more.

Because of all three, the lease never replaces the staleness guard: re-read the live
app revision immediately before any mutating turn, per
`../../fulcrum-mentor-turns/SKILL.md`.
