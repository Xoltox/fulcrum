# File schemas

One heading per file. Read the heading for the file you are about to write or parse.
Skeletons to copy live in `../templates/`.

Rules that hold for every file here:

- UTC ISO-8601 timestamps, second precision: `2026-09-28T14:03:11Z`. Local time makes
  two sessions' lines interleave wrongly and is unorderable across machines.
- Identifiers are **app identifiers, never display names**, everywhere.
- `-` means not applicable (or not yet known). Never leave a cell empty;
  an empty cell is indistinguishable from a truncated write.
- Never reorder or rename a column **within a schema version**. Position is the parse
  contract.
- **Every file with a schema of its own carries a version marker on its first content
  line:**
  `<!-- fulcrum-schema: <file-stem> v<N> -->`. Files whose schema is an existing contract
  elsewhere (`tenant-profile.md`, `HANDOFF.md`, `checkpoints/*`) carry
  the marker only if that contract adds one. `RUN-IDS.md` has its own schema and carries one. Changing a field set, a
  field order or a field's meaning requires bumping `<N>` and updating this document in the same change.
  A reader that finds a version it does not know must stop and report - never guess
  field positions. Without the marker the "never reorder" rule has no legitimate
  mechanism for change, so the first schema change breaks it silently and every later
  parser reads the wrong column. `[UNVERIFIED]`

## Write ownership - who writes which file

In the two projects that ran builds, `.fulcrum/` went stale within a day: `TASKS.md` still
showed finished tasks as `todo`, `project.md` still said "halted" after the gate
passed, `RUN-IDS.md` ended at a `started` line while later work existed.
`[VERIFIED]` The cause was the same each time - several writers (orchestrator,
drivers, pollers, the user) and no rule naming who updates the shared files. One
writer per shared file removes the race and makes staleness one agent's job to fix.

| File | Written by | Others |
|---|---|---|
| `project.md`, `plan.md`, `TASKS.md`, `DECISIONS.md`, `HANDOFF.md`, `external/*` | **the orchestrator only** | Drivers report outcomes, decisions and facts in their result; the orchestrator records them |
| `JOURNAL.md` | the orchestrator; each working session writes **only its own index row** | Drivers never edit the index, `InFlight` or `Tasks` |
| `journal/<session-id>.md` | the orchestrator, which mints the session id and creates the file | A driver appends rows only to the session file whose path its brief names |
| `RUN-IDS.md` | whoever issued the run (a driver, or the orchestrator acting as one) | Append only |
| `lease.<app>.json` | **the orchestrator only** (Fulcrum rule): taken before a Mentor dispatch, released when it returns `session_state: closed`; held (with `open_session`) when it returns `session_state: open` | Drivers and pollers never write it; no per-poll refresh |
| `HALT.md` | whoever stopped the run | Clearing it: `resume-and-halt.md`, heading "Resuming past a halt" |
| `tenant-profile.md` | `../../fulcrum-solution-init/SKILL.md`, or the orchestrator recording a newly observed tenant fact | - |
| `checkpoints/<agent-label>.md` | that agent | - |
| `evidence/render/<task-id>/<UTC-stamp>/*` | `fulcrum-renderer`, only the folder its brief names | The orchestrator links the folder from the session journal line; nobody edits evidence after the run |
| `design/*` | `fulcrum-capturer` in the design loop's capture and gate phases (only the paths its brief names: a shared dispatch the app-wide `tokens.md`, `theme.css`, `data.md`; a screen dispatch only its `screens/<SID>.md`); the orchestrator after. `design/reference/*` and `design/user-shots/*` are the orchestrator's only: it copies the image source, or a renderer capture out of `evidence/render/`, into `reference/`, and files a user's tier-B screenshot under `user-shots/` | Drivers, renderer and verifier never write it |

