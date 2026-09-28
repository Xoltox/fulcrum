# File schemas

One heading per file. Read the heading for the file you are about to write or parse.
Skeletons to copy live in `../templates/`.

Rules that hold for every file here:

- UTC ISO-8601 timestamps, second precision: `2026-09-28T14:03:11Z`. Local time makes
  two sessions' lines interleave wrongly and is unorderable across machines.
- Identifiers are **app identifiers, never display names**, everywhere.
- `—` (em dash) means "not applicable or not yet known". Never leave a cell empty;
  an empty cell is indistinguishable from a truncated write.
- Never reorder or rename a column **within a schema version**. Position is the parse
  contract.
- **Every file with a schema of its own carries a version marker on its first content
  line:**
  `<!-- fulcrum-schema: <file-stem> v<N> -->`. Files whose schema is an existing contract
  elsewhere — `tenant-profile.md`, `HANDOFF.md`, `RUN-IDS.md`, `checkpoints/*` — carry
  the marker only if that contract adds one. Changing a field set, a field order or a
  field's meaning requires bumping `<N>` and updating this document in the same change.
  A reader that finds a version it does not know must stop and report — never guess
  field positions. Without the marker the "never reorder" rule has no legitimate
  mechanism for change, so the first schema change breaks it silently and every later
  parser reads the wrong column. `[UNVERIFIED]`

## project.md

`<!-- fulcrum-schema: project v1 -->`

Rewritten. Identity and settings only — no history, no task state.

| Field | Values |
|---|---|
| `solution` | Name of the solution, as the user calls it. |
| `created` | Timestamp of scaffold. |
| `mode` | `guided` \| `expert` |
| `posture` | `collaborative` \| `directive`. Definitions, the orthogonality rule and the opt-in rule: `../../../CONVENTIONS.md`, heading "Mode and posture". Not restated here. |
| `apps` | Table: app identifier, asset type, role in the solution, target environment. |
| `tier overrides` | Optional. `deep-reasoning` / `workhorse` / `poller` → a concrete model, per `../../../MODEL-TIERS.md`, heading "Resolution — how a tier becomes a concrete model". A project override is rank 1 there, so writing one here wins over the machine-local file. Omit the section entirely when there is no override — an empty section reads as a decision and pins nothing. |

`project.md` does **not** restate tenant facts. Those are in `tenant-profile.md`,
written by `../../fulcrum-solution-init/SKILL.md`. Point at it; never copy a row out
of it, or the two drift and the copy wins by being read first. `[VERIFIED]`

## brief.md

Written once by `../../fulcrum-discovery/SKILL.md`, consumed by
`../../fulcrum-solution-init/SKILL.md` at source triage. Derived requirements brief
produced from an interview when no written source material existed. Carries its own
`<!-- fulcrum-origin: discovery-interview -->` marker rather than a
`fulcrum-schema` version line. Shape: `../../fulcrum-discovery/templates/brief-template.md`.
Not restated here.

## TASKS.md

`<!-- fulcrum-schema: TASKS v1 -->`

Rewritten. The single answer to "what is open right now". A markdown table, because a
human reviews it as a diff in a pull request; the column contract is what keeps it
mechanically parseable at the same time.

Exactly these columns, in this order:

| # | Column | Values |
|---|---|---|
| 1 | `Done` | `[ ]` or `[x]`. Terminal state only. |
| 2 | `ID` | `T-<NNN>`, zero-padded, assigned once, **never reused** even after deletion. A reused ID makes a journal line ambiguous forever, and silently corrupts the oscillation count in the session index. |
| 3 | `Task` | One imperative line. No newlines, no pipes — escape a literal pipe as `\|`. |
| 4 | `App` | App identifier. This is the lease key; a wrong value here books the wrong lock. |
| 5 | `Turn` | `build` \| `fix` \| `inspect` \| `publish` \| `seed` \| `verify` \| `manual` |
| 6 | `Verify` | Required proof rungs, comma-separated rung numbers from `../../fulcrum-verification/SKILL.md`, heading "The proof ladder" — e.g. `1,3,6`. `—` is only valid for `Turn: inspect` and `Turn: manual`. |
| 7 | `Status` | `todo` \| `active` \| `blocked` \| `done` \| `parked` |
| 8 | `Verdict` | `—` \| `pass` \| `fail` \| `unproven` |
| 9 | `Traps` | Reference file stems from `../../fulcrum-engine-traps/references/`, comma-separated, or `—`. |
| 10 | `Step` | Plan step id from `plan.md`, e.g. `P2.04`. The traceability join. |

