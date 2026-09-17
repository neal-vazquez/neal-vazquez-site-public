-- Remove at most 100 expired analytics counters.
-- Extracted from db/portfolio-events.ts; parameter order: now_epoch_seconds.
DELETE FROM analytics_limits WHERE id IN (SELECT id FROM analytics_limits WHERE expires_at < ? LIMIT 100);
