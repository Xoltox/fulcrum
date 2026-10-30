# Build lanes - image, Studio, text spec

How a screen gets from the design into the app. Asked at batch B (Q8), one lane per
app, recorded on the `manifest.md` Policy line **Build lane**. Changing lane is a user
decision, and a lane stop may offer it. Tool facts:
`../../fulcrum-mentor-turns/references/mcp-surface.md`.

| Lane | Who builds | Carries the design by | Needs |
|---|---|---|---|
| `image` (recommended) | `fulcrum-mentor-driver` | `mentor_prompt` with uploaded images | An image of each screen; `attachment-upload` on the driver |
| `studio` | The user, in Studio Mentor | Images fed to Studio's image input | The user's time; a work order |
| `text` | `fulcrum-mentor-driver` | Region-by-region anatomy | A full capture; the most turns |

A source with no image takes `text`, unless a render or frame export can supply one
(`capture-recipes.md`, heading "Reference images"). Mentor reads images and builds
from them, on a new app and with `assetRefs` on an existing one `[VERIFIED]`. Only simple
screens were tried: complex layouts and real data are `[UNVERIFIED]`, so `text` stays
complete and is not retired. (Fulcrum rule)

## What each lane changes

| Phase | `image`, `studio` | `text` |
|---|---|---|
| Capture | Shared dispatch, then short-form screen files (`design-spec-format.md`, heading "Short form") | Full |
| Gate | Checks 1, 9, 12 | All twelve |
| P1.02 Theme | `:root` overrides from `tokens.md` only; `theme.css` classes wait for a fix turn that needs them | As written |
| P1.03 Chrome | Folded into the first screen step, one step fewer: the prompt names screens, access and menu labels | As written |
| P1.04, P1.05 | Before the screen steps, unchanged | Unchanged |
| P1.06+ | One step per image batch, or one Studio pass | One screen per step |
| Render-compare | Unchanged, and never skipped | Unchanged |

An anatomy exists to carry structure through text. With the picture in the prompt
nothing builds from it, and a gate-checked spec the build bypasses is cost with no
reader `[SINGLE-OBSERVATION]`. (Fulcrum rule)

Theme first because classes are not reused between prompts: a later prompt added its
own classes for its own palette `[SINGLE-OBSERVATION]`, so what must match across
screens goes in `:root` before them.

Data first because Mentor models what it sees when no entity is named: one run made a
static entity and computed its KPIs from it, another copied the KPI values as static
text `[SINGLE-OBSERVATION]`. Name the entities and the `data.md` KPI decision in the
prompt, or the same picture yields a different data model each time.

## Image lane

**Upload.** In the session that will prompt: `mentor_request_upload`, PUT the bytes,
then `attachmentRefs` on the `mentor_prompt`, at most 3 per prompt. A fourth rejects the
call, so a batch never exceeds it. An attachment is read, not stored; it does not become
an app resource (batch B Q6).

**Starting batch.** One prompt, up to 3 related images, one Publish: related means same
layout, same palette, same role. Split when fidelity drops: after a blocker or major
diff in a batch, fix it, then send the remaining screens in smaller batches.

One-run comparison, 2026-10-30, `[SINGLE-OBSERVATION]`, simple screens, not a rule:

| Shape | Prompt to published | Result |
|---|---|---|
| One prompt, 3 images | about 2m15s | High fidelity, one cosmetic defect |
| One session, 3 prompts, one image each | about 2m36s | 1.7x events, more visible defects, classes not reused |

One run each, so variance is not ruled out. Keep measuring on real designs.

**Prompt.** Short, within the ceiling in `tenant-profile.md`. The image carries layout,
colour and copy. The text carries what a picture cannot show:

```
Build these screens to match the attached images: Orders (order-list.png),
Order detail (order-detail.png). Layout, colours and text as shown.
Access: <role per batch B Q2>. Menu: Orders, Customers.
Data: bind Orders to entity Order joined to Customer, do not create entities.
KPI "Open orders": <the data.md decision>.
Do not reference any other app in the tenant.
```

**Access.** State it in the prompt. Image-built screens required a role by default and
redirected to Login, so the render owes anonymous or a sign-in
`[SINGLE-OBSERVATION]`. Never make a screen anonymous just to render it: that widens
access outside the batch B Q2 answer, and nothing later reverts it. A sign-in path:
`../../fulcrum-render-check/SKILL.md`; building one:
`../../fulcrum-engine-traps/references/sample-signin.md`.

**Fix turn.** Attach the target and the current render side by side, and lead with the
measured symptom (`render-compare.md`, heading "5. Fix rounds"). Fidelity improved in
the one run tried, but that prompt also listed the fixes in text, so the gain is not
attributable to the images alone `[SINGLE-OBSERVATION]`.

## Studio lane

The user builds screens in Studio from the images, then agents inspect and finish the
logic. `[SINGLE-OBSERVATION]` Used on two projects; reported faster, never measured.
The steps are one hand-off, in this order:

1. **Publish first.** Every agent change is published and the session closed. Studio
   cannot see an unpublished harness turn, so the user would build on an older
   revision and that turn is lost. (User-confirmed.)
2. **Write the work order** `design/STUDIO-PASS.md` from `../templates/studio-pass.md`.
3. **Hand the app to the user.** One `manual` row, parked `Blocked on: the user`. The
   orchestrator writes `lease.<app>.json` with `holder: user`, `task` that row, and a
   hold until the user answers, because two sessions never build one app and a Studio
   session is invisible to the lease. Other apps keep running; non-Mentor checks of a
   published revision still may. The TTL is never broken on expiry: ask the user.
4. **On "published":** read the live revision with `env_app` and record it as the
   observed revision in the session file: Studio work has no run id, and revisions
   jump. Release the lease.
5. **Re-inventory before any Mentor change.** A fresh session, an `inspect` row: list
   screens, actions and entities, then re-cut the remaining rows against it. Studio
   work breaks the model baseline: a plan written before the pass specifies actions
   that now exist, so a driver would duplicate them or overwrite the user's work, and a
   held session answers from its old copy with no warning. Build on what exists.
   `[VERIFIED]`
6. **Render-compare** the published revision (`render-compare.md`, heading "Studio
   lane"). A Studio pass is not proof of fidelity, and the user's "looks fine" is not
   a verdict.

Repeat from step 1 for a second pass. Passes are not capped; compare rounds are.
