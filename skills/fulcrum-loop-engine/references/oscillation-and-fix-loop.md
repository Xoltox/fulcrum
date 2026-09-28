# Oscillation detection and the bounded fix-loop

Two mechanisms at two scales. The **fix-loop** bounds attempts *within* one
iteration. **Oscillation detection** bounds attempts *across* sessions. They use
different evidence and must not be collapsed into one counter.

| | Fix-loop | Oscillation detection |
|---|---|---|
| Scope | One task, one session | One task id, whole project history |
| Evidence | Turns issued in this iteration | `:fail` entries in `.fulcrum/JOURNAL.md` |
| Ceiling | 1 build + 2 fix turns | 2 `:fail` entries |
| Owner of the number | `../../fulcrum-mentor-turns/SKILL.md`, "Turn economics" | `../../../AGENTS.md`, "stuck twice" |
| On breach | Stop the inner loop, record `fail` | Hand to the halt path |

## The fix-loop

A failed verify keeps the iteration open. The inner loop runs between phases 5
and 6 of `../SKILL.md`, heading "The canonical iteration".

```
verify -> fail
  diagnostic step        (mandatory before fix turn 2 onward)
  fix turn               (informed by what the diagnostic showed)
  re-verify same rungs   (not a subset, not a cheaper rung)
  record the attempt     (session-file line, before the next attempt)
-> pass, or ceiling reached
```

**The diagnostic step is not optional and is not a fix.** A fix turn with no new
evidence behind it is the first attempt again, not a second one, and it fails
the same way. What counts and what does not:
`../../fulcrum-unattended-guardrails/references/halt-conditions.md`, heading
"The diagnostic step is not optional". That file owns the rule; this one only
says where it sits in the loop.

Rules the loop adds:

- **Re-verify the same rungs.** A fix turn reporting success is not proof; the
  rung that failed is the rung that must pass. Dropping to a cheaper rung after
  a fix converts a real failure into a recorded pass.
- **Record each attempt before issuing the next.** An attempt held only in
  context is invisible to the crash-recovery path and to the scan below.
- **Never escalate model tier** to break it (`../../../AGENTS.md`). A higher
  tier buys a more expensive version of the same guess; the missing input is
  evidence about the live system, not reasoning capacity.
- **A fix turn is a mutating turn.** It re-enters the precondition gates —
  staleness included. Do not reuse a staleness result from before the failed
  build turn.

On the ceiling: write `Verdict: fail`, record it, then run the oscillation scan
immediately (phase 7). The hand-off to halt is guardrails' call, not the loop's.

## The oscillation scan

### What to scan

`.fulcrum/JOURNAL.md` only — the session index, one row per session. Never the
per-session files; the index exists precisely so this query costs one read.
Column 5, `Tasks`, carries inline outcomes for each task the session reached a
terminal state on: `T-003:pass,T-004:fail,T-007:unproven`.

Schema: `../../fulcrum-project-state/references/file-schemas.md`, heading
"JOURNAL.md — the session index".

### What counts as a repeat

**Two or more `<task-id>:fail` entries anywhere in column 5, across all rows.**

- Task ids are **never reused**, even after a row is deleted, so the count is
  unambiguous and cannot be poisoned by an unrelated task.
- Rows are per session, so two `:fail` entries necessarily come from two
  sessions — one session records one terminal outcome per task.
- A `:fail` recorded minutes ago in the current session's own row counts exactly
  the same as one from six weeks ago. Recency is not a discount.

### What does not count

| Not a repeat | Why |
|---|---|
| `:unproven` | The work happened but was not proven. The next action is to re-prove it, not to re-fix it. Counting it as a failure halts a run that is only under-evidenced |
| A different task id with similar prose | The join is the id. Matching on prose invents repeats and makes the check unreproducible |
| Repeated fix turns inside one iteration | That is the turn cap's job. Counting them here would halt every task that needed its second fix turn |
| A `:fail` against a task later superseded by a new id | The new id has its own count. Say so in the halt report rather than folding the histories together |

### When to run it

Twice per iteration:

1. **Phase 2, before dispatching.** Catches a task that a previous session
   already failed — the cross-session case, which no agent's memory covers.
2. **Phase 7, immediately after recording a `:fail`.** Catches the second
   failure at the moment it becomes the second one. Deferring to the next
   selection costs one more mutating turn against a live app.

### Mechanics

A scan is a single-file read plus a match on column 5. A grep is sufficient and
is preferable to reading the file into context when the index is large:

```
grep -c 'T-014:fail' .fulcrum/JOURNAL.md          # occurrences; >= 2 is the trigger
grep -n  'T-014:'     .fulcrum/JOURNAL.md          # every session that touched it
```

Match the literal `<id>:fail`, not the bare id — a bare match hits `T-014:pass`
and every id that has `T-014` as a prefix.

### The archive case

Rotation moves closed rows into `journal/INDEX-archive-<NN>.md` and leaves a
pointer line in `JOURNAL.md`
(`../../fulcrum-project-state/references/file-schemas.md`, heading "Index
growth — the arithmetic"). **A scan that stops at `JOURNAL.md` after a rotation
under-counts.** If a pointer line is present, scan the named archives too. A
rotation only moves rows whose tasks are all terminal, which is exactly the
population this query is about.

### False negatives to state plainly `[UNVERIFIED]`

The scan is only as good as phase 6. It cannot see:

- A session that crashed **before** recording its outcome. Its index row says
  `State: open` with the id still in `InFlight` — treat an `InFlight` id on a
  crashed row as a possible prior attempt and look at the session file before
  re-dispatching it.
- Work done outside Fulcrum — a human in the portal, another checkout.
- A task re-decomposed into new ids after failing. See the table above.

So a clean scan is not proof the task is untried. It is proof that nothing
*recorded* failed twice. Say which one you mean in a report.

## On detection — the loop stops, guardrails rules

The loop's whole job here is to detect and hand over. It:

1. Does **not** dispatch the task.
2. Records what it found: the task id, the number of `:fail` entries, and the
   session ids they came from.
3. Hands to
   `../../fulcrum-unattended-guardrails/references/halt-conditions.md`, which
   owns the verdict, the halt record and the report to the user.

The loop never rules that a repeat is acceptable, and never resets or discounts
a count to keep going. A count that can be argued away is not a mechanism.
