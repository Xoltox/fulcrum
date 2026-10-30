# Frontier, lanes and batches

Phase 1 of `../SKILL.md` in depth: which rows run next, which run together, and
what holds what back. Every number here is a Fulcrum rule, unmeasured. Tagged
lines are platform evidence; the tool facts behind them live in
`../../fulcrum-mentor-turns/references/mcp-surface.md`.

A **lane** is one app's rows (the `App` column). A **dispatch** is one driver run
on one lane: one batch, or one solo row with the rest of its plan step.

## Select

Run at loop start and each time a dispatch ends. There is no wave barrier: when
one lane's dispatch ends, select again for that lane, plus any idle lane the
newly closed rows made runnable. The slowest lane gates nobody. A barrier would
leave every finished lane idle while the slowest one runs.

1. **Re-check `blocked` library and agent consumers** ("Library consumers" below).
2. **Compute the frontier:** all `todo` rows whose `DependsOn` are done, grouped
   by `App`. Within a group, work in ID order.
3. **Done means** the row has `Status: done` and `Verdict: pass`, or its id is no
   longer in the table (only those rows are ever removed). `unproven` and `fail`
   are not done: building on them is building on work nobody showed to work.
4. **Skip a lane** with a driver in flight, whose lease carries `open_session`
   (its next action is a resume of the same dispatch, or a stop for the user) or
   `holder: user` (at any age: the user is in Studio), or under a gate hold ("G1
   hold" below).
5. **Form one dispatch per lane** ("Dispatch shape" below). A row with
   `Verdict: unproven` is a re-prove dispatch ("Unproven rows" below).
6. **Run the phase 2 gates per dispatch, then dispatch every group in parallel** as
   sibling depth 1 agents, up to the in-flight cap. A harness with no parallel
   dispatch runs one lane at a time under the same selection.

A file still on TASKS schema v2 has no `DependsOn`, `Batchable`, `Risk` or `Gate`:
treat its rows as a chain in ID order, Batchable no, Risk std, and migrate on the
next rewrite (`../../fulcrum-project-state/references/file-schemas.md`, heading
"TASKS.md").

## What runs alongside what

- **One driver per app at a time.** Two sessions never build one app, so
  parallelism only comes from different apps.
- **A single-app project's frontier is a chain.** Speed there comes from batching,
  not from fan-out.
- **Global in-flight cap: 5 drivers** (Fulcrum rule; owner
  `../../fulcrum-unattended-guardrails/references/delegation.md`). 10 parallel
  read-only sessions were observed once `[SINGLE-OBSERVATION]`; builds were not
  measured, so the cap stays at 5. On the first capacity text from any driver, stop adding, let the running
  drivers finish, then continue sequentially. The capacity-stopped row goes back to
  `todo`; a capacity stop is not a `:fail`.
- **G1 hold.** G1 is a renderer or verifier dispatch after the driver returns. A
  lane is not selected again until its G1 reports: a publish there moves the pinned
  revision and G1 returns `untested`. Other lanes keep running. At `demo`, where G1
  runs only at the join, no hold is needed before the join. A `verify` row or a
  re-prove dispatch holds every lane whose app it reads the same way
  (`../../fulcrum-verification/references/gates-and-rigor.md`).
- **Non-Mentor rows run alongside.** `verify`, `code`, `infra`, `external` and
  `manual` rows need no lease and take no driver slot. They obey `DependsOn` like
  any row. An `inspect` row is a Mentor read: it takes the lease and a driver slot.
- **`App: solution` is a literal, not a lane or a lease key.** Join, final G2 and
  demo script rows carry it (`../../fulcrum-solution-init/references/decomposition-and-sizing.md`,
  heading "Gate rows"). They are ordinary rows, so selection, crash recovery and
  records take no special path.
- **Parked or blocked rows hold only their dependents, never other lanes.** A
  stopped lane that stalled its neighbours would turn one user question into a
  whole-project wait.
- **Phases are derived labels** (a layer in the graph), not gates. No stop at a
  phase boundary in `expert`. `guided` reports at a boundary and stops only if a
  decision is needed.

## Unproven rows

`Status` stays `todo`, `Verdict: unproven`: the work exists, only its proof is owed.
Select picks the row as a re-prove dispatch: the owed gate again, proof only, no Mentor
turn, no lease, no driver slot. A Mentor turn here would mutate the app to answer a
question about evidence.

A second `untested` result parks it for the user: count `<id>:unproven` in the index the
way the scan counts `:fail`. Re-proving a third time buys the same gap. A re-prove that
fails takes the late failure rule (`oscillation-and-fix-loop.md`, heading "Late
failures").

## Dispatch shape

**Solo by default.** A dispatch holds one row plus the rest of its plan step: every
`todo` row with the same `Step` and `App` joins it (a step's `build` and `publish`
rows go together), even though those rows depend on each other. They go `active`
together, each closes on its own evidence, and a row the dispatch did not reach goes
back to `todo`.

**Batch.** Consecutive rows of one app, all Batchable yes and Risk std, are one
dispatch: one guard, one consult, one build pass, one Publish, one G1. Start from a
frontier row and add the next row of that app while it qualifies and every open id
in its `DependsOn` is already in the batch. A chain batches; requiring each row to be
on the frontier first would leave a single-app project with no batching at all.

- A batch ends at what one build pass carries: up to 4 short turns
  (`../../fulcrum-mentor-turns/references/granularity.md`, heading "Turn economics"). Past that the
  turn cap is the limit, and a larger batch only moves the failure later.
- **Risk high rows run solo.** Their proof is per row, and a shared revision would
  blur which row caused a regression.
- A batch keeps one guard. Batching raises what one bad publish can take with it,
  so the guard is what stops a batch publishing over a stale model.
- The driver returns per-row verdicts, so `JOURNAL.md` stays per task and
  oscillation detection is unchanged.
- On batch failure inside the dispatch, one fix turn on the batch, then split per
  row. Turn accounting: `oscillation-and-fix-loop.md`, heading "A failed batch". A
  gate that fails after the dispatch never splits: heading "Late failures" there.
- **Consult stays under `collaborative`:** one per batch, not one per row.

## Multi-asset dispatch

A driver may hold one declared producer and consumer pair. The row declares it:
`App` reads `<producer>+<consumer>`. Selection treats the pair as one lane for that
dispatch, so it needs both apps idle.

- **Lease every app it holds**, all or none, before the dispatch
  (`../../fulcrum-project-state/references/lease-and-concurrency.md`, heading
  "Several apps in one session").
- **Gate each publication key.** One Publish can produce several publications
  (`../../fulcrum-mentor-turns/references/mcp-surface.md`, heading "Publishing"). `[SINGLE-OBSERVATION]` Gating only the
  first leaves the second unconfirmed under a recorded pass.
- **Guard each held asset.** A held copy goes stale silently, per asset.
- Observed for a Workflow with its app, once. `[SINGLE-OBSERVATION]` Do not extend
  the pair to another asset type on inference.

## Library consumers

A library consumer is never a pair: `../../fulcrum-mentor-turns/references/mcp-surface.md`, heading "Published-state inspection (context_*)". An agent consumer takes the same path, and its wait has run overnight (`../../fulcrum-engine-traps/references/agents.md`, entry 9).

- `fulcrum-solution-init` emits the row `blocked`, `Blocked on` naming the producer,
  `Unblocks when` "element shows in `context_actions`".
- Re-check at each Select, dispatched like any published-state read: the orchestrator
  never calls `context_*` itself. When the element shows, set the row to `todo`.
- The lane never stalls on it: the row holds only its dependents.
- Only if nothing else is runnable in any lane, wait with blocking reads to a ceiling
  of 60 min (Fulcrum rule; the longest lag seen was over 25 min), then report. The row
  stays `blocked`.

## No spikes

Never plan a spike or probe row to test a platform capability. Spikes consume hours
and publish throwaway revisions, and prove what the first real row would prove
anyway. An unknown is asked at intake, or tried on the first real row, which fails
fast. Traps already live in skills. A tenant capability check stays read-only and
free. If a row in `TASKS.md` exists only to test a capability, it is a plan defect:
report it, do not run it.
