-- Check an active breaker and three independent budget caps.
-- Extracted from db/chat.ts; parameter order: breaker_id, now_epoch_seconds, lifetime_id, lifetime_max, month_id, month_max, day_id, day_max.
SELECT COUNT(*) AS blocked FROM chat_usage WHERE
    (id = ? AND expires_at > ?) OR (id = ? AND count >= ?) OR (id = ? AND count >= ?) OR (id = ? AND count >= ?);
