# Diagnostic REST endpoint pattern

Rung 4 of the proof ladder (live data ground truth) has no model-layer path
on some tenants. This is the workaround, and the debt it creates.

## Check the tenant profile first

Whether a direct data-query path works at all is a **tenant fact**, not a
platform constant. Defer to `tenant-profile.md` (written once per project by
the capability probe) before assuming either way. On some tenants, a direct
query path returns empty results for even a trivial query, which means there
is no such path — not that the query was written wrong. `[TENANT]`

When the profile shows no live model-layer path to row data, build a
temporary diagnostic endpoint instead of retrying the query path.

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
