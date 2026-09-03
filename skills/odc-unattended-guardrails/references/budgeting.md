# Budgeting an unattended agent

Everything here is a **proxy or a discipline, never a measurement.** A subagent
cannot measure its own token usage, so nothing below depends on it doing so.

## The hard constraint

- There is no self-inspection tool. An agent cannot ask "how many tokens have I
  used?"
- Session-level introspection commands, where a harness has them, belong to the
  main session. A dispatched subagent cannot invoke them.
- The orchestrator learns an agent's token count only from the completion
  notification — i.e. after the agent has finished. Too late to act on.

Corollaries, both absolute:

- Never write a token threshold into a prompt. The condition is unevaluable; the
  agent ignores it or claims compliance it cannot have checked.
- Never ask an agent to report its own token usage. It will produce a number
  that then gets trusted.

What an agent *can* count reliably is **its own tool calls** — that is a count
of its own actions, not an introspection of hidden state. So budgets are
expressed in tool calls.

## Evidence base

Nine measured subagents, one session, real completion-notification counts.
[VERIFIED]

| Agent work | Tokens | Tool calls | Tokens/call |
|---|---|---|---|
| Build step, Mentor-poll-heavy | 162k | 157 | 1.0k |
| Build step, Mentor-poll-heavy | 166k | 95 | 1.7k |
| Build step, Mentor-poll-heavy | 96k | 45 | 2.1k |
| Test-fixture repair | 84k | 31 | 2.7k |
| Asset/folder triage | 78k | 38 | 2.1k |
| Screenshot capture + visual review | 89k | 25 | 3.6k |
| Codebase find + doc edit | 81k | 16 | 5.1k |
| Large-doc restructure | 70k | 8 | 8.8k |
| Handoff-doc authoring | 60k | 10 | 6.0k |

Three readings:

1. **Tool-call count is useless as a universal proxy and reliable within a
   class.** Tokens per call spans 1.0k–8.8k, a ~9x range. One global "max 60
   calls" rule would strangle a polling agent and let a document agent blow
   through its window. But the three poll-heavy agents cluster at 1.0–2.1k/call,
   which is tight enough to budget against.
2. **Reads, not calls, dominate.** The pattern inverts intuition: the cheapest
   agents per call made the most calls (polling — many small results), the most
   expensive made the fewest (reading large documents). 8 calls cost 70k; 157
   calls cost 162k. In the same session the orchestrator alone burned 141k on
   file reads.
3. **Therefore the first-order lever is controlling what gets READ.** Trimming
   call counts is second-order.

Limits — do not overclaim. Highest observed agent was 166k; nothing in the
sample hit a wall, so every budget below is an extrapolation from an observed
rate, not an observed failure point. n=9, one workflow, one tool mix. Class
boundaries beyond "poll-heavy" vs "document-heavy" are untested.
[SINGLE-OBSERVATION] on every non-poll row.

## The arithmetic

Budget against a **usable** window, not the raw one. Reserve roughly 20k for the
system prompt, the task brief, and the final report or handoff write.

```
usable             = window - 20k
tool-call budget   = usable / observed_tokens_per_call_for_the_class
checkpoint trigger = 0.65 x budget      (first durable save)
hand-back trigger  = 0.85 x budget      (leaves room to write the handoff)
```

Worked example, poll-heavy class at its midpoint of ~1.5k/call, 200k window:

```
200k / 1.5k = 133 calls   <- nominal window, no headroom
180k / 1.5k = 120 calls   <- usable  ->  BUDGET = 120
0.85 x 120  = 102         ->  hand back at 100
0.65 x 120  =  78         ->  checkpoint at 75
```

## Starting table

Recalibrate per workflow. Only the poll-heavy row rests on a cluster.

| Class | Example work | Est. tokens/call | Budget (180k) | Checkpoint | Hand back |
|---|---|---|---|---|---|
| Poll-heavy | Mentor run polling, publish supervision | 1.0–2.1k (use 1.5k) | 120 | 75 | 100 |
| Mixed action | seed-data repair, triage, small edits | 2–3k (use 2.5k) | 72 | 45 | 60 |
| Visual / binary | screenshot capture, visual comparison | ~3.5k | 51 | 33 | 43 |
| Document-heavy | search + doc edit, spec authoring | ~6k | 30 | 20 | 25 |
| Large-doc restructure | reading and rewriting big files | ~8.8k | 20 | 13 | 17 |

Give every agent its **class label** in the brief ("you are a poll-heavy
agent"), so the budget and the later recalibration line up.

## Recalibration loop

1. Label every agent's class in its brief.
2. On each completion notification, record `class, tokens, tool_calls`.
3. After ~3 agents in a class, set that class's rate to the **75th percentile**
   of observed tokens/call — not the mean. Budgets must hold for the expensive
   tail. With fewer than 3 observations use the max and mark the row provisional.
4. Re-derive the table. Repeat.
5. Re-derive after any change to the tool mix, a tool's response size, or prompt
   size. Rates are workflow properties, not model properties.
6. **An agent that overran by 3x is usually misclassified, not
   under-budgeted.** Check the class before changing the rate.

## Prevention beats handoff

Ranked by leverage, given that reads dominate:

1. **Never have an agent read a file the orchestrator already summarised into
   its brief — and never do both.** Do not inline a summary *and* say "read the
   source for detail". Pick one. Doing both makes the agent pay twice for the
   same content, and leaves it unsure which version is authoritative.
2. **Ask for the narrow form.** The summary form, the `details=false` form, the
   head of the file, grep-with-context. Fetch the full payload only once you
   know you need it. This is what makes a poll loop cheap.
3. **Read ranges, not files.** Give line ranges or a grep target, not a path.
4. **Scope tasks to about half the class budget**, not 95% of it. Agents
   overrun; leave slack.
5. **Prefer many small agents over one large one.** Two 80k agents beat one
   160k agent: each has clean context, and a failure loses half as much.
6. **Return conclusions, not transcripts.** The orchestrator pays for the
   agent's final message. "Fixed X at `path:line`, root cause Y, Z still open" —
   not a replay of the investigation.
7. **Push writes down, pull reads up.** Let the subagent write files and return
   paths. The orchestrator reads only what it must.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Token threshold in a prompt ("stop at 150k") | Unevaluable condition. Silent non-compliance. |
| Poll loop that re-fetches the full payload each iteration | Turns the cheapest class into the most expensive. Poll the summary form with a cursor; fetch detail once, at the end. |
| Re-reading the same file each iteration | Already in context. Re-read only after you changed it and need the result. |
| "Read everything, then decide" | Unbounded read volume before any narrowing. Search first, read the hits. |
| Inlining a summary *and* pointing at the source | Pays twice for one content. |
| Asking an agent for its token usage | Produces a fabricated number that gets trusted. |
| Handoff written only at the end | The case where it is needed most — sudden death — is the case where it never gets written. |
| Holding a run id or session id only in context | The handle dies with the agent; in-flight work becomes unrecoverable. |
| One giant agent "because it has all the context" | Highest-variance, highest-loss design. Split it. |

## Bootstrap on a brand-new workflow

1. Define classes from the **tool mix**, not the task name. The useful axis is
   result size: many-small-results (poll-like) vs few-large-results
   (document-like).
2. Run 3–5 agents with generous budgets. Require each to state its **final
   tool-call count** in its report — it can count that.
3. Compute tokens/call per agent from the completion notifications; group by
   class.
4. Set each class rate to the 75th percentile of its observations.
5. Derive budgets with the arithmetic above.
6. Re-derive after any change to tools, response verbosity, or prompt size.
