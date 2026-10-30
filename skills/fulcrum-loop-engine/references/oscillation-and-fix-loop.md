# Oscillation detection and the bounded fix-loop

Two mechanisms at two scales. The **fix-loop** bounds attempts *within* one
iteration. **Oscillation detection** bounds attempts *across* sessions. They use
different evidence and must not be collapsed into one counter.

| | Fix-loop | Oscillation detection |
|---|---|---|
| Scope | One step or batch, one session | One task id, whole project history |
| Evidence | Turns issued in this iteration | `:fail` entries in `.fulcrum/JOURNAL.md` |
| Ceiling | 1 build (a pass of <= 4 short turns counts as one) + 2 fix turns | 2 `:fail` entries |
| Owner of the number | `../../fulcrum-mentor-turns/references/granularity.md`, "Turn economics" | `../../../AGENTS.md`, "stuck twice" |
| On breach | Stop the inner loop, record `fail` | Hand to guardrails: a lane stop |

## The fix-loop

A failed verify keeps the iteration open. The inner loop runs between phases 5
and 6 of `../SKILL.md`, heading "The canonical iteration", inside the driver dispatch,
so it sees what the driver sees: read-back and G0. Anything later: "Late failures"
below.

```
verify -> fail
  diagnostic step        (mandatory before fix turn 2 onward)
  fix turn               (informed by what the diagnostic showed)
  re-run read-back       (only; a fix report is not proof)
  record the attempt     (session-file line, before the next attempt)
-> pass, or ceiling reached
```

**The diagnostic step is not optional and is not a fix.** A fix turn with no new
evidence behind it is the first attempt again, not a second one, and it fails
the same way. What counts and what does not:
`../../fulcrum-unattended-guardrails/references/halt-conditions.md`, heading
"The diagnostic step is not optional". That file owns the rule; this one only
says where it sits in the loop.

**What the diagnostic reads back.** Model state is read by the instrument that
can see it: published-state inspection when the model is published (once
indexed - the lag is variable, so an empty read is "not yet indexed", not an
absence), Mentor read-back only as
belief, and wire evidence (the target's own log, from
`.fulcrum/external/<system>.md` `## Log locations`, or a probe endpoint) for
settings and consumed REST structures, which have no published-state view. If
Mentor contradicts an independent instrument, trust the instrument and journal
the contradiction. Table:
`../../fulcrum-verification/references/defect-instrument-matrix.md`, heading
"Instrument by model state".

Rules the loop adds:

- **A fix inside a dispatch re-runs read-back only.** Orchestrator gates run between
  dispatches. A fix turn reporting success is not proof; the rung that failed is the
  rung that must pass, so a gate that failed is re-run whole, never swapped for a
  cheaper rung.
- **Record each attempt before issuing the next.** An attempt held only in
  context is invisible to the crash-recovery path and to the scan below.
- **Never escalate model tier** to break it (`../../../AGENTS.md`). A higher
  tier buys a more expensive version of the same guess; the missing input is
  evidence about the live system, not reasoning capacity.
- **The guard runs once per dispatch.** A fix turn runs in the session the guard
  tested, so it runs no second guard. A new dispatch opens with its own.

On the ceiling: write `Verdict: fail`, record it, then run the oscillation scan
immediately (phase 7). What follows is guardrails' call, not the loop's: a lane
stop, where the row parks, its dependents hold and other lanes continue
(`../../fulcrum-unattended-guardrails/references/halt-conditions.md`, heading
"Lane stops").

## A failed batch

A batch is one dispatch, so it shares one ceiling: 1 build + 2 fix. This covers a
failure inside the dispatch. Fulcrum rule:

1. Batch fails: diagnostic, then **one fix turn on the batch**, then re-verify.
2. Still failing: **split per row.** Rows the driver reported OK keep their
   verdict. Each other row runs solo, in ID order, with the one fix turn the batch
   left it. A split row never gets a fresh ceiling: 1 build + 2 fix is what any row
   gets, and re-opening it would turn every batch into three attempts per row.
3. If the session holds unpublished changes it returns `session_state: open`: the
   lease stays and the split rows resume that `sessionId`, one at a time.
4. A batch failure is not a `:fail` on its rows. Only a row's own terminal verdict
   after the split is. Counting the batch would charge one defect to every
   innocent row and park them all on the second batch.

## Late failures

Fulcrum rule. A gate that runs after the driver returned finds the Mentor session
closed, so the fix-loop cannot reach it, and splitting closed rows would re-spend a
ceiling they already used. Any G1, G2 or G3 failure on rows a driver already closed:

1. Those rows are `done`, with the `Verdict` and `Gate` of the last gate they passed,
   and record no `:fail`.
2. Open one new `fix` row per failing area, new id: `Turn: fix`, `App` of the failing
   area (an app, never `solution`), `Verify` the failed rungs, `Risk: high`, `Step` of
   the row carrying the claim. Its `Verify` runs at every rigor: it is how the row closes.
3. Edit dependents to depend on it where they rest on the defect. Others run on.
4. A failed `verify` row goes back to `todo`, with the fix row in its `DependsOn`,
   scoped to what was fixed, and records a `:fail`. So G2 returns once; a second failed
   pass parks it, and a third G2 pass is a user decision.

**A `fix` row gets 2 fix turns,** no build turn, counted across dispatches from the
journal. Each brief states `fix turns remaining`. A gate failing on a `fix` row is a
`:fail` on it and it returns to `todo`; it never opens another `fix` row. Two `:fail`, or
no turns left, parks it: a lane stop.

