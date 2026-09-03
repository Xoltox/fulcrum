# Recovery playbook for interrupted turns

Four distinct interruption shapes. Diagnose which one before reacting — the
correct recovery differs for each, and applying the wrong one wastes a run or
starts a competing one.

## 1. Transport-level auth expires mid-turn

Distinct from the Mentor session token — this is the connection's own
authentication, and it has **no in-session recovery path.** [VERIFIED]

Recovery: reconnect out of band (re-authenticate the transport), then **poll
the same orphaned run** — do not start a competing turn on the same scope.
The server-side turn kept running through the transport gap; only your
ability to observe it was interrupted. Confirm this via the run-id durability
rule in the main skill file: if you logged the run id before the gap, you
still have it.

## 2. Orchestrator error interrupts a session after the work already completed

If an orchestrator-level error (agent killed, process crashed, dispatch
failed) interrupts a session *after* the underlying turn had already reached
a terminal state server-side, do not "resume" a session purely to run a
check-only turn — that spends a turn to learn something you can get for
free.

Recovery: check the app **revision number**, and re-verify live (screenshot
or equivalent runtime check per `../../odc-verification/SKILL.md`). If the
revision reflects the expected work, it landed; if not, treat it as a normal
incomplete turn and continue per the granularity and staleness rules in the
main skill file.

## 3. A resume attempt without a token

A resume/continue call made with no session token is **always rejected.**
This is routine, expected behavior — not an error to chase or retry
around. Fetch or re-derive a valid token per the token-rotation rule in the
main skill file ("Run-id durability and orphaned runs"), then resume normally.

## 4. A permission-classifier block on publish

A publish call can be blocked outright by a permission classifier,
independent of anything OutSystems-side — no OutSystems error shape applies
to it, and Mentor's own reporting will not explain it. [VERIFIED] This kind
of block has resolved after re-authentication in the past — **do not assume
every occurrence is a permanent restriction.**

Recovery: confirm the underlying auth is healthy, then retry once. If it
recurs after a clean retry with healthy auth, stop and report — do not
iterate trying to route around a policy denial; see the hard-stop list in
`../../odc-unattended-guardrails/SKILL.md`.

## Cross-cutting rule for all four

Never let an interruption become a reason to start a second turn or a second
publish covering the same scope while the first might still be alive or
might have already landed. Check state (run-in-flight signal, revision
number, rendered app) before creating any new mutating call. This is the same
discipline as the run-id durability section of the main skill file — applied
here to the recovery case instead of the happy path.
