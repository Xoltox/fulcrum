# Template - `.fulcrum/design/manifest.md`

The design loop's index. The orchestrator reads this file, `gate.md` and fidelity
summaries, plus one `screens/<SID>.md` only while composing that screen step's brief;
images stay in capturer and verifier contexts. Written at intake by the orchestrator;
screen rows filled from the shared capture dispatch's report. On the full profile:
`.fulcrum/design/<app>/manifest.md`, one per app. Schema:
`../references/design-spec-format.md`.

---

<!-- fulcrum-schema: design-manifest v1 -->

# Design manifest - \<app name\>

## Source

- **Kind:** \<image | figma | html | tsx\>
- **Paths / URL:** \<`source/<file>` ... or the design-tool URL\>
- **Received:** \<ISO-8601 UTC date\>

## Viewport

| Form factor | W x H (from the source) |
|---|---|
| \<desktop\> | \<1440 x 900\> |

## Screens

At most 6 per app. More means the engagement is not a design loop. `SID`s are
assigned by the shared capture dispatch. A split screen lists both steps;
render-compare runs once, after the last step of a split screen; earlier split steps
verify rungs 1 and 3 only.

| SID | Name | Archetype | Reference | Step | Nav label | Access |
|---|---|---|---|---|---|---|
| S01 | \<name\> | \<archetype from screen-archetypes.md\> | `reference/S01.<ext>` \<whole image: which part is this screen\> | P1.06 | \<label\> | \<public / sign-in / role X\> |

## Reference library

\<`absent`, or the official skill's path and `metadata.version`; see
`../references/official-skill-interop.md`\>

## Policy

- **App creation:** \<Mentor-created | user's shell `<app key>`\> - \<D-NNN\>
- **Screen access:** \<all sign-in | public: S.. | per role\> - \<D-NNN\>
- **Fidelity bar:** \<structural | visual\> - \<D-NNN\>
- **Render tier:** \<A browser | B user screenshots | C structure only\> - \<D-NNN\>
- **Personas in Development:** \<yes | no | n/a\> - \<D-NNN\>
- **Commit design source / render screenshots:** \<yes|no\> / \<yes|no\> - \<D-NNN\>
- **Assets:** \<Studio upload | placeholders | empty\> - \<D-NNN\>
- **Form factor:** \<desktop | phone width | n/a (source unambiguous)\> - \<D-NNN or -\>
- **MCP re-probe:** \<re-probe first | risk accepted | n/a (none owed)\> - \<D-NNN or -\>

## Decisions

\<D-ids of every batch B answer and the go/no-go, comma-separated\>