A claim G1 or G3 had already proven that now fails is a regression, not this rule:
`../../fulcrum-unattended-guardrails/references/halt-conditions.md`.

## Stall detection

Fulcrum rule. The loop detects; `../../fulcrum-unattended-guardrails/references/halt-conditions.md`,
heading "Stall and no-op decisions", decides. The turn cap and two-fail stop see one task. Neither sees a lane that keeps
dispatching and finishing nothing, each attempt below its own limit.

**After each dispatch's record**, append a session-file `lane check` line with the
lane and its done-count (rows `Status: done`, `Verdict: pass`). The file holds the
count, so a compacted orchestrator can still read the last three.

| Signal | Test | Hand to guardrails as |
|---|---|---|
| Lane flat | Done-count unchanged across 3 consecutive dispatches of that lane | Park the lane and report. Its rows go `parked`; other lanes continue |
| All lanes flat | Every lane with open rows is flat or parked, at least one flat. A row `parked` with `Verdict: fail` reads flat; one parked on a user action does not | Halt. All lanes parked on user actions alone is a user-action stop, not a halt |
| No-op publish | Terminal publish whose revision equals the revision before it | A change that did not land: not a pass, whatever the outcome field says |

A dispatch ending in a wait on the index, a capacity stop or a user-action park is
not counted as flat: nothing failed to progress, the lane has nothing it can do. A
new session starts the count again; the two-fail rule still spans sessions.

Stall detection adds nothing to a stuck task's options. The two-fail rule stands,
and model tier is never escalated.

## The oscillation scan

### What to scan

`.fulcrum/JOURNAL.md` only - the session index, one row per session. Never the
per-session files; the index exists precisely so this query costs one read.
Column 5, `Tasks`, carries inline outcomes for each task the session reached a
terminal state on: `T-003:pass,T-004:fail,T-007:unproven`.

Schema: `../../fulcrum-project-state/references/file-schemas.md`, heading
"JOURNAL.md - the session index".

### What counts as a repeat

**Two or more `<task-id>:fail` entries anywhere in column 5, across all rows.**

- Task ids are **never reused**, even after a row is deleted, so the count is
  unambiguous and cannot be poisoned by an unrelated task.
- A `:fail` recorded minutes ago in the current session's own row counts exactly
  the same as one from six weeks ago. Recency is not a discount.

### What does not count

| Not a repeat | Why |
|---|---|
| `:unproven` | The work happened but was not proven. The next action is to re-prove it, not to re-fix it. Counting it as a failure parks a row that is only under-evidenced |
| A different task id with similar prose | The join is the id. Matching on prose invents repeats and makes the check unreproducible |
| Repeated fix turns inside one iteration | That is the turn cap's job. Counting them here would stop every task that needed its second fix turn |
| A `:fail` against a task later superseded by a new id | The new id has its own count. The orchestrator rewrites dependents' edges and closes the old row (`../../fulcrum-unattended-guardrails/references/halt-conditions.md`, heading "Lane stops"). Say so in the report rather than folding the histories together |

### When to run it

Twice per iteration:

1. **Phase 2, before dispatching.** Catches a task that a previous session
   already failed - the cross-session case, which no agent's memory covers.
2. **Phase 7, immediately after recording a `:fail`.** Catches the second
   failure at the moment it becomes the second one. Deferring to the next
   selection costs one more mutating turn against a live app.

### Mechanics

A scan is a single-file read plus a match on column 5. A grep is sufficient and
is preferable to reading the file into context when the index is large. Count
occurrences, not lines: one session's row can hold two `:fail` for one id.

```
grep -o 'T-014:fail' .fulcrum/JOURNAL.md | wc -l  # occurrences; >= 2 is the trigger
grep -n  'T-014:'     .fulcrum/JOURNAL.md          # every session that touched it
```

Match the literal `<id>:fail`, not the bare id - a bare match hits `T-014:pass`
and every id that has `T-014` as a prefix.

### The archive case

Rotation moves closed rows into `journal/INDEX-archive-<NN>.md` and leaves a
pointer line in `JOURNAL.md`
(`../../fulcrum-project-state/references/file-schemas.md`, heading "Index
growth - the arithmetic"). **A scan that stops at `JOURNAL.md` after a rotation
under-counts.** If a pointer line is present, scan the named archives too. A
rotation only moves rows whose tasks are all terminal, which is exactly the
population this query is about.

### False negatives to state plainly `[UNVERIFIED]`

The scan is only as good as phase 6. It cannot see:

- A session that crashed **before** recording its outcome. Its index row says
  `State: open` with the id still in `InFlight` - treat an `InFlight` id on a
  crashed row as a possible prior attempt and look at the session file before
  re-dispatching it.
- Work done outside Fulcrum - a human in the portal, another checkout.
- A task re-decomposed into new ids after failing. See the table above.

So a clean scan is not proof the task is untried. It is proof that nothing
*recorded* failed twice. Say which one you mean in a report.

## On detection - the loop stops, guardrails rules

The loop's whole job here is to detect and hand over. It:

1. Does **not** dispatch the task.
2. Records what it found: the task id, the number of `:fail` entries, and the
   session ids they came from.
3. Hands to
   `../../fulcrum-unattended-guardrails/references/halt-conditions.md`, which
   owns the verdict and the report to the user. A repeat is a lane stop: the row
   parks, and other lanes keep selecting.

The loop never rules that a repeat is acceptable, and never resets or discounts
a count to keep going. A count that can be argued away is not a mechanism.
