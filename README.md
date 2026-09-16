# SQL portfolio: operational analytics and data integrity

[![SQL checks](https://github.com/neal-vazquez/neal-vazquez-site-public/actions/workflows/sql.yml/badge.svg)](https://github.com/neal-vazquez/neal-vazquez-site-public/actions/workflows/sql.yml)

**Runnable SQL case studies by Neal Vazquez: website measurement, data integrity, and contact-center operations.**

Two review paths, both runnable locally with Python and SQLite:

| Start with | What it demonstrates | Run it |
| --- | --- | --- |
| [Contact-center case study](examples/contact-center/README.md) | AHT, first-contact resolution, repeat-contact windows, missing data, and a business interpretation | `python scripts/contact_center.py` |
| [Website SQL](docs/query-catalog.md) | Event ingestion, daily trends, reconciliation, deduplication, and conditional writes | `python scripts/demo.py` |

**Five-minute review:** read the [contact-center findings and metric definitions](examples/contact-center/README.md), inspect the [CTEs and window function](examples/contact-center/queue_metrics.sql), then review the [boundary tests](tests/test_contact_center.py). For production-derived SQL, start with [event ingestion](sql/runtime/record_event.sql) and [rollup reconciliation](sql/analysis/rollup_reconciliation.sql).

[Professional background](https://neal-vazquez.com/consulting/resume) · [Website](https://neal-vazquez.com) · [All projects](https://github.com/neal-vazquez)

## Website case study

This repository makes the SQL developed for [neal-vazquez.com](https://neal-vazquez.com) inspectable and runnable. It preserves **five schema migrations and all 22 embedded SQL statements from Sites v94**, captured September 7, 2026. This historical snapshot does not describe the current website's schema or retention policy. The queries use SQLite, the SQL engine underlying Cloudflare D1.

The question driving the work: how do you turn repeatable website actions into useful counts while preserving historical totals, avoiding duplicate events, and keeping database operations bounded?

The demo uses entirely synthetic data. It runs in memory with Python's standard library, with no account, cloud service, API key, or connection to the live website.

## Start here

```bash
git clone https://github.com/neal-vazquez/neal-vazquez-site-public.git
cd neal-vazquez-site-public
python scripts/demo.py
python scripts/demo.py --check
python scripts/contact_center.py
python -m unittest discover -s tests -v
```

Use Python 3.10+ linked to SQLite 3.35+ with JSON functions. The runner checks SQLite and JSON support. CI uses Python 3.12. No package installation is required.

The website demo prints three reports. Its `--check` mode executes every extracted runtime statement on an isolated fixture database and checks expected totals. The contact-center demo prints a separate queue-level report. The tests exercise failure and boundary cases and verify the historical SQL against the source hashes.

## What to inspect

| Business or engineering question | SQL to read | Techniques |
| --- | --- | --- |
| How can a retried event avoid counting twice? | [Event ingestion](sql/runtime/record_event.sql), [rollup trigger](sql/migrations/0003_left_redwing.sql) | Primary-key deduplication, `INSERT OR IGNORE`, triggers, UPSERT |
| How do old and new event stores contribute to one report? | [Daily activity](sql/runtime/daily_activity.sql) | `UNION ALL`, aggregation at a common grain |
| Which pages and page areas receive activity? | [Page rankings](sql/runtime/page_rankings.sql), [area rankings](sql/runtime/location_rankings.sql) | Grouping, exclusions, deterministic ordering, bounded results |
| Which chat actions occur on different devices and pages? | [Chat engagement](sql/runtime/chat_engagement.sql) | JSON extraction, allowlisted `CASE` dimensions, time predicates |
| How are usage reservations and session leases represented? | [Quota reservation](sql/runtime/reserve_chat_quota.sql), [session lease](sql/runtime/acquire_session_lock.sql) | Conditional writes, UPSERT, `RETURNING` |
| How can cleanup preserve historical totals? | [Raw-event retention](sql/runtime/prune_analytics_events.sql) | Bounded deletion through a subquery, separate aggregates |
| How do cache writes avoid moving backward in time? | [Cache UPSERT](sql/runtime/upsert_cache.sql) | `excluded` values, conditional conflict resolution |
| What does a gap-free daily trend look like? | [Calendar activity](sql/analysis/calendar_activity.sql) | Recursive CTE, `LEFT JOIN`, `COALESCE`, `LAG`, window frames, `NULLIF` |
| Do raw events agree with their rollups? | [Reconciliation](sql/analysis/rollup_reconciliation.sql) | CTEs, union of dimension keys, joins, mismatch detection |

For positional bindings and every operational query, see the [complete query catalog](docs/query-catalog.md).

## A reproducible result

The fixture submits 17 distinct current events plus one duplicate replay. The accepted current store has 17 rows. Its daily rollups total 16 browser events because the server-side `lead_saved` event is intentionally excluded. Two legacy events remain available to the combined reports.

The calendar exercise counts current browser page views by **UTC receipt date**, including empty days:

| Date | Page views | Days in trailing window | Trailing mean |
| --- | ---: | ---: | ---: |
| 2026-09-01 | 2 | 1 | 2.00 |
| 2026-09-02 | 0 | 2 | 1.00 |
| 2026-09-03 | 4 | 3 | 2.00 |
| 2026-09-04 | 0 | 4 | 1.50 |
| 2026-09-05 | 1 | 5 | 1.40 |
| 2026-09-06 | 0 | 6 | 1.17 |
| 2026-09-07 | 2 | 7 | 1.29 |

The first six means use the available prefix, not an assumed full seven-day history. Percentage change is `NULL` when there is no previous day or its count is zero. Empty days mean zero recorded events in this fixture; live telemetry gaps would need separate interpretation.

## Scope and provenance

| Location | What it contains |
| --- | --- |
| `sql/migrations/` | Five original schema migrations, copied byte for byte |
| `sql/runtime/` | 22 extracted prepared statements; comments and terminal semicolons added |
| `sql/adapted/` | One SQL translation of the existing Drizzle contact INSERT |
| `sql/analysis/` | Three new analytical exercises over the same schema; these are not production features |
| `fixtures/` | Invented events, an empty synthetic session, and a synthetic cache record |
| `scripts/` | Local in-memory demo and statement execution checks |
| `examples/contact-center/` | Standalone synthetic operations case study, schema, fixture, query, and interpretation |
| `tests/` | Website behavior, source-integrity checks, and contact-center metric boundary tests |
| `docs/` | Query bindings, data semantics, design decisions, and source hashes |

This is a snapshot of the accepted website implementation, not an automatic synchronization service or a full website source distribution. Retired historical branches, deployment code, credentials, database contents, and provider orchestration are outside this SQL collection. The site remains separately maintained.

Read [data semantics and limitations](docs/data-semantics.md), [design decisions](docs/design-decisions.md), and the [source manifest](docs/source-manifest.json) for the details that determine whether a count is meaningful.

## Authorship

Project direction, measurement requirements, and review: **Neal Vazquez**. SQL, documentation, and validation were developed collaboratively with ChatGPT. The extracted statements come from that website work; portfolio exercises are identified separately.

The contact-center example was added September 16, 2026 as a synthetic portfolio exercise. Its data and results are invented for demonstration; they are not client outcomes, an employer dataset, or a production deployment.

[Explore the website](https://neal-vazquez.com) · [More projects](https://github.com/neal-vazquez)
