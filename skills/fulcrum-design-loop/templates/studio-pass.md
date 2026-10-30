# Template - `.fulcrum/design/STUDIO-PASS.md`

The work order for one Studio pass, written by the orchestrator before the hand-off
(`../references/build-lanes.md`, heading "Studio lane"). The user reads it in Studio.
A second pass overwrites it; the journal keeps the history. Plain words only: no tool
names, no task ids.

---

<!-- fulcrum-schema: design-studio-pass v1 -->

# Studio pass - \<app name\>

**Start from revision:** \<live revision from env_app\>. It is published; open the app
in Studio now, not before.

## Screens, in order

| Screen | Images, default state first | Access | Layout | Viewport | Data notes |
|---|---|---|---|---|---|
| \<name\> | `source/<file>` | \<role or public\> | \<side menu / top menu / blank\> | \<W x H\> | \<entities to bind, values that are real\> |

## Say to Mentor each time

- \<one line per tenant or project rule, e.g. which blocks to avoid, a name to keep\>
- Match the image for layout, colours and text.
- Do not reference any other app in the tenant.

## When you are done

Publish, then tell me "published". Do not leave work unpublished: I can only see what
is published. I will read the new revision, list what you built, and build on it
without overwriting it.
