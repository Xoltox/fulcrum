# Agents

Agent assets: the entitlement refusal, where the shell comes from, what to do when a
publish is refused, and the traps in the call itself. Publish mechanics:
`../../fulcrum-mentor-turns/references/mcp-surface.md`, heading "Publishing".

An agent is its own asset, not part of a web app `[VERIFIED]`: a plan that puts one
inside a web app halts when Mentor says so, and the re-spec adds an asset and a lease.

## 1. "Standalone Agent" is an entitlement refusal, and its meaning is unknown `[TENANT]`

The verbatim text and its validation shape:
`../../fulcrum-mentor-turns/references/mcp-surface.md`, heading "Error texts", the row
naming 'Standalone Agent'.

**Not known.** The term is undefined in the vendor docs. That it means the Agentic App
entitlement is inference only `[UNVERIFIED]`. Quote the text to the user; never state
which licence fixes it.

**Mentor carries on.** It reads the "Unavailable feature" errors as clearing later
`[VERIFIED]`, so a build turn reports nothing wrong.

**Error count does not predict refusal** `[VERIFIED]`. One asset published at 2 errors,
was refused at 4, then was refused back at the same 2. Other assets published with these
errors, and refusal changed over time. So a tolerated count is a false rule: it plans
work that the next publish refuses. Record each outcome dated in `tenant-profile.md`,
never as a standing yes or no.

## 2. Refused publish: no key, no `OS-*` code, no retry `[VERIFIED]`

**Failure mode.** The Publish turn answers in text and nothing goes live:
`mcp-surface.md`, heading "Publishing", row "A refused publish has no key". It is not a
build result, and an immediate retry repeats it. Refusal has changed over time (entry 1),
so record the date; a later row may try again.

**Tell it apart.** A text refusal for ordinary validation errors looks the same. Read the
error text: it is this entry only when it names the feature (entry 1). Anything else is a
fix turn.

**Do:** no retry. Close the session, since nothing in it can ship and the prompt is on
the row (entry 4). Set the row `parked`, `Blocked on: the user`, and report the verbatim
text. This is a user-action stop, not a halt.

## 3. The shell comes from Studio (Fulcrum rule)

Mentor-built agent shells came out empty with the wrong template, by user report
`[SINGLE-OBSERVATION]`, and a Mentor-created agent could not be referenced (entry 10).
Studio-built shells were edited by Mentor through the harness with no issues
`[SINGLE-OBSERVATION]`. One 2026-10-30 Mentor create did yield an agent, a flow and a
service action, but its publish was refused, so it proves nothing.

**Solution-init:** emit a `manual` row ahead of the agent's first Mentor row, which
depends on it: "Create agent shell `<Name>` in Studio, publish it once, send the asset
key." Publish matters: an unpublished asset is unreachable from another session
(`mcp-surface.md`, heading "Creating and loading an asset"). Then attach by `assetRefs`.
Whether Studio publishes an agent on a tenant that refused one is `[UNVERIFIED]`: if
Studio also refuses, the row stays `parked`; tell the user and quote the text.

## 4. Studio cannot pick up an unpublished harness turn `[SINGLE-OBSERVATION]`

User-confirmed: Studio can publish an agent change, but cannot see a harness turn that
was never published. So Studio cannot rescue a refused publish, and that turn's work is
gone with the session. That Studio publishes on a tenant that refused the harness publish
is `[UNVERIFIED]`.

- **Keep each agent turn small**, one change, so a refusal costs one prompt to redo.
- **Keep the exact prompt on the row** as a replay work order, quoted in `Task`.
  `TASKS.md` allows one line and no raw pipes there, which also keeps the turn small.
- **On refusal, the user replays it** in Studio Mentor, publishes from Studio, and
  reports the revision. That `manual` row writes the Studio hand-off lease, since a
  sibling row must not open a Mentor session on the agent meanwhile
  (`../../fulcrum-project-state/references/lease-and-concurrency.md`, heading "Studio hand-off - `holder: user`"). Replay has never been run `[UNVERIFIED]`: do not promise an
  identical result. Read the revision and re-inventory before the next Mentor change,
  because Studio work moves the baseline.
- **Studio also refuses:** the row stays `parked`, `Blocked on: the user`. Release the
  lease, tell the user and quote the text. Nothing an agent can do changes it.