A **driver** (a delegated agent running turns) writes nothing outside appended rows in
the session journal file its brief names, its `RUN-IDS.md` lines and, if it stops the
run, `HALT.md`. It never mints session ids, never edits the `JOURNAL.md` index or
`TASKS.md`, and never writes the lease. When
there is no delegation, the orchestrator is its own driver and the table still holds.

**Reconcile at every wave close.** Before starting the next wave or ending the
session, the orchestrator reads the wave's index rows, their session files where a
row is not enough, and the new `RUN-IDS.md` lines, then rewrites `TASKS.md` (status,
verdict), `project.md` (newly created app identifiers) and `HANDOFF.md` PART 2 to
match, and commits. Check while doing it: every run id has an outcome line or is named
in some row's `InFlight`; no `TASKS.md` row is `active` without an open session; a
`halted` row has a `HALT.md` and vice versa. A reconciliation skipped "because nothing
changed" is how the stale files above were produced.

**No resume point outside `.fulcrum/`.** An orchestrator checkpoint written elsewhere
(a session-checkpoint file at the repo root, a commit message, a chat summary) becomes
a competing source of truth - in the field it was updated instead of `.fulcrum/` and
ended a full revision ahead of it. `[VERIFIED]` Where we are lives in `TASKS.md` plus
the last `JOURNAL.md` row; the next step and its preconditions in `HANDOFF.md` PART 2
(full profile); anything waiting on the user in the `TASKS.md` "Blocked and parked
rows" table with `Blocked on: the user`. An ephemeral `checkpoints/<agent-label>.md`
is fine, but its durable content moves into those files at wave close.

## project.md

`<!-- fulcrum-schema: project v3 -->`

v2 adds `profile`. A v1 file is read as `profile: full`. v3 adds the optional
`design` field; a v2 file is read as v3 without it.

Rewritten. Identity and settings only - no history, no task state.

| Field | Values |
|---|---|
| `solution` | Name of the solution, as the user calls it. |
| `created` | Timestamp of scaffold. |
| `mode` | `guided` \| `expert` |
| `posture` | `collaborative` \| `directive`. Definitions, the orthogonality rule and the opt-in rule: `../../../CONVENTIONS.md`, heading "Mode and posture". Not restated here. |
| `profile` | `full` \| `micro`. The user confirms micro when the router proposes it; `micro-profile.md`. |
| `apps` | Table: app identifier, asset type, role in the solution, target environment. |
| `design` | Optional. `.fulcrum/design/manifest.md` when the engagement runs the design loop (`../../fulcrum-design-loop/SKILL.md`); on the full profile a list, one `.fulcrum/design/<app>/manifest.md` per app the loop runs for. Present -> the loop engine runs rung 6 on screen rows as the design variant (render-compare). Omit otherwise. |
| `browser` | Optional. The render preflight result for this project: state (`callable` \| `unavailable` \| `unknown`), the browser tool set found (e.g. the MCP server prefix), the capabilities it covers, and the date. Per project, because the harness and its browser can differ between projects. Written per `../../fulcrum-render-check/SKILL.md`, heading "Preflight - once per project". |
| `tier overrides` | Optional. `deep-reasoning` / `workhorse` / `poller` -> a concrete model, per `../../../MODEL-TIERS.md`, heading "Resolution - how a tier becomes a concrete model". A project override is rank 1 there, so writing one here wins over the machine-local file. Omit the section entirely when there is no override - an empty section reads as a decision and pins nothing. |

