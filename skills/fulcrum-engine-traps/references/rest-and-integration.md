# REST and integration

Entries 1-5: what goes over the wire, and how to diagnose it. Entries 6-7:
what can and cannot be proven through the model. Entries 8-12: model-structure
traps around REST methods and references.

## 1. Falsey and empty values are omitted from a REST response body `[VERIFIED]`

**Failure mode.** An Integer `0` or Boolean `False` output on an exposed REST
method can be dropped from the JSON response entirely, not serialized as
`0`/`false`. An empty text field has also been seen omitted
`[SINGLE-OBSERVATION]`. "Zero", "false" and "empty" become indistinguishable
from "never assigned", which is the shape of a silent blank-row or no-op
defect in any caller.

**Visible?** No. Clean publish; only the literal response body (not a Mentor
summary of it) shows the missing key.

**Brief:** where a caller must tell "0/false/empty" from "not set", prefer a
single combined text output over separate numeric/boolean outputs, and say
why: "ODC REST can omit falsey and empty values from the response - an
Integer 0 or Boolean False vanishes entirely, so zero is indistinguishable
from never-assigned." Explaining the why measurably stops Mentor substituting
its own shape. Any client parsing the response must treat a missing key as a
possible zero/false/empty, not as an error.

**Proof:** read the raw response body for a case where the value is 0/false.

## 2. JSON key names default to PascalCase - state an explicit JSON name per attribute `[SINGLE-OBSERVATION]`

**Failure mode.** A structure Mentor creates for an exposed or a consumed REST
method serializes with the attribute name as the JSON key, so keys come out
PascalCase (`StatusCode`, not `statusCode`). Read on the wire for the expose
direction only: an endpoint briefed as `{statusCode, error}` returned
`{"StatusCode":401}`. On the consume side, a POST to a camelCase API was
rejected with a 500; PascalCase keys are the inferred cause - the keys on the
wire were not captured - but setting explicit camelCase JSON names did make
the call land.

