# Turn granularity - the full incident numbers

Detail behind `../SKILL.md`, section 1. Read there for the rule; this file is
the evidence.

## The monolithic-turn failure

[VERIFIED] A single turn carrying 8 elements ran ~50 minutes, went
event-silent for the last ~28 minutes, and was evicted from the run registry.
Its terminal result and validation state were gone permanently - a liveness
probe had confirmed the run was still alive shortly before eviction, so this
was not a misread. Read back afterward: **zero of the 8 elements had
applied.**

## The same scope, granular

The same scope, rebuilt as **9 granular turns** (786-5,057 characters each),
landed all 9 - every one reporting `changeApplied: true` with 0 errors - in
**25m44 total wall clock, faster than the single failed monolithic
attempt.** (`changeApplied` alone is a weak signal: `mcp-surface.md`,
heading "Completion signals".) Decomposing the scope also surfaced a real
spec defect (a foreign key resolved from the wrong natural key) that the
monolithic version would have silently absorbed as a null foreign key on
every affected row.

## Two more stalls, separately

[VERIFIED] Two other steps' full-spec single-turn attempts stalled and were
abandoned - one twice - before the same scope landed cleanly as batched turns
(8 turns in one case).

## Turn economics

Nominal budget per step: **1 build turn + up to 2 fix turns**, plus the
Publish turn. Granular building does not break the cap: a build pass of up to 4
short turns in one step counts as the one build turn; past 4, split the step
(`../../fulcrum-unattended-guardrails/references/halt-conditions.md`, heading "The
turn cap"). Disclose overages, never absorb them. Heavy steps have run 14
turns and ~46 minutes including publishes - a ceiling, not a problem signal.
Granular turns ran ~5-7 minutes; flag past **~7 minutes** as split-further.
A long answer costs thousands of tokens to drain; ask for short answers.

## Publish budgeting

Publishes serialize, so budget wall clock for them. A mid-flight publish is a live
outage; freeze publishing before a demo. Production needs explicit user
confirmation. A promotion (`deploy_start`) takes the `Release` build key from
`build_list`, not `env_app`'s `buildKey`, which is the Debug build
(`mcp-surface.md`, heading "Publishing").
