# Design decisions

## Preserve the real implementation

The migrations and prepared statements form the core of this portfolio. Improving their presentation should not rewrite their history. SQL translations and new analysis are kept in separate directories, while the source manifest records the extraction locations and SHA-256 hashes. The private source revision is retained in the private site's release record, not required to run this repository.

## Make replay behavior explicit

Event IDs form the ingestion key. The insert and its rollup trigger execute together, so repeated delivery with the same ID does not increment totals. The tests also confirm that server events do not inflate browser totals. `INSERT OR IGNORE` can suppress constraint violations beyond duplicate IDs; the application must validate rows before insertion.

## Keep aggregation grain visible

Daily totals combine sources at date and event-name grain. Location ranking deliberately filters generic page labels, chat and operational telemetry. Page ranking filters for `page_view` and returns only the top ten paths. These queries answer different questions, so their totals should not be presented as interchangeable.

## Bound work at the database boundary

Cleanup deletes up to 100 eligible rows at a time. The subquery form avoids relying on SQLite's optional `DELETE ... LIMIT` compile-time feature. Tests insert 105 expired rows, verify only 100 disappear, and confirm historical browser totals remain.

Existing indexes support receipt-date, legacy-date, event-name, and expiry predicates. A small result limit is not a promise of a small scan; sorting and grouping may still read many eligible rows. Inspect plans and benchmark representative volumes before making performance claims.

To inspect a plan locally:

```python
import sys
sys.path.insert(0, 'scripts')
from demo import connect, sql
db = connect()
for row in db.execute(
    'EXPLAIN QUERY PLAN ' + sql('sql/runtime/page_rankings.sql'),
    ('2026-09-01 00:00:00', '2026-09-01 00:00:00'),
):
    print(tuple(row))
```

## Put conditional updates in one statement

Quota reservations, lease acquisition and cache writes express their state predicate in the write itself. This avoids a separate read-then-write decision for those individual operations. The test suite exercises cap exhaustion, repeated lease acquisition, and a stale cache write arriving after a newer one. These local tests do not simulate a distributed production load.

## Add analysis without changing the site

The calendar exercise uses a recursive CTE to construct days, a left join to fill gaps, a seven-row frame over one row per calendar day, and a null-safe growth calculation. The action-mix exercise uses conditional aggregation without manufacturing a conversion funnel. Reconciliation unions the two sets of dimension keys before joining so missing rows on either side remain visible.

These exercises are new to the public portfolio. They operate on the same schema and synthetic data without altering the website database or runtime behavior.

## Validation

Run `python scripts/demo.py --check` and `python -m unittest discover -s tests -v`. The initial local run passed all 22 statement executions and all 12 behavioral tests. The GitHub Actions badge reports the independently executed CI status when available. All evidence is from synthetic in-memory SQLite, not a production database export.