`Done` and `Status` are not redundant: `Done` is the reviewer's one-glance signal,
`Status` distinguishes the four not-done states that need different next actions.
`[UNVERIFIED]` `[x]` with `Status: done` and `Verdict: —` is malformed — a finished
task always carries a verdict, and `unproven` is a legal, honest one.

**Task entries are Mentor-turn-shaped, not tickets.** Every row names the app it
touches, the kind of turn it is, the proof it owes, and the traps that apply. A row
that cannot fill columns 4–6 is not yet a task; it is a plan item, and it belongs in
`plan.md` until it is decomposed.

**Row lifecycle.** Rows for the current phase stay in the table. At a phase boundary,
remove rows with `Status: done`. Nothing is lost: their creation, their run ids and
their outcomes are already in `JOURNAL.md` and `RUN-IDS.md`. Without the removal the
file grows without bound and stops being readable in one go, which is the one property
it exists to have.

## JOURNAL.md — the session index

`<!-- fulcrum-schema: JOURNAL v2 -->`

**`JOURNAL.md` is an index, one row per session — not per action.** The per-action
lines live in `journal/<session-id>.md`, one file per session.

**Why split.** A single monolithic journal is unbounded, and every agent that reads it
pays for the whole project history to answer a question about the last three steps.
The index is the only file a resuming or looping agent must read; a session file is
opened only when someone needs the detail of that one session.

**The index must answer both common queries without opening any session file.** If it
cannot, the cost has been moved, not removed. The two queries are **resume** and
**oscillation detection**, and the columns exist to serve them.

Exactly these columns, in this order:

| # | Column | Values |
|---|---|---|
| 1 | `Session` | `s-<6 hex>`. Also the session file's name: `journal/<session-id>.md`. |
| 2 | `Start` | Timestamp of the session's first write. |
| 3 | `End` | Timestamp the session closed, or `—` while open. |
| 4 | `State` | `open` \| `clean` \| `halted` \| `aborted`. `open` means the row was never closed — the session is live or it crashed. There is no `crashed` value; a crash is indistinguishable from a live session in the file alone, and claiming otherwise invents a fact. |
| 5 | `Tasks` | Task ids touched, comma-separated, each with its terminal outcome for **this session**: `T-003:pass,T-004:fail,T-007:unproven`. Written as each task reaches a terminal state, not at close. |
| 6 | `InFlight` | Task ids with a `started` line and no outcome, comma-separated, or `—`. |
| 7 | `Lines` | Count of action lines in the session file. Tells a reader what opening it costs. |
| 8 | `Note` | One clause — halt reason, budget exhaustion, operator interrupt — or `—`. |

**Query 1, resume.** Read the last row. `Start`/`End`/`State` give where it stopped and
whether it was clean; `InFlight` names the tasks that may have mutated the app with no
recorded outcome. One row, no session file.

**Query 2, oscillation detection.** Match a task id across column 5 of the whole index:
every session that touched `T-004`, with that session's outcome, in one scan. Two
`T-004:fail` occurrences is the "stuck twice means stop and report" non-negotiable in
`../../../AGENTS.md` firing **mechanically**, rather than depending on an agent
remembering it has been here before. `../../fulcrum-loop-engine/SKILL.md` is the main
consumer. `[UNVERIFIED]`

**The task list is inline, not a count plus a pointer.** Counts cannot answer "has this
task been attempted before, and how did it go" — that is the oscillation query itself,
and a pointer forces opening one session file per candidate session, which is exactly
the cost the split removes. The list is bounded in practice because a session is
bounded by its context budget; a row naming more than a dozen tasks is a mis-sized
session, not a reason to change the schema.

