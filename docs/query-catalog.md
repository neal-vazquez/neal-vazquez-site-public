# Query catalog

All 22 runtime statements are extracted from the accepted site source. Bind values in the order shown. SQL formatting and trailing semicolons are the only presentation changes.

| Query | Purpose | Positional bindings |
| --- | --- | --- |
| [record_event](../sql/runtime/record_event.sql) | Deduplicate event ingestion by event ID. | `event_id`, `event_name`, `path`, `location`, `parameters_json`, `session_id`, `occurred_at`, `source` |
| [prune_analytics_events](../sql/runtime/prune_analytics_events.sql) | Remove at most 100 raw records older than 180 days; keep daily totals. |  |
| [prune_analytics_limits](../sql/runtime/prune_analytics_limits.sql) | Remove at most 100 expired analytics counters. | `now_epoch_seconds` |
| [reserve_analytics_quota](../sql/runtime/reserve_analytics_quota.sql) | Atomically increment a bounded request counter. | `bucket_id`, `expires_at_seconds`, `maximum` |
| [daily_activity](../sql/runtime/daily_activity.sql) | Combine legacy event counts and current daily rollups. | `start_sql_timestamp`, `start_date` |
| [location_rankings](../sql/runtime/location_rankings.sql) | Rank meaningful page areas and exclude chat/operational events. | `start_sql_timestamp`, `start_date` |
| [page_rankings](../sql/runtime/page_rankings.sql) | Rank page views across legacy and current browser events. | `start_sql_timestamp`, `start_sql_timestamp` |
| [chat_engagement](../sql/runtime/chat_engagement.sql) | Aggregate chat actions with allowlisted JSON device, page and topic dimensions. | `start_sql_timestamp`, `start_iso_timestamp`, `end_iso_timestamp` |
| [prune_chat_sessions](../sql/runtime/prune_chat_sessions.sql) | Delete at most 100 expired sessions. | `now_epoch_seconds` |
| [prune_chat_usage](../sql/runtime/prune_chat_usage.sql) | Delete at most 100 expired usage buckets. | `now_epoch_seconds` |
| [reserve_chat_quota](../sql/runtime/reserve_chat_quota.sql) | Atomically reserve a unit below a caller-supplied cap. | `bucket_id`, `expires_at_seconds`, `maximum` |
| [budget_status](../sql/runtime/budget_status.sql) | Check an active breaker and three independent budget caps. | `breaker_id`, `now_epoch_seconds`, `lifetime_id`, `lifetime_max`, `month_id`, `month_max`, `day_id`, `day_max` |
| [extend_breaker](../sql/runtime/extend_breaker.sql) | Extend an expiry without shortening an existing pause. | `breaker_id`, `expires_at_seconds` |
| [read_active_session](../sql/runtime/read_active_session.sql) | Retrieve a session only while its expiry is in the future. | `session_id`, `now_epoch_seconds` |
| [delete_session](../sql/runtime/delete_session.sql) | Delete one session by its opaque identifier. | `session_id` |
| [create_session](../sql/runtime/create_session.sql) | Create an empty session with an explicit expiry. | `session_id`, `expires_at_seconds` |
| [acquire_session_lock](../sql/runtime/acquire_session_lock.sql) | Reserve an unlocked session while the turn cap permits. | `lock_until_seconds`, `session_id`, `now_epoch_seconds`, `maximum_turns` |
| [read_session](../sql/runtime/read_session.sql) | Read session state after acquiring the lease. | `session_id` |
| [save_session_turn](../sql/runtime/save_session_turn.sql) | Save JSON messages, increment turns and release the lease. | `messages_json`, `session_id` |
| [release_session_lock](../sql/runtime/release_session_lock.sql) | Release a session lease after an error or completion. | `session_id` |
| [read_cache](../sql/runtime/read_cache.sql) | Read a shared cache record for caller-side validation. | `cache_owner` |
| [upsert_cache](../sql/runtime/upsert_cache.sql) | Reject older cache writes using a conditional UPSERT. | `cache_owner`, `cache_key`, `record_json`, `updated_at_milliseconds` |

The contact INSERT under `sql/adapted/` translates the existing Drizzle operation into SQL. The three `sql/analysis/` queries are new portfolio exercises over the same schema and are not claimed to run in production.
