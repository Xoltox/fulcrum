# Template - `.fulcrum/TASKS.md`

Copy to `<project>/.fulcrum/TASKS.md`. Rewritten in place - this file is current
truth, not history. Column order is the parse contract: never reorder, never rename,
never add a column without updating `../references/file-schemas.md`, heading
"TASKS.md".

Every row is turn-shaped: a Mentor turn, or one `verify`, `code`, `infra`, `external`
or `manual` step. A row that cannot fill `App`, `Turn` and `Verify` is not a task yet - it is a plan item, and it belongs in `plan.md` until decomposed.
The rows form a graph, not a list: the loop runs every row whose `DependsOn` are done.

---

<!-- fulcrum-schema: TASKS v3 -->

# TASKS - \<solution name\>

Phases are derived labels, not gates. Closed rows are removed when their phase is
closed; their history is in `journal/` and `RUN-IDS.md`.

| Done | ID | Task | App | DependsOn | Batchable | Risk | Turn | Verify | Status | Verdict | Gate | Traps | Step |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| [x] | T-001 | Create the Order and Shipment entities with their relationship | ordering_app | - | no | std | build | 1,2 | done | pass | G1 | static-entities | P1.01 |
| [x] | T-002 | Seed 40 Order rows with relative timestamps | ordering_app | T-001 | no | std | seed | 5 | done | pass | G0 | - | P1.02 |
| [ ] | T-003 | Bind the order list screen to GetOrders | ordering_app | T-002 | yes | std | build | 1,3,6 | active | - | - | aggregates-and-repeaters | P2.01 |
| [ ] | T-004 | Prove the order list renders all 40 rows, not one | ordering_app | T-003 | no | std | verify | 6,7 | todo | - | - | aggregates-and-repeaters | P2.01 |
| [ ] | T-005 | Add the shipment detail overlay | ordering_app | T-003 | yes | std | build | 1,6 | todo | - | - | overlays-wizards-charts | P2.02 |
| [ ] | T-006 | Upload the brand icon set | ordering_app | - | no | std | manual | - | parked | - | - | icons-and-theming | P2.03 |
| [ ] | T-007 | Write the External Logic library that signs shipment labels | ordering_app | - | no | std | code | - | todo | - | - | - | P2.04 |
| [ ] | T-008 | Deploy the carrier stub service and write its contract file | carrier-stub | - | no | high | external | - | todo | - | - | - | P2.04 |
| [ ] | T-009 | Call the shipment label action from the label screen | ordering_app | T-007 | no | high | build | 1,3,6 | blocked | - | - | - | P2.05 |
| [ ] | T-010 | Join: a label prints end to end against the carrier stub | solution | T-008,T-009 | no | std | verify | 4,6,7 | todo | - | - | - | P2.06 |
| [ ] | T-011 | Final G2 blind pass | solution | T-004,T-005,T-006,T-010 | no | std | verify | 6,7 | todo | - | - | - | P2.07 |

## Column values

- `Done` - `[ ]` or `[x]`. Terminal state only.
- `ID` - `T-<NNN>`. Assigned once, never reused, even after a row is removed.
- `App` - the app identifier. This is the lane and the lease key. One declared
  producer and consumer pair: `<producer>+<consumer>`, one lease per identifier.
  `solution` is a literal for gate rows: no lane, no lease.
- `DependsOn` - comma-separated task IDs, or `-`. Only true data dependencies. Done
  means `Status: done` and `Verdict: pass`; an id with no row reads as done.
- `Batchable` - `yes` | `no`.
- `Risk` - `std` | `high`. High: auth, data model change on populated data,
  integrations, money or PII, anything touching a prior verified feature.
- `Turn` - `build` | `fix` | `inspect` | `publish` | `seed` (Mentor work; lease) |
  `verify` | `manual` | `code` | `infra` | `external` (no Mentor turn; no lease). A
  `verify` row runs its rungs at every rigor, and exists only for joins, G2 and owed G3.
- `Verify` - proof rungs from `../../fulcrum-verification/SKILL.md`, heading "The proof
  ladder". `-` is legal only for `inspect`, `manual`, `code`, `infra` and `external`.
  Rung 1 is a Mentor read-back, so it never sits on a `verify` row.
- `Status` - `todo` | `active` | `blocked` | `done` | `parked`.
- `Verdict` - `-` | `pass` | `fail` | `unproven`. A `done` row always carries one.
  `pass`: all gates owed so far ran and passed, so a `demo` row at `G0` is `pass`.
  `unproven`: an owed gate did not run or returned `untested`; the row stays `todo`.
- `Gate` - `-` | `G0` | `G1` | `G2` | `G3`: the highest gate actually run. A row is
  never recorded above the gate it ran.
- `Traps` - reference file stems from `../../fulcrum-engine-traps/references/`, or `-`.
  Never incident text.
- `Step` - the `plan.md` step id.

Escape any literal pipe inside a cell as `\|`. No newlines inside a cell. No free text in
`Status`, `Verdict`, `Gate`, `Batchable`, `Risk` or `Turn`: a cell that needs prose means the prose belongs in the
session file. Only the orchestrator rewrites this file - `../references/file-schemas.md`,
heading "Write ownership - who writes which file".

## Blocked and parked rows

| ID | Blocked on | Unblocks when |
|---|---|---|
| T-006 | the user | The icon set is uploaded to the tenant |
| T-009 | T-007, label action | Element shows in `context_actions` |

This table is the home for everything waiting on the user. Keep it current; do not keep
a separate waiting-on-user list anywhere else. A row waiting only on another row is
`todo` with that id in `DependsOn`, not `blocked`. A library consumer is `blocked` from init.
