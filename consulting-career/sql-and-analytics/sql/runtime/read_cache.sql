-- Read a shared cache record for caller-side validation.
-- Extracted from lib/github-source.ts; parameter order: cache_owner.
SELECT cache_key, record FROM github_source_cache WHERE id = ?;
