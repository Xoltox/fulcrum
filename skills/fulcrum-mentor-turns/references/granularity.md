# Turn granularity — the full incident numbers

Detail behind `../SKILL.md`, section 1. Read there for the rule; this file is
the evidence.

## The monolithic-turn failure

[VERIFIED] A single turn carrying 8 elements ran ~50 minutes, went
event-silent for the last ~28 minutes, was evicted from the run registry, and
lost its session token. Terminal result, validation state and refreshed token
were gone permanently — a liveness probe had confirmed the run was still
alive shortly before eviction, so this was not a misread. Read back
afterward: **zero of the 8 elements had applied.**

## The same scope, granular

The same scope, rebuilt as **9 granular turns** (786–5,057 characters each),
landed all 9 — every one `change_applied: true`, 0 errors — in **25m44 total
wall clock, faster than the single failed monolithic attempt.** Decomposing
the scope also surfaced a real spec defect (a foreign key resolved from the
wrong natural key) that the monolithic version would have silently absorbed
as a null foreign key on every affected row.

## Two more stalls, separately

[VERIFIED] Two other steps' full-spec single-turn attempts stalled and were
abandoned — one twice — before the same scope landed cleanly as batched turns
(8 turns in one case).
