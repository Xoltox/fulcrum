# HANDOFF template

Copy to `<project>/HANDOFF.md`. Two parts, with different lifecycles.

**PART 1 — RULES** is stable and accumulates slowly. **PART 2 — BRIEF** is replaced
wholesale every session. Never append session narrative to either; that is what
`BUILD-LOG.md` is for.

Rationale and the failures this shape prevents: `../references/repo-scaffold.md`,
heading "The handoff document — two parts, one replaced".

---

# HANDOFF — \<solution name\>

Two parts. **PART 1 RULES** — stable, rarely changes. **PART 2 BRIEF** — replaced
wholesale each handoff; read this every resume. Append-only history:
`BUILD-LOG.md` plus `buildpatterns/step-<NN>-*.md`.

---

# PART 1 — RULES

## What this is

\<One paragraph: what is being built, into what, for whom. No history.\>

## File map

| File | Role |
|---|---|
| `DOMAIN.md` | Domain source of truth |
| `PLAN.md` | Phases, steps, decomposition, entity owners |
| `tenant-profile.md` | Every tenant-varying fact, with evidence |
| `specs/step-<NN>-*.md` | Self-sufficient spec per step |
| `BUILD-LOG.md` | Append-only history — read for "what happened" |
| `buildpatterns/step-<NN>-*.md` | Per-step reliability log |
| `RUN-IDS.md` | Durable run-id log |
| \<proof harness path\> | Proof harness — trust a live run over any prose |

## Target

| Field | Value |
|---|---|
| App identifier | \<exact identifier, never the display name\> |
| Application type | \<value\> |
| Not the target | \<any confusably named app on the tenant\> |

Do not re-scan these. They are resolved in `tenant-profile.md`.

## Session start sequence

1. Re-run the **Mentor liveness gate** (`tenant-profile.md`, row 0). On fail, halt.
2. Read PART 2 — BRIEF. It names exactly one next step.
3. Read that step's spec. Read nothing else.
4. Record the run id in `RUN-IDS.md` before polling it.

## Standing decisions — do not re-litigate

| Topic | Decision |
|---|---|
| \<topic\> | \<decision\> |

New standing decisions land **here, once**. Never in a second file, never at a second
strength. Everywhere else links here.

## Policies stated elsewhere — do not restate

| Policy | Single source |
|---|---|
| Model tier per phase | \<relative path\> |
| Stop conditions and fix-turn caps | \<relative path\> |
| Polling cadence and run-id durability | \<relative path\> |
| Proof obligations | \<relative path\> |

Link, never copy. A second copy at a different strength is the documentation failure this
table exists to prevent.

## Escalation

\<When to halt and report rather than continue. One line per condition.\>

---

# PART 2 — BRIEF

**Replaced wholesale each handoff. Everything below is current state only.**

**Session:** \<date\>
**Phase:** \<n\> — \<name\>
**Last completed step:** \<NN\> — \<title\>. Landed at revision \<r\>.

## The one next step

**Step \<NN\> — \<title\>**
**Spec:** `specs/step-<NN>-<slug>.md`

\<Two or three lines: what it produces and why it is next. Nothing else.\>

## What that step needs before it can start

- \<Precondition, e.g. a confirmed manual asset upload, a seeded table, a resolved
  question. Empty is fine — write "Nothing".\>

## Known-open items that do NOT block this step

- \<item\> — \<which step it gates instead\>

## Do not do

- \<Anything specifically off-limits this session.\>

---

**Nothing in PART 2 survives the next handoff.** Anything that must persist belongs in
PART 1, `PLAN.md`, or `BUILD-LOG.md`.
