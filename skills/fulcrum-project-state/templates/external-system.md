# Template - `.fulcrum/external/<system>.md`

One file per external system or integration target the ODC solution consumes or
calls: a partner REST API, another vendor's server or a workflow engine, a database the app reads through
a connector, a service built by someone else in the same engagement. `<system>` is a
short lowercase stem, e.g. `bpm-claims`, used verbatim wherever the system is named
(plans, specs, `TASKS.md` `App` column for `Turn: external` rows).

The system itself is built outside Fulcrum - `../../../CONVENTIONS.md`, the
skill-boundaries table, row "Out of family". **This file must exist,
with every section filled or marked unresolved, before the first ODC step that
consumes the system starts.** A brief, spec or diagnosis prompt copies endpoint, auth
scheme and log paths from here, never from memory or from a chat message.

Rules:

- **Never write a secret value here.** This file is committed. Name the auth scheme
  and where the secret lives - normally a secret Setting the user sets in the ODC
  Portal. A secret in a committed file, or in a Mentor prompt, is a leak.
- Every log path is verified once with a directory listing on the machine that hosts
  it, and the date is recorded. An unverified path is marked `unverified`, and a
  diagnosis agent told to read it must report "not checked" rather than "no errors".
  A wrong path reads as a silent system, which is a false pass.
- Rewritten in place when the contract changes. Record why in `DECISIONS.md`.
- `-` means not applicable; `unresolved: <who answers it>` means not yet known. Never
  leave a cell empty.

Schema: `../references/file-schemas.md`, heading "external/<system>.md".

---

<!-- fulcrum-schema: external-system v1 -->

# External system - \<system stem\>

**What it is:** \<one line: product, who builds and runs it, which ODC app consumes it\>
**Built by:** \<team or person; "outside Fulcrum"\>
**Consumed by step(s):** \<plan step ids, e.g. P1.03\>

## Endpoint and auth

| Field | Value |
|---|---|
| Base URL per environment | \<env = URL, one per line\> |
| Reachability from ODC | \<public / private gateway / not yet reachable\> |
| Auth scheme | \<none / basic / API key header / OAuth2 client credentials / ...\> |
| Where the secret lives | \<e.g. secret Setting `<name>` on app `<app identifier>`, set by the user in the Portal\> |
| Who sets it | \<the user - an agent never handles the value\> |

## Payload contract

| Operation | Method and path | Request shape | Response shape | Key casing |
|---|---|---|---|---|
| \<op\> | \<GET /claims/{id}\> | \<fields, or a path to a sample\> | \<fields, or a path to a sample\> | \<camelCase / PascalCase / ...\> |

Samples, if any: \<path to committed sample request/response files, secrets removed\>

## Error codes

| Status or code | Meaning | Body shape (JSON / text / empty) | Consumer must |
|---|---|---|---|
| \<404\> | \<not found\> | \<text\> | \<what the ODC side does\> |

## Log locations

| Log | Host | Path | Verified by | Date |
|---|---|---|---|---|
| \<server log\> | \<machine\> | \<absolute path\> | \<directory listing showed the file / unverified\> | \<YYYY-MM-DD\> |

Copy these paths into briefs verbatim. If a listing finds the path empty or missing,
fix this table before any diagnosis prompt uses it.
