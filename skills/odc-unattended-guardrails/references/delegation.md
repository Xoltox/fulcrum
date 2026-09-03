# Delegation boundaries

## Depth is one level. Full stop.

The orchestrator dispatches. **Subagents never dispatch.** Parallel agents are
siblings under the orchestrator — a builder and a poller run side by side, never
one inside the other.

There is no dial, no per-task grant, no depth counter. One level.

### SUPERSEDED — "successor spawning"

The source corpus documents a pattern in which an agent that reaches its call
budget writes a checkpoint, spawns a successor whose brief is "resume from
`<checkpoint path>`", and returns. It documents that pattern with a maximum
chain depth and a current depth passed in the prompt.

**That pattern is SUPERSEDED and must not be used.** It predates the one-level
policy, and it is the single thing in the corpus a future agent could cite to
grant itself nesting. Its own text concedes it has no measurements behind it.

Why it is out, plainly:

- **Unbounded chains.** Each successor can spawn another. Work never converges
  and spend has no ceiling — a depth dial is only as good as the agent's
  willingness to read it, which is exactly what is untrustworthy in the
  unattended case.
- **Drift.** Every hop loses whatever the checkpoint failed to capture. A few
  hops in, the successor is solving a different problem, confidently.
- **Hidden cost.** The orchestrator dispatched one agent and is billed for six.
- **No supervisor in the loop.** The successor inherits no context, so the
  checkpoint quality *is* the handoff quality — and a chain amplifies a weak
  checkpoint instead of catching it.

### What to do instead — orchestrator-driven continuation

Same result, with a supervisor in the loop:

1. The agent reaches its hand-back trigger (0.65/0.85 of budget — see
   `budgeting.md`).
2. It finalises the checkpoint file and **returns** to the orchestrator with a
   terse report and the checkpoint path.
3. The orchestrator reads the **checkpoint file, not the agent's transcript**,
   decides whether continuing is still the right move, and dispatches the next
   agent with a fresh self-contained brief.

Step 3 is the point. A checkpoint that reveals the work has gone sideways stops
the chain there, instead of funding five more hops.

## Orchestrator prohibitions — categorical

The orchestrator does four things: read state, write a self-contained brief,
dispatch, read the terse report back.

It must **not itself** call `mentor_start` / `mentor_get_run`, call
`publish_start` / `publish_status`, call a `context_*` inventory tool, curl a
REST endpoint, or run browser automation or a verification gate script.

The clauses that get violated, so they are stated separately:

- Not **to finish a small remaining piece** of a step whose agent has returned.
- Not **to "just quickly check"** something.
- Not **when a prior agent left a run half-done.** Dispatch an agent to resume
  that run — polling the *same* run id, never starting a competing one, since a
  competing turn on the same session is how a mutating turn ends up racing.

**Sole exception:** a live blocker needing the user's own action — re-auth, a
portal-only operation, an operation with no MCP path at all. A single direct
attempt to confirm the block is genuine is acceptable. Do **not** iterate
looking for a way around it. Confirm once, then report and wait.

Why it is categorical rather than a preference: the inventory tools return very
large payloads and the polling loops run for many minutes, so a single inline
call can consume more of the orchestrator's window than an entire delegated
step. Once the orchestrator's context is spent, the session's ability to
supervise anything is gone — and that happens quietly, mid-run.

The source corpus's own reusable guide transcribed only half of this rule,
dropping the "not even to check" clause. Restore it every time.

## What a brief must contain

Non-negotiable in every subagent brief:

1. **The objective**, self-contained. The agent should not need to reconstruct
   intent from project documents.
2. **The class label** and the **tool-call budget**, with its checkpoint and
   hand-back numbers (`budgeting.md`).
3. **The checkpoint file path**, supplied by the orchestrator, plus the
   instruction to write it continuously. The agent does not invent a path.
4. **The model tier**, set explicitly (`../../../MODEL-TIERS.md`). Never rely on
   inheritance — inheritance is what makes a tier policy silently untrue.
5. **Scope boundaries** — what to read, what **not** to read, what is already
   summarised in the brief and must not be re-read.
6. **The file scope it owns.** Under concurrency this is what prevents two
   agents writing the same file. Shared project documents belong to the
   orchestrator; the agent reports what should go into them.
7. **The Mentor concurrency status** — whether it is permitted to touch Mentor at
   all in this dispatch.
8. **The turn cap and the halt rule** — 1 build + 2 fix turns; stuck twice after
   a diagnostic step means stop and report.
9. **"Correct my briefing — a correction beats agreement."** Verbatim, in every
   brief. [VERIFIED] On the source build this single line surfaced most of the
   corrections to the project's own documented claims: a false choice passed
   along in a brief, an over-broad trap entry, a CSS utility class that did not
   port across elements, a broken session id/token pair, and a stale invariant
   check. It is a **prompt mechanism, not a model-tier effect** — it does not
   become unnecessary at a higher tier, and it is the cheapest guardrail here.
10. **The disclosure requirement** — report turn-budget overruns with the actual
    count, any scope cut, any deviation, and explicitly **what could not be
    verified**.

## Never inline and also point

Do not put a summary of a long reference document in a brief *and* tell the
agent to go read that document. Pick one.

- Inline it when the agent needs only a stable subset. Then say "do NOT read
  `<path>` — the relevant content is above."
- Point at it when the agent needs to navigate it. Then give a line range or a
  grep target, not a whole path, and do not pre-summarise.

Doing both makes the agent pay twice for the same content and leaves it guessing
which version is authoritative.

## Concurrency

- **One Mentor session per app** — the lock is per app, not per tenant.
  [VERIFIED] Never dispatch two agents concurrently if both may touch Mentor on
  the same app. A poller watching a run and a builder driving the next turn are
  not safely concurrent unless the builder provably cannot start a turn.
- **Across different apps, concurrent sessions are allowed** — useful when a
  solution spans several apps. Maximum concurrency is unpublished and may change
  server-side. [UNVERIFIED] Plan for it to be lower than you expect: fan out
  opportunistically, degrade to sequential on rejection, and never let a step's
  completion depend on a specific number of parallel sessions.
- Safe parallel pairs are ones where only one side touches Mentor at all — for
  example a Mentor builder alongside a documentation or seed-data agent with a
  disjoint file scope.
- **Disjoint file scopes, always.** Two agents writing the same file under
  concurrency produce a last-writer-wins loss with no error.
- Before dispatching anything that will mutate the model, confirm no other
  dispatch is outstanding. If you cannot confirm it, serialise.
