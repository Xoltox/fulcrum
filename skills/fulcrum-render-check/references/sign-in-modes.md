# Sign-in modes

Detail for `../SKILL.md`, heading "Sign-in modes - in order of preference".
Source for mode b: one read-only published-state investigation of one
generated app plus a tenant-wide action search (2026-10-16). Facts read from
the model are `[SINGLE-OBSERVATION]`; nothing below was exercised in a
browser, so behaviour claims are `[UNVERIFIED]` until a render confirms them.

## a. Anonymous

- Open the screen with no session. In mode c the shared browser carries the
  user's session, so anonymous assertions need a session-free page (a
  private window or separate profile where the capability allows it) or must
  run before the user signs in. If neither is possible, report the anonymous
  assertion `untested`.
- Expected-public screen: content renders. Expected-protected screen: the
  app redirects to its Login screen or shows InvalidPermissions. Record the
  final URL either way.

## b. Generated sample personas

### What it is

Apps produced by the platform's app generator have shipped a Login screen
with a "Log in as <persona>" picker. `[SINGLE-OBSERVATION]` Mechanism, as
read from the model:

- A data action on the Login screen computes whether the stage is Dev by
  comparing the default domain with a **hardcoded** Dev domain; the picker
  container's visibility binds to it.
- Each persona button calls a screen action with a fake email and one shared
  literal password as arguments.
- A server action looks the email up. A persona that does not exist yet is
  registered in the built-in identity provider (start then finish
  registration) and granted a role; an existing one goes straight to the
  built-in login. Then the screen redirects.
- The users are real built-in identity-provider end users, not app-entity
  rows and not impersonation.

### Detecting it (published-state reads, after the lag)

Look for, in this order:

1. `context_search` for the action `GetSampleUserVerificationCode`. The same
   action key appeared in many apps of one tenant `[SINGLE-OBSERVATION]`,
   which marks it as a generator default.
2. `IsInDevStage` (a function), and folders named `SampleUsers` /
   `SampleData`.
3. On the Login screen (`context_graph` rooted at it): a screen action
   `LoginAs` with inputs `SampleUsername` / `SamplePassword`, a data action
   `GetShowLoginAs`, buttons labelled "Log in as ...". The per-button naming
   in other apps is `[UNVERIFIED]`.

Any of 1-2 without 3 means the generator pieces exist but the picker may have
been replaced: confirm on the rendered Login screen before relying on it.

### Limits

- Dev only. The picker is hidden in any stage whose default domain differs
  from the hardcoded one, including Dev after a domain change or in a copy of
  the app on another tenant.
- Needs the built-in identity provider enabled for the app.
- Absent from hand-built apps and from apps whose Login screen was replaced.
- The generator default may cover fewer personas than the buttons on the
  screen (later edits can add buttons that rely on a separate seeding
  action). A persona button that fails sign-in is an observation, not a
  reason to try another route.

### The side effect - a user-policy decision

The first click per persona creates an identity-provider user and grants a
role. That is a change to the tenant's user directory, so it is the user's
call: ask once per project, and the orchestrator records the answer in
`DECISIONS.md`. Off until a recorded yes. (Fulcrum rule)

### Choosing the persona

1. Read the target screen's roles from `context_screens` (the roles listed in
   its additional data).
2. Map button labels to roles from the label text (labels have carried the
   role in parentheses). If a label does not name its role, say so and ask;
   do not guess.
3. Positive check: least-privileged persona whose role is required. Negative
   check: a persona without it.
4. Template-screen role flags are unreliable `[VERIFIED]`: a mismatch between
   the flag and the render is a finding, and the render wins.

### Signing in and out

- Sign in: click the persona button, wait for navigation, confirm the
  signed-in state from the page (a user name or menu), not from the URL alone.
- Sign out: the app's own logout control. Confirm by loading a protected
  screen and seeing the Login redirect. Unconfirmed sign-out ends the run.

## c. User hand-off

Use when mode b is absent, refused, or cannot reach the role needed.

1. The orchestrator asks the user, in one message: which app URL, which
   account role is needed, and to sign in in the shared browser (or confirm
   the existing session is the right account). Never ask for the
   credential itself.
2. The renderer opens its own page in that browser, confirms the signed-in
   state from the page, and continues.
3. The renderer never signs the user out and never closes the user's pages.
4. Auto-mode harnesses have blocked typed credentials and workarounds
   `[VERIFIED]`; even where nothing blocks it, Fulcrum forbids it. (Fulcrum
   rule)

## d. None

Report each affected assertion `untested`, with the mode that was missing and
why (no browser capability, picker absent, mode b declined, user not
available). An `untested` row is a stated gap, never a pass.
