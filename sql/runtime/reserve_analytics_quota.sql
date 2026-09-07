-- Atomically increment a bounded request counter.
-- Extracted from db/portfolio-events.ts; parameter order: bucket_id, expires_at_seconds, maximum.
INSERT INTO analytics_limits (id,count,expires_at) VALUES (?,1,?) ON CONFLICT(id) DO UPDATE SET count=count+1 WHERE count < ? RETURNING count;
