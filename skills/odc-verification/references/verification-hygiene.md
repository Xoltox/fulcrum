# Verification hygiene

Cross-cutting rules that apply regardless of which rung of the proof ladder
is in play. All `[VERIFIED]` unless marked otherwise.

## Invariants over fixed values

Assert invariants, never a hardcoded fixed value, for anything that is
time-dependent or scales with live data volume. A hardcoded expected count
drifts as the wall clock moves or as more data is seeded — the drift then
looks exactly like a regression when it is not. Prefer a derived expected
count (read it from somewhere else in the live system) over a hardcoded one,
always. This includes date-relative labels (e.g. a "today/earlier" split) —
express them as a derivation the checker can recompute from the current
timestamp, not as a literal baked into a fixture.

## Hand-classify before comparing

Classify expected results independently, by hand, before comparing against
rendered output. Do not accept the building agent's or Mentor's own
classification of what the correct result should be as the ground truth you
check against — that collapses the check into asking the system whether it
agrees with itself. Cross-check the independent classification against
rendered output afterward.

## Full-row arithmetic, not a sample

Verify arithmetic invariants (totals, sums, pairwise offsets) across **every**
row a change touches, not a sample. A sample can miss the one row where a
formula was applied inconsistently.

## Programmatic comparison

Compare digests, diffs, and any structured output programmatically. Never
compare by eye — eye comparison misses single-character deltas reliably and
does not scale past a handful of rows.

## Fixture correction, not fixture weakening

When new, legitimately correct data changes what an expected-values fixture
should say, tighten the fixture to the new correct values and label the
change explicitly as a fixture correction. Never weaken or delete an
assertion just to make a gate pass — that erases the check's future value
along with today's inconvenience. If a fixture and live output disagree, the
fixture is not automatically right: cross-read another independently-verified
source before deciding which side is stale (see `defect-instrument-matrix.md`
conclusion 4).

## Subagent proof discipline

A subagent's report of success is not, on its own, proof. Require every
verification agent — including yourself, when reporting up — to state
explicitly what it could **not** verify, not just what passed. A report that
only lists passes is incomplete by construction; the gaps are exactly where
the next defect hides.

## New vs. pre-existing failures

Distinguish pre-existing known failures from newly introduced ones on every
verification run. Never silently absorb either:

- A newly introduced failure reported as "pre-existing, not my concern"
  hides a real regression.
- A pre-existing failure reported as new wastes investigation time
  re-diagnosing something already understood, and risks masking whether the
  current change actually made it worse.

Carry a running list of known pre-existing failures forward between runs so
each new run can classify against it, rather than re-deriving the
distinction from memory each time.
