# Fulcrum agent roles

Fulcrum prescribes delegation: a poller absorbs every Mentor wait, a Mentor
driver runs the turns for one app, and a blind verifier judges the result.
A renderer captures what a published screen actually shows, and a capturer turns
one design source into a design spec for the design loop. This folder ships
those five roles as definitions, so no orchestrator has to
improvise them and no user has to ask their harness to build them.

| Role | Tier | Tool classes | Job |
|---|---|---|---|
| `fulcrum-poller` | `poller` | `run-read`, `blocking-wait` | Wait on one Mentor run, drain it, report in 3 lines |
| `fulcrum-mentor-driver` | `workhorse` | `mentor-drive`, `run-read`, `published-read`, `blocking-wait`, `file-read`, `file-write-scoped`, `spawn-poller` | Drive Mentor turns for one app per a written plan step (one dispatch per step, one session inside it); ends each mutating step with its Publish turn |
| `fulcrum-verifier` | `workhorse` | `published-read`, `file-read`, `http-probe`, `blocking-wait` | Verify the live app against stated claims, blind to how it was built. Cannot render: judges rungs 6-7 from `fulcrum-renderer` evidence, else `untested`; on the design loop, compares render captures against reference images by image inspection |
| `fulcrum-renderer` | `workhorse` | `browser-automation`, `published-read`, `blocking-wait`, `file-read`, `file-write-scoped` | Render published screens (anonymous, approved sample persona, or user session) and record evidence; never types credentials, never gives the verdict |
| `fulcrum-capturer` | `deep-reasoning` (capture), `workhorse` (gate, set in the brief) | `file-read`, `file-write-scoped`, `design-source-read` | Capture one design source into the design loop's per-screen spec under `.fulcrum/design/`; in gate mode, grade a capture blind. Never drives Mentor, never publishes, never uses a browser |

## Why they exist - context cost

A general-purpose agent inherits the full tool set, the project instruction
files and every skill and agent listing before it does any work. A poller
dispatched that way has started at 50k+ tokens of context just to call one
read in a loop; a lean, tool-scoped poller definition used about 5.8k tokens
for a whole run `[SINGLE-OBSERVATION]`. Every role here is lean on purpose:
it carries only the tools its job needs, does not load project instructions,
and restates the hard rules it must follow in its own body instead of
reading skills.

## Layout

```
agents/
  roles/<name>.md         # canonical, harness-neutral role spec (edit these)
  claude-code/<name>.md   # Claude Code adapter generated from the role
```

A role spec's frontmatter carries `name`, `description`, `tier` (vocabulary
from `../MODEL-TIERS.md`), `tools` (tool classes, below), `forbidden`,
`max_turns` (a hint) and `loads_project_instructions: false`. The body is the
role's operating prompt.

Adapters mirror the role body verbatim and add a harness-specifics section at
the end. Edit the role first, then mirror the body into each adapter.

## Tool classes

| Class | Means |
|---|---|
| `run-read` | Read a Mentor run (`mentor_get_run`) and single events (`mentor_get_event`) |
| `mentor-drive` | `mentor_start_session`, `mentor_close_session`, `mentor_create_asset`, `mentor_load_asset`, `mentor_prompt`, `mentor_cancel_prompt` |
| `published-read` | `context_*`, `app_info`, `app_revisions`, `app_logs`, `app_traces`, `app_health`, `env_list`, `env_app`, `publish_status`, `publish_logs`, `auth_status` |
| `blocking-wait` | A wait that actually suspends for the requested time (verified, see `../HARNESS-NOTES.md`, "Waiting") |
| `file-read` | Read and search files; includes image inspection (looking at an image file) where a role's job needs it (verifier, capturer) |
| `file-write-scoped` | Write only the paths named in the brief (the driver: append to the session journal file and RUN-IDS; the renderer: its evidence folder only; the capturer: the `.fulcrum/design/` paths its brief names only; never the lease, the `JOURNAL.md` index or TASKS) |
| `browser-automation` | Open and navigate a page, read a DOM snapshot and page text, screenshot, click, hover, press keys, type and fill forms, upload, read console/network output. Never type a password, token, API key or other secret (a Fulcrum rule, not a tool restriction); data-changing interactions only when an assertion requires it, in Development only |
| `spawn-poller` | Start exactly one nested `fulcrum-poller` |
| `http-probe` | Outbound HTTP to the app's own endpoints |
| `design-source-read` | Read frames, variables and the layer tree from a design tool. Optional: an adapter maps it to the harness's design-tool tools or omits it, and the role then asks for frame exports |

## Mapping a role onto a harness

1. **Tier to model:** resolve the role's `tier` through `MODEL-TIERS.local.md`
   (then the defaults in `../MODEL-TIERS.md`). Set it explicitly on the
   definition; never let it inherit the session's model. The shipped Claude
   Code adapters hardcode `model:` defaults; to apply a local override, edit
   that adapter's `model:` line in the installed copy (the one allowed edit;
   `install.sh --force-agents` would overwrite it, so redo it afterwards).
2. **Tool classes to tools:** grant the harness's own tools for each listed
   class and nothing more. Deny the `forbidden` entries where the harness can.
   The renderer's adapter grants no browser tool by name: it inherits the
   session's tools, so whatever browser MCP the user has is available, and
   denies only the mutating OutSystems tools, Edit, NotebookEdit and Agent.
   The capturer's adapter also inherits (so a design-tool MCP serves
   `design-source-read`) and denies every OutSystems tool, shell, web, Edit and
   Agent; its no-browser rule is prose.
3. **Lean context:** turn off loading of project instruction files and skill
   preloading where the harness allows it.
4. **Body:** use the role body as the agent's system prompt, plus a short
   section naming the harness's concrete wait mechanism and tool names.

If a harness has no agent-definition mechanism, paste the role body into the
brief of the subagent you dispatch instead.

## Installation

- **Claude Code:** `install.sh` copies `claude-code/*.md` into
  `~/.claude/agents` by default (`--agents-dir` to change, `--no-agents` to
  skip). Agent definitions load only at session start: **restart the session
  after installing or updating them**, or the harness reports the agent type
  as not found.
- **Other harnesses:** see `../INSTALL.md`, "Agent roles". The installing
  agent builds its harness's definitions from `roles/` using the mapping above.

## Using them

Orchestrator briefs name the role (`fulcrum-poller`, `fulcrum-mentor-driver`,
`fulcrum-verifier`, `fulcrum-renderer`, `fulcrum-capturer`), not a general-purpose agent. The brief still carries the
task-specific inputs each role lists under "Inputs": ids, cadence, paths,
budget, permissions.
