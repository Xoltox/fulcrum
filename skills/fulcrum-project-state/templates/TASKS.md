# Template — `.fulcrum/TASKS.md`

Copy to `<project>/.fulcrum/TASKS.md`. Rewritten in place — this file is current
truth, not history. Column order is the parse contract: never reorder, never rename,
never add a column without updating `../references/file-schemas.md`, heading
"TASKS.md".

Every row is Mentor-turn-shaped. A row that cannot fill `App`, `Turn` and `Verify` is
not a task yet — it is a plan item, and it belongs in `plan.md` until decomposed.

---

<!-- fulcrum-schema: TASKS v1 -->

# TASKS — \<solution name\>

Current phase: \<P2 — name\>. Closed rows are removed at each phase boundary; their
history is in `journal/` and `RUN-IDS.md`.

| Done | ID | Task | App | Turn | Verify | Status | Verdict | Traps | Step |
|---|---|---|---|---|---|---|---|---|---|
| [x] | T-001 | Create the Order and Shipment entities with their relationship | ordering_app | build | 1,2 | done | pass | static-entities | P1.01 |
| [x] | T-002 | Seed 40 Order rows with relative timestamps | ordering_app | seed | 5 | done | pass | — | P1.02 |
| [ ] | T-003 | Bind the order list screen to GetOrders | ordering_app | build | 1,3,6 | active | — | aggregates-and-repeaters | P2.01 |
| [ ] | T-004 | Prove the order list renders all 40 rows, not one | ordering_app | verify | 6,7 | todo | — | aggregates-and-repeaters | P2.01 |
| [ ] | T-005 | Add the shipment detail overlay | ordering_app | build | 1,6 | blocked | — | overlays-wizards-charts | P2.02 |
| [ ] | T-006 | Upload the brand icon set | ordering_app | manual | — | parked | — | icons-and-theming | P2.03 |

## Column values

- `Done` — `[ ]` or `[x]`. Terminal state only.
- `ID` — `T-<NNN>`. Assigned once, never reused, even after a row is removed.
- `App` — the app identifier. This is the lease key.
- `Turn` — `build` | `fix` | `inspect` | `publish` | `seed` | `verify` | `manual`.
- `Verify` — proof rungs from `../../fulcrum-verification/SKILL.md`, heading "The proof
  ladder". `—` is legal only for `inspect` and `manual`.
- `Status` — `todo` | `active` | `blocked` | `done` | `parked`.
- `Verdict` — `—` | `pass` | `fail` | `unproven`. A `done` row always carries one.
- `Traps` — reference file stems from `../../fulcrum-engine-traps/references/`, or `—`.
- `Step` — the `plan.md` step id.

Escape any literal pipe inside a cell as `\|`. No newlines inside a cell.

## Blocked and parked rows

| ID | Blocked on | Unblocks when |
|---|---|---|
| T-005 | T-003 | The list screen exists to open the overlay from |
| T-006 | The user | The icon set is uploaded to the tenant |
