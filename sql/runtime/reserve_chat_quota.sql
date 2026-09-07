-- Atomically reserve a unit below a caller-supplied cap.
-- Extracted from db/chat.ts; parameter order: bucket_id, expires_at_seconds, maximum.
INSERT INTO chat_usage (id, count, expires_at) VALUES (?, 1, ?)
    ON CONFLICT(id) DO UPDATE SET count = count + 1 WHERE count < ? RETURNING count;
