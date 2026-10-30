# Sample sign-in: the build recipe

One-click persona sign-in on the Login screen, Dev only, with real users. Detecting an
existing picker, choosing a persona and signing in during a render:
`../../fulcrum-render-check/references/sign-in-modes.md`. The first click registers
identity-provider users, so the user decides first (that file, "The side effect").

## Why a recipe

A plain Mentor prompt failed `[SINGLE-OBSERVATION]`: two hardcoded buttons, no user
registration, "Invalid credentials." on first click, and by Mentor's own read-back the
buttons "would appear in any stage, including Production". Validation was 0 errors. So
send the shape below, not the wish.

The shape copies the app generator's, read from one generated app, plus two changes: the
server-side Dev check, and a password held on the server. This recipe has not been run
end to end `[UNVERIFIED]`.

## Shape

| Element | Kind | Does |
|---|---|---|
| `IsInDevStage` | Server function | `GetDefaultDomain` equals the Dev domain from `env_list`. A literal fails closed: a domain change or a copy on another tenant hides the block |
| `GetSampleUserVerificationCode(Email)` | Server action | Dev check first; False returns both outputs empty. Then a Switch on Email: `StartUserRegistration` with the persona's Name and Email, keep the code, grant the role, return the password. Otherwise returns both empty |
| `GetShowLoginAs` | Screen data action | `ShowLoginAs` from `IsInDevStage` |
| Sample block | One If around all of it | Bound to `ShowLoginAs`. One button per persona, built-in validations off |
| `LoginAs(Email, Landing)` | Screen action | Get code and password; no password: show an error and end. Code not empty: `FinishUserRegistration`, end on failure. Then `DoLogin`; redirect to `Landing` |

## Rules, each with its failure

- **Server-side Dev check in the actions, not only the UI gate.** A UI gate leaves the
  action callable from the anonymous Login screen, and that action creates users and
  grants roles, so a Production caller could mint a role-holding user. Tag: an earlier
  read-back of a generated app showed the UI gate only `[SINGLE-OBSERVATION]`; the user
  reports nothing in the generated block works outside Dev. Unreconciled, and the check
  costs one node.
- **Whole block inside the If.** Mentor gated nothing by default, and a Visible on some
  children leaves the rest in any stage.
- **Every persona in the Switch.** A generated app's Switch covered 6 of its 10 buttons by
  Mentor's read-back. The rest may fall through to a login with no user, or a seeder may
  cover them `[UNVERIFIED]`.
- **`FinishUserRegistration` is client-only** `[SINGLE-OBSERVATION]`. A server action cannot
  call it, so the server returns the code and the client finishes. Designing it server-side
  cost one build a halt.
- **`StartUserRegistration` returns the code only on its first call** `[SINGLE-OBSERVATION]`.
  For an existing user, look the user up by Email for the grant. One click that failed
  midway then gave "Invalid credentials." on later clicks; an unfinished user is the
  likely cause, not proven `[UNVERIFIED]`. Prove one persona before the roster, so a
  defect strands one sample user.
- **End on a `FinishUserRegistration` failure; do not go on to `DoLogin`.** Mentor cannot
  read the tenant's password policy, so a rejected password leaves a role-holding user
  who never gets a code again, and `DoLogin` then reports only "Invalid credentials.".
  To clear one: a `manual` row for the user to remove that user in the Portal
  `[UNVERIFIED]`, or a new Email for that persona, which registers a fresh user and leaves
  the stranded one holding its role.
- **Pass the user's Id to `Grant<Role>Role` and `Check<Role>Role`.** Take
  `UserRegistrationResult.UserId`, or the found `User.Id` for an existing user. With no
  argument `Check<Role>Role` reads the current user, anonymous here, so it answers false
  for everyone `[SINGLE-OBSERVATION]`.
- **Role actions resolve by the role's own action reference, not by name**
  `[SINGLE-OBSERVATION]`. `Grant<Role>Role` is server-only; `Check<Role>Role` is server and
  client. A "does not resolve" answer here is a wrong lookup, not a missing action.
- **Redirect to the persona's landing screen from `LoginAs`.** A Home that branches on
  `Check<Role>Role` at init ran before the client role cache filled, and signed-in users
  landed on InvalidPermissions `[SINGLE-OBSERVATION]`.
- **Built-in validations off on each button** `[VERIFIED]`. A submit button validates the
  form's required fields on the first click instead of signing in, which reads as a false
  negative.
- **Raise the timeout on the server call.** First sign-in after idle took 12-13 s against
  a 10 s default (`rest-and-integration.md` entry 15). 30 s fixed it.
