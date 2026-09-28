# Diagnostic REST endpoint pattern

Rung 5 of the proof ladder (live data ground truth) has no model-layer path
in v1, on any tenant. This is the workaround, and the debt it creates.

## Why there is no model-layer path

`[SCHEMA]` `db_query` is not a model-layer SQL path. It requires a harness stood
up by `test_setup_start`, accepts only SQL templates declared upfront in that
harness's `query_templates`, and its own schema states that no template —
`SELECT` included — returns rows in v1: every template comes back with
rowcount 0. This is a universal v1 platform limitation, not tenant variance.
Do not probe it per project and do not carry a `db_query` row in
`tenant-profile.md`.

Build a temporary diagnostic endpoint instead of relying on `db_query` for
live row data. The instrument for a real query path is `exec_in_app` against a
harness fork — that procedure is future work, not written here.

## The pattern that works

`[VERIFIED]`

1. **A temporary REST GET returning pipe-delimited plain text**, not JSON.
   Plain delimited text survives being read back through whatever channel
   the orchestrator/agent has, without a parsing layer that can itself hide
   a bug.
2. **Explicit boolean-to-text conversion** on every boolean field. The
   platform omits falsey values from response bodies entirely — a `false` or
   empty value is silently absent, not present-as-false. Its absence from
   the response is NOT evidence that the underlying assignment is missing;
   convert every boolean to an explicit text token (`"true"`/`"false"`)
   before it goes in the response.
3. **An explicit send-default-values property** on the response structure,
   for the same reason — a default/zero value can otherwise be silently
   dropped rather than sent.
4. **A header dump on every call.** Distinguishes a genuinely false/absent
   value from a value that was actually wired to a response header instead
   of a body field — a wiring mistake that a body-only read can't detect.
5. **Its own guard logic**, not bolted onto an existing orchestrator action.
   A diagnostic endpoint that shares logic with production code risks
   inheriting production's bugs (or introducing new ones into production) —
   keep it structurally separate and disposable.

## The debt is real — track it from endpoint one

`[VERIFIED]` These endpoints accumulate as permanent artifacts if left
unmanaged. The source build finished with 7+ live diagnostic endpoints and no
removal plan. Do not let this recur:

- Log every diagnostic endpoint created, with its purpose and creation date,
  starting from the first one — not retroactively once there are several.
- Schedule teardown explicitly as part of the work that created the need for
  it, not as an afterthought once the feature ships.
- Treat an undocumented diagnostic endpoint discovered later as a finding to
  report, not as background noise to ignore.
