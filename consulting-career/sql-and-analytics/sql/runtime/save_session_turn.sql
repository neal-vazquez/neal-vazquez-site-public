-- Save JSON messages, increment turns and release the lease.
-- Extracted from app/api/chat/route.ts; parameter order: messages_json, session_id.
UPDATE chat_sessions SET messages = ?, turns = turns + 1, locked_until = 0 WHERE id = ? RETURNING id;
