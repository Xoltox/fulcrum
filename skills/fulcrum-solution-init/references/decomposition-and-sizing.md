# Solution decomposition and step sizing

Read this for steps 4 and 5 of `../SKILL.md`. It covers how to split a solution into
apps, agents and workflows, how to emit the task graph, and how to size steps against
measured cost.

## Part 1 - Decomposition

### Apps

Split on **persona plus lifecycle** or a **real module boundary in the domain**, not on
screen area or on volume of screens.

Reasons to open a new app boundary:

- A genuinely different persona with a different entry point and different data scope.
- A different release cadence or a different deployable owner.
- A hard data-isolation requirement.
- A real module boundary: a part of the domain that owns its data and meets the rest
  through a narrow contract.

Reasons that are **not** enough:

- "The plan has a lot of screens." A large screen count is a phasing problem.
- "These screens are about a different domain area." A topic is a flow, not a module
  boundary.
- "It would be tidier." Tidiness inside one app is free; a cross-app dependency is not.
- "It would run in parallel." Parallelism alone is no reason to split an app: a split
  adds cross-app references and library index waits, which can cost what the lane saved.

Every extra app boundary costs a dependency that every later step must respect, a second
theme surface to keep consistent, and a publish ordering constraint. Default to one app
and justify each additional one in the plan. Each app is also a lane: parallelism only
comes from different apps, and a single-app plan is a chain whose speed comes from
batching.

### Agents and workflows

For each behaviour, classify it and write the classification down:

| It is a... | When |
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
- **The cross-app consumption mechanism is unproven until a real contract row lands it.**
  `[UNVERIFIED]` - the reference engagement shipped a single-app solution, so multi-app
  entity sharing was never exercised there. Ask at intake what the user knows, make the
  contract an explicit upstream row, and let it fail fast; do not plan a spike for it.

### Deployable units

State which apps and libraries ship together. That set is what "demoable" means at a
join row, and it is what the publishes before that join must cover.
Publish sequencing itself: `../../fulcrum-mentor-turns/SKILL.md`.

### External systems and integration targets

Name every system outside ODC that the solution calls or is called by, and decide for
each whether it already exists or is built in this engagement. Building one is out of
family (`../../../CONVENTIONS.md`, the skill-boundaries table, row "Out of family"):
the plan carries it as `Turn: external` tasks, not Mentor steps. What the plan must
do is order the contract first - `.fulcrum/external/<system>.md`, from
`../../fulcrum-project-state/templates/external-system.md`, exists before the first
ODC step that consumes the system, and that step lists the file as a precondition.
A system whose contract is unknown at planning time is an unresolved item gating that
step, not an assumption written into a spec.

## Part 2 - The task graph

Emit a graph, not a stage list. A linear plan runs one Mentor session where several
could run, and a spike-first plan pays before anything is built. The loop selects
whatever the graph makes runnable (`../../fulcrum-loop-engine/SKILL.md`), so the graph
is where parallelism and speed are won or lost.

### Shape

```
foundation (serial)      shared entities, cross-app contracts
  -> lanes (fan out)     one per app: base, UI, logic, polish
  -> gate rows           join, demo script, final G2 last
```

- **Foundation rows** come first and serial: anything several lanes read.
- **Lanes fan out**, one per app. Standard lane order inside an app: base, UI, logic,
  polish. Base carries the app's theme, navigation shell, entities and seed. A row on one
  lane never waits for another lane unless a `DependsOn` says so.
- **Cross-app contracts are explicit upstream rows.** A consumer depends on the contract
  row (entity or REST shape, auth, URLs), not on the whole producer app, so the producer
  lane can keep going. Slowest lane gates nobody.
- **Non-Mentor rows** (`verify`, `code`, `infra`, `external`, `manual`) sit in the graph
  like any other and run alongside; they take no lease.
