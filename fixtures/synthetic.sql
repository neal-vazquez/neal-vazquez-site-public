-- Entirely invented fixture. No exported visitor data, inquiries or transcripts.
-- UTC dates are fixed so the reports are reproducible.
INSERT INTO portfolio_events (event_name, location, path, created_at) VALUES
('page_view','homepage','/','2026-09-01 08:00:00'),
('project_click','work','/','2026-09-01 08:01:00');

INSERT OR IGNORE INTO analytics_events
(id,event_name,path,location,parameters,session_id,occurred_at,received_at,source) VALUES
('demo-01','page_view','/','homepage','{}',NULL,'2026-09-01T10:00:00.000Z','2026-09-01 10:00:00','browser'),
('demo-02','page_view','/dashboard','portfolio_dashboard','{}',NULL,'2026-09-01T10:01:00.000Z','2026-09-01 10:01:00','browser'),
('demo-03','project_click','/','work','{"destination":"site_sql"}',NULL,'2026-09-01T10:02:00.000Z','2026-09-01 10:02:00','browser'),
('demo-04','page_view','/','homepage','{}',NULL,'2026-09-03T10:00:00.000Z','2026-09-03 10:00:00','browser'),
('demo-05','page_view','/','homepage','{}',NULL,'2026-09-03T10:01:00.000Z','2026-09-03 10:01:00','browser'),
('demo-06','page_view','/dashboard','portfolio_dashboard','{}',NULL,'2026-09-03T10:02:00.000Z','2026-09-03 10:02:00','browser'),
('demo-07','page_view','/','homepage','{}',NULL,'2026-09-03T10:03:00.000Z','2026-09-03 10:03:00','browser'),
('demo-08','chat_open','/','chat_widget','{"device_category":"mobile"}',NULL,'2026-09-03T10:04:00.000Z','2026-09-03 10:04:00','browser'),
('demo-09','chat_guide_select','/dashboard','chat_widget','{"device_category":"desktop","guide_topic":"project"}',NULL,'2026-09-03T10:05:00.000Z','2026-09-03 10:05:00','browser'),
('demo-10','chat_open','/unlisted','chat_widget','{"device_category":"invalid","guide_topic":"unlisted"}',NULL,'2026-09-03T10:06:00.000Z','2026-09-03 10:06:00','browser'),
('demo-11','lead_saved','/','other','{}',NULL,'2026-09-03T10:07:00.000Z','2026-09-03 10:07:00','server'),
('demo-12','page_view','/','homepage','{}',NULL,'2026-09-05T10:00:00.000Z','2026-09-05 10:00:00','browser'),
('demo-13','project_click','/','work','{}',NULL,'2026-09-05T10:01:00.000Z','2026-09-05 10:01:00','browser'),
('demo-14','web_vital','/','work','{}',NULL,'2026-09-05T10:02:00.000Z','2026-09-05 10:02:00','browser'),
('demo-15','page_view','/dashboard','portfolio_dashboard','{}',NULL,'2026-09-07T10:00:00.000Z','2026-09-07 10:00:00','browser'),
('demo-16','page_view','/','homepage','{}',NULL,'2026-09-07T10:01:00.000Z','2026-09-07 10:01:00','browser'),
('demo-17','project_click','/','work','{}',NULL,'2026-09-06T23:59:00.000Z','2026-09-07 00:01:00','browser');

-- Replay of demo-03: its rollup must not increment a second time.
INSERT OR IGNORE INTO analytics_events
(id,event_name,path,location,occurred_at,received_at,source) VALUES
('demo-03','project_click','/','work','2026-09-01T10:02:00.000Z','2026-09-01 10:02:00','browser');

-- Empty synthetic session for operational examples. No transcript content.
INSERT INTO chat_sessions (id,expires_at) VALUES ('demo-session',2000000000);
INSERT INTO github_source_cache (id,cache_key,record,updated_at)
VALUES ('demo-owner','demo-cache','{"repositories":[]}',1000);
