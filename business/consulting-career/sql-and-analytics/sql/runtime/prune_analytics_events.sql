-- Remove at most 100 raw records older than 180 days; keep daily totals.
-- Extracted from db/portfolio-events.ts; parameter order: none.
DELETE FROM analytics_events WHERE id IN (SELECT id FROM analytics_events WHERE received_at < datetime('now','-180 days') LIMIT 100);
