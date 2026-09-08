# The traceability matrix

One row per assessable requirement. The itemised evidence in the row **is** the report;
the coverage figure is a summary of it and never a substitute.

## Requirement identifiers

- Use the document's own numbering when it has one, verbatim, including its oddities.
  A reader must be able to find the requirement in their copy.
- When the document has no numbering, **assign identifiers and declare in the report
  that you assigned them**, with the scheme stated: `R-<area>-<n>`, and
  `R-<area>-<n>.<m>` for named sub-requirements. Undeclared assigned identifiers make a
  re-run incomparable and make findings look like they came from the document.
- Identifiers are stable across re-runs. Never renumber; append, and mark withdrawn
  identifiers as withdrawn rather than reusing them.
- **Split every requirement into named sub-requirements** before assessing. A
  requirement that cannot be split into things individually present or absent is a
  candidate Unfalsifiable requirement — see `finding-classes.md`.

## Row format

| Field | Content |
|---|---|
| ID | Stable identifier; `(assigned)` if not from the document |
| Requirement | One line, in the document's own terms |
| Sub-requirements | Named, each individually assessable |
| Present — evidence | Concrete artifacts by name: `Task` entity with `AssigneeId`, `SequenceOrder`; screen `TaskDetail`; action `SubmitTask`. Name the operation that showed each |
| Absent — evidence | What was checked and not found, by the name searched for. "No action anywhere references `SequenceOrder` (`context_actions`, `context_graph`)" |
| Coverage | `<n> of <m> named sub-requirements present`, then the percentage |
| Class | One of the five, per sub-requirement where they differ |
| Provenance note | Which area's provenance applies, and whether the finding is expected there |
| Remediation | Repair or rebuild, and the spec it becomes |

Two rules that carry the weight:

1. **Both evidence columns are itemised and both name artifacts.** An absent-evidence
   cell reading "not implemented" is not a finding, it is an assertion. It must say what
   was searched for and with which operation, so a reader can reproduce the search.
2. **Never write a row whose only content is a percentage.** If a row has no artifact
   names in it, it has not been assessed.

## Expressing "schema present, logic absent"

The most common shape, and the one a naive matrix destroys by averaging. Do not let a
single row absorb it. Split:

- `R-x.1` the data can be stored → present: `Task.SequenceOrder` exists.
- `R-x.2` the behaviour is enforced → absent: no action, no screen validation and no
  timer references `SequenceOrder` (`context_actions`, `context_graph`, `context_search`).

Coverage reads "1 of 2 named sub-requirements present (50%)", and the row plainly says
the capability does not work. A single unsplit row would have read "partially met" and
hidden that entirely.

## Rows that cannot be resolved

Three kinds, and each is reported as its own count rather than folded into coverage:

- **Unfalsifiable requirement** — cannot be assessed as written. `finding-classes.md`.
- **Unresolved by inventory** — the implementation would plausibly be a Resource,
  Automation or Timer, which the enumeration operations do not list. `inventory.md`.
- **Drift — undetermined** — differs from the document, and no decision record exists to
  say whether that was deliberate. `provenance.md`.

A row in any of these states must not appear in a numerator or a denominator. Reporting
them separately is the only handling that is neither an overstatement nor an
understatement of coverage.

## Security findings leave the matrix

A role inversion, an unauthorised write path, or a screen exposing another role's record
gets a row in the matrix for traceability **and** its own entry in the report's security
section. It is excluded from every coverage average — see `coverage-and-diagrams.md`.
Averaging a security finding into a percentage is how it stops being read.

## Make the matrix re-runnable

The matrix is the artifact a later re-run diffs against. So: stable IDs, the assignment
scheme declared, sub-requirement names unchanged between runs, and the inventory
operation named per evidence item. A re-run should be able to report "R-x.2 moved from
absent to present" without re-deriving the whole document.
