# Template — `.fulcrum/project.md`

Copy to `<project>/.fulcrum/project.md`. Rewritten in place when a setting changes.
Identity and settings only: no history, no task state, no tenant facts.
Schema: `../references/file-schemas.md`, heading "project.md".

---

<!-- fulcrum-schema: project v1 -->

# Project — \<solution name\>

**Created:** \<ISO-8601 UTC\>
**State directory:** `.fulcrum/` — committed. `lease.*.json` and `checkpoints/` are not.

## Apps

| App identifier | Asset type | Role in the solution | Target environment |
|---|---|---|---|
| \<identifier, never the display name\> | \<web app / mobile app / library / agent / workflow\> | \<one line\> | \<env\> |

Do not re-derive these. Confusably named apps on the tenant are listed in
`HANDOFF.md` PART 1 under "Target".

## Settings

| Setting | Value |
|---|---|
| `mode` | `guided` \| `expert` |
| `posture` | `collaborative` \| `directive` |

`collaborative` is the default. Definitions, the orthogonality rule, the failure
mechanism and the opt-in rule: `../../../CONVENTIONS.md`, heading "Mode and posture".

## Tier overrides

\<Delete this whole section if there is no override. An empty section reads as a
decision and pins nothing.\>

| Tier | Model |
|---|---|
| `deep-reasoning` | \<model\> |
| `workhorse` | \<model\> |
| `poller` | \<model\> |

A project override is rank 1 in `../../../MODEL-TIERS.md`, heading "Resolution — how a
tier becomes a concrete model", so anything written here wins over the machine-local
file. Record why, in `DECISIONS.md`.

## Tenant facts

Every tenant-varying fact is in `.fulcrum/tenant-profile.md`, written by
`../../fulcrum-solution-init/SKILL.md`. Read it there. Never copy a row out of it —
the copy and the original drift, and the copy wins by being read first.

## Scope of this directory

`.fulcrum/` is terminal. Nothing here syncs to an issue tracker, in either direction.
