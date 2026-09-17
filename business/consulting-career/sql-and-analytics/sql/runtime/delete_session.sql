-- Delete one session by its opaque identifier.
-- Extracted from app/api/chat/route.ts; parameter order: session_id.
DELETE FROM chat_sessions WHERE id = ?;
