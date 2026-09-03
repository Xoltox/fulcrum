# Tenant capability probe

One read-only pass at project start. Resolves every fact that varies by tenant, licence
or platform version, and writes the answers into `tenant-profile.md` in the project repo.
Read this when starting step 3 of `../SKILL.md`.

**Why it exists.** A tenant-varying fact baked into a skill or a spec is a permanently
wrong instruction. The contract is: skills reference the profile, the probe resolves the
profile, and nothing else asserts a tenant fact.

## Rules for the whole probe

1. **Read-only.** No mutating operation, and specifically nothing that can republish or
   bump a revision. In the reference corpus a test-setup operation invoked with a real
   environment key republished a fork into the live revision chain and overwrote a clean
   build. `[VERIFIED]` If an operation's read-only status is unclear, do not run it here.
2. **Record evidence, never assertions.** Every profile row carries *what you observed*,
   not *what Mentor said*. See "Evidence format".
3. **A Mentor denial is not evidence.** `[VERIFIED]` See "Probing for a UI block".
4. **Run the liveness gate first.** Everything else is worthless if Mentor is not
   actually reading the app.
5. **Re-probe on a stale profile.** If the profile is older than the platform's release
   cadence, or a downstream session hits a contradiction, re-run the affected row rather
   than editing it from memory.

## 0. Mentor liveness gate — run before anything else

**Failure mode.** In a tenant-wide outage, every run returned terminal status
`succeeded`, `attempted_change` false, and a summary stating that no application was
selected. This happened against an unrelated app too, so "it works on the other app" is
not a control. `[SINGLE-OBSERVATION]`

**Why the obvious gate does not work.** A read-only prompt *correctly* returns
`attempted_change` false. So that field cannot distinguish a healthy read-only turn from
a dead one.

**The gate.** Send a cheap read-only prompt against the real target app asking Mentor to
name what it can see — screens, entities, or both. Pass only if the returned summary
**names real content that exists in that app**. Concretely:

- Pass: the summary lists screen or entity names you can independently confirm exist.
- Fail: the summary is generic, says no application was selected, describes a different
  app, or names nothing.

On fail: **halt the engagement.** Do not begin a build, do not retry in a loop, do not
attempt a workaround. Record the failure and the time. Re-gate before any later session
resumes; a session that starts on a dead backend burns budget producing nothing while
every status field reads healthy.

Repeat this gate at the start of **every** session, not only at init. It costs one cheap
read-only turn. Turn mechanics for the probe turn itself:
`../../odc-mentor-turns/SKILL.md`.

## 1. `db_query` liveness

**Probe.** Issue the most trivial query the surface accepts — a constant select that
cannot depend on schema or data.

**Read.** Does it return a row?

- Rows returned → a model-layer path to live row data exists. Record it.
- Empty result for even a trivial constant select → **there is no model-layer path to
  live row data on this tenant at all.** Not "the query was wrong". Record this plainly,
  because it changes the whole verification budget: reading rows then costs a temporary
  diagnostic endpoint, which is roughly two Mentor turns and two revisions per seed step.

Record the actual response shape you saw, not a summary of it. Verification consequences
live in `../../odc-verification/SKILL.md`; seed consequences in `../../odc-seed-data/SKILL.md`.

## 2. Which UI blocks exist — and their real inputs

Probe each of: `Modal`, `BottomSheet`, `ActionSheet`, `Sidebar`, `Accordion`, `Wizard`.
Add any block a phase-one spec depends on.

### Probing for a UI block

**Do not ask Mentor whether a block exists.** In the reference corpus a block Mentor
reported absent was later found to exist *and* to be public. `[VERIFIED]` A denial
conflates "not in my index" with "not on the tenant", and the two are different.

Instead: **attempt to reference the block and read what lands.** Build the smallest thing
that uses it, then read the resulting model or rendered output.

| Observation | Record as |
|---|---|
| The block is placed and its inputs appear in the model | Exists. Record the exact input property names and types you saw. |
| A validation or model error naming the block | Absent, with the exact error text quoted. |
| Mentor substitutes a different block silently | Absent-in-practice. Record what it substituted — that substitution is what specs will get. |
| Mentor says it does not exist but nothing was attempted | **Unresolved.** Attempt the reference before recording anything. |

**Input properties matter as much as existence.** A block that exists with different
input names than a spec assumes fails at build time. Record the property names verbatim.

## 3. Icon font family and name casing

Probe: place one icon and read back what the model holds.

Record: the icon font family in use, the exact casing convention for icon names
(`ArrowRight` vs `arrow-right` vs `arrow_right`), and one confirmed working example.
Casing is not cosmetic — a wrongly cased name yields a blank or a fallback glyph with no
error, so specs must quote names in the confirmed convention.

## 4. Available `ModelFeature_*` flags

Probe: read the flags the tenant exposes.

Record the list. Flags reported "removed on this tenant" in the reference corpus were
tenant state, not platform truth. `[VERIFIED]` A spec depending on a flag that is absent
must be re-specified, not retried, so resolve this before authoring phase-one specs.

## 5. Date and meridiem format-token behaviour

Probe: format one known date/time through the tenant's formatting path and read the
output string.

Record: which tokens produced which output, and specifically whether a meridiem token
renders as expected, renders empty, or renders literally. Record the observed output
string verbatim. Specs then quote the confirmed token, and no build agent guesses.

## 6. Can server actions be marked public?

Probe: attempt to mark a trivial server action public and read whether the property
takes.

Record yes/no plus the error text if no. If no, exposing logic outside the app needs a
REST method instead, which is a step in the plan and a cost in the budget — notably for
seeding and for diagnostic row reads.

## 7. Mentor backend identifier

Probe: read whatever identifier the Mentor surface reports for the backend serving this
tenant.

Record it. Behaviour changes between backends, so a profile without this cannot be
compared against a later one, and a regression cannot be attributed.

## 8. Mentor prompt-length ceiling

Probe: establish the ceiling the tenant actually enforces, by the cheapest available
route — a documented or reported limit, or a bounded escalation of prompt size on a
throwaway read-only turn.

Record the number and how you obtained it. Spec turn blocks are sized against this, so
an unknown ceiling means every long spec risks a truncation whose failure mode is a
partial build reported as success. Turn-splitting rules live in
`../../odc-mentor-turns/SKILL.md`.

## 9. Target app identity

Not tenant capability, but it belongs in the same file because the same class of mistake
follows from getting it wrong.

Record the target app's **exact identifier**, its application type, and its current
revision at init. Record any other app on the tenant with a confusingly similar display
name, and mark it explicitly as not the target. A stale scaffold with a near-identical
name is how a session builds into the wrong app. `[VERIFIED]`

Also record here the answer to the mobile-application-type question from step 2 of
`../SKILL.md`: whether Mentor can add screens to an app of the type you intend to use, as
observed on this tenant.

## Evidence format

Every row in `tenant-profile.md` carries five fields. A row missing any of them is not
resolved.

| Field | Meaning |
|---|---|
| Fact | What was being resolved |
| Answer | The resolved value, stated as a value not a hedge |
| Probe | Exactly what was done to find out |
| Observed | What actually came back, quoted |
| Date | When, plus the backend identifier from row 7 |

An answer of "Mentor said X" is not an answer. Either you attempted the thing and read
the result, or the row is unresolved.

## Exit criteria

- The liveness gate passed against the real target app.
- Every section above has a row in `tenant-profile.md` with all five fields.
- Any unresolved row is marked **UNRESOLVED** with what blocked it and which planned step
  it gates.
- No mutating operation was run and no revision was bumped.
