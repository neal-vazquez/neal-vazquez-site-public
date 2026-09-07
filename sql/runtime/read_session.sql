-- Read session state after acquiring the lease.
-- Extracted from app/api/chat/route.ts; parameter order: session_id.
SELECT id, messages, turns FROM chat_sessions WHERE id = ?;