- **Plain Button in a repeater.** `ButtonLoading` inside a List throws a spinner error
  `[SINGLE-OBSERVATION]`.
- **No password in a prompt.** A prompt is stored, and harness permission layers have
  denied calls carrying one. Mentor chooses the value. Never reuse it; never read it back.
- **No password literal in client logic.** The generated pattern keeps one in button
  arguments, so it ships in the client bundle in every stage `[UNVERIFIED]`, and neither
  the If nor the server check removes it. Here only the server action holds it and returns
  it at sign-in, so the bundle holds none, and it refuses outside Dev. In Dev any caller of
  the action can still read it.
- **Sample users are real identity-provider users.** Whether they span stages is
  `[UNVERIFIED]`, so app access outside Dev is not assumed safe: where they do span, a
  role granted in Dev could hold in Test or Production. Treat them as real accounts.

## Prompt scaffold

Roster (name, email, role), Dev domain and landing screens are the only blanks. Personas
use `@example.com`.

Turn 1, server:

> Create server function IsInDevStage: Value = GetDefaultDomain.DefaultDomain = "`<Dev
> domain>`". Create server action GetSampleUserVerificationCode, input Email, outputs
> SampleUserVerificationCode Text and SampleUserPassword Text. First node: call
> IsInDevStage; if False, end with both outputs empty, because a screen gate alone leaves
> this action callable in any stage. Then Switch on Email: `<email -> name, role, one per
> persona>`. On a match call system StartUserRegistration with that Name and Email, assign
> its VerificationCode, grant the role through the role's own action reference passing
> UserRegistrationResult.UserId, and assign SampleUserPassword. If the user already exists
> no code comes back: find the user by Email, then call Check`<Role>`Role with that
> User.Id and Grant`<Role>`Role with that User.Id only if it is false, because Check with
> no argument reads the current user, anonymous here. Otherwise return both empty. Choose
> one sample password yourself that meets the tenant's policy, keep it in this action
> only, never in client logic, and never show it in a reply. If any identifier does not
> resolve, STOP and name it. Report the validation error count.

Turn 2, Login screen:

> Add data action GetShowLoginAs with output ShowLoginAs from IsInDevStage. Below the
> form add one If on ShowLoginAs around the whole sample block, so nothing of it renders
> when False. Inside, one Button per persona, label "Log in as `<Name>` (`<Role>`)",
> Built-in Validations None, because a submit button validates required fields on the
> first click instead of signing in. OnClick calls screen action LoginAs(Email, Landing).
> LoginAs: call GetSampleUserVerificationCode with a 30 s timeout, because the 10 s
> default trips on cold start. If SampleUserPassword is empty, show an error and end. If
> the code is not empty call FinishUserRegistration, which is client-only, with that
> password; if it fails, show its error and end, without DoLogin. Then DoLogin with that
> password. On success RedirectToURL to Landing; on failure show the error. Pass the
> password only from the server output: no password literal in client logic, because
> client logic ships in the bundle in every stage. If any identifier does not resolve,
> STOP and name it; do not substitute another action or a literal.

Turn 3, read-back:

> Quote verbatim, changing nothing: the If's condition and what sits in each branch; in
> GetSampleUserVerificationCode the first If with its True and False targets; every node
> of LoginAs in order with arguments, password masked; Built-in Validations per button.
> Say yes or no: does any client action or widget hold a password literal? Do not quote it.

## Proof

Read-back is belief, and has reported a conditional's branches swapped
(`access-security-and-settings.md` entry 5). The proof is the first click, per the render
check:

1. One persona: click, confirm the signed-in name and the landing screen. Sign out, click
   again to prove the existing-user path.
2. The other roles, and a screen each must be refused.
3. The published client bundle holds no password: the render brief asks the renderer to
   read the Login screen's loaded scripts and report whether `LoginAs` passes anything but
   the server output as a password, in its usual wording and never the value.
4. The `False` branch cannot run in Dev. It stays `untested` until a non-Dev stage shows no
   block, and that is a stated gap. A swapped branch does show in Dev: the block vanishes
   or sign-in fails.

## Several apps, one set of users `[SINGLE-OBSERVATION]`

Server actions may not be public across apps (`rest-and-integration.md` entry 8), so one
build used a public service action returning Email and code, Dev-gated, with idempotent
role grants; each app's client finishes registration. A public action returning a
verification code or a password must be Dev-only. Consumers hit the index wait
(`rest-and-integration.md` entry 16).
