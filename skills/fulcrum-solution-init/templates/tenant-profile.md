# Tenant profile

Written by `fulcrum-solution-init` step 3, a read-only, free pass. **Every downstream
skill reads this file instead of hardcoding a tenant fact.**

Probe procedure and the rules for each row:
`../references/tenant-capability-probe.md`.

Every row carries five fields. A fact no free read answers is marked `first-row` with the
planned row that will answer it; the orchestrator fills the row when that row lands.
Any other row missing a field is **not resolved** - mark it `UNRESOLVED` and say which
planned step it gates. An answer of "Mentor said X" is not an answer.

**Probed:** \<date\>
**Backend identifier:** \<value from row 7\>
**Probed by:** \<session / agent\>

---

## 0. Mentor liveness gate

| Field | Value |
|---|---|
| Fact | Does Mentor actually read the target app? |
| Answer | \<PASS / FAIL / deferred: Mentor creates the app, first guard runs it\> |
| Probe | Read-only prompt against \<app\> asking Mentor to name visible screens/entities |
| Observed | \<quote the returned summary\> |
| Date | \<date\> |

Pass requires the summary to **name real content from the actual app**. A read-only prompt
correctly returns `attempted_change` false, so that field is not the signal.

On FAIL: **halt.** This row does not replace the per-dispatch guard: gate 5 of the loop (the staleness guard at the start of every Mentor dispatch with an attached asset) re-checks liveness on each dispatch regardless of this row.

---

## 1. Live row data and optional MCP tools

There is no model-layer path to live row data on any tenant, so there is no row-data probe
and no `db_query` row. What does vary, by tenant or server version, is which optional
tools list. Record what this tenant's tool listing shows (names only, read-only); never
assume from another tenant or an older snapshot.

| Tool | Listed on this tenant | Observed (listing source) | Date |
|---|---|---|---|
| `db_query` | \<yes/no\> | \<...\> | \<...\> |
| `exec_in_app` | | | |
| `test_setup_start` / `test_setup_status` | | | |
| `mentor_publish` | | | |

All four were absent on the 2026-10-16 listing (listed 2026-10-09); current record:
`../../fulcrum-mentor-turns/references/mcp-surface.md`. A tool that lists is still not an
instrument until that file records what a call does.

Consequence to carry into the plan: row verification needs a separate diagnostic
instrument - a temporary diagnostic REST endpoint probed over HTTP, at roughly two Mentor
turns and two revisions per seed step. Budget accordingly. The procedure lives in
`fulcrum-verification` (`references/diagnostic-endpoint.md`), not here.

---

## 2. UI blocks

Filled from published-state reads, or by **the first real row that references the
block**, never by asking whether it exists and never by a throwaway build.

| Block | Exists | Input properties observed (verbatim) | Probe / Observed | Date |
|---|---|---|---|---|
| Modal | \<yes/no/first-row/unresolved\> | \<...\> | \<...\> | \<...\> |
| BottomSheet | | | | |
| ActionSheet | | | | |
| Sidebar | | | | |
| Accordion | | | | |
| Wizard | | | | |
| \<other block a spec up to the first join needs\> | | | | |

A Mentor denial with no attempted reference is **unresolved**, not "no".

### OutSystems UI version

| Field | Value |
|---|---|
| Version | \<tag, or `first-row`: read on the app's first render\> |
| Probe | \<which read answered\> |
| Observed | \<verbatim\> |
| Date | \<date\> |

Reads, in order, and what each answer does to the vendored block and theme rows:
`../../fulcrum-design-loop/references/block-map.md`, heading "OutSystems UI library
reference". A runtime read wins over Mentor's answer.

---

## 3. Icon font

| Field | Value |
|---|---|
| Font family | \<name\> |
| Name casing convention | \<e.g. PascalCase / kebab-case\> |
| Confirmed working example | \<exact string that rendered\> |
| Probe / Observed | \<...\> |
| Date | \<date\> |

A wrongly cased icon name renders blank or falls back with **no error**. Specs must quote
names in the confirmed convention.

---

## 4. `ModelFeature_*` flags

| Field | Value |
|---|---|
| Flags available | \<list, verbatim\> |
| Flags absent that a spec assumed | \<list, or None\> |
| Probe / Observed | \<...\> |
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
| Answer | \<yes / no / first-row\> |
| Probe | Public action visible in `context_actions`, or the first real row that marks one public |
| Observed | \<listed / took / error text verbatim\> |
| Date | \<date\> |

If no: exposing logic outside the app needs a REST method. That is a planned step and a
budget line, notably for seeding and diagnostic row reads.

---

## 7. Mentor backend identifier

| Field | Value |
|---|---|
| Identifier | \<value\> |
| Probe / Observed | \<...\> |
| Date | \<date\> |

Without this, this profile cannot be compared against a later one and a regression cannot
be attributed.

---

## 8. Mentor prompt-length ceiling

| Field | Value |
|---|---|
| Ceiling | \<value / first-row\> |
| How established | \<documented / reported / observed on a real row\> |
| Observed | \<...\> |
| Date | \<date\> |

An unknown ceiling means a long spec risks truncation, whose failure mode is a **partial
build reported as success**.

---

## 9. Target app identity

| Field | Value |
|---|---|
| App identifier (exact) | \<value - never the display name\> |
| Application type | \<value\> |
| Revision at init | \<value\> |
| Can Mentor add screens to this application type? | \<observed answer / first-row\> |
| Confusable apps on the tenant - NOT the target | \<list, or None\> |
| Generated sample sign-in picker present (Login screen "Log in as ..." buttons, `GetSampleUserVerificationCode`) | \<yes / no / unknown - per app, from published-state reads\> |
| Sample-persona use approved by the user | \<yes / no / not asked - DECISIONS.md entry id\> |
| Date | \<date\> |

---

## 10. Tool availability

Three states only - never a plain yes/no. Full rules:
`../references/tool-availability-and-fallback.md` and
`../references/tenant-capability-probe.md`, heading "10. Tool availability - three
states, not two". `Unknown` is correct and expected for a mutating op that a
read-only probe never called - do not upgrade it to "available".

| Op | State (callable / unavailable / unknown) | Evidence (result or exact error text) | Fallback if unavailable | Date |
|---|---|---|---|---|
| \<op name\> | \<...\> | \<...\> | \<see tool-availability-and-fallback.md, or "none - halt"\> | \<...\> |
| browser-automation (delegable role) | per project - see each project's `project.md` field `browser` | - | \<rungs 6-7 `untested`; user renders\> | - |

---

## 11. Environments, template screen set

Source: `env_list` (read-only). Lookup rule for this file: project `.fulcrum/` first, then
nearest parent directory; write a new one in `.fulcrum/` only if none is found.

| Field | Value |
|---|---|
| Environment keys | \<name = key, one per line\> |
| New-app template screen set | \<screens present in a fresh app from the standard template, observed / first-row\> |
| Probe / Observed | \<...\> |
| Date | \<date\> |

---

## Unresolved rows

| Row | What blocked it | Which planned step it gates |
|---|---|---|
| \<...\> | \<...\> | \<...\> |
