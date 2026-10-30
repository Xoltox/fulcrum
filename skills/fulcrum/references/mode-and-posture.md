# Mode and posture

Three settings, **three orthogonal axes**: mode, posture and rigor. Never collapse them
into one dial. An expert user may want `collaborative`; a `guided` user may want
`directive`; a `demo` may run under either posture. Every combination is legal and must
be honoured as written. All three are recorded in `.fulcrum/project.md`
(`../../fulcrum-project-state/SKILL.md`, heading "Mode and posture"), never in the
installed skill files.

**Mode - `guided` | `expert`.** Governs who decides and how much is asked of the user.

| | `guided` | `expert` |
|---|---|---|
| Entry | The router runs automatically and interviews the user | The user invokes skills directly |
| On ambiguity | Block and ask. Offer a small number of options with a recommendation | Proceed under a stated assumption and record it in `DECISIONS.md` |
| Assumptions | Surfaced to the user as they are made | Recorded, not narrated |
| Narration | Says what is about to happen and why, in plain language | Terse |
| Parameters and tiers | Defaults | Overridable per project |

**Posture - `collaborative` | `directive`.** Governs how the harness model talks to
Mentor.

| | `collaborative` (default) | `directive` |
|---|---|---|
| Turn shape | Consult Mentor for the idiomatic ODC approach first, review its proposal against the trap registry in `../../fulcrum-engine-traps/SKILL.md`, correct only the specific traps, then build | Instruct Mentor exactly what to build |

**`collaborative` is the default at every tier.**

**The failure mechanism.** `directive` posture is a bet that the harness model's ODC
platform knowledge exceeds Mentor's. That bet loses more often as the harness model
gets cheaper. A model issuing strict build instructions on weak platform knowledge
invents non-idiomatic structures Mentor would never have chosen; those pass validation
and publish clean, then surface later as traps. Mentor is the better source of
platform idiom. Fulcrum is the better source of trap avoidance and verification.
`collaborative` posture is what makes that division of labour operational.

**`directive` is an explicit user opt-in and is NEVER auto-selected by tier**, model,
or budget. Same principle as "Never escalate model tier to break a bug" in
`../../fulcrum-unattended-guardrails/SKILL.md`: posture is a user decision, never a
machine one. A cheaper tier is a reason to lean harder on `collaborative`, not a licence
to switch.

**Rigor - `demo` | `pilot` | `production`.** Governs depth of evidence: which gates run
and how often. Recorded as `Rigor` in `.fulcrum/project.md`. The gates and the rigor
table live once, in `../../fulcrum-verification/SKILL.md`, heading "Gates and rigor";
never restate them.

**Rigor is asked at init in every mode, never defaulted, never inferred.** Missing on
resume: ask. Changing it is a user decision. The failure mechanism: a guessed rigor sets
proof depth for the whole build, so a demo pays for production proof, or a production
build ships on demo evidence, and nothing in the run says the setting was a guess.

**Rigor never changes posture.** `directive` stays an explicit user opt-in, at `demo`
too. Rigor is depth of evidence, not safety: it relaxes no safety rule. The list of what
holds at every rigor lives with the table.

**Economics.** `collaborative` trades one cheap consult turn for fewer expensive fix
turns. `[UNVERIFIED]` This is a design prediction, not a measurement - no run has been
instrumented to compare the two postures' total turn cost. Do not cite it as a
finding.
