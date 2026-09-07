-- Reserve an unlocked session while the turn cap permits.
-- Extracted from app/api/chat/route.ts; parameter order: lock_until_seconds, session_id, now_epoch_seconds, maximum_turns.
UPDATE chat_sessions SET locked_until = ? WHERE id = ? AND locked_until < ? AND turns < ? RETURNING id;
