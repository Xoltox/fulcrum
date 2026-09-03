# REST and integration

## 1. ODC REST silently omits falsey values from the response body `[VERIFIED]`

**Failure mode.** An Integer `0` or Boolean `False` output on a REST
method can be dropped entirely from the JSON response — not serialized as
`0`/`false`, just absent. This makes "zero"/"false" indistinguishable from
"field was never assigned", which is exactly the shape of a silent
blank-row/no-op defect.

**Visible?** No — clean publish; only inspecting the literal response body
(not a Mentor summary of it) shows the missing key.

**Fix:** where a caller must distinguish "0/false" from "never set",
prefer a single combined text/string output over separate numeric/boolean
outputs, and state why in the prompt: "ODC REST silently omits falsey
values from the response — an Integer 0 or Boolean False vanishes
entirely, making zero indistinguishable from never-assigned." Explaining
the *why* measurably stops Mentor substituting a different shape on its
own.

## 2. A Boolean REST output can get wired as a response header, not the body `[VERIFIED]`

**Failure mode.** Asked for a Boolean output (e.g. an idempotency
`Skipped` flag), Mentor can wire it as a custom response **header**
(`X-Skipped`) instead of a body field. Combined with trap #1, a `False`
value is then invisible twice over — dropped from a header a caller isn't
even reading.

**Fix:** be explicit about the response shape, and anchor it to a working
sibling if one exists: "return this in the RESPONSE BODY, exactly the way
the existing `POST /<sibling>` method sends its own outputs — read that
method first and match its configuration rather than guessing."

## 3. No model-layer path to live row data `[TENANT]`

**Failure mode.** On tenants where the raw-row-read path is dead (a
literal `SELECT 1`-equivalent probe returns an empty result even against a
fresh, populated environment), there is no way to inspect live row values
through the model layer at all. Mentor will still *answer* a question
about live data if asked — plausibly, confidently, with no error — because
it only has model/schema visibility, not row visibility; if pressed for a
live value it can fabricate a plausible-sounding one instead of refusing.

**Fix:** check `tenant-profile.md` for this fact before planning any
"verify against live data" step. If the path is dead: never ask Mentor
for live row values at all (it isn't a safe way to find out even that the
path is dead), and never point a row-mutating diagnostic tool at the
actual environment being built in. Use a rendered-UI check, or a
temporary diagnostic REST endpoint deleted after use, as the only ways to
prove row-level state.

## 4. Server Actions cannot be marked Public `[TENANT]`

Where the platform flag that allows a server action to be called directly
is removed for this tenant, plan any "call this on demand" requirement
around a REST API method invoking the action from the start, not as a
fallback. Check `tenant-profile.md`.

## 5. Deleting a REST method and its backing Server Action in one turn is non-deterministic `[VERIFIED]`

Deleting both together in a single turn has failed (`change_applied:
false`, summary claims success, revision does not advance) and succeeded
in another instance with no visible difference in the request. Split into
two turns — delete the method, confirm, then delete the action — and
verify each half against the live `swagger.json` and the endpoint's actual
HTTP status, not against `change_applied`.

## 6. `change_applied` is not a reliable delete signal in either direction `[VERIFIED]`

Mentor infers "deleted" from a "not found" exception thrown by its own
post-delete lookup — which can throw for unrelated reasons. Observed both
false negatives (`change_applied: false` on a delete that did land) and
false positives are possible by the same mechanism. Never accept a
delete's self-report; confirm via the revision number advancing plus
`swagger.json`/endpoint status.

## 7. Reusing an existing structure/response shape instead of creating a dedicated one `[VERIFIED]`

Mentor economizes on new elements by default — a new REST method can
silently reuse an existing response structure rather than getting its own.
Nothing pre-existing is modified, so it publishes clean and initially
works, but the two methods now permanently share a structure: editing
either one's shape changes both, invisibly to anyone editing the other
method later. If a method needs a dedicated structure, say so explicitly
rather than assuming Mentor will create one because the shapes currently
differ.

## 8. Hand-wired JSON/record loaders — see the aggregates reference

The empty-record-literal defect for `CreateOrUpdate`-based loaders is
covered in `aggregates-and-repeaters.md` — it is a data-loading trap, not
strictly a REST one, but it commonly appears alongside REST-sourced seed
batches.
