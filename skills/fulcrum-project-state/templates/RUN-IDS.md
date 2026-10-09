# Template - `.fulcrum/RUN-IDS.md`

Copy to `<project>/.fulcrum/RUN-IDS.md`. **Append-only**, whole lines at the end of the
file. Written by whoever issued the run. Exists and is empty rather than absent before
the first run. Line format, field meanings and the publish slot:
`../references/file-schemas.md`, heading "RUN-IDS.md".

Append the `started` line the instant a start call returns its id - before the first
poll, and before anything else. Append each later state as a new line repeating the
run id; never edit a line.

---

<!-- fulcrum-schema: RUN-IDS v1 -->

# RUN-IDS - \<solution name\>

```
<timestamp> | <session-id> | <task-id> | <app> | <op> | <run-id> | <publication-key> | <revision> | <outcome>
2026-10-08T10:41:07Z | s-4c1e9a | T-001 | claims_web | create-asset | 9b02d7f1 | - | - | started
2026-10-08T10:41:30Z | s-4c1e9a | T-001 | claims_web | create-asset | 9b02d7f1 | - | - | ok: applicationKey 5e7c...
2026-10-08T10:52:12Z | s-4c1e9a | T-002 | claims_web | prompt | 71aa03c2 | - | - | started
2026-10-08T10:55:48Z | s-4c1e9a | T-002 | claims_web | prompt | 71aa03c2 | - | - | succeeded
2026-10-08T11:02:10Z | s-4c1e9a | T-006 | claims_web | publish | 3ec0aa82 | - | - | started
2026-10-08T11:02:41Z | s-4c1e9a | T-006 | claims_web | publish | 3ec0aa82 | 4252ee9c | 5 | accepted
2026-10-08T11:03:05Z | s-4c1e9a | T-006 | claims_web | publish | 3ec0aa82 | 4252ee9c | 5 | success
```

The fence above is for display. In the real file, write the lines as plain text below
the heading: one event per line, nine fields, `-` for not applicable.
