# Template - `.fulcrum/design/report.md`

Written by the orchestrator once every screen row is terminal. The user reads this
first. State what is untested before what passed when the render tier is C.

---

<!-- fulcrum-schema: design-report v1 -->

# Design loop report - \<app name\>

- **App:** [Open \<app name\>](\<runtime URL from env_app\>) - Development
- **Revision:** \<live revision\>   **Date:** \<ISO-8601 UTC\>
- **Bar:** \<structural | visual\>   **Tier:** \<A | B | C\>

## Untested

\<Rungs and screens not proven, with the reason. In tier C, the render-only defect
classes first: repeater collapse, collapsed overlay, dark-on-dark icon, empty chart,
wrapped metric.\>

## Per-screen fidelity

| SID | Name | Verdict | Rounds | Fix turns | Last fidelity file |
|---|---|---|---|---|---|
| S01 | \<name\> | \<pass / fail / unproven\> | \<n\> | \<n\> | `fidelity/S01-r<n>.md` |

## Backlog

\<Minor diffs left at the bar, from `backlog.md`; `-` if none.\>

## Open risks and decisions

\<Gate second-FAILs, unresolved blocks, assets pending upload, security observations
from render-check; D-ids.\>

## Turns and time

\<Turns per screen, compare rounds, wall clock.\>

## Next

Promotion beyond Development is not done by this loop. Offer: \<promote with the
user's go | leave in Development\>.
