# Fulcrum — model tiers

The single source of truth for model tiering. This is the **only** file in Fulcrum
that names a concrete model. Skills use the tier names — `deep-reasoning`,
`workhorse`, `poller` — and nothing else.

## The three tiers

| Tier | Job | What it is for |
|---|---|---|
| `deep-reasoning` | Derivation | Ingesting raw source artifacts, deriving a solution plan from ambiguous input, decomposing a solution into apps/agents/workflows, sizing phases and steps, authoring specs, authoring skills |
| `workhorse` | Execution and orchestration | Every build session after init: reading state, writing subagent briefs, dispatching, reading reports, driving Mentor turns, verification, seed data, publish sequencing |
| `poller` | Waiting | Every wait loop: `mentor_get_run` polling, `publish_status` polling, any long-running job supervision, any "sleep then re-check" cycle |

## Vendor mapping

Pick the row for your vendor. Where a vendor ships several generations, the tier
is the *family position*, not a specific version string — take the current
member of that family.

| Tier | Anthropic | Google |
|---|---|---|
| `deep-reasoning` | Opus | Gemini Pro |
| `workhorse` | Sonnet | Gemini Flash |
| `poller` | Haiku | Gemini Flash-Lite |

Other vendors: map by the same shape — a frontier reasoning model, a
mid-tier general model that is roughly an order of magnitude cheaper on output,
and a small fast model for loops. If a vendor has only two tiers, run `poller`
work on the cheapest available and keep the loop bodies trivial.

## The policy — phase-based

1. **Project init only:** `deep-reasoning`. This is the one phase whose output is
   a *derivation* — the plan, the decomposition, the specs. Getting it wrong is
   paid for in every session afterwards.
2. **Every session after init:** `workhorse` orchestrator. Not "usually" — by
   default. Build sessions execute a written plan; they do not derive one.
3. **All poll loops and wait states:** `poller`.
4. **Init on `workhorse` is an acceptable budget option.** It is a real
   downgrade, not a free one: expect the plan to need more correction turns. It
   is still better than skipping the planning phase.

Set the tier **explicitly on every dispatch**. Subagents otherwise inherit the
session's tier, and inheritance is what makes a tier policy silently untrue.

## Reasoning effort — a separate dial

Tier and effort are independent. Effort is what output tokens are made of, and
output volume is the cost driver, so effort is the second lever.

- **LOW effort for build agents executing a written spec.** [VERIFIED] Two
  consecutive build steps in the source build each ran five Mentor turns,
  first-try, with zero fix turns, against a spec that told them exactly what to
  do. That work does not need high effort.
- **HIGH effort for spec authoring and plan derivation.** That is the real
  derivation work. Keep it high even when the tier is `workhorse`.

## Measured evidence

From the source build, at the point the policy changed [VERIFIED]:

| | |
|---|---|
| Spend on `deep-reasoning` tier | **$153.24** |
| Spend on `workhorse` tier for equivalent work | **$4.97** |
| `deep-reasoning` OUTPUT tokens | **1.2m** |
| Cache read vs true input | 188.9m vs 465k |

Readings:

- **The driver was output-token volume, not cache-read rate.** Cache hit rate was
  already near-perfect on both tiers. There is nothing left to win on caching —
  the levers are output volume and output price.
- **Implied cost per unit of identical work: ~2.7x, not the 5x** a list-price
  comparison suggests. The headline ratio overstates it because the tiers do not
  emit the same number of output tokens for the same task.
- Output volume came from subagent thinking plus tool-call payloads, at 33–75
  tool calls per agent.

Caveat: this is one workflow, one tool mix, measured once. The direction is
solid; treat the multiplier as a calibration starting point.
[SINGLE-OBSERVATION] on the exact 2.7x.

## History — the flat single-tier policy

The source corpus contains a standing rule reading, verbatim, "SONNET ONLY, NO
EXCEPTIONS (budget constraint, hard, not a preference)", including an explicit
ban on using the `deep-reasoning` tier for spec authoring or for a stuck bug.

**That is recorded here as history, not as the rule.** It was written after the
build had already exhausted its budget mid-way, at which point every tier
decision collapsed into "the cheap one". It is a budget-exhaustion artifact.

What survives from it, and is genuinely the rule:

- Do **not** escalate model tier to break a stuck bug. Repeated attempts at the
  same tier repeat the same wrong guess, and a higher tier mostly buys a
  more expensive version of the same guess. Require a diagnostic step instead.
  See `skills/fulcrum-unattended-guardrails/references/halt-conditions.md`.
- "Stuck twice → stop and report to the user" is not a budget measure. It stays.
- Keep the "correct my briefing — a correction beats agreement" line in every
  subagent prompt. The source build credits that single line with surfacing most
  of the corrections to its own documented claims — it is a **prompt
  mechanism, not a model-tier effect**, and it does not become unnecessary at a
  higher tier.

## Resolution — how a tier becomes a concrete model

A tier name (`deep-reasoning`, `workhorse`, `poller`) is not itself a model.
At runtime it resolves to one, in this priority order, first match wins:

1. **A project-level override**, if the project's own rules or handoff
   document specifies one. Budget and vendor access are per-engagement, so a
   project is allowed to pin tiers to something other than the default.
2. **`MODEL-TIERS.local.md`**, written once by the install interview and kept
   beside the installed skills. Available models and per-subagent capability
   are per-machine and per-harness, so this is the second-most-specific
   source.
3. **The documented defaults in this file** — the vendor mapping above.
4. **If none of the above resolve** — no project override, no local file, no
   applicable default row — ask the user. Do not guess a model name.

### The install interview must not edit installed files

This is a hard constraint, not a style preference. The install interview
(`INSTALL.md`) records its five answers into a separate, generated
`MODEL-TIERS.local.md`. It must never rewrite the installed skill files or
this file. An installer that edits installed content makes every future
update fight the user's own edits, and lets the deployed copy silently drift
from source — exactly the failure this file exists to prevent for model
names generally.

`MODEL-TIERS.local.md` is generated and machine-local. Do not commit it to a
project repository — regenerate it per install instead.

### `MODEL-TIERS.local.md` template

```markdown
# Model tiers — local resolution

Recorded: <date>
Harness: <harness name, as it identified itself>

1. Per-subagent model assignment supported: <yes / no>
2. deep-reasoning tier: <model>
3. workhorse tier: <model>
4. poller tier: <model>
5. Native context-free wait primitive available at any depth: <yes / no>
```

### Degradation path

If question 1 comes back "no" — the harness cannot assign a different model
per subagent — do not leave the file implying three distinct models are in
play. Record the fact plainly, collapse all three tiers to the single model
the harness actually runs, and point at `CONVENTIONS.md`'s canonical polling
rule: with no discardable poller, the cadence floor becomes 90 seconds for
every poll, not just build turns, because every poll then persists in the
orchestrator's own context.