### Index write ordering

The row is **appended once at session start and completed in place**. A session edits
**only its own row**, never another's, so two sessions' edits land on different lines
and merge cleanly. Appending a second row to close a session would break the one-row-
per-session property that makes column 5 scannable.

At session start, in this order:

1. Mint the session id.
2. Create `journal/<session-id>.md` with its header line.
3. Append the index row: `End` `—`, `State` `open`, `Tasks` `—`, `InFlight` `—`.

Then during the session: set `InFlight` at dispatch and clear the id from it at
outcome; append the id and its verdict to `Tasks` the moment that task reaches a
terminal state. **Not at close** — a session that crashes mid-task must still leave its
attempt visible, and the crashed attempt is precisely the one oscillation detection
needs.

At session end: write `End`, set `State`, set `InFlight` to `—`.

### Reading a row that was never closed

`State: open` means the session is live **or** it crashed. The file cannot tell the
difference. Resolve it against the lease, never by guessing:

| Lease | Inference | Action |
|---|---|---|
| Live lease held by that session id | The session is running now | Wait or halt. Never take. `../../../AGENTS.md`: one Mentor session per app. |
| No lease, or an expired one | The session crashed | Recover per `resume-and-halt.md`. Treat every `InFlight` id as possibly-mutated: the app may have changed with no recorded outcome. |

### Index growth — the arithmetic

One row, roughly 130 bytes. A 47-step build at two to four sessions per step is about
150 rows, ~20 KB. A year of daily work is 250–500 rows, ~65 KB — a few thousand tokens
to read whole, which is the cost the split was buying down. No rotation is needed
below that. `[UNVERIFIED]`

**Rotation rule, at 500 rows or a major phase boundary, whichever comes first:** move
closed rows whose tasks are all terminal into `journal/INDEX-archive-<NN>.md`, leave a
single pointer line in `JOURNAL.md` naming the archive and the row range it holds, and
record the rotation in `DECISIONS.md`. Rotation is a deliberate, reviewed change —
never automatic, and never applied to a row whose `State` is `open` or whose tasks are
still live, because those are the rows both queries are about.

## journal/<session-id>.md

`<!-- fulcrum-schema: journal-session v1 -->`

**Append-only, one file per working session.** Never edit or delete a line; correct a
wrong line by appending a later line that withdraws it, per
`../../fulcrum-solution-init/references/repo-scaffold.md`, heading "The four
documentation failures to design against" — a silently deleted claim gets re-derived.

One line per event, pipe-delimited, fixed field order:

```
<timestamp> | <session-id> | <task-id or —> | <run-id or —> | <action> | <outcome>
```

- `session-id` — the same `s-<6 hex>` the filename carries. **Redundant on purpose.**
  A self-describing line survives the file being moved, quoted into a prompt, handed to
  a subagent as a fragment, or concatenated — and the rotation rule above concatenates.
  Ten characters a line is a cheaper premium than a merged archive nobody can attribute.
- `action` — a short verb phrase: `dispatch build turn`, `poll`, `publish`,
  `acquire lease`, `break expired lease`, `halt`, `resolve halt`, `withdraw`.
- `outcome` — `started`, `ok`, `failed: <reason>`, `blocked: <reason>`, or a value.

**Three ids, three different things. Do not confuse them.** A `session-id` is the
orchestrating agent's working session — one cold-start-to-stop span, and one file here.
A **Mentor session id** is the ODC-side session opened against an app and is not
written to this file. A **run id** is one Mentor or publish run inside that Mentor
session, and is field 4 here and in `RUN-IDS.md`. One working session may open several
Mentor sessions and many runs.

Two lines per unit of work is the norm: one `started` before the wait, one outcome
after. The `started` line is the one that matters — it is what tells a resuming session
that a turn may be in flight against the app.

Append only at the end of the file. A session file is written by exactly one session,
so it does not merge-conflict at all; the append discipline is what keeps a crashed
file readable and correctly ordered, not a concurrency measure.

