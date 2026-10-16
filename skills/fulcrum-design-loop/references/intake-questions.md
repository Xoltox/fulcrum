# Intake questions - batches B and C

Exact text for the design loop's up-front questions. Batch A (mode if `project.md`
is absent; profile "design loop or full path") belongs to the router
(`../../fulcrum/references/guided-mode-interaction.md`) and is not repeated here.

Every question below is a **user-policy choice**: asked, never defaulted, recorded in
`DECISIONS.md` with `Decider: user`. A guessed answer here is a scope, security or
cost decision taken without the user. (Fulcrum rule)

## Batch B - phase 0, one batch

Guided mode: ask with the options and the recommendation shown. Expert mode: the same
questions, answerable in the invocation (form below); any question left unanswered is
still asked - nothing is defaulted. Never one question per turn.

1. **App creation.** "Should Mentor create the app (`<name>`), or will you create a
   shell from the standard template for me to load? No default: Mentor-created is
   faster; your shell lets you choose name, template and portfolio."
2. **Screen access.** "Who may open each screen? (a) all require sign-in, any role;
   (b) `<listed>` public, the rest sign-in; (c) per role - name roles and screens. No
   default: a wrong guess locks everyone out or exposes data."
3. **Fidelity bar.** "How close must screens match? (a) structural - blocks, regions,
   data, icons, copy; colour and spacing drift goes to a backlog; (b) visual - also
   colours, typography, spacing and sizes, judged same-at-a-glance. Pixel-exact is not
   offered: no instrument proves it on ODC. Recommended: (a) for screenshots/concepts
   with approximate colours, (b) for Figma/HTML/TSX with exact values."
4. **Render-compare instrument.** "(a) a browser a delegated agent can drive (I check
   it works); (b) you send a screenshot of each screen when asked; (c) skip - structure
   only, every visual check untested. Recommended: (a) if available."
   - Only if (a) and a screen needs sign-in: "May the renderer use the generated sample
     personas in Development? The first click registers a real identity-provider user
     with a role. Or you sign in for it." (Mode b and c in
     `../../fulcrum-render-check/SKILL.md`, heading "Sign-in modes - in order of
     preference".)
5. **Evidence in the repo.** "Commit (a) copies of your design under
   `.fulcrum/design/source/` and (b) render screenshots, or keep either out of the
   repository? They can hold real data." This also answers render-check's screenshot
   question; do not ask it twice. Fulcrum never adds an ignore entry on its own.
6. **Assets.** "The design shows `<logo / N images>`; there is no MCP image upload.
   (a) you upload them in Studio when the chrome step asks; (b) text wordmark and
   neutral placeholders; (c) leave slots empty." The upload claim rests on the
   `mentor_request_upload` row (allowed extensions, no image format) in
   `../../fulcrum-mentor-turns/references/mcp-surface.md`, heading "Tool families".
7. **Form factor** - only if the source is ambiguous: "Desktop Reactive Web, or
   phone-width layout in a Reactive Web app? (Mobile type refused Mentor screens once
   `[SINGLE-OBSERVATION]`.)" Source of the caveat:
   `../../fulcrum-solution-init/SKILL.md`, step 2.
8. **MCP re-probe** - only while `mcp-surface.md` says "Re-probe owed since": "(a)
   re-probe on a throwaway app first; (b) accept the risk for this run, recorded.
   Recommended: (a)."

### Dependencies

| Answer | Consequence |
|---|---|
| Q1 shell | P1.01 is a `manual` row (user creates the shell) then a load; the app key comes from the user |
| Q1 Mentor | P1.01 brief carries `portfolioKey` from `tenant-profile.md` section 11 |
| Q2 | Access lines in every `screens/<SID>.md` header; render sign-in modes per screen |
| Q3 | `manifest.md`, Policy line **Fidelity bar**; severity of `token` and `spacing` diffs (`render-compare.md`) |
| Q4 (a) | Browser preflight runs at phase 0; a failed preflight re-asks Q4 with (a) removed |
| Q4 (b) | Tier B: one `manual` row per screen per round, parked `Blocked on: the user` |
| Q4 (c) | Tier C: every screen `unproven`; the report leads with render-only classes |
| Q5 | `manifest.md`, Policy line **Commit design source / render screenshots**; render briefs say whether screenshots may be written |
| Q6 (a) | A `manual` upload row on P1.03 |
| Q8 (a) | No mutating step until the re-probe snapshot exists |

### Expert pre-answer form

```
design-loop: create=<mentor|shell:<app key>> access=<all-signin|public:<S..>|roles:<role>=<S..>;...>
  bar=<structural|visual> render=<browser|user|skip> personas=<yes|no|n/a>
  commit-source=<yes|no> commit-screens=<yes|no> assets=<studio|placeholder|empty>
  form=<desktop|phone|n/a> reprobe=<first|accept|n/a> go=<preapproved|ask>
```

Parse it, show what was read in one line, and ask only for what is missing or
unparseable.

### Recording

One `DECISIONS.md` record per answer, `Decider: user`, `Affects` naming the concrete
artifacts (the app, the screens by `SID` and name, `design/source/`). Each D-id goes on
its `manifest.md` Policy line (Q1-Q8; Q7 and Q8 `-` when not asked) and all of them in
the **Decisions** section. Block choices, data model, KPI sources, chart types, token
values and turn decomposition are agent decisions (`Decider: agent`), recorded once
the gate passes.

## Batch C - end of phase 3

Summary, then one question:

- screens (SID, name, archetype), entities, seed rows, steps (5 + N, plus every split
  screen step; over 11 steps the engagement promotes to the full profile - say so);
- estimated turns per step: guard 1 + consult 1 + build <= 4 + publish 1 + fix <= 2;
- estimated wall clock from `../../fulcrum-mentor-turns/references/granularity.md`
  (about 5-7 min per granular turn) - an estimate, not a promise;
- render tier (A/B/C), fidelity bar, open risks from `gate.md` (second FAILs,
  `unresolved` blocks, icon names flagged for the probe).

"Go, change something, or stop?"

Budget accounting and the 0.65 / 0.85 thresholds:
`../../fulcrum-unattended-guardrails/references/budgeting.md`, unchanged. Expert mode
may pre-approve batch C in batch B (`go=preapproved`); the summary is still written to
`JOURNAL.md`. Promotion beyond Development is never part of "go". (Fulcrum rule)
