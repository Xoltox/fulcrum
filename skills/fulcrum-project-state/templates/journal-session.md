# Template — `.fulcrum/journal/<session-id>.md`

Copy to `<project>/.fulcrum/journal/<session-id>.md`, named for the session id minted at
session start. **Append-only.** Never edit a line, never delete one, never insert into
the middle. Correct a wrong line by appending a later line with the action `withdraw`.

Written by exactly one session, so it never merge-conflicts. The append discipline is
what keeps a crashed file readable and correctly ordered.

Create this file **before** appending the session's row to `../JOURNAL.md`, and both
before the first dispatch. Schema: `../references/file-schemas.md`, heading
`journal/<session-id>.md`.

---

<!-- fulcrum-schema: journal-session v1 -->

# Session `s-7b22af` — \<solution name\>

One line per event:

```
<timestamp UTC> | <session-id> | <task-id or —> | <run-id or —> | <action> | <outcome>
```

The `started` line is written **before** the wait. The outcome line is written after.
A `started` with no outcome is the signal that work may still be in flight, and it is
what the index row's `InFlight` column mirrors.

The `session-id` repeats the filename on purpose — a self-describing line survives the
file being moved, quoted, handed to a subagent as a fragment, or concatenated by the
index rotation rule.

```
2026-09-28T13:02:55Z | s-7b22af | —     | —        | open session | ok
2026-09-28T13:03:10Z | s-7b22af | T-003 | —        | acquire lease | ok: ordering_app
2026-09-28T13:05:02Z | s-7b22af | T-003 | r-8f21c4 | dispatch build turn | started
2026-09-28T13:06:32Z | s-7b22af | T-003 | r-8f21c4 | poll | running
2026-09-28T13:08:05Z | s-7b22af | T-003 | r-8f21c4 | dispatch build turn | ok: model updated
2026-09-28T13:09:40Z | s-7b22af | T-003 | r-9a03de | publish | started
2026-09-28T13:13:10Z | s-7b22af | T-003 | r-9a03de | publish | ok: revision 42
2026-09-28T13:21:18Z | s-7b22af | T-003 | —        | verify rung 6 | failed: repeater renders 1 row
2026-09-28T13:21:44Z | s-7b22af | T-003 | —        | withdraw | 13:08:05 "model updated" was Mentor's claim, not verified
2026-09-28T15:30:02Z | s-7b22af | T-003 | —        | release lease | ok
2026-09-28T15:31:44Z | s-7b22af | —     | —        | close session | clean
```

## Actions in use

`open session` · `close session` · `acquire lease` · `refresh lease` ·
`break expired lease` · `release lease` · `dispatch <turn type> turn` · `poll` ·
`publish` · `verify rung <n>` · `recover` · `withdraw` · `halt` · `resolve halt`

Extend the list as needed; keep each action a short verb phrase and reuse an existing
one before inventing a synonym. Two words for one event makes the file unsearchable.