- **Consume is the silent killer.** The target rejects or ignores the body
  (the 500 above came from the target's own validation), or response fields
  deserialize empty because no key matches. The consuming app's own logs
  usually show only a generic `500 Internal Server Error`; the actual fault
  (which field, why) is in the **target system's** log.
- **Expose** breaks any client written against the documented contract.

**Visible?** No. Clean publish, and Mentor may claim JSON names exist when
they do not (see the read-back row in `../SKILL.md`).

**Brief, on every REST consume and expose turn:** "Set an explicit JSON name on
every attribute of every request and response structure, exactly matching the
external contract's case: `<attr> -> <jsonName>` for each. Do not rely on the
attribute name. Report the full attribute-to-JSON-name table." Copy the names
from the contract (spec file, sample payload), never from memory.

**Proof:** behavioural or wire-level only - see entry 6. One real call, then
find the request in the target's log by its field names, or call an exposed
endpoint and read the raw keys.

## 3. A consumed REST call with a non-JSON error body breaks status handling `[SINGLE-OBSERVATION]`

**Failure mode.** Many targets return a plain-text or empty body on an error
status (a `401` with body `Unauthorized`, an HTML error page from a proxy).
When the consumed method expects a JSON response, deserialization of that
body throws (observed: `OS-BERT-60600`, "Failed to deserialize"). The real
status code never reaches your logic; a `CatchAll` handler reports a
deserialize error instead.

**Brief:** "In the consumed API's `OnAfterResponse`, if the response body is
not valid JSON (empty, plain text, HTML), replace it with a JSON object that
carries the status code and the raw text, matching the response structure,
before deserialization. Handle the status code from that object." State that
a plain-text error body is expected, not exceptional.

**Proof:** force a known error status (an unauthenticated call to a protected
path is the cheapest) and confirm the app surfaces the status code, not a
deserialize error.

## 4. Outbound connectivity: diagnose route before credentials `[SINGLE-OBSERVATION]`

**Failure mode.** An outbound call that fails with a transport error and **no
HTTP status** (observed: `OS-BERT-00000`, "An error occurred while sending
the request") never reached an HTTP server. It is a
connectivity fault - network path, private gateway or tunnel down, wrong
scheme or host - not an auth or payload fault. Changing credentials or
structures in response burns fix turns on the wrong layer.

**Diagnostic, needs no secret:** make an **unauthenticated** call from the app
to a path on the target known to be protected. A `401` (or `403`) proves the
route, scheme, host and port end to end, without any credential travelling
anywhere. A transport error means fix connectivity first; a `401` with
credentials set means look at auth; a `4xx/5xx` with a body means look at
the payload and the target's log.

Where no MCP-visible status exists for the network path (common for private
connectivity), this in-app probe is the only proof - build it as a temporary
diagnostic endpoint per `../../fulcrum-verification/references/diagnostic-endpoint.md`
and re-run it right before anything that depends on the integration live.

## 5. A Boolean output can get wired as a response header, not the body `[VERIFIED]`

**Failure mode.** Asked for a Boolean output (e.g. an idempotency `Skipped`
flag), Mentor can wire it as a custom response **header** (`X-Skipped`)
instead of a body field. Combined with entry 1, a `False` is then invisible
twice over.

**Brief:** be explicit about the response shape, and anchor it to a working
sibling if one exists: "return this in the RESPONSE BODY, exactly the way the
existing `POST /<sibling>` method sends its outputs - read that method first
and match its configuration rather than guessing."

## 6. Constructs with no published-state read path need behavioural proof `[VERIFIED]`

The model-inspection surface does not show everything. Observed blind
spots: **Settings** (no view at all), and **consumed REST request/response
structures and their JSON names** (not exposed by structure or search reads;
seen by two separate agents). Inspection also reflects published state only,
so nothing is readable before the first publish.

For these, Mentor's own read-back is evidence of Mentor's belief, not of the
model, and has contradicted published state. Plan the proof as behaviour or
wire-level evidence from the start: the target's log for the real request, an
exposed endpoint's raw response, or an in-app probe. See
`../../fulcrum-verification/SKILL.md` for instrument selection.

## 7. No model-layer path to live row data `[SCHEMA]`

**Failure mode.** There is no model-layer SQL path to live row values on any
tenant (the canonical fact is in `CONVENTIONS.md`, "No model-layer path to live row
data").
Mentor only has model/schema visibility, yet it will still *answer* a
question about live data - plausibly, confidently, with no error - and if
pressed can fabricate a value instead of refusing.

**Brief:** never ask Mentor for live row values. Prove row-level state through
the rendered UI or a temporary diagnostic endpoint, per
`../../fulcrum-verification/references/diagnostic-endpoint.md`. Never point a
row-mutating diagnostic at the environment being built in.

## 8. Server Actions may not be markable Public `[TENANT]`

Where the flag allowing a server action to be called directly is unavailable
on this tenant, plan any "call this on demand" requirement around a REST
method invoking the action from the start, not as a fallback. Check
`tenant-profile.md`.

## 9. A new REST method can silently reuse an existing structure `[VERIFIED]`

Mentor economizes on new elements - a new method can reuse an existing
response structure rather than getting its own. It publishes clean and works,
but the two methods now share one structure: editing either one's shape
changes both, invisibly. If a method needs a dedicated structure, say so
explicitly; do not assume Mentor creates one because the shapes differ today.

## 10. Deletes: split method and action, and never trust the delete report `[VERIFIED]`

Deleting a REST method and its backing Server Action in a single turn has
both failed (no change applied, summary claims success, revision does not
advance) and succeeded, with no visible difference in the request. Mentor
infers "deleted" from a not-found exception in its own post-delete lookup,
which can throw for unrelated reasons, so the report is wrong in both
directions.

**Brief:** two turns - delete the method, confirm, then delete the action.
**Proof:** the revision advancing plus the live `swagger.json` and the
endpoint's actual HTTP status, never the turn's own report.

## 11. A cross-app or library element must be referenced before it is named `[UNVERIFIED]`

Reported by the vendor's own skill set, citing public ODC docs, not observed
in the Fulcrum corpus: a **library**'s elements are not consumable until its
first version is released, and a public element from another app or library
must be added as a reference before a prompt names it. Mentor can locate a
named element and offer to add the reference - accept only when it names the
producer you meant. Surface a missing reference as a prerequisite, not a
build step.

## 12. Hand-wired JSON/record loaders - see the aggregates reference

The empty-record-literal defect for `CreateOrUpdate`-based loaders is in
`aggregates-and-repeaters.md` entry 9 - a data-loading trap that commonly
appears alongside REST-sourced batches.