**Crash-idempotency.** Creating the file and appending to it are both safe to repeat: a
re-created file that already exists is left alone, and a duplicate append is a
duplicate line, not a corruption. A crashed session therefore leaves a truncated but
**valid** file, and an index row that says `open` with the in-flight ids still listed —
which is a true description of the world, not a lie that has to be detected.

## DECISIONS.md

`<!-- fulcrum-schema: DECISIONS v1 -->`

**Append-only, ADR-lite.** One record per decision, newest appended at the bottom.

```markdown
## D-007 — <short title>

- **Date:** <timestamp>
- **Decider:** user | agent | mentor
- **Status:** accepted | superseded by D-0NN | reverted
- **Affects:** <app identifier> / <entity, screen, action or block identifiers>

**Context.** <What was true that forced a choice.>

**Decision.** <What was decided, in the imperative.>

**Alternatives rejected.** <What else was on the table, and why not.>

**Consequences.** <What this makes harder or impossible later.>
```

- **`Affects` is load-bearing.** `../../fulcrum-gap-analysis/SKILL.md` classifies a
  deviation as **drift** rather than a gap only if it can find a decision record for
  the artifact in question. It joins on the artifact identifier, not on prose, so a
  record that says "the ordering screens" instead of naming them will not be found and
  the deviation will be reported as a defect. `[UNVERIFIED]`
- **Never edit an accepted record.** Supersede it with a new one and set the old
  record's `Status` to `superseded by D-0NN` — that status line is the only edit ever
  permitted. Editing the body rewrites the dated evidence that explains why the app
  looks the way it does at a given revision.
- `Decider: mentor` means Mentor chose the approach and the agent accepted it. Record
  it. Under `posture: collaborative` this is the common case, and an unrecorded
  Mentor choice is exactly the drift gap analysis cannot explain later.

## RUN-IDS.md

**Append-only. Existing contract** — schema and rationale in
`../../fulcrum-solution-init/references/repo-scaffold.md`, heading "Durable run-id
log", and mechanics in `../../fulcrum-mentor-turns/SKILL.md`. Do not restate it here.

`.fulcrum/` adds one thing to the stated minimum: **include the task ID** on each
line. It is the join key from a run back to `TASKS.md`, and without it a resuming
session that finds an unpolled run cannot tell which row it belongs to.

## HANDOFF.md

**Existing contract** — two parts, RULES stable and BRIEF replaced wholesale. Schema:
`../../fulcrum-solution-init/templates/handoff-template.md`. Do not restate or fork it.

Inside `.fulcrum/` it is a **regenerated snapshot**: its BRIEF is derivable from
`TASKS.md` plus the last rows of `JOURNAL.md`, and it exists so a cold reader gets the
current position in one read. Where the BRIEF and `TASKS.md` disagree, `TASKS.md`
wins and the BRIEF is stale — regenerate it rather than reconciling by hand.

## plan.md

Rewritten, rarely. Phases and steps, with a stable step id (`P<phase>.<NN>`) per step.
Sizing and decomposition rules belong to `../../fulcrum-solution-init/SKILL.md`; this
file only requires that every step id referenced by a `TASKS.md` row exists here.

## runs/<run-id>.md

Optional, one per run, for detail too large for a session-file line — a full prompt, a
diff, a failure dump. The session-file line and the `RUN-IDS.md` entry are mandatory; this
file is not. Never make it the only record of a run id.

## checkpoints/<agent-label>.md

**Existing contract, unchanged** — `../../fulcrum-unattended-guardrails/references/checkpoints.md`.
Overwrite in place, one file per agent, a page not a transcript. `.fulcrum/` supplies
the path so the orchestrator does not invent one, which that contract requires it to
supply. These files are ephemeral working state; they may be gitignored, and nothing
may depend on one after its agent ends. The durable residue of a checkpoint is the
session-file line and the TASKS row.

## HALT.md

Present only when halted. See `resume-and-halt.md`.

## lease.json

Not committed. See `lease-and-concurrency.md`.