- **Library consumers need the index, not just a dependency.** Emit the row `blocked`,
  depending on the row that publishes the library, `Blocked on` naming that producer,
  `Unblocks when` "element shows in `context_actions`". Plan other rows of that lane
  around the wait: the lane never stalls on it. A Workflow can be made with its app in one multi-asset session; a library cannot
  (`../../fulcrum-mentor-turns/references/mcp-surface.md`).
- **An agent's shell comes from Studio.** Emit a `manual` row, parked `Blocked on: the
  user`, ahead of the agent's first Mentor row, which depends on it: "Create agent shell
  `<Name>` in Studio, publish it once, send the asset key." A Mentor-made shell has come
  out empty or unreferenceable, and an unpublished one is unreachable from another
  session (`../../fulcrum-engine-traps/references/agents.md`, entries 3 and 10).
- **Agent consumers need the index too.** Emit the row `blocked`, depending on the row
  that publishes the agent, `Blocked on` naming that producer, `Unblocks when` "service
  action shows in `context_actions`". The wait has run overnight, not minutes, so plan
  the lane's other rows around it (`agents.md`, entry 9). The agent is its own `App` lane:
  a parked agent row holds only its dependents (`agents.md`, entry 5).

### Gate rows

Gates are ordinary rows, so selection, crash recovery and records need no special path.
A gate owed only by convention is the one a crash loses.

| Row | `Turn` | `App` | `DependsOn` | Emit |
|---|---|---|---|---|
| Join, one per consumer app (a single-app plan has one), plus any cross-app check | `verify` | `solution` | The rows it joins | Always |
| Lane G2 | `verify` | `solution` | The lane's last row; its join depends on it | `production`, one per lane |
| Demo script, output `.fulcrum/demo-script.md` | `code` | `solution` | Nothing it cannot read | `demo` |
| Final G2 | `verify` | `solution` | All leaves | Always, once |

`solution` is a literal: no lane, no lease. Skill `fulcrum-demo` owns the demo script
format. `verify` rows carry no Mentor rung and run their rungs at every rigor; emit them
only for joins, G2 and owed G3. Micro plans get the same rows
(`../../fulcrum-project-state/templates/plan-micro.md`).

### Filling the TASKS columns

Column values and order: `../../fulcrum-project-state/references/file-schemas.md`,
heading "TASKS.md". Here, only how to choose them:

| Column | How to choose |
|---|---|
| `App` | The app the row touches, or a declared pair `<producer>+<consumer>`, one lease per identifier. It is the lane and the lease key. Gate rows: `solution` |
| `DependsOn` | Task IDs of **true data dependencies** only, or `-`. "Comes earlier in the plan" is not a dependency; a false edge turns a parallel frontier back into a chain |
| `Batchable` | `yes` when the row can share one build pass and one Publish with its neighbours on the same app, `no` otherwise. A row may batch with a row it depends on: an open id in `DependsOn` is allowed when it is in the same batch |
| `Risk` | `high` for auth, a data model change on populated data, integrations, money or PII, or anything touching a prior verified feature. Otherwise `std`. High rows run solo |
| `Verify` | The row's rung list; which rows actually pay for it depends on `Rigor`: `../../fulcrum-verification/SKILL.md`, heading "Gates and rigor" |
| `Gate` | `-` at emission. Set only from the gate a row actually ran |

Under-marking `Risk` is the expensive mistake: a `std` row batches, so an auth change
hidden in a batch shares its blast radius and skips its solo proof.

### No spike or probe rows

**Do not plan a spike or probe row to test a platform capability.** An unknown is asked
at intake, or tried on the first real row, which fails fast. Traps already live in
skills, so a known construct needs no rediscovery. A tenant capability check stays
read-only and free (`tenant-capability-probe.md`).

The failure mode: spikes consume hours and publish throwaway revisions, and prove what
the first real row would prove anyway. If a row exists only to learn something and ships
nothing, delete it and put the question to the user or to the first row that needs the
answer.

### Slices inside a lane

A vertical slice is data + screens + navigation for one coherent user job. In a large
app, group a lane's UI and logic rows by slice, cheapest and most central first, rather
than all screens and then all bindings: that leaves the app un-demoable for the whole
middle of its lane and defers every integration risk to the end.

"Cheapest and most central first" resolves ties: the slice that the most other slices
depend on, weighted down by how expensive it is. Auth and a primary dashboard usually
win. A settlement or reporting slice usually loses.

### Phases are labels

A phase is a derived label: a layer in the graph, written in `plan.md` and the `Step` id.
It is not a gate, and nothing stops at one except what the mode says
(`../../fulcrum-loop-engine/SKILL.md`).

### Every phase ends demoable

Hard rule. **Never leave the solution mid-transformation across a session boundary.**
An unattended orchestrator resuming into a half-transformed model cannot tell a
deliberate intermediate state from a defect, and will "fix" the intermediate state.

Practical consequences:

- Navigation only ever lists screens that exist by then. A nav entry to a screen built
  later is a broken link in a demo.
- A row group that renames or restructures something finishes the rename inside the group.
- If a layer would end mid-transformation, the layer is drawn wrong. Redraw it.

### Data before screens

Seed before building any screen that reads it. A screen built against an empty table
looks identical whether the binding is correct or absent, so the build agent gets no
signal and the fix turns get spent later at higher cost. Loader patterns:
`../../fulcrum-seed-data/SKILL.md`.

### Scale

Reference engagement, built before the graph existed: a ~28 screen/flow-group scope
became **5 phases, 47 numbered steps**. `[SINGLE-OBSERVATION]`

Explicitly: **a ~28-screen scope is not a one-shot, and neither is a 12-screen one.**
`[VERIFIED]` If a plan proposes doing a solution-sized scope in one session, that is the
error, not the ambition.

The opposite end: one app, about five or fewer steps, no BRD, is below what this
skill is for. The router proposes the micro profile for it
(`../../fulcrum-project-state/references/micro-profile.md`); if that engagement grows
past its size, it is promoted here with its micro `plan.md` as source material.

## Part 3 - Step sizing

### The right-sizing test

A step is right-sized when **a fresh agent with no history can execute it against one
written spec within a cap of one build turn (a build pass of up to 4 short turns
counts as one) plus two fix turns.**

Every clause carries weight:

- **Fresh agent** - no memory of earlier steps. Anything the step needs must be in its
  spec.
- **One written spec** - if the agent must read a second file to proceed, the step is
  under-specified or drawn across a boundary.
- **One build plus two fix turns** - if it habitually needs more, split it. The cap is a
  measuring instrument here; as a stop condition it belongs to
  `../../fulcrum-unattended-guardrails/SKILL.md`.

Sizing stays per row even when rows run as a batch. A batch is a loop decision over
right-sized rows, so a row too big to pass this test alone is not made safe by batching.

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
  no model-layer row read on any tenant `[SCHEMA]`. Size a seed step as a
  step in its own right, never as a preamble bolted onto a screen step.
- **A "one turn" spec is a fiction.** Steps that were sized to one Mentor turn ran ~14.
  Size steps by *scope*, and let turn decomposition inside the step be the build agent's
  business under `../../fulcrum-mentor-turns/SKILL.md`.

### Splitting a step that fails the test

In order of preference:

1. **Split data from presentation.** Schema, then seed, then screens.
2. **Split by screen.** One screen per step for heavy screens.
3. **Split within a screen** along the natural turn boundaries - data retrieval, then
   layout skeleton, then real widgets and bindings. If a single screen needs this, it is
   a multi-step screen, and the plan should say so.

Do not split by "and then polish". Cosmetic parity is never worth a capped turn; make it
a non-goal in the spec and, if it matters, a later dedicated pass.

### Numbering and stability

Number steps once, globally, and never renumber. Downstream logs, specs and handoffs all
cite step numbers; renumbering silently invalidates every citation. Insert as `12a`,
`12b` rather than shifting the sequence.