## 5. Agent rows never block other lanes (Fulcrum rule)

The agent is its own `App` lane. A parked agent row holds only its dependents; every
other lane keeps moving
(`../../fulcrum-loop-engine/references/frontier-and-batching.md`, heading "What runs
alongside what"). Refusal timing is unknowable (entry 1), so a stop here would stall the
build on something no agent can change.

## 6. Mentor builds `CallAgentCore`; the build rejects it `[SINGLE-OBSERVATION]`

**Failure mode.** Mentor's validator passes `CallAgentCore` nodes, then the build fails
with `OS-BEW-40006`: "CallAgentCore is no longer supported. Please migrate to the
CallAgent language element". The failed publish still consumes a revision number.

**Brief:** "Build agent calls with the CallAgent language element, not CallAgentCore: the
validator accepts the old node and the build rejects it." One turn fixed it.

## 7. `OS-ABRS-FM-40001`: no non-system message reached the model `[SINGLE-OBSERVATION]`

**Failure mode.** The template left agent-level `Messages` as a System-only fallback.
Mentor said the Call Agent argument overrides it; it does not, so every call failed.
Mentor cannot set it empty. Three read-backs called the flow sound; a consult about
agent-level fields found it. A later generated agent held both System and User messages,
so read the property, do not assume either.

**Second cause, same code.** Blank input from a refresh path flooded the log.

**Brief:** "Quote agent-level `Messages` verbatim. It must bind to the `Messages` input,
because a System-only value fails every call." Binding is the fix that worked. A value
that carries its own User message is `[UNVERIFIED]`: the one agent holding both was never
published or called.
Guard empty input before every call. Never call an agent from a data action, an
aggregate or a screen refresh: they fire with no user input, repeatedly. A background
caller needs the same guard.

**Proof:** a real call. A read-back of the flow does not prove runtime.

## 8. Call limits `[SINGLE-OBSERVATION]`

| Limit | Consequence |
|---|---|
| Action calling and structured output are mutually exclusive on one Call Agent node | Plan two chained calls or a second agent |
| Server Request Timeout on a Call Agent node cannot be set through Mentor; Studio only. Same for the agent itself, timers and screens | A `manual` row, or set it on the calling `RunServerAction` |
| Client to server default 10 s. Cold agent call 24-25 s, warm 6 s; a light one 1 s | First call after idle fails unless the timeout is raised: `rest-and-integration.md` entry 15 |
| Agent service actions are Text in and Text out | The consumer deserializes; see entry 11 |
| Agent `context_*` reads return next to nothing: `mcp-surface.md`, heading "Published-state inspection (context_*)" | Plan no proof on them: model binding and flow internals are belief until a real call shows them |

## 9. A new agent can take hours to become referenceable `[VERIFIED]`

**Failure mode.** A consumer can reference an agent's public service action only once
the public-element index lists it. `context_actions` was empty at 20 minutes and Mentor
could not find it at about 13; it appeared next day. Overnight, not minutes
`[SINGLE-OBSERVATION]`.

**Do:** emit the consumer row `blocked` as for a library consumer
(`../../fulcrum-solution-init/references/decomposition-and-sizing.md`, the bullet "Library
consumers need the index" under "Part 2 - The task graph"), and work the rest of that lane. No fixed wait is safe. Stuck past that:
`rest-and-integration.md` entry 16.

## 10. "No published revision" against a deployed agent `[SINGLE-OBSERVATION]`

**Failure mode.** Referencing a Mentor-created agent failed with "AddDependency(IGlobalKey)
path requires a module signature resolver that isn't available" and "has no published
revision", while `env_app` showed it deployed. Mentor rolled the reference back. Trust
`env_app`; retrying the turn does not help. A Studio-built shell (entry 3) was referenced
at once. Mentor could not delete the old agents, so they stay until the user removes them.

## 11. Binary input and model output `[SINGLE-OBSERVATION]`

- **Image input:** the content's `FileFormat` wants a full MIME type (`image/png`), not an
  extension. Add a `MimeType` input beside the Binary. Mentor reported no Base64 built-in;
  say so in the brief rather than letting it invent one. Which models accept images is
  `[TENANT]`.
- **Model output is text around JSON:** a bare deserialize fails. Slice from the first `{`
  to the last `}`, and tolerate malformed JSON, or the raw reply reaches the user's screen.
