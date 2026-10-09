# Screen access, security and settings

Who can reach a screen, where a credential lives, and which server-trust rules
the platform enforces. Access policy and credentials belong to the user: where
an entry says "ask", the agent asks and records the answer, it does not pick
a default.

## 1. Screen access is not what you assume after creating an app or a screen `[SINGLE-OBSERVATION]`

**Failure mode.** After a new app is created through Mentor, the template
login flow can exist while the **Login screen is non-public**, and a screen
Mentor adds can be created non-public with no way to sign in - a user hits a
dead end, while validation and publish are clean. One build hit the
non-public-Login dead end; a later probe confirmed a Mentor-created web app
ships template screens (Login, RecoverPasswordRequest, RecoverPasswordReset,
InvalidPermissions, UserProfile, ChangePassword in the Common flow) with no
explicitly configured default screen `[VERIFIED]` (one probe, live read). The
template can change, so read it, do not assume. No default screen was
explicitly configured in the probe, so the **default screen** must be set
deliberately. Mentor's read-back is not proof of access: it has claimed
"all screens are anonymous" while published state showed Login non-public
`[VERIFIED]` - where read-back and an independent instrument disagree, trust
the instrument and record it (the read-back row in `../SKILL.md`).

A new screen can also carry a role requirement nobody asked for `[VERIFIED]` -
the default-children instinct extends to screen-level *properties*, so check
the screen's own properties, not just its widget tree.

**Ask the user, do not decide:** which screens are anonymous, which require
which role, and which screen is the default. Record the answer in
`DECISIONS.md`.

**Brief, right after app creation and after every turn that adds a screen:**
"For every screen, report: public/anonymous yes or no, required roles, and
whether it is the default screen. Confirm the Login (and password-recovery)
screens are public and that the login flow returns to the requested page.
Set access to exactly: `<screen>: <anonymous | role X>` for each."

**Proof:** render it, never take Mentor's word. Open the default URL signed
out (expect the login screen or the intended anonymous page, not an error or
blank), sign in, and reach one authenticated screen. Neither Mentor's
read-back nor published-state screen inspection is reliable for access on the
template login screens - in the probe they disagreed with each other
`[SINGLE-OBSERVATION]` - so the render is the only proof.
Where the browser step needs a login the agent cannot perform, that render
is a user-action hand-off.

## 2. Secrets never travel through a Mentor prompt `[SINGLE-OBSERVATION]`

**Rule.** Never put a password, API key, token or connection secret into a
Mentor prompt, a spec file Mentor reads, a structure default, or a seed
payload. A prompt is stored and replayed; the value leaks into the model,
history and logs `[UNVERIFIED]` - the leak path is inferred, but the rule costs
nothing. The pattern below was used in one build and worked.

**Brief:** "Create a Setting `<Name>` of type Text, marked secret, with no
default value. Read it at runtime where the credential is needed. Do not ask
me for the value." Then hand off to the user: they set the value per stage in
the Portal. That is a legitimate user-action stop, not a halt.

Vendor-documented consequences, cited by the vendor's own skill set and not
observed in the Fulcrum corpus `[UNVERIFIED]`:
- A secret Setting has no authored default, so a first run that expects a
  default to work needs the Portal value set first - plan the hand-off
  before the first integration test, not after it fails.
- Switching a secret Setting back to non-secret deletes its value on the
  next publish. Decide secret-ness once, at creation.
- A Setting default value is capped at 2,000 characters. Large text (a long
  system prompt, a template) needs another home - an entity row, a resource,
  or runtime assignment.

**Proof:** settings have no published-state read path (see
`rest-and-integration.md` entry 6). Prove the credential works behaviourally:
the integration call succeeds where the unauthenticated probe returned 401.

## 3. Entity actions called from client logic raise a security warning `[UNVERIFIED]`

Reported by the vendor's skill set: calling a generated `Create<E>`,
`CreateOrUpdate<E>`, `Update<E>` or `Delete<E>` from a screen or client action
raises a security warning about exposing a database operation client-side.
Route every write through a server action that validates before it writes; a
pass-through wrapper only silences the warning. This one is visible - as a
warning, not an error - so read warning counts, not just error counts.

## 4. A planned action name can collide with an entity's generated action `[UNVERIFIED]`

Every entity gets generated `Create<E>`/`Update<E>`/`Delete<E>`/
`CreateOrUpdate<E>` actions. A spec that names its own action the
same way (e.g. a custom `CreateOrder` beside entity `Order`) invites Mentor to
reuse the generated action or rename yours unasked. Name custom actions with
a distinct verb (`SubmitOrder`, `RegisterOrder`). Reported by the vendor's
skill set as a plan-gate rule, not observed in the Fulcrum corpus.
