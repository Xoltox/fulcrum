# Checkpoints and always-handoff-ready

## The rule

**The agent writes durable state to a file continuously, so that a handoff costs
nothing whenever it happens.**

Not "when approaching the budget". **Continuously** — after every unit of work
that produced a durable result or a resumable identifier.

## Why this beats threshold detection

Threshold detection needs a number the agent cannot see (`budgeting.md`).
Always-handoff-ready needs no number at all, and is correct in all four states:

- **Nowhere near the limit** — cost is a few small writes.
- **At the limit** — the handoff file already exists; nothing to compose under
  pressure, in the exact window where context is scarcest.
- **Handing back deliberately** — the orchestrator reads the file, not the
  transcript.
- **Dead unexpectedly** — context overflow, tool error, cancellation, crash.
  Threshold detection covers none of these, because nothing gets a chance to
  run. This case is why the mechanism is primary rather than supplementary.

## Write handles at the moment they are issued

Before doing anything with them. A run id, session id, job handle or revision
number held only in the agent's context dies with the agent.

Concrete consequence [VERIFIED]: a long-running operation was launched and its
run identifier existed only in one agent's context. The operation was later
evicted from its server-side registry and its result became **permanently
unreadable** — no way to poll it, no way to recover the work. Writing the
identifier to a file the instant it was issued would have made it recoverable.

Durable state is not only about handoff. It is about not losing handles to work
already in flight.

## What a checkpoint must contain

1. **Task** — the goal in the agent's own words, plus a pointer to the brief.
2. **Handles** — run ids, session ids, job ids, branch names, URLs, temp paths,
   and the app revision before changes. Written on issue.
3. **What has landed** — each item with **evidence**: a file path, a published
   revision, a test result, a screenshot path. "Done" with no evidence is not a
   checkpoint entry.
4. **What remains** — ordered, next concrete action first.
5. **Known gaps and open questions** — what was tried and failed, what is
   uncertain, and what the successor must **not** assume.

## Discipline

- The orchestrator supplies the path. The agent does not invent one.
- **Overwrite in place.** Do not append an ever-growing log — that file becomes a
  read cost for whoever resumes.
- Keep it short enough to read in one go. A page, not a transcript.
- Write it **before** any long, risky, or opaque operation, not after.
- No transcript, no tool output, no restatement of the spec.

## Two-part handoff structure

A project-level handoff document, as distinct from an agent checkpoint, has two
parts and they behave differently:

- **Rules** — stable. Standing constraints, the tier policy, the halt rules, the
  concurrency lock. Edited rarely and deliberately.
- **Brief** — replaced wholesale at every handoff. Current state, next action,
  live blockers.

Never let step-by-step narrative accumulate in a handoff document. The point of
the document is that a cold reader can act in one read; a growing log defeats
that, and a reader who has to skim history will skim the rules too.

## Worked example

```markdown
# CHECKPOINT — step 12 (order screens wiring)
Class: poll-heavy | Budget: 120 calls | Used: 68 | Tier: workhorse
Updated: after landing 12c

## Task
Wire the three order screens to the OrderService actions and publish.
Brief: orchestrator message; spec summary is inlined there — do NOT re-read the spec dir.

## Handles (written on issue, never only in context)
- Mentor session id: <id>
- current Mentor run id: <id>   (poll the summary form, with a cursor)
- app revision before changes: 41

## Landed
- 12a Order list bound to GetOrders    — evidence: screen exists, publish rev 42, screenshot shows 6 rows
- 12b Detail bound to GetOrder         — evidence: publish rev 43, screenshot shows populated fields
- 12c Create-form validation           — evidence: 4/4 fixture checks pass

## Remaining (next action first)
1. Bind OrderCreate submit -> CreateOrder (action exists, not bound)
2. Re-run the verification gate
3. Publish and record the revision here

## Known gaps
- CreateOrder returns no id on failure; unclear whether defect or by design. NOT investigated.
- Detail screen untested on a mobile viewport.
- Do NOT assume rev 43 is current — re-check the revision before publishing.
```

Note the last gap line. That is the staleness guard surviving the agent's death:
whoever resumes is told not to trust a revision number they did not observe.
See `../../fulcrum-mentor-turns/SKILL.md` for the guard itself.

## Resuming after a death

1. Read the **checkpoint file**, not the dead agent's transcript.
2. **Re-verify, do not trust, the "landed" list** wherever an item lacks
   evidence. Evidence is what makes an entry reusable.
3. **Re-read the live app revision independently** before any mutating turn.
   A revision recorded in the checkpoint is a baseline, not a current value.
4. For any Mentor run id in Handles, **poll that same run** — never start a
   competing turn on the same session.
5. Only then dispatch the next agent, with a fresh self-contained brief.
