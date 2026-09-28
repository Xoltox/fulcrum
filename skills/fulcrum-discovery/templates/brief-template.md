# Template — derived brief

Copy to `<project>/.fulcrum/brief.md`. This is the source material
`../../fulcrum-solution-init/SKILL.md` ingests at step 1.

**The section set is not negotiable.** It matches what
`../../fulcrum-solution-init/references/source-triage.md`, heading "Deriving the brief
when none was supplied", requires a brief to contain, so ingestion needs no translation.
Delete no section — an empty section is information. Write "None" or "Not applicable".

Every requirement line carries `Confidence`: `held` | `elicited` | `assumed` |
`undecided`. Definitions: `../SKILL.md`, step 5. This is a separate namespace from the
`[VERIFIED]`/`[UNVERIFIED]` evidence tags in `../../../CONVENTIONS.md` — do not mix
them in one line.

No line may be unfalsifiable. If it states no observable outcome, it belongs in **Open
questions** as `undecided`, not in a requirement table. See
`../references/observable-requirements.md`.

---

<!-- fulcrum-origin: discovery-interview -->

# Brief — \<solution name\>

**Derived by:** discovery interview, \<ISO-8601 UTC\>
**Source material:** \<what existed before the interview, by path — or "none; interview only"\>
**Batches run:** \<n\> of 3 · **Questions asked:** \<n\> of 15
**Stopped because:** \<readiness set satisfied / ceiling reached / early-stop signal, named\>

## 1. What this is, and who uses it

\<Two or three sentences. The persona and its scope, stated explicitly. A wrong persona
mis-shapes every entity, so state it even when it feels obvious.\>

- **Primary persona:** \<…\> · Confidence: \<…\>
- **Scope boundary — what this is NOT for:** \<…\> · Confidence: \<…\>

## 2. Roles and personas

One row per role. Evidence is where it came from: a user statement, an existing
document, or an interviewer assumption the user accepted.

| Role | What they do | Evidence | Confidence |
|---|---|---|---|
| \<Manager\> | \<…\> | \<"user stated, batch 1 Q2"\> | held |

\<If only one role appeared, say so explicitly and say you are assuming single-role —
do not let the absence read as a decision.\>

**Prohibitions** — what a role must NOT be able to do. Users rarely volunteer these:

- \<Role\> must not \<observable action\> on \<named screen or entity\> · Confidence: \<…\>

## 3. Core entities

| Entity | Key attributes | Relationships | Fixed value sets | Confidence |
|---|---|---|---|---|
| `Order` | \<…\> | one `Customer`, many `Shipment` | `OrderStatus`: \<enumerate\> | held |

- **Ambiguities noted:** \<anything the user was unsure of, and what it affects\>
- **Two references to the same entity:** \<e.g. `Order` names both a requester and an
  approver, both `Customer` — or "none identified"\>

Relationships are stated in domain terms only. Do not name aggregates, actions or
variables — `../../fulcrum-solution-init/templates/spec-template.md`, DATA FLOW.

## 4. Screen and flow inventory

Grouped by area. One line per screen, each with its access rule and its mode.

### \<Area\>

| Screen | Purpose | Roles — read | Roles — write | Mode | Empty state | Confidence |
|---|---|---|---|---|---|---|
| `OrderList` | \<…\> | Manager, Agent | — | read-only | \<what shows with no rows\> | held |
| `ShipmentDetail` | \<…\> | Manager | Manager | transactional | \<…\> | elicited |

**Mode** is `read-only` or `transactional`, per screen, always stated. A missing mode is
read as static by the build agent
(`../../fulcrum-solution-init/templates/spec-template.md`, FUNCTIONAL BEHAVIOR) and
selects the wrong proof rung (`../../fulcrum-verification/SKILL.md`, proof ladder).

**Source traceability:** \<per group, the source filenames this came from — or "interview
only, no source artifact"\>

## 5. Target platform

| Decision | Value | Confidence |
|---|---|---|
| Web or mobile | \<…\> | \<…\> |
| Phone-width or desktop layout | \<…\> | \<…\> |

**Consequence, stated:** reversing this means re-creating the app and rebuilding every
screen. Confirmed against `../../fulcrum-solution-init/SKILL.md`, step 2 — which owns
the final decision; this section records what the user wants, not the verdict.

## 6. Integrations

| System | Direction | Data | Timing | System of record? | Confidence |
|---|---|---|---|---|---|
| \<…\> | in / out / both | \<…\> | while the user waits / scheduled | yes / no | \<…\> |

## 7. Data needed to demonstrate this

What must exist before a screen can be shown working. Seeding precedes any screen that
reads it (`../../fulcrum-seed-data/SKILL.md`).

| Entity | Rows | Spread / states to cover | Real values available? | Confidence |
|---|---|---|---|---|
| `Order` | \<n\> | \<…\> | invented | elicited |

## 8. Acceptance — one observable statement per screen

Each states something someone can see, read or count. **No item may say "looks right",
"renders correctly" or "works as expected"** — those always pass.

| Screen | Observable statement | Confidence |
|---|---|---|
| `OrderList` | \<"shows one row per Order, newest first, with customer name and status"\> | held |

## 9. Smallest slice worth demonstrating

\<One paragraph. Which part, standing alone, is worth showing someone. Do not name
phases or steps — sizing is `fulcrum-solution-init`'s.\>

## 10. Assets

| Asset | Exists? | Source | Who uploads | Confidence |
|---|---|---|---|---|
| Logo | \<…\> | \<path or "must be produced"\> | \<named person\> | \<…\> |

Uploads are a human handoff — there is no asset-upload path over the ODC MCP surface
(`../../fulcrum-solution-init/references/source-triage.md`, heading "Assets are a human
handoff — plan for it"). An asset with no named owner is an unowned blocker.

## 11. Corrections to what was assumed going in

Written as corrections, next to the claim each overturns — never as quiet replacements.
An unrecorded correction gets re-litigated by a later session.

- **Was assumed:** \<…\> → **Corrected:** \<…\> \<one-line reason\>

## 12. Open questions

### Blocking — these gate the plan

| # | Question | Who decides | What it blocks |
|---|---|---|---|
| 1 | \<…\> | \<…\> | \<readiness item or step\> |

### Non-blocking — resolve at the step that needs them

| # | Question | Who decides | What it blocks |
|---|---|---|---|

An item here is `undecided`. It is never a requirement and must never be scored against
the app — `../../fulcrum-gap-analysis/references/finding-classes.md`.

## 13. Decisions recorded

Interview decisions live in `.fulcrum/DECISIONS.md`, not here. List the record IDs only:

- `D-001`, `D-002`, \<…\>

---

## Confidence summary

| Value | Count |
|---|---|
| held | \<n\> |
| elicited | \<n\> |
| assumed | \<n\> |
| undecided | \<n\> |

A brief that is mostly `assumed` was not an interview. Say so in the handoff rather
than letting the count speak only to whoever reads the table.
