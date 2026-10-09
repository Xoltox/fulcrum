# Tool availability and fallback

Extends `tenant-capability-probe.md`. Read this when the probe reaches its
tool-availability section, or when a step is about to depend on an op that has
never been confirmed callable on this tenant.

## The governing rule

**A schema that loads is not a tool that dispatches.** Tool discovery and tool
dispatch are separate paths. Successfully fetching an op's schema proves only
that the operation is *described* somewhere — not that calling it reaches a
working implementation. An agent that treats schema availability as proof of
callability finds this out mid-build, after it has already committed to a plan
that needs the op.

This rhymes with this skill set's founding thesis: a clean platform signal
proves nothing about the thing actually working. Zero validation errors and a
clean publish don't prove correct rendering or logic
(`../../../CONVENTIONS.md`); a listed, schema-complete tool doesn't prove it
dispatches. Same shape, one layer earlier.

**One tenant, one harness, one point in time.** A tool confirmed unavailable
today may work on another tenant, another harness wiring, or after a server
update next week. Nothing here is a general platform claim — see the
three-state probe below, which is exactly the mechanism that keeps this from
being hardcoded.

## Fallback table

Only for ops with a genuine alternative path. Where there is no fallback, the
row says so — do not invent a workaround; halt instead
(`../../fulcrum-unattended-guardrails/SKILL.md`, heading "Halt on an
unavailable op with no fallback").

| Op confirmed unavailable | Fallback | Why |
|---|---|---|
| `app_create`, `publish_start`, `mentor_start`, `mentor_cancel` | Not a fallback case: these tools are absent from the live surface (dated record: `../../fulcrum-mentor-turns/references/mcp-surface.md#tool-families`). Creation is `mentor_start_session` then `mentor_create_asset`; see `mentor-turns` `mcp-surface.md#creating-and-loading-an-asset`. | Do not probe for them or treat their absence as an outage. |
| `mentor_publish` | A `mentor_prompt` turn with the message "Publish" | `mentor_publish` is deprecated by the server itself. `mcp-surface.md#publishing`. |
| `context_graph` | The specific `context_*` ops this skill set already uses instead: `context_entities`, `context_screens`, `context_actions`, `context_roles`, and the rest of the `context_*` family the app needs | Two independent reasons, not one: (1) `context_graph`'s underlying model conversion can time out against a real app rather than returning `[SINGLE-OBSERVATION]`; (2) a separate finding marks `context_graph` concurrency-sensitive — it must not be called in parallel with other work — which already made it a poor fit for this skill set's fan-out posture before availability was ever in question. |
| `publish_status` / `publish_logs` | Not unavailable. Semantics are now recorded: publishing is a Mentor "Publish" turn, the key arrives in the run, and `publish_status` polls it. See `../../fulcrum-mentor-turns/references/mcp-surface.md#publishing`. An earlier 404-on-every-key observation was inconclusive (no genuine key existed). |  -  |
| Any other op with no row above | None. Route to the halt rule. | Improvising a path around a missing capability is exactly the drift `../../fulcrum-unattended-guardrails/SKILL.md` exists to prevent. |

## What "unknown" means and why it must stay unknown

A read-only probe must never call a mutating op to learn whether it dispatches
— doing so would itself be the kind of destructive write this skill set guards
against. So every mutating op starts, and by construction stays, **unknown**
until some real step in the engagement dispatches it for its own reason and the
outcome is recorded. Unknown is the correct and expected state for these ops —
it must never be silently upgraded to "available" because no failure was ever
observed. Absence of a failure is not evidence of success when the op was never
tried.
