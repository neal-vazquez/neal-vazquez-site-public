CREATE INDEX `chat_sessions_expiry_idx` ON `chat_sessions` (`expires_at`);--> statement-breakpoint
CREATE INDEX `chat_usage_expiry_idx` ON `chat_usage` (`expires_at`);