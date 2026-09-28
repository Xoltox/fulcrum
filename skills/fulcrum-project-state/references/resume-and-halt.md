# Cold start, crash recovery, and the halt record

## Read order on every session start

Fixed, and short on purpose. A cold session reads these and nothing else before it
acts.

1. **`HALT.md`** — if the file exists, stop here. See "The halt record" below.
2. **`project.md`** — identity, apps, `mode`, `posture`, tier overrides.
3. **`HANDOFF.md`** — PART 1 RULES, then PART 2 BRIEF.
4. **`TASKS.md`** — the current truth. Where it disagrees with the BRIEF, it wins.
5. **The last row of `JOURNAL.md`** — the session index. It alone answers where the
   last session stopped and what was in flight. Open `journal/<session-id>.md` only
   when that row is not enough.
6. **`lease.<app>.json`** for the app about to be touched.

Do not read `plan.md`, `DECISIONS.md` or `runs/*` on a normal start. Read `plan.md`
when a task's `Step` needs resolving, `DECISIONS.md` when about to reverse or
re-litigate something, and a run file only when diagnosing that run.

## Crash recovery — the four signals of interrupted work

A crash leaves recoverable evidence precisely because state is written before the
wait, never after the result (`../SKILL.md`, heading "Write ordering — state before
the wait, never after the result"). Check all four; any one of them means work was in
flight.

| Signal | Meaning | Action |
|---|---|---|
| A `TASKS.md` row with `Status: active` | A turn was dispatched | Find its run in `RUN-IDS.md` by task ID |
| A `JOURNAL.md` row with `State: open`, or a `started` line in its session file with no matching outcome | The wait was entered and never returned | Same |
| A `RUN-IDS.md` line with no recorded outcome | A run may still be executing | **Poll that same run to a terminal state. Never start a competing turn on it.** |
| A lease held by a holder that is not you | Another agent may be live | `lease-and-concurrency.md` |

Then, and only then:

- **Re-read the live app revision independently** before any mutating turn. A revision
  recorded anywhere in `.fulcrum/` is a baseline, not a current value — publishing
  from a stale model advances the revision while silently reverting completed work.
  `[VERIFIED]`
- **Re-prove anything carrying `Verdict: unproven`.** That value exists to be
  distrusted. A `done` row with `unproven` is work that happened but was never shown
  to work; treat it as unfinished, not as finished-with-a-caveat.
- Append a recovery line to the new session's `journal/<session-id>.md`, naming what
  was found in flight, and close the crashed session's index row as `aborted`.
  Without it the interruption leaves no trace and the next anomaly looks unexplained.

## Idempotency of the writes themselves

Every write must leave `.fulcrum/` resumable, which means each one is complete or
absent, never half-applied.

- **One file per write.** Do not spread one logical update across two files with a
  gap between them where a crash changes the meaning. Where two writes are
  unavoidable, order them so the crash window is **safe pessimistic**: the row goes
  to `active` before the dispatch, so a crash over-reports work in flight rather than
  under-reporting it. Over-reporting costs one poll; under-reporting costs a
  concurrent session on a live app.
- **Append-only files are appended in whole lines**, at the end of the file only.
- **Rewritten files are written whole**, not patched in place, so a partial write is
  visible as a malformed file rather than as plausible wrong content.
- **Never delete a row or a line to record a change of mind.** Rewrite the row in
  `TASKS.md`, or append a withdrawal line to the current `journal/<session-id>.md`. A silently deleted claim
  gets re-derived — `../../fulcrum-solution-init/references/repo-scaffold.md`,
  heading "The four documentation failures to design against". `[VERIFIED]`

## The halt record

`HALT.md` exists only while the engagement is halted. **Its existence is the signal**
— there is no status field to misread and no way to be halted without the file, or to
have the file and not be halted.

It is written by whatever stopped the run, under the conditions in
`../../fulcrum-unattended-guardrails/references/halt-conditions.md`. That skill owns
*when* to halt; this one owns only the record.

Contents:

```markdown
# HALT — <ISO-8601 UTC timestamp>

- **Trigger:** <which hard stop or condition fired>
- **Task:** <T-NNN, or — >
- **App:** <app identifier>
- **Last run id:** <run id, or — >
- **App revision at halt:** <value, or "not established">

## What was being attempted
<One paragraph.>

## What was tried, and what each attempt showed
<Ordered. Evidence per attempt, not a narrative.>

## What must NOT be assumed on resume
<The specific beliefs the halting agent could not confirm.>

## What a human has to decide
<The question, stated so it can be answered without reading the transcript.>
```

### Resuming past a halt

A halt is never silently passed. `[UNVERIFIED]` Resuming without resolving it re-runs
the situation that produced the halt with the same inputs, and the halt's whole
purpose was that continuing was unsafe — so the second run fails the same way, having
spent another turn mutating a live application.

The only legal resume:

1. A human decides what changes. Nothing else clears a halt — not a later agent
   judging the problem solved, not the condition appearing to have gone away, and
   never an automatic retry.
2. Append a `DECISIONS.md` record: what was decided, by `user`, and what it affects.
3. **Delete `HALT.md` in the same change as that record.** One without the other is a
   defect: a deleted halt with no record loses why the run stopped, and a record with
   the file still present leaves the engagement stopped for no reason.
4. Append a `resolve halt` line to the current `journal/<session-id>.md` citing the
   decision id.
5. Re-establish ground truth before continuing — live app revision, any run in flight,
   the lease — exactly as for a crash. A halt may be hours or weeks old.

Never delete `HALT.md` because it is blocking progress. That is the mechanism working.
