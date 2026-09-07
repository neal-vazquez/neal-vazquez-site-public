CREATE TABLE `analytics_daily` (
	`key` text PRIMARY KEY NOT NULL,
	`date` text NOT NULL,
	`event_name` text NOT NULL,
	`location` text NOT NULL,
	`count` integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
CREATE INDEX `analytics_daily_date_idx` ON `analytics_daily` (`date`);--> statement-breakpoint
CREATE TABLE `analytics_events` (
	`id` text PRIMARY KEY NOT NULL,
	`event_name` text NOT NULL,
	`path` text NOT NULL,
	`location` text DEFAULT 'other' NOT NULL,
	`parameters` text DEFAULT '{}' NOT NULL,
	`session_id` text,
	`occurred_at` text NOT NULL,
	`received_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL,
	`source` text DEFAULT 'browser' NOT NULL
);
--> statement-breakpoint
CREATE INDEX `analytics_events_received_idx` ON `analytics_events` (`received_at`);--> statement-breakpoint
CREATE TABLE `analytics_limits` (
	`id` text PRIMARY KEY NOT NULL,
	`count` integer DEFAULT 0 NOT NULL,
	`expires_at` integer NOT NULL
);
--> statement-breakpoint
CREATE INDEX `analytics_limits_expiry_idx` ON `analytics_limits` (`expires_at`);--> statement-breakpoint
CREATE TABLE IF NOT EXISTS `portfolio_events` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`event_name` text NOT NULL,
	`location` text,
	`path` text NOT NULL,
	`created_at` text DEFAULT CURRENT_TIMESTAMP NOT NULL
);
--> statement-breakpoint
CREATE INDEX IF NOT EXISTS `portfolio_events_created_at_idx` ON `portfolio_events` (`created_at`);--> statement-breakpoint
CREATE INDEX IF NOT EXISTS `portfolio_events_event_name_idx` ON `portfolio_events` (`event_name`);
--> statement-breakpoint
CREATE TRIGGER analytics_events_rollup AFTER INSERT ON analytics_events
WHEN NEW.source = 'browser'
BEGIN
  INSERT INTO analytics_daily (key,date,event_name,location,count)
  VALUES (substr(NEW.received_at,1,10)||':'||NEW.event_name||':'||NEW.location,substr(NEW.received_at,1,10),NEW.event_name,NEW.location,1)
  ON CONFLICT(key) DO UPDATE SET count=count+1;
END;
