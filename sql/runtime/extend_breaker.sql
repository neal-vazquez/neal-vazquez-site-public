-- Extend an expiry without shortening an existing pause.
-- Extracted from db/chat.ts; parameter order: breaker_id, expires_at_seconds.
INSERT INTO chat_usage (id,count,expires_at) VALUES (?,1,?) ON CONFLICT(id) DO UPDATE SET expires_at = MAX(expires_at, excluded.expires_at);
