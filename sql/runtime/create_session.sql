-- Create an empty session with an explicit expiry.
-- Extracted from app/api/chat/route.ts; parameter order: session_id, expires_at_seconds.
INSERT INTO chat_sessions (id, expires_at) VALUES (?, ?);
