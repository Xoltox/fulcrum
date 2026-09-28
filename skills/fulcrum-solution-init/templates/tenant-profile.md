# Tenant profile

Written once by `fulcrum-solution-init` step 3. **Every downstream skill reads this file
instead of hardcoding a tenant fact.**

Probe procedure and the rules for each row:
`../references/tenant-capability-probe.md`.

Every row carries five fields. A row missing any field is **not resolved** — mark it
`UNRESOLVED` and say which planned step it gates. An answer of "Mentor said X" is not an
answer.

**Probed:** \<date\>
**Backend identifier:** \<value from row 7\>
**Probed by:** \<session / agent\>

---

## 0. Mentor liveness gate

| Field | Value |
|---|---|
| Fact | Does Mentor actually read the target app? |
| Answer | \<PASS / FAIL\> |
| Probe | Read-only prompt against \<app\> asking Mentor to name visible screens/entities |
| Observed | \<quote the returned summary\> |
| Date | \<date\> |

Pass requires the summary to **name real content from the actual app**. A read-only prompt
correctly returns `attempted_change` false, so that field is not the signal.

On FAIL: **halt.** Re-gate at the start of every session regardless of this row.

---

## 1. Live row data — not a tenant fact

No row here. There is no model-layer path to live row data on any tenant, so nothing
varies and nothing is probed. `[SCHEMA]` Do not re-add a `db_query` row.

Consequence to carry into the plan: row verification needs a separate diagnostic
instrument — historically a temporary diagnostic endpoint at roughly two Mentor turns and
two revisions per seed step. Budget accordingly. The instrument for live row data is
`exec_in_app` against a harness fork `[SCHEMA]`; the procedure lives in
`fulcrum-verification`, not here.

---

## 2. UI blocks

Probed by **attempting to reference the block**, never by asking whether it exists.

| Block | Exists | Input properties observed (verbatim) | Probe / Observed | Date |
|---|---|---|---|---|
| Modal | \<yes/no/unresolved\> | \<…\> | \<…\> | \<…\> |
| BottomSheet | | | | |
| ActionSheet | | | | |
| Sidebar | | | | |
| Accordion | | | | |
| Wizard | | | | |
| \<other block a phase-one spec needs\> | | | | |

A Mentor denial with no attempted reference is **unresolved**, not "no".

---

## 3. Icon font

| Field | Value |
|---|---|
| Font family | \<name\> |
| Name casing convention | \<e.g. PascalCase / kebab-case\> |
| Confirmed working example | \<exact string that rendered\> |
| Probe / Observed | \<…\> |
| Date | \<date\> |

A wrongly cased icon name renders blank or falls back with **no error**. Specs must quote
names in the confirmed convention.

---

## 4. `ModelFeature_*` flags

| Field | Value |
|---|---|
| Flags available | \<list, verbatim\> |
| Flags absent that a spec assumed | \<list, or None\> |
| Probe / Observed | \<…\> |
| Date | \<date\> |

An absent flag means re-specify, not retry.

---

## 5. Date / meridiem format tokens

| Token | Input | Output observed | Verdict |
|---|---|---|---|
| \<token\> | \<known date/time\> | \<verbatim output string\> | \<as expected / empty / literal\> |

Specs quote the confirmed tokens. No build agent guesses a format token.

---

## 6. Public server actions

| Field | Value |
|---|---|
| Fact | Can a server action be marked public? |
| Answer | \<yes / no\> |
| Probe | Attempt to mark a trivial server action public |
| Observed | \<took / error text verbatim\> |
| Date | \<date\> |

If no: exposing logic outside the app needs a REST method. That is a planned step and a
budget line, notably for seeding and diagnostic row reads.

---

## 7. Mentor backend identifier

| Field | Value |
|---|---|
| Identifier | \<value\> |
| Probe / Observed | \<…\> |
| Date | \<date\> |

Without this, this profile cannot be compared against a later one and a regression cannot
be attributed.

---

## 8. Mentor prompt-length ceiling

| Field | Value |
|---|---|
| Ceiling | \<value\> |
| How established | \<documented / reported / bounded escalation on a throwaway read-only turn\> |
| Observed | \<…\> |
| Date | \<date\> |

An unknown ceiling means every long spec risks truncation, whose failure mode is a
**partial build reported as success**.

---

## 9. Target app identity

| Field | Value |
|---|---|
| App identifier (exact) | \<value — never the display name\> |
| Application type | \<value\> |
| Revision at init | \<value\> |
| Can Mentor add screens to this application type? | \<observed answer\> |
| Confusable apps on the tenant — NOT the target | \<list, or None\> |
| Date | \<date\> |

---

## 10. Tool availability

Three states only — never a plain yes/no. Full rules:
`../references/tool-availability-and-fallback.md` and
`../references/tenant-capability-probe.md`, heading "Tool availability — three
states, not two". `Unknown` is correct and expected for a mutating op that a
read-only probe never called — do not upgrade it to "available".

| Op | State (callable / unavailable / unknown) | Evidence (result or exact error text) | Fallback if unavailable | Date |
|---|---|---|---|---|
| \<op name\> | \<…\> | \<…\> | \<see tool-availability-and-fallback.md, or "none — halt"\> | \<…\> |

---

## Unresolved rows

| Row | What blocked it | Which planned step it gates |
|---|---|---|
| \<…\> | \<…\> | \<…\> |
