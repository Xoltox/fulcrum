# Sufficiency and stopping

When to stop interviewing. Read this before asking a fourth batch, or whenever the
question "should I ask one more?" comes up.

Everything here is design, not field observation: `[UNVERIFIED]` unless tagged
otherwise.

## The readiness set

The interview is sufficient when **every item below has an answer or an explicit
`undecided` marker naming what it blocks**. Not when the brief feels complete.

The set is derived from what `../../fulcrum-solution-init/SKILL.md` cannot start
without — steps 2, 4, 5 and 6. Anything outside it is not this interview's business,
however interesting.

| # | Item | Blocking? | Gates |
|---|---|---|---|
| 1 | What the thing is, and who uses it | Yes | Everything |
| 2 | Named roles | Yes | Decomposition, every screen spec |
| 3 | Per-screen role access, read and write stated separately | Yes | Screen specs; security findings later |
| 4 | Entities, key attributes, relationships | Yes | Decomposition, entity ownership |
| 5 | Web or mobile; phone-width or desktop | Yes | Target-platform decision; irreversible cheaply |
| 6 | Screen inventory, one line each | Yes | Sizing |
| 7 | Per screen: read-only or transactional | Yes | Spec FUNCTIONAL BEHAVIOR; proof rung selection |
| 8 | Fixed value sets | No | Static-entity modelling |
| 9 | Integration points, direction and payload | No | Decomposition; may become a whole phase |
| 10 | Rows that must exist to demonstrate a screen | No | Seed phase sizing |
| 11 | One observable acceptance statement per screen | No | Acceptance checklists |
| 12 | Smallest demoable slice | No | Phase-one scope |
| 13 | Assets that exist, and who uploads them | No | Asset gates |

**Blocking** means `fulcrum-solution-init` cannot produce a usable plan without it, so
an `undecided` there halts rather than defers. Non-blocking items may ship as
`undecided` and be resolved by the step that needs them.

## The ceiling

**Three batches, five questions each. Fifteen questions is the hard ceiling.**

The mechanism, and why a ceiling rather than "ask until done":

- **Patience is a budget and it is spent linearly.** The interview competes for it with
  every later clarification the build genuinely needs. An interview that spends it all
  leaves nothing for the question that actually matters at step 30.
- **Answer quality decays with question count.** A user asked thirty questions answers
  the last ten carelessly. This inverts the naive intuition: the late answers are the
  *least* reliable, not the most, so a long interview does not converge on truth — it
  accumulates `elicited` lines with `held` formatting.
- **Context spent here is context not spent building.** Discovery runs before any
  Mentor turn exists to show for it.

### The one override

Extend past the ceiling only when a **blocking** item is still open and the user is
actively engaged. Then ask exactly that item, alone, and stop again. Never extend for a
non-blocking item, and never extend to "round out" the brief.

### What to do at the ceiling

Everything still open becomes `undecided`, with who decides and what it blocks. Say so
to the user plainly, in one line. A brief that declares five open questions is more
useful than one that quietly invented five answers — the first routes to a human, the
second routes to a build turn that produces the wrong app.

## Deliberately never asked

Asking these produces confident-sounding answers that are wrong, because the user has
no basis for them and the interview format makes declining feel unhelpful.

| Do not ask | Why | Who decides instead |
|---|---|---|
| How many apps this should be | Requires the tenant probe and entity ownership analysis | `fulcrum-solution-init`, step 4 |
| Which parts are agents versus workflows versus server actions | Platform knowledge the user does not have | `fulcrum-solution-init`, step 4 |
| Which UI blocks or widgets to use | Tenant-varying; the probe answers it | The tenant profile |
| How long it will take, or how many steps | Sizing is derived from the plan, not promised before it | `fulcrum-solution-init`, step 5 |
| Screen layout in pixel detail | Better captured from a mockup than from speech; asking invites invention | A design source, or the build |
| Anything already answered in supplied material | Reads as inattention and spends budget for nothing | Read the material first |

Under `posture: collaborative` (`../../../CONVENTIONS.md`, heading "Mode and posture") the
platform questions are Mentor's to answer anyway. Asking the user is strictly worse: it
substitutes a guess for an expert answer, and writes the guess down as a requirement.

## Signals to stop early

Stop before the ceiling on any of these. They all mean further questions return noise:

- Answers get shorter batch over batch, or shift to "whatever you think".
- The user starts answering with implementation ("just make it a dropdown") instead of
  need. They have run out of domain content and are filling.
- Two answers in one batch contradict an earlier `held` line. Stop and reconcile; a
  brief with an unreconciled contradiction is worse than a short one.
- The user asks when the building starts. Take it literally.

Stopping early is not failure. The remaining items become `undecided`, which is a
routable state, and the build produces something to react to — which elicits better
answers than any further question would have.
