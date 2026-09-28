# Fulcrum

Fulcrum is a harness-agnostic skill set for driving OutSystems ODC Mentor
through long, largely unattended build sessions with real guardrails. It is
derived from a 47-step production build and its incident log: the rules here
encode what actually broke, and what proved a change had actually landed.

This file is the entry point on harnesses without skill auto-triggering.

## Entry point

**Load `skills/fulcrum` first.** It detects engagement state from the
filesystem and the tenant — no `.fulcrum/`, source material present, an app
already existing, a halt, an open task — and dispatches to the right skill
itself. It never asks the user to self-classify. In almost every case this is
the only routing decision you need to make.

## Manual routing table (fallback)

Use this table instead of the router only when you already know exactly which
skill applies and want to skip detection — for example, resuming mid-task with
the target skill already named, or an expert-mode user invoking a skill
directly. Otherwise, load `skills/fulcrum`.

| Your situation | Load |
|---|---|
| Unsure which skill applies, or resuming an engagement | `skills/fulcrum` |
| Have an idea for an app but nothing written down yet | `skills/fulcrum-discovery` |
| Starting a new engagement: raw BRD, Figma/Stitch export, mockups, or screenshots, not yet a plan | `skills/fulcrum-solution-init` |
| An app already exists and you need to know how it compares to its requirements, what is missing, or what to build next | `skills/fulcrum-gap-analysis` |
| Where durable project state lives — `.fulcrum/` file set, the session lease, the halt record | `skills/fulcrum-project-state` |
| Working through the task list — selecting, dispatching, polling, verifying, recording, advancing | `skills/fulcrum-loop-engine` |
| About to issue a Mentor turn, chunking a spec, unsure of session vs conversation, or a turn didn't land | `skills/fulcrum-mentor-turns` |
| Building or editing a screen, aggregate, repeater, link, icon, date expression, REST integration, static entity, chart, or overlay | `skills/fulcrum-engine-traps` |
| Need to prove a change actually works, not just that publish was clean | `skills/fulcrum-verification` |
| Seeding, resetting, or debugging sample/demo data | `skills/fulcrum-seed-data` |
| Running many steps unattended, delegating to subagents, or defining stop/escalate rules | `skills/fulcrum-unattended-guardrails` |

## Non-negotiables

These hold even if no skill file is ever loaded:

- Never publish from a Mentor session whose model state you have not just
  verified — a stale model reverts completed work while the revision number
  still advances.
- One Mentor session at a time **per app** (concurrency across different apps
  is allowed; the ceiling is unpublished and may change server-side).
- Aggressive orchestration is the default, not an advanced option: delegate
  poll loops and read-only inspection to subagents; keep judgement and
  verification verdicts in the orchestrator. Mutating work is depth 1 always.
  See `skills/fulcrum-unattended-guardrails` for the rules.
- One subagent depth level, with a single narrow exception: a subagent may
  spawn one nested poller when its own tier is expensive and the phase is
  long, and that poller does nothing but wait and report. No other nesting.
  See `skills/fulcrum-unattended-guardrails`.
- The orchestrator never calls Mentor, publish, REST, or gate scripts itself
  — it dispatches.
- Zero validation errors and a clean publish prove nothing about rendering
  or logic.
- A schema that loads is not a tool that dispatches — tool availability is
  probed, not assumed, and the result is recorded in `tenant-profile.md`.
- A halt record is never resumed past without a new human decision.
- Project state lives in `.fulcrum/` in the project repository, never in the
  installed skills.
- Stuck twice on the same problem means stop and report. Never escalate
  model tier to break a stuck bug.
- Disclose overruns and deviations. Never absorb them silently.
- Citing a Fulcrum skill means applying a named rule from it — never attribute
  a standard, benchmark, or conclusion to Fulcrum that its text does not state.
- Capture a run identifier durably before the first wait.
- Poll cadence depends on who pays for it: with a discardable poller, 45s for
  answer-back turns and 90s for turns that mutate the model; with no
  delegation, a 90s floor for everything. See `skills/fulcrum-mentor-turns`.

## Tenant-varying facts

Facts that vary by tenant, licence, or platform version (UI-block
availability, icon font, and similar) live in the
project's own `tenant-profile.md`, produced once by `fulcrum-solution-init`.
Skills reference that file — they never hardcode the answer.

## Model tiers

See `MODEL-TIERS.md` for the tier vocabulary (`deep-reasoning`, `workhorse`,
`poller`) and the vendor mapping. The tiers are deliberately vendor-neutral;
map them to whatever models your harness gives you access to.
