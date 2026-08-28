# 002 — Generic Statistic Indicator Engine

- **Status:** Accepted
- **Date:** 2026-08-28
- **Applies to:** statistics/reporting across the Archdiocese of Kigali's
  organisational tree.

## Context

ADR 001 established `app/services/org/hierarchy_resolver.py` as the sanctioned
rollup helper module and called for the statistics engine to use
`get_descendant_parish_ids` before aggregating `Faithful`/`Family`-style
records. The first consumer (`Annuario Pontificio`) was still a single
hand-written method, and every new report ("faithful by deanery", "land value
by vicariate", "donations trend by parish") was heading toward yet another
hand-written method with its own ad-hoc SQL.

## Decision

Introduce a **configuration-driven indicator engine**:

- `StatisticIndicator` (`app/schemas/indicators.py`) — a declarative Pydantic
  config describing one aggregate: source model, aggregation (`count`/`sum`/
  `avg`), optional metric field, output grouping level (`archdiocese` /
  `deanery` / `vicariate` / `parish`), optional trend bucketing (`year` /
  `quarter` / `month`) over a date column, and filter constraints.
- `INDICATORS` registry + `AggregationService` (`app/services/indicators.py`)
  — the *single* generic pipeline used by every indicator:
  1. resolve the scope (archdiocese or deanery) to concrete parish ids via
     `get_descendant_parish_ids`;
  2. when bucketing above the parish level, resolve `parish → deanery →
     archdiocese` via `get_parish_ancestry_map` (bulk helper added to
     `hierarchy_resolver.py`);
  3. fetch the source rows for those parishes (`IndicatorRepository` in
     `app/repositories/indicators.py`);
  4. bucket by (period, group) and reduce by count/sum/avg in the service.
- The three motivating examples are now plain configuration entries, not
  methods.

`vicariate` is accepted as the ecclesiastical synonym for a deanery (a deanery
is led by a Vicar Forane): both group by `deanery_id`, while the API keeps the
configured `vicariate` label in the output.

## Why this shape

- **New statistics stay cheap and consistent.** Adding a report is a config
  entry in `INDICATORS`; cross-level rollup joins remain owned exclusively by
  `hierarchy_resolver.py` (ADR 001).
- **One query shape.** The engine never builds bespoke SQL per report. The
  repository only filters by the resolved parish set, and grouping happens in
  Python over the fetched rows — fine for a diocesan reporting workload and
  keeps every indicator on the same testable code path.
- **Scope correctness.** Every aggregation is bounded by a real organisational
  scope (`archdiocese_id` or `deanery_id`), so "count faithful in Deanery X"
  always resolves the exact parish set instead of relying on denormalised
  columns.

## Trade-offs accepted

- Python-side grouping means all source rows for the scope are loaded into the
  application. Acceptable at diocesan scale; if a future indicator needs
  DB-side `GROUP BY`, the repository can be extended behind the same interface.
- `Annuario Pontificio` remains a hand-written method for now; it can be
  re-expressed on this engine (e.g. with `AnnualParishStatistic` as the source
  model and predetermined year buckets) without changing its API.

## Consequences

- All new aggregated statistics are declared in
  `app/services/indicators.py::INDICATORS` and computed through
  `AggregationService` — no new hand-written per-report methods.
- `get_parish_ancestry_map` is the sanctioned bulk ancestor rollup for
  consumers that already hold a parish set.
- Tests live in `tests/unit/test_indicators.py` (engine) and
  `tests/test_statistics_integration.py` (endpoints).