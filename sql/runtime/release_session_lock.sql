-- Release a session lease after an error or completion.
-- Extracted from app/api/chat/route.ts; parameter order: session_id.
UPDATE chat_sessions SET locked_until = 0 WHERE id = ?;
