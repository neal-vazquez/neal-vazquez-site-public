-- Delete at most 100 expired sessions.
-- Extracted from db/chat.ts; parameter order: now_epoch_seconds.
DELETE FROM chat_sessions WHERE id IN (SELECT id FROM chat_sessions WHERE expires_at <= ? LIMIT 100);
