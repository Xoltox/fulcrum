# Question bank

Questions organised by **what they unblock downstream**, not by topic. Each carries
concrete options and, where one exists, a recommendation with its reason.

Do not ask all of these. Pick against the readiness set in
`sufficiency-and-stopping.md`, skip anything the supplied material already answers, and
respect the fifteen-question ceiling. Rewrite the wording into the user's own domain
language — a question echoing their nouns gets a better answer than one echoing ours.

All examples use neutral nouns (`Order`, `Shipment`, `Customer`). Everything here is
design, `[UNVERIFIED]`.

## Batch shape

A batch is up to five questions in **one** turn, numbered, each with options. Close the
batch with: "Answer what you can. 'Not sure' is a fine answer — I will mark it open
rather than guess." That sentence is load-bearing: without it a user invents an answer
rather than look unprepared, and the invention is written down as a requirement.

---

## Unblocks: persona and scope — readiness 1

**Who uses this, and what are they trying to get done?**
Options where the answer stalls: one kind of user doing one job / several kinds of user
with different jobs / one job that passes between people.
Follow-up if a handoff is described: who hands to whom, and what changes at the handoff.

**Is there anyone who only looks and never changes anything?**
A read-only persona is the cheapest thing to get wrong late, because it is usually
discovered only when someone's screen writes something it should not.

## Unblocks: roles and per-screen access — readiness 2, 3

**Name every kind of person who signs in.** Ask for names, not counts.

**For each screen or area — who can see it, and separately, who can change anything on
it?** Ask read and write separately, always. A single "who has access" question gets
one answer covering both, and the two are what make role inversion visible: a user
reaching the screen that records their own outcome and being able to write it.

**Is there anything one role must NOT see?** Options: another person's records / money
or pay figures / anything before it is approved / nothing.
Negative access statements are the ones users never volunteer and the ones with the
worst consequences when missing.

**Recommend when unsure:** start with the smallest role set that distinguishes the
access rules actually named. Reason — a role is cheap to add and expensive to split
once screens reference it.

## Unblocks: the data model — readiness 4, 8

**What are the main things the system keeps track of?** Nouns only. Push back on verbs.

**For each: what do you need to know about one of them?** Attributes, in their words.

**How do these connect — one `Order` has many `Shipment`s, or one of each?** State the
candidate relationship back and let them correct it. Users correct a wrong statement
readily and generate a correct one poorly.

**Does one record ever point at the same kind of record twice for different reasons?**
Example: a record naming both a requester and an approver, both of whom are `Customer`s.
Ask this explicitly — it is legal, commonly needed, and almost never volunteered.

**Which of these has a fixed list of possible values?** Example: a `Shipment` status.
Recommend a fixed list when the user can enumerate it without hesitating. Reason —
enumerable sets become static entities, and a wrong guess here means a model change and
a publish later instead of data entry.

## Unblocks: the target platform — readiness 5

**Where will people use this — at a desk, or on a phone while doing something else?**
Options: desk mostly / phone mostly / both, but one matters more.
**Recommendation:** name the one that matters more and design for it.
**Reason, state it:** reversing this later means re-creating the app and rebuilding
every screen — see `../../fulcrum-solution-init/SKILL.md`, step 2.

## Unblocks: the screen inventory — readiness 6, 7

**Walk me through one typical case from start to finish.** A narrative produces a
screen inventory more reliably than asking for a screen list, because users describe
what they do and not what they look at.

**For each screen you have named — does anyone type into it, or is it just for
looking?** Ask per screen, and write the answer per screen. A spec that omits "display
only" gets a build agent that hardcodes text
(`../../fulcrum-solution-init/templates/spec-template.md`, FUNCTIONAL BEHAVIOR), and a
transactional screen needs a stronger proof rung than a read-only one
(`../../fulcrum-verification/SKILL.md`, proof ladder).

**What happens when there is nothing to show yet?** Empty states are omitted from
almost every brief and are the first thing a demo hits.

## Unblocks: integrations — readiness 9

**Does anything here have to talk to another system?** Options: pull data in / push
data out / both / nothing, it stands alone.
For each named: which direction, what data, and does it happen while someone waits or
on a schedule. "While someone waits" versus "on a schedule" changes what gets built, so
ask it in those words rather than "synchronous or asynchronous".

**Is there a system of record for any of this that is not this app?** If yes, that
entity is probably read-only here, which changes both the model and the screens.

## Unblocks: seed data — readiness 10

**If I showed you this working next week, what would have to already be in it for the
screen to look real?** Ask for counts and shapes: how many `Order`s, spread over what
period, in which states.

**Recommendation:** enough rows to make every state visible at least once, and no more.
**Reason:** seeding is its own multi-turn phase and precedes any screen that reads it
(`../../fulcrum-seed-data/SKILL.md`), so every extra shape is real cost.

**Are any real values available, or is everything invented?** Determines whether seeding
is a load step or an authoring step.

## Unblocks: acceptance and phase one — readiness 11, 12

**For the main screen, what would you look at to tell me it is right?** Drive to
something countable or readable: a number on screen, a row appearing after a save, a
name in a list. If the answer is "it looks right", convert it —
`observable-requirements.md`.

**If only one part of this existed and worked, which part?** That is phase one. Do not
say "phase one" back; naming the plan is `fulcrum-solution-init`'s.

## Unblocks: assets — readiness 13

**Is there a logo, brand colours, or any images this must use — and who can upload
them?** State that uploads are a person's job, not the agent's: there is no
asset-upload path over the ODC MCP surface
(`../../fulcrum-solution-init/references/source-triage.md`, heading "Assets are a human
handoff — plan for it"), so an unowned asset is an unowned blocker on every step that
consumes it.

---

## Recording as you go

Each answer becomes a brief line with a `Confidence` value the moment it is given —
`held` if they arrived with it, `elicited` if the question produced it, `assumed` if
you proposed it and they did not object. Deciding provenance later is guesswork; the
distinction is only reliable at the moment of the answer.

Every accepted recommendation and every rejected alternative is a `DECISIONS.md`
record. Shape: `../../fulcrum-project-state/SKILL.md`, heading "DECISIONS.md closes an
existing hole".
