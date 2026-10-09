# Detection procedure

The full state-detection ladder, cheap by construction, plus every
conflicting-signal case found so far. `[UNVERIFIED]` - new design, not an
observed procedure; sharpen as real conflicts surface.

## What "cheap" means here

Three checks, in order, each answerable without opening a session file:

1. **Does `.fulcrum/` exist in the project repo?** A directory check.
2. **Does an app already exist?** `env_apps` / `app_list`-shaped inventory
   check against the tenant, or a repo convention that already names the
   target app. Read-only, no Mentor session.
3. **Is there source material?** A file glob for anything that looks like a
   BRD, a Figma/Stitch export, HTML mockups, or screenshots, in the locations
   `../../fulcrum-solution-init/references/source-triage.md` already enumerates.
   Do not re-derive that list here - cite it.

None of these three requires reading `plan.md`, `TASKS.md`, a session file, or
any Mentor state. If a step needs a session file to answer, detection has
already gone off cheap - stop and re-derive the answer from the index instead.

## The ladder, in full

| # | Found | Route | Notes |
|---|---|---|---|
| 0 | No `.fulcrum/`, no app, no BRD or source material to triage, and the ask names one app of about five or fewer steps | **Propose** the micro profile; the user confirms | Confirmed: `../../fulcrum-project-state/references/micro-profile.md`, then `../../fulcrum-loop-engine/SKILL.md` phase 1. Declined: rows 1-2. Signals and the proposal: "Proposing the micro profile" below. |
| 1 | No `.fulcrum/`, no app, no source material | `../../fulcrum-discovery/SKILL.md` | Nothing to ingest yet; interview first. |
| 2 | No `.fulcrum/`, no app, source material present | `../../fulcrum-solution-init/SKILL.md` | Source material is the trigger, not the user's framing of it. |
| 3 | No `.fulcrum/`, app exists | `../../fulcrum-gap-analysis/SKILL.md` | An app with no `.fulcrum/` was built by something other than a Fulcrum-tracked session (a generator, a prior manual build, another agent). Never re-run `fulcrum-solution-init` against it - that skill is pre-build only. |
| 4 | `.fulcrum/` present, `HALT.md` present | Stop, report, ask a human | See `../SKILL.md`, heading "HALT.md is absolute - state the mechanism". Absolute - no exceptions below override this row. |
| 5 | `.fulcrum/` present, last `JOURNAL.md` row `State: open` | Resume at `../../fulcrum-loop-engine/SKILL.md` phase 4 (poll to terminal) | Possible crash or a run still executing - not a halt. See `../../fulcrum-project-state/references/resume-and-halt.md`, "Crash recovery". |
| 6 | `.fulcrum/` present, last row `State: clean`, open task in `TASKS.md` | Resume -> `../../fulcrum-loop-engine/SKILL.md` phase 1 | Clean stop; select the next actionable row. |
| 7 | `.fulcrum/` present, all tasks closed | Report status; offer next phase | Read `plan.md` only now, to name what phase comes next. If none remains, offer `../../fulcrum-gap-analysis/SKILL.md` as a completeness check. |

Rows 4-7 apply unchanged to a `.fulcrum/` on the micro profile (`profile: micro` in
`project.md`); only its file set is smaller.

Rows 5 and 6 both answer from the **last row alone** - never scan the whole
index and never open `journal/<session-id>.md` to decide which of the two
applies. That file is opened only by the loop engine, once it is already
committed to resuming, to get recovery detail the row itself does not carry.

## Proposing the micro profile

Signals, all required, all answerable from the user's ask and the cheap checks above:
one app (no agent, workflow or second app named); about five or fewer steps when the
ask is sketched as steps; no BRD, design export or other source material that needs
triage. A short written ask, or a one-paragraph note, is not source material in this
sense.

Put it to the user in the first batch, alongside mode, as one question: micro
(recommended, with the one-clause reason - "one app, about N steps, no source
material to triage") or the full path (discovery, or solution-init if source material
appears). If micro is confirmed, the app-creation choice follows as the micro
profile's first question - neither option is the default
(`../../fulcrum-solution-init/SKILL.md`, step 2).
**Never auto-pick micro**, including in `expert` mode: the user may know the scope will
grow, and a profile chosen for them is a scope decision taken without them.

