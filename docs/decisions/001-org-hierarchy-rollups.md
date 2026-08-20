# 001 — Organisational Hierarchy Rollups

- **Status:** Accepted
- **Date:** 2026-08-20
- **Applies to:** statistics/reporting modules that aggregate across the
  Archdiocese of Kigali's organisational tree.

## Context

Arkidi models the Archdiocese of Kigali using a chain of dedicated tables rather
than one generic "node" table:

```
Archdiocese → Deanery → Parish → Centrale → SmallChristianCommunity
```

Individual `Faithful` and `Family` records link **directly to `parish_id`**; they
do not denormalise a `deanery_id` or `archdiocese_id` onto every row. This means
that a query like *"count the faithful in Deanery X"* cannot be answered with a
single table lookup — it must first resolve the set of parishes under that
deanery (either directly by `deanery_id`, or transitively through `Deanery`
when the scope is an archdiocese).

## Decision

Keep the four-table hierarchy as-is. Do **not** consolidate it into a single
generic/recursive hierarchy table.

Provide a single, sanctioned rollup helper module at
`app/services/org/hierarchy_resolver.py` exposing two functions:

- `get_ancestors(db, parish_id=…, centrale_id=…, scc_id=…) -> dict` — given any
  single level, returns the full chain up to the archdiocese
  (`{"scc_id", "centrale_id", "parish_id", "deanery_id", "archdiocese_id"}`),
  with `None` for levels above the supplied node that are not resolvable.
- `get_descendant_parish_ids(db, deanery_id=…, archdiocese_id=…) -> list[uuid]` —
  returns every `Parish.id` beneath a deanery or the whole archdiocese.

New code that aggregates across organisational levels **must** call these
functions rather than writing ad-hoc cross-table joins inline.

## Why keep the four-table structure

- **Matches real diocesan structure.** Deaneries, parishes, centrales and small
  Christian communities are distinct real-world entities with their own
  attributes; collapsing them into a generic hierarchy would force pattern
  matching / type-checking logic into every consumer.
- **Type safety per level.** Each level is a typed SQLAlchemy model and a typed
  FK column, so the ORM (and static analysis) knows exactly which primary keys
  belong to which level. A recursive generic hierarchy erases that.

## Trade-offs accepted

- Rollup queries require explicit joins. A single recursive (or generic-tree)
  query would traverse the tree in one pass, but would lose per-level typing and
  complicate every consumer. Concentrating the joins in
  `hierarchy_resolver.py` keeps the trade-off localised: consumer modules get a
  simple function call, and the multi-table join exists in exactly one place.

## Consequences

- `hierarchy_resolver.py` is the only place that may own cross-level rollup
  joins. New aggregation code (e.g. the statistics engine) uses
  `get_descendant_parish_ids` before counting `Faithful`/`Family` records.
- Tests for both functions live in `tests/unit/`.