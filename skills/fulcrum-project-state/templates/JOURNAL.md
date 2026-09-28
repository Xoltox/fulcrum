# Template — `.fulcrum/JOURNAL.md` (the session index)

Copy to `<project>/.fulcrum/JOURNAL.md`. **One row per session, never per action.**
The per-action lines live in `<project>/.fulcrum/journal/<session-id>.md` — skeleton in
`journal-session.md` beside this file.

A row is **appended at session start and completed in place**. Edit only your own row.
Never append a second row to close a session: one row per session is what makes the
`Tasks` column scannable for oscillation detection.

Schema: `../references/file-schemas.md`, heading "JOURNAL.md — the session index".

---

<!-- fulcrum-schema: JOURNAL v2 -->

# JOURNAL — \<solution name\>

Session index. Detail for any row: `journal/<Session>.md`.

| Session | Start | End | State | Tasks | InFlight | Lines | Note |
|---|---|---|---|---|---|---|---|
| `s-4c1e90` | 2026-09-28T09:12:04Z | 2026-09-28T09:44:20Z | clean | T-001:pass,T-002:pass | — | 18 | — |
| `s-7b22af` | 2026-09-28T13:02:55Z | 2026-09-28T15:31:44Z | clean | T-003:fail | — | 31 | repeater rendered 1 row |
| `s-9d41c7` | 2026-09-29T08:05:12Z | 2026-09-29T09:50:03Z | clean | T-003:fail,T-004:pass | — | 26 | second T-003 failure — loop engine must stop |
| `s-a0f3b2` | 2026-09-29T10:14:38Z | — | halted | T-003:— | — | 4 | stuck twice on T-003, see HALT.md |
| `s-b17e45` | 2026-09-30T09:00:01Z | — | open | T-006:pass | T-007 | 12 | — |

## Reading this file

- **Resume** — read the last row. `State`/`End` say whether it closed; `InFlight` names
  tasks that may have mutated the app with no recorded outcome.
- **Oscillation** — match a task id across the `Tasks` column. Two `:fail` entries for
  one task is "stuck twice means stop and report" (`../../../AGENTS.md`) firing
  mechanically. The example above shows exactly that, and the halt that followed.
- **`State: open`** — live session or crashed session; the file cannot tell. Resolve
  against the lease, per `../references/file-schemas.md`, heading "Reading a row that
  was never closed". Never guess.

## Values

`State`: `open` · `clean` · `halted` · `aborted`
`Tasks`: `<task-id>:<pass|fail|unproven|—>`, comma-separated, written as each task
reaches a terminal state — **not** at session close, so a crashed attempt still shows.
`—` means "not applicable or not yet known". Never leave a cell empty.
