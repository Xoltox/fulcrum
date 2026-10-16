# The micro profile

A lighter `.fulcrum/` for a small engagement: **one app, about five or fewer steps,
no BRD or other source material to triage.** The full profile (brief, tenant probe,
specs, `HANDOFF.md`, build-pattern log) is sized for a multi-app, multi-phase build
and is overhead here. The signal is a small app that the "plan must exist on disk" pre-flight
would push into `fulcrum-solution-init`, where the user instead hand-writes a one-page
plan and collapses `.fulcrum/` to a few files. `[SINGLE-OBSERVATION]` The micro profile makes that collapse legitimate and keeps the parts that
crash recovery and oscillation detection depend on.

## Who chooses it

The router proposes it when its signals match (`../../fulcrum/references/detection-procedure.md`,
row 0 and heading "Proposing the micro profile"); **the user confirms.** Never auto-pick: the user may know the ask will
grow, and a profile chosen for them is a scope decision taken without them. Record the
confirmation in `DECISIONS.md` (`Decider: user`). A declined proposal routes by the
ordinary ladder.

## Files

| File | Micro profile | Why |
|---|---|---|
| `project.md` | **mandatory** | Identity, app, mode, posture - the router reads mode from it |
| `plan.md` | **mandatory**, from `../templates/plan-micro.md` | Satisfies the guardrails pre-flight "plan on disk"; the `Step` join target |
| `TASKS.md` | **mandatory** | Current truth; the loop engine selects from it |
| `JOURNAL.md` + `journal/<session-id>.md` | **mandatory** | Resume and oscillation queries read the index; the session file holds the `started` lines crash recovery needs |
| `RUN-IDS.md` | **mandatory** | An unrecorded run id is unpollable after a crash, at any scale |
| `DECISIONS.md` | created at the first decision | The profile confirmation and the create-vs-shell choice are decisions, so in practice it exists from the start |
| `external/<system>.md` | required per external system the app consumes | Must exist before the consuming step starts |
| `HALT.md` | written on halt, never only prose | `resume-and-halt.md`, heading "The halt record" |
| `lease.<app>.json` | runtime, uncommitted, written by the orchestrator for each Mentor dispatch | One Mentor session per app holds at every scale |
| `tenant-profile.md` | read if one is found (lookup rule in `../../fulcrum-solution-init/templates/tenant-profile.md`, section 11); not probed for in full, but procedure step 4 records `portfolioKey` and the environment keys in its section 11 | The session-start tool preflight still runs; a driver creating the app needs `portfolioKey` from its brief; record any tenant fact learned in the profile, not in `DECISIONS.md` |
| `brief.md`, `DOMAIN.md` (the root brief file solution-init scaffolds), `HANDOFF.md`, specs, build-pattern log, `runs/`, `checkpoints/` | not used | The plan's Acceptance and Steps sections replace the brief and the specs; `TASKS.md` plus the last `JOURNAL.md` row is the resume point |

Keep the session-file split even when the engagement is small. A single combined
per-action log was the field workaround, and it lost the index row that answers
"what was in flight" in one read. Two short files cost less than one reconstruction.

## Procedure

1. The router has proposed micro and the user confirmed. Ask, in the same batch, the
   app-creation choice: Mentor creates the app, or the user makes a shell from the
   standard template for Fulcrum to load. Neither is the default -
   `../../fulcrum-solution-init/SKILL.md`, step 2. Record both answers in
   `DECISIONS.md`.
2. Write `project.md`, then `plan.md` from `../templates/plan-micro.md` with the user,
   then `TASKS.md` rows for the steps, then empty `JOURNAL.md` and `RUN-IDS.md`.
3. For every external system the plan names, write `external/<system>.md` from
   `../templates/external-system.md`, or park the consuming step until it exists.
4. Run the session-start tool preflight (`../../fulcrum/references/tool-preflight.md`),
   then call `env_list` (read-only; the orchestrator may make this call itself) and
   record `portfolioKey` and the environment keys in `tenant-profile.md`, section 11
   (lookup rule there; write a new one in `.fulcrum/` only if none is found). Briefs
   pass both to the driver. Then hand to `../../fulcrum-loop-engine/SKILL.md`. Write ordering, ownership and
   halt rules are exactly the full profile's: `../SKILL.md`.

## Leaving the micro profile

Promote to the full profile when any of these becomes true: a second app, more than
about five steps, a step that fails the right-sizing test and cannot be split within
the five, or source material arrives that needs triage. Stop at a step boundary,
record the promotion in `DECISIONS.md`, and route to
`../../fulcrum-solution-init/SKILL.md` with `plan.md` as its source material. Keep
every existing file; the micro set is a subset of the full one, so nothing is
migrated. Growing a micro plan past its size quietly is how a demo turns into an
unplanned build.
