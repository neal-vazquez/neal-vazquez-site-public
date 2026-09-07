# Data semantics and limits

## Table grains

| Table | Grain | Time representation | Purpose |
| --- | --- | --- | --- |
| `portfolio_events` | One legacy event | UTC SQL timestamp | Retained historical counts |
| `analytics_events` | One accepted event ID | UTC ISO occurrence time and SQL receipt timestamp | Raw event analysis and deduplication |
| `analytics_daily` | Receipt date × event name × location | UTC date | Browser-event totals that survive raw retention |
| `analytics_limits` | One caller-defined request bucket | Unix seconds | Request reservations |
| `chat_sessions` | One opaque session ID | Unix seconds | Session state, turn count and lease |
| `chat_usage` | One caller-defined budget or breaker ID | Unix seconds | Usage reservations and pause state |
| `contact_inquiries` | One saved inquiry | UTC SQL timestamp | Separate contact records |
| `github_source_cache` | One cache owner | Unix milliseconds | Replaceable serialized summary |

These are purpose-separated tables. The schema does not declare foreign keys, and the aggregate examples do not join visitor identity to contacts or chat content.

## Counts are actions

Page views, project clicks, chat opens and handoffs can repeat. They are not unique people, completed payments, confirmed messages delivered to a phone, or ordered conversion funnels. `lead_saved` means an inquiry was stored, not that it was emailed or became a paying engagement. The action-mix exercise keeps this server signal distinct from browser actions.

The daily and page ranking queries combine legacy and current stores. That assumes each underlying action was recorded in one source, not both. `UNION ALL` does not deduplicate cross-store events; migration or dual-write overlap must be resolved separately. The fixture uses disjoint events.

## Two clocks

The rollup trigger uses `received_at`, the server receipt clock. A late event that occurred September 6 but arrived September 7 increments September 7. The fixture includes this case.

Chat engagement bounds both receipt and occurrence times, then groups by the UTC date in `occurred_at`. Therefore chat charts and receipt-date totals need not match at time boundaries. The extracted query has no `source='browser'` predicate; it selects the listed chat event names exactly as the existing application does.

SQL timestamp comparisons here rely on the application's fixed UTC formats. Mixing offsets or arbitrary timestamp strings would invalidate these assumptions. The added exercises use an exclusive next-day boundary for inclusive date ranges. The extracted site queries preserve their original lower-bound behavior, including the absence of an upper bound in daily/page ranking queries.

## Rollup lifecycle

Only inserted browser events fire the rollup body. Replaying an existing ID through `INSERT OR IGNORE` inserts no row and increments nothing. Server events stay in the raw store without entering browser totals.

The trigger is insert-only. Updating or deleting a raw event does not reverse its aggregate. This preserves historical counts during 180-day raw retention, but it also means corrections need a deliberate aggregate-repair procedure. The reconciliation exercise is meaningful only for receipt-date windows whose raw rows remain fully retained. A historical rollup exceeding retained raw rows is expected after cleanup.

Daily rollups retain event and location dimensions, not path or device. Consequently page and chat reports depend on retained raw rows; older rollups cannot reconstruct those dimensions. Chat `CASE` expressions collapse unknown categories to a bounded value. This limits output dimensions but is not a claim of statistical anonymization or small-cell suppression.

## SQL and its caller

Placeholders must remain bound parameters. This repository exposes their order without copying the request handlers or their inputs. Application code is responsible for validating event names, paths, JSON, positive quota limits, timestamps and identifiers before binding.

The quota UPSERT inserts an initial count of one and enforces the cap on subsequent conflicts. It assumes a positive cap and caller-managed bucket identity/expiry. Expired rows do not reset themselves merely because a query runs. Three individual budget reservations are not one all-or-nothing transaction; the site's existing policy conservatively spends partial reservations.

The session lease prevents another reservation while its timestamp is active. It is not a general distributed locking system: an application that outlives its lease would need ownership/fencing checks before saving. The SQL alone does not provide cookie security, authentication, complete rate limiting, or content validation.

Cache writes reject strictly older timestamps. Equal timestamps may overwrite because the original condition is `>=`. Cache reads return serialized data; schema validation and freshness decisions occur in the caller. SQLite execution here verifies SQL behavior, not Cloudflare latency, provider behavior, or production-scale concurrency.
