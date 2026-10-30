# Evidence tags

The vocabulary every Fulcrum file uses to mark how strongly a claim is known. Tag any
claim that is not directly observed.

- `[VERIFIED]` - observed live, more than once, in the source build.
- `[SINGLE-OBSERVATION]` - seen once; real but not generalised.
- `[UNVERIFIED]` - inferred or reported but never confirmed. Say so plainly.
- `[TENANT]` - belongs in `tenant-profile.md`; a skill defers to the probe.
- `[SCHEMA]` - asserted by the vendor's own MCP tool documentation, not observed
  live. Stronger than inference: the vendor is describing its own system.
  Weaker than observation: documentation drifts from behaviour, and a schema
  states intent, not what a given tenant actually does. Keep it distinct -
  collapsing it into `[VERIFIED]` launders documentation as field evidence,
  which is exactly what these tags exist to prevent. Promote to `[VERIFIED]`
  only on a live observation.

Default to `[VERIFIED]` only when the source corpus shows repeat occurrence.
Do not launder a single observation into a general rule.

Rows labelled "Fulcrum rule" state Fulcrum policy, not platform evidence, and carry no
evidence tag.
