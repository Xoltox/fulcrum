# Template - `.fulcrum/plan.md` (micro profile)

The plan for a micro engagement: one app, about five or fewer steps, no BRD. The
orchestrator fills this directly with the user; no `fulcrum-solution-init` pass, no
spec files, no `HANDOFF.md`. When and how the micro profile applies, and which
`.fulcrum/` files it requires: `../references/micro-profile.md`.

It is still `plan.md`: same file name, same `P<phase>.<NN>` step ids, so `TASKS.md`
`Step` joins to it and the guardrails pre-flight item "the plan exists on disk" is
satisfied by it. Keep it to one screen. If a section will not fit, the engagement is
not micro - see "Leaving the micro profile" in the reference.

---

<!-- fulcrum-schema: plan-micro v1 -->

# Plan (micro) - \<solution name\>

**Profile:** micro - confirmed by the user on \<date\>, `DECISIONS.md` \<D-NNN\>
**App:** \<app identifier, or the intended name until created\> - \<asset type\>
**App creation:** \<Mentor creates it / user-made shell loaded\> - `DECISIONS.md` \<D-NNN\>

## Goal

\<Two lines: what the app must let someone do, and how the user will know it works.\>

## Acceptance

Observable statements only - something a person or an instrument can see, click or
count. Never "works as expected".

1. \<e.g. Signed-in user opens Claims and sees every claim from the external system\>
2. \<...\>

## External systems

\<`-` if none. Otherwise one line per system: stem, and the path
`.fulcrum/external/<system>.md`. That file must exist before the step that consumes
the system starts.\>

## Steps

| Step | What it produces | Turn kinds | Proof (acceptance items) |
|---|---|---|---|
| P1.01 | \<e.g. the Claim entity and its static Status values\> | build | 1 |
| P1.02 | \<...\> | build, verify | 1, 2 |

At most about five rows. Each step must pass the right-sizing test in
`../../fulcrum-solution-init/references/decomposition-and-sizing.md`, heading
"The right-sizing test".

## Standing rules for this engagement

\<Rules the user stated that every step must obey, e.g. "never write to app X".
One line each. `-` if none.\>

## Out of scope

- \<What this engagement explicitly does not build.\>
