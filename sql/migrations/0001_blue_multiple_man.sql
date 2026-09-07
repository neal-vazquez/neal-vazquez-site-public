CREATE TABLE `chat_sessions` (
	`id` text PRIMARY KEY NOT NULL,
	`messages` text DEFAULT '[]' NOT NULL,
	`turns` integer DEFAULT 0 NOT NULL,
	`locked_until` integer DEFAULT 0 NOT NULL,
	`expires_at` integer NOT NULL
);
--> statement-breakpoint
CREATE TABLE `chat_usage` (
	`id` text PRIMARY KEY NOT NULL,
	`count` integer DEFAULT 0 NOT NULL,
	`expires_at` integer NOT NULL
);
