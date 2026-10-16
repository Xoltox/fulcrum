# Template - `.fulcrum/design/fidelity/<SID>-r<n>.md`

One file per screen per compare round, written by the orchestrator after the blind
verifier reports. Procedure, vocabulary and severity:
`../references/render-compare.md`. Never edited after the round closes; the next
round is a new file.

---

<!-- fulcrum-schema: design-fidelity v1 -->

# Fidelity - \<SID\> \<Name\> - round r\<n\>

- **Task:** \<T-NNN\>   **Step:** \<P1.NN\>   **Revision:** \<applicationRevision\>
- **Bar:** \<structural | visual\>   **Tier:** \<A | B | C\>
- **Evidence:** `.fulcrum/evidence/render/<task-id>/<UTC-stamp>/` (tier B: `design/user-shots/<SID>-r<n>.<ext>`, captured by the user)

## Verifier report (verbatim)

```
<the blind verifier's report, unedited: per F-item OK / FAIL / PARTIAL / untested,
the diff list, and what it could not judge>
```

## Triage

| Diff | Class | Severity | Disposition (fix / pattern / backlog) | Task id |
|---|---|---|---|---|
| \<observed vs expected\> | \<structure / data / icon / size / token / spacing / copy\> | \<blocker / major / minor\> | \<...\> | \<T-NNN or -\> |

## Verdict

\<pass | fail | unproven\> - \<one line: why; for unproven, which rung is untested
and the reason\>
