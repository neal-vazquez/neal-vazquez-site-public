-- Retrieve a session only while its expiry is in the future.
-- Extracted from app/api/chat/route.ts; parameter order: session_id, now_epoch_seconds.
SELECT id, messages, turns FROM chat_sessions WHERE id = ? AND expires_at > ?;