`project.md` carries no run outcome, gate verdict or halt status: those are in
`RUN-IDS.md`, `TASKS.md` and `HALT.md`, and a copy here was the line found stale in
the field. `project.md` does **not** restate tenant facts either. Those are in `tenant-profile.md` (`.fulcrum/` first, else the nearest parent
directory's), written by `../../fulcrum-solution-init/SKILL.md`. Point at it; never copy a row out
of it, or the two drift and the copy wins by being read first. `[VERIFIED]`

## brief.md

Written once by `../../fulcrum-discovery/SKILL.md`, consumed by
`../../fulcrum-solution-init/SKILL.md` at source triage. Derived requirements brief
produced from an interview when no written source material existed. Carries its own
`<!-- fulcrum-origin: discovery-interview -->` marker rather than a
`fulcrum-schema` version line. Shape: `../../fulcrum-discovery/templates/brief-template.md`.
Not restated here. `brief.md` is distinct from the root `DOMAIN.md` that
`../../fulcrum-solution-init/references/repo-scaffold.md` scaffolds: the brief is the
discovery interview's output, `DOMAIN.md` is the domain source of truth derived from it.

## TASKS.md

`<!-- fulcrum-schema: TASKS v2 -->`

v2 adds the `code`, `infra` and `external` turn types; columns and order are
unchanged from v1. A v1 file is read as v2 with no other change.

Rewritten. The single answer to "what is open right now". A markdown table, because a
human reviews it as a diff in a pull request; the column contract is what keeps it
mechanically parseable at the same time.

Exactly these columns, in this order:

| # | Column | Values |
|---|---|---|
| 1 | `Done` | `[ ]` or `[x]`. Terminal state only. |
| 2 | `ID` | `T-<NNN>`, zero-padded, assigned once, **never reused** even after deletion. A reused ID makes a journal line ambiguous forever, and silently corrupts the oscillation count in the session index. |
| 3 | `Task` | One imperative line. No newlines, no pipes - escape a literal pipe as `\|`. |
| 4 | `App` | App identifier. This is the lease key; a wrong value here books the wrong lock. For `Turn: external` rows, the system stem from `external/<system>.md`. |
| 5 | `Turn` | `build` \| `fix` \| `inspect` \| `publish` \| `seed` \| `verify` \| `manual` \| `code` \| `infra` \| `external` |
| 6 | `Verify` | Required proof rungs, comma-separated rung numbers from `../../fulcrum-verification/SKILL.md`, heading "The proof ladder" - e.g. `1,3,6`. `-` is valid for `inspect`, `manual`, `code`, `infra` and `external` rows; for the last three the session-file outcome line names the evidence (test run, build output, listing). |
| 7 | `Status` | `todo` \| `active` \| `blocked` \| `done` \| `parked` |
| 8 | `Verdict` | `-` \| `pass` \| `fail` \| `unproven` |
| 9 | `Traps` | Reference file stems from `../../fulcrum-engine-traps/references/`, comma-separated, or `-`. |
| 10 | `Step` | Plan step id from `plan.md`, e.g. `P2.04`. The traceability join. |

**Turn types.** The first six are Mentor work against an ODC app. The rest are not:

| Turn | Means | Lease |
|---|---|---|
| `manual` | A step only the user can take (Portal-only operation, asset upload, setting a secret, a sign-in-gated check). Normally `parked` with `Blocked on: the user` | none |
| `code` | Repository code the agent writes outside Mentor - an External Logic library's source, a script, a test harness | none |
| `infra` | Infrastructure or environment work - gateway, connector, CI, local tooling | none |
| `external` | Building, deploying or changing an external system or integration target (`external/<system>.md`) | none |

Before v2, field projects forced code and infrastructure work into `manual`, which
told every reader the user had to do it. `[VERIFIED]` Only Mentor turns take a lease;
the lease is the one-Mentor-session-per-app lock, not a general mutex.

**Columns stay contract values.** `Status`, `Verdict` and `Turn` take only the values
above - no "done (partial: ...)", no "read-only", no "mentor". `Traps` takes only
registry stems; an incident description goes in the session file, and a new trap is
reported as engine-traps feedback (see "DECISIONS.md" below for what does not go
there either). A cell that needs prose means the task should be split, or the prose
belongs in the journal.

`Done` and `Status` are not redundant: `Done` is the reviewer's one-glance signal,
`Status` distinguishes the four not-done states that need different next actions.
`[UNVERIFIED]` `[x]` with `Status: done` and `Verdict: -` is malformed - a finished
task always carries a verdict, and `unproven` is a legal, honest one.

**Task entries are Mentor-turn-shaped, not tickets.** Every row names the app it
touches, the kind of turn it is, the proof it owes, and the traps that apply. A row
that cannot fill columns 4-6 is not yet a task; it is a plan item, and it belongs in
`plan.md` until it is decomposed.

**Row lifecycle.** Rows for the current phase stay in the table. At a phase boundary,
remove rows with `Status: done`. Nothing is lost: their creation, their run ids and
their outcomes are already in `JOURNAL.md` and `RUN-IDS.md`. Without the removal the
file grows without bound and stops being readable in one go, which is the one property
it exists to have.

## JOURNAL.md - the session index

`<!-- fulcrum-schema: JOURNAL v2 -->`

**`JOURNAL.md` is an index, one row per session - not per action.** The per-action
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
| 3 | `End` | Timestamp the session closed, or `-` while open. |
| 4 | `State` | `open` \| `clean` \| `halted` \| `aborted`. `open` means the row was never closed - the session is live or it crashed. There is no `crashed` value; a crash is indistinguishable from a live session in the file alone, and claiming otherwise invents a fact. |
| 5 | `Tasks` | Task ids touched, comma-separated, each with its terminal outcome for **this session**: `T-003:pass,T-004:fail,T-007:unproven`. Written as each task reaches a terminal state, not at close. |
| 6 | `InFlight` | Task ids with a `started` line and no outcome, comma-separated, or `-`. |
| 7 | `Lines` | Count of action lines in the session file. Tells a reader what opening it costs. |
| 8 | `Note` | One clause - halt reason, budget exhaustion, operator interrupt - or `-`. |

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
task been attempted before, and how did it go" - that is the oscillation query itself,
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
3. Append the index row: `End` `-`, `State` `open`, `Tasks` `-`, `InFlight` `-`.

Then during the session: set `InFlight` at dispatch and clear the id from it at
outcome; append the id and its verdict to `Tasks` the moment that task reaches a
terminal state. **Not at close** - a session that crashes mid-task must still leave its
attempt visible, and the crashed attempt is precisely the one oscillation detection
needs.

At session end: write `End`, set `State`, set `InFlight` to `-`.

### Reading a row that was never closed

`State: open` means the session is live **or** it crashed. The file cannot tell the
difference. Resolve it against the lease, never by guessing:

| Lease | Inference | Action |
|---|---|---|
| Live lease held by that session id | The session is running now | Wait or halt. Never take. `../../../AGENTS.md`: one Mentor session per app. |
| No lease, or an expired one whose holder's dispatch is known dead (no return, budget exceeded) | The session crashed | Recover per `resume-and-halt.md`. Treat every `InFlight` id as possibly-mutated: the app may have changed with no recorded outcome. |

### Index growth - the arithmetic

One row, roughly 130 bytes. A 47-step build at two to four sessions per step is about
150 rows, ~20 KB. A year of daily work is 250-500 rows, ~65 KB - a few thousand tokens
to read whole, which is the cost the split was buying down. No rotation is needed
below that. `[UNVERIFIED]`

**Rotation rule, at 500 rows or a major phase boundary, whichever comes first:** move
closed rows whose tasks are all terminal into `journal/INDEX-archive-<NN>.md`, leave a
single pointer line in `JOURNAL.md` naming the archive and the row range it holds, and
record the rotation in `DECISIONS.md`. Rotation is a deliberate, reviewed change -
never automatic, and never applied to a row whose `State` is `open` or whose tasks are
still live, because those are the rows both queries are about.

## journal/<session-id>.md

`<!-- fulcrum-schema: journal-session v1 -->`

**Append-only, one file per working session.** Never edit or delete a line; correct a
wrong line by appending a later line that withdraws it, per
`../../fulcrum-solution-init/references/repo-scaffold.md`, heading "The four
documentation failures to design against" - a silently deleted claim gets re-derived.

One line per event, pipe-delimited, fixed field order:

```
<timestamp> | <session-id> | <task-id or -> | <run-id or -> | <action> | <outcome>
```

- `session-id` - the same `s-<6 hex>` the filename carries. **Redundant on purpose.**
  A self-describing line survives the file being moved, quoted into a prompt, handed to
  a subagent as a fragment, or concatenated - and the rotation rule above concatenates.
  Ten characters a line is a cheaper premium than a merged archive nobody can attribute.
- `action` - a short verb phrase: `dispatch build turn`, `poll`, `publish`,
  `acquire lease`, `break expired lease`, `release lease`, `hold lease`, `halt`, `resolve halt`,
  `withdraw`.
- `outcome` - `started`, `ok`, `failed: <reason>`, `blocked: <reason>`, or a value.

**Three ids, three different things. Do not confuse them.** A `session-id` is the
orchestrating agent's working session - one cold-start-to-stop span, and one file here.
The orchestrator mints it; drivers write lines carrying it but never mint one.
A **Mentor session id** is the ODC-side session opened against an app and is
written to this file only as the outcome of a `hold lease` line (a dispatch returned
`session_state: open`). A **run id** is one Mentor or publish run inside that Mentor
session, and is field 4 here and in `RUN-IDS.md`. One working session may open several
Mentor sessions and many runs.

Two lines per unit of work is the norm: one `started` before the wait, one outcome
after. The `started` line is the one that matters - it is what tells a resuming session
that a turn may be in flight against the app.

Append only at the end of the file. A session file is written by exactly one session,
so it does not merge-conflict at all; the append discipline is what keeps a crashed
file readable and correctly ordered, not a concurrency measure.

**Crash-idempotency.** Creating the file and appending to it are both safe to repeat: a
re-created file that already exists is left alone, and a duplicate append is a
duplicate line, not a corruption. A crashed session therefore leaves a truncated but
**valid** file, and an index row that says `open` with the in-flight ids still listed -
which is a true description of the world, not a lie that has to be detected.

## DECISIONS.md

`<!-- fulcrum-schema: DECISIONS v2 -->`

v2 makes the file strictly append-only: `Status` no longer changes in place, and a
`Supersedes` field carries the link instead. A v1 file stays readable; its in-place
`superseded by` lines are honoured as written, and new records use v2.

**Append-only, ADR-lite.** One record per decision, newest appended at the bottom.
**No existing line is ever edited, including `Status`.**

```markdown
## D-007 - <short title>

- **Date:** <timestamp>
- **Decider:** user | agent | mentor
- **Status:** proposed | accepted | rejected | reverted
- **Supersedes:** D-0NN | -
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
- **A status change is a new record.** Approval of a `proposed` decision, a reversal,
  or a replacement is appended as a new record whose `Supersedes` names the old one.
  A record is current unless a later record supersedes it; readers find that by
  scanning `Supersedes`, never by trusting an old record's `Status`. In the field a
  `Status` edited in place ("accepted (user approved ... record outcome in ...)")
  erased when approval happened and left the outcome unrecorded. `[SINGLE-OBSERVATION]`
  Editing the body rewrites the dated evidence that explains why the app looks the
  way it does at a given revision.
- **Not everything with a reason is a decision.** A platform or tenant fact (a runtime
  version cut-off, a missing upload path, a tool that behaves differently) goes to
  `tenant-profile.md`; a construct that fails to build or publish goes to the
  engine-traps registry as feedback (`../../fulcrum-engine-traps/SKILL.md`). Both
  were found stored as decision rationale, where no later reader looks for them.
  `[VERIFIED]` A decision may cite either; it does not hold it.
- **Adopt, do not re-transcribe.** If the engagement already has a decision log from
  before Fulcrum, link it from `DECISIONS.md` and append only new records here.
  Copying it creates two numberings of one history.
- **Before artifacts exist**, `Affects` names the intended identifier from
  `plan.md` or the brief, marked `(planned)`. A later record may supersede it with
  the real identifier.
- `Decider: mentor` means Mentor chose the approach and the agent accepted it. Record
  it. Under `posture: collaborative` this is the common case, and an unrecorded
  Mentor choice is exactly the drift gap analysis cannot explain later.

## RUN-IDS.md

`<!-- fulcrum-schema: RUN-IDS v1 -->`

**Append-only.** Why it exists: `../../fulcrum-solution-init/references/repo-scaffold.md`,
heading "Durable run-id log". Polling mechanics: `../../fulcrum-mentor-turns/SKILL.md`.
This heading owns the line format.

One line per event, pipe-delimited, fixed field order:

```
<timestamp> | <session-id> | <task-id> | <app> | <op> | <run-id> | <publication-key> | <revision> | <outcome>
```

- `task-id` - the join key back to `TASKS.md`. Without it a resuming session that
  finds an unpolled run cannot tell which row it belongs to.
- `op` - `create-asset` | `prompt` | `publish` | `extlib` | `deploy` | another tool
  name for any other long-running start.
- `run-id` - the id the start call returned. For `create-asset`, the returned
  application key goes in `outcome` once known.
- `publication-key`, `revision` - `-` except on `publish` lines.
- `outcome` - `started` first; later lines carry `accepted`, a terminal value, or
  `failed: <code>`.

**Two or more lines per run, never one edited line.** Append `started` the instant the
id is issued; append the outcome as a later line repeating the run id. A run with a
`started` line and no later line is the crash-recovery signal.

**Publish yields two ids, so it gets its own slot.** The Publish prompt's `runId` is
not the publication key; the key arrives only in the run's `publishAccepted` event,
and `publish_status` is polled with the key (facts and dates:
`../../fulcrum-mentor-turns/references/mcp-surface.md`, heading "Publishing"). Record
a publish as:

```
2026-10-08T11:02:10Z | s-4c1e9a | T-006 | claims_web | publish | 3ec0aa82 | - | - | started
2026-10-08T11:02:41Z | s-4c1e9a | T-006 | claims_web | publish | 3ec0aa82 | 4252ee9c | 5 | accepted
2026-10-08T11:03:05Z | s-4c1e9a | T-006 | claims_web | publish | 3ec0aa82 | 4252ee9c | 5 | success
```

The terminal `outcome` uses the `publish_status` outcome vocabulary from the same
heading. Before this slot existed, projects mixed run ids, publication keys,
revisions, deployment and build keys and Mentor session ids on free-text lines and
the publish outcome was lost. `[VERIFIED]` Other keys (`deploymentKey`, `buildKey`,
Mentor session id) go in the session-file line, not here.

## HANDOFF.md

**Existing contract** - two parts, RULES stable and BRIEF replaced wholesale. Schema:
`../../fulcrum-solution-init/templates/handoff-template.md`. Do not restate or fork it.

Inside `.fulcrum/` it is a **regenerated snapshot**: its BRIEF is derivable from
`TASKS.md` plus the last rows of `JOURNAL.md`, and it exists so a cold reader gets the
current position in one read. Where the BRIEF and `TASKS.md` disagree, `TASKS.md`
wins and the BRIEF is stale - regenerate it rather than reconciling by hand.

## plan.md

Rewritten, rarely. Phases and steps, with a stable step id (`P<phase>.<NN>`) per step.
Sizing and decomposition rules belong to `../../fulcrum-solution-init/SKILL.md`; this
file only requires that every step id referenced by a `TASKS.md` row exists here.

Micro profile: `plan.md` is filled from `../templates/plan-micro.md` by the
orchestrator, and carries its own `<!-- fulcrum-schema: plan-micro v1 -->` marker.
See `micro-profile.md`.

Where the user keeps other project files (specs, domain notes, source exports) is the
user's choice. `plan.md` or `HANDOFF.md` PART 1 records the actual paths; Fulcrum does
not impose a folder layout outside `.fulcrum/`.

## external/<system>.md

`<!-- fulcrum-schema: external-system v1 -->`

Rewritten when the contract changes. One file per external system or integration
target the solution consumes; template `../templates/external-system.md`. Exactly
these H2 sections, in this order: `## Endpoint and auth`, `## Payload contract`,
`## Error codes`, `## Log locations`.

- **Gate:** the file exists, with every section filled or marked unresolved, before
  the first ODC step that consumes the system starts. A step whose system has no file
  is `blocked`.
- Auth names the scheme and where the secret lives (normally a secret Setting the user
  sets in the Portal) - never the secret value.
- Each log path is verified once with a directory listing and recorded with the date.
  Briefs and diagnosis prompts copy paths from here, never from memory: a wrong path
  in a brief made a diagnosis agent report a working system as untested. `[SINGLE-OBSERVATION]`

## runs/<run-id>.md

Optional, one per run, for detail too large for a session-file line - a full prompt, a
diff, a failure dump. The session-file line and the `RUN-IDS.md` entry are mandatory; this
file is not. Never make it the only record of a run id.

## evidence/render/<task-id>/<UTC-stamp>/

Written once by `fulcrum-renderer`, never edited. `report.md` plus capture
files; layout and the per-assertion record:
`../../fulcrum-render-check/references/evidence-and-report.md`. `<UTC-stamp>`
is compact UTC (`20261016T140311Z`). `report.md` is committed. Screenshots can
contain real data, so whether they are committed is the user's choice, asked
before the first render and recorded in `DECISIONS.md`. Until it is recorded a
render writes no screenshot file (page text and DOM snapshot only); Fulcrum
never adds an ignore entry or leaves files untracked on its own. Never a
secret, token or cookie.

## design/

Present only on the design loop (`project.md` field `design`); on the full profile one
`design/<app>/` per app, same layout. Layout: `manifest.md`,
`source/` (verbatim copies of the user's design, write-once), `reference/<SID>.<ext>`
(the image source copied unchanged, or a copied HTML render; orchestrator only),
`tokens.md`, `theme.css`, `data.md`, `screens/<SID>.md`, `gate.md`,
`fidelity/<SID>-r<n>.md`, `user-shots/<SID>-r<n>.<ext>` (tier B, orchestrator only),
`backlog.md`, `report.md`. Markers, `<!-- fulcrum-schema: <marker> -->`:
`design-manifest v1`, `design-screen v1`, `design-gate v1`, `design-fidelity v1`,
`design-report v1`; the other files carry none. The schemas live in `../../fulcrum-design-loop/references/design-spec-format.md`,
not here. Whether `source/` copies and render screenshots are committed is the user's
choice, recorded in `DECISIONS.md`. Ownership: "Write ownership" above.

## checkpoints/<agent-label>.md

**Existing contract, unchanged** - `../../fulcrum-unattended-guardrails/references/checkpoints.md`.
Overwrite in place, one file per agent, a page not a transcript. `.fulcrum/` supplies
the path so the orchestrator does not invent one, which that contract requires it to
supply. These files are ephemeral working state; they may be gitignored, and nothing
may depend on one after its agent ends. The durable residue of a checkpoint is the
session-file line and the TASKS row.

## HALT.md

Present only when halted, and **always a file**. A halt written only in prose - a
journal note, a `project.md` line, a chat report - is not a halt: the next session
reads no `HALT.md` and resumes. In the field, two projects "halted" in prose and
neither wrote the file. `[VERIFIED]` Contents and clearing: `resume-and-halt.md`.

## lease.<app>.json

Not committed. One per app. See `lease-and-concurrency.md`.
