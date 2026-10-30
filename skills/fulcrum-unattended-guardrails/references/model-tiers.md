# Model tiers - vocabulary, policy and resolution

Skills and briefs use tier names only. A tier name is not a model; this file says how
one becomes a model at run time. Concrete vendor names never appear in a skill.

## The three tiers

| Tier | Job | What it is for |
|---|---|---|
| `deep-reasoning` | Derivation | Ingesting raw source artifacts, deriving a solution plan from ambiguous input, decomposing a solution into apps/agents/workflows, sizing phases and steps, authoring specs, authoring skills |
| `workhorse` | Execution and orchestration | Every build session after init: reading state, writing subagent briefs, dispatching, reading reports, driving Mentor turns, verification, seed data, publish sequencing |
| `poller` | Waiting | Every wait loop: `mentor_get_run` polling, `publish_status` polling (key from the "Publish" run), any long-running job supervision, any "sleep then re-check" cycle |

## The policy - phase-based

1. **Project init only:** `deep-reasoning`. This is the one phase whose output is
   a *derivation* - the plan, the decomposition, the specs. Getting it wrong is
   paid for in every session afterwards.
2. **Every session after init:** `workhorse` orchestrator. Not "usually" - by
   default. Build sessions execute a written plan; they do not derive one.
3. **All poll loops and wait states:** `poller`.
4. **Init on `workhorse` is an acceptable budget option.** It is a real
   downgrade, not a free one: expect the plan to need more correction turns. It
   is still better than skipping the planning phase.

Set the tier **explicitly on every dispatch**. Subagents otherwise inherit the
session's tier, and inheritance is what makes a tier policy silently untrue. Never
raise a tier to break a stuck bug: `../SKILL.md`, heading "Never escalate model tier to
break a bug".

## Resolution - how a tier becomes a concrete model

First match wins:

1. **A project-level override**: `tier overrides` in `.fulcrum/project.md`, or the
   project's own rules or handoff document. Budget and vendor access are per-engagement,
   so a project may pin tiers to something other than the default.
2. **`MODEL-TIERS.local.md`**, written once by the install interview and kept beside
   the installed skills. Available models and per-subagent capability are per-machine
   and per-harness. It is generated and machine-local: never commit it to a project
   repository.
3. **The vendor mapping** in `MODEL-TIERS.md` in the Fulcrum repo, when that repo is at
   hand. It is not installed.
4. **If none of the above resolve, ask the user.** Do not guess a model name.

## No per-subagent model

If the harness cannot assign a different model per subagent, all three tiers collapse
to the one model it runs. There is then no discardable poller, so the cadence floor is
90 s for every poll, because every poll persists in the orchestrator's own context:
`../../fulcrum-mentor-turns/SKILL.md`, heading "5. Polling".
