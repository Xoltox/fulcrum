# Inventorying what actually exists

The inventory is the report's ground truth. It comes from the platform's own
context/inventory operations — never from the requirements document, never from a design
export, and never from an agent's prose summary of what it saw.

## Operations, and what each settles

Bare operation names; map them to your harness's wiring yourself.

| Need | Operation | Notes |
|---|---|---|
| Entities and their attributes | `context_entities` | Attribute-level detail is the point. A requirement usually turns on one attribute, not on the entity existing. |
| Screens | `context_screens` | Existence only. Reachability is a separate question — see below. |
| Roles | `context_roles` | The role list, and per-screen assignment, are different findings. |
| Server actions and functions | `context_actions` | The place where "schema present, logic absent" becomes visible. |
| Structures | `context_structures` | Usually integration payload shapes. |
| Integrations and external connections | `context_connections`, `app_refs` | `app_refs` also gives cross-app and library dependencies. |
| AI agents | `context_agents` | |
| Theme | `context_themes` | Rarely a requirement; occasionally a Drift finding. |
| Relationships between elements | `context_graph` | Use for "what references this entity" questions the flat lists cannot answer. |
| Anything by name across the app | `context_search` | Use it before filing any Gap: a named search is how you avoid filing an absence for something named differently. |
| App identity and revision timeline | `app_info`, `app_revisions` | Provenance, not inventory. See `provenance.md`. |

## Known blind spots — absence from an inventory is not evidence of absence

The context enumeration operations **do not list Resources, nor Automations and
Timers**. `[TENANT]` The exposed operation set varies by server version, so confirm
against the operation list your server actually exposes and record the answer in
`tenant-profile.md` (see `../../fulcrum-solution-init/references/tenant-capability-probe.md`).

Consequence, and it is the whole reason this section exists: a requirement satisfied by a
Timer or an Automation will look absent in an enumeration that cannot see one. Filing
that as a Gap is a false finding, and a false Gap in a report is worse than a missing
one — it sends someone to build a thing that already exists.

So for any requirement whose implementation would plausibly be a Resource, an
Automation, or a Timer:

- Mark the row **unresolved by inventory**, not absent.
- Say which operation would have been needed and that it does not exist.
- Name the out-of-band check that would settle it — portal inspection, or the app's own
  observable behaviour — and either run it or list it as an open question.
- Never let an unresolved row into the numerator or the denominator of a coverage figure.
  Report unresolved rows as their own count, exactly as unfalsifiable requirements are.

## Two inventory facts that are not on any list

- **Per-screen role assignment.** A screen existing and a screen being reachable by the
  intended audience are different facts, and only the second satisfies a requirement.
  Record the assigned roles per screen, not just the role list. This is where both
  "built and unreachable" and role-inversion findings come from.
- **Logic behind an attribute.** An attribute exists in `context_entities` whether or
  not anything reads it. Cross-check with `context_actions` and `context_graph` before
  treating a schema element as evidence that a behaviour exists.

## Do not trust a prose read-back

Mentor's own read-back of the model is not reliable evidence — it has misreported counts
and claimed a fix worked while the rendered output still showed the defect. `[VERIFIED]`
Take inventory from the operations directly. For the general rule and the proof ladder,
see `../../fulcrum-verification/SKILL.md`, heading "The proof ladder"; this skill only
needs its rung 1, demanded verbatim.