If the ask is too vague to write the micro plan's Acceptance section in observable
terms, micro is still possible, but the holes are filled first with
`../../fulcrum-discovery/SKILL.md` in its fill-one-hole use, not by guessing.

## Conflicting-signal cases

### A freshly made shell app is not an existing app

The user chose the shell option and made a template app in Studio or the Portal for
this engagement, before `.fulcrum/` exists. The cheap check now finds an app, which
reads as row 3. It is not: there is nothing built to assess. Ask the user to confirm
it is the shell for this engagement (name the app identifier found); if yes, route by
row 0, 1 or 2 as if no app existed and record the shell in `DECISIONS.md`. If the app
carries anything beyond the template screen set, it is row 3.

### A micro engagement outgrows its profile

A second app, more than about five steps, or source material that needs triage
appears in a `profile: micro` project. Do not keep extending the micro plan. Stop at a
step boundary and offer promotion per
`../../fulcrum-project-state/references/micro-profile.md`, heading "Leaving the micro
profile".

### The plan names an external system with no contract file

A step that consumes an external system cannot start until
`.fulcrum/external/<system>.md` exists (`../../fulcrum-project-state/references/file-schemas.md`,
heading "external/<system>.md"). Report which file is missing and route the next
action to the user, or to a `Turn: external` task; building the system itself is out
of family.

Detection degrades honestly rather than picking silently. Each case names what
the router does; none of them is resolved by guessing.

### `.fulcrum/` exists but does not match the tenant or app in scope

E.g. `project.md` names an app identifier that the current tenant's inventory
does not contain, or names an environment the current session has no
credentials for.

**Do not treat this as "no `.fulcrum/`."** That silently starts a second
engagement over one already in flight and is exactly the kind of drift
`../../fulcrum-project-state/SKILL.md` exists to prevent. Report the mismatch -
named app, named tenant, what `project.md` says versus what was found - and
ask which is authoritative. Do not guess and do not auto-correct `project.md`.

### An app exists, but `.fulcrum/` is absent everywhere checked

Route to `../../fulcrum-gap-analysis/SKILL.md` per row 3. Say explicitly in the
handoff that provenance is unknown - gap analysis's own first step already
establishes provenance before judging anything
(`../../fulcrum-gap-analysis/SKILL.md`, "Gap analysis never assumes how the app
got there," `../../../CONVENTIONS.md`), so the router does not need to determine
it; it only needs to not assume the app is untouched Fulcrum work.

### `TASKS.md` has rows but `plan.md` is missing, empty, or unreadable

A `TASKS.md` with no backing plan cannot be traced to a phase or step. This is
not row 6's "clean, resume" case - resuming without a plan means the loop
engine's phase 1 (`Select`) has nothing to join a task back to, and a task
built without that join reads later as an undocumented addition
(`../../fulcrum-loop-engine/SKILL.md`, phase 1 table). Do not resume. Report the
mismatch and ask whether to reconstruct `plan.md` from `TASKS.md`'s content or
whether `plan.md` was lost and needs to be regenerated from source material.

### `.fulcrum/` present, no `JOURNAL.md`, or an empty one

Cannot be a resume - there is no prior session to resume. Treat as if this
were the first session against an already-scaffolded repo: read
`project.md` and `TASKS.md` directly, and hand off to
`../../fulcrum-loop-engine/SKILL.md` at phase 1 with no crash-recovery step. Note
the anomaly (a scaffolded project with no journal is itself unusual) in the
handoff rather than silently proceeding as if it were routine.

### Source material present alongside an existing app

Both row 2 and row 3's conditions look true at once (source material exists,
and so does an app). Prefer row 3 - `../../fulcrum-gap-analysis/SKILL.md` - since
an app that already exists is the stronger signal that a build already
happened; treat the source material as gap analysis's requirements input
rather than triggering a second `fulcrum-solution-init` pass over an app that
is already live. State this preference explicitly in the handoff so a human
can override it if the source material actually describes a *different,
unbuilt* app.
