CREATE TABLE `github_source_cache` (
	`id` text PRIMARY KEY NOT NULL,
	`cache_key` text NOT NULL,
	`record` text NOT NULL,
	`updated_at` integer NOT NULL
);
