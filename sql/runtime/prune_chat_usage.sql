-- Delete at most 100 expired usage buckets.
-- Extracted from db/chat.ts; parameter order: now_epoch_seconds.
DELETE FROM chat_usage WHERE id IN (SELECT id FROM chat_usage WHERE expires_at <= ? LIMIT 100);
