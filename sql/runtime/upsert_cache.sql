-- Reject older cache writes using a conditional UPSERT.
-- Extracted from lib/github-source.ts; parameter order: cache_owner, cache_key, record_json, updated_at_milliseconds.
INSERT INTO github_source_cache (id, cache_key, record, updated_at) VALUES (?, ?, ?, ?)
      ON CONFLICT(id) DO UPDATE SET cache_key = excluded.cache_key, record = excluded.record, updated_at = excluded.updated_at
      WHERE excluded.updated_at >= github_source_cache.updated_at;
