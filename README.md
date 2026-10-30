# Fulcrum

**A harness-agnostic skill set for driving OutSystems ODC Mentor through long, largely unattended build sessions - with real guardrails.**

Derived from multiple zero-shot, one-shot, multi-shot, and long-running ODC builds and their incident/build logs: the traps here are field-observed, not theoretical.

![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)
![Status: Experimental](https://img.shields.io/badge/status-experimental-orange.svg)
![Harness: Agnostic](https://img.shields.io/badge/harness-agnostic-lightgrey.svg)

> [!NOTE]
> Derived from several ODC builds across different tenants and build styles. The traps are field-observed, but the skill set has been exercised on one harness only; other harnesses are untested.

## Table of contents

- [Why this exists](#why-this-exists)
- [The skills](#the-skills)
- [Quickstart](#quickstart)
- [How it is meant to be used](#how-it-is-meant-to-be-used)
- [The standard path](#the-standard-path)
- [Design lanes](#design-lanes)
- [Agent assets: the honest limits](#agent-assets-the-honest-limits)
- [What is untested](#what-is-untested)
- [Non-negotiables](#non-negotiables)
- [Model tiers](#model-tiers)
- [Conventions](#conventions)
- [Repository layout](#repository-layout)
- [Manual install](#manual-install)
- [Status and provenance](#status-and-provenance)

## Why this exists

A nine-rule oneshot build guide, developed for a rehearsed conference demo
(Developer Days Bengaluru), held up on stage but was not enough for the
longer, unattended, many-step builds that came after - the kind where nobody
is watching to notice a Mentor turn quietly go sideways at step 23 of 47.

- **Platform success signals are unreliable in both directions.** Zero validation errors and a clean publish are compatible with blank rows, empty repeaters, unrendered icons, and corrupted content. Model-layer checks are structurally blind to whole defect classes.
- **Tenant-varying facts are read, asked at intake, or recorded on the first real row that needs them**, then referenced thereafter - never a spike. Differences in available UI blocks, icon fonts, meridiem tokens, and Mentor backend identifiers are never hardcoded. Tool-specific facts live, dated, in `skills/fulcrum-mentor-turns/references/mcp-surface.md`.
- **Every rule carries its failure mode explicitly.** Measured finding: prompts that named *why* a construct fails stopped the failure recurring. Prompts that only said "don't" did not.
- **Claims carry explicit evidence strength tags:** `[VERIFIED]` (observed multiple times), `[SINGLE-OBSERVATION]` (real but not generalized), `[UNVERIFIED]` (inferred only), `[TENANT]` (deferred to the profile), or `[SCHEMA]` (asserted by the vendor's own MCP tool documentation, not observed live).
- **Hand-restated rules degrade over a long build.** These rules are packaged as skills so the same logic runs unmodified across many sessions, on any harness.
- **A combined Mentor turn crashed mid-execution.** Splitting it into smaller, separate turns fixed the crash, at the cost of added round-trip time - the origin of the turn-granularity rules in `fulcrum-mentor-turns`.

## The skills

| Skill | Owns | When it fires |
|---|---|---|
| `fulcrum` | The router and entry point: detecting engagement state from the filesystem and tenant, resuming, mode selection, asking `Rigor`, guided-mode question discipline, dispatching to the right skill | Any OutSystems, ODC or Mentor work. Load this first on any harness without skill auto-triggering. It routes; it performs no Mentor turn, verification, or planning itself. |
| `fulcrum-discovery` | Interviewing a user who has an idea but no written requirements; producing the brief that `fulcrum-solution-init` ingests | Before any plan exists and nothing is written down yet. |
| `fulcrum-solution-init` | Ingesting source material; decomposing into apps, agents, workflows; emitting the task graph; asking `Rigor`; read-only tenant checks; scaffolding repo and specs | Once per project, before any Mentor turn. Run on deep-reasoning tier. |
| `fulcrum-design-loop` | One design source (screenshot, concept image, mockup, Figma frames, HTML or TSX) for one app of about six or fewer screens: build lanes (image, Studio, text spec), capture into a spec of real OutSystems UI blocks, the block-mapping gate, step decomposition, render-compare against the source with a bounded fix loop | When the router proposes it for one design and one app and the user confirms, or per app from `fulcrum-solution-init` for a visual or code source. |
| `fulcrum-gap-analysis` | Assessing an app that already exists against the requirements it was meant to satisfy: build provenance, requirement-to-artifact traceability, classifying gaps vs drift vs stale requirements vs undocumented additions vs unfalsifiable requirements, remediation sequencing | When an app already exists (generated or inherited) and you need to know where it stands against its requirements before planning further work. |
| `fulcrum-mentor-turns` | Turn granularity and decomposition; prompt shape and ceiling; session reuse vs fresh session; staleness guard before mutations; polling cadence (rate depends on whether a discardable poller absorbs the cost); run-id durability; publish sequencing | Before issuing any `mentor_start_session` / `mentor_prompt` call and during turn-by-turn execution. |
| `fulcrum-engine-traps` | Construct-indexed trap registry: aggregates, repeaters, links, icons, dates, REST integrations, static entities, charts, overlays, wizards, theming, agents, workflows, sample sign-in | When building or editing any screen component or model element. |
| `fulcrum-verification` | Proof obligations; the gates G0 to G3 and the rigor table; which instrument catches which defect class; visual capture and comparison; diagnostic REST endpoint pattern for live data; what platform signals do and do not mean | Before marking any build step done. After publish. When changes seem not to land. |
| `fulcrum-render-check` | Rendering published screens in a browser: preflight, sign-in modes (anonymous, generated sample personas, user hand-off), render timing, evidence capture, security observations | After a publish passes the gate, for any step that adds or changes a screen, and for access checks. |
| `fulcrum-seed-data` | Idempotent loaders; natural keys; relative timestamps; static-entity identifiers; reset and teardown paths | Before building any screen that reads from data. |
| `fulcrum-demo` | The demo script format (`.fulcrum/demo-script.md`), the readiness checklist, the optional scripted in-app tour | Preparing a demo, and the demo script row of a `demo` rigor build. |
| `fulcrum-unattended-guardrails` | Stop conditions; fix-turn caps; halt-and-report rules; subagent depth and delegation; context and call budgeting; checkpoints and handoff discipline; Mentor concurrency locks; model tier policy | Load before the first dispatch of any long unattended session. |
| `fulcrum-project-state` | The `.fulcrum/` file contract: file set and schemas, append-only vs rewritten discipline, crash-idempotent write ordering, the one-session-per-app lease, the decision record, the halt record | Whenever any Fulcrum skill needs to read or write durable project state. |
| `fulcrum-loop-engine` | The iteration mechanism: select the runnable frontier, precondition/staleness check, dispatch parallel lanes, poll, verify, record, advance; the bounded fix-loop; oscillation and stall detection; per-iteration budget accounting | Running through the task list - "work through the tasks," "run the next task," "resume the loop." |

## Quickstart

> [!IMPORTANT]
> Prefer installing through your coding agent - it runs the install interview that records which models serve which tier. A manual copy skips that interview entirely.

Point your coding agent at this repository and say:

```
Install Fulcrum from this repo (use the latest released tag, not the
default branch) following INSTALL.md.
```

Your agent knows where its own skills directory lives, and `INSTALL.md` walks it through a short interview to resolve model tiers and wait-primitive support. Install from a released tag, not the tip of the default branch - a tag is a revision someone reviewed and froze.

For harnesses without skill auto-triggering, `AGENTS.md` is the entry point: it routes by situation to the named skill.

**Making it fire on its own.** Three layers, in `INSTALL.md` under "Automatic triggers":

1. Skill descriptions lead with the words a user types, including "use Mentor to" and a BRD in the folder. Nothing to install.
2. One conditioned line in a project or workspace instruction file, never at user scope. Recommended. The install asks, because it writes a file you own.
3. An opt-in hook (Claude Code, Node, one file): hints on a `.fulcrum/` directory or on `outsystems`, `odc`, or `mentor` with `.fulcrum/` present, silent otherwise. It never blocks. Not installed by default; a hook is a command that runs every session, so the install shows it and asks.

## How it is meant to be used

1. **Load `fulcrum`, the router, first.** It looks at the filesystem and the tenant - no `.fulcrum/`, source material present, an app already existing, a halt, an open task - and dispatches to the right skill itself. You do not choose between solution-init and gap-analysis by hand; the router works that out from what it finds.

   - **No plan and nothing written down** routes to `fulcrum-discovery`, which interviews the user and produces the brief `fulcrum-solution-init` ingests.
   - **Source material present, no app yet** routes to `fulcrum-solution-init` on the deep-reasoning tier. It produces the plan, specs, `tenant-profile.md`, and project repo scaffold. This phase is expensive but happens once.
   - **An app already exists** routes to `fulcrum-gap-analysis` - a first-class entry point, not a repair path for something that went wrong. It applies equally to fresh generator output (the platform's web app-generation route optimises for speed over depth, so large gaps there are expected and normal) and to an inherited mature app assessed at any time. It establishes where the app stands against its requirements; remediation then proceeds through the normal spec-and-turn path below.
   - **`.fulcrum/` already present** routes to resume via `fulcrum-loop-engine`, or reports a halt untouched - see `fulcrum-project-state` for what that directory holds.

2. **Every session after init.** Run on the workhorse tier. `fulcrum-loop-engine` reads the written spec and task list and executes step by step, driving Mentor turns per `fulcrum-mentor-turns`. Do not re-derive the plan; the plan is already written.

3. **Polling and wait loops.** Run on the poller tier. All `mentor_get_run` polling, `publish_status` polling, and long-running supervision happens on the cheapest available model.

On a harness without skill auto-triggering, load `AGENTS.md` first - it names `fulcrum` as the entry point and carries a manual fallback table for when you already know which skill applies.

Tiers are vendor-neutral - see [Model tiers](#model-tiers) below for the mapping and rationale.

## The standard path

The plan is a module graph, not a line of stages. Parallelism is the point: one Mentor session per app, as many apps as the frontier allows.

- **Module graph.** `fulcrum-solution-init` splits the solution into apps, agents and workflows and emits a task graph: `TASKS.md` rows with `App`, `DependsOn` and `Batchable`. Foundation rows run first and serially, lanes fan out per app, and they join at integration, with gate rows last. No spike rows: an unknown is asked at intake or tried on the first real row, which fails fast.
- **Lanes.** Each app is a lane with the same inner order: base, UI, logic, polish. `fulcrum-loop-engine` runs the whole runnable frontier in parallel, and the slowest lane gates nobody. Work that needs no Mentor session (renders of a published revision, seed design, the demo script) runs alongside.
- **Rigor dial.** `demo`, `pilot` or `production`, asked at init in every mode, never defaulted or inferred. It sets depth of evidence only, never safety and never posture. Two of the field builds overspent because depth was never chosen.
- **Gates.** G0 publish gate, G1 runtime check, G2 blind pass by a separate verifier, G3 per-row proof. Which gate runs when is one table in `skills/fulcrum-verification/SKILL.md`, heading "Gates and rigor"; it is not restated here.
- **User-action rows.** What only a person can do (a Studio shell, a role grant) is a `manual` row, and a row waiting on a user parks only its dependents.

## Design lanes

`fulcrum-design-loop` asks one lane per app:

| Lane | Who builds | Carries the design by |
|---|---|---|
| `image` (recommended) | The Mentor driver | Uploaded images on `mentor_prompt`, at most 3 per prompt |
| `studio` | You, in Studio Mentor, from a work order | Images fed to Studio's image input |
| `text` | The Mentor driver | Region-by-region anatomy; the most turns |

The image lane reads a picture and builds from it, on a new app and on an existing one. Only simple screens were tried: complex layouts and real data are `[UNVERIFIED]`, so the text lane stays complete. An attachment is read by Mentor; it does not become an app resource, so a logo or file still needs its own path. Render-compare against the source runs on every lane.

## Agent assets: the honest limits

Fulcrum can plan and drive an agent asset, but it cannot promise you a publish.

- **A publish can be refused.** The text names a "Standalone Agent" entitlement. The term is undefined in the vendor docs, so Fulcrum quotes it and never says which licence fixes it. Refusal changed over time on the same asset, and the error count does not predict it.
- **A refused publish has no key and no `OS-*` code, and a retry repeats it.** The row parks, you are told the verbatim text, and every other lane keeps moving.
- **The shell comes from Studio**, as a `manual` row: Mentor-built shells were not reliable.
- **Studio cannot rescue a refused turn.** It cannot see a harness turn that was never published, so that work is gone with the session. The row keeps the exact prompt as a replay work order; that replay has never been run.
- **A new agent can take hours to become referenceable**, overnight in one case, so its consumer rows start `blocked`.
- **Almost nothing inside an agent is readable** through `context_*`. Model binding and flow internals rest on Mentor read-back or Studio, so a claim about them is belief, and only a real call proves runtime.

Details: `skills/fulcrum-engine-traps/references/agents.md`.

## What is untested

Stated so you do not assume otherwise. `ROADMAP-capabilities.md`, heading "Open live evaluations", tracks each one.

- **The v0.6 path has not run as a whole.** Its parts come from field builds and probes on throwaway apps; no build has gone end to end on the module graph and rigor dial, and the rigor table is unmeasured.
- **Live evals were never run** for the design loop's render-compare and capture end to end. Trigger evals exist (`evals/`): six routing cases passed on Haiku, Sonnet and Opus on 2026-10-30, with no tenant, so they show a prompt lands in the right skill and nothing about build quality.
- **The sample sign-in recipe has not been run end to end.**
- **The scripted tour has not been built by any run.**
- **The agent replay work order has not been run.**
- **One prompt with three images beat three prompts once, on simple screens.** It has not been repeated on a real design, so it is a starting batch, not a rule.
- **The trigger hook has only seen sample stdin**; it has never run in a live session.
- **Other harnesses.** Everything has been exercised on one harness only.

## Non-negotiables

These hold even if no skill file is ever loaded (from `AGENTS.md`):

- Never publish from a Mentor session whose model state you have not just verified - a stale model reverts completed work while the revision number still advances.
- One Mentor session at a time **per app** (concurrency across different apps is allowed; the ceiling is unpublished and may change server-side). The plan is a task graph: the loop runs the whole runnable frontier in parallel, one driver per app, and the slowest lane gates nobody. `[SCHEMA]` Mentor handles one prompt at a time per session: a `mentor_prompt` call issued while a prior prompt is still running is silently ignored, not rejected with an error.
- `Rigor` (`demo`, `pilot`, `production`) is asked of the user, never defaulted or inferred, and it changes depth of evidence, never safety or posture.
- Do not plan a spike or probe row to test a platform capability. Ask at intake or try it on the first real row, which fails fast: spikes consume hours, publish throwaway revisions, and prove what that row would prove anyway.
- Aggressive orchestration is the default, not an advanced option: delegate poll loops and read-only inspection to subagents; keep judgement and verification verdicts in the orchestrator. Mutating work is depth 1 always.
- One subagent depth level, with one exception: the Mentor-driver role may spawn exactly one nested poller that only waits and reports.
- The orchestrator never calls Mentor, issues the "Publish" turn, polls `publish_status`, calls REST, or runs gate scripts itself - it dispatches.
- Zero validation errors and a clean publish prove nothing about rendering or logic.
- A schema that loads is not a tool that dispatches - tool availability is checked by read-only calls, not assumed, and the result is recorded in `tenant-profile.md`.
- A halt record is never resumed past without a new human decision.
- Project state lives in `.fulcrum/` in the project repository, never in the installed skills.
- Stuck twice on the same problem means stop and report. Never escalate model tier to break a stuck bug.
- Disclose overruns and deviations. Never absorb them silently.
- Citing a Fulcrum skill means applying a named rule from it - never attribute a standard, benchmark, or conclusion to Fulcrum that its text does not state.
- Capture a run identifier durably before the first wait.
- Poll cadence depends on who pays for it: with a discardable poller, 45s for answer-back turns and 90s for turns that mutate the model; with no delegation, a 90s floor for everything.

> [!WARNING]
> The orchestrator never calls Mentor, publish, REST, or gate scripts itself. If you find yourself doing so at the top level, you've broken the delegation contract - see `skills/fulcrum-unattended-guardrails`.

## Model tiers

Three vendor-neutral tiers, mapped to whatever models your harness gives you access to. `MODEL-TIERS.md` has the vendor mapping and measured cost evidence; `skills/fulcrum-unattended-guardrails/references/model-tiers.md` has the policy and resolution order.

| Tier | Job | What it is for |
|---|---|---|
| `deep-reasoning` | Derivation | Project init: ingesting sources, deriving the plan, decomposing into apps/agents/workflows, sizing phases, authoring specs |
| `workhorse` | Execution and orchestration | Every session after init: reading state, dispatching, driving Mentor turns, verification, seed data, publish sequencing |
| `poller` | Waiting | Every wait loop: `mentor_get_run` polling, `publish_status` polling, long-running job supervision |

A tier resolves to a concrete model in this order: a project-level override, then `MODEL-TIERS.local.md` (written by the install interview), then the documented defaults, then - if nothing resolves - ask the user rather than guess.

## Conventions

All skills are bound by the authoring contract in `CONVENTIONS.md`. Read it before writing or editing a skill.

Two headline rules:

- **Harness agnostic.** No vendor model names (use the tier vocabulary), no harness tool names, no harness-specific frontmatter in skill bodies.
- **Platform truth by default.** Every rule is general ODC/Mentor truth, not incident history from one build. Tenant-varying facts go through `tenant-profile.md`, never hardcoded. Rules state their failure mechanism.

<details>
<summary>Full authoring contract detail</summary>

- **Hard rule 1 - harness agnostic.** Never name a harness-specific tool as the required instrument; say what capability is needed and let the agent map it. Never name a model - use tier vocabulary. ODC MCP tool names (`mentor_start_session`, `mentor_request_upload`, `mentor_prompt`, `mentor_get_run`, `mentor_get_event`, `publish_status`, `env_app`, `app_revisions`, `context_*`) are allowed since they are the ODC surface itself, written bare with no harness-specific prefix. No harness-specific frontmatter (`allowed-tools`, slash-command syntax, `$ARGUMENTS`) in a skill body. Harness quirks go in `HARNESS-NOTES.md`, never in a skill.
- **Hard rule 2 - platform truth by default.** Strip all project nouns; keep the consequence, drop the anecdote. Tenant-varying facts live in `tenant-profile.md`, read, asked, or recorded on the first real row, and skills reference the profile rather than hardcoding the answer.
- **Hard rule 3 - state the mechanism, not just the ban.** A rule that cannot state what breaks is not ready to write.
- **Hard rule 4 - mark evidence strength** on any claim that is not directly observed: `[VERIFIED]`, `[SINGLE-OBSERVATION]`, `[UNVERIFIED]`, `[TENANT]`, `[SCHEMA]`.
- **Skill file layout:** `SKILL.md` thin (target under 220 lines) plus `references/*.md` loaded on demand, and `templates/` where applicable.
- **Frontmatter** is a portable subset only: `name`, `description`, and `metadata` holding `version` and `requires` (bare `version`/`requires` keys are rejected by spec-only surfaces). No `allowed-tools`, `license` or `compatibility`.
- **Cross-references** are relative paths (`../fulcrum-verification/SKILL.md`), never section-number anchors.
- **Tone:** terse, imperative, evidence-first. No hedging, no filler, no praise. A rule per line where possible. The reader is an agent mid-task with limited context - every line must earn its place.

Skill boundaries (one topic, one owner) and the full canonical-facts list (polling cadence math, subagent depth exception, gap-analysis finding taxonomy, coverage-denominator rule) are in `CONVENTIONS.md` itself - read it directly rather than through this summary before editing any skill.

</details>

## Repository layout

<details>
<summary>Full tree</summary>

```
fulcrum/
  skills/
    fulcrum/
      SKILL.md                    # Router and entry point
      references/                 # Detection procedure, guided-mode interaction, tool preflight, mode and posture
    fulcrum-discovery/
      SKILL.md
      references/                 # Question bank, observable requirements, sufficiency/stopping
      templates/                  # Brief template
    fulcrum-solution-init/
      SKILL.md                    # When to run, what it does
      references/                 # Depth docs: decomposition, repo scaffold, tenant probe, source triage, tool availability
      templates/                  # Handoff and spec templates; tenant-profile skeleton
    fulcrum-design-loop/
      SKILL.md
      references/                 # Intake, build lanes, capture recipes, design spec format, block map, OutSystems UI reference, archetypes, render-compare, interop, third-party notice
      templates/                  # Manifest, screen, fidelity and report templates
    fulcrum-gap-analysis/
      SKILL.md
      references/                 # Provenance, inventory, traceability matrix, finding classification, coverage/diagrams, repair-vs-rebuild
      templates/                  # Gap report template
    fulcrum-project-state/
      SKILL.md
      references/                 # File schemas, lease and concurrency, resume and halt
      templates/                  # project.md, JOURNAL.md, journal-session, TASKS.md, DECISIONS.md
    fulcrum-loop-engine/
      SKILL.md
      references/                 # Iteration contract, iteration budget, oscillation and fix-loop
    fulcrum-mentor-turns/
      SKILL.md
      references/                 # Granularity, posture, prompt scaffolds, polling, turn recovery
    fulcrum-engine-traps/
      SKILL.md
      references/                 # Per-construct trap detail: aggregates, repeaters, dates, etc.
    fulcrum-verification/
      SKILL.md
      references/                 # Proof instruments, visual verification, diagnostic patterns, runtime telemetry, evidence tags
    fulcrum-render-check/
      SKILL.md
      references/                 # Sign-in modes, evidence and report
    fulcrum-seed-data/
      SKILL.md
      references/                 # Idempotent loader pattern
    fulcrum-demo/
      SKILL.md                    # Demo script format, readiness, scripted tour
    fulcrum-unattended-guardrails/
      SKILL.md
      references/                 # Halt conditions, budgeting, checkpoints, delegation rules, model tiers
  agents/
    README.md                     # Agent roles: why, tool classes, harness mapping
    roles/                        # Harness-neutral role specs: poller, mentor driver, verifier, renderer, capturer
    claude-code/                  # Claude Code adapters, installed by install.sh
      hooks/                      # Opt-in trigger hook, copied only with install.sh --hooks
  scripts/
    gen-osui-ref.py               # Maintainer-only: refreshes the OutSystems UI reference; never run at install
  install.sh                      # Portable installer: skills/, Claude Code agents, opt-in hook
  AGENTS.md                       # Entry point for harnesses without skill auto-triggering
  CONVENTIONS.md                  # Authoring contract (binding)
  MODEL-TIERS.md                  # Tier vocabulary and vendor mapping
  INSTALL.md                      # Agent-driven install contract
  HARNESS-NOTES.md                # Observed per-harness behaviour (not requirements)
  ROADMAP-capabilities.md         # Capability roadmap
  LICENSE                         # MIT
```

</details>

## Manual install

<details>
<summary>For a person installing without an agent's help</summary>

1. **Find your skills directory.** Claude Code reads from `~/.claude/skills/`. Other harnesses commonly use `~/.agents/skills/` by convention - check your harness's own docs if unsure.
2. **Copy all fourteen skill directories in whole**, not just their `SKILL.md` files: `fulcrum`, `fulcrum-discovery`, `fulcrum-solution-init`, `fulcrum-design-loop`, `fulcrum-gap-analysis`, `fulcrum-project-state`, `fulcrum-loop-engine`, `fulcrum-mentor-turns`, `fulcrum-engine-traps`, `fulcrum-verification`, `fulcrum-render-check`, `fulcrum-seed-data`, `fulcrum-demo`, `fulcrum-unattended-guardrails`. Almost all carry a `references/` directory beside `SKILL.md`, and some a `templates/` directory - a skill missing its `references/` is broken even though it looks installed.
3. **Or run the installer.** `install.sh [target-dir] [--dry-run]` at the repo root copies `skills/` into `target-dir` (defaults to `~/.claude/skills`) and the Claude Code agents into `~/.claude/agents` (`--no-agents` skips them). `--dry-run` prints what it would do without changing anything. It never deletes anything, but it can overwrite: a skill file that differs is skipped unless `--force`, a marked agent file that differs is overwritten by a plain run, including a local `model:` edit. `--hooks` also copies the opt-in trigger hook and prints its settings snippet; it never edits a settings file.
4. **Verify the install.** Confirm each of the fourteen directories exists at the target path, whole, and that your agent's skill listing (or equivalent discovery mechanism) picks them up.
5. **Update later** by re-running step 2 or 3 against a newer tag. Both touch only files this repo ships, and both can replace your edits to them: step 2 overwrites anything copied, and step 3 needs `--force` for skill files that changed, so read its `--dry-run` list first.

> [!NOTE]
> A manual install gets no install interview. The interview is what decides which model serves which tier (`deep-reasoning`, `workhorse`, `poller`) and whether your harness supports per-subagent model assignment - installing by hand means you must make those calls yourself. Read `MODEL-TIERS.md` for what to decide and the resolution order, then record your answers in a `MODEL-TIERS.local.md` file beside the installed skills - never edit the answers into the skill files themselves or into `MODEL-TIERS.md`.

</details>

## Status and provenance

Background: written up by Parth Sharma (Senior Solution Architect,
OutSystems) after a talk at Developer Days Bengaluru -
[the post](https://dd26.parth.gg/blog.html).

Derived from several ODC builds across different tenants and build styles (zero-shot, one-shot, multi-shot, long-running) - the oneshot stage build plus error and build logs from other, separate builds. The traps are field-observed but the skill set has been exercised on one harness only; other harnesses are untested.

This skill set complements and does not replace the separate `outsystems-mcp-skills` catalog, which covers app bootstrap, architecture dependency analysis, and deploy workflows. Fulcrum layers long-run build discipline and construction correctness on top.

Licensed under MIT - see `LICENSE`. `skills/fulcrum-design-loop` condenses and modifies reference material from OutSystems' `outsystems-design-to-app` skill (MIT, Copyright (c) 2026 OutSystems); its notice and the list of derived files are in `skills/fulcrum-design-loop/references/THIRD-PARTY-NOTICE.md`.
