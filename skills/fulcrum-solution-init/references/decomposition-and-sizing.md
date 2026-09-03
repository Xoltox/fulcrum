# Solution decomposition and step sizing

Read this for steps 4 and 5 of `../SKILL.md`. It covers how to split a solution into
apps, agents and workflows, and how to size phases and steps against measured cost.

## Part 1 — Decomposition

### Apps

Split on **persona plus lifecycle**, not on screen area or on volume of screens.

Reasons to open a new app boundary:

- A genuinely different persona with a different entry point and different data scope.
- A different release cadence or a different deployable owner.
- A hard data-isolation requirement.

Reasons that are **not** enough:

- "The plan has a lot of screens." A large screen count is a phasing problem.
- "These screens are about a different domain area." That is a module or a flow.
- "It would be tidier." Tidiness inside one app is free; a cross-app dependency is not.

Every extra app boundary costs a dependency that every later step must respect, a second
theme surface to keep consistent, and a publish ordering constraint. Default to one app
and justify each additional one in the plan.

### Agents and workflows

For each behaviour, classify it and write the classification down:

| It is a… | When |
|---|---|
| Server action | Deterministic, synchronous, inside one request |
| Workflow | Multi-step, long-running, or spanning a human wait or an external event |
| Agent | Requires model reasoning over unstructured input, or a non-deterministic decision |

Name each one and name its trigger. An unnamed, untriggered agent in a plan is a
placeholder that a later session will implement as a screen.

Classify conservatively. An agent introduced where a server action suffices adds
non-determinism to a build that already has plenty.

### Entity ownership

- **Exactly one owning app or library per entity.** Write the owner into the plan next to
  the entity.
- **Consumers reference the owner. They never redeclare it.** A redeclared entity is two
  entities that look like one, and the divergence surfaces as data that "disappears".
- **Shared reference data belongs at the lowest level** everything above it can consume.
- **Confirm the cross-app consumption mechanism against the tenant** before planning
  around it, and record what you confirmed. `[UNVERIFIED]` — the reference engagement
  shipped a single-app solution, so multi-app entity sharing was never exercised there.
  Treat any multi-app data plan as unproven until you have confirmed it on the tenant.

### Deployable units

State which apps and libraries ship together. That set is what "demoable" means at a
phase boundary, and it is what the publish sequence at the end of each phase must cover.
Publish sequencing itself: `../../fulcrum-mentor-turns/SKILL.md`.

## Part 2 — Phase sizing

### Global-then-local ordering

1. **Global, once, up front:** theme, navigation shell, data model.
2. **Then vertical slices**, one at a time: cheapest and most central slice first.

A vertical slice is data + screens + navigation for one coherent user job. Slicing
horizontally instead — all entities, then all screens, then all bindings — leaves the
solution un-demoable for the whole middle of the build and defers every integration risk
to the end.

"Cheapest and most central first" resolves ties: the slice that the most other slices
depend on, weighted down by how expensive it is. Auth and a primary dashboard usually
win. A settlement or reporting slice usually loses.

### Every phase ends demoable

Hard rule. **Never leave the solution mid-transformation across a session boundary.**
An unattended orchestrator resuming into a half-transformed model cannot tell a
deliberate intermediate state from a defect, and will "fix" the intermediate state.

Practical consequences:

- Navigation only ever lists screens that exist in the current phase. A nav entry to a
  screen built next phase is a broken link in a demo.
- A phase that renames or restructures something finishes the rename inside the phase.
- If a phase would end mid-transformation, the phase is drawn wrong. Redraw it.

### Data before screens

Seed before building any screen that reads it. A screen built against an empty table
looks identical whether the binding is correct or absent, so the build agent gets no
signal and the fix turns get spent later at higher cost. Loader patterns:
`../../fulcrum-seed-data/SKILL.md`.

### Phase count and shape

Reference engagement: a ~28 screen/flow-group scope became **5 phases, 47 numbered
steps**. `[SINGLE-OBSERVATION]`

Shape that worked:

| Phase | Content |
|---|---|
| 1 | Theme, navigation shell, auth, data model, seed, one dashboard slice |
| 2–4 | One vertical slice each, cheapest and most central first |
| 5 | Remaining slice plus a cross-phase QA pass (reachability, nav completeness, visual parity) |

Explicitly: **a ~28-screen scope is not a one-shot, and neither is a 12-screen one.**
`[VERIFIED]` If a plan proposes doing a solution-sized scope in one session, that is the
error, not the ambition.

## Part 3 — Step sizing

### The right-sizing test

A step is right-sized when **a fresh agent with no history can execute it against one
written spec within a cap of one build turn plus two fix turns.**

Every clause carries weight:

- **Fresh agent** — no memory of earlier steps. Anything the step needs must be in its
  spec.
- **One written spec** — if the agent must read a second file to proceed, the step is
  under-specified or drawn across a boundary.
- **One build plus two fix turns** — if it habitually needs more, split it. The cap is a
  measuring instrument here; as a stop condition it belongs to
  `../../fulcrum-unattended-guardrails/SKILL.md`.

### Cost anchors

Measured in the reference engagement. `[SINGLE-OBSERVATION]` Budget from these.

| Step type | Observed cost |
|---|---|
| Seed / data step | 4+ hours, 14 Mentor turns, ~18 revisions |
| Heavy screen step | ~14 Mentor turns, ~46 minutes |
| Light screen or fix step | Materially less; not separately measured |

Two things to take from this:

- **Seed steps are the most expensive class, not the cheapest.** They look trivial and
  are not, because verifying that rows actually landed is itself expensive when there is
  no model-layer row read (see `db_query` in `tenant-profile.md`). Size a seed step as a
  step in its own right, never as a preamble bolted onto a screen step.
- **A "one turn" spec is a fiction.** Steps that were sized to one Mentor turn ran ~14.
  Size steps by *scope*, and let turn decomposition inside the step be the build agent's
  business under `../../fulcrum-mentor-turns/SKILL.md`.

### Splitting a step that fails the test

In order of preference:

1. **Split data from presentation.** Schema, then seed, then screens.
2. **Split by screen.** One screen per step for heavy screens.
3. **Split within a screen** along the natural turn boundaries — data retrieval, then
   layout skeleton, then real widgets and bindings. If a single screen needs this, it is
   a multi-step screen, and the plan should say so.

Do not split by "and then polish". Cosmetic parity is never worth a capped turn; make it
a non-goal in the spec and, if it matters, a later dedicated pass.

### Numbering and stability

Number steps once, globally, and never renumber. Downstream logs, specs and handoffs all
cite step numbers; renumbering silently invalidates every citation. Insert as `12a`,
`12b` rather than shifting the sequence.
