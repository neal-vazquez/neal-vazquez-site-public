-- Deduplicate event ingestion by event ID.
-- Extracted from db/portfolio-events.ts; parameter order: event_id, event_name, path, location, parameters_json, session_id, occurred_at, source.
INSERT OR IGNORE INTO analytics_events (id,event_name,path,location,parameters,session_id,occurred_at,source) VALUES (?,?,?,?,?,?,?,?);
