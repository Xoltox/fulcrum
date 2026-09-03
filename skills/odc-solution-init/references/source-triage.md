# Source triage

How to turn a pile of source artifacts into a written brief, a deduplicated screen
inventory, and an honest asset list. Read this when starting step 1 of
`../SKILL.md`.

Governing assumption: **the source material is not a spec and its filenames mean
nothing.** Design-tool exports carry auto-generated names (`Frame 3`, `Group 17589`,
`Vector`), so nothing about the file tree tells you what any file is.

## Order of operations

Never inspect before you scan. A systematic dimension scan is a census; visual
inspection is sampling. In the reference corpus the two disagreed on how many
full-screen frames existed (67 by first-pass inspection, 87 by scan) because
inspection stopped once the picture seemed clear. `[VERIFIED]`

1. **Scan.** Read width, height, byte size, format and DPI for every file. Any
   image-metadata tool will do; a shell one-liner over the directory is enough.
2. **Bucket** by dimension and aspect (table below).
3. **Sample** each bucket — inspect enough files to characterise the bucket, then stop.
   Inspect every file only in the smallest, highest-value bucket.
4. **Deduplicate** screens into screen/flow groups.
5. **Write the brief.**
6. **Write the asset list**, with provenance and rights resolved.

Steps 1–3 parallelise cleanly across subagents by bucket. Give each subagent the bucket's
file list and the characterisation questions; do not ask any of them to plan.

## Bucket table

Dimensions below are the shape of the evidence, not thresholds to hardcode. Bucket by
what the numbers mean.

| Bucket | Signature | Usable? | What to do with it |
|---|---|---|---|
| Brand assets | Square or circular, large (512–2048 px), alpha channel | Yes, sometimes as-is | Candidate app icon / favicon / logo. Inspect every one. |
| Full-screen frames | Phone or desktop widths, tall (2–4x width) | No | The screen inventory. Sample, then dedupe. |
| Icon glyphs | Small (10–120 px), single mark | Almost never | Map to the platform icon font instead — see below. |
| Fragment crops | Odd aspect, mid-size, or very wide | No | Widget snapshots and sample-data tooltips. Reference only. |
| Blanks | Small, low byte size, uniform | No | Empty exports. Discard, but record the count. |

Expect the signal ratio to be brutal. Reference corpus: **2 of 138** files were genuinely
upload-ready brand assets. `[VERIFIED]` Plan the triage to *find those two*, not to
document the other 136.

## Two traps that produce false asset needs

- **Fused icon tiles.** A "background circle + glyph" component exported as one PNG
  cannot be recoloured or resized cleanly, so it looks like an asset and is not one.
  If the platform icon font serves the glyph, the answer is the icon widget, never an
  upload. In the reference corpus every one of 33 glyph exports mapped to a stock icon
  and **zero** were real asset needs. `[VERIFIED]`
- **A composed lockup is not a wordmark.** If the only exports containing the wordmark
  also contain a background fill and extra marks, there is no transparent wordmark to
  be had. Say so explicitly, then plan the crop as required work.

## Deduplicating to screen/flow groups

Collapse into one group:

- Filter states of one list template (six exception filters is one screen, six states).
- Collapsed / expanded states of the same list.
- Empty / populated states of the same screen.
- Tab variants only if the tabs share a single screen; separate them if each tab is its
  own screen in the target.

Keep separate: distinct steps of a wizard, and any state whose widget tree differs
rather than just its data.

Record the raw-export filenames per group in the brief. Traceability back to the source
is the only defence when a later phase needs the original picture. Reference corpus
collapsed raw screen exports to screen/flow groups at roughly **2.4x**.

## Deriving the brief when none was supplied

The brief is the domain source of truth for the whole engagement. It must contain:

- **What the thing is, and who uses it.** State the persona and its scope explicitly.
  Getting this wrong mis-shapes every entity.
- **Roles and personas**, with the evidence for each. If only one persona appears in the
  source, say so and say you are assuming single-role.
- **Core entities**, each with observed key attributes and a note on anything ambiguous.
- **Screen/flow inventory**, grouped by area, each group traced to source filenames.
- **Open questions**, split into blocking and non-blocking.

## Resolving, not deferring

An open question left open gets re-litigated by every later session. Resolve what you can
now, on your own authority, and mark it **RESOLVED** with the reasoning in one line. In
the reference corpus a modelling ambiguity (two payment views — one entity or two?) was
resolved to one entity with two views, and the resolution note is what stopped it
reopening. `[VERIFIED]`

Only leave a question open when a human decision genuinely gates work. Then say which
step it gates.

## Correcting the incoming brief

Whoever handed you the source material had a mental model of it. Triage will falsify
parts of that model. **Write the corrections down as corrections**, next to the claim they
overturn — not as quiet replacements.

Reference corpus, both `[VERIFIED]`:

- The brief assumed no usable asset existed in the export folder. Two existed.
- The brief attributed a large empty region on a screen to a missing hero image. The
  design had no hero image there; the region was a layout-anchoring bug. Fixing the
  "missing asset" would not have closed it.

The second is the more instructive shape: a **wrong diagnosis produces the wrong work
item**. Any asset need must be justified against what the app actually renders, not
against what the design looks like it needs.

## Assets are a human handoff — plan for it

There is **no asset-upload path over the ODC MCP surface.** `[VERIFIED]` External-library
upload operations carry code, not resources. So every asset must be uploaded as a proper
platform resource by a human through the portal.

Consequences for the plan, all of which belong in the plan and not in a build agent's
head:

- Any step that consumes an asset is **gated** on a confirmed upload, and must be
  sequenced *between* Mentor turns rather than inside one.
- The build agent must never work around a missing asset with a base64 data URI or an
  embedded-HTML asset. Both bloat the theme and make swapping the asset awkward, and both
  were explicitly rejected in the reference corpus.
- Record the decided upload mechanism in the repo once, so no later session re-litigates
  it.

## Output of step 1

Four artifacts in the repo:

1. The derived brief.
2. The screen/flow inventory with source traceability.
3. The asset list: confirmed needs, candidate source file per need, the preparation each
   needs, and explicit **not needed** entries with reasons.
4. A short corrections list against the incoming brief.
